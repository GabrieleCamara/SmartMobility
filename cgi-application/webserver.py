#!/usr/bin/python
 
import BaseHTTPServer
import CGIHTTPServer
 

handler = CGIHTTPServer.CGIHTTPRequestHandler
server_address = ("", 8000)
server = BaseHTTPServer.HTTPServer
 
httpd = server(server_address, handler)
httpd.serve_forever()