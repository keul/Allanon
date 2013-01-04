# -*- coding: utf8 -*-

import unittest

from allanon.url_generator import generate_urls
from allanon.url_generator import get_dynamic_urls

class UrlGeneratorTest(unittest.TestCase):

    def test_empty(self):
        results = list(generate_urls("foo bar"))
        self.assertEqual(results, [("foo bar", [], [])])
        self.assertEqual(len(results), 1)

    def test_same_number(self):
        results = list(generate_urls("foo {3:3} bar"))
        self.assertEqual(results[0][0], "foo 3 bar")
        self.assertEqual(len(results), 1)

    def test_range(self):
        results = list(generate_urls("foo {3:5} bar"))
        self.assertEqual(results, [("foo 3 bar", [3], [1]),
                                   ("foo 4 bar", [4], [1]),
                                   ("foo 5 bar", [5], [1])])

    def test_revert(self):
        results = list(generate_urls("foo {4:2} bar"))
        self.assertEqual(results, [("foo 4 bar", [4], [1]),
                                   ("foo 3 bar", [3], [1]),
                                   ("foo 2 bar", [2], [1])])
        results = list(generate_urls("foo {12:9} bar"))
        self.assertEqual(results, [("foo 12 bar", [12], [2]),
                                   ("foo 11 bar", [11], [2]),
                                   ("foo 10 bar", [10], [2]),
                                   ("foo 9 bar", [9], [2])])

    def test_multiple(self):
        results = list(generate_urls("foo {3:4} bar {39:41} baz"))
        self.assertEqual(results, [("foo 3 bar 39 baz", [3, 39], [1, 2]),
                                   ("foo 3 bar 40 baz", [3, 40], [1, 2]),
                                   ("foo 3 bar 41 baz", [3, 41], [1, 2]),
                                   ("foo 4 bar 39 baz", [4, 39], [1, 2]),
                                   ("foo 4 bar 40 baz", [4, 40], [1, 2]),
                                   ("foo 4 bar 41 baz", [4, 41], [1, 2])])

    def test_multiple_many(self):
        results = list(generate_urls("foo {3:4} bar {5:6} baz {0:1} qux {143:143}"))
        self.assertEqual(results, [("foo 3 bar 5 baz 0 qux 143", [3, 5, 0, 143],
                                    [1, 1, 1, 3]),
                                   ("foo 3 bar 5 baz 1 qux 143", [3, 5, 1, 143],
                                    [1, 1, 1, 3]),
                                   ("foo 3 bar 6 baz 0 qux 143", [3, 6, 0, 143],
                                    [1, 1, 1, 3]),
                                   ("foo 3 bar 6 baz 1 qux 143", [3, 6, 1, 143],
                                    [1, 1, 1, 3]),
                                   ("foo 4 bar 5 baz 0 qux 143", [4, 5, 0, 143],
                                    [1, 1, 1, 3]),
                                   ("foo 4 bar 5 baz 1 qux 143", [4, 5, 1, 143],
                                    [1, 1, 1, 3]),
                                   ("foo 4 bar 6 baz 0 qux 143", [4, 6, 0, 143],
                                    [1, 1, 1, 3]),
                                   ("foo 4 bar 6 baz 1 qux 143", [4, 6, 1, 143],
                                    [1, 1, 1, 3])])


class DynamicURLGenerationTest(unittest.TestCase):
    
    def test_urls(self):
        self.assertEqual(tuple(get_dynamic_urls(('http://host1/{1:2}/?param={3:4}',))),
                         (('http://host1/1/?param=3', [1, 3], [1, 1]),
                          ('http://host1/1/?param=4', [1, 4], [1, 1]),
                          ('http://host1/2/?param=3', [2, 3], [1, 1]),
                          ('http://host1/2/?param=4', [2, 4], [1, 1]))
                         )

    def test_multiple_urls(self):
        self.assertEqual(tuple(get_dynamic_urls(('http://host1/{1:2}/?param={3:4}',
                                                 'http://host2/dummy?param={11:12}',))),
                         (('http://host1/1/?param=3', [1, 3], [1, 1]),
                          ('http://host1/1/?param=4', [1, 4], [1, 1]),
                          ('http://host1/2/?param=3', [2, 3], [1, 1]),
                          ('http://host1/2/?param=4', [2, 4], [1, 1]),
                          ('http://host2/dummy?param=11', [11], [2]),
                          ('http://host2/dummy?param=12', [12], [2]))
                         )


if __name__ == "__main__":
    unittest.main()
