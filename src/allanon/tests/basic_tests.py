# -*- coding: utf8 -*-

import unittest

from allanon.main import get_urls

class AllanonTest(unittest.TestCase):

    def test_multiple_urls(self):
        self.assertEqual(tuple(get_urls(('http://host1/{1:2}/?param={3:4}',
                                         'http://host2/dummy?param={5:6}'))),
                         ('http://host1/1/?param=3',
                          'http://host1/1/?param=4',
                          'http://host1/2/?param=3',
                          'http://host1/2/?param=4',
                          'http://host2/dummy?param=5',
                          'http://host2/dummy?param=6',)
                         )
        

if __name__ == "__main__":
    unittest.main()
