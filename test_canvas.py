import tkinter as tk
import sv_ttk

def test_canvas_color():
    root = tk.Tk()
    root.title("Canvas Color Test")
    root.geometry("800x100")
    
    # Apply sv_ttk theme
    sv_ttk.set_theme("light")
    
    # Test colors
    test_colors = ["#0078d4", "#60cdff", "blue", "red"]
    
    for i, color in enumerate(test_colors):
        canvas = tk.Canvas(root, height=60, bg=color, highlightthickness=0)
        canvas.pack(fill="x", pady=2)
        
        # Add some text
        canvas.create_text(100, 30, text=f"Canvas {i+1}: {color}", fill="white", font=("Arial", 12))
        
        # Test if color persists after update
        root.after(100, lambda c=canvas, col=color: c.configure(bg=col))
    
    root.mainloop()

if __name__ == "__main__":
    test_canvas_color()
