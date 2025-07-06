# main.py
import tkinter as tk
from tkinter import ttk
from api_pipeline import run_pipeline
from ui import setup_ui, update_log_colors
import sys
import platform
import os

# Optional UI enhancements
# Initialize the global variable
SV_TTK_AVAILABLE = False

try:
    import sv_ttk
    # Check if sv_ttk is compatible with current Tk version
    try:
        tk_version = tk.TkVersion
        if tk_version >= 8.6:
            SV_TTK_AVAILABLE = True
        else:
            print(f"Warning: sv_ttk requires Tk 8.6 or newer, but you have {tk_version}")
            SV_TTK_AVAILABLE = False
    except Exception:
        # If we can't determine Tk version, assume it's compatible
        SV_TTK_AVAILABLE = True
except ImportError:
    SV_TTK_AVAILABLE = False

# Only import platform-specific modules when needed
pywinstyles = None
if platform.system() == "Windows":
    try:
        import pywinstyles
    except ImportError:
        pywinstyles = None

def get_theme_mode():
    """Get current theme mode (dark or light)"""
    try:
        if SV_TTK_AVAILABLE:
            return sv_ttk.get_theme()
        else:
            # Default to light if sv_ttk not available
            return "light"
    except Exception:
        return "light"

def apply_theme_to_titlebar(root):
    """Apply theme to window titlebar based on platform"""
    system = platform.system()
    is_dark = get_theme_mode() == "dark"
    
    if system == "Darwin":
        # macOS appearance mode
        # This only works on macOS 10.14+ (Mojave and later)
        try:
            # For macOS, we set the appearance at the OS level
            # Note: This requires macOS 10.14+ to work properly
            if is_dark:
                root.tk.call('::tk::unsupported::MacWindowStyle', 'appearance', root, 'dark')
            else:
                root.tk.call('::tk::unsupported::MacWindowStyle', 'appearance', root, 'light')
        except Exception:
            # Older macOS versions don't support this, so we silently ignore
            pass
    
    elif system == "Windows" and pywinstyles is not None:
        # Windows appearance mode
        try:
            version = sys.getwindowsversion()
            
            if version.major == 10 and version.build >= 22000:
                # Windows 11
                pywinstyles.change_header_color(root, "#1c1c1c" if is_dark else "#fafafa")
            elif version.major == 10:
                # Windows 10
                pywinstyles.apply_style(root, "dark" if is_dark else "normal")
                # Force update title bar
                root.wm_attributes("-alpha", 0.99)
                root.wm_attributes("-alpha", 1)
        except Exception as e:
            print(f"Warning: Could not apply window style: {e}")
    
    # For Linux or other systems, we don't do anything special

def apply_font_settings(root, style):
    # Use platform-appropriate fonts with consistent sizes
    if platform.system() == "Darwin":  # macOS
        # Use SF Pro Text on macOS with smaller sizes
        font_family = "SF Pro Text"
        default_size = 10  # Reduced from 12
        button_size = 11  # Reduced from 13
    else:  # Windows/Linux
        # Use Segoe UI on Windows/Linux with consistent sizes
        font_family = "Segoe UI"
        default_size = 9
        button_size = 10
    
    # Create the font tuples
    default_font = (font_family, default_size)
    button_font = (font_family, button_size, "bold")
    
    # Reset all widget styles to avoid any theme inheritance issues
    style.theme_use(style.theme_use())  # This reloads the current theme
    
    # Configure all widgets with explicit font settings
    style.configure(".", font=default_font)
    
    # Set font for each widget type individually to ensure consistency
    for widget_type in ["TLabel", "TButton", "TCheckbutton", "TRadiobutton", 
                       "TCombobox", "TEntry", "Treeview", "Text"]:
        style.configure(widget_type, font=default_font)
    
    # Configure special styles that might have different fonts
    style.configure("TNotebook.Tab", font=default_font)
    style.configure("Treeview.Heading", font=default_font)
    style.configure("TScale", font=default_font)
    
    # Configure custom button style for both themes with explicit font and width
    style.configure("Large.Accent.TButton", 
                   font=button_font,
                   padding=(20, 10),
                   width=20)  # Set explicit width for consistency
    
    # Apply fonts globally to all Tk and Ttk widgets
    root.option_add("*Font", default_font)
    root.option_add("*font", default_font)
    root.option_add("*Text.font", default_font)
    root.option_add("*Listbox.font", default_font)
    root.option_add("*Entry.font", default_font)
    root.option_add("*Menu.font", default_font)
    
    # Apply directly to any existing Text widgets
    for widget in root.winfo_children():
        try:
            widget.configure(font=default_font)
        except:
            pass  # Ignore widgets that don't have a font option
        
        # Try to configure child widgets too
        for child in widget.winfo_children():
            try:
                child.configure(font=default_font)
            except:
                pass  # Ignore widgets that don't have a font option
    
    # Force a complete refresh
    root.update_idletasks()
    root.update()

