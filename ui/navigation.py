import tkinter as tk
from tkinter import ttk
from colors import get_colors

class NavigationBar:
    """Handles the main navigation bar with tabs"""
    
    UNDERLINE_SPACING = 20
    
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
        
        # Create navigation canvas
        accent_color = "#66c2ff"
        nav_height = 60
        
        self.nav_bar = tk.Canvas(
            self.root,
            height=nav_height,
            bg=accent_color,
            highlightthickness=0,
        )
        self.nav_bar.pack(fill="x", side="top", pady=0)
        
        # Add tabs
        tabs = ["Bulk Download", "Hack History"]
        tab_width = 130
        
        for i, tab in enumerate(tabs):
            x_pos = 10 + (i * tab_width)
            
            tab_id = self.nav_bar.create_text(
                x_pos + 10,
                nav_height // 2 - 3,
                text=tab,
                font=("Segoe UI", 11, "bold" if tab == self.current_page else "normal"),
                fill="black",
                anchor="w"
            )
            
            text_bbox = self.nav_bar.bbox(tab_id)
            text_width = text_bbox[2] - text_bbox[0]
            text_left = text_bbox[0]
            
            underline_id = None
            if tab == self.current_page:
                underline_id = self.nav_bar.create_line(
                    text_left, nav_height - self.UNDERLINE_SPACING,
                    text_left + text_width, nav_height - self.UNDERLINE_SPACING,
                    width=3,
                    fill="black"
                )
            
            self.tab_refs.append({
                "name": tab,
                "text_id": tab_id,
                "underline_id": underline_id,
                "x": x_pos,
                "width": tab_width,
                "text_left": text_left,
                "text_width": text_width
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
        """Update tab styling based on active page"""
        for tab_ref in self.tab_refs:
            # Update text style
            self.nav_bar.itemconfig(
                tab_ref["text_id"],
                font=("Segoe UI", 11, "bold" if tab_ref["name"] == active_page else "normal")
            )
            
            # Handle underline
            if tab_ref["name"] == active_page:
                text_bbox = self.nav_bar.bbox(tab_ref["text_id"])
                text_width = text_bbox[2] - text_bbox[0]
                text_left = text_bbox[0]
                
                if not tab_ref["underline_id"]:
                    tab_ref["underline_id"] = self.nav_bar.create_line(
                        text_left, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING,
                        text_left + text_width, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING,
                        width=3,
                        fill="black"
                    )
                else:
                    self.nav_bar.coords(
                        tab_ref["underline_id"],
                        text_left, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING,
                        text_left + text_width, self.nav_bar.winfo_height() - self.UNDERLINE_SPACING
                    )
            else:
                if tab_ref["underline_id"]:
                    self.nav_bar.delete(tab_ref["underline_id"])
                    tab_ref["underline_id"] = None