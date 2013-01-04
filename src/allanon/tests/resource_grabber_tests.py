# -*- coding: utf8 -*-

from tempfile import mkdtemp
import os.path

import unittest

from httpretty import HTTPretty

from allanon.resouce_grabber import ResourceGrabber

class ResourceGrabberDirectDownalodTest(unittest.TestCase):
    
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
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/foo.pdf?bar=123",
                           body="foo")
        rg = ResourceGrabber("http://foo.net/foo.pdf?bar=123")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'foo.pdf')
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")
        HTTPretty.register_uri(HTTPretty.GET, "http://baz.net/qux.pdf/?bar=123",
                           body="foo")
        rg = ResourceGrabber("http://baz.net/qux.pdf/?bar=123")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'qux.pdf')
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")
        HTTPretty.register_uri(HTTPretty.GET, "http://baz.net/qux%20file.pdf/?bar=123",
                           body="foo")
        rg = ResourceGrabber("http://baz.net/qux%20file.pdf/?bar=123")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'qux file.pdf')
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_download_with_no_path(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/",
                           body="foo")
        rg = ResourceGrabber("http://foo.net/")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'foo.net')
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_download_with_attach_filename(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/page",
                           body="foo",
                           content_disposition="attachment; filename=foo.pdf")
        rg = ResourceGrabber("http://foo.net/page")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'foo.pdf')
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")
        # another test, playgin with case and whitespaces
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/page",
                           body="foo",
                           content_disposition="attachment;FILENAME  =\tbar.pdf")
        rg = ResourceGrabber("http://foo.net/page")
        rg.download(self.directory)
        path = os.path.join(self.directory, 'bar.pdf')
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

    def test_generate_filename_from_model(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/foo.pdf")
        rg = ResourceGrabber("http://foo.net/foo.pdf")
        self.assertEqual(rg._generate_filename_from_model('foo.pdf', 'bar-baz-%FULLNAME'),
                         'bar-baz-foo.pdf')
        self.assertEqual(rg._generate_filename_from_model('foo.pdf', 'bar-%NAME-baz.%EXTENSION'),
                         'bar-foo-baz.pdf')
        self.assertEqual(rg._generate_filename_from_model('foo.pdf', '%HOST-foo.pdf'),
                         'foo.net-foo.pdf')
        self.assertEqual(rg._generate_filename_from_model('foo.pdf', '%INDEX-foo.pdf', index=12),
                         '12-foo.pdf')
        self.assertEqual(rg._generate_filename_from_model('foo.pdf', '%INDEX-foo.pdf', index=12,
                                                          index_digit_len=3),
                         '012-foo.pdf')
        self.assertEqual(rg._generate_filename_from_model('foo.pdf', 'foo-%1-bar-%2.pdf',
                                                          ids=[2, 5], ids_digit_len=[1,1]),
                         'foo-2-bar-5.pdf')
        self.assertEqual(rg._generate_filename_from_model('foo.pdf', 'foo-%1-bar-%2.pdf',
                                                          ids=[2, 84],
                                                          ids_digit_len=[2, 4],
                                                          index_digit_len=4),
                         'foo-02-bar-0084.pdf')


class ResourceGrabberInnerResourcesTest(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.temp_dir = mkdtemp()
        HTTPretty.enable()
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.org/main.html",
                               body=self._read_file('page.html'))
        HTTPretty.register_uri(HTTPretty.GET, "http://fooimages.org/image1.png",
                               body=self._read_file('image1.png'))
        HTTPretty.register_uri(HTTPretty.GET, "http://foofiles.org/text1.txt",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://foofiles.org/text2.txt",
                               body=self._read_file('text2.txt'))
        f = open(os.path.join(self.test_dir, 'page.html'))
        self.html = f.read()
        f.close()
    
    def tearDown(self):
        HTTPretty.disable()

    def _read_file(self, filename):
        with open(os.path.join(self.test_dir, filename)) as f:
            return f.read()

    def test_download(self):
        rg = ResourceGrabber("http://foo.org/main.html")
        rg.download_resources('div.images img', self.temp_dir)
        with open(os.path.join(self.temp_dir, 'image1.png')) as original:
            with open(os.path.join(self.test_dir, 'image1.png')) as downloaded:
                self.assertEqual(original.read(), downloaded.read())

    def test_mass_download(self):
        rg = ResourceGrabber("http://foo.org/main.html")
        rg.download_resources('div.links a', self.temp_dir)
        with open(os.path.join(self.test_dir, 'text1.txt')) as downloaded:
            self.assertEqual(downloaded.read(),
                             "Allanon was the last of the Druids of Paranor")
        with open(os.path.join(self.test_dir, 'text2.txt')) as downloaded:
            self.assertEqual(downloaded.read(),
                             "Allanon was killed in the battle with a Jachyra")


    def test_get_internal_links(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/main.html",
                               body=self._read_file('page.html'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/page1.html",
                               body=self._read_file('page1.html'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/page2.html",
                               body=self._read_file('page2.html'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/text1.txt",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/text2.txt",
                               body=self._read_file('text2.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/text3.txt",
                               body=self._read_file('text1.txt'))
        HTTPretty.register_uri(HTTPretty.GET, "http://recursive.org/text4.txt",
                               body=self._read_file('text2.txt'))

        rg = ResourceGrabber("http://recursive.org/main.html")
        links = rg.get_internal_links('.recursiveTest a', 'li a')
        self.assertEqual(list(links),
                         ['http://recursive.org/text1.txt',
                          'http://recursive.org/text2.txt',
                          'http://recursive.org/text3.txt',
                          'http://recursive.org/text4.txt'])


if __name__ == "__main__":
    unittest.main()
