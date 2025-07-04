import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import webbrowser
from scraper import run_scraper_pipeline

CONFIG_PATH = "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

FONT = ("Segoe UI", 12)

root = tk.Tk()
root.title("SMWC Downloader & Patcher")
root.geometry("800x800")
root.resizable(True, True)

# Styles
style = ttk.Style()
style.configure("Custom.TCheckbutton", font=FONT)
style.configure("Custom.TRadiobutton", font=FONT)
style.configure("Custom.TButton", font=FONT)

flips_path_var = tk.StringVar(value=config.get("flips_path", ""))
base_rom_path_var = tk.StringVar(value=config.get("base_rom_path", ""))
output_dir_var = tk.StringVar(value=config.get("output_dir", ""))

type_var = tk.StringVar(value="Kaizo")
hof_var = tk.StringVar(value="Any")
sa1_var = tk.StringVar(value="Any")
collab_var = tk.StringVar(value="Any")
demo_var = tk.StringVar(value="Any")

difficulty_options = [
    "newcomer", "casual", "skilled", "advanced",
    "expert", "master", "grandmaster"
]
difficulty_vars = {d: tk.BooleanVar() for d in difficulty_options}
toggle_all_state = tk.BooleanVar(value=False)

hack_type_options = ["Standard", "Kaizo", "Puzzle", "Tool-Assisted", "Pit"]

def dropdown_to_flag(value):
    return {"Yes": "1", "No": "0"}.get(value, None)

def select_flips():
    path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
    if path: flips_path_var.set(path); save_paths()

def select_base_rom():
    path = filedialog.askopenfilename(filetypes=[("SMC files", "*.smc")])
    if path: base_rom_path_var.set(path); save_paths()

def select_output_dir():
    folder = filedialog.askdirectory()
    if folder: output_dir_var.set(folder); save_paths()

def save_paths():
    config["flips_path"] = flips_path_var.get()
    config["base_rom_path"] = base_rom_path_var.get()
    config["output_dir"] = output_dir_var.get()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def log(msg):
    log_text.config(state="normal")
    log_text.insert("end", msg + "\n")
    log_text.see("end")
    log_text.config(state="disabled")

def run_pipeline():
    selected_difficulties = [d for d, v in difficulty_vars.items() if v.get()]
    if not selected_difficulties or not all([flips_path_var.get(), base_rom_path_var.get(), output_dir_var.get()]):
        messagebox.showerror("Missing Info", "Fill in all fields and select at least one difficulty.")
        return
    config_payload = {
        "type": [type_var.get().lower()],
        "difficulties": selected_difficulties,
        "demo": dropdown_to_flag(demo_var.get()),
        "hof": dropdown_to_flag(hof_var.get()),
        "sa1": dropdown_to_flag(sa1_var.get()),
        "collab": dropdown_to_flag(collab_var.get())
    }
    log("🚀 Running patcher...")
    try:
        run_scraper_pipeline(config_payload,
                             flips_path=flips_path_var.get(),
                             base_rom_path=base_rom_path_var.get(),
                             output_dir=output_dir_var.get(),
                             log=log)
        log("✅ Done!")
    except Exception as e:
        log(f"❌ Error: {e}")

def run_threaded():
    threading.Thread(target=run_pipeline, daemon=True).start()

def add_radio_row(parent, label, var, row):
    ttk.Label(parent, text=f"{label}:", font=FONT).grid(row=row, column=0, sticky="w", pady=3)
    for i, val in enumerate(["Any", "Yes", "No"]):
        ttk.Radiobutton(parent, text=val, variable=var, value=val, style="Custom.TRadiobutton").grid(row=row, column=i+1, padx=8, pady=3, sticky="w")

def toggle_difficulties():
    new_state = not toggle_all_state.get()
    for var in difficulty_vars.values():
        var.set(new_state)
    toggle_all_state.set(new_state)
    toggle_button.config(text="Deselect All" if new_state else "Select All")

# Layout
main_frame = ttk.Frame(root, padding=25)
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text="SMWCentral Downloader & Patcher", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

# Difficulty Frame
diff_frame = ttk.LabelFrame(main_frame, text="Difficulty Selection", padding=15)
diff_frame.pack(fill="x", pady=10)

for i, d in enumerate(difficulty_options):
    ttk.Checkbutton(
        diff_frame,
        text=d.title(),
        variable=difficulty_vars[d],
        style="Custom.TCheckbutton"
    ).grid(row=0, column=i, sticky="w", padx=10, pady=4)

toggle_button = ttk.Button(diff_frame, text="Select All", command=toggle_difficulties, style="Custom.TButton")
toggle_button.grid(row=1, column=0, padx=5, pady=10, sticky="w")

# Setup + Filters
row_frame = ttk.Frame(main_frame)
row_frame.pack(fill="x", pady=10)

setup_frame = ttk.LabelFrame(row_frame, text="Setup", padding=15)
setup_frame.grid(row=0, column=0, sticky="nsew", padx=(0,20))
filter_frame = ttk.LabelFrame(row_frame, text="Hack Filters", padding=15)
filter_frame.grid(row=0, column=1, sticky="nsew")

row_frame.columnconfigure(0, weight=1)
row_frame.columnconfigure(1, weight=1)

# Setup Inputs
ttk.Label(setup_frame, text="Flips Path:", font=FONT).grid(row=0, column=0, sticky="w")
ttk.Button(setup_frame, text="Browse", command=select_flips, style="Custom.TButton").grid(row=0, column=1, sticky="w")
ttk.Label(setup_frame, textvariable=flips_path_var, foreground="gray", font=FONT).grid(row=1, column=0, columnspan=2, sticky="w", padx=30)

ttk.Label(setup_frame, text="Base ROM:", font=FONT).grid(row=2, column=0, sticky="w", pady=(10,0))
ttk.Button(setup_frame, text="Browse", command=select_base_rom, style="Custom.TButton").grid(row=2, column=1, sticky="w")
ttk.Label(setup_frame, textvariable=base_rom_path_var, foreground="gray", font=FONT).grid(row=3, column=0, columnspan=2, sticky="w", padx=30)

ttk.Label(setup_frame, text="Output Folder:", font=FONT).grid(row=4, column=0, sticky="w", pady=(10,0))
ttk.Button(setup_frame, text="Browse", command=select_output_dir, style="Custom.TButton").grid(row=4, column=1, sticky="w")
ttk.Label(setup_frame, textvariable=output_dir_var, foreground="gray", font=FONT).grid(row=5, column=0, columnspan=2, sticky="w", padx=30)

# Filter Inputs
ttk.Label(filter_frame, text="Hack Type:", font=FONT).grid(row=0, column=0, sticky="w", pady=(0,5))
ttk.Combobox(filter_frame, textvariable=type_var, values=hack_type_options, state="readonly", font=FONT).grid(row=0, column=1, sticky="w", columnspan=3)

add_radio_row(filter_frame, "Hall of Fame", hof_var, 1)
add_radio_row(filter_frame, "SA-1", sa1_var, 2)
add_radio_row(filter_frame, "Collab", collab_var, 3)
add_radio_row(filter_frame, "Demo", demo_var, 4)

# Run + Log
ttk.Button(main_frame, text="Download & Patch", command=run_threaded, padding=10, style="Custom.TButton").pack(pady=15)
log_text = scrolledtext.ScrolledText(main_frame, height=12, wrap="word", state="disabled")
log_text.pack(fill="both", expand=True)

root.mainloop()
