import tkinter as tk
from tkinter import ttk
from api_pipeline import run_pipeline
from ui import setup_ui, update_log_colors
import sv_ttk
import sys
import platform
import pywinstyles

VERSION = "v3.0"

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
    
    # FIXED: Force disable sv_ttk font management to prevent conflicts
    sv_ttk.USE_FONT_CONFIG = False
    
    # Configure all widgets before updating
    style.configure(".", font=default_font)
    for widget in ["TLabel", "TButton", "TCheckbutton", "TRadiobutton", 
                  "TCombobox", "TEntry"]:  # REMOVED: "Treeview" from this list
        style.configure(widget, font=default_font)

    # ADDED: Configure Treeview with larger font and row height for better readability
    style.configure("Treeview", 
                   font=("Segoe UI", 10),  # Larger font for table
                   rowheight=25)  # More padding
    
    style.configure("Treeview.Heading", 
                   font=("Segoe UI", 10, "bold"))  # Bold headers

    # Configure custom button style for both themes
    style.configure("Large.Accent.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   padding=(20, 10))
    
    # CHANGED: Configure the default Switch style to use toggle background
    from colors import get_colors
    colors = get_colors()
    
    # Configure Switch.TCheckbutton to use toggle background
    style.configure("Switch.TCheckbutton",
                   background=colors["toggle_bg"])

    # Apply font to root and force update
    root.option_add("*font", default_font)
    root.update()

def toggle_theme_callback(root):
    style = ttk.Style()
    
    # Toggle theme first
    sv_ttk.toggle_theme()
    
    # ADDED: Reapply font settings after theme change to ensure consistency
    apply_font_settings(root, style)
    
    # Get new colors immediately
    from colors import get_colors
    colors = get_colors()
    
    # Update all toggle-related colors TOGETHER without calling update()
    style.configure("Switch.TCheckbutton", background=colors["toggle_bg"])
    
    # Update navigation elements immediately without intermediate updates
    if hasattr(root, 'navigation'):
        if hasattr(root.navigation, 'theme_frame') and root.navigation.theme_frame:
            root.navigation.theme_frame.configure(bg=colors["toggle_bg"])
        
        if hasattr(root.navigation, 'moon_label') and root.navigation.moon_label:
            root.navigation.moon_label.configure(bg=colors["toggle_bg"], fg=colors["nav_text"])
        
        # Update navigation without calling update methods that cause flashing
        if root.navigation.nav_bar:
            root.navigation.nav_bar.configure(bg=colors["nav_bg"])
            root.navigation._update_tab_styles(root.navigation.current_page)
            
            # Update toggle background rectangle
            for item in root.navigation.nav_bar.find_withtag("toggle_bg"):
                root.navigation.nav_bar.itemconfig(item, fill=colors["toggle_bg"], outline=colors["toggle_bg"])
    
    # Update title bar
    apply_theme_to_titlebar(root)
    
    # Update log colors if log_text exists
    if hasattr(root, 'log_text'):
        update_log_colors(root.log_text)
    
    # Single update at the very end
    root.update_idletasks()

def clear_log_shortcut(root):
    """Handle Ctrl+L keyboard shortcut"""
    if hasattr(root, 'log_text'):
        log_text = root.log_text
        log_text.config(state="normal")
        log_text.delete(1.0, tk.END)
        log_text.config(state="disabled")

def main():
    root = tk.Tk()
    root.title("SMWC Downloader & Patcher")
    root.geometry("1000x900")
    
    # Initial setup
    style = ttk.Style()
    # MOVED: Set USE_FONT_CONFIG to False BEFORE setting theme
    sv_ttk.USE_FONT_CONFIG = False
    sv_ttk.set_theme("dark")
    
    # Configure fonts after theme
    apply_font_settings(root, style)
    
    # Apply title bar theme immediately after dark theme is set
    apply_theme_to_titlebar(root)
    
    # Setup UI and run - pass version to setup_ui
    download_button = setup_ui(root, run_pipeline, toggle_theme_callback, VERSION)
    
    # Store button reference for pipeline access
    root.download_button = download_button
    
    # Add keyboard shortcut for clearing log
    root.bind("<Control-l>", lambda e: clear_log_shortcut(root))
    
    root.mainloop()

if __name__ == "__main__":
    main()
