from tkinter import ttk

class PageManager:
    """Manages page switching and content display"""
    
    def __init__(self, content_frame):
        self.content_frame = content_frame
        self.pages = {}
        self.current_page = None
    
    def add_page(self, name, page_frame):
        """Add a page to the manager"""
        self.pages[name] = page_frame
    
    def show_page(self, page_name):
        """Show a specific page and hide others"""
        # Hide all pages
        for name, frame in self.pages.items():
            frame.pack_forget()
        
        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill="both", expand=True)
            self.current_page = page_name
    
    def get_current_page(self):
        """Get the currently displayed page"""
        return self.current_page