@echo off
rem SERVER.BAT - Runs the server in CLI for windows
rem args:
rem - 1. Host/address for the proxy to listen on
rem - 2. Port for the proxy to listen on
rem - 3. Protocol (only http)
rem - 4. Working directory, where the handler rules are located
set host=localhost
set port=80
set proto=http
set directory=%cd%\example\
call python src\proxyserver.py -a %host% -p %port% -x %proto% -d %directory%
pause