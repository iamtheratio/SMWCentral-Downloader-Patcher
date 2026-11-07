"""
FXPAK Pro service layer (no UI code)

Runs QUSB2SNES operations on one dedicated background event loop so a single
websocket connection can be reused across several UI actions (browse, send, play).

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import asyncio
import threading
from concurrent.futures import Future
from typing import Callable, Optional

from qusb2snes_sync import QUSB2SNESSync

DEFAULT_REMOTE_FOLDER = "/ROMS"

HELP_TEXT = (
    "QUsb2Snes must be running for the FXPAK features. The console's USB port can "
    "only be used by one program at a time, so close other programs that use it."
)

ERROR_HINT = (
    "Check that QUsb2Snes is running, the FXPAK Pro is connected and switched on, "
    "and no other program is using its USB port."
)


def fxpak_settings(config) -> dict:
    """Read the FXPAK/QUSB2SNES settings from a config object."""
    return {
        "enabled": bool(config.get("qusb2snes_enabled", False)),
        "host": config.get("qusb2snes_host", "localhost") or "localhost",
        "port": int(config.get("qusb2snes_port", 23074) or 23074),
        "device": config.get("qusb2snes_device", "") or "",
        "play_target": config.get("qusb2snes_play_target", "emulator") or "emulator",
        "remote_folder": config.get("qusb2snes_remote_folder", DEFAULT_REMOTE_FOLDER) or DEFAULT_REMOTE_FOLDER,
    }


async def open_client(settings: dict, on_progress=None, on_error=None) -> Optional[QUSB2SNESSync]:
    """Connect to QUSB2SNES and attach the configured (or first) device."""
    client = QUSB2SNESSync(settings["host"], settings["port"])
    client.on_progress = on_progress
    client.on_error = on_error
    # Interactive use: the conservative sync delays make send/play needlessly slow.
    client.fast = True
    client.list_delay = 0.05
    client.attach_wait = 0.3
    client.mkdir_delay = 0.3
    if not await client.connect():
        return None
    device = settings.get("device")
    if not device:
        devices = await client.get_devices()
        if not devices:
            client.log_error("❌ No device found. Is the FXPAK connected and QUsb2Snes running?")
            await client.disconnect()
            return None
        device = devices[0]
    if not await client.attach_device(device):
        await client.disconnect()
        return None
    return client


class FxpakWorker:
    """A background thread running an asyncio loop plus one shared client."""

    def __init__(self, settings: dict, on_progress=None, on_error=None):
        self.settings = settings
        self.on_progress = on_progress
        self.on_error = on_error
        self.client: Optional[QUSB2SNESSync] = None
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro_factory: Callable, callback: Optional[Callable] = None) -> Future:
        """Run coro_factory(client) on the worker loop (connecting first if needed).

        callback(result, error) is invoked on the worker thread when finished; the
        UI must marshal it to the main thread (e.g. widget.after(0, ...)).
        """
        async def runner():
            if self.client is None:
                self.client = await open_client(self.settings, self.on_progress, self.on_error)
                if self.client is None:
                    raise ConnectionError("Could not connect to the FXPAK via QUsb2Snes")
            self.client.cancelled = False
            return await coro_factory(self.client)

        future = asyncio.run_coroutine_threadsafe(runner(), self._loop)
        if callback:
            def done(f):
                try:
                    result = f.result()
                except BaseException as e:  # noqa: BLE001 - surfaced to the UI
                    callback(None, e)
                else:
                    callback(result, None)
            future.add_done_callback(done)
        return future

    def cancel(self):
        if self.client:
            self.client.cancel_operation()

    def close(self):
        async def shutdown():
            if self.client:
                try:
                    await self.client.disconnect()
                except Exception:
                    pass
                self.client = None
        try:
            asyncio.run_coroutine_threadsafe(shutdown(), self._loop).result(timeout=5)
        except Exception:
            pass
        self._loop.call_soon_threadsafe(self._loop.stop)
