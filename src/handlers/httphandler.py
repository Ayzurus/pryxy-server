"""
httphandler.py

Customizable handler for HTTP requests. Uses http.json for
direction.

The handler extends the BaseHTTPRequestHandler from the
http.server module, and most of its integral logic is an
adaptation of it
___________________
by:
Ayzurus
"""
__version__ = "0.3.0"

import handlers.jsonrules
import http.client
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from socket import timeout
from utils import safeprint

class HttpHandler(BaseHTTPRequestHandler):
    server_version = "Pryxy-HttpHandler/" + __version__
    WILDCARD = "*"

    def __init__(self, *args, rules=None, **kwargs):
        self._rules = rules if rules else handlers.jsonrules.get("http")
        super().__init__(*args, **kwargs)

    def log_request(self, code='-', size='-'):
        if isinstance(code, HTTPStatus):
            code = code.value
        if isinstance(code, int):
            self.log_message('%s Response %s - "%s" %s',
                            self.address_string(), str(code), self.requestline, str(size))
        else:
            self.log_message('%s Request "%s" %s',
                            self.address_string(), self.requestline, str(size))

    def log_error(self, format, *args):
        self.log_message(format, *args)

    def log_message(self, format, *args):
        safeprint.log(format % args)
        
    def parse_request(self):
        """Parse a request (internal).

        The request should be stored in self.raw_requestline; the results
        are in self.command, self.path, self.request_version and
        self.headers.

        Return True for success, False for failure; on failure, any relevant
        error response has already been sent back.

        """
        self.command = None  # set in case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = True
        requestline = str(self.raw_requestline, 'iso-8859-1')
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        # the request requires at least the command and path of the URI
        if len(words) < 2:
            self.send_error(HTTPStatus.BAD_REQUEST, 
                    "The request requires at least the command and path")
            return False
        # if the protocol version is present, check it
        # otherwise ignore it and attempt to respond anyway
        if len(words) >= 3:
            version = words[-1]
            try:
                if version.startswith('HTTP/'):
                    version_number = version.split('/', 1)[1].split(".")
                    version_number = int(version_number[0]), int(version_number[1])
                    # only supported up to http/1.x
                    if version_number >= (2, 0):
                        self.send_error(HTTPStatus.HTTP_VERSION_NOT_SUPPORTED, 
                                "Pryxy does not support version %s" % version)
                        return False
                    self.request_version = version
            except (ValueError, IndexError):
                self.log_error("could not parse the protocol version, ignoring...")
        self.command, self.path = words[:2]
        # Examine the headers and look for a Connection directive.
        try:
            self.headers = http.client.parse_headers(self.rfile,
                                                     _class=self.MessageClass)
        except http.client.LineTooLong as err:
            self.send_error(
                HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                "Line too long",
                str(err))
            return False
        except http.client.HTTPException as err:
            self.send_error(
                HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                "Too many headers",
                str(err)
            )
            return False
        # TODO check if connection is needed to be kept (in the context of simulating)
        conntype = self.headers.get('Connection', "")
        if conntype.lower() == 'close':
            self.close_connection = True
        elif (conntype.lower() == 'keep-alive' and
              self.protocol_version >= "HTTP/1.1"):
            self.close_connection = False
        # Examine the headers and look for an Expect directive
        expect = self.headers.get('Expect', "")
        if (expect.lower() == "100-continue" and
                self.protocol_version >= "HTTP/1.1" and
                self.request_version >= "HTTP/1.1"):
            if not self.handle_expect_100():
                return False
        return True

    def _fetch_response_rules(self):
        """fetches the response rules that match the given request"""
        uri_requestline = "%s %s" % (self.command, self.path)
        if self._rules:
            uri_found = False
            # Test if any rule matches this request's URI, exclude wildcard rule DEFAULT
            for rule in self._rules.keys():
                if rule != HttpHandler.WILDCARD:
                    uri = rule
                    uri_wildcard_id = rule.find(HttpHandler.WILDCARD)
                    if uri_wildcard_id != -1:
                        if rule.startswith(HttpHandler.WILDCARD):
                            uri = rule[uri_wildcard_id+1:len(rule)]
                            uri_found = uri_requestline.endswith(uri)
                        else:
                            uri = rule[0:uri_wildcard_id]
                            uri_found = uri_requestline.startswith(uri)
                    else:
                        uri_found = uri_requestline == uri
                    if uri_found:
                        return self._rules[rule]
            # If no rules match the request, test if there is a wildcard rule DEFAULT
            if not uri_found and HttpHandler.WILDCARD in self._rules:
                return self._rules[HttpHandler.WILDCARD]
        return None

    def _respond(self):
        """Responds to the request with the given rules from the json"""
        response = self._fetch_response_rules()
        self.body = None
        # If any rule matched, send the rule's response
        if response:
            safeprint.debug("http response rule = %s" % response)
            code = int(response["code"])
            if code > 399:
                self.send_error(code, response["reason"] if "reason" in response else "")
            else:
                self.send_response(code)
            for header in [(k,v) for k,v in response.items() if k not in ("code", "reason", "body")]:
                self.send_header(header[0], header[1])
            if "body" in response:
                self.body = str(response["body"])
                self.send_header("Content-Length", str(len(self.body)))
                # TODO detect Content-Type automatically, but only allow text types
                # TODO allow file paths to send files instead of only text types
            self.end_headers()
            if self.body:
                self.wfile.write(self.body.encode("UTF-8", "strict"))
            return
        # In case no rule is configured for the request, send default error
        self.send_error(HTTPStatus.NOT_IMPLEMENTED, "No rules found for the given Request/URI")

    def handle_one_request(self):
        """Handle a single HTTP request."""
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            # Handler name logic not required, all messages are just responded based on the rules
            if self.parse_request():
                self._respond()
            # actually send the response if not already done
            self.wfile.flush() 
        except timeout as e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.send_error(HTTPStatus.REQUEST_TIMEOUT)
            self.close_connection = True
            return
