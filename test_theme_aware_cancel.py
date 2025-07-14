#!/usr/bin/env python3
"""
Test script for the enhanced theme-aware cancel button
"""

import tkinter as tk
from tkinter import ttk
import sv_ttk
import sys
import os

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(__file__))
from colors import get_colors

def test_theme_aware_cancel_button():
    """Test the theme-aware cancel button implementation"""
    
    # Create test window
    root = tk.Tk()
    root.title("Theme-Aware Cancel Button Test")
    root.geometry("500x400")
    
    # Set initial theme
    sv_ttk.set_theme("dark")
    style = ttk.Style()
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill="both", expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="Theme-Aware Cancel Button Test", 
                           font=("Segoe UI", 14, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Current theme label
    theme_label = ttk.Label(main_frame, text="Current Theme: Dark")
    theme_label.pack(pady=(0, 10))
    
    # Current state label
    state_label = ttk.Label(main_frame, text="Current State: Download Mode")
    state_label.pack(pady=(0, 10))
    
    # Test button (start as ttk button)
    test_button = ttk.Button(main_frame, 
                            text="Download & Patch", 
                            style="Large.Accent.TButton")
    test_button.pack(pady=20)
    
    # Configure Large.Accent.TButton style
    style.configure("Large.Accent.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   padding=(20, 10))
    
    # State tracking
    current_state = {"mode": "download", "button_ref": test_button}
    
    def update_cancel_button_theme():
        """Update cancel button colors for current theme"""
        if (hasattr(current_state["button_ref"], 'config') and 
            current_state["button_ref"].cget('text') == 'Cancel'):
            colors = get_colors()
            current_state["button_ref"].configure(
                bg=colors["cancel_bg"],
                fg=colors["cancel_fg"],
                activebackground=colors["cancel_hover"],
                activeforeground=colors["cancel_fg"]
            )
    
    def toggle_theme():
        """Toggle between light and dark themes"""
        sv_ttk.toggle_theme()
        current_theme = sv_ttk.get_theme()
        theme_label.configure(text=f"Current Theme: {current_theme.title()}")
        
        # Update cancel button colors if in cancel mode
        update_cancel_button_theme()
        
        print(f"Theme changed to: {current_theme}")
        colors = get_colors()
        if current_state["mode"] == "cancel":
            print(f"Cancel button colors updated:")
            print(f"  Background: {colors['cancel_bg']}")
            print(f"  Foreground: {colors['cancel_fg']}")
            print(f"  Hover: {colors['cancel_hover']}")
    
    def toggle_button_state():
        """Toggle between download and cancel modes"""
        if current_state["mode"] == "download":
            # Switch to cancel mode - replace ttk button with tk button
            colors = get_colors()
            
            # Store button info
            original_parent = current_state["button_ref"].master
            original_pack_info = current_state["button_ref"].pack_info()
            
            # Destroy ttk button
            current_state["button_ref"].destroy()
            
            # Create tk button for cancel mode
            current_state["button_ref"] = tk.Button(
                original_parent,
                text="Cancel",
                font=("Segoe UI", 10, "bold"),
                bg=colors["cancel_bg"],
                fg=colors["cancel_fg"],
                activebackground=colors["cancel_hover"],
                activeforeground=colors["cancel_fg"],
                relief="flat",
                borderwidth=0,
                highlightthickness=0,  # Remove focus outline
                takefocus=0,           # Disable focus
                cursor="hand2",        # Hand cursor on hover
                command=lambda: print("Cancel button clicked!")
            )
            
            # Apply original pack configuration
            current_state["button_ref"].pack(**original_pack_info)
            
            state_label.configure(text="Current State: Cancel Mode (tk.Button with custom colors)")
            current_state["mode"] = "cancel"
            toggle_btn.configure(text="Switch to Download Mode")
            
            print("Switched to cancel mode:")
            print(f"  Background: {colors['cancel_bg']}")
            print(f"  Foreground: {colors['cancel_fg']}")
            print(f"  No focus outline, no keyboard focus")
            
        else:
            # Switch to download mode - replace tk button with ttk button
            # Store button info
            original_parent = current_state["button_ref"].master
            original_pack_info = current_state["button_ref"].pack_info()
            
            # Destroy tk button
            current_state["button_ref"].destroy()
            
            # Create ttk button for download mode
            current_state["button_ref"] = ttk.Button(
                original_parent,
                text="Download & Patch",
                style="Large.Accent.TButton",
                command=lambda: print("Download button clicked!")
            )
            
            # Apply original pack configuration
            current_state["button_ref"].pack(**original_pack_info)
            
            state_label.configure(text="Current State: Download Mode (ttk.Button with theme styling)")
            current_state["mode"] = "download"
            toggle_btn.configure(text="Switch to Cancel Mode")
            
            print("Switched to download mode (ttk button)")
    
    # Control buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)
    
    toggle_btn = ttk.Button(button_frame, 
                           text="Switch to Cancel Mode",
                           command=toggle_button_state)
    toggle_btn.pack(side="left", padx=(0, 10))
    
    theme_btn = ttk.Button(button_frame, 
                          text="Toggle Theme",
                          command=toggle_theme)
    theme_btn.pack(side="left")
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="1. Click 'Switch to Cancel Mode' to see the red cancel button\n"
                                "2. Click 'Toggle Theme' to switch between light/dark modes\n"
                                "3. Notice how cancel button colors adapt to the theme\n\n"
                                "Cancel button features:\n"
                                "• Theme-aware colors (different for light/dark)\n"
                                "• No focus outline or keyboard focus\n"
                                "• Proper hover effects\n"
                                "• Automatic color updates on theme change",
                           justify="left")
    instructions.pack(pady=20)
    
    print("Theme-Aware Cancel Button Test")
    print("=" * 50)
    print("✓ Dark mode cancel colors:")
    
    sv_ttk.set_theme("dark")
    colors = get_colors()
    print(f"  Background: {colors['cancel_bg']}")
    print(f"  Foreground: {colors['cancel_fg']}")
    print(f"  Hover: {colors['cancel_hover']}")
    
    print("✓ Light mode cancel colors:")
    sv_ttk.set_theme("light")
    colors = get_colors()
    print(f"  Background: {colors['cancel_bg']}")
    print(f"  Foreground: {colors['cancel_fg']}")
    print(f"  Hover: {colors['cancel_hover']}")
    
    # Reset to dark for test
    sv_ttk.set_theme("dark")
    
    print("\nTest the button modes and theme switching!")
    
    root.mainloop()

if __name__ == "__main__":
    test_theme_aware_cancel_button()
