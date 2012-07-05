# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: UrlShortener.py 3e8a10e0791e 2009/11/25 15:26:47 Oliver Lau <oliver@von-und-fuer-lau.de> $

import os
import logging
from google.appengine.api import urlfetch
from django.utils import simplejson as json
from urllib_utf8 import encode


URL_SHORTENER_SETTINGS = {
    'bit.ly': {
        'url'   : 'http://api.bit.ly/shorten',
        'login' : '',
        'apiKey': ''
    },
}


def shortenUrl(longUrl, service='bit.ly'):
    if service == 'bit.ly':
        params = {
             'login'  : URL_SHORTENER_SETTINGS['bit.ly']['login'],
             'apiKey' : URL_SHORTENER_SETTINGS['bit.ly']['apiKey'],
             'version': '2.0.1',
             'format' : 'json'
        }
        url = '%s?%s&longUrl=%s' % (URL_SHORTENER_SETTINGS['bit.ly']['url'],
                                    '&'.join('%s=%s' % (k, params[k]) for k in params), encode(longUrl))
        response = urlfetch.fetch(url)
        if response:
            result = json.loads(response.content)
            if result['errorCode'] == 0:
                return result['results'][longUrl]['shortUrl']

    elif service == 'is.gd':
        url = '%s?longurl=%s' % (URL_SHORTENER_SETTINGS['is.gd']['url'], encode(longUrl))
        response = urlfetch.fetch(url)
        if response:
            if response.content.find('http://is.gd/') == 0:
                return response.content

    elif service == 'tinyurl.com':
        url = '%s?url=%s' % (URL_SHORTENER_SETTINGS['tinyurl.com']['url'], encode(longUrl))
        response = urlfetch.fetch(url)
        if response:
            if response.content.find('http://tinyurl.com/') == 0:
                return response.content

    return None
