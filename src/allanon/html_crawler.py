# -*- coding: utf8 -*-

from pyquery import PyQuery
from urlparse import urlparse

def apply_base_url(url, base_url):
    if url.startswith('http') or url.startswith('https') or url.startswith('ftp'):
        return url
    parsed_url = urlparse(base_url)
    base_url = base_url.replace("?%s" % parsed_url.query, '')
    if url.startswith('/'):
        # root absolute path
        base_url = "%s://%s" % (parsed_url.scheme, parsed_url.hostname)
        url = url[1:]
    else:
        # relative path
        base_url = "%s://%s/%s" % (parsed_url.scheme,
                                   parsed_url.hostname,
                                   "/".join(parsed_url.path.split('/')[:-1]))
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    return "%s/%s" % (base_url, url)


def search_in_html(html, query, base_url=''):
    """
    Apply the CSS3 query (in pyquery format) to the HTML and return resource URLs
    """
    pq = PyQuery(html)
    elements = pq(query)
    for element in elements:
        if isinstance(element, basestring):
            # BBB pyquery return "something" also when no elements are found... bah!
            continue 
        if element.tag=='img':
            yield apply_base_url(element.attrib.get('src'), base_url)
        elif element.tag=='a':
            yield apply_base_url(element.attrib.get('href'), base_url)
        elif element.tag=='embed':
            yield apply_base_url(element.attrib.get('src'), base_url)
        elif element.tag=='object':
            yield apply_base_url(element.attrib.get('data'), base_url)
        elif element.tag=='param':
            yield apply_base_url(element.attrib.get('value'), base_url)
        elif element.tag=='source':
            yield apply_base_url(element.attrib.get('src'), base_url)
        else:
            # default, hoping that we are pointing to some text that is an URL
            yield apply_base_url(element.text, base_url)

