# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: Page.py 3948f2b7018e 2009/12/21 08:42:59 Oliver Lau <oliver@von-und-fuer-lau.de> $

import os, logging, sys, re, urllib
import inspect
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.labs import taskqueue
from django.utils import simplejson as json
from UrlShortener import shortenUrl
from datetime import datetime

import BlogModel, Permissions
from DatastoreUtils import Importer, Exporter
from Session import Session, SessionData
from oauth import TwitterClient, YahooClient, MyspaceClient
from urllib_utf8 import htmlentities, encode

"""
Globals
"""

PROJECT = 'demoblo9'

TEMPLATES = {
             'index': 'templates/%s/index.html' % PROJECT,
             'manageblogentries': 'templates/%s/manageblogentries.html' % PROJECT,
             'manageresources': 'templates/%s/manageresources.html' % PROJECT,
             'show': 'templates/%s/show.html' % PROJECT,
             'edit': 'templates/%s/edit.html' % PROJECT,
             'import': 'templates/%s/import.html' % PROJECT,
             'export': 'templates/%s/export.html' % PROJECT,
             'upload': 'templates/%s/upload.html' % PROJECT,
             'error': 'templates/%s/error.html' % PROJECT,
             }


"""
Utility functions
"""

def cleanup(s):
    return unicode.strip(s)

def cleanupTags(tags):
    # unnötigen Whitespace löschen sowie Duplikate und Leereinträge tilgen
    return filter(lambda x: x != '', set(map(cleanup, tags.split(','))))

youtube = re.compile(r'http:\/\/www\.youtube\.com\/watch\?v=(\w+)', re.MULTILINE | re.UNICODE)

def beautify(content):
    return youtube.sub(r'<object width="425" height="344"><param name="movie" value="http://www.youtube.com/watch?v=\1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/\1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>', content)


def permalink(reqh, title):
    return "%s/-%s" % (reqh.request.host_url, title)


"""
Utility classes
"""

class GoogleAuthInfo:
    email    = None
    nickname = None
    id       = None
    url      = None
    admin    = False

    def __init__(self, user, redirect):
        if user:
            self.email    = user.email()
            self.nickname = user.nickname()
            self.id       = user.user_id()
            self.url      = users.create_logout_url('/')
            self.admin    = users.is_current_user_admin()
        else:
            self.url      = users.create_login_url(redirect)


"""
Page handler classes
"""

class Display(webapp.RequestHandler):

    def display(self, entry):
        user = users.get_current_user()
        session = Session(self, user)
        authinfo = GoogleAuthInfo(user, self.request.uri)
        if entry is not None:
            entry.created = entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
            entry.changed = entry.changed_at.strftime('%Y-%m-%d %H:%M:%S')
            entry.content = beautify(entry.content)
            template_values = {
                'title'   : entry.title,
                'entry'   : entry,
            }
            self.response.out.write(template.render(TEMPLATES['show'], template_values))
        else:
            self.response.set_status(404)
            self.response.out.write(u'Angeforderter Eintrag wurde nicht gefunden')


    def get(self, title):
        if title:
            entry = BlogModel.Entry.all().filter('permalink = ', title).get()
            self.display(entry)


class Show(Display):
    def get(self, key):
        if key:
            entry = BlogModel.Entry.get(key)
            self.display(entry)



