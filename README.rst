.. contents::

Introduction
============

Let's say that you want to access a slow streaming site to see something (obviously: something not
protected by copyright).

The streaming site use URLs in that format:

    http://legal-streaming-site.org/program-name/season5/episode4/

Every page contains some HTML code like the following::

    ....
        <div id="video-container">
           ...
           <embed src="http://someotherurl.org/qwerty.flv" ... 
           ...
        <div>
    ...

Let say this is the URL for the episode 4 of the fifth season of your program.
You know that this program has 6 seasons with 22 episode each.

As said before: this site is very slow so you probably want to download the movies in background
then watch them later.

To download the movies you need also to watch the HTML inside the page and get some resources
(commonly: and FLV file).
The best would be download *all* episode in a single (long running) operation instead of manually
doing it.

**Allanon** will help you exactly in such tasks.
You simply need to provide it:

* a simple URL or a *dynamic URL pattern*
* a *query selector* for resources inside the page

Quick example (you can keep it single lined)::

    allanon --search "#movie-container embed" \
    > "http://legal-streaming-site.org/program-name/season{1:6}/episode{1:22}"

Documentation
=============

Installation
------------

You can use `distribute`__ or `pip`__ to install the utility in your Python environment.

__ http://pypi.python.org/pypi/distribute
__ http://pypi.python.org/pypi/pip

::

    $ easy_install Allanon

or alternately::

    $ pip install Allanon

Invocation
----------

After installing you will be able to run the ``allanon`` script from command line.
For example: run the following for access the utility help::

    $ allanon --help

Basic usage (you probably don't need Allanon at all for this)
-------------------------------------------------------------

The ``allanon`` script accept an URL (or a list of URLs) to be downloaded::

    $ allanon "http://myhost/folder/image1.jpg" "http://myhost/folder/image2.jpg" ...

Every command line URL given to Allanon can be a simple URL or an *URL model* like the following::

    $ allanon "http://myhost/folder/image{1:50}.jpg"

This will crawl 50 different URL automatically. 

Main usage (things became interesting now)
------------------------------------------

The ``allanon`` script take an additional ``--search`` parameter (see the first example given
above).
When you provide it, you are meaning:

    "*I don't want to download the given URL, but this/those URL contain link to
    file that I really want*".

The search parameter format must be CSS 3 compatible, like the one supported the famous
`jQuery library`__, and it's based onto the `pyquery`__ library.
Se it's documentation for more details about what you can look for.

__ http://api.jquery.com/category/selectors/
__ http://packages.python.org/pyquery/

Extreme usage (uncommon, but possible)
--------------------------------------

The ``--search`` parameter can be provided multiple times::

    allanon --search "ul.image-repos a" \
    > --search "div.image-containers img" \ 
    > "http://image-repository-sites.org/category{1:30}.html"

When you provide (for example) two different search parameters, you are meaning:
    "*I dont' want to download the given URL. This/those URL contains links to secondary pages,
    and inside those pages there are links to resources I want to download*"

Filters are applied in the given order, so:

* Allanon will search inside 30 pages named *category1.html*, *category2.html*, ...
* inside those pages, Allanon will look for all links inside *UL* tags with CSS class
  "*image-repos*" and recurvisely search inside them
* inside those pages, Allanon will looks for images inside *DIV* with class "*image-containers*"
* images will be downloaded

Potentially you can continue this way, providing a third level of filters, and so on.

Naming downloaded resources
---------------------------

Allanon download all files in the current directory (or in the directory specified using the
``--directory`` option) so a filename conflict is possible.

Instead of downloading resources "as is", you can change dynamically the filename using the
``--filename`` option.

An example::

    $ allanon --filename="%HOST-%INDEX-section%1-version%3-%FULLNAME"
    > "http://foo.org/pdf-repo-{1:10}/file{1:50}.pdf?version={0:3}"

``%HOST``
    Will be replaced with the hostname used in the URL.
``%INDEX``
    Is a progressive from 1 to the number of downloaded resources.
``%X``
    When using dynamic URLs models you can refer to the current number of an URL
    section.
    
    In this case "%1" is the current "pdf-repo-*x*" number and "%3" is the "version"
    parameter value.
``%FULLNAME``
    If the original filename (the one used if ``--filename`` is not provided).
    
    You can also use the ``%NAME`` and ``%EXTENSION`` to get only the name of the file
    (without extension) or simply the extension.

TODO
====

This utility is in alpha stage, a lot of thing can goes wrong when downloading and many features
are missing:

* supporting authentication
* do not try to download or crawl when the loaded page is an error/not-found page
* what to do with duplicates resources (right now: we are skipping)?
* verbosity controls
* handle timeout and sleep time after each download

If you find other bug or want to ask for a missing feature, use the `product issue tracker`__.

__ https://github.com/keul/Allanon/issues

