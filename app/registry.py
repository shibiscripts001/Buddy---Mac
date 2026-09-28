#!/usr/bin/env python3
"""
The full list of Buddy's tools, grouped and ordered the way they appear
in the nav rail.

A tool that isn't available yet is a placeholder (see
pages/placeholder.py), so the complete layout is still visible. Which ones
are real is never written down here - ToolPage.is_placeholder is the one
source of truth.

Adding a tool = writing its own pages/<tool_id>/page.py (a ToolPage
subclass, see pages/base.py) and swapping its placeholder() call below
for the real import - the category/order here don't need to change.

macOS note: a few tools call Windows-only APIs (winreg, ctypes.windll,
Windows font enumeration, etc.) from some of their features. So on macOS a
tool only loads for real once it's been checked there - its mac=True
below. The rest stay placeholders until then. Enabling one = fixing
whatever it does that's Windows-only, then flipping it to mac=True.
"""

import sys

from pages.placeholder import make_placeholder_page
from pages.buddy_network.page import BuddyNetworkPage

IS_MAC = sys.platform == "darwin"


def _tool(tool_id, display_name, category, import_path, class_name, mac=False):
    """The real page class - except on macOS for a tool not yet checked
    there (mac=False), which gets a placeholder and isn't imported at all.
    See the module docstring above."""
    if IS_MAC and not mac:
        return make_placeholder_page(tool_id, display_name, category)
    import importlib

    module = importlib.import_module(import_path)
    return getattr(module, class_name)


# List of (category, page_cls), in nav order. NOTE: tests/test_network_client.py
# reads this file's source with ast rather than importing it (importing pulls
# in every real page), and asserts REGISTRY is a plain list literal ending in
# a bare ("", BuddyNetworkPage) tuple - keep this a literal list, not built up
# with comprehensions/concatenation, and keep that last entry as-is.
REGISTRY = [
    ("Ask", _tool("manual_chat", "Ask Buddy", "Ask", "pages.manual_chat.page", "ManualChatPage", mac=True)),

    ("Setup", _tool("project_setup", "Project Setup", "Setup", "pages.project_setup.page", "ProjectSetupPage", mac=True)),

    ("Media & Assets", _tool("asset_manager", "Asset Manager", "Media & Assets", "pages.asset_manager.page", "AssetManagerPage", mac=True)),
    ("Media & Assets", _tool("image_importer", "Image Importer", "Media & Assets", "pages.image_importer.page", "ImageImporterPage", mac=True)),
    ("Media & Assets", _tool("svg_importer", "SVG Importer", "Media & Assets", "pages.svg_importer.page", "SVGImporterPage", mac=True)),
    ("Media & Assets", _tool("media_relink", "Media Relink", "Media & Assets", "pages.media_relink.page", "MediaRelinkPage", mac=True)),

    ("Editing Tools", _tool("batch_clip_renamer", "Batch Clip Renamer", "Editing Tools", "pages.batch_clip_renamer.page", "BatchClipRenamerPage", mac=True)),
    ("Editing Tools", _tool("text_animator", "Animation", "Editing Tools", "pages.text_animator.page", "AnimationPage", mac=True)),
    ("Editing Tools", _tool("transcribe", "Transcribe", "Editing Tools", "pages.transcribe.page", "TranscribePage", mac=True)),
    ("Editing Tools", _tool("color_palette", "Color Palette Manager", "Editing Tools", "pages.color_palette.page", "ColorPalettePage", mac=True)),

    ("Export & Delivery", _tool("stills_exporter", "Stills Exporter", "Export & Delivery", "pages.stills_exporter.page", "StillsExporterPage", mac=True)),
    ("Export & Delivery", _tool("youtube_chapters", "YouTube Chapters", "Export & Delivery", "pages.youtube_chapters.page", "YouTubeChaptersPage", mac=True)),

    ("Business", _tool("time_tracker", "Time Tracker", "Business", "pages.time_tracker.page", "TimeTrackerPage", mac=True)),

    # "" = a plain line above it instead of a heading.
    ("", BuddyNetworkPage),
]
