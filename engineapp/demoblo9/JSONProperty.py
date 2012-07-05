# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: JSONProperty.py ab145b17ce30 2009/12/02 16:10:44 Oliver Lau <oliver@von-und-fuer-lau.de> $


import logging
from google.appengine.api import datastore_types
from google.appengine.ext import db
from django.utils import simplejson as json


class JSONProperty(db.Property):
    # Override
    def get_value_for_datastore(self, model_instance):
        value = super(JSONProperty, self).get_value_for_datastore(model_instance)
        return self._deflate(value)

    # Override
    def validate(self, value):
        return self._inflate(value)

    # Override
    def make_value_from_datastore(self, value):
        return self._inflate(value)

    def _inflate(self, value):
        if value is None:
            return {}
        if isinstance(value, unicode) or isinstance(value, str):
            return json.loads(value)
        return value

    def _deflate(self, value):
        return json.dumps(value)

    data_type = datastore_types.Text