class Init(webapp.RequestHandler):
    def get(self, what):
        self.response.headers.add_header('Content-type', 'text/plain')
        user = users.get_current_user()
        if user is None:
            self.response.set_status(403)
            self.response.out.write(u'Login erforderlich')
            return
        if not users.is_current_user_admin():
            self.response.set_status(403)
            self.response.out.write(u'Nur für Admins')
            return
        session = Session(self, user)

        if what == 'blog':
            #for entry in BlogModel.Entry.all():
            #    entry.permalink = entry.nice_title()
            #    entry.put()
            self.response.out.write(u"Löschen der bisherigen Beiträge ...\n")
            db.delete(BlogModel.Entry.all())
            BlogModel.Entry.flushTagList()

        elif what == 'permissions':
            f = open('raw/permissions.csv', 'r')
            if f is None:
                self.response.set_status(500)
                self.response.out.write(u'Datei mit den Berechtigungen fehlt')
                return
            self.response.out.write(u"Löschen der bisherigen Berechtigungen ...\n")
            db.delete(Permissions.Permission.all())
            self.response.out.write(u"Anlegen neuer Berechtigungen ...\n")
            for line in f:
                p = line.split(',')
                user            = users.User(email=p[0].strip().lower())
                is_admin        = p[1].strip().lower() in [ 'true', 'yes', '1' ]
                can_post        = p[2].strip().lower() in [ 'true', 'yes', '1' ]
                can_crosspost   = p[3].strip().lower() in [ 'true', 'yes', '1' ]
                can_import_blog = p[4].strip().lower() in [ 'true', 'yes', '1' ]
                can_export_blog = p[5].strip().lower() in [ 'true', 'yes', '1' ]
                can_upload      = p[6].strip().lower() in [ 'true', 'yes', '1' ]
                perm = Permissions.Permission(user=user,
                                              is_admin=is_admin,
                                              can_post=can_post,
                                              can_crosspost=can_crosspost,
                                              can_import_blog=can_import_blog,
                                              can_export_blog=can_export_blog,
                                              can_upload=can_upload
                                              )
                perm.put()
                self.response.out.write(" - %s\n" % perm)

        self.response.out.write(u"OK.\n")


class Manage(webapp.RequestHandler):
    numEntries = 20

    def get(self, what):
        user = users.get_current_user()
        if user is None:
            self.response.set_status(403)
            self.response.out.write(u'Login erforderlich')
            return
        auth = GoogleAuthInfo(user, self.request.uri)
        if not auth.admin:
            self.response.set_status(403)
            self.response.out.write(u'Admin-Rechte erforderlich')
            return
        session = Session(self, user)
        if what == 'files':
            entries = BlobInfo.all()
            sortkey = 'creation'
        elif what == 'blog':
            entries = BlogModel.Entry.all()
            sortkey = 'created_at'
        else:
            self.response.set_status(403)
            self.response.out.write(u'Fehlerhafte URL')
            return
        if self.request.get('offset'):
            offset = int(self.request.get('offset'))
            if offset < 0: offset = 0
        else: offset = 0
        entryCount = entries.count()
        if offset > entryCount: offset = entryCount - 1
        oldOffset = offset
        nextOffset = offset + self.numEntries
        prevOffset = offset - self.numEntries
        if prevOffset < 0: prevOffset = 0
        entries = entries.order('-%s' % sortkey).fetch(self.numEntries, offset)
        if what == 'files':
            for entry in entries:
                entry.created = entry.creation.strftime('%d.%m.%Y %H:%M:%S')
        elif what == 'blog':
            for entry in entries:
                entry.created = entry.created_at.strftime('%d.%m.%Y %H:%M:%S')
                entry.changed = entry.changed_at.strftime('%d.%m.%Y %H:%M:%S')
                entry.author_nickname = entry.author.nickname()
                entry.content = beautify(entry.content)
                entry.permalink = permalink(self, entry.nice_title())
        template_values = {
            'authinfo'  : auth,
            'twitter'   : session.data.twitter_data,
            'myspace'   : session.data.myspace_data,
            'yahoo'     : session.data.yahoo_data,
            'user'      : user,
            'entries'   : entries,
            'nextOffset': nextOffset,
            'hasNext'   : nextOffset < entryCount,
            'prevOffset': prevOffset,
            'hasPrev'   : prevOffset >= 0 and oldOffset != 0,
            'permissions': Permissions.PermissionChecker(user),
        }
        if what == 'files':
            template_values['title'] = u'Dateien verwalten'
            self.response.out.write(template.render(TEMPLATES['manageresources'], template_values))
        elif what == 'blog':
            template_values['title'] = u'Blog-Einträge verwalten'
            self.response.out.write(template.render(TEMPLATES['manageblogentries'], template_values))


