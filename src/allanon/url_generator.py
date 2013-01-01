# -*- coding: utf8 -*-


import re

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
            new_url = spre.sub(str(x), url, 1)
            if new_url.find("{")==-1:
                yield new_url, ids
            for y, inner_ids in generate_urls(new_url, level+1):
                yield y,  ids + inner_ids
    elif level==0:
        # first attempt doesn't match: then I'll return original URL
        yield url, []

