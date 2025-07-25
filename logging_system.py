import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import sv_ttk
from colors import get_colors

class LoggingSystem:
    """Centralized logging system with theme support"""
    
    def __init__(self, font=("Segoe UI", 9)):
        self.log_text = None
        self.log_level = "Information"
        self.font = font
        self.history = []
        self._updating_display = False  # Flag to prevent recursive updates
    
    def setup(self, parent):
        """Create and configure the log text widget"""
        # Create log text widget
        self.log_text = scrolledtext.ScrolledText(
            parent, height=18, wrap="word",
            state="disabled",
            bg="#2b2b2b" if sv_ttk.get_theme() == "dark" else "#ffffff",
            fg="#e0e0e0" if sv_ttk.get_theme() == "dark" else "#000000"
        )
        
        # Configure tags
        self.update_colors()
        
        return self.log_text
    
    def setup_log_with_controls(self, parent):
        """Create just the log text widget (controls are handled by layout)"""
        self.log_text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            height=20,
            font=self.font,
            state="disabled"
        )
        
        # Apply initial colors
        self.update_colors()
        
        return self.log_text

    def update_colors(self):
        """Update log colors based on current theme"""
        if not self.log_text:
            return
            
        try:
            colors = get_colors()
            
            self.log_text.configure(
                bg=colors["log_bg"], 
                fg=colors["log_fg"]
            )
            self.log_text.tag_configure("error", foreground=colors["error"], font=(self.font[0], self.font[1], "italic"))
            self.log_text.tag_configure("warning", foreground=colors["warning"], font=(self.font[0], self.font[1], "italic")) 
            self.log_text.tag_configure("debug", foreground=colors["debug"])
            self.log_text.tag_configure("filter_info", foreground=colors["filter_info"], font=(self.font[0], self.font[1], "italic"))
            self.log_text.tag_configure("applying", foreground=colors["applying"], font=(self.font[0], self.font[1], "italic"))
        except tk.TclError:
            # Widget was destroyed or doesn't exist
            pass
    
    def should_log(self, level):
        """Determine if a message should be displayed based on current log level"""
        if self.log_level == "Error":
            return level.lower() == "error"  # Only show error messages
        if level.lower() == "error":
            return True  # Always show errors in any log level
        if self.log_level == "Verbose":
            return True  # Show all messages in Verbose mode
        if self.log_level == "Debug":
            return level.lower() != "verbose"  # Show everything except verbose in Debug mode
        return level.lower() in ["information", "warning", "error", "applying"]  # Information mode
    
    def log(self, message, level="Information"):
        """Log a message with appropriate styling"""
        if self._updating_display:
            return  # Skip logging during display update to prevent recursion
            
        if not self.log_text:
            # Store in history even if widget isn't available yet
            self.history.append((level, message))
            return
        
        # Store in history
        self.history.append((level, message))
        
        # Check if we should display this message
        if not self.should_log(level):
            return
        
        # Add message with appropriate tag
        try:
            self.log_text.configure(state="normal")
            
            tag = None
            if level.lower() == "error":
                tag = "error"
            elif level.lower() == "warning":
                tag = "warning"
            elif level.lower() == "debug":
                tag = "debug"
            elif level.lower() == "applying":
                tag = "applying"
            
            if tag:
                self.log_text.insert(tk.END, message + "\n", tag)
            else:
                self.log_text.insert(tk.END, message + "\n")
            
            self.log_text.configure(state="disabled")
            self.log_text.see(tk.END)
            self.log_text.update_idletasks()  # Use update_idletasks instead of update
        except tk.TclError:
            # Widget was destroyed or doesn't exist
            pass
    
    def clear_log(self):
        """Clear the log text AND history"""
        # Clear both the visible text AND the stored history
        self.history = []  # Clear stored log entries
        
        if self.log_text:
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
    
    def set_log_level(self, level):
        """Change log level and refresh display"""
        # If it's the same level, do nothing
        if level == self.log_level:
            return
            
        self.log_level = level
        
        # Clear and redisplay messages
        if not self.log_text:
            return
        
        try:
            # Set flag to prevent recursive logging
            self._updating_display = True
            
            self.log_text.configure(state="normal")
            self.log_text.delete(1.0, tk.END)
            
            # Add informational message for Error level
            if level == "Error":
                self.log_text.insert(tk.END, "Showing only error messages. Switch back to Information for all messages.\n\n", "filter_info")
            
            self.log_text.configure(state="disabled")
            
            # Display messages directly without calling log() to avoid recursion
            for stored_level, message in self.history:
                if self.should_log(stored_level):
                    try:
                        self.log_text.configure(state="normal")
                        
                        tag = None
                        if stored_level.lower() == "error":
                            tag = "error"
                        elif stored_level.lower() == "warning":
                            tag = "warning"
                        elif stored_level.lower() == "debug":
                            tag = "debug"
                        elif stored_level.lower() == "applying":
                            tag = "applying"
                        
                        if tag:
                            self.log_text.insert(tk.END, message + "\n", tag)
                        else:
                            self.log_text.insert(tk.END, message + "\n")
                        
                        self.log_text.configure(state="disabled")
                    except tk.TclError:
                        break
            
            # Ensure we see the end
            self.log_text.see(tk.END)
            
        except tk.TclError:
            # Widget was destroyed or doesn't exist
            pass
        finally:
            # Reset flag
            self._updating_display = False