class Index(webapp.RequestHandler):
    numEntries = 10

    def display(self):
        errors = []
        if self.request.get('error'):
            errors.append(self.request.get('error'))
        user = users.get_current_user()
        session = Session(self, user)
        tag = self.request.get('tag')
        if self.request.get('offset'):
            offset = int(self.request.get('offset'))
            if offset < 0: offset = 0
        else: offset = 0
        auth = GoogleAuthInfo(user, self.request.uri)
        entries = BlogModel.Entry.all()\
            .filter('publish_in_timeline = ', True)\
            .filter('published = ', True)
        if tag != '':    entries = entries.filter('tags = ', tag)
        entryCount = entries.count()
        if offset > entryCount: offset = entryCount - 1
        oldOffset = offset
        nextOffset = offset + self.numEntries
        prevOffset = offset - self.numEntries
        if prevOffset < 0: prevOffset = 0
        entries = entries.order('-created_at').fetch(self.numEntries, offset)
        for entry in entries:
            entry.created = entry.created_at.strftime('%d.%m.%Y %H:%M:%S')
            entry.changed = entry.changed_at.strftime('%d.%m.%Y %H:%M:%S')
            entry.author_nickname = entry.author.nickname()
            entry.content = beautify(entry.content)
            entry.permalink = permalink(self, entry.nice_title())
        tags = BlogModel.Entry.getTagList()
        template_values = {
            'authinfo'   : auth,
            'twitter'    : session.data.twitter_data,
            'myspace'    : session.data.myspace_data,
            'yahoo'      : session.data.yahoo_data,
            'user'       : user,
            'selectedtag': tag,
            'entries'    : entries,
            'nextOffset' : nextOffset,
            'hasNext'    : nextOffset < entryCount,
            'prevOffset' : prevOffset,
            'hasPrev'    : prevOffset >= 0 and oldOffset != 0,
            'tags'       : tags,
            'title'      : PROJECT,
            'permissions': Permissions.PermissionChecker(user),
            'errors'     : errors,
            'msg'        : self.request.get('msg'),
        }
        self.response.out.write(template.render(TEMPLATES['index'], template_values))

    def get(self):
        self.display()

    def post(self):
        self.get()


class Search(Index):
    def get(self, pattern):
        self.display() # TODO: Suchergebnisse anzeigen


class ErrorHandler(webapp.RequestHandler):
    def get(self, errmsg):
        # self.redirect("/?error=%s" % errmsg)
        template_values = {
            'errmsg': urllib.unquote(errmsg),
        }
        self.response.out.write(template.render(TEMPLATES['error'], template_values))


