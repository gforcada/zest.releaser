import logging
import os
import sys
import zest.releaser.hg
import zest.releaser.svn
import zest.releaser.utils

logger = logging.getLogger('zest.releaser')

def version_control():
    """Return an object that provides the version control interface based
    on the detected version control system."""
    for dirpath, dirnames, filenames in os.walk('.'):
        if '.svn' in dirnames:
            return zest.releaser.svn.Subversion()
        elif '.hg' in dirnames:
            return zest.releaser.hg.Hg()
    else:
        logger.critical('No version control system detected.')
        sys.exit(1)