def toggle_theme_callback(root):
    """Toggle between dark and light theme with consistent font sizes"""
    # Reference the global variable
    global SV_TTK_AVAILABLE
    
    # Create a fixed title font that won't change during theme switching
    if platform.system() == "Darwin":  # macOS
        title_font = ("SF Pro Display", 18, "bold")
    else:  # Windows/Linux
        title_font = ("Segoe UI", 20, "bold")
    
    # First, locate and save the title label
    title_label = None
    title_frame = None
    
    # Find the title label using a more robust approach
    for widget in root.winfo_children():
        for child in widget.winfo_children():
            try:
                # Look for frames that might contain the title
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if (hasattr(grandchild, 'is_title') and grandchild.is_title):
                            title_label = grandchild
                            title_frame = child
                            break
                
                # Also look for direct label (backwards compatibility)
                if ((isinstance(child, tk.Label) and child.cget('text') == "SMWCentral Downloader & Patcher") or
                    (hasattr(child, 'is_title') and child.is_title)):
                    title_label = child
                    break
            except (tk.TclError, AttributeError):
                pass
            
            # If we found the title, no need to continue
            if title_label:
                break
        if title_label:
            break
    
    # Toggle theme if sv_ttk is available
    current_theme = None
    if SV_TTK_AVAILABLE:
        # Store current theme before toggle for later reference
        current_theme = sv_ttk.get_theme()
        
        # Disable sv_ttk's font configuration
        sv_ttk.USE_FONT_CONFIG = False
        
        # Toggle the theme
        sv_ttk.toggle_theme()
        
        # Let theme changes settle
        root.update_idletasks()
    
    # Apply general font settings
    style = ttk.Style()
    apply_font_settings(root, style)
    
    # Handle the title label specifically
    if title_label:
        # Save the original font if available
        original_font = getattr(title_label, 'font_spec', title_font)
        
        # Force the title font to be exactly what we want
        title_label.configure(font=original_font)
        
        # Update the background color to match the new theme
        # Get the root background directly instead of style lookup
        new_bg = root.cget("background")
        title_label.configure(background=new_bg)
        
        # Force update to ensure changes are applied
        root.update_idletasks()
    
    # Update title bar appearance
    apply_theme_to_titlebar(root)
    
    # Update log colors if needed
    if hasattr(root, 'log_text'):
        root.update_idletasks()
        update_log_colors(root.log_text)
    
    # Save current button size before theme change
    button_width = None
    if hasattr(root, 'download_button'):
        try:
            # Get the current width in pixels (actual rendered size)
            button_width = root.download_button.winfo_width()
        except:
            pass
    
    # Apply button styling with consistent settings
    if hasattr(root, 'download_button'):
        # Get the appropriate font
        button_font = ("SF Pro Text" if platform.system() == "Darwin" else "Segoe UI", 
                     11 if platform.system() == "Darwin" else 10, 
                     "bold")
        
        # Configure style with light mode properties that we want to keep
        style.configure("Large.Accent.TButton", 
                       font=button_font,
                       padding=(20, 10),
                       width=20)  # Set explicit width
        
        # Force button refresh with the style
        root.download_button.configure(style="Large.Accent.TButton")
        root.update_idletasks()
        
        # If we captured a width and we're going to light mode, ensure it maintains that width
        if button_width and get_theme_mode() == "light":
            # Schedule a fix after the theme has fully settled
            def fix_button_width():
                current_width = root.download_button.winfo_width()
                if current_width < button_width:
                    # If smaller than dark mode, apply explicit width
                    style.configure("Large.Accent.TButton", width=20)
                    root.download_button.configure(style="Large.Accent.TButton")
                    root.update_idletasks()
            
            # Run with a delay to ensure theme changes have settled
            root.after(50, fix_button_width)
    
    # Schedule a final update of the title to ensure it's correct
    # We use multiple approaches to ensure it works reliably
    if title_label:
        def ensure_title_appearance():
            # Apply the font again to override any theme-based changes
            original_font = getattr(title_label, 'font_spec', title_font)
            title_label.configure(font=original_font)
            
            # Update background color based on current theme (direct from root)
            new_bg = root.cget("background")
            title_label.configure(background=new_bg)
            
            # Force update
            root.update_idletasks()
        
        # Schedule with multiple delays to ensure it runs after all theme changes are complete
        root.after(50, ensure_title_appearance)
        root.after(150, ensure_title_appearance)

