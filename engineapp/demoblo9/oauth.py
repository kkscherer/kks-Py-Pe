# coding=utf8
"""
A simple OAuth implementation for authenticating users with third party
websites.
@author: Mike Knapp <micknapp@gmail.com>
@copyright: Unrestricted. Feel free to use modify however you see fit.
@url: http://github.com/mikeknapp/AppEngine-OAuth-Library
"""

import logging
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import db
from cgi import parse_qs
from django.utils import simplejson as json
from hashlib import sha1
from hmac import new as hmac
from random import getrandbits
from time import time
from urllib import unquote as urlunquote


from urllib_utf8 import encode, urlencode
import Session


consumer_key =    {
                   'twitter': '',
                   'myspace': '',
                   'google' : '',
                   'yahoo'  : '',
                   }

consumer_secret = {
                   'twitter': '',
                   'myspace': '',
                   'google' : '',
                   'yahoo'  : '',
                   }

callback_url =    {
                   'twitter': '/twitter/callback',
                   'myspace': '/myspace/callback',
                   'google' : '/google/callback',
                   'yahoo'  : '/yahoo/callback',
                   }


class OAuthClient():

    __public__ = ('callback', 'cleanup', 'login', 'logout')

    def __init__(self, name, consumer_key, consumer_secret, request_url,
                 access_url, session, callback_url=None):
        self.name            = name
        self.consumer_key    = consumer_key
        self.consumer_secret = consumer_secret
        self.request_url     = request_url
        self.access_url      = access_url
        self.session         = session
        self.callback_url    = callback_url


    def make_request(self, url, token='', secret='', additional_params={},
                           protected=False, method='GET', payload=''):

        method = method.upper()
        params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_signature_method': "HMAC-SHA1",
            'oauth_timestamp': str(int(time())),
            'oauth_nonce': str(getrandbits(64)),
            'oauth_version': "1.0"
        }

        params.update(additional_params)

        if token: params["oauth_token"] = token
        elif self.callback_url: params["oauth_callback"] = self.callback_url

        message = u'&'.join(map(encode, [method, url, u'&'.join('%s=%s' % (encode(k), encode(params[k])) for k in sorted(params))]))
        key = "%s&%s" % (self.consumer_secret, secret) # Note compulsory "&".
        params["oauth_signature"] = hmac(key, message, sha1).digest().encode('base64')[:-1]

        headers = {}
        if protected: headers['Authorization'] = 'OAuth'

        payload = urlencode(params)

        if method == 'GET':
            return urlfetch.fetch("%s?%s" % (url, urlencode(params)), headers=headers, method=method)
        elif method == 'POST':
            return urlfetch.fetch(url, payload=payload, headers=headers, method=method)
        else:
            raise UserWarning, 'Method %s not implemented. Please use GET or POST' % method


    def get_authorization_url(self):
        raise NotImplementedError, "Must be implemented by a subclass"


    def get_user_info(self, auth_token, auth_verifier=''):
        auth_token = urlunquote(auth_token)
        auth_verifier = urlunquote(auth_verifier)
        auth_secret = memcache.get(self._get_memcache_auth_key(auth_token))
        if not auth_secret:
            result = Session.SessionData.gql('WHERE %s_oauth_token = :1 LIMIT 1' % (self.name), auth_token).get()
            if result: auth_secret = result.secret

        response = self.make_request(self.access_url,
                                     token=auth_token,
                                     secret=auth_secret,
                                     additional_params={'oauth_verifier': auth_verifier})
        result = self._extract_credentials(response)
        self.update_auth(result['token'], result['secret'])
        user_info = self._lookup_user_info(result['token'], result['secret'])
        return user_info


    def _get_auth_token(self):
        response = self.make_request(self.request_url)
        result = self._extract_credentials(response)
        auth_token = result['token']
        auth_secret = result['secret']
        logging.info('Storing auth_token %s in Memcache' % auth_token)
        memcache.set(self._get_memcache_auth_key(auth_token), auth_secret, time=20)
        return auth_token


    def _get_memcache_auth_key(self, auth_token):
        key = "oauth_%s_%s" % (self.name, auth_token)
        logging.info("_get_memcache_auth_key(): %s" % key)
        return key


    def _extract_credentials(self, result):
        token = None
        secret = None
        parsed_results = parse_qs(result.content)

        if "oauth_token" in parsed_results:
          token = parsed_results["oauth_token"][0]

        if "oauth_token_secret" in parsed_results:
          secret = parsed_results["oauth_token_secret"][0]

        if not (token and secret) or result.status_code != 200:
          logging.error("Could not extract token/secret: %s" % result.content)
          raise Exception, "Problem talking to the service"

        return {
          'token':   token,
          'secret':  secret
        }


    def _lookup_user_info(self, access_token, access_secret):
        raise NotImplementedError, 'Must be implemented by a subclass'


    def _get_default_user_info(self):
        return {
          "id": "",
          "username": "",
          "name": "",
          "picture": ""
        }


