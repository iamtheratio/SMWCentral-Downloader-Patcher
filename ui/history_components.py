import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ui_constants import get_labelframe_padding

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
        self.cleanup()
    
    def cleanup(self):
        """Clean up entry widget and bindings"""
        if self.binding_id:
            try:
                self.tree.winfo_toplevel().unbind("<Button-1>", self.binding_id)
                self.binding_id = None
            except:
                pass
                
        if self.entry:
            self.entry.destroy()
            self.entry = None
            
        # Reset state
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


class HackHistoryInlineEditor(InlineEditor):
    """Extended inline editor that knows how to find hack data"""
    
    def __init__(self, tree, data_manager, parent_page, logger=None):
        super().__init__(tree, data_manager)
        self.parent_page = parent_page
        self.logger = logger
    
    def _log(self, message, level="Information"):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log(message, level)
        
    def _find_hack_data(self, hack_id_str):
        """Find hack data from parent page"""
        return self.parent_page._find_hack_data(hack_id_str)
    
    def start_edit(self, hack_id, item, event, field_name, column, validator=None):
        """Override start_edit to handle field-specific display formatting"""
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
        
        # Format value for editing display (v3.1 NEW)
        if field_name == "time_to_beat":
            # Convert to int first, handling string values
            try:
                time_value = int(current_value) if current_value else 0
            except (ValueError, TypeError):
                time_value = 0
            
            if time_value > 0:
                # Show time in user-friendly format for editing
                if hasattr(self.parent_page, '_format_time_display'):
                    display_value = self.parent_page._format_time_display(time_value)
                else:
                    display_value = str(time_value)
            else:
                display_value = ""
        else:
            display_value = str(current_value) if current_value else ""
        
        # Create entry widget
        x, y, width, height = bbox
        self.entry = ttk.Entry(self.tree, font=("Segoe UI", 10))
        self.entry.place(x=x, y=y, width=width, height=height)
        self.entry.insert(0, display_value)
        
        # Bind events
        self.entry.bind("<Return>", lambda e: self.save())
        self.entry.bind("<Escape>", lambda e: self.cancel())
        
        # Global click binding
        self.binding_id = self.tree.winfo_toplevel().bind("<Button-1>", self._check_outside_click, add="+")
        
        # Focus the entry
        self.tree.after(50, self._focus_entry)
    
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
        """Override save to refresh table after saving"""
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
                
        except:
            self.cleanup()
            return
            
        # Save to data manager
        if self.data_manager.update_hack(self.editing_hack_id, self.field_name, new_value):
            hack_data = self.parent_page._find_hack_data(self.editing_hack_id)
            hack_title = hack_data.get('title', 'Unknown') if hack_data else 'Unknown'
            
            # UPDATE LOCAL DATA IMMEDIATELY - this fixes the UI update issue
            if hack_data:
                hack_data[self.field_name] = new_value
                
                # AUTO-SET/CLEAR COMPLETED STATUS when date is added/removed
                if self.field_name == "completed_date":
                    if new_value and not hack_data.get("completed", False):
                        # Date added - set completed to True
                        hack_data["completed"] = True
                        self.data_manager.update_hack(self.editing_hack_id, "completed", True)
                        self._log(f"✅ Automatically marked '{hack_title}' (hack #{self.editing_hack_id}) as completed when date was added", "Debug")
                    elif not new_value and hack_data.get("completed", False):
                        # Date removed - set completed to False
                        hack_data["completed"] = False
                        self.data_manager.update_hack(self.editing_hack_id, "completed", False)
                        self._log(f"❌ Automatically marked '{hack_title}' (hack #{self.editing_hack_id}) as not completed when date was removed", "Debug")
            
            # Update the specific tree item directly without rebuilding entire table
            for item in self.parent_page.tree.get_children():
                item_tags = self.parent_page.tree.item(item)["tags"]
                if item_tags and str(item_tags[0]) == str(self.editing_hack_id):
                    # Get current values
                    current_values = list(self.parent_page.tree.item(item)["values"])
                    
                    # Update the specific column
                    if self.field_name == "completed_date":
                        current_values[5] = new_value  # Column index 5 for completed_date
                        # Update completed checkbox based on whether we have a date and completed status
                        if hack_data:
                            current_values[0] = "✓" if hack_data.get("completed", False) else ""  # Column index 0 for completed
                    elif self.field_name == "time_to_beat":  # v3.1 NEW
                        # Format time for display (convert seconds back to readable format)
                        if hasattr(self.parent_page, '_format_time_display'):
                            display_time = self.parent_page._format_time_display(new_value)
                        else:
                            display_time = str(new_value) if new_value else ""
                        current_values[6] = display_time  # Column index 6 for time_to_beat
                    elif self.field_name == "notes":
                        # Truncate notes for display
                        display_notes = new_value[:30] + "..." if len(new_value) > 30 else new_value
                        current_values[7] = display_notes  # Column index 7 for notes (was 6)
                    
                    # Update the tree item
                    self.parent_page.tree.item(item, values=current_values)
                    
                    # User-friendly logging
                    field_display = {"completed_date": "completion date", "notes": "notes", "time_to_beat": "time to beat"}.get(self.field_name, self.field_name)
                    if new_value:
                        self._log(f"📝 Updated {field_display} for '{hack_title}' (hack #{self.editing_hack_id})", "Information")
                    else:
                        self._log(f"🗑️ Cleared {field_display} for '{hack_title}' (hack #{self.editing_hack_id})", "Information")
                    break
            
        else:
            hack_data = self.parent_page._find_hack_data(self.editing_hack_id)
            hack_title = hack_data.get('title', 'Unknown') if hack_data else 'Unknown'
            field_display = {"completed_date": "completion date", "notes": "notes", "time_to_beat": "time to beat"}.get(self.field_name, self.field_name)
            self._log(f"❌ Failed to update {field_display} for '{hack_title}' (hack #{self.editing_hack_id}) - data manager returned false", "Error")
            
        self.cleanup()
