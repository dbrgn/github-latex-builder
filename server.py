"""Github LaTeX builder.

Usage:
    server.py [-i HOST] [-p PORT]
    server.py --help
    server.py --version

Options:
    -h --help  Show this message.
    --version  Show the version.
    -i HOST    Hostname or IP to bind to [default: localhost].
    -p PORT    Port number [default: 9393].

"""
__version__ = '0.0.1'
from bottle import get, post, run, redirect, request, abort, HTTPResponse
from docopt import docopt
import multiprocessing
import json
import builder


@get('/')
def home():
    return '<img src="http://i1.kym-cdn.com/photos/images/newsfeed/000/345/309/5eb.gif">'


@post('/webhook')
def store():
    """Webhook for notifications about a new commit on Github."""
    try:
        data = json.loads(request.POST['payload'])
    except ValueError:
        abort(400, 'Bad request: Could not decode request body')
    name = data['repository']['name']
    repo_url = data['repository']['url']
    commit = data['after']
    b = builder.Builder(name, repo_url, commit)
    p = multiprocessing.Process(target=b.run)
    p.start()
    raise HTTPResponse('Started build process in background.\n', 202)


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    try:
        port = int(args['-p'])
    except ValueError:
        raise ValueError('Invalid port number: %s.' % args['-p'])
    run(host=args['-i'], port=port, debug=True)
