# coding=utf-8
# Copyright (c) 2009 Oliver Lau <oliver@von-und-fuer-lau.de>
# $Id: cleanup.py 8f87e4670619 2009/12/11 13:07:30 Oliver Lau <oliver@von-und-fuer-lau.de> $

import logging
from google.appengine.ext import db
from Session import SessionData
from datetime import datetime


def main():
    db.delete(SessionData.all().filter('expires < ', datetime.utcnow()))
    logging.info("Abgelaufene Web-Sitzungen gelöscht.")


if __name__ == "__main__":
    main()
