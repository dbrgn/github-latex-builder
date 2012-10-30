Github LaTeX Builder
====================

Github LaTeX builder is a script that provides a Github Webhook URL and builds
the LaTeX repository on each new commit.

.. DANGER::

    This script is not yet finished. There are still some serious security
    issues that need to be fixed. In case you still want to run it, make sure
    that the permissions are locked down and you're running the script in a
    chroot.

Setup Server
------------

Prerequisites:

- A LaTeX compiler (e.g. texlive, installing `texlive-full` is recommended)
- GNU Make
- latexmk (usually comes with texlive)
- Python 2
- pip

::

    pip install -r requirements.txt
    python server.py

The webhook URL is now running at http://localhost:9393/webhook

Other commandline options::

    Usage:
        server.py [-i HOST] [-p PORT]
        server.py --help
        server.py --version

    Options:
        -h --help  Show this message.
        --version  Show the version.
        -i HOST    Hostname or IP to bind to [default: localhost].
        -p PORT    Port number [default: 9393].

Setup Repository
----------------

Add the publicly accessible Webhook URL to `https://github.com/<user>/<repo>/admin/hooks`.

License
-------

MIT License, see `LICENSE` file.
