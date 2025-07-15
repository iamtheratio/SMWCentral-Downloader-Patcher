import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api_pipeline import fetch_hack_list
from ui_constants import get_page_padding, get_section_padding
from ui.components import DifficultySection
from ui.download_components import DownloadFilters, DownloadResults, DownloadButton
from config_manager import ConfigManager

class DownloadPage:
    """Individual Hack Download page with advanced filtering and selection"""
    
    def __init__(self, parent, run_pipeline_func, logger=None):
        self.parent = parent
        self.run_pipeline_func = run_pipeline_func
        self.logger = logger
        self.frame = None
        
        # Search state
        self.current_search_config = {}
        self.is_searching = False
        self.search_cancelled = False
        self.search_thread = None  # Track the search thread
        
        # UI components
        self.filters = None
        self.difficulty_section = None
        self.results = None
        self.download_button_component = None
        
        # Create difficulty section with the same list as bulk download
        difficulty_list = ["newcomer", "casual", "skilled", "advanced", "expert", "master", "grandmaster", "no difficulty"]
        self.difficulty_section = DifficultySection(None, difficulty_list)
    
    def _log(self, message, level="Information"):
        """Log a message if logger is available"""
        if self.logger:
            self.logger.log(message, level)
        else:
            print(f"[{level}] {message}")
    
    def create(self):
        """Create the download page"""
        self.frame = ttk.Frame(self.parent, padding=get_page_padding())
        
        # Create main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True)
        
        # Create filters component FIRST
        self.filters = DownloadFilters(
            main_container,
            callback_search=self._start_search,
            callback_clear=self._clear_filters,
            callback_time_period_update=self._update_time_period_state,
            callback_cancel=self._cancel_search
        )
        
        # Create difficulty section SECOND
        self._create_difficulty_section(main_container)
        
        # Create results component
        self.results = DownloadResults(
            main_container,
            callback_selection_change=self._update_selection_display
        )
        
        # Create download button component
        self.download_button_component = DownloadButton(
            main_container,
            callback_download=self._download_selected,
            callback_cancel=self._cancel_download
        )
        
        return self.frame
    
    def _create_difficulty_section(self, parent):
        """Create the difficulty section exactly like bulk download"""
        _, section_padding_y = get_section_padding()
        
        # Set parent for difficulty section
        self.difficulty_section.parent = parent
        self.difficulty_section.create(("Segoe UI", 9))  # Use default font
        self.difficulty_section.frame.pack(fill="x", pady=(0, section_padding_y))
    
    def _update_time_period_state(self, *args):
        """Time period now works independently - no need to disable"""
        # With API-based sorting by date, time period filtering can work independently
        # No need to disable the time period dropdown anymore
        pass
    
    def _clear_filters(self):
        """Clear all filter inputs"""
        self.filters.clear_all()
        
        # Clear difficulty selections
        if self.difficulty_section:
            for var in self.difficulty_section.difficulty_vars.values():
                var.set(False)
        
        # Update time period state
        self._update_time_period_state()
    
    def _cancel_search(self):
        """Cancel the current search"""
        if self.is_searching:
            self._log("🛑 Search cancellation requested by user", "Information")
            
            # Set the cancellation flag
            self.search_cancelled = True
            
            # Update UI immediately to show cancellation
            self.is_searching = False
            self.filters.set_searching_state(False)
            self.results.set_status("❌ Search cancelled")
            
            # The background thread will see search_cancelled=True and exit gracefully
    
    def _start_search(self):
        """Start the search in a background thread"""
        if self.is_searching:
            return
        
        # Build search configuration from filters
        config = self.filters.build_search_config()
        
        # Add difficulty filters
        selected_difficulties = []
        if self.difficulty_section:
            for diff_key, var in self.difficulty_section.difficulty_vars.items():
                if var.get():
                    selected_difficulties.append(diff_key)
        
        if selected_difficulties:
            config["difficulties"] = selected_difficulties
        
        # Get time period for API-based filtering
        time_period = self.filters.time_period_var.get()
        
        # For time period only searches, we need at least the time period
        if not config and time_period == "All Time":
            messagebox.showwarning("No Filters", "Please set at least one search filter or select a time period.")
            return
        
        self.is_searching = True
        self.search_cancelled = False
        self.filters.set_searching_state(True)
        self.results.set_status("🔍 Searching...")
        
        # Clear previous results
        self.results.clear_results()
        
        # Start search in background thread
        self.search_thread = threading.Thread(target=self._perform_search, args=(config, time_period))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def _perform_search(self, config, time_period):
        """Perform the actual search with efficient time period filtering"""
        try:
            # Check for cancellation right at the start
            if self.search_cancelled:
                self._log("Search cancelled before starting", "Information")
                return
                
            self.current_search_config = config
            all_results = []
            
            # Calculate cutoff timestamp for time period filtering
            cutoff_timestamp = self._calculate_cutoff_timestamp(time_period)
            
            # Determine which hack types to search based on Include Waiting checkbox
            include_waiting = self.filters.include_waiting_var.get()
            search_modes = [False]  # Always search moderated hacks
            
            if include_waiting:
                search_modes.append(True)  # Also search waiting hacks if enabled
            
            # Search the specified hack types
            for waiting_mode in search_modes:
                page = 1
                
                while True:
                    # Check for cancellation at the start of each page
                    if self.search_cancelled:
                        self._log(f"❌ Search stopped due to cancellation (page {page})", "Information")
                        return
                    
                    try:
                        # Add order by date for efficient time period filtering
                        search_config = config.copy()
                        if cutoff_timestamp:  # Only add order if we have time filtering
                            search_config["order"] = "date"  # Sort by date descending (newest first)
                        
                        self._log(f"Searching page {page} with config: {search_config}", "Debug")
                        
                        # Note: We can't cancel the API call once it starts, but we can check afterwards
                        result = fetch_hack_list(search_config, page=page, waiting_mode=waiting_mode, log=self._log)
                        
                        # CRITICAL: Check for cancellation immediately after API call
                        # This is the most important check because API calls can't be interrupted
                        if self.search_cancelled:
                            self._log(f"❌ Search cancelled - discarding results from page {page}", "Information")
                            return
                        
                        hacks = result.get("data", [])
                        
                        # Check for cancellation after getting hack data
                        if self.search_cancelled:
                            self._log(f"❌ Search cancelled - not processing {len(hacks)} hacks from page {page}", "Information")
                            return
                        
                        if not hacks:
                            self._log(f"No more hacks found on page {page}, stopping search", "Information")
                            break
                        
                        # If we have a time period filter, check if we've gone past the cutoff
                        if cutoff_timestamp:
                            # Check for cancellation before processing results
                            if self.search_cancelled:
                                self._log(f"❌ Search cancelled before processing time period filter on page {page}", "Information")
                                return
                            
                            page_hacks = []
                            all_past_cutoff = True
                            oldest_timestamp = None
                            
                            for hack in hacks:
                                # Check for cancellation every few hacks during processing
                                if self.search_cancelled:
                                    self._log(f"❌ Search cancelled during hack processing on page {page}", "Information")
                                    return
                                
                                hack_time = hack.get("time")
                                if hack_time:
                                    try:
                                        hack_timestamp = int(hack_time)
                                        if oldest_timestamp is None or hack_timestamp < oldest_timestamp:
                                            oldest_timestamp = hack_timestamp
                                        
                                        if hack_timestamp >= cutoff_timestamp:
                                            page_hacks.append(hack)
                                            all_past_cutoff = False
                                        # If hack is older than cutoff, don't include it
                                    except (ValueError, TypeError):
                                        # If we can't parse the date, include it anyway
                                        page_hacks.append(hack)
                                        all_past_cutoff = False
                                else:
                                    # If no time data, include it anyway
                                    page_hacks.append(hack)
                                    all_past_cutoff = False
                            
                            all_results.extend(page_hacks)
                            
                            # Log page results for debugging
                            from datetime import datetime
                            oldest_date = datetime.fromtimestamp(oldest_timestamp).strftime("%Y-%m-%d") if oldest_timestamp else "Unknown"
                            self._log(f"Page {page}: Found {len(page_hacks)}/{len(hacks)} hacks within time period. Oldest: {oldest_date}", "Information")
                            
                            # OPTIMIZATION: If this page has fewer than 50 hacks (typical page size),
                            # we've reached the end of available data from the API
                            expected_page_size = 50  # SMWCentral typical page size
                            if len(hacks) < expected_page_size:
                                self._log(f"Page {page} returned {len(hacks)} hacks (less than {expected_page_size}), reached end of data", "Information")
                                break
                            
                            # If all hacks on this page are past the cutoff date, stop searching
                            if all_past_cutoff and len(hacks) > 0:
                                self._log(f"Reached time cutoff on page {page} (all hacks older than cutoff), stopping search", "Information")
                                break
                        else:
                            # No time filtering - include all results
                            all_results.extend(hacks)
                            
                            # OPTIMIZATION: Still check for end of data even without time filtering
                            expected_page_size = 50  # SMWCentral typical page size
                            if len(hacks) < expected_page_size:
                                self._log(f"Page {page} returned {len(hacks)} hacks (less than {expected_page_size}), reached end of data", "Information")
                                # Don't break here for non-time searches, let normal pagination handle it
                        
                        # Update status
                        if self.search_cancelled:
                            return
                        
                        if len(search_modes) > 1:  # Searching both types
                            hack_type = "waiting" if waiting_mode else "moderated"
                            self.frame.after(0, lambda: self.results.set_status(
                                f"🔍 Found {len(all_results)} hacks so far... (searching {hack_type})"
                            ))
                        else:  # Only searching moderated
                            self.frame.after(0, lambda: self.results.set_status(
                                f"🔍 Found {len(all_results)} hacks so far..."
                            ))
                        
                        # Check if we've reached the last page (API tells us)
                        if page >= result.get("last_page", 1):
                            self._log(f"Reached last page ({page}) according to API", "Information")
                            break
                        
                        page += 1
                        
                    except Exception as e:
                        self._log(f"Error searching page {page}: {str(e)}", "Error")
                        break
            
            # Final check for cancellation before displaying results
            if self.search_cancelled:
                self._log("Search was cancelled, not displaying results", "Information")
                return
            
            # Update UI with results (no need for client-side time filtering now)
            self.frame.after(0, lambda: self.results.display_results(all_results, time_period))
            self.frame.after(0, lambda: self._search_completed())
            
        except Exception as e:
            # Don't log errors if the search was cancelled
            if not self.search_cancelled:
                self._log(f"Search failed: {str(e)}", "Error")
                self.frame.after(0, lambda: self._search_completed("❌ Search failed"))
    
    def _calculate_cutoff_timestamp(self, time_period):
        """Calculate the cutoff timestamp for time period filtering"""
        if time_period == "All Time":
            return None
        
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if time_period == "Last Week":
            cutoff_date = now - timedelta(weeks=1)
        elif time_period == "Last Month":
            cutoff_date = now - timedelta(days=30)
        elif time_period == "3 Months":
            cutoff_date = now - timedelta(days=90)
        elif time_period == "6 Months":
            cutoff_date = now - timedelta(days=180)
        elif time_period == "1 Year":
            cutoff_date = now - timedelta(days=365)
        else:
            return None
        
        cutoff_timestamp = int(cutoff_date.timestamp())
        self._log(f"Time period '{time_period}' cutoff: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} (timestamp: {cutoff_timestamp})", "Information")
        return cutoff_timestamp
    
    def _search_completed(self, status_text=None):
        """Handle search completion"""
        # Don't override if we're already cancelled
        if self.search_cancelled:
            return
            
        self.is_searching = False
        self.search_cancelled = False
        self.search_thread = None  # Clear thread reference
        self.filters.set_searching_state(False)
        if status_text:
            self.results.set_status(status_text)
        self._update_selection_display()
    
    def _update_selection_display(self):
        """Update the download button state based on selection"""
        count = self.results.get_selected_count()
        self.download_button_component.update_state(count)
    
    def _download_selected(self):
        """Download the selected hacks using the bulk download pipeline"""
        selected_hacks = self.results.get_selected_hacks()
        
        if not selected_hacks:
            messagebox.showwarning("No Selection", "Please select at least one hack to download.")
            return
        
        # Check if required settings are configured
        config = ConfigManager()
        base_rom_path = config.get("base_rom_path", "")
        output_dir = config.get("output_dir", "")
        
        # Validate required paths
        missing_paths = []
        if not base_rom_path:
            missing_paths.append("Base ROM Path")
        if not output_dir:
            missing_paths.append("Output Directory")
        
        if missing_paths:
            # Show dialog warning for missing settings
            missing_list = "\n• ".join([""] + missing_paths)
            messagebox.showerror(
                "Missing Required Settings",
                f"Please configure the following required settings in the Settings page before downloading:{missing_list}\n\n"
                f"Go to Settings → Setup to configure these paths."
            )
            return
        
        # Convert selected hacks to the format expected by the bulk download system
        hack_list = []
        for hack in selected_hacks:
            # Extract the properly formatted data
            raw_fields = hack.get("raw_fields", {})
            
            # Get type (handle list or string)
            hack_type = raw_fields.get("type") or hack.get("type", "")
            if isinstance(hack_type, list):
                hack_type = hack_type[0] if hack_type else ""
            
            # Get authors array
            authors_data = hack.get("authors", [])
            authors_list = []
            if isinstance(authors_data, list):
                for author in authors_data:
                    if isinstance(author, dict):
                        name = author.get("name", "")
                    else:
                        name = str(author)
                    if name:
                        authors_list.append(name)
            
            hack_list.append({
                "id": hack.get("id"),
                "name": hack.get("name"),
                "authors": authors_list,  # Pass as array
                "type": hack_type,  # Use the processed type string
                "difficulty": raw_fields.get("difficulty", ""),
                "rating": hack.get("rating"),
                "exit": raw_fields.get("length") or hack.get("length", 0),
                "date": hack.get("date"),
                "raw_fields": raw_fields  # Include raw_fields for compatibility
            })
        
        # Log the download initiation - removed duplicate message
        # self._log(f"🚀 Starting download of {len(hack_list)} selected hacks", "Information")
        
        # Set downloading state
        self.download_button_component.set_downloading(True)
        
        # Run download in background thread
        def download_worker():
            try:
                # Define progress callback to update button
                def progress_callback(current, total, hack_name):
                    self.frame.after(0, lambda: self.download_button_component.update_progress(current, total, hack_name))
                
                self.run_pipeline_func(selected_hacks=hack_list, log=self._log, progress_callback=progress_callback)
            except Exception as e:
                self._log(f"❌ Failed to download: {str(e)}", "Error")
            finally:
                # Re-enable button
                self.frame.after(0, lambda: self.download_button_component.set_downloading(False))
                self.frame.after(0, lambda: self._update_selection_display())
        
        # Start download in background thread
        download_thread = threading.Thread(target=download_worker, daemon=True)
        download_thread.start()
    
    def _cancel_download(self):
        """Cancel the current download operation"""
        try:
            from api_pipeline import cancel_operation
            cancel_operation()
            self._log("🛑 Download cancellation requested by user", "Information")
            
            # Reset button state
            self.download_button_component.set_downloading(False)
            self._update_selection_display()
        except ImportError:
            self._log("❌ Could not import cancel_operation - cancellation not available", "Error")
        except Exception as e:
            self._log(f"❌ Error during download cancellation: {str(e)}", "Error")
    
    def show(self):
        """Called when the page becomes visible"""
        if self.frame:
            self._log("📋 Single Download page loaded - ready to search and download individual hacks", "Information")
    
    def hide(self):
        """Called when the page becomes hidden"""
        pass
    
    def get_download_button(self):
        """Return the download button reference for external access"""
        return self.download_button_component.get_button() if self.download_button_component else None
