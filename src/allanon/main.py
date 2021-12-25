# -*- coding: utf8 -*-

import sys
import os.path
import time

from optparse import OptionParser, OptionGroup

from allanon import config
from allanon.url_generator import get_dynamic_urls
from allanon.url_generator import search_resources
from allanon.resouce_grabber import ResourceGrabber

VERSION = (
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "version.txt"))
    .read()
    .strip()
)
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

parser = OptionParser(
    usage="Usage: %prog [option, ...] url_model [url_model, ...]",
    version="%prog " + VERSION,
    description=DESCRIPTION,
    prog="allanon",
)

parser.remove_option("--help")
parser.add_option(
    "--help",
    "-h",
    action="store_true",
    default=False,
    help="show this help message and exit",
)

parser.add_option(
    "--search",
    "-s",
    dest="search_queries",
    default=[],
    action="append",
    metavar="QUERY",
    help="Query for other URLs inside every argument URLs and download them instead "
    "of the URL itself.\n"
    "See the pyquery documentation for more info about the query "
    "format (http://packages.python.org/pyquery/).\n"
    "Can be provided multiple times to recursively search for links to "
    "pages until resources are found (last search filter must always "
    "points to the final resource to download).",
)
parser.add_option(
    "--directory",
    "-d",
    dest="destination_directory",
    default=os.getcwd(),
    metavar="TARGET_DIR",
    help="Directory where to store all resources that will be downloaded.\n"
    "Default is the current directory.\n"
    'Can be also a directory path string in nix format (like "foo/bar"), '
    "in that case all intermediate directories will be created.\n"
    "You can use some markers for creating a dynamic name.\n"
    "Use %x (%1, %2, ...) to include the current URLs range "
    "(if any). Use %1 for the first range in the URL, %2 for "
    "the second, and so on.\n"
    "Use %HOST for include the original host where the resource has "
    "been downloaded.\n"
    "Use %INDEX for include a progressive number of downloaded resources.\n",
)
parser.add_option(
    "--filename",
    "-f",
    dest="filename_model",
    default=None,
    metavar="FILENAME",
    help="Download resources with a custom, dynamic, filename.\n"
    "You can use some markers for creating a dynamic name.\n"
    "Use %x (%1, %2, ...) to include the current URLs range "
    "(if any). Use %1 for the first range in the URL, %2 for "
    "the second, and so on.\n"
    "Use %HOST for include the original host where the resource has "
    "been downloaded.\n"
    "Use %INDEX for include a progressive number of downloaded resources.\n"
    "Use %NAME for include the original filename (without extension).\n"
    "Use %EXTENSION for include the original file extensions.\n"
    "Use %FULLNAME for include the original filename (with extension).\n"
    'Default is "%FULLNAME"',
)
parser.add_option(
    "--check-duplicate",
    "-c",
    action="store_true",
    dest="duplicate_check",
    default=False,
    help="When finding a duplicate filename check they are duplicates. "
    "In this case, do not save the new file. Default action is to keep all "
    "resources handling filename collision, without checking files content.",
)
parser.add_option(
    "--offset",
    "-o",
    type="int",
    dest="offset",
    default=0,
    help="Start download resources only after skipping first OFFSET found.\n"
    "This only affects resource that would be downloaded (not crawled).\n"
    "Default is: do not skip any resource.",
)

group = OptionGroup(
    parser,
    "Request options",
    "This set of options control how Allanon connect to remote servers.",
)

group.add_option(
    "--user-agent",
    "-u",
    dest="user_agent",
    default=None,
    metavar="USER_AGENT",
    help="Change the User-Agent header sent with every request.\n"
    'Default is "Allanon Crawler %s".' % VERSION,
)
group.add_option(
    "--timeout",
    "-t",
    dest="timeout",
    default=60.0,
    type="float",
    help="Number of seconds to wait for server response before giving up.\n"
    "Default is 60. Use 0 for disable timeout.",
)
group.add_option(
    "--sleep-time",
    dest="sleep",
    default=1.0,
    type="float",
    help="Number of seconds to wait after each downloaded resource.\n"
    "Use this to not overload a server or being banned.\n"
    "Default is 1.",
)
parser.add_option_group(group)


def main(options=None, *args):
    if not options:
        # invocation from command line
        options, args = parser.parse_args()

    if len(args) < 1 or options.help:
        # personal version of the help, to being able to keep \n in description
        result = [
            "Allanon: a crawler for visit a predictable set of URLs, "
            "and download resources from them\n"
        ]
        result.append(parser.get_usage())
        result.append(DESCRIPTION + "\n")
        result.append(parser.format_option_help(parser.formatter))
        result.append("By Luca Fabbri - luca<at>keul.it\n")
        result.append(
            "See https://github.com/keul/Allanon for detailed documentation or "
            "provide bug report."
        )
        print(("\n".join(result)))
        sys.exit(0)

    if options.user_agent:
        config.USER_AGENT = options.user_agent
    if options.timeout:
        config.TIMEOUT = options.timeout
    if options.sleep:
        config.SLEEP_TIME = options.sleep

    # first, command line URLs sequence
    try:
        urls = get_dynamic_urls(args)
        index_digit_len = 0

        # optimization: we don't need to count all the URLs in that case
        if options.filename_model and "%INDEX" in options.filename_model:
            urls = tuple(urls)
            index_digit_len = len(str(len(urls)))

        # in case we are not directly downloading, we need to look for inner resources
        if options.search_queries:
            urls = search_resources(urls, options.search_queries)

        for index, urls_data in enumerate(urls):
            if options.offset and (index + 1) <= options.offset:
                print(("Skipping resource %d due to offset settings" % (index + 1)))
                continue
            url, ids, max_ids = urls_data
            rg = ResourceGrabber(url)
            rg.download(
                options.destination_directory,
                options.filename_model,
                ids,
                index + 1,
                ids_digit_len=max_ids,
                index_digit_len=index_digit_len,
                duplicate_check=options.duplicate_check,
            )
            time.sleep(options.sleep)
    except KeyboardInterrupt:
        print("\nTerminated by user action")
        sys.exit(1)


if __name__ == "__main__":
    main()