def main():
    # Reference the global variable
    global SV_TTK_AVAILABLE
    
    root = tk.Tk()
    root.title("SMWC Downloader & Patcher v2.3")
    root.geometry("900x850")
    
    # Initial setup
    style = ttk.Style()
    
    # Define title font at the start so it's consistent
    if platform.system() == "Darwin":  # macOS
        title_font = ("SF Pro Display", 18, "bold")
    else:  # Windows/Linux
        title_font = ("Segoe UI", 20, "bold")
    
    # Store as a global property for consistent access
    root.title_font_spec = title_font
    
    # Apply sv_ttk theme if available and compatible with Tk version
    if SV_TTK_AVAILABLE:
        try:
            # Explicitly disable sv_ttk font configuration
            sv_ttk.USE_FONT_CONFIG = False
            
            # Store the default widget font before applying theme
            original_font = style.lookup("TLabel", "font")
            
            # Set theme
            sv_ttk.set_theme("dark")
            
            # Brief pause to let the theme apply
            root.update_idletasks()
            
            # Reset any potential font changes from sv_ttk
            if original_font:
                style.configure(".", font=original_font)
                
        except Exception as e:
            print(f"Warning: Could not apply sv_ttk theme: {e}")
            SV_TTK_AVAILABLE = False  # Disable if it fails
    
    # Configure fonts after theme - this ensures our font settings override theme defaults
    apply_font_settings(root, style)
    
    # Apply title bar theme immediately after dark theme is set
    apply_theme_to_titlebar(root)
        
    # Pre-configure the title style to ensure consistency
    style.configure("Title.TLabel", font=title_font)
    
    # Setup UI and run - this will return the button reference
    download_button = setup_ui(root, run_pipeline, toggle_theme_callback)
    
    # Store button reference for pipeline access
    root.download_button = download_button
    
    # Make sure button has appropriate styling
    style.configure("Large.Accent.TButton", 
                   font=("SF Pro Text", 11, "bold") if platform.system() == "Darwin" else ("Segoe UI", 10, "bold"),
                   padding=(20, 10),
                   width=20)  # Set explicit width
    
    # Schedule an extra update for the button width to ensure consistency
    def ensure_button_width():
        if hasattr(root, 'download_button'):
            root.download_button.configure(width=20)
            # Force the style to be applied with correct width
            style.configure("Large.Accent.TButton", width=20)
            root.download_button.configure(style="Large.Accent.TButton")
            root.update_idletasks()
            
    # Schedule with a slight delay to ensure all widgets are rendered
    root.after(100, ensure_button_width)
    
    # Do one final update to ensure title font is applied
    # Find and update the title label after UI is created
    for widget in root.winfo_children():
        for child in widget.winfo_children():
            try:
                # Look for our title label
                if ((isinstance(child, tk.Label) and child.cget('text') == "SMWCentral Downloader & Patcher") or
                    (hasattr(child, 'is_title') and child.is_title)):
                    # Apply the title font directly
                    child.configure(font=title_font)
                    break
                
                # Look in nested frames too
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if (hasattr(grandchild, 'is_title') and grandchild.is_title):
                            grandchild.configure(font=title_font)
                            break
            except (tk.TclError, AttributeError):
                pass
    
    root.update_idletasks()
    root.mainloop()

if __name__ == "__main__":
    main()
