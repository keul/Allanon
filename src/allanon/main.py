# -*- coding: utf8 -*-

import os

from optparse import OptionParser

from allanon.url_generator import generate_urls
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
                  help="Look for resource inside every URLs and download it instead of the "
                       "URL itself.\n"
                       "See the pyquery documentation for more info about the query "
                       "format (http://packages.python.org/pyquery/).")
parser.add_option('--directory', '-d', dest="destination_directory", default=os.getcwd(),
                  metavar="TARGET_DIR",
                  help="Directory where to store all resources that will be downloaded.\n"
                       "Default if the current directory")
parser.add_option('--filename', '-f', dest="filename_model", default=None, metavar="FILENAME",
                  help="Download resources with a custom, dynamic, filename.\n"
                       "You can use some marker for creating a dynamic content.\n"
                       "Use %x (%1, %2, ...) for include the current URLs range "
                       "(if any). Use %1 for the first range in the URL, %2 for "
                       "the second, and so on.\n"
                       "Use %HOST for include the original host where the resource has "
                       "been downloaded.\n"
                       "Use %NAME for include the original filename (without extension).\n"
                       "Use %EXTENSION for include the original file extensions.\n"
                       "Use %FULLNAME for include the original filename (with extension)\n"
                       "Default is \"%FULLNAME\"")


def get_urls(raw_urls):
    for raw_url in raw_urls:
        for url in generate_urls(raw_url):
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
    for index, url in enumerate(urls):
        rg = ResourceGrabber(url)
        if not options.search:
            rg.download(options.destination_directory, options.filename_model, index+1)
        else:
            rg.download_resources(options.search, options.destination_directory,
                                  options.filename_model, index+1)

if __name__ == '__main__':
    main()
