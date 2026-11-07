"""
FXPAK Pro UI components: remote folder browser, send/play actions, settings block

Uses fxpak_service.FxpakWorker (one background asyncio loop + one websocket) for
all device access; every UI update is marshalled back with widget.after(0, ...).

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from fxpak_service import (FxpakWorker, fxpak_settings, HELP_TEXT, ERROR_HINT, DEFAULT_REMOTE_FOLDER)
from qusb2snes_sync import QUSB2SNESSync
from utils import set_window_icon


def _center(dialog, parent, min_width=420):
    dialog.update_idletasks()
    top = parent.winfo_toplevel()
    dw = max(dialog.winfo_reqwidth(), min_width)
    dh = dialog.winfo_reqheight()
    x = top.winfo_x() + (top.winfo_width() - dw) // 2
    y = top.winfo_y() + (top.winfo_height() - dh) // 2
    dialog.geometry(f"{dw}x{dh}+{max(x, 0)}+{max(y, 0)}")


def _log_funcs(logger):
    def progress(msg):
        if logger:
            logger.log(msg, "Information")

    def error(msg):
        if logger:
            logger.log(msg, "Error")
    return progress, error


class _BusyDialog:
    """Small modal progress dialog with a Cancel button."""

    def __init__(self, parent, title, on_cancel, determinate=False, maximum=1):
        self.parent = parent
        self._on_cancel = on_cancel
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.resizable(False, False)
        self.top.transient(parent.winfo_toplevel())
        self.top.grab_set()
        set_window_icon(self.top)
        self.top.protocol("WM_DELETE_WINDOW", self._cancel)

        outer = ttk.Frame(self.top, padding=(24, 20, 24, 20))
        outer.pack(fill="both", expand=True)
        self.label = ttk.Label(outer, text="Connecting to the FXPAK…", width=52)
        self.label.pack(anchor="w", pady=(0, 10))
        self.bar = ttk.Progressbar(
            outer, mode="determinate" if determinate else "indeterminate",
            maximum=max(maximum, 1), length=380)
        self.bar.pack(fill="x")
        if not determinate:
            self.bar.start(12)
        self.cancel_btn = ttk.Button(outer, text="Cancel", command=self._cancel, width=12)
        self.cancel_btn.pack(anchor="e", pady=(14, 0))
        _center(self.top, parent)

    def _cancel(self):
        self.cancel_btn.configure(state="disabled", text="Cancelling…")
        self.label.configure(text="Cancelling after the current file…")
        self._on_cancel()

    def update(self, text, value=None):
        self.label.configure(text=text)
        if value is not None:
            self.bar["value"] = value

    def close(self):
        try:
            self.bar.stop()
            self.top.grab_release()
            self.top.destroy()
        except tk.TclError:
            pass


class RemoteFolderBrowser:
    """Modal dialog to pick (or create) a folder on the FXPAK's SD card."""

    def __init__(self, parent, settings, initial_path, on_select, logger=None):
        self.parent = parent
        self.on_select = on_select
        self.current = "/"
        self._busy = False
        self._closed = False
        progress, error = _log_funcs(logger)
        self.worker = FxpakWorker(settings, progress, error)

        self.top = tk.Toplevel(parent)
        self.top.title("Browse FXPAK SD Card")
        self.top.transient(parent.winfo_toplevel())
        self.top.grab_set()
        set_window_icon(self.top)
        self.top.protocol("WM_DELETE_WINDOW", self._close)

        outer = ttk.Frame(self.top, padding=(20, 16, 20, 16))
        outer.pack(fill="both", expand=True)

        self.path_var = tk.StringVar(value="/")
        ttk.Entry(outer, textvariable=self.path_var, state="readonly").pack(fill="x", pady=(0, 8))

        list_frame = ttk.Frame(outer)
        list_frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(list_frame, height=14, activestyle="dotbox", exportselection=False)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.listbox.bind("<Double-1>", lambda e: self._enter_selected())
        self.listbox.bind("<Return>", lambda e: self._enter_selected())

        self.status = ttk.Label(outer, text="Connecting…", font=("Segoe UI", 8), foreground="gray")
        self.status.pack(anchor="w", pady=(6, 0))
        ttk.Label(outer, text=HELP_TEXT, font=("Segoe UI", 8), foreground="gray",
                  wraplength=420, justify="left").pack(anchor="w", pady=(4, 0))

        row = ttk.Frame(outer)
        row.pack(fill="x", pady=(12, 0))
        self.up_btn = ttk.Button(row, text="Up", command=self._go_up, width=8)
        self.up_btn.pack(side="left")
        self.new_btn = ttk.Button(row, text="New Folder…", command=self._new_folder, width=14)
        self.new_btn.pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Cancel", command=self._close, width=10).pack(side="right")
        self.select_btn = ttk.Button(row, text="Select This Folder", style="Accent.TButton",
                                     command=self._select, width=18)
        self.select_btn.pack(side="right", padx=(0, 8))

        self.top.bind("<Escape>", lambda e: self._close())
        _center(self.top, parent, 460)

        self._navigate_initial(initial_path)

    # -- helpers -------------------------------------------------------
    def _ui(self, fn):
        if not self._closed:
            try:
                self.top.after(0, fn)
            except (tk.TclError, RuntimeError):
                pass

    def _set_busy(self, busy, text=None):
        self._busy = busy
        state = "disabled" if busy else "normal"
        for b in (self.up_btn, self.new_btn, self.select_btn):
            b.configure(state=state)
        if text is not None:
            self.status.configure(text=text)

    def _show(self, path, items):
        self.current = path
        self.path_var.set(path)
        self.listbox.delete(0, "end")
        folders = sorted((i["name"] for i in items if i.get("is_dir")), key=str.lower)
        for name in folders:
            self.listbox.insert("end", name)
        self._set_busy(False, f"{len(folders)} folder(s)")
        self.up_btn.configure(state="disabled" if path == "/" else "normal")

    def _fail(self, err):
        self._set_busy(False, "Failed")
        messagebox.showerror("FXPAK", f"{err}\n\n{ERROR_HINT}", parent=self.top)
        if self.listbox.size() == 0 and self.path_var.get() == "/" and not self.current_loaded:
            self._close()

    current_loaded = False

    def _run_listing(self, coro_factory):
        self._set_busy(True, "Loading…")

        def cb(result, err):
            def apply():
                if err:
                    self._fail(err)
                else:
                    path, items = result
                    self.current_loaded = True
                    self._show(path, items)
            self._ui(apply)
        self.worker.submit(coro_factory, cb)

    # -- navigation ----------------------------------------------------
    def _navigate_initial(self, initial):
        async def resolve(client):
            # Walk down the stored path only through folders that exist (listing a
            # missing folder would make the SD2SNES drop the connection).
            path = "/"
            items = await client.list_directory("/")
            for part in [p for p in (initial or "").replace("\\", "/").split("/") if p]:
                match = client.find_directory_case_insensitive(
                    part, [i["name"] for i in items if i.get("is_dir")])
                if not match:
                    break
                path = f"{path.rstrip('/')}/{match}"
                items = await client.list_directory(path)
            return path, items
        self._run_listing(resolve)

    def _go(self, path):
        async def go(client):
            return path, await client.list_directory(path)
        self._run_listing(go)

    def _enter_selected(self):
        sel = self.listbox.curselection()
        if sel and not self._busy:
            self._go(f"{self.current.rstrip('/')}/{self.listbox.get(sel[0])}")

    def _go_up(self):
        if self.current != "/" and not self._busy:
            parent = self.current.rstrip("/").rpartition("/")[0] or "/"
            self._go(parent)

    def _new_folder(self):
        name = simpledialog.askstring("New Folder", "Name of the new folder:", parent=self.top)
        if not name:
            return
        safe = QUSB2SNESSync.safe_remote_name(name)
        if not safe or safe != name.strip():
            messagebox.showwarning(
                "New Folder", 'Folder names cannot contain  < > : " / \\ | ? *', parent=self.top)
            return
        target = f"{self.current.rstrip('/')}/{safe}"
        base = self.current

        async def make(client):
            items = await client.list_directory(base)
            if any(i["name"].lower() == safe.lower() for i in items):
                raise FileExistsError(f"'{safe}' already exists here")
            if not await client.create_directory(target):
                raise RuntimeError(f"Could not create {target}")
            return target, await client.list_directory(target)
        self._run_listing(make)

    def _select(self):
        path = self.current
        self._close()
        self.on_select(path)

    def _close(self):
        if self._closed:
            return
        self._closed = True
        worker = self.worker
        try:
            self.top.grab_release()
            self.top.destroy()
        except tk.TclError:
            pass
        import threading
        threading.Thread(target=worker.close, daemon=True).start()


