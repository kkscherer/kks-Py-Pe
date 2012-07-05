# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: blog.py 3948f2b7018e 2009/12/21 08:42:59 Oliver Lau <oliver@von-und-fuer-lau.de> $

__author__ = 'Oliver Lau'


"""
TODO:

  * Registrierung von Benutzern. Nur registrierte Benutzer dürfen Kommentare schreiben et cetera
    * Kommentarfunktion
      * Moderator via E-Mail über neuen Kommentar informieren
      * Moderator kann Kommentare sperren
  * Blog-Beiträge à la Posterous.com via E-Mail empfangen
  * beim Upload kann ein bestehender BLOB nicht durch den neu hochgeladenen ersetzt werden?
  * Volltextsuche über Blog-Beiträge

"""


import os, sys

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

# Force sys.path to have our own directory first, so we can import from it.
# sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import Page

def main():
    application = webapp.WSGIApplication(
        [
            ('/',                  Page.Index),
            ('/manage/(\w+)',      Page.Manage),
            ('/edit/(\w*)',        Page.Edit),
            ('/search/(.*)',       Page.Search),
            ('/delete/(\w+)',      Page.Delete),
            ('/show/(\w+)',        Page.Show),
            ('/display/([^/]+)?',  Page.Display),
            ('/-([^/]+)?',         Page.Display),
            ('/get/([^/]+)?',      Page.ServeHandler),
            ('/doupload',          Page.UploadHandler),
            ('/upload/([^/]+)?',   Page.UploadFormHandler),
            ('/unload/([^/]+)?',   Page.UnloadHandler),
            ('/flush/(\w+)/(\w+)', Page.Flush),
            ('/info',              Page.Infos),
            ('/init/(\w+)',        Page.Init),
            ('/google/(\w+)',      Page.GoogleHandler),
            ('/myspace/(\w+)',     Page.MyspaceHandler),
            ('/twitter/(\w+)',     Page.TwitterHandler),
            ('/yahoo/(\w+)',       Page.YahooHandler),
            ('/export',            Page.ExportHandler),
            ('/import',            Page.ImportHandler),
            ('/error/(.*)',        Page.ErrorHandler),
        ],
        debug=True)
    util.run_wsgi_app(application)


if __name__ == "__main__":
    main()
