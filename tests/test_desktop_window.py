"""The desktop layout's desk (app/core/desktop_window.py): clicking inside a
window's page brings that window to the front, and the windows move with
the desk when the link bar goes in above it. Built offscreen with stand-in
pages - no web views, no settings, no Resolve."""

import os
import unittest

import _paths  # noqa: F401

try:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QPoint
    from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget
    from core.desktop_window import DesktopArea
    HAVE_QT = True
except ImportError:  # pragma: no cover
    HAVE_QT = False


def _page():
    page = QWidget()
    page.field = QLineEdit(page)
    page.on_shown = lambda: None
    QVBoxLayout(page).addWidget(page.field)
    return page


@unittest.skipUnless(HAVE_QT, "PySide6 not installed")
class FrontOnFocusTests(unittest.TestCase):
    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.shell = QWidget()
        self.addCleanup(self.shell.deleteLater)
        self.shell.resize(1400, 900)
        self.pages = {"alpha": _page(), "beta": _page()}
        self.desk = DesktopArea(self.shell, self.pages, {"alpha": "Alpha", "beta": "Beta"},
                                lambda page: None, lambda front: None)
        self.desk.setGeometry(0, 0, 1400, 900)
        self.shell.show()
        self.desk.show_desk()
        self.desk.open("alpha")
        self.desk.open("beta")
        self.shell.activateWindow()
        self.app.processEvents()

    def test_focus_inside_a_window_behind_brings_it_forward(self):
        self.assertEqual(self.desk.front(), "beta")
        self.pages["alpha"].field.setFocus()
        self.app.processEvents()
        self.assertEqual(self.desk.front(), "alpha")

    def test_focus_in_the_front_window_changes_nothing(self):
        self.pages["beta"].field.setFocus()
        self.app.processEvents()
        self.assertEqual(self.desk.front(), "beta")

    def test_a_hidden_desk_ignores_focus(self):
        self.desk.hide()
        self.pages["alpha"].field.setFocus()
        self.app.processEvents()
        self.assertEqual(self.desk.front(), "beta")


@unittest.skipUnless(HAVE_QT, "PySide6 not installed")
class DeskUnderTheLinkBar(unittest.TestCase):
    """The windows are native, the desk isn't: when the link bar goes in
    above the desk, the desk only moves - and the windows have to move with
    it, not stay over the bar."""

    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.top = QWidget()
        self.addCleanup(self.top.deleteLater)
        self.top.resize(1000, 700)
        self.root = QVBoxLayout(self.top)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)
        self.desk = DesktopArea(self.top, {"tool": _page()}, {"tool": "Tool"}, lambda page: None, lambda front: None)
        self.root.addWidget(self.desk, 1)
        self.bar = QLabel("links")
        self.bar.setFixedHeight(40)
        self.root.addWidget(self.bar)                       # along the bottom, as under the other themes
        self.top.show()
        self.desk.show()
        self.app.processEvents()
        self.desk.open("tool")
        self.app.processEvents()

    def tearDown(self):
        self.top.close()
        self.app.processEvents()

    def native_y(self):
        win = self.desk.windows["tool"]
        return win.windowHandle().position().y(), win.mapTo(self.top, QPoint(0, 0)).y()

    def test_the_windows_move_down_with_the_desk(self):
        actual, expected = self.native_y()
        self.assertEqual(actual, expected)
        # The desktop layout puts the bar along the top: the desk moves down,
        # its size the same.
        self.root.removeWidget(self.bar)
        self.root.insertWidget(0, self.bar)
        self.app.processEvents()
        self.assertEqual(self.desk.y(), 40)
        actual, expected = self.native_y()
        self.assertEqual(actual, expected)
        self.assertGreaterEqual(actual, 40)                 # below the bar, never over it


if __name__ == "__main__":
    unittest.main()
