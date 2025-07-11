import tkinter as tk
from tkinter import ttk
from colors import get_colors
import sv_ttk

class NavigationBar:
    """Handles the main navigation bar with tabs"""
    
    def __init__(self, root, page_manager, toggle_theme_callback=None):
        self.root = root
        self.page_manager = page_manager
        self.toggle_theme_callback = toggle_theme_callback
        self.nav_bar = None
        self.tab_refs = []
        self.theme_frame = None  # ADDED: Store reference to theme frame
        self.moon_label = None   # ADDED: Store reference to moon label
        self.current_page = "Bulk Download"
        
    def create(self):
        """Create the navigation bar"""
        # Get colors from theme
        colors = get_colors()
        nav_height = 60
        
        self.nav_bar = tk.Canvas(
            self.root,
            height=nav_height,
            bg=colors["nav_bg"],
            highlightthickness=0,
        )
        self.nav_bar.pack(fill="x", side="top", pady=0)
        
        # Add tabs - CENTERED VERTICALLY, NO UNDERLINES
        tabs = ["Bulk Download", "Hack History"]
        tab_width = 140
        
        for i, tab in enumerate(tabs):
            x_pos = 20 + (i * tab_width)
            
            tab_id = self.nav_bar.create_text(
                x_pos + 10,
                nav_height // 2,
                text=tab,
                font=("Segoe UI", 11, "bold" if tab == self.current_page else "normal"),
                fill=colors["nav_text"],
                anchor="w"
            )
            
            self.tab_refs.append({
                "name": tab,
                "text_id": tab_id,
                "x": x_pos,
                "width": tab_width
            })
            
            self.nav_bar.tag_bind(tab_id, "<Button-1>", lambda e, t=tab: self.show_page(t))
            self.nav_bar.tag_bind(tab_id, "<Enter>", lambda e: self.nav_bar.config(cursor="hand2"))
            self.nav_bar.tag_bind(tab_id, "<Leave>", lambda e: self.nav_bar.config(cursor=""))
        
        # FIXED: Dynamic positioning for toggle
        if self.toggle_theme_callback:
            colors = get_colors()
            
            # Create toggle first with default position
            self.theme_frame = tk.Frame(
                self.root,
                bg=colors["toggle_bg"]
            )
            
            theme_switch = ttk.Checkbutton(
                self.theme_frame,
                style="Switch.TCheckbutton",
                command=lambda: self.toggle_theme_callback(self.root),
                takefocus=False
            )
            theme_switch.pack(side="left")
            theme_switch.state(['selected'] if sv_ttk.get_theme() == "dark" else [])
            
            self.moon_label = tk.Label(
                self.theme_frame, 
                text="🌙",
                font=("Segoe UI Emoji", 12),
                bg=colors["toggle_bg"],
                fg=colors["nav_text"]
            )
            self.moon_label.pack(side="left", padx=(2, 8))
            
            # ADDED: Bind to configure event to update position when window resizes
            self.nav_bar.bind("<Configure>", self._update_toggle_position)
            
            # Initial position setup
            self.root.after(100, self._update_toggle_position)
    
    def show_page(self, page_name):
        """Switch to a specific page"""
        self.current_page = page_name
        self.page_manager.show_page(page_name)
        self._update_tab_styles(page_name)
    
    def _update_tab_styles(self, active_page):
        """Update tab styling based on active page"""
        colors = get_colors()
        
        for tab_ref in self.tab_refs:
            self.nav_bar.itemconfig(
                tab_ref["text_id"],
                font=("Segoe UI", 11, "bold" if tab_ref["name"] == active_page else "normal"),
                fill=colors["nav_text"]
            )
    
    def update_theme(self):
        """Update navigation bar colors when theme changes"""
        colors = get_colors()
        if self.nav_bar:
            self.nav_bar.configure(bg=colors["nav_bg"])
            self._update_tab_styles(self.current_page)
            
            # Update toggle background rectangle
            for item in self.nav_bar.find_withtag("toggle_bg"):
                self.nav_bar.itemconfig(item, fill=colors["toggle_bg"], outline=colors["toggle_bg"])
            
            # FIXED: Update theme frame and moon label to match rectangle background
            if self.theme_frame:
                self.theme_frame.configure(bg=colors["toggle_bg"])
            
            if self.moon_label:
                self.moon_label.configure(bg=colors["toggle_bg"], fg=colors["nav_text"])
    
    # ADDED: Method to update toggle position dynamically
    def _update_toggle_position(self, event=None):
        """Update toggle position to stay on the right edge"""
        if hasattr(self, 'theme_frame') and self.theme_frame:
            # Get current canvas width
            canvas_width = self.nav_bar.winfo_width()
            nav_height = 60
            
            # Rectangle coordinates
            rect_width = 128
            rect_height = 100
            rect_x = canvas_width - rect_width  # CHANGED: Removed -10 padding
            rect_y = (nav_height - rect_height) // 2
            
            # Delete old rectangle and create new one
            self.nav_bar.delete("toggle_bg")
            colors = get_colors()
            self.nav_bar.create_rectangle(
                rect_x, rect_y,
                rect_x + rect_width, rect_y + rect_height,
                fill=colors["toggle_bg"],
                outline=colors["toggle_bg"],
                tags="toggle_bg"
            )
            
            # Update toggle button position
            toggle_x = canvas_width - 10  # CHANGED: Reduced from -20 to -10
            self.nav_bar.delete("toggle_window")
            self.nav_bar.create_window(
                toggle_x, nav_height // 2, 
                window=self.theme_frame, 
                anchor="e",
                tags="toggle_window"
            )