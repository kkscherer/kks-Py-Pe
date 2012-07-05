# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: DatastoreUtils.py bdb7881e36be 2009/12/16 16:17:13 Oliver Lau <oliver@von-und-fuer-lau.de> $

import inspect, sys, types, pickle, bz2

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import datastore_types
from django.utils import simplejson as json
from BlogModel import Entry
from JSONProperty import JSONProperty
from Session import Session, SessionData
from datetime import datetime, time, date


"""
README:

 Der in Importer und Exporter implementierte Backup/Restore-Mechanismus ignoriert
 Primär- und Fremdschlüssel. Der Exporter kann keine Referenzen exportieren.
 Der Importer nicht den exakten Originalzustand inklusive Primärschlüssel von
 vor dem Backup wiederherstellen, sondern lediglich die die benutzerdefinierten
 Daten aus dem Model restaurieren.

"""



class Importer:
    obj = None
    fields = None

    def __init__(self, obj):
        self.obj = obj
        self.fields = getattr(self.obj, '_properties')

    def load(self, data, out=None, format='pickle', compress=False):
        if compress:
            decompressor = bz2.BZ2Decompressor()
            data = decompressor.decompress(data)

        if format == 'pickle': data = pickle.loads(data)
        elif format == 'json': data = json.loads(data)
        else: raise NotImplementedYet, "Input format '%s' is not implemented yet. Please use one of 'pickle', 'json'" % format


        for d in data:
            entry = {}
            for f in self.fields:
                e = getattr(self.obj, f)
                if f in d:
                    if isinstance(e, db.DateTimeProperty):
                        entry[f] = datetime.strptime(d[f], '%Y-%m-%d %H:%M:%S')
                    elif isinstance(e, db.DateProperty):
                        entry[f] = datetime.strptime(d[f], '%Y-%m-%d')
                    elif isinstance(e, db.TimeProperty):
                        entry[f] = datetime.strptime(d[f], '%H:%M:%S')
                    elif isinstance(e, db.UserProperty):
                        entry[f] = users.User(email=d[f])
                    elif isinstance(e, ( db.BooleanProperty,
                                         db.StringListProperty,
                                         db.ListProperty ) ):
                        entry[f] = d[f]
                    else: entry[f] = '%s' % d[f]
                    # out.write("  %s (%s/%s): %s\n" % (f, type(e), type(entry[f]), entry[f]))

            o = object.__new__(self.obj)
            if o is not None:
                # laut Python-Referenz sollte __init__() schon durch
                # __new__() aufgerufen worden sein, in meinen Tests
                # war das aber nicht der Fall
                o.__init__(**entry)
                o.put()
                if o.is_saved():
                    out.write("NEW KEY = %s\n" % o.key())


class Exporter:
    obj = None
    fields = None

    def __init__(self, obj):
        self.obj = obj
        self.fields = getattr(self.obj, '_properties')

    def dump(self, out=None, format='pickle', compress=False):
        data = self.obj.all()
        result = []
        for d in data:
            entry = { 'key': '%s' % d.key() }
            for f in self.fields:
                e = getattr(d, f)
                if type(e) in [ types.BooleanType,
                                types.DictionaryType,
                                types.DictType,
                                types.FloatType,
                                types.IntType,
                                types.ListType,
                                types.LongType,
                                types.StringType,
                                types.UnicodeType,
                                types.TupleType
                              ]:
                    entry[f] = e
                elif type(e) in [ types.NoneType,
                                  types.NotImplementedType
                                ]: pass
                elif type(e) == datetime:
                    entry[f] = e.strftime('%Y-%m-%d %H:%M:%S')
                elif type(e) == time:
                    entry[f] = e.strftime('%H:%M:%S')
                elif type(e) == date:
                    entry[f] = e.strftime('%Y-%m-%d')
                else:
                    entry[f] = '%s' % e
            result.append(entry)

        if format == 'pickle': result = pickle.dumps(result)
        elif format == 'json': result = json.dumps(result)
        else: raise NotImplementedYet, "Output format '%s' is not implemented yet. Please use one of 'pickle', 'json'" % format

        if compress:
            compressor = bz2.BZ2Compressor()
            compressor.compress(result)
            result = compressor.flush()

        if out is None: return result
        else: out.write(result)
