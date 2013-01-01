# -*- coding: utf8 -*-

import unittest

from allanon.main import get_urls

class AllanonTest(unittest.TestCase):

    def test_urls(self):
        self.assertEqual(tuple(get_urls(('http://host1/{1:2}/?param={3:4}',))),
                         (('http://host1/1/?param=3', [1, 3]),
                          ('http://host1/1/?param=4', [1, 4]),
                          ('http://host1/2/?param=3', [2, 3]),
                          ('http://host1/2/?param=4', [2, 4]))
                         )

    def test_multiple_urls(self):
        self.assertEqual(tuple(get_urls(('http://host1/{1:2}/?param={3:4}',
                                         'http://host2/dummy?param={5:6}',))),
                         (('http://host1/1/?param=3', [1, 3]),
                          ('http://host1/1/?param=4', [1, 4]),
                          ('http://host1/2/?param=3', [2, 3]),
                          ('http://host1/2/?param=4', [2, 4]),
                          ('http://host2/dummy?param=5', [5]),
                          ('http://host2/dummy?param=6', [6]))
                         )
        

if __name__ == "__main__":
    unittest.main()
