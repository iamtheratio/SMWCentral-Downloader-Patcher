import tkinter as tk
from tkinter import ttk
from api_pipeline import run_pipeline
from ui import setup_ui, update_log_colors
from utils import resource_path  # ADDED: Import resource path utility
import sv_ttk
import sys
import platform
import pywinstyles

VERSION = "v4.0"

def apply_theme_to_titlebar(root):
    if platform.system() != "Windows":
        return
        
    version = sys.getwindowsversion()
    
    if version.major == 10 and version.build >= 22000:
        # Windows 11
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        # Windows 10
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")
        # Force update title bar
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

def apply_font_settings(root, style):
    default_font = ("Segoe UI", 9)
    
    # FIXED: Force disable sv_ttk font management to prevent conflicts
    sv_ttk.USE_FONT_CONFIG = False
    
    # Configure all widgets before updating
    style.configure(".", font=default_font)
    for widget in ["TLabel", "TButton", "TCheckbutton", "TRadiobutton", 
                  "TCombobox", "TEntry"]:  # REMOVED: "Treeview" from this list
        style.configure(widget, font=default_font)

    # ADDED: Configure Treeview with larger font and row height for better readability
    style.configure("Treeview", 
                   font=("Segoe UI", 10),  # Larger font for table
                   rowheight=25)  # More padding
    
    style.configure("Treeview.Heading", 
                   font=("Segoe UI", 10, "bold"))  # Bold headers

    # Configure custom button style for both themes
    style.configure("Large.Accent.TButton", 
                   font=("Segoe UI", 10, "bold"),
                   padding=(20, 10))
    
    # CHANGED: Configure the default Switch style to use toggle background
    from colors import get_colors
    colors = get_colors()
    
    # Configure Switch.TCheckbutton to use toggle background
    style.configure("Switch.TCheckbutton",
                   background=colors["toggle_bg"])

    # Apply font to root and force update
    root.option_add("*font", default_font)
    root.update()

def toggle_theme_callback(root):
    style = ttk.Style()
    
    # Toggle theme first
    sv_ttk.toggle_theme()
    
    # ADDED: Reapply font settings after theme change to ensure consistency
    apply_font_settings(root, style)
    
    # Get new colors immediately
    from colors import get_colors
    colors = get_colors()
    
    # Update all toggle-related colors TOGETHER without calling update()
    style.configure("Switch.TCheckbutton", background=colors["toggle_bg"])
    
    # Update navigation elements immediately without intermediate updates
    if hasattr(root, 'navigation'):
        if hasattr(root.navigation, 'theme_frame') and root.navigation.theme_frame:
            root.navigation.theme_frame.configure(bg=colors["toggle_bg"])
        
        if hasattr(root.navigation, 'moon_label') and root.navigation.moon_label:
            root.navigation.moon_label.configure(bg=colors["toggle_bg"], fg=colors["nav_text"])
        
        # Update navigation without calling update methods that cause flashing
        if root.navigation.nav_bar:
            root.navigation.nav_bar.configure(bg=colors["nav_bg"])
            root.navigation._update_tab_styles(root.navigation.current_page)
            
            # Update toggle background rectangle
            for item in root.navigation.nav_bar.find_withtag("toggle_bg"):
                root.navigation.nav_bar.itemconfig(item, fill=colors["toggle_bg"], outline=colors["toggle_bg"])
    
    # Update title bar
    apply_theme_to_titlebar(root)
    
    # Update log colors if log_text exists
    if hasattr(root, 'log_text'):
        update_log_colors(root.log_text)
    
    # Update dashboard if it exists
    if hasattr(root, 'navigation') and hasattr(root.navigation, 'page_manager'):
        current_page = root.navigation.page_manager.get_current_page()
        if current_page == "Dashboard":
            # Refresh the dashboard to apply new theme using the stored reference
            if hasattr(root, 'dashboard_page') and hasattr(root.dashboard_page, '_refresh_dashboard'):
                try:
                    root.dashboard_page._refresh_dashboard()
                except Exception as e:
                    print(f"Error refreshing dashboard during theme toggle: {e}")
    
    # Single update at the very end
    root.update_idletasks()

