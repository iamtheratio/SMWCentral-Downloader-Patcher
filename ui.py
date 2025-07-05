# ui.py — Part 1

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json

CONFIG_PATH = "config.json"
FONT = ("Segoe UI", 9)  # Changed from 12 to 9
LOG_COLORS = {
    "Debug": "blue",
    "Information": "black",
    "Error": "red",
    "Verbose": "purple"
}
HACK_TYPES = ["Standard", "Kaizo", "Puzzle", "Tool-Assisted", "Pit"]
DIFFICULTY_LIST = [
    "newcomer", "casual", "skilled",
    "advanced", "expert", "master", "grandmaster"
]

def setup_ui(root, run_pipeline_func):
    # Load or create config
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    # Path & filter variables
    flips_path_var    = tk.StringVar(root, value=config.get("flips_path", ""))
    base_rom_path_var = tk.StringVar(root, value=config.get("base_rom_path", ""))
    output_dir_var    = tk.StringVar(root, value=config.get("output_dir", ""))

    log_level_var = tk.StringVar(root, value="Information")
    type_var      = tk.StringVar(root, value="Kaizo")
    hof_var       = tk.StringVar(root, value="Any")
    sa1_var       = tk.StringVar(root, value="Any")
    collab_var    = tk.StringVar(root, value="Any")
    demo_var      = tk.StringVar(root, value="Any")

    difficulty_vars  = {d: tk.BooleanVar(root) for d in DIFFICULTY_LIST}
    toggle_all_state = tk.BooleanVar(root, value=False)

    # Save paths back to config.json
    def save_paths():
        config["flips_path"]    = flips_path_var.get()
        config["base_rom_path"] = base_rom_path_var.get()
        config["output_dir"]    = output_dir_var.get()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    # File/folder selectors
    def select_flips():
        p = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])
        if p:
            flips_path_var.set(p)
            save_paths()

    def select_base_rom():
        p = filedialog.askopenfilename(filetypes=[("SMC files", "*.smc")])
        if p:
            base_rom_path_var.set(p)
            save_paths()

    def select_output_dir():
        p = filedialog.askdirectory()
        if p:
            output_dir_var.set(p)
            save_paths()

    # Convert Yes/No to API flag
    def dropdown_to_flag(v):
        return {"Yes": "1", "No": "0"}.get(v)

    # Build API filter payload
    def generate_filter_payload():
        payload = {
            "type": [type_var.get().lower()],
            "difficulties": [d for d in DIFFICULTY_LIST if difficulty_vars[d].get()]
        }
        for key, var in (
            ("demo", demo_var), ("hof", hof_var),
            ("sa1", sa1_var), ("collab", collab_var)
        ):
            flag = dropdown_to_flag(var.get())
            if flag:
                payload[key] = [flag]
        return payload

    # Logging controls
    def should_log(level):
        cur = log_level_var.get()
        if level == "Error":
            return True
        if cur == "Verbose":
            return True
        if cur == "Debug":
            return level in ("Information", "Debug")
        return level == "Information"

    def log(msg, level="Information"):
        if not should_log(level):
            return
        log_text.config(state="normal")
        
        if " - Replaced with a new version!" in msg:
            base_message = msg.split(" - ")[0]
            log_text.insert("end", base_message + " - ", level)
            log_text.insert("end", "Replaced with a new version!\n", "red_italic")
        else:
            log_text.insert("end", msg + "\n", level)
            
        log_text.config(state="disabled")
        log_text.see("end")

    # Threaded pipeline runner
    def run_pipeline_threaded():
        if not (
            flips_path_var.get()
            and base_rom_path_var.get()
            and output_dir_var.get()
        ):
            messagebox.showerror("Missing Info", "Fill in all paths before continuing.")
            return
        if not any(v.get() for v in difficulty_vars.values()):
            messagebox.showerror("No Difficulty", "Please select at least one difficulty.")
            return

        payload = generate_filter_payload()

        def task():
            try:
                run_pipeline_func(
                    filter_payload=payload,
                    flips_path=flips_path_var.get(),
                    base_rom_path=base_rom_path_var.get(),
                    output_dir=output_dir_var.get(),
                    log=log
                )
                log("✅ Done!", level="Information")
            except Exception as e:
                log(f"❌ Error: {e}", level="Error")

        threading.Thread(target=task, daemon=True).start()

    # Toggle all difficulty checkboxes
    def toggle_difficulties():
        new = not toggle_all_state.get()
        for v in difficulty_vars.values():
            v.set(new)
        toggle_all_state.set(new)
        toggle_button.config(text="Deselect All" if new else "Select All")

    # Radio-button helper
    def add_radio_row(parent, label, var, row):
        ttk.Label(parent, text=f"{label}:", font=FONT)\
            .grid(row=row, column=0, sticky="w", pady=3)
        for i, val in enumerate(["Any", "Yes", "No"]):
            ttk.Radiobutton(
                parent, text=val, variable=var, value=val,
                style="Custom.TRadiobutton"
            ).grid(row=row, column=i+1, padx=8, pady=3, sticky="w")
