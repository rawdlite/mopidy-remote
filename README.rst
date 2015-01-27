****************************
Mopidy-Remoteplay
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-Remote.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Remote/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-Remote.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Remote/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/rawdlite/mopidy-remote/master.png?style=flat
    :target: https://travis-ci.org/rawdlite/mopidy-remote
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/rawdlite/mopidy-remote/master.svg?style=flat
   :target: https://coveralls.io/r/rawdlite/mopidy-remote?branch=master
   :alt: Test coverage

Operate Mopidy with a Remote Control.
Autoplay for different moods
Learn to avoid tracks that have been skipped by user.
Rate tracks.

Prerequisites
=============
- working LIRC setup.
- mpc for basic commands

Installation
============

Install by running::

    pip install Mopidy-Remote


Operations
==========
Basic Operations are hanndled by a http request like:
curl http://192.168.0.2:6688/remote/\?cmd\=<Cmd>
Cmd can be

- play
- pause
- stop
- next
- previous

Advanced Operations provided

- play more_by_(album|artist|genre)
curl http://192.168.0.2:6688/remote/\?cmd\=more_of_artist

- play remote track (out of a selection defined by a query construct.)
curl --data '{"query": {u"artist": [u"Super Flu"]},"uris": ["spotify:","beetslocal"],"options": {"track": 5,"album": 0}}' http://192.168.0.2:6688/remote/

- play remote album (out of a selection defined by a query construct.)
curl --data '{"query": {u"artist": [u"Solomun"]},"options": {"track": 0,"album": 1}}' http://192.168.0.2:6688/remote/

- continous random play (radio mode) **work in progress

- find related artists on LastFM *TODO

- rate a track ( 1 to 5 star rating) *TODO

- track info (spoken) *TODO


Internal Operations
- maintain play count  **work in progress

- register skips, maintain skip count  **work in progress

- weigh in rating, play count and skip count on randomnes *TODO

- save playlist (on mopidy restart) *TODO
 
Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-Remote to your Mopidy configuration file::

    [remote]
    # TODO: Add example of extension config


Project resources
=================

- `Source code <https://github.com/rawdlite/mopidy-remote>`_
- `Issue tracker <https://github.com/rawdlite/mopidy-remote/issues>`_
- `Development branch tarball <https://github.com/rawdlite/mopidy-remote/archive/master.tar.gz#egg=Mopidy-Remote-dev>`_


Changelog
=========

v0.0.1 (UNRELEASED)
----------------------------------------

- Initial release.
