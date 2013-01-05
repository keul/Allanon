# -*- coding: utf8 -*-

import sys
import os.path

from optparse import OptionParser

from allanon import logger
from allanon.url_generator import get_dynamic_urls
from allanon.url_generator import search_resources
from allanon.resouce_grabber import ResourceGrabber

VERSION = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt")).read()
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

parser = OptionParser(usage="Usage: %prog [option, ...] url_model [url_model, ...]",
                      version="%prog " + VERSION,
                      description=DESCRIPTION,
                      prog="allanon")

parser.remove_option("--help")
parser.add_option('--help', '-h',
                 action="store_true", default=False,
                 help='show this help message and exit')

parser.add_option('--search', '-s', dest="search_queries", default=[], action="append",
                  metavar="QUERY",
                  help="Query for other URLs inside every argument URLs and download them instead "
                       "of the URL itself.\n"
                       "See the pyquery documentation for more info about the query "
                       "format (http://packages.python.org/pyquery/).\n"
                       "Can be provided multiple times to recursively search for links to "
                       "pages until resources are found (last search filter must always "
                       "points to the final resource to download).")
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
                       "Use %INDEX for include a progressive number of downloaded resources.\n"
                       "Use %NAME for include the original filename (without extension).\n"
                       "Use %EXTENSION for include the original file extensions.\n"
                       "Use %FULLNAME for include the original filename (with extension)\n"
                       "Default is \"%FULLNAME\"")


def main(options=None, *args):
    if not options:
        # invocation from command line
        options, args = parser.parse_args()
    
    if len(args)<1 or options.help:
        # personal version of the help, to being able to keep \n in description
        result = ['Allanon: a crawler for visit a predictable set of URLs, '
                  'and download resources from them\n']
        result.append(parser.get_usage())
        result.append(DESCRIPTION+"\n")
        result.append(parser.format_option_help(parser.formatter))
        result.append('See https://github.com/keul/Allanon for detailed documentation or '
                      'provide bug report.')
        print "\n".join(result)
        sys.exit(0)
    
    # first, command line URLs sequence
    try:
        urls = get_dynamic_urls(args)
        index_digit_len = 0

        # optimization: we don't need to count all the URLs in that case
        if options.filename_model and '%INDEX' in options.filename_model:
            urls = tuple(urls)
            index_digit_len = len(str(len(urls)))

        # in case we are not directly downloading, we need to look for inner resources
        if options.search_queries:
            urls = search_resources(urls, options.search_queries)

        for index, urls_data in enumerate(urls):
            url, ids, max_ids = urls_data
            rg = ResourceGrabber(url)
            try:
                rg.download(options.destination_directory, options.filename_model, ids, index+1,
                            ids_digit_len=max_ids,
                            index_digit_len=index_digit_len)
            except IOError, inst:
                logger.warning(str(inst))
                print "Skipping (%s)" % inst
    except KeyboardInterrupt:
        print "\nTerminated by user action"
        sys.exit(1)


if __name__ == '__main__':
    main()
