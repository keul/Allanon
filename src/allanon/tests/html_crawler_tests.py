# -*- coding: utf8 -*-

import os.path
import unittest

from httpretty import HTTPretty

from allanon.html_crawler import search_in_html
from allanon.html_crawler import apply_base_url


class HtmlCrawlingTest(unittest.TestCase):
    
    def setUp(self):
        self.dir_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        HTTPretty.enable()
        HTTPretty.register_uri(HTTPretty.GET, "http://fooimages.org/image1.png",
                               body="foo")
        HTTPretty.register_uri(HTTPretty.GET, "http://foofiles.org/text1.txt",
                               body="foo")
        HTTPretty.register_uri(HTTPretty.GET, "http://foofiles.org/text2.txt",
                               body="foo")
        f = open(os.path.join(self.dir_name, 'page.html'))
        self.html = f.read()
        f.close()
    
    def tearDown(self):
        HTTPretty.disable()

    def test_basic_filter_img(self):
        self.assertEqual(list(search_in_html(self.html, 'div.images img'))[0],
                         'http://fooimages.org/image1.png')

    def test_basic_filter_ahref(self):
        self.assertEqual(list(search_in_html(self.html, 'div.links a'))[0],
                         'http://foofiles.org/text1.txt')

    def test_basic_filter_textual(self):
        self.assertEqual(list(search_in_html(self.html, 'div:eq(2)'))[0],
                         'http://fooimages.org/image1.png')

    def test_multiple_filter(self):
        self.assertEqual(list(search_in_html(self.html, 'div.links a')),
                         ['http://foofiles.org/text1.txt',
                          'http://foofiles.org/text2.txt'])

    def test_relative_urls(self):
        self.assertEqual(list(search_in_html(self.html, 'div.relLinks a',
                                             'http://foofiles.org/')),
                         ['http://foofiles.org/text1.txt',
                          'http://foofiles.org/text2.txt'])


class URLTransformationTest(unittest.TestCase):
    
    def test_default_url(self):
        self.assertEqual(apply_base_url('http://fooimages.org/path', 'foo'),
                         'http://fooimages.org/path')

    def test_root_absolute_url(self):
        self.assertEqual(apply_base_url('/path', 'http://fooimages.org'),
                         'http://fooimages.org/path')
        self.assertEqual(apply_base_url('/path', 'http://fooimages.org/aaa'),
                         'http://fooimages.org/path')
        self.assertEqual(apply_base_url('/path', 'http://fooimages.org/aaa?bar=65'),
                         'http://fooimages.org/path')

    def test_relative_url(self):
        self.assertEqual(apply_base_url('path', 'http://fooimages.org'),
                         'http://fooimages.org/path')
        self.assertEqual(apply_base_url('path', 'http://fooimages.org/aaa'),
                         'http://fooimages.org/path')
        self.assertEqual(apply_base_url('path', 'http://fooimages.org/aaa?bar=65'),
                         'http://fooimages.org/path')


if __name__ == "__main__":
    unittest.main()