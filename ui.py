# ui.py — Part 1

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
from utils import TYPE_KEYMAP
import sv_ttk

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

def setup_ui(root, run_pipeline_func, toggle_theme_callback):
    # Create theme toggle frame for top right
    theme_frame = ttk.Frame(root)
    theme_frame.pack(anchor="ne", padx=10, pady=5)
    
    # Add light mode label (empty)
    ttk.Label(
        theme_frame, 
        text="", 
        width=1
    ).pack(side="left", padx=(0, 5))
    
    # Add theme switch
    theme_switch = ttk.Checkbutton(
        theme_frame,
        style="Switch.TCheckbutton",
        command=lambda: toggle_theme_callback(root)
    )
    theme_switch.pack(side="left")
    theme_switch.state(['selected'])  # Start checked for dark mode
    
    # Add dark mode label
    ttk.Label(
        theme_frame, 
        text="🌙",
        font=("Segoe UI Emoji", 12),
    ).pack(side="left", padx=(2, 5))

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

    def browse_rom():
        filename = filedialog.askopenfilename(
            title="Select Base ROM",
            filetypes=[
                ("Super Nintendo ROMs", "*.smc *.sfc"),
                ("All files", "*.*")
            ]
        )
        if filename:
            base_rom_path_var.set(filename)
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
        selected_type_label = type_var.get()
        selected_type = TYPE_KEYMAP.get(selected_type_label, "standard")

        payload = {
            "type": [selected_type],
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
            return level != "Debug"  # Don't show Debug messages in Debug mode
        return level == "Information"

    def log(message, level="Information"):
        """Log a message with appropriate styling"""
        if not hasattr(log, 'log_text'):
            print("Log text not available yet")
            return
        
        # Check if we should log this message based on current log level
        # using original should_log function
        if not should_log(level):
            return
            
        log_text = log.log_text
        log_text.configure(state="normal")
        
        if level == "Error":
            log_text.insert(tk.END, message + "\n", "red_italic")
        elif level == "Warning":
            log_text.insert(tk.END, message + "\n", "dark_gray_italic")
        else:
            log_text.insert(tk.END, message + "\n")  # No special tag for debug messages
        
        log_text.configure(state="disabled")
        log_text.see(tk.END)
        log_text.update()

    # Threaded pipeline runner
    def run_pipeline_threaded():
        # Disable button and show running state
        download_button.configure(state="disabled", text="Running...")
        
        def pipeline_worker():
            try:
                payload = generate_filter_payload()
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
            finally:
                # Re-enable button when done
                root.after(0, lambda: download_button.configure(
                    state="normal", 
                    text="Download & Patch"
                ))
        
        # Start pipeline in separate thread
        import threading
        thread = threading.Thread(target=pipeline_worker, daemon=True)
        thread.start()

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

    style.configure("Large.Accent.TButton", 
                   font=("Segoe UI", 10, "bold"),  # Larger, bold font
                   padding=(20, 10))  # More internal padding

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
    ).grid(row=0, column=1, sticky="e", padx=(10, 0))  # Changed to sticky="e" and added left padding
    ttk.Label(
        setup_frame, textvariable=flips_path_var,
        foreground="gray", font=FONT
    ).grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 15))

    ttk.Label(setup_frame, text="Base ROM:", font=FONT).grid(row=2, column=0, sticky="w", pady=(10,0))
    ttk.Button(
        setup_frame, text="Browse", command=browse_rom,
        style="Custom.TButton"
    ).grid(row=2, column=1, sticky="e", padx=(10, 0))  # Changed to sticky="e" and added left padding
    ttk.Label(
        setup_frame, textvariable=base_rom_path_var,
        foreground="gray", font=FONT
    ).grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 15))

    ttk.Label(setup_frame, text="Output Folder:", font=FONT).grid(row=4, column=0, sticky="w", pady=(10,0))
    ttk.Button(
        setup_frame, text="Browse", command=select_output_dir,
        style="Custom.TButton"
    ).grid(row=4, column=1, sticky="e", padx=(10, 0))  # Changed to sticky="e" and added left padding
    ttk.Label(
        setup_frame, textvariable=output_dir_var,
        foreground="gray", font=FONT
    ).grid(row=5, column=0, columnspan=2, sticky="ew", padx=5)

    # Configure column weights
    setup_frame.columnconfigure(0, weight=1)  # Label column expands
    setup_frame.columnconfigure(1, weight=0)  # Button column stays fixed

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

    # Download & Patch button
    download_button = ttk.Button(
        main_frame, 
        text="Download & Patch", 
        command=run_pipeline_threaded,
        style="Large.Accent.TButton"
    )
    download_button.pack(pady=(10, 15))
    
    # Log-level selector
    log_frame = ttk.Frame(main_frame)
    log_frame.pack(fill="x", pady=(5,0))
    right = ttk.Frame(log_frame)
    right.pack(side="right")
    ttk.Label(right, text="Log Level:", font=FONT).pack(side="left", padx=(0,6))
    
    # Create a global log level variable that's directly accessible
    log_level_var = tk.StringVar(value="Information")

    def on_log_level_changed(*args):
        log.log_level = log_level_var.get()

    log_level_var.trace_add("write", on_log_level_changed)
    
    log_level_combo = ttk.Combobox(
        right, textvariable=log_level_var, 
        values=["Information", "Debug", "Verbose"],
        width=12, state="readonly"
    )
    log_level_combo.pack(side="right")
    log_level_combo.current(0)
    
    # Initialize log level
    log.log_level = "Information"
    
    # Log text area
    log_text = scrolledtext.ScrolledText(
        main_frame, height=18, wrap="word",
        state="disabled",
        bg="#2b2b2b" if sv_ttk.get_theme() == "dark" else "#ffffff",
        fg="#e0e0e0" if sv_ttk.get_theme() == "dark" else "#000000"
    )
    log_text.pack(fill="both", expand=True, pady=(2,0))
    
    # Store log_text reference
    log.log_text = log_text
    log.log_level = "Information"  # Default log level

    # Original tag configurations (no custom debug tag)
    log_text.tag_configure("red_italic", foreground="#ff6b6b" if sv_ttk.get_theme() == "dark" else "red", 
                      font=(FONT[0], FONT[1], "italic"))
    log_text.tag_configure("dark_gray_italic", foreground="#888888" if sv_ttk.get_theme() == "dark" else "#555555", 
                      font=(FONT[0], FONT[1], "italic"))

