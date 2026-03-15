"""
Multi-Patch Selection Dialog
Shows when a downloaded ZIP contains multiple BPS/IPS patch files.
Lets the user choose which versions to patch, rename them, and designate a primary.

Copyright (c) 2025 iamtheratio
Licensed under the MIT License - see LICENSE file for details
"""

import os
import re
import threading
import tkinter as tk
from tkinter import ttk

from utils import set_window_icon, safe_filename, title_case


def _suggest_name(patch_path, temp_dir):
    """Derive a clean suggested output name from a patch file path."""
    try:
        rel = os.path.relpath(patch_path, temp_dir)
    except ValueError:
        rel = os.path.basename(patch_path)
    # Use the filename segment (strips the folder prefix like "V1.10/")
    name, _ = os.path.splitext(rel)
    parts = name.replace("\\", "/").split("/")
    raw = parts[-1].strip()
    # Replace underscores with spaces before any other processing
    raw = raw.replace("_", " ")
    # Insert a space between letters and digits so "Akogare2" → "Akogare 2",
    # but protect version tokens like "v1.10" from being split first.
    raw = re.sub(r'(?<![Vv])([A-Za-z])(\d)', r'\1 \2', raw)
    # Apply the same filename sanitisation + title-case the app uses everywhere
    result = title_case(safe_filename(raw))
    # Normalise version tokens: "V 1.10" / "V1.10" → "v1.10"
    result = re.sub(r'\bV\s*(\d[\d.]*)', lambda m: 'v' + m.group(1), result)
    return result


def _display_label(patch_path, temp_dir):
    """Relative path shown in the dialog (mirrors the zip structure)."""
    try:
        rel = os.path.relpath(patch_path, temp_dir)
    except ValueError:
        rel = os.path.basename(patch_path)
    return rel.replace("\\", "/")