def clear_log_shortcut(root):
    """Handle Ctrl+L keyboard shortcut"""
    if hasattr(root, 'log_text'):
        log_text = root.log_text
        log_text.config(state="normal")
        log_text.delete(1.0, tk.END)
        log_text.config(state="disabled")

def run_pipeline_wrapper(*args, **kwargs):
    """Wrapper function to handle both bulk downloads and single downloads"""
    # Check if this is a single download call with selected_hacks
    if 'selected_hacks' in kwargs:
        selected_hacks = kwargs.pop('selected_hacks')
        
        # For single downloads, we'll use the regular pipeline but with a custom hack list
        # Instead of fetching from API, we'll inject the selected hacks
        return run_single_download_pipeline(selected_hacks, **kwargs)
    else:
        # This is a regular bulk download call
        run_pipeline(*args, **kwargs)

def run_single_download_pipeline(selected_hacks, log=None, progress_callback=None):
    """Custom pipeline for single download page that works like bulk download"""
    from api_pipeline import fetch_file_metadata, load_processed, save_processed, reset_cancel_flag, is_cancelled, extract_patches_from_zip, make_output_path, clean_hack_title, DIFFICULTY_LOOKUP, get_sorted_folder_name, title_case, safe_filename
    from patch_handler import PatchHandler
    from config_manager import ConfigManager
    import tempfile
    import requests
    import os
    
    # Get config for paths
    config = ConfigManager()
    base_rom_path = config.get("base_rom_path", "")
    output_dir = config.get("output_dir", "")
    
    if not base_rom_path or not output_dir:
        if log: log("Error: Base ROM path and output directory must be configured", "Error")
        return
    
    if log: log(f"🎯 Starting download of {len(selected_hacks)} selected hacks...", "Information")
    
    # Reset cancellation flag
    reset_cancel_flag()
    
    # Load processed hacks
    processed = load_processed()
    
    successful_downloads = 0
    skipped_hacks = 0
    errored_hacks = 0
    total_hacks = len(selected_hacks)
    base_rom_ext = os.path.splitext(base_rom_path)[1]
    
    for i, hack in enumerate(selected_hacks, 1):
        # Check for cancellation
        if is_cancelled():
            if log: log("❌ Download cancelled by user", "warning")
            break
        
        hack_id = str(hack.get("id"))
        hack_name = hack.get("name", "Unknown")
        title_clean = title_case(safe_filename(hack_name))
        
        if log: log(f"📥 [{i}/{total_hacks}] Processing: {hack_name}", "Information")
        
        # Update progress callback if provided
        if progress_callback:
            progress_callback(i, total_hacks, hack_name)
        
        # Get difficulty info
        raw_fields = hack.get("raw_fields", {})
        raw_diff = raw_fields.get("difficulty", "")
        if not raw_diff or raw_diff in [None, "N/A"]:
            raw_diff = ""
        display_diff = DIFFICULTY_LOOKUP.get(raw_diff, "No Difficulty")
        folder_name = get_sorted_folder_name(display_diff)
        
        # Check if already processed
        if hack_id in processed:
            # Check if this hack needs multi-type copies that are missing
            existing_hack = processed[hack_id]
            
            # Get current hack types from the fresh data
            from multi_type_utils import get_hack_types_from_raw_data
            current_hack_types = get_hack_types_from_raw_data(raw_fields, hack)
            
            # Check if multi-type is enabled and hack has multiple types
            multi_type_enabled = config.get("multi_type_enabled", True)
            download_mode = config.get("multi_type_download_mode", "primary_only")
            
            if (multi_type_enabled and download_mode == "copy_all" and 
                len(current_hack_types) > 1 and 
                existing_hack.get("file_path") and 
                os.path.exists(existing_hack["file_path"])):
                
                # Check if additional_paths exist or are missing
                existing_additional_paths = existing_hack.get("additional_paths", [])
                expected_additional_types = current_hack_types[1:]  # Skip primary type
                
                missing_copies = []
                for hack_type in expected_additional_types:
                    expected_path = os.path.join(make_output_path(output_dir, hack_type, existing_hack["folder_name"]), 
                                               os.path.basename(existing_hack["file_path"]))
                    if not os.path.exists(expected_path):
                        missing_copies.append((hack_type, expected_path))
                
                if missing_copies:
                    if log: log(f"🔄 Creating missing multi-type copies for: {hack_name}", "Information")
                    
                    # Create missing copies
                    new_additional_paths = list(existing_additional_paths)
                    for hack_type, target_path in missing_copies:
                        try:
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            import shutil
                            shutil.copy2(existing_hack["file_path"], target_path)
                            new_additional_paths.append(target_path)
                            if log: log(f"📄 Created copy in {hack_type.title()} folder", "Debug")
                        except Exception as e:
                            if log: log(f"⚠️ Failed to create {hack_type} copy: {str(e)}", "Error")
                    
                    # Update processed data with new additional paths and hack_types
                    existing_hack["additional_paths"] = new_additional_paths
                    existing_hack["hack_types"] = current_hack_types
                    save_processed(processed)
                    
                    if log: log(f"✅ Updated multi-type copies for: {hack_name}", "Information")
                    successful_downloads += 1
                else:
                    if log: log(f"✅ Skipped: {hack_name} (all multi-type copies exist)", "Debug")
                    skipped_hacks += 1
            else:
                if log: log(f"✅ Skipped: {hack_name}", "Debug")
                skipped_hacks += 1
            continue
        
        try:
            # Get download URL - search results don't include download_url, so fetch it
            download_url = hack.get("download_url")
            if not download_url:
                # Fetch detailed metadata to get download URL
                if log: log(f"🔍 Fetching download URL for {hack_name}...", "Information")
                file_metadata = fetch_file_metadata(hack_id, log)
                if file_metadata and file_metadata.get("data"):
                    download_url = file_metadata["data"].get("download_url")
                
                if not download_url:
                    if log: log(f"❌ No download URL found for {hack_name}", "Error")
                    continue
            
            # Create temp directory for processing
            temp_dir = tempfile.mkdtemp()
            try:
                zip_path = os.path.join(temp_dir, "hack.zip")
                
                # Download the hack
                if log: log(f"⬇️ Downloading {hack_name}...", "Information")
                r = requests.get(download_url)
                r.raise_for_status()  # Raise exception for bad status codes
                with open(zip_path, "wb") as f:
                    f.write(r.content)
                
                # Extract patch file
                patch_path = extract_patches_from_zip(zip_path, temp_dir, title_clean)
                if not patch_path:
                    raise Exception("Patch file (.ips or .bps) not found in archive")
                
                # Determine hack types for output path - support multiple types
                from multi_type_utils import get_hack_types_from_raw_data, handle_multi_type_download
                
                hack_types = get_hack_types_from_raw_data(raw_fields, hack)
                primary_type = hack_types[0] if hack_types else "standard"
                
                # Create primary output path
                output_filename = f"{title_clean}{base_rom_ext}"
                primary_output_path = os.path.join(make_output_path(output_dir, primary_type, folder_name), output_filename)
                
                # Apply the patch to primary location
                if log: log(f"🔧 Patching {hack_name}...", "Information")
                success = PatchHandler.apply_patch(patch_path, base_rom_path, primary_output_path, log)
                if not success:
                    raise Exception("Patch application failed")
                
                # Handle multi-type downloads
                additional_paths = handle_multi_type_download(
                    primary_output_path, hack_types, output_dir, folder_name, 
                    title_clean, base_rom_ext, config, log
                )
                
                # Update processed data with multi-type support
                processed[hack_id] = {
                    "title": clean_hack_title(hack_name),
                    "current_difficulty": display_diff,
                    "folder_name": folder_name,
                    "file_path": primary_output_path,  # Use primary path for backward compatibility
                    "additional_paths": additional_paths,  # Store additional paths for multi-type
                    "hack_type": primary_type,  # Keep for backward compatibility
                    "hack_types": hack_types,   # New: array of all types
                    "hall_of_fame": bool(raw_fields.get("hof", False)),
                    "sa1_compatibility": bool(raw_fields.get("sa1", False)),
                    "collaboration": bool(raw_fields.get("collab", False)),
                    "demo": bool(raw_fields.get("demo", False)),
                    "authors": hack.get("authors", []),
                    "exits": raw_fields.get("length", hack.get("length", 0)) or 0
                }
                
                if log: log(f"✅ Successfully processed: {hack_name}", "Information")
                successful_downloads += 1
                
                # Save progress after each successful download
                save_processed(processed)
                
            finally:
                # Clean up temp directory
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            
        except Exception as e:
            if log: log(f"❌ Error processing {hack_name}: {str(e)}", "Error")
            errored_hacks += 1
            continue
    
    # Final summary
    if progress_callback:
        progress_callback(total_hacks, total_hacks, "Complete!")
    if log: log(f"✅ Download complete! {successful_downloads} processed, {skipped_hacks} skipped, {errored_hacks} errored, out of {total_hacks} hacks.", "Information")

