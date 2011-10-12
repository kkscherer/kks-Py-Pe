#! /usr/bin/env python

# Our tutorial's WSGI server
# from wsgiref.simple_server import make_server
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

def env_application():

   # Sorting and stringifying the environment key, value pairs
   response_body = ['%s: %s' % (key, value)
                    for key, value in sorted(environ.items())]
   response_body = '\n'.join(response_body)

   response_body = response_body + '\nThe End\n'
   
   status = '200 OK'
   response_headers = [('Content-Type', 'text/plain'),
                  ('Content-Length', str(len(response_body)))]
   start_response(status, response_headers)

   return [response_body]
"""
# Instantiate the WSGI server.
# It will receive the request, pass it to the application
# and send the application's response to the client
httpd = make_server(
   'localhost', # The host name.
   8051, # A port number where to wait for the request.
   env_application # Our application object name, in this case a function.
   )

# Wait for a single request, serve it and quit.
httpd.handle_request()
"""
def main():
    application = webapp.WSGIApplication([('/',env_application )],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