class MultiPatchDialog:
    """
    Modal dialog for selecting which patch files to apply when a ZIP
    contains multiple BPS/IPS files.

    Usage (on the main thread):
        dialog = MultiPatchDialog(root, patch_files, hack_name, temp_dir)
        selections = dialog.show()
        # selections is None (cancelled) or a list of:
        #   {"patch_path": str, "output_name": str, "primary": bool}
    """

    def __init__(self, root, patch_files, hack_name, temp_dir):
        self.root = root
        # Sort so higher versions (alphabetically later) appear last and become default primary
        self.patch_files = sorted(patch_files,
                                  key=lambda p: os.path.basename(p).lower())
        self.hack_name = hack_name
        self.temp_dir = temp_dir
        self.result = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show(self):
        """Display the dialog (blocking) and return selections or None."""
        self._build()
        self.dialog.wait_window()
        return self.result

    # ------------------------------------------------------------------
    # Dialog construction
    # ------------------------------------------------------------------

    def _build(self):
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Multiple Patch Files Found")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.root)
        self.dialog.grab_set()
        set_window_icon(self.dialog)

        # ── Per-row state ──────────────────────────────────────────────
        n = len(self.patch_files)
        self._check_vars = [tk.BooleanVar(value=True) for _ in range(n)]
        self._name_vars  = [tk.StringVar(value=_suggest_name(p, self.temp_dir))
                            for p in self.patch_files]
        # Default primary = last file (highest version alphabetically)
        self._primary_var = tk.StringVar(value=str(n - 1))

        # ── Layout ────────────────────────────────────────────────────
        outer = ttk.Frame(self.dialog, padding=(24, 20, 24, 20))
        outer.pack(fill="both", expand=True)

        # Header
        ttk.Label(
            outer,
            text=f"{n} patch files found in \"{self.hack_name}\"",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        ttk.Label(
            outer,
            text=(
                "Select which versions to patch and set your output filenames.\n"
                "The 'Default' file will open by default when launching from your collection."
            ),
            justify="left"
        ).pack(anchor="w", pady=(6, 18))

        # Single grid frame shared by headers (row 0) and data rows (row 1+)
        # so every column is guaranteed to align perfectly.
        self._grid_frame = ttk.Frame(outer)
        self._grid_frame.pack(fill="x")

        bold = ("Segoe UI", 9, "bold")
        ttk.Label(self._grid_frame, text="Include",  font=bold, anchor="center").grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
        ttk.Label(self._grid_frame, text="Default",  font=bold, anchor="center").grid(row=0, column=1, padx=(0, 6), pady=(0, 6), sticky="w")
        ttk.Label(self._grid_frame, text="Source file in ZIP", font=bold, anchor="w").grid(row=0, column=2, padx=(0, 8), pady=(0, 6), sticky="w")
        ttk.Label(self._grid_frame, text="").grid(row=0, column=3, pady=(0, 6))        # arrow spacer
        ttk.Label(self._grid_frame, text="Output filename (no extension)", font=bold, anchor="w").grid(row=0, column=4, pady=(0, 6), sticky="w")
        self._grid_frame.columnconfigure(2, weight=1)
        self._grid_frame.columnconfigure(4, weight=1)

        ttk.Separator(outer, orient="horizontal").pack(fill="x", pady=(0, 10))

        # Data rows – built directly into self._grid_frame starting at grid row 1
        self._entries = []
        for i, patch_path in enumerate(self.patch_files):
            self._build_row(i, patch_path)

        # Buttons
        btn_frame = ttk.Frame(outer)
        btn_frame.pack(fill="x", pady=(18, 0))

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self._on_cancel,
            style="Custom.TButton",
            width=12
        ).pack(side="right", padx=(8, 0))

        self._patch_btn = ttk.Button(
            btn_frame,
            text="Patch Selected",
            command=self._on_patch,
            style="Accent.TButton",
            width=16
        )
        self._patch_btn.pack(side="right")

        self._update_patch_button()
        self._centre_on_parent()

        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    # Characters that are illegal in filenames on Windows/macOS/Linux.
    # Kept as a frozenset for O(1) lookup on every keystroke.
    _INVALID_CHARS = frozenset('<>:"/\\|?*')

    def _build_row(self, i, patch_path):
        grid = self._grid_frame
        r = i + 1  # header is row 0

        # Include checkbox — whether to patch this file at all
        cb = ttk.Checkbutton(
            grid,
            variable=self._check_vars[i],
            command=lambda idx=i: self._on_check_change(idx),
        )
        cb.grid(row=r, column=0, padx=(0, 6), pady=8, sticky="w")

        # Default (primary) radio — opens this file in the emulator by default
        rb = ttk.Radiobutton(
            grid,
            variable=self._primary_var,
            value=str(i),
            command=lambda idx=i: self._on_primary_change(idx),
        )
        rb.grid(row=r, column=1, padx=(0, 6), pady=8, sticky="w")

        # Source label (zip-relative path)
        display = _display_label(patch_path, self.temp_dir)
        ttk.Label(grid, text=display, anchor="w").grid(row=r, column=2, padx=(0, 8), pady=8, sticky="ew")

        ttk.Label(grid, text="→").grid(row=r, column=3, padx=(0, 8), pady=8)

        # Output name entry — block invalid filename characters on every keystroke
        vcmd = (self.dialog.register(
                    lambda text: not any(c in MultiPatchDialog._INVALID_CHARS for c in text)
                ), "%P")  # %P = value of the field *if* the edit is allowed
        entry = ttk.Entry(grid, textvariable=self._name_vars[i],
                          font=("Segoe UI", 9), width=30,
                          validate="key", validatecommand=vcmd)
        entry.grid(row=r, column=4, pady=8, sticky="ew")
        self._entries.append(entry)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_check_change(self, idx):
        """Ensure the primary radio always points to a checked row."""
        checked_indices = [i for i, v in enumerate(self._check_vars) if v.get()]

        if not checked_indices:
            # Nothing checked – disable patch button, keep radio where it is
            self._update_patch_button()
            return

        current_primary = int(self._primary_var.get())
        if current_primary not in checked_indices:
            # Auto-move primary to the last remaining checked item
            self._primary_var.set(str(checked_indices[-1]))

        # Enable/disable entry based on check state
        state = "normal" if self._check_vars[idx].get() else "disabled"
        self._entries[idx].config(state=state)

        self._update_patch_button()

    def _on_primary_change(self, idx):
        """When user clicks a primary radio, auto-check that row."""
        self._check_vars[idx].set(True)
        self._entries[idx].config(state="normal")
        self._update_patch_button()

    def _update_patch_button(self):
        any_checked = any(v.get() for v in self._check_vars)
        state = "normal" if any_checked else "disabled"
        try:
            self._patch_btn.config(state=state)
        except Exception:
            pass

    def _on_cancel(self):
        self.result = None
        self.dialog.destroy()

    def _on_patch(self):
        primary_idx = int(self._primary_var.get())
        selections = []

        for i, patch_path in enumerate(self.patch_files):
            if not self._check_vars[i].get():
                continue

            output_name = self._name_vars[i].get().strip()
            if not output_name:
                output_name = _suggest_name(patch_path, self.temp_dir)

            selections.append({
                "patch_path": patch_path,
                "output_name": output_name,
                "primary": (i == primary_idx)
            })

        # Guard: ensure exactly one primary flag is set in the result
        if selections and not any(s["primary"] for s in selections):
            selections[-1]["primary"] = True

        self.result = selections
        self.dialog.destroy()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _centre_on_parent(self):
        self.dialog.update_idletasks()
        MIN_WIDTH = 720
        pw = self.root.winfo_width()
        ph = self.root.winfo_height()
        px = self.root.winfo_rootx()
        py = self.root.winfo_rooty()
        dw = max(self.dialog.winfo_reqwidth(), MIN_WIDTH)
        dh = self.dialog.winfo_reqheight()
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2
        self.dialog.geometry(f"{dw}x{dh}+{x}+{y}")


# ---------------------------------------------------------------------------
# Thread-safe factory
# ---------------------------------------------------------------------------

def make_multi_patch_callback(root):
    """
    Returns a callback suitable for passing to the download pipeline.

    The callback is called from the download background thread.  It marshals
    the dialog onto the main thread via root.after(), blocks the download
    thread with a threading.Event until the user responds, then returns the
    selections (or None if cancelled).

    Usage:
        callback = make_multi_patch_callback(root)
        run_pipeline_wrapper(..., multi_patch_callback=callback)
    """
    def callback(patch_files, hack_name, temp_dir):
        event = threading.Event()
        result_box = [None]

        def show_on_main():
            try:
                from ui.components.multi_patch_dialog import MultiPatchDialog
                dialog = MultiPatchDialog(root, patch_files, hack_name, temp_dir)
                result_box[0] = dialog.show()
            finally:
                event.set()

        root.after(0, show_on_main)
        event.wait(timeout=600)   # 10-minute safety timeout
        return result_box[0]

    return callback
