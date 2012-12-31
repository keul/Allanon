# -*- coding: utf8 -*-

import re
import os.path
from urlparse import urlparse

import requests

from allanon import logger
from allanon.html_crawler import search_in_html

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
            logger.info("Getting %s" % self.url)
            self.request = requests.get(self.url)
            logger.info("Done")
    
    def _get_filename(self, filename_model=None, counter=1):
        content_disposition = self.request.headers.get('content-disposition', '')
        filename_re = cdre.match(content_disposition)
        filename = ""
        if filename_re:
            filename = filename_re.groupdict().get('filename')
        else:
            up = urlparse(self.url)
            path = up.path
            if path and path!='/':
                if path.endswith('/'):
                    path = path[:-1]
                filename = path.split('/')[-1]
            else:
                # let's use hostname
                filename = up.hostname
        if filename_model:
            filename = self._generate_filename_from_model(filename,
                                                          filename_model=filename_model,
                                                          counter=counter)
        return filename
    
    def _generate_filename_from_model(self, original, filename_model, counter=1):
        filename = filename_model
        while filename.find("%")>-1 and filename[filename.indexOf("%")+1].isdigit():
            # TODO
            break
        return filename
    
    def download(self, directory, filename_model=None, counter=1):
        self._open()
        filename = self._get_filename(filename_model=filename_model, counter=counter)
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            raise IOError("File %s exists" % path)
        f = open(path, 'wb')
        f.write(self.request.content)
        f.close()

    def download_resources(self, query, directory, filename_model=None, counter=1):
        self._open()
        resources = search_in_html(self.html, query)
        for url in resources:
            rg = ResourceGrabber(url)
            rg.download(directory, filename_model=filename_model, counter=counter)


