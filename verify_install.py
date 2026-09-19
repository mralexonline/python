#!/usr/bin/env python
"""Smoke-test the JARVIS-MARK5 install. Run: ./venv/bin/python verify_install.py"""
import importlib, os, sys

THIRD_PARTY = ["chromadb", "gradio_client", "groq", "eel", "cv2", "numpy", "psycopg",
               "pptx", "webscout", "easyocr", "pyttsx3", "speech_recognition", "selenium"]
REPO = ["backend.modules.extra", "backend.modules.basic.listenpy", "backend.modules.filter",
        "backend.modules.search", "backend.modules.llms", "backend.modules.Powerpointer.main",
        "backend.AI.dealers.dealing", "backend.modules.speak.speakmid", "TOOLS.RawDog",
        "TOOLS.Alpaca_DS_Converser", "IMPORTS", "morefunctions", "backend.modules.automodel"]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
fails = []

def check(group, mods):
    print(f"\n== {group} ==")
    for m in mods:
        try:
            importlib.import_module(m)
            print(f"  ok    {m}")
        except BaseException as e:
            fails.append(m)
            print(f"  FAIL  {m}: {type(e).__name__}: {str(e)[:100]}")

check("third-party packages", THIRD_PARTY)
check("repo modules", REPO)

print("\n== required files ==")
for f in ["config/config.json", ".env", "ChatLog.json"]:
    ok = os.path.exists(f)
    print(f"  {'ok   ' if ok else 'FAIL '} {f}")
    if not ok:
        fails.append(f)

print("\n" + ("ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILED: {fails}"))
sys.exit(1 if fails else 0)
