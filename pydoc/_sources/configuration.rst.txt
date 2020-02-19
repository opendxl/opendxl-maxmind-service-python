Configuration
=============

The MaxMind Geolocation Service application requires a set of configuration files to operate.

This distribution contains a ``config`` sub-directory that includes the configuration files that must
be populated prior to running the application.

Each of these files are documented throughout the remained of this page.

Application configuration directory:

    .. code-block:: python

        config/
            dxlclient.config
            dxlmaxmindservice.config
            logging.config (optional)

.. _dxl_client_config_file_label:

DXL Client Configuration File (dxlclient.config)
------------------------------------------------

    The required ``dxlclient.config`` file is used to configure the DXL client that will connect to the DXL fabric.

    The steps to populate this configuration file are the same as those documented in the `OpenDXL Python
    SDK`, see the
    `OpenDXL Python SDK Samples Configuration <https://opendxl.github.io/opendxl-client-python/pydoc/sampleconfig.html>`_
    page for more information.

    The following is an example of a populated DXL client configuration file:

        .. code-block:: python

            [Certs]
            BrokerCertChain=c:\\certificates\\brokercerts.crt
            CertFile=c:\\certificates\\client.crt
            PrivateKey=c:\\certificates\\client.key

            [Brokers]
            {5d73b77f-8c4b-4ae0-b437-febd12facfd4}={5d73b77f-8c4b-4ae0-b437-febd12facfd4};8883;mybroker.mcafee.com;192.168.1.12
            {24397e4d-645f-4f2f-974f-f98c55bdddf7}={24397e4d-645f-4f2f-974f-f98c55bdddf7};8883;mybroker2.mcafee.com;192.168.1.13

.. _dxl_service_config_file_label:

MaxMind Geolocation Service (dxlmaxmindservice.config)
------------------------------------------------------

    The required ``dxlmaxmindservice.config`` file is used to configure the application.

    The following is an example of a populated application configuration file:

        .. code-block:: python

            [MaxMindDatabase]

            # A MaxMind license key
            # If left blank, databasePath must be specified
            licenseKey=

            # The path to a local MaxMind database to be used
            # If left blank the database will be automatically downloaded and updated
            databasePath=

            # The number of hours between database updates when downloading the database
            # Only takes effect if the databasePath is not set
            databaseUpdateInterval=24

    **MaxMindDatabase**

        The ``MaxMindDatabase`` section is used to specify where the MaxMind database will be loaded from.

        +------------------------+----------+----------------------------------------------------------------------+
        | Name                   | Required | Description                                                          |
        +========================+==========+======================================================================+
        | licenseKey             | no       | A MaxMind license key. If left blank, databasePath must be           |
        |                        |          | specified.                                                           |
        +------------------------+----------+----------------------------------------------------------------------+
        | databasePath           | no       | The path to a local MaxMind database. If left blank, the database    |
        |                        |          | specified will automatically be downloaded and updated.              |
        +------------------------+----------+----------------------------------------------------------------------+
        | databaseUpdateInterval | no       | The interval (in hours) to check for updates to the database.        |
        |                        |          | Updates only occur if the database is being downloaded.              |
        +------------------------+----------+----------------------------------------------------------------------+

Logging File (logging.config)
-----------------------------

    The optional ``logging.config`` file is used to configure how the application writes log messages.
