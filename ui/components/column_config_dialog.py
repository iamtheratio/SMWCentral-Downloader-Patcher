import tkinter as tk
from tkinter import ttk

class ColumnConfigDialog:
    """Dialog for configuring table columns (visibility and order) with drag-and-drop reordering"""
    
    def __init__(self, parent, all_columns, current_columns, on_apply, config_manager=None, default_columns=None):
        """
        Args:
            parent: Parent window
            all_columns: List of all available column definitions (dicts with 'id', 'header')
            current_columns: List of currently visible column IDs in order
            on_apply: Callback function(new_column_ids_list)
            config_manager: ConfigManager instance for saving column order
            default_columns: List of default column order (optional, falls back to all_columns)
        """
        self.parent = parent
        self.all_columns = all_columns
        self.current_columns = current_columns
        self.on_apply = on_apply
        self.config_manager = config_manager
        self.default_columns = default_columns if default_columns else all_columns
        self.dialog = None
        
        # Ordered list of (col_id, is_visible, header) tuples
        self.ordered_items = []
        
        # Drag state
        self.drag_source_index = None
        self.drag_widget = None
        self.drag_label = None
        self.grid_widgets = []  # List of (frame, checkbox, label, index) tuples
        
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
            text="Select columns to display and drag to reorder.\nNumbers show column order (left-to-right, top-to-bottom).",
            font=("Segoe UI", 9),
            justify="left"
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # List frame
        self.list_frame = ttk.LabelFrame(main_frame, text="Column Order & Visibility", padding=10)
        self.list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Initialize ordered items from saved column order
        self._initialize_ordered_items()
        
        # Build the grid
        self._build_grid()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Apply", command=self._apply, style="Accent.TButton").pack(side="right")
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side="right", padx=(0, 10))
        ttk.Button(btn_frame, text="Reset to Default", command=self._reset_to_default).pack(side="left")
        
        # Center with wider width
        self.dialog.update_idletasks()
        width = 550
        height = self.dialog.winfo_reqheight()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def _initialize_ordered_items(self):
        """Initialize ordered items from config or default order"""
        # Get saved column order from config
        saved_order = None
        if self.config_manager:
            saved_order = self.config_manager.get("column_order", None)
        
        # If no saved order, use default all_columns order
        if not saved_order:
            saved_order = [col["id"] for col in self.all_columns]
        
        # Build ordered items list
        self.ordered_items = []
        for col_id in saved_order:
            # Find column definition
            col_def = next((c for c in self.all_columns if c["id"] == col_id), None)
            if col_def:
                is_visible = col_id in self.current_columns
                self.ordered_items.append((col_id, is_visible, col_def["header"]))
        
        # Add any new columns that might not be in saved order (for backward compatibility)
        existing_ids = [item[0] for item in self.ordered_items]
        for col in self.all_columns:
            if col["id"] not in existing_ids:
                is_visible = col["id"] in self.current_columns
                self.ordered_items.append((col["id"], is_visible, col["header"]))
    
    def _build_grid(self, highlight_index=None):
        """Build or rebuild the grid layout with drag-and-drop support"""
        # Clear existing widgets
        for widget_data in self.grid_widgets:
            widget_data[0].destroy()
        self.grid_widgets = []
        
        # Configure grid for 3 columns
        for i in range(3):
            self.list_frame.grid_columnconfigure(i, weight=1)
        
        # Create grid items
        num_cols = 3
        for idx, (col_id, is_visible, header) in enumerate(self.ordered_items):
            row = idx // num_cols
            col = idx % num_cols
            
            # Create container frame
            item_frame = ttk.Frame(self.list_frame, relief="raised" if idx == highlight_index else "flat", borderwidth=1)
            item_frame.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            
            # Number label
            num_label = ttk.Label(item_frame, text=f"{idx + 1}.", font=("Segoe UI", 9))
            num_label.pack(side="left", padx=(0, 5))
            
            # Checkbox
            var = tk.BooleanVar(value=is_visible)
            cb = ttk.Checkbutton(item_frame, text=header, variable=var)
            cb.pack(side="left")
            
            # Store variable for later retrieval
            cb.column_data = (col_id, var)
            
            # Disable title checkbox (always visible)
            if col_id == "title":
                cb.configure(state="disabled")
                var.set(True)
            
            # Bind drag events to ALL widgets (frame, label, AND checkbox)
            # This ensures drag works even when clicking on checkbox
            for widget in [item_frame, num_label, cb]:
                widget.bind("<Button-1>", lambda e, i=idx: self._start_drag(e, i))
                widget.bind("<B1-Motion>", self._on_drag)
                widget.bind("<ButtonRelease-1>", self._end_drag)
            
            # Store widget references
            self.grid_widgets.append((item_frame, cb, num_label, idx))
    
    def _start_drag(self, event, index):
        """Start dragging an item"""
        # Store initial position to detect if this is a click or drag
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.drag_source_index = index
        self.drag_widget = event.widget
        self.is_dragging = False
        self.drag_label = None  # For visual feedback during drag
    
    def _on_drag(self, event):
        """Handle drag motion"""
        if self.drag_source_index is None:
            return
        
        # Only start visual drag if moved more than 5 pixels
        if not self.is_dragging:
            dx = abs(event.x_root - self.drag_start_x)
            dy = abs(event.y_root - self.drag_start_y)
            if dx > 5 or dy > 5:
                self.is_dragging = True
                if self.drag_widget and self.drag_widget.winfo_exists():
                    self.drag_widget.configure(cursor="hand2")
                
                # Create visual feedback label showing what's being dragged
                _, _, header = self.ordered_items[self.drag_source_index]
                self.drag_label = tk.Label(
                    self.dialog, 
                    text=f"   {header}   ",
                    background="#4a6fa5",
                    foreground="white",
                    relief="raised",
                    borderwidth=2,
                    font=("Segoe UI", 9, "bold")
                )
                self.drag_label.place(x=event.x_root - self.dialog.winfo_rootx(), 
                                     y=event.y_root - self.dialog.winfo_rooty())
        
        if not self.is_dragging:
            return
        
        # Update drag label position
        if self.drag_label and self.drag_label.winfo_exists():
            self.drag_label.place(x=event.x_root - self.dialog.winfo_rootx(), 
                                 y=event.y_root - self.dialog.winfo_rooty())
        
        # Find which grid cell we're over
        x = event.x_root
        y = event.y_root
        
        target_index = None
        for frame, cb, label, idx in self.grid_widgets:
            fx, fy = frame.winfo_rootx(), frame.winfo_rooty()
            fw, fh = frame.winfo_width(), frame.winfo_height()
            
            if fx <= x <= fx + fw and fy <= y <= fy + fh:
                target_index = idx
                break
        
        # Highlight target
        if target_index is not None and target_index != self.drag_source_index:
            for frame, cb, label, idx in self.grid_widgets:
                if idx == target_index:
                    frame.configure(relief="sunken", borderwidth=2)
                else:
                    frame.configure(relief="flat", borderwidth=1)
    
    def _end_drag(self, event):
        """End dragging and reorder items"""
        if self.drag_source_index is None:
            return
        
        # Clean up drag label
        if self.drag_label and self.drag_label.winfo_exists():
            self.drag_label.destroy()
        self.drag_label = None
        
        # Only reorder if we actually dragged (not just a click)
        if not self.is_dragging:
            # This was just a click, reset and return
            self.drag_source_index = None
            self.drag_widget = None
            return
        
        # Find drop target
        x = event.x_root
        y = event.y_root
        
        target_index = None
        for frame, cb, label, idx in self.grid_widgets:
            fx, fy = frame.winfo_rootx(), frame.winfo_rooty()
            fw, fh = frame.winfo_width(), frame.winfo_height()
            
            if fx <= x <= fx + fw and fy <= y <= fy + fh:
                target_index = idx
                break
        
        # Reorder if valid drop and actually moved
        if target_index is not None and target_index != self.drag_source_index:
            # Get current checkbox states before reordering
            checkbox_states = {}
            for frame, cb, label, idx in self.grid_widgets:
                col_id, var = cb.column_data
                checkbox_states[col_id] = var.get()
            
            # Reorder the items list
            item = self.ordered_items.pop(self.drag_source_index)
            self.ordered_items.insert(target_index, item)
            
            # Update visibility states
            updated_items = []
            for col_id, is_visible, header in self.ordered_items:
                new_visibility = checkbox_states.get(col_id, is_visible)
                updated_items.append((col_id, new_visibility, header))
            self.ordered_items = updated_items
            
            # Rebuild grid
            self._build_grid()
        
        # Reset drag state - check if widget still exists before configuring
        self.drag_source_index = None
        if self.drag_widget and self.drag_widget.winfo_exists():
            try:
                self.drag_widget.configure(cursor="")
            except tk.TclError:
                pass  # Widget was destroyed, ignore
        self.drag_widget = None
        
        # Clear highlights
        for frame, cb, label, idx in self.grid_widgets:
            if frame.winfo_exists():
                frame.configure(relief="flat", borderwidth=1)
    
    def _reset_to_default(self):
        """Reset to default column order and make all columns visible"""
        # Reset to default order with ALL columns visible
        self.ordered_items = []
        for col in self.default_columns:
            col_id = col["id"]
            # Make all columns visible by default
            is_visible = True
            self.ordered_items.append((col_id, is_visible, col["header"]))
        
        # Clear saved column order from config to use default
        if self.config_manager:
            self.config_manager.set("column_order", None)
            self.config_manager.save()
        
        # Rebuild grid
        self._build_grid()
    
    def _apply(self):
        """Apply column configuration and save to config"""
        # Get current checkbox states
        checkbox_states = {}
        for frame, cb, label, idx in self.grid_widgets:
            col_id, var = cb.column_data
            checkbox_states[col_id] = var.get()
        
        # Build ordered list of visible columns only (preserving grid order)
        visible_columns = []
        for col_id, _, _ in self.ordered_items:
            if checkbox_states.get(col_id, False) or col_id == "title":
                visible_columns.append(col_id)
        
        # Save to config (order and visibility)
        if self.config_manager:
            # Save the full column order (all columns, not just visible ones)
            column_order = [col_id for col_id, _, _ in self.ordered_items]
            self.config_manager.set("column_order", column_order)
            self.config_manager.set("visible_columns", visible_columns)
            self.config_manager.save()
        
        # Callback to collection page
        self.on_apply(visible_columns)
        self.dialog.destroy()