def log_message(text, level="Information"):
    """Log a message to the text widget with appropriate styling"""
    if not hasattr(log_message, 'log_text'):
        print("Log text not available yet")
        return
    
    # Check if we should show this message based on log level setting
    current_level = getattr(log_message, 'log_level', "Information")
    
    # Debug messages should be shown in Debug or Verbose mode, but not Information
    if level.lower() == "debug":
        if current_level == "Information":
            # Skip debug messages in Information mode
            return
    
    log_text = log_message.log_text
    log_text.configure(state="normal")
    
    # Apply appropriate tag
    if level.lower() == "debug":
        log_text.insert(tk.END, text + "\n", "custom_debug_tag")
    elif level.lower() == "error":
        log_text.insert(tk.END, text + "\n", "red_italic")
    else:
        log_text.insert(tk.END, text + "\n")
    
    log_text.configure(state="disabled")
    log_text.see(tk.END)

def update_log_colors(log_text):
    """Update log text colors based on current theme"""
    if sv_ttk.get_theme() == "dark":
        log_text.configure(bg="#2b2b2b", fg="#e0e0e0")
        log_text.tag_configure("red_italic", foreground="#ff6b6b", font=(FONT[0], FONT[1], "italic"))
        log_text.tag_configure("dark_gray_italic", foreground="#888888", font=(FONT[0], FONT[1], "italic"))
        log_text.tag_configure("debug", foreground="#16C172", font=(FONT[0], FONT[1]))  # Green debug color
    else:
        log_text.configure(bg="#ffffff", fg="#000000")
        log_text.tag_configure("red_italic", foreground="red", font=(FONT[0], FONT[1], "italic"))
        log_text.tag_configure("dark_gray_italic", foreground="#555555", font=(FONT[0], FONT[1], "italic"))
        log_text.tag_configure("debug", foreground="#16C172", font=(FONT[0], FONT[1]))  # Green debug color for light mode too
    

# Add this debug function
def debug_log_tags(log_text):
    """Print debug info about log text tags"""
    print("=== DEBUG LOG TAG INFO ===")
    print(f"Tags defined: {log_text.tag_names()}")
    print(f"custom_debug_tag config: {log_text.tag_configure('custom_debug_tag')}")
    # Try to create a test message with the tag
    log_text.configure(state="normal")
    log_text.insert(tk.END, "TEST DEBUG TAG\n", "custom_debug_tag")
    log_text.configure(state="disabled")
