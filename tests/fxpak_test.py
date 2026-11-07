"""Unit tests for the FXPAK helpers. A fake websocket stands in for QUsb2Snes (no hardware)."""
import asyncio
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import qusb2snes_sync  # noqa: E402
from qusb2snes_sync import QUSB2SNESSync  # noqa: E402


class FakeWebSocket:
    """Minimal QUsb2Snes: keeps a folder tree, answers List, records everything."""

    closed = False

    def __init__(self, tree):
        self.tree = {k: dict(v) for k, v in tree.items()}  # path -> {name: is_dir}
        self.commands = []
        self.binary = []
        self._replies = []
        self.running = "/sd2snes/menu.bin"

    async def send(self, data):
        if isinstance(data, (bytes, bytearray)):
            self.binary.append(bytes(data))
            return
        cmd = json.loads(data)
        self.commands.append(cmd)
        op, ops = cmd["Opcode"], cmd.get("Operands", [])
        if op == "List":
            entries = self.tree.get(ops[0].rstrip("/") or "/")
            if entries is None:
                raise ConnectionError("device dropped the connection")
            results = []
            for name, is_dir in entries.items():
                results += ["0" if is_dir else "1", name]
            self._replies.append(json.dumps({"Results": results}))
        elif op == "Boot":
            self.running = ops[0]
        elif op == "Info":
            self._replies.append(json.dumps({"Results": ["1.11.0", "x", self.running + "\x00\x00"]}))
        elif op == "MakeDir":
            path = ops[0]
            parent, _, name = path.rpartition("/")
            self.tree.setdefault(parent or "/", {})[name] = True
            self.tree.setdefault(path, {})
        elif op == "PutFile":
            parent, _, name = ops[0].rpartition("/")
            self.tree.setdefault(parent or "/", {})[name] = False

    async def recv(self):
        return self._replies.pop(0)

    async def close(self, **kw):
        self.closed = True


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    async def fast(_):
        return None
    monkeypatch.setattr(qusb2snes_sync.asyncio, "sleep", fast)


def make_client(tree):
    client = QUSB2SNESSync("localhost", 23074)
    client.websocket = FakeWebSocket(tree)
    client.connected = True
    client.errors = []
    client.on_error = client.errors.append
    return client


def run(coro):
    return asyncio.run(coro)


def test_boot_sends_boot_opcode_with_normalized_path():
    client = make_client({"/": {}})
    assert run(client.boot_rom("ROMS\\Kaizo/Hack.smc")) is True
    assert client.websocket.commands[0] == {
        "Opcode": "Boot", "Space": "SNES", "Operands": ["/ROMS/Kaizo/Hack.smc"]}
    # stays connected until the console reports the new ROM
    assert client.websocket.commands[1]["Opcode"] == "Info"


def test_boot_reports_failure_when_rom_not_running():
    client = make_client({"/": {}})
    client.websocket.running = "/other.smc"
    orig = client.websocket.send

    async def send(data):
        await orig(data)
        client.websocket.running = "/other.smc"
    client.websocket.send = send
    assert run(client.boot_rom("/ROMS/Hack.smc")) is False


def test_upload_reports_byte_progress(tmp_path):
    f = tmp_path / "a.smc"
    f.write_bytes(b"x" * 100000)
    client = make_client({"/": {"ROMS": True}, "/ROMS": {}})
    seen = []
    run(client.send_files([(str(f), "a.smc")], "/ROMS", on_bytes=lambda s, t, n: seen.append((s, t, n))))
    assert seen and seen[-1] == (100000, 100000, "a.smc")
    assert [x[0] for x in seen] == sorted(x[0] for x in seen)


def test_directory_exists_lists_parent_only():
    client = make_client({"/": {"ROMS": True}, "/ROMS": {}})
    assert run(client.directory_exists("/roms")) is True
    assert run(client.directory_exists("/missing")) is False
    # never listed the missing directory itself
    listed = [c["Operands"][0] for c in client.websocket.commands if c["Opcode"] == "List"]
    assert "/missing" not in listed


def test_ensure_directory_creates_missing_parents():
    client = make_client({"/": {}})
    assert run(client.ensure_directory("/ROMS/Kaizo")) is True
    made = [c["Operands"][0] for c in client.websocket.commands if c["Opcode"] == "MakeDir"]
    assert made == ["/ROMS", "/ROMS/Kaizo"]


def test_send_files_never_overwrites_and_reports_skipped(tmp_path):
    a = tmp_path / "a.smc"
    b = tmp_path / "b.smc"
    a.write_bytes(b"A" * 2048)
    b.write_bytes(b"B" * 10)
    client = make_client({"/": {"ROMS": True}, "/ROMS": {"A.SMC": False}})
    seen = []
    result = run(client.send_files([(str(a), "a.smc"), (str(b), "b.smc")], "/ROMS",
                                   on_file=lambda i, n, name: seen.append((i, n, name))))
    assert result["skipped"] == ["a.smc"]          # case-insensitive match, not overwritten
    assert result["uploaded"] == ["b.smc"]
    puts = [c for c in client.websocket.commands if c["Opcode"] == "PutFile"]
    assert [p["Operands"][0] for p in puts] == ["/ROMS/b.smc"]
    assert b"".join(client.websocket.binary) == b"B" * 10
    assert seen == [(1, 2, "a.smc"), (2, 2, "b.smc")]
    assert result["remote_paths"]["a.smc"] == "/ROMS/a.smc"


def test_send_files_cancel_stops_between_files(tmp_path):
    f = tmp_path / "x.smc"
    f.write_bytes(b"x")
    client = make_client({"/": {"ROMS": True}, "/ROMS": {}})
    client.cancelled = True
    result = run(client.send_files([(str(f), "x.smc")], "/ROMS"))
    assert result["cancelled"] is True and result["uploaded"] == []
    assert not [c for c in client.websocket.commands if c["Opcode"] == "PutFile"]


def test_remote_file_exists():
    client = make_client({"/": {"ROMS": True}, "/ROMS": {"Hack.smc": False, "Sub": True}})
    assert run(client.remote_file_exists("/ROMS", "hack.SMC")) is True
    assert run(client.remote_file_exists("/ROMS", "Sub")) is False   # a folder is not a file
    assert run(client.remote_file_exists("/Nope", "Hack.smc")) is False


def test_safe_remote_name():
    assert QUSB2SNESSync.safe_remote_name('a:b*c?.smc') == "a_b_c_.smc"
    assert QUSB2SNESSync.safe_remote_name("  name.smc ") == "name.smc"


def test_config_keeps_qusb_keys(tmp_path, monkeypatch):
    import config_manager
    monkeypatch.setattr(config_manager, "CONFIG_PATH", str(tmp_path / "config.json"))
    cm = config_manager.ConfigManager()
    cm.set("qusb2snes_remote_folder", "/Kaizo")
    assert config_manager.ConfigManager().get("qusb2snes_remote_folder") == "/Kaizo"
