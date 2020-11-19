#!/bin/bash
# SERVER.SH - Runs the server in CLI for unix
# args:
# - 1. Host/address for the proxy to listen on
# - 2. Port for the proxy to listen on
# - 3. Protocol (only http)
# - 4. Working directory, where the handler rules are located
host="localhost"
port="80"
proto="http"
directory="$(pwd)/example/"
python -OO src/proxyserver.py -a $host -p $port -x $proto -d $directory
echo "press any key to continue..."
read -rsn1