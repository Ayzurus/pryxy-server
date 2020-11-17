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
        self.wfile = open(write_path, "wb")
        self.client_address = ("127.0.0.1", 80)
    
    def close(self):
        self.rfile.close()
        self.wfile.close()
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
    handler._respond()
    cap = capsys.readouterr()
    assert cap.out.find("Response 200") != -1

def testHttpHandlerBadRequest(capsys):
    """responding with 400 when the request URI is incomplete"""
    handler.raw_requestline = "PUT\r\n".encode("iso-8859-1", "strict")
    assert not handler.parse_request()
    cap = capsys.readouterr()
    assert cap.out.find("Response 400") != -1

def testHttpHandlerNotImplemented(capsys):
    """responding with 501 when no rule found"""
    handler.raw_requestline = "DELETE / HTTP/1.1\r\n".encode("iso-8859-1", "strict")
    assert handler.parse_request()
    handler._respond()
    cap = capsys.readouterr()
    assert cap.out.find("Response 501") != -1

def testHttpHandlerUnsupportedVersion(capsys):
    """responding with 505 to an http version >= 2.0"""
    handler.raw_requestline = "GET / HTTP/2.0\r\n".encode("iso-8859-1", "strict")
    assert not handler.parse_request()
    cap = capsys.readouterr()
    assert cap.out.find("Response 505") != -1

def teardown_module():
    handler.close()