"""The shared colour picker (Buddy.pickColor in app/web/buddy.js) opens where
it can be seen: Settings' Custom colours (accent, background, panels) once
opened it below the bottom of the window - it was handed the button, not
the button's box - so pressing them seemed to do nothing. Offscreen,
against a stand-in shell with in-memory settings - never the real ones."""

import json
import os
import unittest

import _paths  # noqa: F401

try:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QCoreApplication, QEvent, QEventLoop, Qt, QTimer
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    from PySide6.QtWidgets import QApplication, QWidget
    import PySide6.QtWebEngineWidgets  # noqa: F401
    from core.settings_dialog import SettingsDialog
    from core.theme import get_theme_tokens
    HAVE_WEB = True
except ImportError:  # pragma: no cover
    HAVE_WEB = False


class Settings(dict):
    def save(self):
        pass


class Shell(QWidget if HAVE_WEB else object):
    def __init__(self):
        super().__init__()
        self.shared_settings = Settings(theme="Resolve", subtheme="Custom")

    def theme_tokens(self):
        return get_theme_tokens("Resolve", "Custom")


def wait(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def js(view, expression):
    out, loop = [], QEventLoop()
    view.page().runJavaScript(f"JSON.stringify({expression})", 0, lambda value: (out.append(value), loop.quit()))
    QTimer.singleShot(5000, loop.quit)
    loop.exec()
    return json.loads(out[0]) if out and out[0] else None


PICKER_BOX = """(() => { const p = document.getElementById('picker');
  if (!p || p.hidden) return null; const r = p.getBoundingClientRect();
  return {l: r.left, t: r.top, r: r.right, b: r.bottom, w: innerWidth, h: innerHeight}; })()"""


@unittest.skipUnless(HAVE_WEB, "PySide6 with QtWebEngine not installed")
class SettingsColourTests(unittest.TestCase):
    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.shell = Shell()
        self.shell.show()
        self.dialog = SettingsDialog(self.shell, self.shell.shared_settings, lambda: None)
        self.addCleanup(self._close)
        self.dialog.resize(560, 720)
        self.dialog.show()
        for _ in range(100):
            wait(50)
            if self.dialog._ready:
                break
        wait(200)

    def _close(self):
        self.dialog.hide()
        self.dialog.deleteLater()
        self.shell.deleteLater()
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)

    def test_each_custom_colour_opens_the_picker_on_screen_and_saves(self):
        keys = js(self.dialog.view, "[...document.querySelectorAll('.set-color')].map(b => b.dataset.key)")
        self.assertEqual(keys, ["accent_color", "background_color", "panel_color"])
        for size in ((560, 720), (480, 460)):
            self.dialog.resize(*size)
            wait(150)
            for key in keys:
                js(self.dialog.view, f"(() => {{ const b = document.querySelector('.set-color[data-key={key}]');"
                                     f" b.scrollIntoView({{block: 'center'}}); b.click(); return 1; }})()")
                wait(100)
                box = js(self.dialog.view, PICKER_BOX)
                self.assertIsNotNone(box, f"{key}: no picker opened")
                self.assertTrue(box["l"] >= 0 and box["t"] >= 0 and box["r"] <= box["w"] and box["b"] <= box["h"],
                                f"{key} at {size}: the picker is off screen: {box}")
                js(self.dialog.view, "Buddy.closePicker() || 1")
        # Picking a colour and pressing OK saves it.
        js(self.dialog.view, "(() => { document.querySelector('.set-color[data-key=accent_color]').click();"
                             " const f = document.querySelector('#picker .pk-hex'); f.value = '#12AB34';"
                             " f.dispatchEvent(new Event('input')); return 1; })()")
        wait(50)
        js(self.dialog.view, "(() => { document.querySelector('#picker .pk-ok').click(); return 1; })()")
        wait(300)
        self.assertEqual(self.shell.shared_settings.get("accent_Resolve"), "#12AB34")

    def test_the_picker_takes_an_element_or_nothing(self):
        for at in ("document.querySelector('.set-color')", "undefined"):
            js(self.dialog.view, f"Buddy.pickColor({{hex: '#336699', at: {at}}}) || 1")
            wait(50)
            box = js(self.dialog.view, PICKER_BOX)
            self.assertIsNotNone(box)
            self.assertTrue(box["l"] >= 0 and box["t"] >= 0 and box["r"] <= box["w"] and box["b"] <= box["h"],
                            f"at {at}: the picker is off screen: {box}")
            js(self.dialog.view, "Buddy.closePicker() || 1")


if __name__ == "__main__":
    unittest.main()