class Edit(webapp.RequestHandler):
    informViaEmail = True

    def post(self, key):
        errors = []
        msg = None
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um einen Blog-Beitrag schreiben zu dürfen.'))
            return
        uauth = Permissions.PermissionChecker(user)
        if not uauth.can_post():
            self.redirect("/error/%s" % encode(u'Sie sind nicht berechtigt zum Schreiben von Blog-Beiträgen.'))
            return
        session  = Session(self, user)
        authinfo = GoogleAuthInfo(user, self.request.uri)
        autopost_twitter = self.request.get('autopost_twitter') in [ 'yes', 'true', '1' ]
        autopost_myspace = self.request.get('autopost_myspace') in [ 'yes', 'true', '1' ]
        autopost_yahoo   = self.request.get('autopost_yahoo')   in [ 'yes', 'true', '1' ]
        title    = self.request.get('title')
        intro    = self.request.get('intro')
        intro = re.sub("[\n\r]+", " ", intro)
        if len(intro) > 500:
            errors.append(u'Der Einleitungstext darf nicht länger als 500 Zeichen sein.')
            intro = intro[:500]
        content = self.request.get('content')
        tags = self.request.get('tags')
        published = self.request.get('published') in [ 'yes', 'true', '1' ]
        publish_in_timeline = self.request.get('publish_in_timeline') in [ 'yes', 'true', '1' ]
        changed_at = datetime.utcnow()
        created_at = None
        if self.request.get('created'):
            created = self.request.get('created')
            if re.match("\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}", created):
                created_at = datetime.strptime(created, '%d.%m.%Y %H:%M:%S')
            else:
                errors.append(u'Das Änderungsdatum muss im Format DD.MM.JJJJ hh:mm:ss vorliegen.')
        if not key:
            entry = BlogModel.Entry()
            if title and content:
                entry.author    = user
                entry.title     = title
                entry.content   = content
                entry.intro     = intro
                entry.published = published
                entry.publish_in_timeline = publish_in_timeline
                if tags != '':
                    entry.tags = cleanupTags(tags)
                    if len(entry.tags) > 0:
                        BlogModel.Entry.flushTagList()
                entry.put()
                if entry.is_saved():
                    if self.request.get('autopost_twitter') in [ 'yes', 'true', '1' ]:
                        taskqueue.add(url='/twitter/post',
                                      params={
                                              'key': entry.key(),
                                              'twitter_oauth_token': session.data.twitter_oauth_token,
                                              'twitter_oauth_secret': session.data.twitter_oauth_secret
                                              })
                    if self.informViaEmail:
                        message = mail.EmailMessage(
                            sender = user.email(),
                            subject = 'Neuer Post: %s' % title,
                            to = 'Oliver Lau <ola@ct.de>')
                        message.html = content
                        message.send()

        else:
            try:
                entry = db.get(key)
            except db.BadKeyError:
                self.redirect("/error/%s" % encode(u'Der angeforderte Blog-Beitrag konnte nicht gefunden werden.'))
                return
            if entry.intro is None: entry.intro = ''
            if entry.content is None: entry.content = ''
            if not entry:
                entry = BlogModel.Entry()
                key = None
            if title and content:
                entry.title   = title
                entry.content = content
                entry.intro   = intro
                entry.published = published
                entry.publish_in_timeline = publish_in_timeline
                if changed_at is not None: entry.changed_at = changed_at
                if created_at is not None: entry.created_at = created_at
                if tags:
                    submittedTags = cleanupTags(tags)
                    if submittedTags != entry.tags:
                        entry.tags = submittedTags
                        BlogModel.Entry.flushTagList()
                entry.put()
        if not entry.is_saved():
            entry.title   = ''
            entry.content = ''
            entry.intro   = ''
            entry.tags    = []
        else:
            entry.author_email = entry.author.email()
        if entry.tags:
            entry.tagList = entry.tags
        if entry.created_at:
            entry.created = entry.created_at.strftime('%d.%m.%Y %H:%M:%S')
        if entry.created_at:
            entry.changed = entry.changed_at.strftime('%d.%m.%Y %H:%M:%S')
        tags = BlogModel.Entry.getTagList()
        template_values = {
            'authinfo'  : authinfo,
            'twitter'   : session.data.twitter_data,
            'myspace'   : session.data.myspace_data,
            'yahoo'     : session.data.yahoo_data,
            'title'     : 'Beitrag editieren',
            'entry'     : entry,
            'tags'      : tags,
            'errors'    : errors,
            'msg'       : msg,
        }
        self.response.out.write(template.render(TEMPLATES['edit'], template_values))

    def get(self, key):
        self.post(key)


class Delete(webapp.RequestHandler):
    def get(self, key):
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um einen Blog-Beitrag löschen zu dürfen.'))
            return
        session = Session(self, user)
        if user:
            if key:
                entry = db.get(key)
                if entry:
                    if users.is_current_user_admin() or entry.author.user_id() == user.user_id():
                        db.delete(entry)
                        BlogModel.Entry.flushTagList()
        if self.request.get('goto'): self.redirect(self.request.get('goto'))
        else: self.redirect('/')


class Flush(webapp.RequestHandler):
    def get(self, where, what):
        self.response.headers.add_header('Content-type', 'text/plain')
        user = users.get_current_user()
        if user is None:
            self.response.set_status(403)
            self.response.out.write(u'Login erforderlich')
            return
        if not users.is_current_user_admin():
            self.response.set_status(403)
            self.response.out.write(u'Nur für Admins')
            return
        session = Session(self, user)
        if where == 'memcache':
            if what == 'tags':
                BlogModel.Entry.flushTagList()
                self.response.out.write("memcache 'tags' flushed.")


class Infos(webapp.RequestHandler):
    def get(self):
        # self.response.headers.add_header('Content-type', 'text/plain')
        if not users.is_current_user_admin():
            self.response.set_status(403)
            self.response.out.write(u'Nur für Admins')
            return
        self.response.out.write(self.request.environ)


class GoogleHandler(webapp.RequestHandler):
    def get(self, action):
        user = users.get_current_user()
        session = Session(self, user)
        pass # TODO