def main():
    root = tk.Tk()
    root.title("SMWC Downloader & Patcher")
    root.geometry("1050x900")
    
    # Set application icon
    try:
        root.iconbitmap(resource_path("assets/icon.ico"))
    except tk.TclError:
        print("Could not load application icon. Make sure the file exists.")
    
    # Initial setup
    style = ttk.Style()
    # MOVED: Set USE_FONT_CONFIG to False BEFORE setting theme
    sv_ttk.USE_FONT_CONFIG = False
    sv_ttk.set_theme("dark")
    
    # Configure fonts after theme
    apply_font_settings(root, style)
    
    # Apply title bar theme immediately after dark theme is set
    apply_theme_to_titlebar(root)
    
    # Check for migration before setting up UI
    def setup_after_migration():
        # Setup UI and run - pass version to setup_ui
        download_button = setup_ui(root, run_pipeline_wrapper, toggle_theme_callback, VERSION)
        
        # Store button reference for pipeline access
        root.download_button = download_button
        
        # Add keyboard shortcut for clearing log
        root.bind("<Control-l>", lambda e: clear_log_shortcut(root))
        
        # Add cleanup handler for when app closes
        def on_closing():
            # Force save any pending changes in history
            if hasattr(root, 'navigation') and hasattr(root.navigation, 'page_manager'):
                pages = root.navigation.page_manager.pages
                if 'History' in pages:
                    history_page = pages['History']
                    if hasattr(history_page, 'cleanup'):
                        history_page.cleanup()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Import and run migration check
    try:
        from migration_manager import check_and_migrate
        if not check_and_migrate(root, setup_after_migration):
            return  # User cancelled migration, app should close
    except ImportError:
        # If migration manager doesn't exist, just setup normally
        setup_after_migration()
    
    # Quick multi-type migration check (silent, fast)
    try:
        from api_pipeline import load_processed, save_processed
        processed = load_processed()
        needs_multi_type_update = False
        
        for hack_id, hack_data in processed.items():
            if isinstance(hack_data, dict) and "hack_type" in hack_data and "hack_types" not in hack_data:
                # Convert single hack_type to hack_types array
                single_type = hack_data["hack_type"]
                hack_data["hack_types"] = [single_type] if single_type else ["standard"]
                needs_multi_type_update = True
        
        if needs_multi_type_update:
            save_processed(processed)
            print("✅ Updated processed.json for multi-type support")
    except Exception as e:
        print(f"Note: Could not update processed.json for multi-type support: {e}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
