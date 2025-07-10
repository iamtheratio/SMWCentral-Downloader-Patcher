from tkinter import ttk
from colors import get_colors

class VersionDisplay:
    """Handles version label display"""
    
    def __init__(self, root, version):
        self.root = root
        self.version = version
        self.version_label = None
    
    def create(self):
        """Create version display label"""
        if not self.version:
            return
            
        self.version_label = ttk.Label(
            self.root, 
            text=self.version, 
            font=("Segoe UI", 8, "italic")
        )
        self.version_label.place(relx=1.0, rely=1.0, anchor="se", x=-26, y=-10)
        
        # Set initial color
        colors = get_colors()
        self.version_label.configure(foreground=colors["version_label"])
        
        # Store reference
        self.root.version_label = self.version_label
    
    def update_colors(self):
        """Update colors based on current theme"""
        if self.version_label:
            colors = get_colors()
            self.version_label.configure(foreground=colors["version_label"])