# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: Permissions.py db239e9ab1e7 2009/12/17 15:58:45 Oliver Lau <oliver@von-und-fuer-lau.de> $

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users


class Permission(db.Model):
    user = db.UserProperty()
    is_admin = db.BooleanProperty(default=False)
    can_post = db.BooleanProperty(default=False)
    can_crosspost = db.BooleanProperty(default=False)
    can_import_blog = db.BooleanProperty(default=False)
    can_export_blog = db.BooleanProperty(default=False)
    can_upload = db.BooleanProperty(default=False)
    can_comment = db.BooleanProperty(default=False)

    def __str__(self):
        return ", ".join('%s' % (k) for k in [
                                              self.user.email(),
                                              self.is_admin,
                                              self.can_post,
                                              self.can_crosspost,
                                              self.can_import_blog,
                                              self.can_export_blog,
                                              self.can_upload,
                                              self.can_comment,
                                              ] )


class PermissionChecker:
    user = None
    permissions = None

    def __init__(self, user=None):
        self.user = user
        if self.user is not None:
            self.permissions = Permission.all().filter('user = ', user).get()

    # returns True if the user has an administrative role
    def is_admin(self):
        if self.permissions is not None:
            return self.permissions.is_admin
        return False

    # returns True if the user is allowed to post blog entries
    def can_post(self):
        if self.permissions is not None:
            return self.permissions.can_post
        return False

    # returns True if the user is allowed to x-post messages on Twitter etc.
    def can_crosspost(self):
        if self.permissions is not None:
            return self.permissions.can_crosspost
        return False

    # returns True if the user is allowed to export blog data
    def can_export_blog(self):
        if self.permissions is not None:
            return self.permissions.can_export_blog
        return False

    # returns True if the user is allowed to import blog data
    def can_import_blog(self):
        if self.permissions is not None:
            return self.permissions.can_import_blog
        return False

    # returns True if the user is allowed to upload BLOBs
    def can_upload(self):
        if self.permissions is not None:
            return self.permissions.can_upload
        return False

    # returns True if the user is allowed to comment on blog entries
    def can_comment(self):
        if self.permissions is not None:
            return self.permissions.can_comment
        return False
