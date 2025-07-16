import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class InlineEditor:
    """Generic inline editor for table cells"""
    
    def __init__(self, tree, data_manager):
        self.tree = tree
        self.data_manager = data_manager
        self.entry = None
        self.binding_id = None
        self.editing_hack_id = None
        self.editing_item = None
        self.original_value = None
        self.field_name = None
        self.column = None
        self.validator = None
        
    def start_edit(self, hack_id, item, event, field_name, column, validator=None):
        """Start editing a cell"""
        # Clean up any existing edit
        self.cleanup()
        
        hack_id_str = str(hack_id)
        
        # Get the bounding box of the cell
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
            
        # Store editing info
        self.editing_hack_id = hack_id_str
        self.editing_item = item
        self.field_name = field_name
        self.column = column
        self.validator = validator
        
        # Get current value from data
        hack_data = self._find_hack_data(hack_id_str)
        if not hack_data:
            return
            
        current_value = hack_data.get(field_name, "")
        self.original_value = current_value
        
        # Create entry widget
        x, y, width, height = bbox
        self.entry = ttk.Entry(self.tree, font=("Segoe UI", 10))
        self.entry.place(x=x, y=y, width=width, height=height)
        self.entry.insert(0, current_value)
        
        # Bind events
        self.entry.bind("<Return>", lambda e: self.save())
        self.entry.bind("<Escape>", lambda e: self.cancel())
        
        # Global click binding
        self.binding_id = self.tree.winfo_toplevel().bind("<Button-1>", self._check_outside_click, add="+")
        
        # Focus the entry
        self.tree.after(50, self._focus_entry)
        
    def _find_hack_data(self, hack_id_str):
        """Find hack data from filtered data"""
        # This needs to be implemented by the parent class
        raise NotImplementedError("Subclass must implement _find_hack_data")
        
    def _focus_entry(self):
        """Focus and select all text in entry"""
        if self.entry:
            try:
                self.entry.focus_force()
                self.entry.select_range(0, tk.END)
                self.tree.winfo_toplevel().focus_force()
                self.entry.focus_force()
                self.entry.icursor(tk.END)
                self.tree.update_idletasks()
            except tk.TclError:
                pass
                
    def _check_outside_click(self, event):
        """Check if click is outside entry and save if needed"""
        if not self.entry:
            return
            
        try:
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty()
            w = self.entry.winfo_width()
            h = self.entry.winfo_height()
            
            if event.x_root < x or event.x_root > x+w or event.y_root < y or event.y_root > y+h:
                self.save()
        except tk.TclError:
            pass
            
    def save(self):
        """Save the edited value"""
        if not self.entry:
            return
            
        # Remove binding first
        if self.binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.binding_id)
                self.binding_id = None
            except:
                pass
                
        try:
            new_value = self.entry.get().strip()
            
            # Apply validator if provided
            if self.validator:
                validated_value = self.validator(new_value)
                if validated_value is None:  # Validation failed
                    self.cleanup()
                    return
                new_value = validated_value
                
        except tk.TclError:
            self.cleanup()
            return
            
        # Save to data manager
        if self.data_manager.update_hack(self.editing_hack_id, self.field_name, new_value):
            print(f"SUCCESS: {self.field_name} updated for hack {self.editing_hack_id}")
        else:
            print(f"ERROR: Failed to update {self.field_name} for hack {self.editing_hack_id}")
            
        self.cleanup()
        
    def cancel(self):
        """Cancel editing without saving"""
        if self.binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.binding_id)
                self.binding_id = None
            except:
                pass
        self.cleanup()
        
    def cleanup(self):
        """Clean up editing widgets and variables"""
        if self.binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.binding_id)
                self.binding_id = None
            except:
                pass
                
        if self.entry:
            try:
                self.entry.destroy()
            except tk.TclError:
                pass
            self.entry = None
            
        # Clear editing state
        self.editing_hack_id = None
        self.editing_item = None
        self.original_value = None
        self.field_name = None
        self.column = None
        self.validator = None


class DateValidator:
    """Validator for date fields"""
    
    @staticmethod
    def validate(date_string):
        """Validate and normalize date string"""
        if not date_string:
            return ""
            
        date_formats = [
            "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
            "%m.%d.%Y", "%d.%m.%Y", "%Y.%m.%d", "%d %m %Y", "%m %d %Y", "%Y %m %d",
            "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y", "%Y%m%d", "%m%d%Y", "%d%m%Y"
        ]
        
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_string, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
        # Invalid date
        messagebox.showerror("Invalid Date", 
                           "Invalid date format detected. The date field has been cleared.\n\n"
                           "Valid format is YYYY-MM-DD (e.g., 2025-01-15)")
        return ""


class NotesValidator:
    """Validator for notes fields"""
    
    @staticmethod
    def validate(notes_string):
        """Validate notes (just limit length)"""
        if len(notes_string) > 280:
            return notes_string[:280]
        return notes_string
