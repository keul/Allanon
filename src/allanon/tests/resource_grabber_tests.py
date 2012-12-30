# -*- coding: utf8 -*-

from tempfile import mkdtemp
import os.path

import unittest

from httpretty import HTTPretty
from httpretty import httprettified

from allanon.resouce_grabber import ResourceGrabber

class ResourceGrabberTest(unittest.TestCase):
    
    def setUp(self):
        HTTPretty.enable()
        self.directory = mkdtemp()
    
    def tearDown(self):
        HTTPretty.disable()
    
    def test_can_store_data(self):
        body = '<html><body>foo</body></html>'
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/page",
                           body=body)
        rg = ResourceGrabber("http://foo.net/page")
        self.assertEqual(rg.html, body)

    def test_basic_download(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/foo.pdf",
                           body="foo")
        rg = ResourceGrabber("http://foo.net/foo.pdf")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'foo.pdf')
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_basic_download_with_attach_filename(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/page",
                           body="foo",
                           content_disposition="attachment; filename=foo.pdf")
        rg = ResourceGrabber("http://foo.net/page")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'foo.pdf')
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_file_exists_error(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/foo.pdf",
                           body="foo")
        rg = ResourceGrabber("http://foo.net/foo.pdf")
        f = open(os.path.join(self.directory, 'foo.pdf'), 'wb')
        f.write('bar')
        f.close()
        self.assertRaises(IOError, rg.download, self.directory)