class FxpakActions:
    """Send ROMs to the FXPAK and/or boot them. Used by the collection page."""

    def __init__(self, widget, logger=None):
        self.widget = widget
        self.logger = logger
        self._progress, self._error = _log_funcs(logger)

    # -- config / helpers ---------------------------------------------
    def _settings(self):
        from config_manager import ConfigManager
        settings = fxpak_settings(ConfigManager())
        if not settings["enabled"]:
            messagebox.showinfo(
                "FXPAK not enabled",
                "Enable the FXPAK / QUSB2SNES connection in Settings first "
                "(and choose the folder on the SD card).\n\n" + HELP_TEXT,
                parent=self.widget.winfo_toplevel())
            return None
        return settings

    def _ui(self, fn):
        try:
            self.widget.after(0, fn)
        except (tk.TclError, RuntimeError):
            pass

    def _worker(self, settings):
        return FxpakWorker(settings, self._progress, self._error)

    @staticmethod
    def _close_async(worker):
        import threading
        threading.Thread(target=worker.close, daemon=True).start()

    def _show_error(self, err):
        messagebox.showerror("FXPAK", f"{err}\n\n{ERROR_HINT}", parent=self.widget.winfo_toplevel())

    @staticmethod
    def remote_name(local_path):
        return QUSB2SNESSync.safe_remote_name(os.path.basename(local_path))

    # -- public actions -----------------------------------------------
    def send(self, paths, play_path=None):
        """Send one or more local ROMs to the configured folder (optionally play one)."""
        settings = self._settings()
        if not settings:
            return
        top = self.widget.winfo_toplevel()
        existing = [p for p in dict.fromkeys(paths) if p and os.path.isfile(p)]
        missing = [p for p in paths if p and not os.path.isfile(p)]
        if not existing:
            messagebox.showwarning("Send to FXPAK", "None of the selected ROM files exist on disk.", parent=top)
            return
        if missing:
            self._progress(f"⚠️ {len(missing)} file(s) not found locally and ignored")
        self._start_send(settings, self._worker(settings), existing, play_path)

    def play(self, local_path):
        """Boot a ROM that is on the card; offer to send it first if it is not."""
        settings = self._settings()
        if not settings:
            return
        top = self.widget.winfo_toplevel()
        if not local_path or not os.path.isfile(local_path):
            messagebox.showwarning("Play on FXPAK", "The ROM file does not exist on disk.", parent=top)
            return
        name = self.remote_name(local_path)
        folder = settings["remote_folder"]
        worker = self._worker(settings)
        dialog = _BusyDialog(self.widget, "Play on FXPAK", worker.cancel)

        self._ui(lambda: dialog.update("Connecting to the FXPAK…"))

        async def check(client):
            self._ui(lambda: dialog.update("Looking for the game on the card…"))
            return await client.remote_file_exists(folder, name)

        def cb(result, err):
            def apply():
                dialog.close()
                if err:
                    self._close_async(worker)
                    self._show_error(err)
                    return
                if result:
                    self._boot(worker, f"{folder.rstrip('/')}/{name}")
                else:
                    self._start_send(settings, worker, [local_path], local_path)
            self._ui(apply)
        worker.submit(check, cb)

    # -- internals -----------------------------------------------------
    def _boot(self, worker, remote_path):
        dialog = _BusyDialog(self.widget, "Play on FXPAK", worker.cancel)
        dialog.update(f"Starting {os.path.basename(remote_path)} on the console…")

        def cb(result, err):
            def apply():
                dialog.close()
                self._close_async(worker)
                if err or not result:
                    self._show_error(err or f"Boot command failed for {remote_path}")
                else:
                    self._progress(f"▶️ Started {remote_path} on the FXPAK")
            self._ui(apply)
        worker.submit(lambda c: c.boot_rom(remote_path), cb)

    def _start_send(self, settings, worker, paths, play_path):
        files = [(p, self.remote_name(p)) for p in paths]
        folder = settings["remote_folder"]
        dialog = _BusyDialog(self.widget, "Sending to FXPAK", worker.cancel,
                             determinate=True, maximum=100)

        state = {"index": 1, "total": len(files), "name": ""}

        def on_file(index, total, name):
            state.update(index=index, total=total, name=name, pct=0)
            self._ui(lambda: dialog.update(f"Sending {index}/{total}: {name} (0%)", 0))

        def on_bytes(sent, size, name):
            pct = int(sent * 100 / size) if size else 100
            if pct == state.get("pct"):
                return
            state["pct"] = pct
            idx, total = state["index"], state["total"]
            text = (f"Sending {idx}/{total}: {name} ({pct}%)" if pct < 100
                    else f"Sending {idx}/{total}: {name} (100%)")
            self._ui(lambda: dialog.update(text, pct))

        def cb(result, err):
            self._ui(lambda: self._send_done(settings, worker, dialog, files, result, err, play_path))
        worker.submit(lambda c: c.send_files(files, folder, on_file, on_bytes), cb)

    def _send_done(self, settings, worker, dialog, files, result, err, play_path):
        dialog.close()
        top = self.widget.winfo_toplevel()
        if err:
            self._close_async(worker)
            self._show_error(err)
            return
        lines = []
        if result["uploaded"]:
            lines.append(f"Uploaded ({len(result['uploaded'])}):\n" + "\n".join(f"  • {n}" for n in result["uploaded"]))
        if result["skipped"]:
            lines.append(f"Skipped, already on the card ({len(result['skipped'])}) — not overwritten:\n"
                         + "\n".join(f"  • {n}" for n in result["skipped"]))
        if result["failed"]:
            lines.append(f"Failed ({len(result['failed'])}):\n" + "\n".join(f"  • {n}" for n in result["failed"]))
        if result["cancelled"]:
            lines.append("Cancelled — remaining files were not sent.")
        folder = settings["remote_folder"]
        summary = f"Target: {folder}\n\n" + "\n\n".join(lines or ["Nothing to do."])

        play_name = self.remote_name(play_path) if play_path else None
        can_play = bool(play_name) and not result["cancelled"] and play_name not in result["failed"]
        if can_play and play_name in result["skipped"]:
            summary += "\n\nThe existing copy on the card will be started."
        if result["failed"] or result["cancelled"]:
            messagebox.showwarning("Send to FXPAK", summary, parent=top)
        elif not can_play:
            messagebox.showinfo("Send to FXPAK", summary, parent=top)
        self._progress("📤 Send to FXPAK: " + " | ".join(
            f"{k} {len(result[k])}" for k in ("uploaded", "skipped", "failed")))
        if can_play:
            self._boot(worker, result["remote_paths"].get(play_name, f"{folder.rstrip('/')}/{play_name}"))
        else:
            self._close_async(worker)


