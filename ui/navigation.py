import tkinter as tk
from tkinter import ttk
from colors import get_colors
import sv_ttk

class NavigationBar:
    """Handles the main navigation bar with tabs"""
    
    def __init__(self, root, page_manager, toggle_theme_callback=None):  # ONLY ADDED toggle_theme_callback
        self.root = root
        self.page_manager = page_manager
        self.toggle_theme_callback = toggle_theme_callback  # ONLY ADDED THIS LINE
        self.nav_bar = None
        self.tab_refs = []
        self.current_page = "Bulk Download"
        
    def create(self):
        """Create the navigation bar"""
        # REMOVED: Create spacer to push navigation down
        # spacer = ttk.Frame(self.root, height=60)
        # spacer.pack(side="top", fill="x")
        
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
        
        # ONLY ADDED: Embed existing theme toggle in navigation bar
        if self.toggle_theme_callback:
            theme_frame = ttk.Frame(self.root)
            
            theme_switch = ttk.Checkbutton(
                theme_frame,
                style="Switch.TCheckbutton",
                command=lambda: self.toggle_theme_callback(self.root)
            )
            theme_switch.pack(side="left")
            theme_switch.state(['selected'] if sv_ttk.get_theme() == "dark" else [])
            
            moon_label = ttk.Label(
                theme_frame, 
                text="🌙",
                font=("Segoe UI Emoji", 12),
            )
            moon_label.pack(side="left", padx=(2, 0))
            
            # Embed in canvas
            self.nav_bar.create_window(
                870, nav_height // 2, window=theme_frame, anchor="e"
            )
    
    # EVERYTHING ELSE UNCHANGED
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