class MyspaceHandler(webapp.RequestHandler):
    def get(self, action):
        user = users.get_current_user()
        session = Session(self, user)
        oauthClient = MyspaceClient(session, self)
        if action == 'login':
            self.redirect(oauthClient.get_authorization_url())

        elif action == 'logout':
            session.data.myspace_data = None
            session.data.myspace_oauth_token = None
            session.data.myspace_oauth_secret = None
            session.data.put()
            referer = self.request.headers['Referer']
            if referer is None: referer = '/'
            self.redirect(referer)

        elif action == 'callback':
            logging.info("CALLBACK: %s" % self.request.query_string)
            oauth_token    = self.request.get('oauth_token')
            oauth_verifier = self.request.get('oauth_verifier')
            logging.info("OAUTH_TOKEN = %s" % oauth_token)
            logging.info("OAUTH_VERIFIER = %s" % oauth_verifier)
            user_info = oauthClient.get_user_info(oauth_token, oauth_verifier)
            session.data.myspace.data = user_info
            session.data.put()
            self.redirect('/')


class YahooHandler(webapp.RequestHandler):
    def get(self, action):
        user = users.get_current_user()
        session = Session(self, user)
        oauthClient = YahooClient(session, self)
        if action == 'login':
            self.redirect(oauthClient.get_authorization_url())

        elif action == 'logout':
            session.data.yahoo_data = None
            session.data.yahoo_oauth_token = None
            session.data.yahoo_oauth_secret = None
            session.data.put()
            referer = self.request.headers['Referer']
            if referer is None: referer = '/'
            self.redirect(referer)

        elif action == 'callback':
            oauth_token = self.request.get('oauth_token')
            oauth_verifier = self.request.get('oauth_verifier')
            user_info = oauthClient.get_user_info(oauth_token, oauth_verifier)
            session.data.yahoo_data = user_info
            session.data.put()
            self.redirect('/')


