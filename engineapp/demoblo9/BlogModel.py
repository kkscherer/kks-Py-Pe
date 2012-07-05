# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: BlogModel.py e8cfa4c95f1f 2009/12/17 16:08:20 Oliver Lau <oliver@von-und-fuer-lau.de> $

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from datetime import datetime

from urllib_utf8 import nicen

class Entry(db.Model):
    author = db.UserProperty()
    content = db.TextProperty()
    title = db.StringProperty()
    intro = db.StringProperty(required=False)
    permalink = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now_add=True, required=True)
    changed_at = db.DateTimeProperty(auto_now_add=True, indexed=False)
    tags = db.StringListProperty()
    published = db.BooleanProperty(default=True)
    publish_in_timeline = db.BooleanProperty(default=True)
    posted_to_twitter = db.BooleanProperty(default=False)
    posted_to_yahoo   = db.BooleanProperty(default=False)
    posted_to_myspace = db.BooleanProperty(default=False)


    def nice_title(self):
        return "%s-%s" % (self.created_at.strftime('%Y%m%d%H%M%S'), nicen(self.title))

    def put(self):
        if not self.is_saved():
            self.permalink = self.nice_title()
        return super(Entry, self).put()

    @staticmethod
    def flushTagList():
        memcache.delete('tags')

    @staticmethod
    def makeTagList():
        allEntries = Entry.all()
        tags = {}
        for entry in allEntries:
            for tag in entry.tags:
                if tag in tags:
                    tags[tag]['count'] += 1
                else:
                    tags[tag] = { 'count': 0 }
        maxTagCount = -1
        for key in tags.keys():
            if tags[key]['count'] > maxTagCount:
                maxTagCount = tags[key]['count']
        if maxTagCount > -1:
            minSize, maxSize = 90, 180
            if maxTagCount == 0: maxTagCount = 1
            f = float(maxSize-minSize)/maxTagCount
            for key in tags.keys():
                tags[key]['size'] = str(minSize +
                    int(f*(tags[key]['count']))) + '%'
        tagList = []
        for key, value in tags.items():
            tagList.append({ 'tag'  : key.encode('utf-8'),
                             'count': value['count'],
                             'size' : value['size'] })
        return tagList

    @staticmethod
    def getTagList():
        tagList = memcache.get('tags')
        if tagList is None:
            tagList = Entry.makeTagList()
            memcache.add('tags', tagList)
        return tagList



class UrlMapping(db.Model):
    url = db.StringProperty(required=True)
    created_at = db.DateTimeProperty(auto_now_add=True)

    def __init__(self, url):
        db.Model.__init__(self)
        self.url = url

    def id(self):
        return self.key().id()

    def url(self):
        return self.url



class Comment(db.Model):
    for_entry = db.ReferenceProperty(Entry, required=True)
    text = db.TextProperty(required=True)
    author = db.UserProperty(required=True)

    def __init__(self, args, **kwargs):
        super(Comment, self).__init__(args, **kwargs)
