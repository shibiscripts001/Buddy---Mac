"""The desktop layout's desk (app/core/desktop_window.py): clicking inside a
window's page brings that window to the front. Built offscreen with
stand-in pages - no web views, no settings, no Resolve."""

import os
import unittest

import _paths  # noqa: F401

try:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget
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


if __name__ == "__main__":
    unittest.main()
