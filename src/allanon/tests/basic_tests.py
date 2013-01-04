# -*- coding: utf8 -*-

import unittest

from allanon.main import get_urls

class AllanonTest(unittest.TestCase):

    def test_urls(self):
        self.assertEqual(tuple(get_urls(('http://host1/{1:2}/?param={3:4}',))),
                         (('http://host1/1/?param=3', [1, 3], [1, 1]),
                          ('http://host1/1/?param=4', [1, 4], [1, 1]),
                          ('http://host1/2/?param=3', [2, 3], [1, 1]),
                          ('http://host1/2/?param=4', [2, 4], [1, 1]))
                         )

    def test_multiple_urls(self):
        self.assertEqual(tuple(get_urls(('http://host1/{1:2}/?param={3:4}',
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
