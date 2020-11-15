"""
proxyserver.py

Main module for the TCP proxy server. Defines the Proxy class and the main
entry point for executing the server.
___________________
by:
Ayzurus
"""
import http.server
import sys
import safeprint
import argparse
import time
from threading import Thread
from socketserver import TCPServer

PROTO = {
    "http": http.server.SimpleHTTPRequestHandler
}

class ProxyServer(Thread, TCPServer):
    THREAD_NAME = "pyxy-server"
    THREAD_POLL_INTERVAL = 5

    def __init__(self, host: str, port: int, proto: str):
        Thread.__init__(self)
        TCPServer.__init__(self, (host, port), PROTO[proto])
        self._active = False
        self._proto = proto
        self.setName(ProxyServer.THREAD_NAME)
    
    def run(self):
        safeprint.log("starting listener {}".format(str(self)))
        self._active = True
        self.serve_forever(ProxyServer.THREAD_POLL_INTERVAL)
        
    def await_shutdown(self):
        """
        awaits for a shutdown request from the CLI, in parallel, 
        to deactivate and close the proxy
        """
        safeprint.log("awaiting proxy shutdown...")
        while self._active:
            if sys.stdin.read(1) != "":
                safeprint.log("received shutdown request")
                self.shutdown()
                self._active = False
        safeprint.log("shutting down proxy...")
    
    def __str__(self):
        return ProxyServer.THREAD_NAME + "@" + str(self.socket.getsockname()) + " proto: " + self._proto
    
    def __repr__(self):
        return self.__str__()

def main(args):
    parser = argparse.ArgumentParser(args[0], description="Simple python proxy server for development, debug and testing")
    parser.add_argument("-a", "--host", action="store", type=str, default="127.0.0.1", help="the proxy's host/address to listen on")
    parser.add_argument("-p", "--port", action="store", type=int, default=80, help="the proxy's port to listen on")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="logs expressive information during execution")
    parser.add_argument("-x", "--proto", action="store", type=str, default="http", help="the proxy's protocol to work with (http only)")
    result_args = parser.parse_args()
    safeprint.setup(result_args.verbose, __debug__)
    pyxy = ProxyServer(result_args.host, result_args.port, result_args.proto)
    pyxy.start()
    time.sleep(1)
    pyxy.await_shutdown()
    pyxy.join()

main(sys.argv)