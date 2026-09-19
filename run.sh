#!/usr/bin/env bash
# Launch JARVIS-MARK5. On a headless machine this wraps the app in a virtual
# display, because jarvis.py imports pyautogui (which needs $DISPLAY) and eel
# opens a Chromium window.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

[ -f ChatLog.json ] || echo '[]' > ChatLog.json   # LoadMessages() requires it

if [ -n "${DISPLAY:-}" ]; then
    exec ./venv/bin/python jarvis.py "$@"
elif command -v xvfb-run >/dev/null 2>&1; then
    echo "No \$DISPLAY; starting under Xvfb. UI will be at http://localhost:44444/spider.html"
    exec xvfb-run -a --server-args="-screen 0 1280x1024x24" ./venv/bin/python jarvis.py "$@"
else
    echo "No display and no xvfb-run. Install it with: sudo apt-get install -y xvfb" >&2
    exit 1
fi
