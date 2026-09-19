"""Platform guard for the Windows-only `winreg` stdlib module.

`system_theme.py` and `taskbar.py` drive Windows-specific settings (the
Personalize theme key and taskbar alignment) through the Windows Registry, so
they are Windows-only by nature. They imported `winreg` unconditionally at
module scope, which made `import IMPORTS` -- and therefore the whole of
JARVIS -- fail on Linux and macOS, including the many parts that are not
platform-specific at all.

This module returns the real `winreg` on Windows, so behaviour there is
unchanged. Elsewhere it returns a stand-in that imports cleanly but raises a
clear error the moment a registry operation is actually attempted, so the
Windows-only features fail loudly instead of silently doing nothing.
"""

_MESSAGE = (
    "This feature uses the Windows Registry (winreg) and is only available on "
    "Windows. Windows theme switching and taskbar customisation have no "
    "equivalent on this platform."
)


class _UnavailableWinreg:
    """Stand-in for `winreg` on non-Windows platforms."""

    # Defined so that `except winreg.error:` remains valid at import time.
    error = OSError

    def __getattr__(self, name):
        raise RuntimeError(f"{_MESSAGE} (tried to access winreg.{name})")


try:  # pragma: no cover - platform dependent
    import winreg
except ImportError:  # non-Windows
    winreg = _UnavailableWinreg()
