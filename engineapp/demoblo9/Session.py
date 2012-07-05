# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: Session.py b72d72533281 2009/12/09 16:30:09 Oliver Lau <oliver@von-und-fuer-lau.de> $

import logging
from datetime import timedelta, datetime
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
from JSONProperty import JSONProperty

DEFAULT_COOKIE_NAME = 'SESSIONID'
DEFAULT_COOKIE_LIFETIME = 14*24*60*60


class SessionData(db.Model):
    user = db.UserProperty()
    cookiename = db.StringProperty(required=True)
    expires = db.DateTimeProperty(auto_now_add=True)
    myspace_data = JSONProperty()
    myspace_oauth_token = db.StringProperty()
    myspace_oauth_secret = db.StringProperty()
    twitter_data = JSONProperty()
    twitter_oauth_token = db.StringProperty()
    twitter_oauth_secret = db.StringProperty()
    yahoo_data = JSONProperty()
    yahoo_oauth_token = db.StringProperty()
    yahoo_oauth_secret = db.StringProperty()


class OAuth(db.Model):
    session = db.ReferenceProperty(SessionData, required=True)
    service = db.StringProperty(required=True)
    data = JSONProperty()
    token = db.StringProperty()
    secret = db.StringProperty()

    def __init__(self, **kwargs):
        super(OAuth).__init__(**kwargs)
        self.service = kwargs['service']


class Session:
    data = None

    # @param rh: response handler of the page owning the session
    # @param user: user owning the session (type = db.UserProperty())
    # @param cookiename: cookie name
    # @param timeout: session timeout in seconds
    def __init__(self, rh, user=None, cookiename=DEFAULT_COOKIE_NAME, timeout=DEFAULT_COOKIE_LIFETIME):
        # Cookie in der Cookie-Liste suchen
        if cookiename in rh.request.cookies.keys():
            # Cookie gefunden, Sitzungsdaten laden
            key = rh.request.cookies[cookiename]
            try:
                self.data = SessionData.get(key)
            except db.BadRequestError, e:
                logging.exception(e)
            if self.data is not None:
                if self.data.user != user:
                    self.data.user = user
                    self.data.put()
        if self.data is None:
            # keine Sitzungsdaten vorhanden, neues Cookie generieren
            expiry = datetime.utcnow() + timedelta(seconds=timeout%(24*60*60), days=timeout/(24*60*60))
            self.data = SessionData(user=user, cookiename=cookiename, expires=expiry)
            self.data.put()
            cookie = "%s=%s; expires=%s; path=/" % (self.data.cookiename, self.data.key(), expiry.strftime('%a, %d-%b-%Y %H:%M:%S UTC'))
            rh.response.headers.add_header('Set-Cookie', cookie)


    def id(self):
        if self.data is not None:
            return self.data.key();
        return None
