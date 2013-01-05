# -*- coding: utf8 -*-

import unittest
import os.path
from os import listdir
from tempfile import mkdtemp
from optparse import OptionParser

from httpretty import HTTPretty

from allanon.main import main

class AllanonTest(unittest.TestCase):
    """Main acceptance tests"""

    def setUp(self):
        self.options = OptionParser()
        self.options.help = None
        self.options.filename_model = ''
        self.options.search_queries = []
        self.temp_dir = mkdtemp()
        self.options.destination_directory = self.temp_dir
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        HTTPretty.enable()

    def tearDown(self):
        HTTPretty.disable()
    
    def _read_file(self, filename):
        with open(os.path.join(self.test_dir, filename)) as f:
            return f.read()
    
    def _get_downloaded_files(self):
        return listdir(self.temp_dir)

    def _same_content(self, temp_file, model_file):
        """
        Return True is the temp_file in the temp directory has same content of the
        file in the tests directory
        """
        with open(os.path.join(self.test_dir, model_file)) as original:
            with open(os.path.join(self.temp_dir, temp_file)) as downloaded:
                return original.read() == downloaded.read()
    
    # Step 1: useless features
    def simple_one_download_test(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/main.html",
                               body=self._read_file('page.html'))
        main(self.options, 'http://foo.org/main.html')
        self.assertEqual(self._get_downloaded_files(), ['main.html'])
        self.assertTrue(self._same_content('main.html', 'page.html'))

    def simple_multiple_resource_download_test(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/foo%201.pdf",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/foo2.pdf?aaa=b",
                               body=self._read_file('text2.txt'))
        main(self.options, 'http://foo.org/foo 1.pdf', 'http://foo.org/foo2.pdf?aaa=b')
        self.assertEqual(self._get_downloaded_files(), ['foo 1.pdf', 'foo2.pdf'])
        self.assertTrue(self._same_content('foo 1.pdf', 'text1.txt'))
        self.assertTrue(self._same_content('foo2.pdf', 'text2.txt'))

    def dynamic_url_downloads_test(self):
        self.options.filename_model = "%INDEX-%FULLNAME"
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/foo1.pdf?aaa=6",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/foo1.pdf?aaa=7",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/foo2.pdf?aaa=6",
                               body=self._read_file('text2.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/foo2.pdf?aaa=7",
                               body=self._read_file('text2.txt'))
        main(self.options, 'http://foo.org/foo{1:2}.pdf?aaa={6:7}')
        self.assertEqual(self._get_downloaded_files(), ['1-foo1.pdf', '2-foo1.pdf',
                                                        '3-foo2.pdf', '4-foo2.pdf'])
        self.assertTrue(self._same_content('1-foo1.pdf', 'text1.txt'))
        self.assertTrue(self._same_content('2-foo1.pdf', 'text1.txt'))
        self.assertTrue(self._same_content('3-foo2.pdf', 'text2.txt'))
        self.assertTrue(self._same_content('4-foo2.pdf', 'text2.txt'))

    # Step 2: really useful features
    def inner_resources_download_test(self):
        # main command line URLs set
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/section-1/download.html",
                               body=self._read_file('page.html'))
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/section-2/download.html",
                               body=self._read_file('page1.html'))
        self.options.filename_model = "%INDEX-%1-%FULLNAME"
        self.options.search_queries = ['div.recursiveTest a']
        # resources found inside main pages
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/page1.html",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/page2.html",
                               body=self._read_file('text2.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/text1.txt",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/text2.txt",
                               body=self._read_file('text2.txt'))
        main(self.options, 'http://foo.org/section-{1:2}/download.html')
        self.assertEqual(self._get_downloaded_files(), ['1-1-page1.html', '2-1-page2.html',
                                                        '3-2-text1.txt', '4-2-text2.txt',
                                                        ])


if __name__ == "__main__":
    unittest.main()
