# python and pytest are somewhat complicated with the paths...
# added the 'src/' directory to the path to find the remaining modules
import sys, os
sys.path.append("./src/")

from handlers.httphandler import HttpHandler
from handlers import jsonrules

read_path = "./tests/handlers/http_in.txt"
write_path = "./tests/handlers/http_out.txt"
handler = None

# Mock class to override TCPServer constructor
class MockHttpHandler(HttpHandler):
    def __init__(self):
        self._rules = jsonrules.get("http")
        self.rfile = open(read_path, "rb")
        self.client_address = ("127.0.0.1", 80)
    
    def close(self):
        self.rfile.close()
        os.remove(read_path)
        os.remove(write_path)

def setup_module():
    jsonrules.setup("./tests/handlers/")
    with open(read_path, "wb") as msg:
        msg.write("Connection: close\r\n".encode("iso-8859-1", "strict"))
    global handler
    handler = MockHttpHandler()

def testHttpHandlerRespondGetOk(capsys):
    """
        receive a 'GET /' and parse it. since request does not trigger no exception, 
        should parse as TRUE and respond according to rule
    """
    handler.raw_requestline = "GET / HTTP/1.1\r\n".encode("iso-8859-1", "strict")
    assert handler.parse_request()
    handler.wfile = open(write_path, "wb")
    handler._respond()
    handler.wfile.close()
    with open(write_path, "rb") as result:
        assert "HTTP/1.0 200 OK".encode("iso-8859-1", "strict") in result.read()

def testHttpHandlerBadRequest(capsys):
    """responding with 400 when the request URI is incomplete"""
    handler.raw_requestline = "PUT\r\n".encode("iso-8859-1", "strict")
    handler.wfile = open(write_path, "wb")
    assert not handler.parse_request()
    handler.wfile.close()
    with open(write_path, "rb") as result:
        assert "<p>Error code: 400</p>".encode("iso-8859-1", "strict") in result.read()

def testHttpHandlerNotImplemented(capsys):
    """responding with 501 when no rule found"""
    handler.raw_requestline = "DELETE / HTTP/1.1\r\n".encode("iso-8859-1", "strict")
    assert handler.parse_request()
    handler.wfile = open(write_path, "wb")
    handler._respond()
    handler.wfile.close()
    with open(write_path, "rb") as result:
        assert "HTTP/1.0 501 No rules found for the given Request/URI".encode("iso-8859-1", "strict") in result.read()

def testHttpHandlerUnsupportedVersion(capsys):
    """responding with 505 to an http version >= 2.0"""
    handler.raw_requestline = "GET / HTTP/2.0\r\n".encode("iso-8859-1", "strict")
    handler.wfile = open(write_path, "wb")
    assert not handler.parse_request()
    handler.wfile.close()
    with open(write_path, "rb") as result:
        assert "<p>Error code: 505</p>".encode("iso-8859-1", "strict") in result.read()

def teardown_module():
    handler.close()