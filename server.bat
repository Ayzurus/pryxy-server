@echo off
rem SERVER.BAT - Runs the server in CLI for windows
rem args:
rem - 1. Host/address for the proxy to listen on
rem - 2. Port for the proxy to listen on
rem - 3. Protocol (only http)
set host=localhost
set port=80
set proto=http
call python src\proxyserver.py --host %host% --port %port% --proto %proto%
pause