"""Defer Hugging Face Space connections from import time to first use.

`llms.py` and `dealers/dealing.py` constructed `gradio_client.Client(...)` at
module scope, which opens a live network connection to a third-party Hugging
Face Space the moment the module is imported. Those Spaces are owned by other
people and several are currently down (RUNTIME_ERROR / PAUSED), so importing
any of them raised and took the entire application down with it -- including
every feature that does not touch those Spaces.

`LazyGradioClient` keeps the exact same call surface but builds the real
client on first attribute access. Code that never uses a given Space no
longer pays for it, and a dead Space now fails only where it is actually
used, with the original error preserved.
"""


class LazyGradioClient:
    def __init__(self, space, *args, **kwargs):
        self._space = space
        self._args = args
        self._kwargs = kwargs
        self._client = None

    def _resolve(self):
        if self._client is None:
            from gradio_client import Client
            self._client = Client(self._space, *self._args, **self._kwargs)
        return self._client

    def __getattr__(self, name):
        # Only called for attributes not found normally, so the private
        # attributes set in __init__ never route through here.
        return getattr(self._resolve(), name)

    def __repr__(self):
        state = "connected" if self._client is not None else "not yet connected"
        return f"<LazyGradioClient {self._space!r} ({state})>"
