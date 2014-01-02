# -*- coding: utf8 -*-

import re
import hashlib
import tempfile
import sys
import os.path
import traceback
import urllib
from shutil import copyfile
from urlparse import urlparse

import requests
from progress.bar import Bar
from progress.spinner import PieSpinner

from allanon import config
from allanon.html_crawler import search_in_html

CONTENT_DISPOSITION_MODEL = r"""^.*filename\s*="?\s*(?P<filename>.*?)"?;?$"""
cdre = re.compile(CONTENT_DISPOSITION_MODEL, re.IGNORECASE)

DYNA_ID_MODEL = r"""(\%\d+)"""
dynaid_re = re.compile(DYNA_ID_MODEL)

EXTENSION_MODEL = r"""^(?P<name>.+?)(?P<index>_\d+)?(?P<extension>\.[a-zA-Z]{2,4})?$"""


def _int_format(i, ilen):
    if not ilen:
        return str(i)
    return ("%%0%dd" % ilen) % i

def _try_new_filename(filename):
    """
    Getting a filename in the form foo_X.ext where X,
    it generate a new filename as foo_Y.ext, where Y is X+1
    
    In the case that _X is missing (like foo.ext), Y=1 i used
    
    Extension is optional
    """
    match = re.match(EXTENSION_MODEL, filename)
    if match:
        name, version, extension = match.groups()
        if version:
            version = "_%d" % (int(version[1:])+1)
        else:
            version = "_1"
        filename = name + version + (extension if extension else '')
    return filename    


class ResourceGrabber(object):
    
    def __init__(self, url):
        self.url = url
        self.url_info = urlparse(url)
        self.request = None
        self.timeout = config.TIMEOUT

    @property
    def html(self):
        self._open()
        return self.request.text if self.request else None

    def _open(self):
        if self.request is None:
            print "Getting %s" % self.url
            try:
                self.request = requests.get(self.url, headers=config.headers(), stream=True,
                                            timeout=self.timeout)
            except requests.exceptions.Timeout:
                print "Can't get resource at %s. Request timed out" % self.url
                return
            if self.request.status_code>=200 and self.request.status_code<300:
                print "Done"
            else:
                print "Can't get resource at %s. HTTP error %d" % (self.url,
                                                                   self.request.status_code)
    
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
    
    def _string_interpolation(self, model, ids=[], index=0,
                              ids_digit_len=[], index_digit_len=0):
        # replace %x with proper ids
        cnt = 0
        while dynaid_re.search(model):
            match = dynaid_re.search(model)
            dynaid = match.group()
            model = model.replace(dynaid, _int_format(ids[cnt],
                                                      ids_digit_len[cnt]), 1)
            cnt+=1
        # replace %INDEX with the progressive
        if model.find("%INDEX")>-1:
            model = model.replace("%INDEX", _int_format(index, index_digit_len))
        # replace %HOST with current host
        if model.find("%HOST")>-1:
            model = model.replace("%HOST", self.url_info.hostname)
        return model
    
    def _generate_filename_from_model(self, original, filename_model, ids=[], index=0,
                                      ids_digit_len=[], index_digit_len=0):
        filename = self._string_interpolation(filename_model, ids, index, ids_digit_len, index_digit_len)
        # *** Other interpolation (only file's specific) ***
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

    def _create_subdirs(self, directory, ids=[], index=0,
                      ids_digit_len=[], index_digit_len=0):
        """Given a directory name, or a directory path string in nix format
        (e.g: foo/bar), create all intermediate directories.
        Return the new (existing) final directory absolute path 
        """
        directory = self._string_interpolation(directory, ids, index, ids_digit_len, index_digit_len)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def _get_resource_content(self, file_out, filename):
        """Save data stored in the current request object in a file"""
        content_length = self.request.headers.get('content-length', '')
        size = int(content_length) if content_length else 0
        if size:
            progress = Bar("Getting %s" % filename, fill='#', suffix='%(percent)d%%', max=size)
        else:
            progress = PieSpinner("Getting %s " % filename)
        try:
            for chunk in self.request.iter_content(config.CHUNK_SIZE):
                file_out.write(chunk)
                progress.next(config.CHUNK_SIZE if size else 1)
        except:
            print "Error while getting %s" % self.url
            traceback.print_exc(file=sys.stdout)
            return None
        finally:
            progress.finish()
        return file_out.name

    def download(self, directory, filename_model=None, ids=[], index=0,
                 ids_digit_len=[], index_digit_len=0, duplicate_check=False):
        """Download a remote resource. Return the new path or None if no resource has been created"""
        self._open()
        if not self.request:
            return
        directory = self._create_subdirs(directory, ids=ids, index=index,
                                      ids_digit_len=ids_digit_len,
                                      index_digit_len=index_digit_len)
        filename = self._get_filename(filename_model=filename_model, ids=ids, index=index,
                                      ids_digit_len=ids_digit_len,
                                      index_digit_len=index_digit_len)
        path = os.path.join(directory, filename)
        cache = None
        if duplicate_check and os.path.exists(path):
            # Before trying to find a free filename, check is this file is a duplicate
            with open(path, 'rb') as saved:
                md5_saved = hashlib.md5(saved.read()).digest()
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                cache = self._get_resource_content(tmp, filename)
                tmp.seek(0)
                md5_remote = hashlib.md5(tmp.read()).digest()
            if md5_saved==md5_remote:
                # same file
                print "Resource at %s is a duplicate of %s" % (self.url,
                                                               path)
                return
        while os.path.exists(path):
            # continue trying until we get a good filename
            filename = _try_new_filename(filename)
            path = os.path.join(directory, filename)
        if self.request.status_code>=200 and self.request.status_code<300:
            if cache:
                # re-use file in temp directory, used for md5 checksum
                copyfile(cache, path)
                os.remove(cache)
            else:
                with open(path, 'wb') as f:
                    print "Writing resource to %s" % path
                    self._get_resource_content(f, filename)
            return path

    def download_resources(self, query, directory, filename_model=None, ids=[], index=0,
                           ids_digit_len=[], index_digit_len=0, duplicate_check=False):
        self._open()
        if not self.request:
            return
        resources = search_in_html(self.html, query, self.url)
        for url in resources:
            rg = ResourceGrabber(url)
            rg.download(directory, filename_model=filename_model, ids=ids, index=index,
                        ids_digit_len=ids_digit_len, index_digit_len=ids_digit_len,
                        duplicate_check=duplicate_check)

    def get_internal_links(self, *args, **kwargs):
        self._open()
        if not self.request:
            return
        level = kwargs.get('level', 0)
        if self.request.status_code >=200 and self.request.status_code<300:
            links = search_in_html(self.html, args[level], self.url)
            for link in links:
                rg = ResourceGrabber(link)
                if len(args)>level+1:
                    for inner_link in rg.get_internal_links(*args, level=level+1):
                        yield inner_link
                else:
                    yield link