class FxpakSettingsSection:
    """Settings block: enable, connection, SD card folder (with browser)."""

    def __init__(self, parent, config, logger=None):
        self.parent = parent
        self.config = config
        self.logger = logger

    def create(self):
        s = fxpak_settings(self.config)
        frame = ttk.LabelFrame(self.parent, text="FXPAK Pro (QUSB2SNES)", padding=(15, 10, 15, 15))
        self.frame = frame

        self.enabled_var = tk.BooleanVar(value=s["enabled"])
        ttk.Checkbutton(frame, text="Enable Send / Play on FXPAK in the Collection (right-click a hack)",
                        variable=self.enabled_var, style="Custom.TCheckbutton",
                        command=self._save).pack(anchor="w", pady=(0, 8))

        target_row = ttk.Frame(frame)
        target_row.pack(fill="x", pady=(0, 8))
        ttk.Label(target_row, text="Play button (▶) starts the game on:", style="Custom.TLabel").pack(side="left", padx=(0, 10))
        self.target_var = tk.StringVar(value=s["play_target"])
        for text, value in (("Emulator", "emulator"), ("FXPAK Pro (send if needed, then play)", "fxpak")):
            ttk.Radiobutton(target_row, text=text, value=value, variable=self.target_var,
                            command=self._save).pack(side="left", padx=(0, 14))

        conn = ttk.Frame(frame)
        conn.pack(fill="x", pady=(0, 8))
        self.host_var = tk.StringVar(value=s["host"])
        self.port_var = tk.StringVar(value=str(s["port"]))
        self.device_var = tk.StringVar(value=s["device"])
        for label, var, width in (("Host:", self.host_var, 16), ("Port:", self.port_var, 7),
                                  ("Device (blank = first found):", self.device_var, 22)):
            ttk.Label(conn, text=label, style="Custom.TLabel").pack(side="left", padx=(0, 6))
            entry = ttk.Entry(conn, textvariable=var, width=width)
            entry.pack(side="left", padx=(0, 16))
            entry.bind("<FocusOut>", self._save)
            entry.bind("<Return>", self._save)

        folder_row = ttk.Frame(frame)
        folder_row.pack(fill="x", pady=(0, 8))
        ttk.Label(folder_row, text="Folder on SD card:", style="Custom.TLabel").pack(side="left", padx=(0, 10))
        self.folder_var = tk.StringVar(value=s["remote_folder"])
        entry = ttk.Entry(folder_row, textvariable=self.folder_var, width=40)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry.bind("<FocusOut>", self._save)
        entry.bind("<Return>", self._save)
        ttk.Button(folder_row, text="Browse…", command=self._browse, style="Custom.TButton").pack(side="left")

        ttk.Label(frame, text=HELP_TEXT, style="Custom.TLabel", font=("Segoe UI", 8),
                  foreground="gray", wraplength=700, justify="left").pack(anchor="w")
        return frame

    def _save(self, event=None):
        folder = self.folder_var.get().strip() or DEFAULT_REMOTE_FOLDER
        if not folder.startswith("/"):
            folder = "/" + folder
        self.folder_var.set(folder)
        try:
            port = int(self.port_var.get())
        except ValueError:
            port = 23074
            self.port_var.set(str(port))
        for key, value in (("qusb2snes_enabled", self.enabled_var.get()),
                           ("qusb2snes_host", self.host_var.get().strip() or "localhost"),
                           ("qusb2snes_port", port),
                           ("qusb2snes_device", self.device_var.get().strip()),
                           ("qusb2snes_play_target", self.target_var.get()),
                           ("qusb2snes_remote_folder", folder)):
            self.config.config[key] = value
        self.config.save()

    def _browse(self):
        self._save()
        settings = fxpak_settings(self.config)

        def picked(path):
            self.folder_var.set(path)
            self._save()
        RemoteFolderBrowser(self.frame, settings, settings["remote_folder"], picked, self.logger)
