.. contents::

Introduction
============

Let's say that you want to access slow streaming site to see something (obviously something not
covered by copyright).

The streaming site use URLs in that format:

    http://legal-streaming-site.org/program-name/season5/episode4/

Let say this is the URL for the episode 4 of the fifth season of your program.
This program has 6 seasons with 22 episode each.

As said before: this site is very slow so you probably want to download the movies in foreground
the watch it later.

To download the movies you need also to watch the HTML inside the page and get some resources
(commonly: and FLV file).
The best would be to download *all* episode in a single (long running) operation instead of manually
doing it.

**Allanon** will help you exactly in such tasks.
You simply need to provide it:

* a *dynamic URL pattern*
* a *query selector* for resources inside the page

Example::

    allanon -s "#movie-container object.movie param[name=movie]" \
    > http://legal-streaming-site.org/program-name/season{1:6}/episode{1:22}

