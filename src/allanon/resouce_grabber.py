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
        self.url_info = urlparse(url)
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
    
    def _get_filename(self, filename_model=None, counter=1, ids=[], index=0):
        content_disposition = self.request.headers.get('content-disposition', '')
        filename_re = cdre.match(content_disposition)
        filename = ""
        if filename_re:
            filename = filename_re.groupdict().get('filename')
        else:
            path = self.url_info.path
            if path and path!='/':
                if path.endswith('/'):
                    path = path[:-1]
                filename = path.split('/')[-1]
            else:
                # let's use hostname
                filename = self.url_info.hostname
        if filename_model:
            filename = self._generate_filename_from_model(filename,
                                                          filename_model=filename_model,
                                                          counter=counter,
                                                          ids=ids,
                                                          index=index)
        return filename
    
    def _generate_filename_from_model(self, original, filename_model, ids=[], index=0):
        filename = filename_model
        # replace %x with proper ids
        while filename.find("%")>-1 and filename[filename.find("%")+1].isdigit():
            id = int(filename[filename.find("%")+1])
            filename = filename.replace("%%%d" % id, ids[id-1])
        # replace #INDEX with the progressive
        if filename.find("%INDEX")>-1:
            filename = filename.replace("%INDEX", str(index))
        # replace #HOST with current host
        if filename.find("%HOST")>-1:
            filename = filename.replace("%HOST", self.url_info.hostname)
        # replace %NAME with original filename
        if filename.find("%NAME")>-1:
            filename = filename.replace("%NAME", original[:original.rfind('.')])
        # replace %EXTENSION with original extension
        if filename.find("%EXTENSION")>-1:
            filename = filename.replace("%EXTENSION", original[original.rfind('.')+1:])
        # replace %EXTENSION with original extension
        if filename.find("%FULLNAME")>-1:
            filename = filename.replace("%FULLNAME", original)
        return filename

    def download(self, directory, filename_model=None, ids=[], index=0):
        self._open()
        filename = self._get_filename(filename_model=filename_model, ids=ids, index=index)
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            raise IOError("File %s exists" % path)
        f = open(path, 'wb')
        f.write(self.request.content)
        f.close()

    def download_resources(self, query, directory, filename_model=None, ids=[], index=0):
        self._open()
        resources = search_in_html(self.html, query)
        for url in resources:
            rg = ResourceGrabber(url)
            rg.download(directory, filename_model=filename_model, ids=ids, index=index)