class TwitterClient(OAuthClient):
    def __init__(self, session, reqh):
        cb = '%s%s' % (reqh.request.application_url, callback_url['twitter'])
        logging.info('TwitterClient CALLBACK URL = %s' % cb)
        OAuthClient.__init__(self,
            'twitter',
            consumer_key['twitter'],
            consumer_secret['twitter'],
            "https://twitter.com/oauth/request_token",
            "https://twitter.com/oauth/access_token",
            session,
            cb)

    def get_authorization_url(self):
        token = self._get_auth_token()
        return "https://twitter.com/oauth/authorize?oauth_token=%s" % token


    def update_auth(self, auth_token, auth_secret):
        if self.session.data is None:
            raise UserWarning, 'session.data is None'
        else:
            self.session.data.twitter_oauth_token  = auth_token
            self.session.data.twitter_oauth_secret = auth_secret
            self.session.data.put()


    def _lookup_user_info(self, access_token, access_secret):
        response = self.make_request(
            "https://twitter.com/account/verify_credentials.json",
            token=access_token, secret=access_secret, protected=True)
        data = json.loads(response.content)
        user_info = self._get_default_user_info()
        user_info['id'] = data['id']
        user_info['username'] = data['screen_name']
        user_info['name'] = data['name']
        user_info['picture'] = data['profile_image_url']
        user_info['url'] = data['url']
        user_info['name'] = data['name']
        user_info['created_at'] = data['created_at']
        user_info['location'] = data['location']
        user_info['description'] = data['description']
        user_info['utc_offset'] = data['utc_offset']
        user_info['time_zone'] = data['time_zone']
        return user_info



class MyspaceClient(OAuthClient):
    def __init__(self, session, reqh):
        OAuthClient.__init__(self,
                'myspace',
                consumer_key['myspace'],
                consumer_secret['myspace'],
                "http://api.myspace.com/request_token",
                "http://api.myspace.com/access_token",
                session,
                '%s%s' % (reqh.request.application_url, callback_url['myspace']))


    def update_auth(self, auth_token, auth_secret):
        if self.session.data is None:
            raise UserWarning, 'session.data is None'
        else:
            self.session.data.myspace_oauth_token  = auth_token
            self.session.data.myspace_oauth_secret = auth_secret
            self.session.data.put()


    def get_authorization_url(self):
        token = self._get_auth_token()
        # logging.info("get_authorization_url(): token='%s'" % token)
        return "http://api.myspace.com/authorize?oauth_token=%s&oauth_callback=%s" % (token, encode(self.callback_url))


    def _lookup_user_info(self, access_token, access_secret):
        response = self.make_request("http://api.myspace.com/v1/user.json",
                token=access_token, secret=access_secret, protected=True)
        data = json.loads(response.content)
        user_info = self._get_default_user_info()
        username = data['webUri'].replace("http://www.myspace.com/", "")
        user_info['username'] = username
        user_info['id']       = data['userId']
        user_info['name']     = data['name']
        user_info['picture']  = data['image']
        return user_info


class YahooClient(OAuthClient):
    def __init__(self, session, reqh):
        OAuthClient.__init__(self,
                'yahoo',
                consumer_key['yahoo'],
                consumer_secret['yahoo'],
                "https://api.login.yahoo.com/oauth/v2/get_request_token",
                "https://api.login.yahoo.com/oauth/v2/get_token",
                session,
                '%s%s' % (reqh.request.application_url, callback_url['yahoo']))


    def get_authorization_url(self):
        token = self._get_auth_token()
        return "https://api.login.yahoo.com/oauth/v2/request_auth?oauth_token=%s" % token


    def update_auth(self, auth_token, auth_secret):
        if self.session.data is None:
            raise UserWarning, 'session.data is None'
        else:
            self.session.data.yahoo_oauth_token = auth_token
            self.session.datayahoo_oauth_secret = auth_secret
            self.session.data.put()


    def _lookup_user_info(self, access_token, access_secret):
        user_info = self._get_default_user_info()
        # 1) Obtain the user's GUID.
        response = self.make_request(
                "http://social.yahooapis.com/v1/me/guid", token=access_token,
                secret=access_secret, additional_params={"format": "json"},
                protected=True)
        data = json.loads(response.content)["guid"]
        guid = data["value"]
        # 2) Inspect the user's profile.
        response = self.make_request(
                "http://social.yahooapis.com/v1/user/%s/profile/usercard" % guid,
                 token=access_token, secret=access_secret,
                 additional_params={"format": "json"}, protected=True)
        data = json.loads(response.content)["profile"]
        user_info['id']       = guid
        user_info['username'] = data['nickname'].lower()
        user_info['name']     = data['nickname']
        user_info['picture']  = data['image']['imageUrl']
        return user_info
