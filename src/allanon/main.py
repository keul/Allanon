# -*- coding: utf8 -*-

import os

from optparse import OptionParser

from allanon.url_generator import generate
from allanon.resouce_grabber import ResourceGrabber

VERSION = "0.1"
DESCRIPTION = """
Crawl a replicable set of URLs, then download resources from them.

URLs can be composed by a variable range(s) like:

    http://foo.org/{1:10}/page?section={1:4}

This will make this utility to crawl through a set of URLs like this:

    http://foo.org/1/page?section=1
    http://foo.org/1/page?section=2
    ...
    http://foo.org/2/page?section=1
    ...
    http://foo.org/10/page?section=4

""".strip()

parser = OptionParser(usage="Usage: %prog [option, ...] urls_model [urls_model, ...]",
                      version="%prog " + VERSION,
                      description=DESCRIPTION,
                      prog="allanon")

parser.remove_option("--help")
parser.add_option('--help', '-h',
                 action="store_true", default=False,
                 help='show this help message and exit')

parser.add_option('--search', '-s', dest="search", default=None,
                  help="Look for this resource inside every URLs and download it.\n"
                       "See the pyquery documentation for more info about the query "
                       "format (http://packages.python.org/pyquery/).")

parser.add_option('--directory', '-d', dest="destination_directory", default=os.getcwd(),
                  metavar="TARGET_DIR",
                  help="Directory where to store all resources that will be downloaded.\n"
                       "Default if the current directory")


def get_urls(raw_urls):
    for raw_url in raw_urls:
        for url in generate(raw_url):
            yield url


def main():
    options, args = parser.parse_args()
    
    if len(args)<1 or options.help:
        # personal version of the help, to being able to keep \n in description
        result = []
        result.append(parser.get_usage())
        result.append(DESCRIPTION+"\n")
        result.append(parser.format_option_help(parser.formatter))
        print "\n".join(result)
    
    urls = get_urls(args)
    for url in urls:
        rg = ResourceGrabber(url)
        if not options.search:
            rg.download(options.destination_directory)


if __name__ == '__main__':
    main()