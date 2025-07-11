import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
from datetime import datetime
from hack_data_manager import HackDataManager

class HackHistoryPage:
    """Comprehensive hack history page with filtering and editing"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.data_manager = HackDataManager()
        
        # Filter variables
        self.name_filter = tk.StringVar()
        self.difficulty_filter = tk.StringVar(value="All")
        self.completed_filter = tk.StringVar(value="All")
        self.rating_filter = tk.StringVar(value="All")
        
        # Table data
        self.tree = None
        self.filtered_data = []
        
    def create(self):
        """Create the hack history page"""
        self.frame = ttk.Frame(self.parent, padding=10)
        
        # Title
        ttk.Label(
            self.frame,
            text="Downloaded Hacks History",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 15))
        
        # Create filter section
        self._create_filters()
        
        # Create table section
        self._create_table()
        
        # Load initial data
        self._refresh_table()
        
        return self.frame
    
    def _create_filters(self):
        """Create filter controls"""
        filter_frame = ttk.LabelFrame(self.frame, text="Filters", padding=10)
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # First row of filters
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill="x", pady=(0, 5))
        
        # Name filter
        ttk.Label(row1, text="Name:").pack(side="left", padx=(0, 5))
        name_entry = ttk.Entry(row1, textvariable=self.name_filter, width=20)
        name_entry.pack(side="left", padx=(0, 15))
        name_entry.bind("<KeyRelease>", lambda e: self._apply_filters())
        
        # Difficulty filter
        ttk.Label(row1, text="Difficulty:").pack(side="left", padx=(0, 5))
        difficulties = ["All"] + self.data_manager.get_unique_difficulties()
        diff_combo = ttk.Combobox(row1, textvariable=self.difficulty_filter, 
                                 values=difficulties, state="readonly", width=15)
        diff_combo.pack(side="left", padx=(0, 15))
        diff_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Second row of filters
        row2 = ttk.Frame(filter_frame)
        row2.pack(fill="x", pady=(5, 0))
        
        # Completed filter
        ttk.Label(row2, text="Completed:").pack(side="left", padx=(0, 5))
        completed_combo = ttk.Combobox(row2, textvariable=self.completed_filter,
                                      values=["All", "Completed", "Not Completed"], 
                                      state="readonly", width=15)
        completed_combo.pack(side="left", padx=(0, 15))
        completed_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Rating filter
        ttk.Label(row2, text="Rating:").pack(side="left", padx=(0, 5))
        rating_combo = ttk.Combobox(row2, textvariable=self.rating_filter,
                                   values=["All", "★★★★★", "★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆", "☆☆☆☆☆"],
                                   state="readonly", width=15)
        rating_combo.pack(side="left", padx=(0, 15))
        rating_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Clear filters button
        ttk.Button(row2, text="Clear Filters", 
                  command=self._clear_filters).pack(side="right")
        
    def _create_table(self):
        """Create the main data table"""
        # Table frame with scrollbars
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True)
        
        # Create treeview with columns
        columns = ("completed", "title", "difficulty", "rating", "completed_date", "folder", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("completed", text="✓")
        self.tree.heading("title", text="Hack Name")
        self.tree.heading("difficulty", text="Difficulty")
        self.tree.heading("rating", text="Rating")
        self.tree.heading("completed_date", text="Completed Date")
        self.tree.heading("folder", text="📁")
        self.tree.heading("notes", text="Notes")
        
        # Set column widths
        self.tree.column("completed", width=40, minwidth=40)
        self.tree.column("title", width=300, minwidth=200)
        self.tree.column("difficulty", width=100, minwidth=80)
        self.tree.column("rating", width=80, minwidth=80)
        self.tree.column("completed_date", width=120, minwidth=100)
        self.tree.column("folder", width=40, minwidth=40)
        self.tree.column("notes", width=200, minwidth=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Double-1>", self._on_item_double_click)
        self.tree.bind("<Button-1>", self._on_item_click)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(pady=(5, 0))
    
    def _refresh_table(self):
        """Refresh table data from data manager"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all hacks and apply filters
        all_hacks = self.data_manager.get_all_hacks()
        self.filtered_data = self._filter_hacks(all_hacks)
        
        # Populate table
        for hack in self.filtered_data:
            completed_display = "✓" if hack["completed"] else ""
            rating_display = self._get_rating_display(hack["personal_rating"])
            folder_display = "📁"
            
            # Truncate notes for display
            notes_display = hack["notes"][:50] + "..." if len(hack["notes"]) > 50 else hack["notes"]
            
            self.tree.insert("", "end", values=(
                completed_display,
                hack["title"],
                hack["difficulty"],
                rating_display,
                hack["completed_date"],
                folder_display,
                notes_display
            ), tags=(hack["id"],))
        
        # Update status
        total_count = len(all_hacks)
        filtered_count = len(self.filtered_data)
        completed_count = sum(1 for hack in self.filtered_data if hack["completed"])
        
        status_text = f"Showing {filtered_count} of {total_count} hacks"
        if filtered_count > 0:
            status_text += f" • {completed_count} completed"
        
        self.status_label.config(text=status_text)
    
    def _filter_hacks(self, hacks):
        """Apply current filters to hack list"""
        filtered = hacks.copy()
        
        # Name filter
        name_text = self.name_filter.get().lower()
        if name_text:
            filtered = [h for h in filtered if name_text in h["title"].lower()]
        
        # Difficulty filter
        if self.difficulty_filter.get() != "All":
            filtered = [h for h in filtered if h["difficulty"] == self.difficulty_filter.get()]
        
        # Completed filter
        completed_val = self.completed_filter.get()
        if completed_val == "Completed":
            filtered = [h for h in filtered if h["completed"]]
        elif completed_val == "Not Completed":
            filtered = [h for h in filtered if not h["completed"]]
        
        # Rating filter
        rating_val = self.rating_filter.get()
        if rating_val != "All":
            rating_num = rating_val.count("★")
            filtered = [h for h in filtered if h["personal_rating"] == rating_num]
        
        return filtered
    
    def _apply_filters(self):
        """Apply current filters and refresh table"""
        self._refresh_table()
    
    def _clear_filters(self):
        """Clear all filters"""
        self.name_filter.set("")
        self.difficulty_filter.set("All")
        self.completed_filter.set("All")
        self.rating_filter.set("All")
        self._apply_filters()
    
    def _get_rating_display(self, rating):
        """Convert numeric rating to star display"""
        if rating == 0:
            return "☆☆☆☆☆"
        return "★" * rating + "☆" * (5 - rating)
    
    def _on_item_click(self, event):
        """Handle single click on table item"""
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if not item:
            return
        
        hack_id = self.tree.item(item)["tags"][0]
        hack_data = next((h for h in self.filtered_data if h["id"] == hack_id), None)
        
        if not hack_data:
            return
        
        # Handle completed checkbox click
        if column == "#1":  # Completed column
            new_completed = not hack_data["completed"]
            self.data_manager.update_hack(hack_id, "completed", new_completed)
            self._refresh_table()
        
        # Handle folder icon click
        elif column == "#6":  # Folder column
            self._open_file_location(hack_data["file_path"])
    
    def _on_item_double_click(self, event):
        """Handle double click on table item"""
        item = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify("column", event.x, event.y)
        
        if not item:
            return
        
        hack_id = self.tree.item(item)["tags"][0]
        hack_data = next((h for h in self.filtered_data if h["id"] == hack_id), None)
        
        if not hack_data:
            return
        
        # Open edit dialog for different columns
        if column == "#4":  # Rating column
            self._edit_rating(hack_id, hack_data)
        elif column == "#5":  # Completed date column
            self._edit_date(hack_id, hack_data)
        elif column == "#7":  # Notes column
            self._edit_notes(hack_id, hack_data)
    
    def _edit_rating(self, hack_id, hack_data):
        """Open rating edit dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit Rating")
        dialog.geometry("300x200")
        dialog.transient(self.frame.winfo_toplevel())
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Rating for: {hack_data['title']}", 
                 font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        rating_var = tk.IntVar(value=hack_data["personal_rating"])
        
        # Rating buttons
        rating_frame = ttk.Frame(dialog)
        rating_frame.pack(pady=10)
        
        for i in range(6):  # 0-5 stars
            text = "☆☆☆☆☆" if i == 0 else "★" * i + "☆" * (5 - i)
            ttk.Radiobutton(rating_frame, text=text, variable=rating_var, 
                           value=i).pack(anchor="w", pady=2)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def save_rating():
            self.data_manager.update_hack(hack_id, "personal_rating", rating_var.get())
            dialog.destroy()
            self._refresh_table()
        
        ttk.Button(button_frame, text="Save", command=save_rating).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
    
    def _edit_date(self, hack_id, hack_data):
        """Open date edit dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit Completed Date")
        dialog.geometry("300x150")
        dialog.transient(self.frame.winfo_toplevel())
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Completed date for: {hack_data['title']}", 
                 font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        date_var = tk.StringVar(value=hack_data["completed_date"])
        
        ttk.Label(dialog, text="Date (YYYY-MM-DD):").pack(pady=5)
        date_entry = ttk.Entry(dialog, textvariable=date_var, width=20)
        date_entry.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def save_date():
            date_text = date_var.get()
            # Basic validation
            try:
                if date_text:
                    datetime.strptime(date_text, "%Y-%m-%d")
                self.data_manager.update_hack(hack_id, "completed_date", date_text)
                dialog.destroy()
                self._refresh_table()
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")
        
        def set_today():
            date_var.set(datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(button_frame, text="Today", command=set_today).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save", command=save_date).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
    
    def _edit_notes(self, hack_id, hack_data):
        """Open notes edit dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit Notes")
        dialog.geometry("400x250")
        dialog.transient(self.frame.winfo_toplevel())
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Notes for: {hack_data['title']}", 
                 font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        notes_text = tk.Text(text_frame, wrap="word", height=8, width=50)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=notes_text.yview)
        notes_text.configure(yscrollcommand=scrollbar.set)
        
        notes_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        notes_text.insert("1.0", hack_data["notes"])
        
        # Character count
        char_label = ttk.Label(dialog, text=f"Characters: {len(hack_data['notes'])}/200")
        char_label.pack(pady=5)
        
        def update_char_count(event=None):
            content = notes_text.get("1.0", "end-1c")
            char_label.config(text=f"Characters: {len(content)}/200")
            if len(content) > 200:
                char_label.config(foreground="red")
            else:
                char_label.config(foreground="")
        
        notes_text.bind("<KeyRelease>", update_char_count)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_notes():
            content = notes_text.get("1.0", "end-1c")
            if len(content) > 200:
                messagebox.showerror("Too Long", "Notes must be 200 characters or less")
                return
            
            self.data_manager.update_hack(hack_id, "notes", content)
            dialog.destroy()
            self._refresh_table()
        
        ttk.Button(button_frame, text="Save", command=save_notes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
    
    def _open_file_location(self, file_path):
        """Open file location in system file manager"""
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("File Not Found", "The file path no longer exists")
            return
        
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file location: {e}")