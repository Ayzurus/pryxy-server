# Pryxy Server

Cross platform simple python proxy server for HTTP, up to version 1.1, related application testing and development.

Pryxy can be executed in any OS using python 3 OR bundled to a standalone executable via
pyinstaller to be run in any machine independent of python version or installation.

## Contents

  1. [Building](#1-building)
  2. [Contributing](#2-contributing)
  3. [Using](#3-using)
     1. [Running Pryxy](#running-pryxy)
     2. [Configuring Rules](#configuring-rules)
     3. [Automated Responses](#automated-responses)
  4. [License](#4-license)

## 1. Building

> NOTE: Building Pryxy by default requires [pyinstaller](https://www.pyinstaller.org/). You may bundle or compile with any other tool at your own volition.

To build the bundle just run the `build.bat`/`build.sh` script **OR** run the following command on the project's root:

```bash
pyinstaller -F --clean src/proxyserver.py
```

The resulting binary will be inside 'dist\\'.

## 2. Contributing

If you would like to contribute to the project, please follow this steps:

* Clone the repository to your machine
* Create a new branch
* Commit your changes in a proper way you see fit
* Push your branch to the repository
* Submit a pull request for reviewing
  * Please add a note in the pull request if you'd like to be credited for the changes

> NOTE: Do not commit changes to the default values in `server.bat`/`server.sh`, unless to add new values.

## 3. Using

### Running Pryxy

To run the server, for simplicity sake, there are 2 scripts, `server.bat` and `server.sh`, that allow to fast start the proxy on default values (address=`localhost`, port=`80`, protocol=`http`, directory=`./example/`).

This values can be changed in the scripts it self.

Otherwise, the server can be easily run from the root directory with the following command:

`python src/proxyserver.py [args]`

Or, if you installed the server via [pyinstaller](https://www.pyinstaller.org/) with the `build` script file:

`dist/proxyserver(.exe) [args]`

#### Arguments

All arguments are optional, and when one is not present, its default value is used.

* **-h, --help** = Show the arguments help text
* **-a, --host** = In which IPv4 host/address should the proxy listen on. Defaults to `127.0.0.1`
* **-p, --port** = In which port should the proxy listen on. Defaults to `80`
* **-x, --proto** = The protocol for the proxy to listen to (currently only supports HTTP). defaults to `http`
* **-d, --directory** = The effective directory containing the `.json` rule files for the handlers. Defaults to `./`
* **-v, --verbose** = Print more information with the logging process. Defaults to `False`

### Configuring Rules

#### The rules file

In order for the proxy to respond, it will require a configurated set of rules in a `.json` file. There is a simple example in the `example/` directory.

The configuration requires to have the name of the protocol used and since it is only possible to run the server for http, the rules file will be: `http.json`.

This file may be anywhere as long as you give the directory argument to which folder it is located.

#### Configurating rules

To create a rule, you just require the expected URI and the response code, a series of headers and a body, like in this example:

```json
{
  "GET /": {
    "code": 200,
    "Content-Type": "text/plain",
    "body": "HELLO WORLD!"
  }
}
```

This rule will respond to any "GET /" requests with a **200 Ok** response with the additional header **"Content-Type: text/plain"** and the content: **HELLO WORLD!**.

To respond with an error, you can use the `"reason"` tag to send a short message:

```json
{
  "GET /": {
    "code": 400,
    "reason": "I don't want to answer that..."
  }
}
```

> NOTE: The rules have a priority from top to bottom, so in case of a collision, the first defined rule is picked

#### Wildcards

The wildcard `*` can be used for some configurations as in the following examples:

```json
{
  "GET*": {
    "code": 200,
    "Content-Type": "text/plain",
    "body": "I accept any get!"
  },
  "PUT /home/*": {
    "code": 200,
    "Content-Type": "text/plain",
    "body": "I accept PUT to any path inside /home/"
  },
  "* /root/": {
    "code": 401,
    "reason": "DON'T TOUCH THE ROOT FOLDER!"
  },
  "*": {
    "code": 400,
    "reason": "Everything else I reject"
  }
}
```
* **GET\***, any request starting with **"GET"** is responded with this rule.
* **PUT /home/\***, any PUT request to any directory inside `/home/`, is responded with this rule
* **\* /root/**, any request to the `/root/` directory is responded with this rule
* **\***, any OTHER request that does not fit in any of the above rules is handled with this rule

### Automated Responses

Pryxy does not support nor validate HTTP RFCs, headers or content, it serves mostly as a permissive simulation HTTP proxy in order to allow testing/development with multiple request-response scenarios.

With this said, there are some cases where Pryxy may respond not according to the configuration, these are:

* If the **"Expect: 100-continue"** header is present in an HTTP/1.1, Pryxy will send a **100 Continue**, to avoid to have the user configure responses for the [RFC 7231](https://tools.ietf.org/html/rfc7231) every time
* When the request does not present the command OR path, it responds with: **400 Bad Request**
* When a request times out, Pryxy will respond with: **408 Request Timeout**
* When the request's URI is too long, Pryxy will respond with: **414 URI Too Long**
* When the request's headers are too large OR too many: **431 Request Header Fields Too Large**
* When there are no configured rules to the given request (including default "*"), it will respond with: **501 Not Implemented**
* And finally, if the request's HTTP version is 2.0 or above: **505 HTTP Version Not Supported**

> NOTE: This is subject to change in the future, if features to add request validations or the like are implemented

## 4. License

MIT License

Copyright (c) 2020 Ayzurus

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
