# -*- coding: utf8 -*-

import os.path
import unittest
from requests import exceptions as requests_exceptions
from tempfile import mkdtemp
from httpretty import HTTPretty
from allanon.resouce_grabber import ResourceGrabber
from allanon.resouce_grabber import _try_new_filename


class ResourceGrabberTest(unittest.TestCase):
    def setUp(self):
        HTTPretty.enable()
        self.directory = mkdtemp()

    def tearDown(self):
        HTTPretty.disable()

    def test_create_subdirs(self):
        rg = ResourceGrabber("foo")
        self.assertEqual(
            rg._create_subdirs(os.path.join(self.directory, "foo")),
            os.path.join(self.directory, "foo"),
        )

    def test_create_multiple_dirs(self):
        rg = ResourceGrabber("foo")
        self.assertEqual(
            rg._create_subdirs(os.path.join(self.directory, "foo/bar/baz")),
            os.path.join(self.directory, "foo", "bar", "baz"),
        )

    def test_create_multiple_dirs_some_exists(self):
        rg = ResourceGrabber("foo")
        os.mkdir(os.path.join(self.directory, "foo"))
        self.assertEqual(
            rg._create_subdirs(os.path.join(self.directory, "foo/bar/baz")),
            os.path.join(self.directory, "foo", "bar", "baz"),
        )

    def test_create_dirs_with_interpolation(self):
        rg = ResourceGrabber("http://foo.com/part{1:4}/section-{10:20}/foo.pdf")
        result = rg._create_subdirs(
            os.path.join(self.directory, "%HOST/section-%1/%2"),
            ids=[2, 3],
            index=2,
            ids_digit_len=[1, 1],
            index_digit_len=1,
        )
        self.assertEqual(
            result, os.path.join(self.directory, "foo.com", "section-2", "3")
        )

    def test_open_exceptions_generic(self):
        def timeout_callback(method, uri, headers):
            return (
                404,
                [],
                "Resource not found",
            )

        rg = ResourceGrabber("http://foo.com/foo.pdf")
        HTTPretty.register_uri(
            HTTPretty.GET, "http://foo.com/foo.pdf", body=timeout_callback
        )
        response = rg._open()
        self.assertEqual(response, None)


