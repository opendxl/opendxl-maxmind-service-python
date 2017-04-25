import tempfile
import os
import StringIO
import gzip
import logging
from threading import Timer

import requests
import maxminddb
from dxlbootstrap.app import Application
from dxlclient.service import ServiceRegistrationInfo
from requesthandlers import *

# Configure local logger
logger = logging.getLogger(__name__)


class MaxMindGeolocationService(Application):
    """
    The "MaxMind Geolocation Service" service class.
    """

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the
            application
        """
        super(MaxMindGeolocationService, self).__init__(config_dir, "dxlmaxmindservice.config")

        self._database = None

    @property
    def client(self):
        """
        The DXL client used by the application to communicate with the DXL
        fabric
        """
        return self._dxl_client

    @property
    def config(self):
        """
        The application configuration (as read from the "dxlmaxmindservice.config" file)
        """
        return self._config

    def on_run(self):
        """
        Invoked when the application has started running.
        """
        logger.info("On 'run' callback.")

    def on_load_configuration(self, config):
        """
        Invoked after the application-specific configuration has been loaded

        This callback provides the opportunity for the application to parse
        additional configuration properties.

        :param config: The application configuration
        """
        logger.info("On 'load configuration' callback.")

        # Initialize the MaxMind Database
        self._database = MaxMindDatabase(int(config.get('MaxMindDatabase', 'databaseUpdateInterval')),
                                         config.get('MaxMindDatabase', 'databasePath'))

    def on_dxl_connect(self):
        """
        Invoked after the client associated with the application has connected
        to the DXL fabric.
        """
        logger.info("On 'DXL connect' callback.")
    
    def on_register_services(self):
        """
        Invoked when services should be registered with the application
        """
        # Register service 'maxmind_geolocation_service'
        logger.info("Registering service: {0}".format("maxmind_geolocation_service"))
        service = ServiceRegistrationInfo(self._dxl_client, "/opendxl-maxmind/service/geolocation")
        logger.info("Registering request callback: {0}".format("maxmind_service_hostlookup"))
        self.add_request_callback(service, "/opendxl-maxmind/service/geolocation/host_lookup",
                                  MaxMindHostLookupRequestCallback(self), True)
        self.register_service(service)

    def destroy(self):
        logger.info("Destroying MaxMindGeolocationService...")
        super(MaxMindGeolocationService, self).destroy()

    @property
    def database(self):
        """
        The MaxMind Database access object
        """
        return self._database


class MaxMindDatabase(object):
    """
    A class to handle IP lookups and updating of the MaxMind Database
    """

    #: The URL of the free MaxMind GeoLite database
    MAXMIND_FREE_DB_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'

    def __init__(self, update_interval, database_path):
        """
        Initializes the MaxMindDatabase

        :param update_interval: The interval to update the MaxMind database in minutes
        """
        if database_path is not None and database_path != "":
            logger.info("Local database specified. Updates will not be automatically downloaded.")
            if not os.path.isfile(database_path):
                raise Exception("Invalid database path specified: " + database_path)
            self._download_database = False
            self._database_path = database_path
            self._reader = maxminddb.open_database(database_path, maxminddb.const.MODE_MEMORY)
        else:
            self._download_database = True
            self._reader = None
            self._database_path = None
            self._database_checksum = None
            self._update_interval = update_interval
            self._update_database()

    def _update_database(self):
        """
        Determines if a database update is needed and if so downloads a new one from MaxMind
        """
        if not self._download_database:
            logger.warning("_update_database called while in pre-specified database"
                           " mode... returning without updates...")
            return

        logger.info("Checking for MaxMind database updates...")
        try:
            if not self._is_update_needed():
                logger.info("No database updates to retrieve.")
                return

            logger.info("Retrieving MaxMind Database...")
            response = requests.get(self.MAXMIND_FREE_DB_URL)
            response.raise_for_status()
            logger.info('Retrieved MaxMind database.')

            data = gzip.GzipFile(fileobj=StringIO.StringIO(response.content))

            # Write the database to a temporary file
            fd, file_path = tempfile.mkstemp()
            with os.fdopen(fd, 'wb') as temp_file:
                temp_file.write(data.read())

            self._swap_database(file_path)
            logger.info("MaxMind database updated.")
        except:
            logger.exception("Failed to update MaxMind database.")
        finally:
            # Schedule this function to run again in the configured update interval
            self._update_thread = Timer(self._update_interval * 60 * 60, self._update_database)
            self._update_thread.daemon = True
            self._update_thread.start()

    def _is_update_needed(self):
        """
        Determines if an update for the database is necessary

        :return: Whether or not the database should be updated
        """

        # Retrieve the headers of the response to compare the MD5 checksums of the file
        headers_response = requests.head(self.MAXMIND_FREE_DB_URL)
        logger.debug(headers_response.headers)
        headers_response.raise_for_status()
        response_checksum = headers_response.headers.get('X-Database-MD5')
        logger.info("Database MD5 received in response headers: " + str(response_checksum))
        # Compare the current file checksum to the one received from MaxMind
        if response_checksum is not None and response_checksum == self._database_checksum:
            return False
        self._response_checksum = response_checksum
        return True

    def _swap_database(self, new_database_path):
        """
        Swap the current database with a new database

        :param new_database_path: The path to the new database
        """
        # Open the new database
        self._reader = maxminddb.open_database(new_database_path, maxminddb.const.MODE_MEMORY)

        # Delete the temporary new database file
        try:
            os.remove(new_database_path)
        except:
            logger.exception("Failed to remove old database file.")
        self._database_checksum = self._response_checksum

    def lookup_ip(self, ip):
        """
        Looks up an IP or hostname in the MaxMind database

        :param ip: The IP or Hostname to look up
        :return: A dictionary of the MaxMind Database response
        """
        if self._reader is None:
            raise Exception("MaxMind database not yet initialized.")
        return self._reader.get(ip)
