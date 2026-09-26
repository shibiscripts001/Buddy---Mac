"""Put app/ (and the transcribe worker's folder) on sys.path for the tests.

The modules tested here are the pure ones - no Qt, no Resolve, no models -
so the suite runs with plain Python on any machine:

    python -m unittest discover tests
"""

import os
import sys
from pathlib import Path

# Web pages in tests draw offscreen, where there's no real graphics
# context: Chromium's GPU compositor keeps losing it and, now and then,
# crashes the test process outright (on macOS, a "Python quit unexpectedly"
# dialog). Drawing in software instead changes no layout. Set before
# QtWebEngine starts - every test imports this module first.
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

APP = Path(__file__).resolve().parents[1] / "app"
TRANSCRIBE = APP / "pages" / "transcribe"
for p in (str(APP), str(TRANSCRIBE), str(APP.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)
