# Buddy

A set of DaVinci Resolve tools in one app, plus a chat assistant that answers
questions about Resolve from the official reference manual and can read -
and, if you let it, change - your open project.

Buddy lives in Resolve's **Workspace > Scripts** menu as a single entry. It's
a PySide6 app whose screens are web pages (HTML/CSS/JS in QtWebEngine) driven
from Python.

## Tools

- **Ask Buddy** - chat about Resolve, grounded in the Reference Manual, with
  citations. Can read your project; can change it only with your consent.
- **Project Setup** - a bin structure from a list, folder-tree import,
  bins to timelines, and multicam sync.
- **Asset Manager** - a library of the images, audio and video you reuse,
  with per-project lists.
- **Image Importer** - images into a bin straight from the clipboard: a
  copied image, copied files, or an image URL.
- **SVG Importer** - SVG artwork and Lottie animations as Fusion nodes,
  copied for pasting into the Fusion page.
- **Media Relink** - relinks offline clips, and relocates media that's still
  online.
- **Batch Clip Renamer** - renames a bin's clips, or just the selected ones,
  by sequential numbering or find & replace.
- **Animation** - formerly Text Animator; its Text+ tab is empty for now, as
  the Text+ tools moved to Transcribe.
- **Transcribe** - subtitles from the timeline's dialogue, and translations,
  run locally; then subtitles to Text+, and Text+ font styling, layout and
  animation.
- **Audio Assistant** - new: an easier alternative to the Fairlight page for a
  clip's audio. Only the page is there so far; its tools are coming.
- **Color Palette Manager** - palettes, generators, colours from images and
  contrast checks. Never touches your project.
- **Stills Exporter** - places markers, grabs stills from them on the Color
  page, and exports them as image files.
- **YouTube Chapters** - a YouTube chapter list from the timeline's markers.
- **Time Tracker** - tracks time against whichever project is open, with idle
  detection.
- **Buddy Network** - an anonymous chat between Buddy users.

The sidebar can be reordered and tools hidden from Settings.

## Requirements

- macOS and DaVinci Resolve. The free Resolve runs scripts up to version
  21.0.x; from 21.1, scripting needs DaVinci Resolve Studio.
- Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
  (Resolve runs scripts with it), with the packages in
  `installer/requirements.txt`: PySide6 (including QtWebEngine and
  QtMultimedia), Pillow, NumPy, openpyxl, pynput, PyMuPDF and cryptography.

## Installing

**With the installer.** Download `Buddy-<version>.pkg` from the
[Releases](https://github.com/shibiscripts001/Buddy---Mac/releases) page (built
by `.github/workflows/release.yml` whenever `VERSION` changes), or build it with
`python3 build_mac_installer.py`, which writes `dist/Buddy-<version>.pkg`, then
open the .pkg. It installs Python from
python.org if the Mac has no suitable one (checksum-verified), adds Buddy's
packages, and puts Buddy in Resolve's Scripts menu. The .pkg is unsigned, so
macOS may ask you to allow it in System Settings > Privacy & Security. The
install log is `/Library/Logs/Buddy-install.log`.

**By hand.** With python.org's Python installed, double-click
`Deploy to Resolve.command`, or run:

```bash
python3 -m pip install -r installer/requirements.txt
python3 build_buddy_zip.py --deploy
```

That builds `buddy.zip` and copies it, with the `Buddy.py` launcher, into
`~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility`.
Quit and reopen Resolve, then choose **Workspace > Scripts > Buddy**. Run it
again after changing the code - Resolve loads the zip, not the source tree.

Buddy also runs on Windows: `python build_installer.py` builds a Windows
installer (Inno Setup), and `docs/manual_install.txt` covers installing there
by hand.

## Running from source

```bash
python3 app/main.py
```

The tools that talk to Resolve need Buddy launched from Resolve's Scripts
menu: the free Resolve only accepts the connection it hands to a script it
started.

## Background behaviour

Closing the window keeps Buddy running in the menu bar, so Time Tracker keeps
tracking (turn this off in Settings). Launching Buddy again brings the
running one to the front instead of starting a second. On Windows, Buddy can
also start itself when Resolve starts.

## Ask Buddy

Bring your own model: Google Gemini, Anthropic Claude, OpenAI, OpenRouter,
Groq, Azure OpenAI, any OpenAI-compatible endpoint, or Ollama running locally.
Keys are set in Settings and stored in your home folder.

**Manual data.** Answers are grounded in a bundle built from the DaVinci
Resolve Reference Manual PDF, kept in `~/.buddy/manual/bundle/`. Buddy runs
without it, but answers are then ungrounded and uncited. To build it,
download the manual PDF and use **Settings > Ask Buddy > Rebuild from PDF...**,
or run:

```bash
python3 build_manual_bundle.py DavinciManual.pdf
```

The builder needs `pymupdf` and `pymupdf4llm`, and Ollama with
`embeddinggemma` for semantic search (without Ollama it builds a keyword-only
bundle).

**Changing your project** is off by default and behind two gates: consent in
Settings (you type a sentence out in full; unticking revokes it), and
approval of every action - the model only proposes, Buddy shows exactly what
would change, and nothing happens until you press Apply.

## Transcribe

Turns the timeline's dialogue into subtitles locally: it renders the audio
mix, runs Whisper (faster-whisper) or NVIDIA Parakeet, builds readable
subtitles from the word timings, and puts them on subtitle track 1 as well as
saving an SRT. Translation runs locally too (NLLB-200 or MADLAD-400), or
through the model Ask Buddy uses. The engine and models are installed from
inside Transcribe the first time, into `~/.buddy/transcribe/`. Resolve's
render settings are saved before the audio render and restored after. Its
Subtitle Conversion tab turns subtitles into Text+ clips, and the tabs after
it style, place and animate them.

## Buddy Network

A text chat between Buddy users: public rooms, your own rooms, direct
messages (end-to-end encrypted) and a buddies list. Anonymous by design: no
accounts, emails or IP addresses. Buddy connects to the public server by
default; `server/README.md` covers running your own.

## Themes

Seven themes, each with its own subthemes and a Custom palette: Default (the
look of DaVinci Resolve itself), Don't be evil, Retro, Modern, Nova, Off-world
and Desktop (tools in floating windows). Open Sans ships in
`app/assets/fonts/` under the SIL Open Font License.

## Layout

```
app/
  main.py            entry point
  core/              shell window, theming, settings, Resolve bridge, web page host
  web/               shared web runtime (buddy.js, buddy.css) and the shell's pages
  pages/             one package per tool: Python logic plus its web/ view
  registry.py        which tools exist
Buddy.py             launcher for Resolve's Scripts menu
build_buddy_zip.py   builds buddy.zip, and deploys it with --deploy
build_mac_installer.py / build_installer.py   the macOS / Windows installers
build_manual_bundle.py   builds Ask Buddy's manual bundle from the PDF
server/              the Buddy Network server
tests/               automated tests
```

## Tests

```bash
python3 -m unittest discover tests
```

Most tests are plain Python. The ones that render pages need PySide6 with
QtWebEngine and skip without it. `tests/test_layout_overlaps.py` opens every
tool, tab and window at a range of sizes in every theme and fails if any UI
overlaps other UI - it takes a few minutes.
