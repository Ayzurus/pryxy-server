"""
proxyserver.py

Main module for the TCP proxy server. Defines the Proxy class and the main
entry point for executing the server.
___________________
by:
Ayzurus
"""
__version__ = "0.3.0"

import sys
import argparse
import time
import signal
import socket
import handlers.jsonrules
import handlers.httphandler
from utils import safeprint
from threading import Thread
from socketserver import TCPServer

__handlers__ = {
    "http": handlers.httphandler.HttpHandler
}

class CustomTCPServer(TCPServer):
    def __init__(self, addr: tuple, no_block: bool, handler):
        TCPServer.__init__(self, addr, handler)
        if no_block:
            self.socket.setblocking(False)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, 0)

class ProxyServer(Thread, CustomTCPServer):
    THREAD_NAME = "pryxy-server"
    THREAD_POLL_INTERVAL = 2

    def __init__(self, host: str, port: int, proto: str, no_block: bool):
        Thread.__init__(self)
        CustomTCPServer.__init__(self, (host, port), no_block, __handlers__[proto])
        self._active = False
        self._proto = proto
        self.setName(ProxyServer.THREAD_NAME)
        self._shutdown_signal = False
        signal.signal(signal.SIGINT, self._close)
        signal.signal(signal.SIGTERM, self._close)
    
    def run(self):
        safeprint.log("starting listener {}".format(str(self)))
        self._active = True
        self.serve_forever(ProxyServer.THREAD_POLL_INTERVAL)
        safeprint.log("listener closed")
        
    def await_shutdown(self):
        """awaits for a shutdown signal to proceed"""
        safeprint.log("awaiting proxy shutdown...")
        while self._active:
            time.sleep(ProxyServer.THREAD_POLL_INTERVAL)

    def _close(self, signum, frame):
        if not self._shutdown_signal:
            self._shutdown_signal = True
            safeprint.log("received SIG %i, shutting down proxy..." % signum)
            self.shutdown()
            self._active = False

    def __str__(self):
        return ProxyServer.THREAD_NAME + ("@%s:%d proto: " % self.socket.getsockname() + self._proto)
    
    def __repr__(self):
        return self.__str__()

def main(args):
    parser = argparse.ArgumentParser(args[0], description="Simple python proxy server for development, debug and testing")
    parser.add_argument("-a", "--host", action="store", type=str, default="127.0.0.1", help="the proxy's host/address to listen on")
    parser.add_argument("-p", "--port", action="store", type=int, default=80, help="the proxy's port to listen on")
    parser.add_argument("-x", "--proto", action="store", type=str, default="http", help="the proxy's protocol to work with (http only)")
    parser.add_argument("-d", "--directory", action="store", type=str, default="./", help="the root directory to look for json rules")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="logs expressive information during execution")
    parser.add_argument("--no-block", action="store_true", default=False, help="""will not wait for client's connection shutdown to 
            close the server. WARNING: This may result in the TCP connection lingering on the client's side""")
    result_args = parser.parse_args()
    safeprint.setup(result_args.verbose, __debug__)
    handlers.jsonrules.setup(result_args.directory)
    pryxy = ProxyServer(result_args.host, result_args.port, result_args.proto, result_args.no_block)
    pryxy.start()
    pryxy.await_shutdown()
    pryxy.join()

main(sys.argv)