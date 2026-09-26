"""
Python's cycle collector, run on the GUI thread only.

Left automatic, a collection runs on whichever thread happens to allocate
past the threshold - Ask Buddy's agent, a Resolve poll, a download. If the
garbage holds a Qt web view (a window whose Python side sat in a reference
cycle), its Chromium objects are destroyed on that thread, and Chromium
aborts: Buddy vanished every hour or two with no error. So automatic
collection is turned off and a GUI-thread timer collects instead - the
young generation every couple of seconds, everything now and then.
core/web_page.py's _Bridge avoids making such cycles in the first place;
this covers any other.
"""

import gc

from PySide6.QtCore import QTimer

INTERVAL_MS = 2000
FULL_EVERY = 30   # ticks: a full collection about once a minute

_timer = None


def install(app):
    """Turns automatic collection off and collects from a timer on `app`'s
    (the GUI) thread. Call once, right after creating the QApplication."""
    global _timer
    if _timer is not None:
        return _timer
    gc.disable()
    ticks = 0

    def collect():
        nonlocal ticks
        ticks += 1
        if ticks % FULL_EVERY == 0:
            gc.collect()
        else:
            gc.collect(0)

    _timer = QTimer(app)
    _timer.setInterval(INTERVAL_MS)
    _timer.timeout.connect(collect)
    _timer.start()
    return _timer
