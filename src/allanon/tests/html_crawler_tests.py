# -*- coding: utf8 -*-

import os.path
import unittest

from httpretty import HTTPretty

from allanon.html_crawler import search_in_html


class HtmlCrawlerTest(unittest.TestCase):
    
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


if __name__ == "__main__":
    unittest.main()