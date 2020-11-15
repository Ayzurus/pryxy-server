#!/bin/bash
# SERVER.SH - Runs the server in CLI for unix
# args:
# - 1. Host/address for the proxy to listen on
# - 2. Port for the proxy to listen on
# - 3. Protocol (only http)
host="localhost"
port="80"
proto="http"
python src/proxyserver.py --host $host --port $port --proto $proto
echo "press any key to continue..."
read -rsn1