"""A closed web window is freed on the GUI thread, straight away - never left
for Python's cycle collector, which runs on whichever thread triggers it
(Ask Buddy's agent, a Resolve poll). Chromium aborts when a web view is
destroyed off the GUI thread: Buddy crashed every hour or two with no error.
core/web_page.py's _Bridge holds its window weakly (no cycle),
open_settings() deletes its dialog, and core/gui_gc.py only collects from a
GUI-thread timer. Offscreen, against a stand-in shell - never the real
settings."""

import gc
import os
import unittest
import weakref

import _paths  # noqa: F401

try:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QCoreApplication, QEvent, Qt, QTimer
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    from PySide6.QtWidgets import QApplication, QDialog, QWidget
    import PySide6.QtWebEngineWidgets  # noqa: F401
    from core import gui_gc
    from core.message_dialog import MessageDialog, alert
    from core.settings_dialog import SettingsDialog
    from core.shell_window import ShellWindow
    from core.theme import get_theme_tokens
    HAVE_WEB = True
except ImportError:  # pragma: no cover
    HAVE_WEB = False

# Where a leaked web window's objects come from.
WEB_MODULES = ("PySide6.QtWebEngine", "PySide6.QtWebChannel", "core.web_page", "core.message_dialog",
               "core.settings_dialog")


class Settings(dict):
    def save(self):
        pass


class Shell(QWidget if HAVE_WEB else object):
    """What a web window asks of the shell, and what open_settings() uses."""

    def __init__(self):
        super().__init__()
        self.shared_settings = Settings(theme="Resolve")
        self.pages, self._layout, self._current_tool_id = {}, "rail", None
        self.stack = self

    def theme_tokens(self):
        return get_theme_tokens("Resolve")

    def front(self):            # the pane stack's page in front: none here
        return None

    def _on_settings_applied(self):
        pass


def web_garbage():
    """Web-window objects Python's cycle collector found unreachable."""
    return [type(o).__name__ for o in gc.garbage
            if (type(o).__module__ or "").startswith(WEB_MODULES)]


def close_when_shown(shell, kind):
    """Closes the first `kind` dialog of `shell`'s once it's open (exec()
    blocks until then)."""
    timer = QTimer(shell)

    def check():
        for dialog in shell.findChildren(kind):
            if dialog.isVisible():
                timer.stop()
                dialog.done(QDialog.Rejected)

    timer.timeout.connect(check)
    timer.start(50)
    QTimer.singleShot(10000, timer.stop)


@unittest.skipUnless(HAVE_WEB, "PySide6 with QtWebEngine not installed")
class WebLifetimeTests(unittest.TestCase):
    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.shell = Shell()
        self.shell.resize(800, 600)
        self.shell.show()
        self.addCleanup(self._drop_shell)

    def _drop_shell(self):
        if self.shell is not None:
            self.shell.deleteLater()
            QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            self.shell = None

    def test_a_closed_message_leaves_no_web_view_for_the_collector(self):
        # Whatever earlier tests left behind isn't this test's garbage.
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        gc.collect()
        gc.set_debug(gc.DEBUG_SAVEALL)
        try:
            for text in ("One", "Two"):
                close_when_shown(self.shell, MessageDialog)
                alert(self.shell, "Test", text)
            QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            self.assertEqual(self.shell.findChildren(MessageDialog), [], "a closed message stayed alive")
            # Its window going is what used to turn it into cycle garbage.
            self._drop_shell()
            gc.collect()
            leaked = web_garbage()
        finally:
            gc.set_debug(0)
            gc.garbage.clear()
        self.assertEqual(leaked, [], "a closed window's web view was left for the cycle collector")

    def test_a_dropped_window_is_freed_without_the_collector(self):
        """The window and its bridge make no reference cycle: once Qt
        deletes it and the last reference goes, it's gone - no collection."""
        was = gc.isenabled()
        gc.disable()
        try:
            dialog = MessageDialog(self.shell, None, "Test", "Dropped")
            gone = weakref.ref(dialog)
            dialog.deleteLater()
            QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            del dialog
            self.assertIsNone(gone(), "the window was left for the cycle collector")
        finally:
            if was:
                gc.enable()

    def test_open_settings_leaves_no_dialog_behind(self):
        for _ in range(2):
            close_when_shown(self.shell, SettingsDialog)
            ShellWindow.open_settings(self.shell)
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.assertEqual(self.shell.findChildren(SettingsDialog), [])


@unittest.skipUnless(HAVE_WEB, "PySide6 with QtWebEngine not installed")
class GuiCollectorTests(unittest.TestCase):
    def test_install_turns_automatic_collection_off(self):
        app = QApplication.instance() or QApplication([])
        was = gc.isenabled()
        try:
            timer = gui_gc.install(app)
            self.assertFalse(gc.isenabled())
            self.assertTrue(timer.isActive())
            self.assertIs(timer.thread(), app.thread())
            self.assertIs(gui_gc.install(app), timer)   # once only
        finally:
            if gui_gc._timer is not None:
                gui_gc._timer.stop()
                gui_gc._timer.deleteLater()
                gui_gc._timer = None
            if was:
                gc.enable()


if __name__ == "__main__":
    unittest.main()
