# -*- coding: utf8 -*-

from pyquery import PyQuery

def search_in_html(html, query):
    pq = PyQuery(html)
    elements = pq(query)
    for element in elements:
        if element.tag=='img':
            yield element.attrib.get('src')
        elif element.tag=='a':
            yield element.attrib.get('href')
        else:
            # default, hoping that we are pointing to some text that is an URL
            yield element.text

