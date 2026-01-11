import tkinter as tk
from tkinter import ttk

class ColumnConfigDialog:
    """Dialog for configuring table columns (visibility and order)"""
    
    def __init__(self, parent, all_columns, current_columns, on_apply):
        """
        Args:
            parent: Parent window
            all_columns: List of all available column definitions (dicts with 'id', 'header')
            current_columns: List of currently visible column IDs in order
            on_apply: Callback function(new_column_ids_list)
        """
        self.parent = parent
        self.all_columns = all_columns
        self.current_columns = current_columns
        self.on_apply = on_apply
        self.dialog = None
        self.items = [] # List of (col_id, var, widget_frame)
        
    def show(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Configure Columns")
        self.dialog.resizable(False, False)
        
        # Main layout
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Multi-line description with wrapping
        desc_label = ttk.Label(
            main_frame, 
            text="Select columns to display in the collection table.\nNote: 'Title' column is always visible and cannot be hidden.",
            font=("Segoe UI", 9),
            justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # List frame
        list_frame = ttk.LabelFrame(main_frame, text="Visible Columns", padding=10)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Configure grid for 2 columns
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_columnconfigure(1, weight=1)
        list_frame.grid_columnconfigure(2, weight=1)
        
        self.vars = {}
        row = 0
        col = 0
        
        for column in self.all_columns:
            col_id = column["id"]
            is_visible = col_id in self.current_columns
            var = tk.BooleanVar(value=is_visible)
            self.vars[col_id] = var
            
            # Create checkbox
            cb = ttk.Checkbutton(list_frame, text=column["header"], variable=var)
            cb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            
            # Disable title checkbox (always visible)
            if col_id == "title":
                cb.configure(state="disabled")
                var.set(True)  # Force title to be checked
            
            # Move to next column/row
            col += 1
            if col >= 3:
                col = 0
                row += 1
            
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Apply", command=self._apply, style="Accent.TButton").pack(side="right")
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side="right", padx=(0, 10))
        
        # Center with wider width
        self.dialog.update_idletasks()
        width = 450  # Increased from 300
        height = self.dialog.winfo_reqheight()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def _apply(self):
        # Build new list of column IDs based on checked state
        # Preserving original definition order for now (MVP)
        # Always include title even if somehow unchecked
        new_columns = []
        for col in self.all_columns:
            col_id = col["id"]
            # Force title to always be included
            if col_id == "title" or self.vars[col_id].get():
                new_columns.append(col_id)
                
        self.on_apply(new_columns)
        self.dialog.destroy()