# ui.py — Part 2

    # --- BUILD THE GUI LAYOUT BELOW ---
    main_frame = ttk.Frame(root, padding=25)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(
        main_frame,
        text="SMWCentral Downloader & Patcher",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=(0, 20))

    style = ttk.Style()
    for widget in ("TCheckbutton", "TRadiobutton", "TButton", "TCombobox"):
        style.configure(f"Custom.{widget}", font=FONT)

    # Difficulty selection
    diff_frame = ttk.LabelFrame(main_frame, text="Difficulty Selection", padding=15)
    diff_frame.pack(fill="x", pady=10)
    for i, d in enumerate(DIFFICULTY_LIST):
        ttk.Checkbutton(
            diff_frame, text=d.title(), variable=difficulty_vars[d],
            style="Custom.TCheckbutton"
        ).grid(row=0, column=i, padx=10)
    toggle_button = ttk.Button(
        diff_frame, text="Select All", command=toggle_difficulties,
        style="Custom.TButton"
    )
    toggle_button.grid(row=1, column=0, pady=10, sticky="w")

    # Setup & filters section
    row_frame = ttk.Frame(main_frame)
    row_frame.pack(fill="both", expand=True, pady=10)

    setup_frame = ttk.LabelFrame(row_frame, text="Setup", padding=15)
    setup_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))

    filter_frame = ttk.LabelFrame(row_frame, text="Hack Filters", padding=15)
    filter_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))

    for col in (0,1):
        row_frame.columnconfigure(col, weight=1)
        setup_frame.columnconfigure(col, weight=1)
        filter_frame.columnconfigure(col, weight=1)

    # Setup input fields
    ttk.Label(setup_frame, text="Flips Path:", font=FONT).grid(row=0, column=0, sticky="w")
    ttk.Button(
        setup_frame, text="Browse", command=select_flips,
        style="Custom.TButton"
    ).grid(row=0, column=1, sticky="w")
    ttk.Label(
        setup_frame, textvariable=flips_path_var,
        foreground="gray", font=FONT
    ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)

    ttk.Label(setup_frame, text="Base ROM:", font=FONT).grid(row=2, column=0, sticky="w", pady=(10,0))
    ttk.Button(
        setup_frame, text="Browse", command=select_base_rom,
        style="Custom.TButton"
    ).grid(row=2, column=1, sticky="w")
    ttk.Label(
        setup_frame, textvariable=base_rom_path_var,
        foreground="gray", font=FONT
    ).grid(row=3, column=0, columnspan=2, sticky="ew", padx=5)

    ttk.Label(setup_frame, text="Output Folder:", font=FONT).grid(row=4, column=0, sticky="w", pady=(10,0))
    ttk.Button(
        setup_frame, text="Browse", command=select_output_dir,
        style="Custom.TButton"
    ).grid(row=4, column=1, sticky="w")
    ttk.Label(
        setup_frame, textvariable=output_dir_var,
        foreground="gray", font=FONT
    ).grid(row=5, column=0, columnspan=2, sticky="ew", padx=5)

    # Filter controls
    ttk.Label(filter_frame, text="Hack Type:", font=FONT).grid(row=0, column=0, sticky="w", pady=(0,5))
    ttk.Combobox(
        filter_frame, textvariable=type_var, values=HACK_TYPES,
        state="readonly", style="Custom.TCombobox"
    ).grid(row=0, column=1, columnspan=3, sticky="ew")

    add_radio_row(filter_frame, "Hall of Fame", hof_var, 1)
    add_radio_row(filter_frame, "SA-1",        sa1_var, 2)
    add_radio_row(filter_frame, "Collab",      collab_var, 3)
    add_radio_row(filter_frame, "Demo",        demo_var, 4)

    # Run button
    ttk.Button(
        main_frame, text="Download & Patch",
        command=run_pipeline_threaded, padding=10,
        style="Custom.TButton"
    ).pack(pady=(10,4))

    # Log-level selector
    log_frame = ttk.Frame(main_frame)
    log_frame.pack(fill="x", pady=(5,0))
    right = ttk.Frame(log_frame); right.pack(side="right")
    ttk.Label(right, text="Log Level:", font=FONT).pack(side="left", padx=(0,6))
    ttk.Combobox(
        right, textvariable=log_level_var,
        values=["Information", "Debug", "Verbose"],
        state="readonly", style="Custom.TCombobox"
    ).pack(side="left")

    # Log window
    global log_text
    log_text = scrolledtext.ScrolledText(
        main_frame, height=18, wrap="word",
        state="disabled", font=("Segoe UI", 9)
    )
    log_text.pack(fill="both", expand=True, pady=(2,0))
    log_text.configure(font=FONT)
    log_text.tag_configure("red_italic", foreground="red", font=("Segoe UI", 9, "italic"))

    # Configure tag colors
    for tag, color in LOG_COLORS.items():
        log_text.tag_config(tag, foreground=color)

def log_message(text_widget, message, replacement=False):
    text_widget.configure(state='normal')
    if replacement:
        base_message = "✅ Patched: " + message.split(" - ")[0]
        replacement_text = " - Replaced with a new version!"
        text_widget.insert(tk.END, base_message)
        text_widget.insert(tk.END, replacement_text + "\n", "red_italic")
    else:
        text_widget.insert(tk.END, message + "\n")
    text_widget.configure(state='disabled')
    text_widget.see(tk.END)
