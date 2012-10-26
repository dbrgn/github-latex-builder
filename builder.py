from __future__ import with_statement  # py2.5
import os
import errno
import conf
import contextlib
import subprocess


@contextlib.contextmanager  
def chdir(dirname):
    """Context manager to change the cwd."""
    curdir = os.getcwd()
    try:
        os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


class Builder(object):
    """The LaTeX Builder class. Builds PDFs via Make or latexmk.
    
    Algorithm:

    - Create ``build`` directory and ``pdf`` directories, if they don't exist.
    - Create project folder inside ``build`` and ``pdf`` directories.
    - Create a lockfile ``build/<reponame>/.<commit-id>``.

    - Clone repo into ``build/<reponame>/<commit-id>/``.

    - Try to run ``make`` inside repo name.
    - If no Makefile exists, look for .tex-files in the root directory. Build them via ``latexmk``.

    - Clean ``pdf/<reponame>/`` directory.
    - Recursively find all ``pdf`` documents in the build dir. Copy them to ``pdf/<reponame>/``.

    - Remove Lockfile.
        
    """

    def __init__(self, name, repo_url, commit):
        self.name = name
        self.repo_url = repo_url
        self.commit = commit
        if repo_url.startswith('https://'):
            self.clone_url = repo_url + '.git'
        elif repo_url.startswith('git://'):
            self.clone_url = repo_url
        else:
            raise ValueError('Invalid repo_url')

    def _prepare(self):
        """Prepare directories and environment."""

        # Create directories

        def safely_create_directory(path):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        self.build_dir = os.path.join(os.getcwdu(), conf.BUILD_DIR_NAME)
        self.pdf_dir = os.path.join(os.getcwdu(), conf.PDF_DIR_NAME)
        self.repo_build_dir = os.path.join(self.build_dir, self.name)
        self.repo_pdf_dir = os.path.join(self.pdf_dir, self.name)
        self.clone_dir = os.path.join(self.repo_build_dir, self.commit)

        safely_create_directory(self.build_dir)
        safely_create_directory(self.pdf_dir)
        safely_create_directory(self.repo_build_dir)
        safely_create_directory(self.repo_pdf_dir)

        # Create lockfile

        try:
            lockfile_name = os.path.join(self.repo_build_dir, '.' + self.commit)
            fd = os.open(lockfile_name, os.O_EXCL | os.O_CREAT, 0664)
        except OSError as e:
            if e.errno == errno.EEXIST:
                raise RuntimeError('Lockfile exists. If you\'re sure that no '
                        'other process is currently building that project, you '
                        'can remove "%s" manually.' % lockfile_name)
            raise
        else:
            os.close(fd)


    def _clone(self):
        """Clone repository to build folder."""
        if not subprocess.call(['git', 'clone', self.clone_url, self.clone_dir]) == 0:
            raise RuntimeError('git clone failed')
        with chdir(self.clone_dir):
            if os.getcwd() != self.clone_dir:
                raise RuntimeError('Changing into build directory failed.')
            if not subprocess.call(['git', 'checkout', self.commit]) == 0:
                raise RuntimeError('git checkout failed')

    def _build(self):
        """Build specified commit."""
        raise NotImplementedError

    def _copy(self):
        """Copy PDF files to output directory."""
        raise NotImplementedError

    def _cleanup(self):
        """Do cleanups, like removing lockfiles."""
        raise NotImplementedError

    def run(self):
        """Prepare and build specified commit."""
        self._prepare()
        self._clone()
        self._build()
        self._copy()
        self._cleanup()