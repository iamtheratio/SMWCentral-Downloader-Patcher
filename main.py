# main.py
import tkinter as tk
from api_pipeline import run_pipeline
from ui import setup_ui

def main():
    root = tk.Tk()
    root.title("SMWC Downloader & Patcher v2.0")
    root.geometry("900x850")
    setup_ui(root, run_pipeline)
    root.mainloop()

if __name__ == "__main__":
    main()
