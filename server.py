#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    responseHeader = ""
    content = ""
    statusCode = {  200:'OK',
                    404:'NOT FOUND',
                    501:'NOT IMPLEMENTED'}

    def handle(self):
        print("Connected by", self.client_address)
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #why there is b'' request?
        if not self.data:
            return

        try :
            header = self.data.decode('utf-8').split('\r\n')
            self.method, path, self.httpVersion = header[0].split(' ')
        except:
            print("Error: Unknown request.")
            return
        
        #Base path <- /www/
        baseDir = '/www'

        if path.endswith("/"):
            path += 'index.html'

        pathComponents = path.rsplit('/', 1)
        path, content_file = baseDir + pathComponents[0], pathComponents[1]
        
        #print('code = ' + method + ' path = "' + path + '" content_file = ' + content_file + ' version = ' + http_version)
        if self.method == 'GET':
            self.do_GET(path, content_file)
        else:
            #handle NOT IMPLEMENTED
            pass
    
    def do_GET(self, path, content_file):
        response = None
        directory = '.' + path + '/' + content_file
        
        #ignore .ico request
        if content_file.endswith('.ico'):
            #print(".ico request ignored.")
            return
        try:
            f = open(directory, 'r')
            self.content = f.read()
            f.close()
            self.set_status_line(200)
        except NotADirectoryError:
            print("Not a directory.")
            self.set_status_line(404)
            #handle 404 NOT FOUND

        if content_file.endswith('.html'):
            self.responseHeader += 'Content-Type: text/html;charset=utf-8\r\n'
        elif content_file.endswith('.css'):
            self.responseHeader += 'Content-Type: text/css;charset=utf-8\r\n'
        
        self.responseHeader += 'Content-Length: ' + str(len(self.content)) + '\r\n'

        response = self.statusLine + self.responseHeader + '\r\n' + self.content
        if response:
            print("sending...\n" + response)
            self.request.sendall(response.encode('utf-8'))
        return

    def set_status_line(self, code):
        statusLinePattern = '{} {} {}\r\n'
        self.statusLine = statusLinePattern.format(
            self.httpVersion, str(code), self.statusCode[code])


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
