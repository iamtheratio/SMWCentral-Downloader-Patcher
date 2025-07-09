import tkinter as tk
from tkinter import ttk
from api_pipeline import run_pipeline
from ui import setup_ui, update_log_colors
import sv_ttk
import sys
import platform
import pywinstyles

VERSION = "v2.4"

def apply_theme_to_titlebar(root):
    if platform.system() != "Windows":
        return
        
    version = sys.getwindowsversion()
    
    if version.major == 10 and version.build >= 22000:
        # Windows 11
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        # Windows 10
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")
        # Force update title bar
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

def apply_font_settings(root, style):
    default_font = ("Segoe UI", 9)
    
    # Configure all widgets before updating
    style.configure(".", font=default_font)
    for widget in ["TLabel", "TButton", "TCheckbutton", "TRadiobutton", 
                  "TCombobox", "TEntry", "Treeview"]:
        style.configure(widget, font=default_font)

    # Configure custom button style for both themes
    style.configure("Large.Accent.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   padding=(20, 10))

    # Apply font to root and force update
    root.option_add("*font", default_font)
    root.update()

def toggle_theme_callback(root):
    style = ttk.Style()
    
    # Toggle theme first
    sv_ttk.toggle_theme()
    
    # Apply fonts immediately after theme change
    apply_font_settings(root, style)
    
    # Update title bar
    apply_theme_to_titlebar(root)
    
    # Update log colors if log_text exists
    if hasattr(root, 'log_text'):
        root.update_idletasks()  # Force update
        update_log_colors(root.log_text)

def main():
    root = tk.Tk()
    root.title("SMWC Downloader & Patcher")
    root.geometry("900x850")
    
    # Initial setup
    style = ttk.Style()
    sv_ttk.USE_FONT_CONFIG = True
    sv_ttk.set_theme("dark")
    
    # Configure fonts after theme
    apply_font_settings(root, style)
    
    # Apply title bar theme immediately after dark theme is set
    apply_theme_to_titlebar(root)
    
    # Setup UI and run - pass version to setup_ui
    download_button = setup_ui(root, run_pipeline, toggle_theme_callback, VERSION)
    
    # Store button reference for pipeline access
    root.download_button = download_button
    
    root.mainloop()

if __name__ == "__main__":
    main()
