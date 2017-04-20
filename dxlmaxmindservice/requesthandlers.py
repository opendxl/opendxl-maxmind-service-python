import logging
import socket

from dxlclient.callbacks import RequestCallback
from dxlclient.message import Response, ErrorResponse
from dxlbootstrap.util import MessageUtils


# Configure local logger
logger = logging.getLogger(__name__)


class MaxMindHostLookupRequestCallback(RequestCallback):
    """
    Request callback for looking up IPs in the MaxMind geolocation database
    """

    #: The host request parameter
    _PARAM_HOST = "host"

    def __init__(self, app):
        """
        Constructor parameters:

        :param app: The application this handler is associated with
        """
        super(MaxMindHostLookupRequestCallback, self).__init__()
        self._app = app

    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param request: The request message
        """
        # Handle request
        logger.info("Request received on topic: '{0}' with payload: '{1}'".format(
            request.destination_topic, MessageUtils.decode_payload(request)))

        try:
            # Retrieve the parameters from the request
            params = MessageUtils.json_payload_to_dict(request)

            if self._PARAM_HOST not in params:
                raise Exception("Required parameter not specified: '{0}'".format(self._PARAM_HOST))

            target = params[self._PARAM_HOST]

            ipaddr = socket.gethostbyname(target)

            logger.debug("IP to be located: " + ipaddr)
            # Lookup the IP/host
            results = self._app.database.lookup_ip(ipaddr)
            logger.debug(results)

            # Create response
            res = Response(request)

            # Set payload
            MessageUtils.dict_to_json_payload(res, results)

            # Send response
            self._app.client.send_response(res)

        except Exception as ex:
            logger.exception("Error handling request")
            err_res = ErrorResponse(request, MessageUtils.encode(str(ex)))
            self._app.client.send_response(err_res)