class TwitterHandler(webapp.RequestHandler):
    user = None
    session = None
    oauthClient = None

    def tweet(self, entry, twitter_oauth_token, twitter_oauth_secret):
        self.response.headers.add_header('Content-Type', 'text/x-json')
        callback = 'twitterCallback'
        shortenedUrl = shortenUrl('%s%s%s' % (self.request.application_url, '/-', entry.permalink))
        res = u'%s({})' % callback
        if shortenedUrl is None:
            res = u'%s({"key":"%s","error":"URL konnte nicht gekürzt werden. Bitte versuchen Sie es später noch einmal."})' % (callback, entry.key())
        else:
            cutoff = None
            ellipsis = ':'
            if (len(shortenedUrl) + len(entry.title)) > 138:
                cutoff = -len(shortenedUrl) - 2
                ellipsis = u'\u8230'
            status =  u'%s%s %s' % (entry.title[:cutoff], ellipsis, shortenedUrl)
            result = self.oauthClient.make_request('https://twitter.com/statuses/update.json',
                                                   token=twitter_oauth_token,
                                                   secret=twitter_oauth_secret,
                                                   additional_params={ 'status': status },
                                                   method='POST')
            if result.status_code == 200:
                d = json.loads(result.content)
                if d['text']:
                    d['key'] = str(entry.key())
                    entry.posted_to_twitter = True
                    entry.put()
                    res = '%s(%s)' % (callback, json.dumps(d))
                else:
                    res = u'%s({"key":"%s","error":"In der Daten von Twitter fehlt das \'text\'-Feld."})' % (callback, entry.key())
            else:
                res = u'%s({"key":"%s","error":"Laden der Daten von Twitter resultierte im Fehler %d."})' % (callback, entry.key(), result.status_code)
        self.response.out.write(res)


    def get(self, action):
        self.user = users.get_current_user()
        self.session = Session(self, self.user)
        self.oauthClient = TwitterClient(self.session, self)
        if action == 'login':
            self.redirect(self.oauthClient.get_authorization_url())

        elif action == 'logout':
            self.session.data.twitter_data = None
            self.session.data.twitter_oauth_token = None
            self.session.data.twitter_oauth_secret = None
            self.session.data.put()
            referer = self.request.headers['Referer']
            if referer is None: referer = '/'
            self.redirect(referer)

        elif action == 'callback':
            oauth_token = self.request.get('oauth_token')
            oauth_verifier = self.request.get('oauth_verifier')
            logging.info("OAUTH_TOKEN = %s" % oauth_token)
            user_info = self.oauthClient.get_user_info(oauth_token, oauth_verifier)
            self.session.data.twitter_data = user_info
            self.session.data.put()
            self.redirect('/')

        elif action == 'post':
            key = self.request.get('key')
            if key:
                entry = db.get(key)
                if not entry:
                    self.response.out.write(u"%s({'error':'No matching entry found for key %s'})" % (callback, key))
                    return
                if entry.published == False:
                    self.response.out.write(u"%s({'error':'Entry with key %s: published status is %s'})" % (callback, key, entry.published))
                    return
                oauth_token = self.session.data.twitter_oauth_token
                if not oauth_token: oauth_token = self.request.get('twitter_oauth_token')
                if not oauth_token:
                    self.response.out.write(u"%s({'error':'Session/params is missing twitter_oauth_token'})" % callback)
                    return
                oauth_secret = self.session.data.twitter_oauth_secret
                if not oauth_secret: oauth_secret = self.request.get('twitter_oauth_secret')
                if not oauth_secret:
                    self.response.out.write(u"%s({'error':'Session/params is missing twitter_oauth_secret'})" % callback)
                    return
                self.tweet(entry, oauth_token, oauth_secret)
            else:
                logging.error("/twitter/post missing key.")

        elif action == 'post-async':
            self.response.headers.add_header('Content-Type', 'text/x-json')
            key = self.request.get('key')
            taskqueue.add(queue_name='twitter-queue',
                          url='/twitter/post',
                          params={
                                  'key': key,
                                  'twitter_oauth_token': self.session.data.twitter_oauth_token,
                                  'twitter_oauth_secret': self.session.data.twitter_oauth_secret
                                  })
            callback = 'twitterCallback'
            res = '%s(%s)' % (callback, json.dumps({ 'message': 'enqueued' }))
            self.response.out.write(res)

        else:
            pass # TODO: ggf. Fehleranzeige bei unbekanntem Twitter-Handler


    def post(self, action):
        self.get(action)



class ImportHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um Blog-Beiträge zu importieren.'))
            return
        if not users.is_current_user_admin():
            self.redirect("/error/%s" % encode(u'Nur Administratoren dürfen Blog-Beiträge importieren.'))
            return
        uauth = Permissions.PermissionChecker(user)
        if not uauth.can_import_blog():
            self.redirect("/error/%s" % encode(u'Sie sind nicht berechtigt, Blog-Beiträge zu importieren.'))
            return
        session = Session(self, user)
        authinfo = GoogleAuthInfo(user, self.request.uri)
        template_values = {
            'authinfo'  : authinfo,
        }
        self.response.out.write(template.render(TEMPLATES['import'], template_values))


    def post(self):
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um Blog-Beiträge zu importieren.'))
            return
        if not users.is_current_user_admin():
            self.redirect("/error/%s" % encode(u'Nur Administratoren dürfen Blog-Beiträge importieren.'))
            return
        uauth = Permissions.PermissionChecker(user)
        if not uauth.can_import_blog():
            self.redirect("/error/%s" % encode(u'Sie sind nicht berechtigt, Blog-Beiträge zu importieren.'))
            return
        what = self.request.get('what').lower()
        if what not in [ 'permissions', 'blog' ]:
            self.response.set_status(500)
            self.response.out.write(u'Es lassen sich nur "permissions" und "blog" importieren')
            return
        format = self.request.get('format').lower()
        if format not in [ 'json', 'pickle' ]:
            self.redirect("/error/%s" % encode(u'Es sind nur die Eingabeformate "json" und "pickle" zugelassen'))
            return
        compress = self.request.get('compress').lower() in [ 'true', '1', 'yes', 'on' ]
        self.response.headers.add_header('content-type', 'text/plain')
        if what == 'blog':
            data = self.request.get('file')
            if data:
                importer = Importer(BlogModel.Entry)
                importer.load(data, out=self.response.out, format=format)
                BlogModel.Entry.flushTagList()
                # TODO: wenn gewünscht, bestehende Einträge vor dem Import löschen
            else: pass # TODO


class ExportHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um Blog-Beiträge zu exportieren.'))
            return
        if not users.is_current_user_admin():
            self.redirect("/error/%s" % encode(u'Nur Administratoren dürfen Blog-Beiträge exportieren.'))
            return
        uauth = Permissions.PermissionChecker(user)
        if not uauth.can_export_blog():
            self.redirect("/error/%s" % encode(u'Sie sind nicht berechtigt, Blog-Beiträge zu exportieren.'))
            return
        session = Session(self, user)
        authinfo = GoogleAuthInfo(user, self.request.uri)
        template_values = {
            'authinfo'  : authinfo,
        }
        self.response.out.write(template.render(TEMPLATES['export'], template_values))


    def post(self):
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um Blog-Beiträge zu exportieren.'))
            return
        if not users.is_current_user_admin():
            self.redirect("/error/%s" % encode(u'Nur Administratoren dürfen Blog-Beiträge exportieren.'))
            return
        uauth = Permissions.PermissionChecker(user)
        if not uauth.can_export_blog():
            self.redirect("/error/%s" % encode(u'Sie sind nicht berechtigt, Blog-Beiträge zu exportieren.'))
            return
        what = self.request.get('what').lower()
        if what not in [ 'permissions', 'blog' ]:
            self.response.set_status(500)
            self.response.out.write(u'Es lassen sich nur "permissions" und "blog" exportieren')
            return
        format = self.request.get('format').lower()
        if format not in [ 'json', 'pickle' ]:
            self.response.set_status(500)
            self.redirect("/error/%s" % encode(u'Es sind nur die Ausgabeformate "json" und "pickle" zugelassen'))
            return
        compress = self.request.get('compress').lower() in [ 'true', '1', 'yes', 'on' ]
        if compress:
            self.response.headers.add_header('content-type', 'application/bzip2')
            suffix = '.bz2'
        else:
            self.response.headers.add_header('content-type', 'text/%s' % format)
            suffix = ''
        self.response.headers.add_header('content-disposition', "attachment; filename=%s-%s.%s%s" %
                                         (datetime.utcnow().strftime('%Y%m%d-%H%M%S'), what, format, suffix))
        if what == 'blog':
            exporter = Exporter(BlogModel.Entry)
            exporter.dump(out=self.response.out, format=format, compress=compress)

        elif what == 'permissions':
            exporter = Exporter(Permissions.Permission)
            exporter.dump(out=self.response.out, format=format, compress=compress)

        else: pass


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        if resource is None:
            self.response.set_status(404)
            return
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class UnloadHandler(webapp.RequestHandler):
    def get(self, resource):
        if resource is None:
            self.response.set_status(404)
            return
        resource = str(urllib.unquote(resource))
        BlobInfo.get(resource).delete()
        if self.request.get('goto'): self.redirect(self.request.get('goto'))
        else: self.redirect('/manage/files')


class UploadFormHandler(webapp.RequestHandler):
    def get(self, resource):
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um Dateien hochzuladen.'))
            return
        uauth = Permissions.PermissionChecker(user)
        if not uauth.can_upload():
            self.redirect("/error/%s" % encode(u'Sie sind nicht berechtigt, Dateien hochzuladen.'))
            return
        session = Session(self, user)
        authinfo = GoogleAuthInfo(user, self.request.uri)
        blob_info = None
        if resource:
            resource = str(urllib.unquote(resource))
            blob_info = BlobInfo.get(resource)
        template_values = {
            'authinfo'  : authinfo,
            'upload_url': blobstore.create_upload_url('/doupload'),
            'blob'      : blob_info,
        }
        self.response.out.write(template.render(TEMPLATES['upload'], template_values))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        user = users.get_current_user()
        if user is None:
            self.redirect("/error/%s" % encode(u'Sie müssen angemeldet sein, um Dateien hochzuladen.'))
            return
        if not users.is_current_user_admin():
            self.redirect("/error/%s" % encode(u'Sie sind nicht berechtigt, Dateien hochzuladen.'))
            return
        self.redirect('/manage/files')

