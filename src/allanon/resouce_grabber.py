# -*- coding: utf8 -*-

import re
import os.path
from urlparse import urlparse

import requests

CONTENT_DISPOSITION_MODEL = r"""^.*filename\s*=\s*(?P<filename>.*?);?$"""
cdre = re.compile(CONTENT_DISPOSITION_MODEL, re.IGNORECASE)

class ResourceGrabber(object):
    
    def __init__(self, url):
        self.url = url
        self.request = None

    @property
    def html(self):
        self._open()
        return self.request.text

    def _open(self):
        if self.request is None:
            self.request = requests.get(self.url)
    
    def _get_filename(self):
        content_disposition = self.request.headers.get('content-disposition', '')
        filename_re = cdre.match(content_disposition)
        if filename_re:
            filename = filename_re.groupdict().get('filename')
        else:
            p = urlparse(self.url)
            filename = p.path.split('/')[-1]
        return filename
    
    def download(self, directory):
        self._open()
        filename = self._get_filename()
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            raise IOError("File %s exists" % path)
        f = open(path, 'wb')
        f.write(self.request.content)
        f.close()

