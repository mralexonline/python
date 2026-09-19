# JARVIS-MARK5 — install notes

Installed and verified on Ubuntu 24.04 / Python 3.11.15.
Verify any time with `./venv/bin/python verify_install.py`; launch with `./run.sh`.

## Read this first

The repository's own README opens with:

> use this instead https://github.com/TonyStark1109/JARVIS-MARK-5

The author has deprecated this repo. That replacement is **not publicly
readable** (`git ls-remote` gets an auth challenge, i.e. private or deleted),
so this install targets the repo as given. Treat it as unmaintained.

## What works

All 13 core modules import, and `jarvis.py` starts and serves its eel UI on
`http://localhost:44444/spider.html`.

## Install steps performed

**System packages**
```
portaudio19-dev espeak-ng libespeak-ng1 python3-dev build-essential \
libgl1 libglib2.0-0 xvfb scrot xauth python3.11-tk
```
`python3.11-tk` specifically — `python3-tk` installs for the system default
(3.12) and the venv's 3.11 will not see it.

**Python packages** — `requirements-linux.txt`, plus the webscout step below.

## Defects found and fixed

These are bugs in the repository, not environment problems. All source changes
are in `jarvis-source-fixes.patch` (6 files, +29/-13).

1. **`morefunctions.py:58` — `SyntaxError: 'continue' not properly in loop.`**
   A `continue` sits inside `def logic()` with no enclosing loop; the code was
   lifted out of a `while` loop without adjusting it. The file could not be
   imported by *any* Python on any OS. Changed to `return`, which is what it
   meant: stop handling this utterance.

2. **`jarvis.py` — `json` used but never imported.** `get_api()` calls
   `json.load()`; the resulting `NameError` was swallowed by a bare
   `except Exception`, so `get_api()` returned `None` and
   `os.environ['GROQ_API'] = None` raised `TypeError` at startup. Added the import.

3. **`jarvis.py` — `os.chdir()` race in a background thread.** `run_docker()`
   ran `os.chdir("backend/AI/Perplexica")` in a thread. `os.chdir` is
   process-wide, so it moved the cwd out from under the main thread and
   `LoadMessages()` failed with `FileNotFoundError: ChatLog.json` — a file that
   existed. Replaced with `subprocess.run(..., cwd=...)`.

4. **`backend/modules/llms.py` — psycopg2/psycopg3 mismatch.** Code imported
   `psycopg2` and `from psycopg2.rows import dict_row`, but `rows` is a
   psycopg **3** module and `requirements.txt` lists `psycopg` (v3). Migrated
   the code to psycopg 3 names (`connect`/`Error` are identical).

5. **Unguarded `import winreg`** in `TOOLS/SYSTEM_SETTINGS/{system_theme,taskbar}.py`.
   These drive the Windows registry and are Windows-only by nature, but the
   top-level import killed the entire `IMPORTS` chain on Linux/macOS —
   including everything platform-independent. Added
   `_winreg_compat.py`: real `winreg` on Windows (behaviour unchanged), and
   elsewhere a stand-in that imports cleanly and raises a clear error only if a
   registry call is actually attempted.

6. **Hugging Face Spaces opened at import time.** `llms.py` and
   `dealers/dealing.py` constructed `gradio_client.Client(...)` at module
   scope. Two of the three third-party Spaces are currently down:

   | Space | State |
   |---|---|
   | `osanseviero/mistral-super-fast` | **RUNTIME_ERROR** |
   | `KingNish/OpenGPT-4o` | **PAUSED** |
   | `stabilityai/stable-diffusion-3-medium` | alive |

   A dead Space therefore took down the whole application at import. Added
   `backend/modules/_lazy_client.py`, which connects on first use instead.
   **These Spaces belong to other people — no install can revive them.** The
   features that depend on them will fail when used, by design, with the real
   error.

## Dependency manifest defects

- **`pptx`** — no such project on PyPI. The code does `from pptx import
  Presentation`, which comes from **`python-pptx`**.
- **`pywin32`** — Windows-only, no Linux wheel. Nothing in this repo imports
  it; dropped.
- **`webscout==2.9`** — depends on `Helpingai-T2`, **deleted from PyPI**. Every
  webscout version that still exposes the API this repo calls
  (`webscout.PhindSearch`, `OPENGPT`, `KOBOLDAI`, …) has the same dead
  dependency; from 4.9 on, the dependency is gone but so is the API. Resolved
  by installing the pinned version without deps and shimming the missing module:

  ```bash
  ./venv/bin/pip install --no-deps webscout==2.9
  ```
  plus `venv/lib/python3.11/site-packages/Helpingai_T2.py` (a shim). This is
  safe: `Perplexity` is imported in 15 webscout files and **used in exactly
  one**, a provider this repo never calls. The shim raises if that one provider
  is ever used rather than faking results.
- **`numpy`** unpinned — 2.x breaks the pinned opencv/easyocr stack
  (`numpy.core.multiarray failed to import`). Pinned `numpy<2`.
- **opencv** — easyocr pulls `opencv-python-headless` 5.x, which requires
  numpy>=2 and fights the pin, while also installing a second competing `cv2`.
  Aligned both to `4.9.0.80`.
- **`prompt_toolkit`** — `GoogleBard1` (via webscout) drags in 1.x, which does
  `from collections import Mapping`, removed in Python 3.10. Upgraded to 3.x.
  (`pyinquirer` then reports a conflict; nothing here uses it.)

## Configuration still required

`.env` and `config/config.json` are created but **empty of credentials**:

- `config/config.json` → `GROQ_API` (and `OCR_LINK`)
- `.env` → `SERPER_API_KEY`; `InputLanguage`/`NickName`/`AssistantName` are
  pre-filled but `jarvis.py` raises `KeyError` if they are removed.
- PostgreSQL (`memory_agent` db) for conversation history — not installed here.

## What cannot run in a headless container

Not defects — missing hardware:

- **Microphone / speakers** — no `/dev/snd`, so wake-word, STT and TTS cannot
  run end to end.
- **Webcam** — vision features log `Could not open webcam`.
- **Docker** — no daemon, so the Perplexica search module does not come up.
  It is started in a background thread and does not block the rest of the app.
- **Display** — `pyautogui` needs `$DISPLAY`; `run.sh` supplies Xvfb
  automatically. Desktop automation has nothing real to drive.
