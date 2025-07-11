import tkinter as tk
from tkinter import ttk
from colors import get_colors

class NavigationBar:
    """Handles the main navigation bar with tabs"""
    
    def __init__(self, root, page_manager):
        self.root = root
        self.page_manager = page_manager
        self.nav_bar = None
        self.tab_refs = []
        self.current_page = "Bulk Download"
        
    def create(self):
        """Create the navigation bar"""
        # Create spacer to push navigation down
        spacer = ttk.Frame(self.root, height=60)
        spacer.pack(side="top", fill="x")
        
        # Get colors from theme
        colors = get_colors()
        nav_height = 60
        
        self.nav_bar = tk.Canvas(
            self.root,
            height=nav_height,
            bg=colors["nav_bg"],  # Use theme-based color
            highlightthickness=0,
        )
        self.nav_bar.pack(fill="x", side="top", pady=0)
        
        # Add tabs - CENTERED VERTICALLY, NO UNDERLINES
        tabs = ["Bulk Download", "Hack History"]
        tab_width = 130
        
        for i, tab in enumerate(tabs):
            x_pos = 10 + (i * tab_width)
            
            tab_id = self.nav_bar.create_text(
                x_pos + 10,
                nav_height // 2,  # CENTERED VERTICALLY (removed -3 offset)
                text=tab,
                font=("Segoe UI", 11, "bold" if tab == self.current_page else "normal"),
                fill=colors["nav_text"],  # Use theme-based text color
                anchor="w"
            )
            
            # Store tab reference WITHOUT underline_id
            self.tab_refs.append({
                "name": tab,
                "text_id": tab_id,
                "x": x_pos,
                "width": tab_width
            })
            
            self.nav_bar.tag_bind(tab_id, "<Button-1>", lambda e, t=tab: self.show_page(t))
            self.nav_bar.tag_bind(tab_id, "<Enter>", lambda e: self.nav_bar.config(cursor="hand2"))
            self.nav_bar.tag_bind(tab_id, "<Leave>", lambda e: self.nav_bar.config(cursor=""))
    
    def show_page(self, page_name):
        """Switch to a specific page"""
        self.current_page = page_name
        self.page_manager.show_page(page_name)
        self._update_tab_styles(page_name)
    
    def _update_tab_styles(self, active_page):
        """Update tab styling based on active page - NO UNDERLINES"""
        colors = get_colors()  # Get current theme colors
        
        for tab_ref in self.tab_refs:
            # Update text style - only font weight changes for active state
            self.nav_bar.itemconfig(
                tab_ref["text_id"],
                font=("Segoe UI", 11, "bold" if tab_ref["name"] == active_page else "normal"),
                fill=colors["nav_text"]  # Update text color for theme
            )
            # NO UNDERLINE LOGIC - removed all underline handling
    
    def update_theme(self):
        """Update navigation bar colors when theme changes"""
        colors = get_colors()
        if self.nav_bar:
            self.nav_bar.configure(bg=colors["nav_bg"])
            # Update all text colors
            self._update_tab_styles(self.current_page)