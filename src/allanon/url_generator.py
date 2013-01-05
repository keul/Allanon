# -*- coding: utf8 -*-


import re
from allanon.resouce_grabber import ResourceGrabber

SPREAD_MODEL = r"""\{(?P<start>\d+)\:(?P<end>\d+)\}"""
spre = re.compile(SPREAD_MODEL)

def generate_urls(url, level=0):
    """
    Using a string (commonly an URL) that contains a range section like this:
    
        foo {n:m} bar
    
    This will iterate through a set of results like those:
    
        foo n bar
        foo n+1 bar
        foo n+2 bar
        ...
        foo m bar
    
    This will also work when n>m:
    
        foo n bar
        foo n-1 bar
        foo n-2 bar
        ...
        foo m bar    
    
    The range section can be used also multiple times:
    
        foo {n:m} bar {x:y} baz

    This will generate:
    
        foo n bar x baz
        foo n bar x+1 baz
        ...
        foo n bar y baz
        foo n+1 bar x baz
        ...
        foo m bar y baz
    """
    
    match = spre.search(url)
    if match:
        start, end = match.groups()
        start = int(start); end = int(end)
        step = start<=end and 1 or -1
        for x in xrange(start, end+step, step):
            ids = [x]
            max_ids = [len(str(max(start, end+step)))]
            new_url = spre.sub(str(x), url, 1)
            if new_url.find("{")==-1:
                yield new_url, ids, max_ids
            for y, inner_ids, inner_max_ids in generate_urls(new_url, level+1):
                yield y, ids + inner_ids, max_ids + inner_max_ids
    elif level==0:
        # first attempt doesn't match: then I'll return original URL
        yield url, [], []


def get_dynamic_urls(raw_urls, outer_ids=[], outer_max_ids=[]):
    for raw_url in raw_urls:
        for url, ids, max_ids in generate_urls(raw_url):
            ids = ids or outer_ids
            max_ids = max_ids or outer_max_ids
            yield url, ids, max_ids


def search_resources(urls, search_queries):
    for generated_url in urls:
        url, ids, max_ids = generated_url
        rg = ResourceGrabber(url)
        inner_urls = rg.get_internal_links(*search_queries)
        for url in inner_urls:
            yield url, ids, max_ids

