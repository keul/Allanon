# -*- coding: utf8 -*-

import re
import os.path
import urllib
from urlparse import urlparse

import requests

from allanon import logger
from allanon.html_crawler import search_in_html

CONTENT_DISPOSITION_MODEL = r"""^.*filename\s*=\s*(?P<filename>.*?);?$"""
cdre = re.compile(CONTENT_DISPOSITION_MODEL, re.IGNORECASE)


def _int_format(i, ilen):
    if not ilen:
        return str(i)
    return ("%%0%dd" % ilen) % i


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
            print "Getting %s" % self.url
            self.request = requests.get(self.url)
            print "Done"
    
    def _get_filename(self, filename_model=None, ids=[], index=0,
                      ids_digit_len=0, index_digit_len=0):
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
            filename = urllib.unquote(filename)
        if filename_model:
            filename = self._generate_filename_from_model(filename,
                                                          filename_model=filename_model,
                                                          ids=ids,
                                                          index=index,
                                                          ids_digit_len=ids_digit_len,
                                                          index_digit_len=index_digit_len)
        return filename
        
    def _generate_filename_from_model(self, original, filename_model, ids=[], index=0,
                                      ids_digit_len=[], index_digit_len=0):
        filename = filename_model
        # replace %x with proper ids
        cnt = 0
        while filename.find("%")>-1 and filename[filename.find("%")+1].isdigit():
            id = int(filename[filename.find("%")+1])
            filename = filename.replace("%%%d" % id, _int_format(ids[cnt],
                                                                 ids_digit_len[cnt]), 1)
            cnt+=1
        # replace #INDEX with the progressive
        if filename.find("%INDEX")>-1:
            filename = filename.replace("%INDEX", _int_format(index, index_digit_len))
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

    def download(self, directory, filename_model=None, ids=[], index=0,
                 ids_digit_len=[], index_digit_len=0):
        self._open()
        filename = self._get_filename(filename_model=filename_model, ids=ids, index=index,
                                      ids_digit_len=ids_digit_len, index_digit_len=ids_digit_len)
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            raise IOError("File %s exists" % path)
        print "Writing resource to %s" % path
        f = open(path, 'wb')
        f.write(self.request.content)
        f.close()

    def download_resources(self, query, directory, filename_model=None, ids=[], index=0,
                           ids_digit_len=[], index_digit_len=0):
        self._open()
        resources = search_in_html(self.html, query, self.url)
        for url in resources:
            rg = ResourceGrabber(url)
            rg.download(directory, filename_model=filename_model, ids=ids, index=index,
                        ids_digit_len=ids_digit_len, index_digit_len=ids_digit_len)


