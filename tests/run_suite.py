"""Runs the whole suite and exits with its result the moment it's printed.

QtWebEngine can crash while it tears down at exit, after "OK" - which would
turn a passing run into a failed one. os._exit() skips that teardown.

    python tests/run_suite.py
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    suite = unittest.defaultTestLoader.discover(HERE, top_level_dir=HERE)
    result = unittest.TextTestRunner(verbosity=2 if "-v" in sys.argv else 1).run(suite)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0 if result.wasSuccessful() else 1)
