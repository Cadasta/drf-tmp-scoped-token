import codecs
import os
import re
import sys
from setuptools import setup, find_packages, Command


###
NAME = 'drf-tmp-scoped-token'
META_PATH = ['rest_framework_tmp_scoped_token', '__init__.py']
PACKAGES = find_packages()
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
]
INSTALL_REQUIRES = [
    'djangorestframework>=3.6',
    'six'
]
###


def read(parts):
    """
    Build an absolute path from parts array and and return the contents
    of the resulting file.  Assume UTF-8 encoding.
    """
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(cur_dir, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


def ensure_clean_git(operation='operation'):
    """ Verify that git has no uncommitted changes """
    if os.system('git diff-index --quiet HEAD --'):
        print("Unstaged or uncommitted changes detected. {} aborted.".format(
            operation.capitalize()))
        sys.exit()


class CleanCommand(Command):
    """ Custom clean command to tidy up the project root. """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


class PublishCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        ensure_clean_git('publishing')
        if os.system("pip freeze | grep twine"):
            print("twine not installed.\nUse `pip install twine`.\nExiting.")
            sys.exit()
        os.system("python setup.py sdist")
        os.system("python setup.py bdist_wheel")
        os.system("twine upload --skip-existing dist/*")


class TagCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        ensure_clean_git('tagging')
        os.system("git tag -a {0} -m 'version {0}'".format(
            find_meta('version')))
        os.system("git push --tags")


if __name__ == "__main__":
    long_description = open('README.md').read()
    try:
        import pypandoc
        pattern = re.compile('<.*\w*>')
        no_html_descr = re.sub(pattern, '', long_description)
        long_description = pypandoc.convert_text(
            no_html_descr, 'rst', 'markdown')
    except(IOError, ImportError):
        if 'publish' in sys.argv:
            raise

    setup(
        name=NAME,
        packages=PACKAGES,
        classifiers=CLASSIFIERS,

        version=find_meta('version'),
        description=find_meta('description'),
        author=find_meta('author'),
        author_email=find_meta('email'),
        license=find_meta('license'),
        url=find_meta('url'),

        long_description=long_description,

        install_requires=INSTALL_REQUIRES,
        cmdclass={
            'clean': CleanCommand,
            'publish': PublishCommand,
            'tag': TagCommand,
        }
    )
