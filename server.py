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
    #intialize instance variables.
    responseHeader = ""
    responseContent = ""
    ctype = ""
    root_path = os.getcwd()
    request_path = ""
    statusCode = {  200:'OK',
                    301:'MOVED PERMANENTLY',
                    404:'NOT FOUND',
                    405:'METHOD NOT ALLOWED',
                    501:'NOT IMPLEMENTED'}
    contentType = {'html':'Content-Type: text/html;charset=utf-8\r\n',
                   'css':'Content-Type: text/css;charset=utf-8\r\n',
                   'default': 'Content-Type: application/octet-stream;charset=utf-8\r\n'}
    implementedMethods = ['GET']

    #This method handles a simple HTTP request from connection at a time.
    def handle(self):
        print("Connected by", self.client_address)
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)

        #ignore empty message received.
        if not self.data:
            return

        #parse request to get header infomation.
        try :
            header = self.data.decode('utf-8').split('\r\n')
            self.method, path, self.httpVersion = header[0].split(' ')
        except:
            print("Error: Unknown request.")
            return
        
        #Base path <- /www
        baseDir = '/www'

        #return index.html from directories.
        if path.endswith("/"):
            path += 'index.html'
        #Parse url to get directory and filename, respectively.
        pathComponents = path.rsplit('/', 1)
        directory, content_filename = baseDir + pathComponents[0], pathComponents[1]
        
        #print('code = ' + self.method + ' directory = "' + directory + '" content_filename = ' + content_filename + ' version = ' + self.httpVersion)
        
        if self.method in self.implementedMethods:
            #handle a GET request
            if self.method == 'GET':
                self.do_GET(directory, content_filename)
        else:
            #handle unimplemented reuqests
            response = self.get_response(405)
            self.request.sendall(response.encode('utf-8'))

    #This method handles a GET request. 
    #It takes a directory of requested url and 
    #a filename as arguments.
    def do_GET(self, directory, content_filename):
        response = None
        self.request_path = '.' + directory + '/' + content_filename

        #check if reuqested url is under server working directory.
        if not os.path.abspath(self.request_path).startswith(self.root_path):
            #Bad request url. Set response code <- 404
            code = 404
        else:
            try:
                #Case 1: Read content successfully. Set response code <- 200
                f = open(self.request_path, 'r')
                self.responseContent = f.read()
                f.close()
                code = 200
            #Case 2: File does not exist. Set response code <- 404
            except FileNotFoundError:
                print("File Not Found.")
                code = 404
            #Case 3: request url is a directory. Set response code <- 301
            except IsADirectoryError:
                print("Is A Directory.")
                code = 301
        
        response = self.get_response(code)
        if response:
            print("sending...\n" + response)
            self.request.sendall(response.encode('utf-8'))
        return

    #This method takes an argument code and set the status line
    #of response according to the code.
    def set_status_line(self, code):
        statusLinePattern = '{} {} {}\r\n'
        self.statusLine = statusLinePattern.format(
            self.httpVersion, str(code), self.statusCode[code])
        return 

    #This method takes an int code as argument.
    #It constructs and returns a response according to the code.
    def get_response(self, code):
        response = None
        #Set status line.
        self.set_status_line(code)

        #Set Content-Length
        self.responseHeader += 'Content-Length: ' + \
            str(len(self.responseContent)) + '\r\n'
        
        #Set Content-Type
        if self.request_path.endswith('.html'):
            self.responseHeader += self.contentType['html']
        elif self.request_path.endswith('.css'):
            self.responseHeader += self.contentType['css']
        else:
            self.responseHeader += self.contentType['default']  #maybe something else.

        #set client error body.
        if 400 <= code <= 499:
            self.responseContent = ""
        #set redirection body.
        elif code == 301:
            self.responseHeader += 'Location: ' + \
                self.request_path[5:] + '/\r\n'
        
        response = self.statusLine + self.responseHeader + '\r\n' + self.responseContent

        return response

            
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
