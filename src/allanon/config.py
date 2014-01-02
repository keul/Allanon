# -*- coding: utf8 -*-

import os


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt")) as version_file:
    version = version_file.read()

CHUNK_SIZE = 10000
TIMEOUT = 60.0
USER_AGENT = "Allanon Crawler %s" % version

def headers():
    return {
            'User-Agent': USER_AGENT,
            }