class ResourceGrabberDirectDownloadTest(unittest.TestCase):
    def setUp(self):
        HTTPretty.enable()
        self.directory = mkdtemp()

    def tearDown(self):
        HTTPretty.disable()

    def test_can_store_data(self):
        body = "<html><body>foo</body></html>"
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/page", body=body)
        rg = ResourceGrabber("http://foo.net/page")
        self.assertEqual(rg.html, body)

    def test_basic_download(self):
        HTTPretty.register_uri(
            HTTPretty.GET, "http://foo.net/foo.pdf?bar=123", body="foo"
        )
        rg = ResourceGrabber("http://foo.net/foo.pdf?bar=123")
        rg.download(self.directory)
        path = os.path.join(self.directory, "foo.pdf")
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")
        HTTPretty.register_uri(
            HTTPretty.GET, "http://baz.net/qux.pdf/?bar=123", body="foo"
        )
        rg = ResourceGrabber("http://baz.net/qux.pdf/?bar=123")
        rg.download(self.directory)
        path = os.path.join(self.directory, "qux.pdf")
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")
        HTTPretty.register_uri(
            HTTPretty.GET, "http://baz.net/qux%20file.pdf/?bar=123", body="foo"
        )
        rg = ResourceGrabber("http://baz.net/qux%20file.pdf/?bar=123")
        rg.download(self.directory)
        path = os.path.join(self.directory, "qux file.pdf")
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_download_with_no_path(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/", body="foo")
        rg = ResourceGrabber("http://foo.net/")
        rg.download(self.directory)
        path = os.path.join(self.directory, "foo.net")
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_download_with_attach_filename(self):
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://foo.net/page",
            body="foo",
            content_disposition="attachment; filename=foo.pdf",
        )
        rg = ResourceGrabber("http://foo.net/page")
        rg.download(self.directory)
        path = os.path.join(self.directory, "foo.pdf")
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")
        # another test, playgin with case and whitespaces
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://foo.net/page",
            body="foo",
            content_disposition="attachment;FILENAME  =\tbar.pdf",
        )
        rg = ResourceGrabber("http://foo.net/page")
        rg.download(self.directory)
        path = os.path.join(self.directory, "bar.pdf")
        self.assertTrue(os.path.exists(path))
        with open(path, encoding="utf-8") as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_file_exists(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/foo.pdf", body="foo")
        rg = ResourceGrabber("http://foo.net/foo.pdf")
        with open(os.path.join(self.directory, "foo.pdf"), "w") as f:
            f.write("bar")
        with open(os.path.join(self.directory, "foo_1.pdf"), "w") as f:
            f.write("baz")
        path = os.path.join(self.directory, "foo_2.pdf")
        self.assertEqual(rg.download(self.directory), path)
        self.assertTrue(os.path.exists(path))
        with open(path) as tfile:
            self.assertEqual(tfile.read(), "foo")

    def test_file_exists_no_duplicate(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/foo.pdf", body="foo")
        rg = ResourceGrabber("http://foo.net/foo.pdf")
        with open(os.path.join(self.directory, "foo.pdf"), "w") as f:
            f.write("foo")
        self.assertEqual(rg.download(self.directory, duplicate_check=True), None)

    def test_generate_filename_from_model(self):
        HTTPretty.register_uri(HTTPretty.GET, "http://foo.net/foo.pdf")
        rg = ResourceGrabber("http://foo.net/foo.pdf")
        self.assertEqual(
            rg._generate_filename_from_model("foo.pdf", "bar-baz-%FULLNAME"),
            "bar-baz-foo.pdf",
        )
        self.assertEqual(
            rg._generate_filename_from_model("foo.pdf", "bar-%NAME-baz.%EXTENSION"),
            "bar-foo-baz.pdf",
        )
        self.assertEqual(
            rg._generate_filename_from_model("foo.pdf", "%HOST-foo.pdf"),
            "foo.net-foo.pdf",
        )
        self.assertEqual(
            rg._generate_filename_from_model("foo.pdf", "%INDEX-foo.pdf", index=12),
            "12-foo.pdf",
        )
        self.assertEqual(
            rg._generate_filename_from_model(
                "foo.pdf", "%INDEX-foo.pdf", index=12, index_digit_len=3
            ),
            "012-foo.pdf",
        )
        self.assertEqual(
            rg._generate_filename_from_model(
                "foo.pdf", "foo-%1-bar-%2.pdf", ids=[2, 5], ids_digit_len=[1, 1]
            ),
            "foo-2-bar-5.pdf",
        )
        self.assertEqual(
            rg._generate_filename_from_model(
                "foo.pdf",
                "foo-%1-bar-%2.pdf",
                ids=[2, 84],
                ids_digit_len=[2, 4],
                index_digit_len=4,
            ),
            "foo-02-bar-0084.pdf",
        )


class ResourceGrabberInnerResourcesTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.temp_dir = mkdtemp()
        HTTPretty.enable()
        HTTPretty.register_uri(
            HTTPretty.GET, "http://foo.org/main.html", body=self._read_file("page.html")
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://fooimages.org/image1.png",
            body=self._read_file("image1.png"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://foofiles.org/text1.txt",
            body=self._read_file("text1.txt"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://foofiles.org/text2.txt",
            body=self._read_file("text2.txt"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://foofiles.org/text3.txt",
            body=self._read_file("notfound.html"),
            status=404,
        )
        f = open(os.path.join(self.test_dir, "page.html"), encoding="utf-8")
        self.html = f.read()
        f.close()

    def tearDown(self):
        HTTPretty.disable()

    def _read_file(self, filename):
        with open(os.path.join(self.test_dir, filename), "rb") as f:
            return f.read()

    def test_download(self):
        rg = ResourceGrabber("http://foo.org/main.html")
        rg.download_resources("div.images img", self.temp_dir)
        with open(os.path.join(self.temp_dir, "image1.png"), "rb") as original:
            with open(os.path.join(self.test_dir, "image1.png"), "rb") as downloaded:
                self.assertEqual(original.read(), downloaded.read())

    def test_mass_download(self):
        rg = ResourceGrabber("http://foo.org/main.html")
        rg.download_resources("div.links a", self.temp_dir)
        with open(os.path.join(self.test_dir, "text1.txt")) as downloaded:
            self.assertEqual(
                downloaded.read(), "Allanon was the last of the Druids of Paranor"
            )
        with open(os.path.join(self.test_dir, "text2.txt")) as downloaded:
            self.assertEqual(
                downloaded.read(), "Allanon was killed in the battle with a Jachyra"
            )

    def test_mass_download_with_error(self):
        """Some of target resource contains error"""
        rg = ResourceGrabber("http://foo.org/main.html")
        rg.download_resources("div.linksButSomeBroken a", self.temp_dir)
        with open(os.path.join(self.test_dir, "text1.txt")) as downloaded:
            self.assertEqual(
                downloaded.read(), "Allanon was the last of the Druids of Paranor"
            )
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, "text3.txt")))

    def test_get_internal_links(self):
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/main.html",
            body=self._read_file("page.html"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/page1.html",
            body=self._read_file("page1.html"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/page2.html",
            body=self._read_file("page2.html"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/page3.html",
            body=self._read_file("notfound.html"),
            status=404,
        )
        # these are resources inside pages defined above
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/text1.txt",
            body=self._read_file("text1.txt"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/text2.txt",
            body=self._read_file("text2.txt"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/text3.txt",
            body=self._read_file("text1.txt"),
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            "http://recursive.org/text4.txt",
            body=self._read_file("text2.txt"),
        )

        rg = ResourceGrabber("http://recursive.org/main.html")
        links = rg.get_internal_links(".recursiveTest a", "li a")
        self.assertEqual(
            list(links),
            [
                "http://recursive.org/text1.txt",
                "http://recursive.org/text2.txt",
                "http://recursive.org/text3.txt",
                "http://recursive.org/text4.txt",
            ],
        )


class TextTryNewFilename(unittest.TestCase):
    def test_simple_no_extension(self):
        self.assertEqual(_try_new_filename("foo"), "foo_1")

    def test_simple_extension(self):
        self.assertEqual(_try_new_filename("foo.txt"), "foo_1.txt")

    def test_index_extension(self):
        self.assertEqual(_try_new_filename("foo_2.txt"), "foo_3.txt")

    def test_index_no_extension(self):
        self.assertEqual(_try_new_filename("foo_2"), "foo_3")


if __name__ == "__main__":
    unittest.main()
