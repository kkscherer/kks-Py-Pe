from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from os import environ

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        hello = self.request.get('gr')
        if not hello:
            hello = 'Hello'

        if user:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(hello + ' , ' + user.nickname())
            if user.nickname().lower().find('kks') >= 0:
                self.response.out.write('</br>authorized</br>')
            self.response.out.write( self.request.arguments())
            for k in self.request.arguments():
                self.response.out.write("</br>" + k + ":" + self.request.get(k))
        else:
            self.redirect(users.create_login_url(self.request.uri))

application = webapp.WSGIApplication([('/.*', MainPage)],
                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

