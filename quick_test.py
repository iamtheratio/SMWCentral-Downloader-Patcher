#!/usr/bin/env python3
"""Quick test to verify button visibility"""

import tkinter as tk
from tkinter import ttk

def quick_layout_test():
    root = tk.Tk()
    root.title("Layout Test")
    root.geometry("800x600")
    
    # Simulate the layout structure
    main_container = ttk.Frame(root)
    main_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Top sections (filters, difficulty)
    top_frame = ttk.LabelFrame(main_container, text="Filters")
    top_frame.pack(fill="x", pady=(0, 10))
    ttk.Label(top_frame, text="Filter controls would go here").pack(pady=10)
    
    difficulty_frame = ttk.LabelFrame(main_container, text="Difficulty")
    difficulty_frame.pack(fill="x", pady=(0, 10))
    ttk.Label(difficulty_frame, text="Difficulty checkboxes would go here").pack(pady=10)
    
    # Bottom button - pack this FIRST
    button_frame = ttk.Frame(main_container)
    button_frame.pack(side="bottom", fill="x", pady=(10, 0))
    download_button = ttk.Button(button_frame, text="Download & Patch", style="Accent.TButton")
    download_button.pack()
    
    # Results in middle - pack this LAST so it fills remaining space
    results_frame = ttk.LabelFrame(main_container, text="Search Results")
    results_frame.pack(fill="x", expand=False, pady=(0, 10))
    
    # Create a treeview to simulate the results table
    tree = ttk.Treeview(results_frame, height=8)
    tree["columns"] = ("Title", "Type", "Difficulty")
    tree.heading("#0", text="✓")
    tree.heading("Title", text="Title")
    tree.heading("Type", text="Type")
    tree.heading("Difficulty", text="Difficulty")
    
    # Add some sample data
    for i in range(15):  # More than height=8 to test scrolling
        tree.insert("", "end", text="☐", values=(f"Hack {i+1}", "Kaizo", "Expert"))
    
    scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def check_button():
        try:
            button_y = download_button.winfo_y()
            root_height = root.winfo_height()
            print(f"Button Y: {button_y}, Window height: {root_height}")
            if button_y > 0 and button_y < root_height - 50:
                print("✅ Button is visible")
            else:
                print("❌ Button may be hidden")
        except Exception as e:
            print(f"Error: {e}")
    
    def test_resize():
        root.geometry("800x400")  # Make window smaller
        root.after(100, check_button)
    
    # Test controls
    control_frame = ttk.Frame(root)
    control_frame.pack(side="top", fill="x", padx=10, pady=5)
    
    ttk.Button(control_frame, text="Check Button Position", command=check_button).pack(side="left", padx=5)
    ttk.Button(control_frame, text="Resize Smaller", command=test_resize).pack(side="left", padx=5)
    
    print("Layout Test: Button should remain visible when resizing")
    root.after(500, check_button)
    
    root.mainloop()

if __name__ == "__main__":
    quick_layout_test()
