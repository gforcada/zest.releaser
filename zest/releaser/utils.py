# Small utility methods.
import logging
import re
import sys
import urllib

logger = logging.getLogger('utils')

WRONG_IN_VERSION = ['svn', 'dev', '(']


def loglevel():
    """Return DEBUG when -v is specified, INFO otherwise"""
    if len(sys.argv) > 1:
        if '-v' in sys.argv:
            return logging.DEBUG
    return logging.INFO


def strip_version(version):
    """Strip the version of all whitespace."""
    return version.strip().replace(' ', '')



def ask(question, default=True):
    """Ask the question in y/n form and return True/False.

    If you don't want a default 'yes', set default to None (or to False if you
    want a default 'no').

    """
    while True:
        yn = 'y/n'
        if default is True:
            yn = 'Y/n'
        if default is False:
            yn = 'y/N'
        print question + " (%s)?" % yn
        input = raw_input()
        if not input:
            if default is not None:
                return default
            print 'Please explicitly answer y/n'
            continue
        return 'y' in input.lower()



def ask_server(question, servers):
    """Ask for the server to upload the package to and return the selected
    server. The listed options are taken from the .pypirc.
    """
    while True:
        print question + ' - '.join(servers)
        input = raw_input()
        if not input:
            if input in servers:
                return  input
            print 'Please answer with the name of one of the servers listed./n'
            continue
        return input

def fix_rst_heading(heading, below):
    """If the 'below' line looks like a reST line, give it the correct length.

    This allows for different characters being used as header lines.
    """
    if len(below) == 0:
        return below
    first = below[0]
    if first not in '-=`~':
        return below
    below = first * len(heading)
    return below


def cleanup_version(version):
    """Check if the version looks like a development version."""
    for w in WRONG_IN_VERSION:
        if version.find(w) != -1:
            logger.debug("Version indicates development: %s.", version)
            version = version[:version.find(w)].strip()
            logger.debug("Removing debug indicators: %r", version)
    return version


def extract_headings_from_history(history_lines):
    """Return list of dicts with version-like headers.

    We check for patterns like '2.10 (unreleased)', so with either
    'unreleased' or a date between parenthesis as that's the format we're
    using. Just fix up your first heading and you should be set.

    As an alternative, we support an alternative format used by some
    zope/plone paster templates: '2.10 - unreleased'

    """
    pattern = re.compile(r"""
    (?P<version>.+)  # Version string
    \(               # Opening (
    (?P<date>.+)     # Date
    \)               # Closing )
    \W*$             # Possible whitespace at end of line.
    """, re.VERBOSE)
    alt_pattern = re.compile(r"""
    ^                # Start of line
    (?P<version>.+)  # Version string
    \ -\             # space dash space
    (?P<date>.+)     # Date
    \W*$             # Possible whitespace at end of line.
    """, re.VERBOSE)
    headings = []
    line_number = 0
    for line in history_lines:
        match = pattern.search(line)
        alt_match = alt_pattern.search(line)
        if match:
            result = {'line': line_number,
                      'version': match.group('version').strip(),
                      'date': match.group('date'.strip())}
            headings.append(result)
            logger.debug("Found heading: %r", result)
        if alt_match:
            result = {'line': line_number,
                      'version': alt_match.group('version').strip(),
                      'date': alt_match.group('date'.strip())}
            headings.append(result)
            logger.debug("Found alternative heading: %r", result)
        line_number += 1
    return headings


def package_in_pypi(package):
    """Check whether the package is registered on pypi"""
    url = 'http://pypi.python.org/simple/%s' % package
    result = urllib.urlopen(url).read().strip()
    if package in result:
        # Some link with the package name is present. If the package doesn't
        # exist on pypi, the result would be 'Not Found'.
        return True
    else:
        logger.debug("Package not found on pypi: %r", result)
        return False
