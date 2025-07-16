import requests
import os
import tempfile
import time
from datetime import datetime

from utils import (
    safe_filename, get_sorted_folder_name,
    DIFFICULTY_LOOKUP, DIFFICULTY_KEYMAP,
    load_processed, save_processed, make_output_path,
    TYPE_KEYMAP, TYPE_DISPLAY_LOOKUP,
    title_case, clean_hack_title  # Import the new function
)
from smwc_api_proxy import smwc_api_get, get_api_delay
from patch_handler import PatchHandler

# Global cancellation flag
_cancel_operation = False

def cancel_pipeline():
    """Cancel the current pipeline operation"""
    global _cancel_operation
    _cancel_operation = True

def reset_cancel_flag():
    """Reset the cancellation flag"""
    global _cancel_operation
    _cancel_operation = False

def is_cancelled():
    """Check if operation was cancelled"""
    global _cancel_operation
    return _cancel_operation

def fetch_hack_list(config, page=1, waiting_mode=False, log=None):
    """Fetch hack list - separated for moderated vs waiting hacks"""
    params = {"a": "getsectionlist", "s": "smwhacks", "n": page, "u": "1" if waiting_mode else "0"}
    
    # Add order parameter if specified
    if "order" in config:
        params["o"] = config["order"]
    
    # Handle difficulty filtering with "No Difficulty" support
    difficulties = config.get("difficulties", [])
    has_no_difficulty = "no difficulty" in difficulties
    regular_difficulties = [d for d in difficulties if d != "no difficulty"]
    
    for key, values in config.items():
        if key == "difficulties" and values:
            if regular_difficulties and not has_no_difficulty:
                converted = []
                for d in regular_difficulties:
                    if d in DIFFICULTY_KEYMAP:
                        diff_key = DIFFICULTY_KEYMAP[d]
                        if diff_key:
                            converted.append(f"diff_{diff_key}")
                if converted:
                    params["f[difficulty][]"] = converted
        elif key == "name" and values:
            # Handle name search - direct text search
            params["f[name]"] = values
        elif key == "author" and values:
            # Handle author search - direct text search
            params["f[author]"] = values
        elif key == "tags" and values:
            # Handle tags search - comma-separated
            if isinstance(values, list):
                params["f[tags]"] = ", ".join(values)
            else:
                params["f[tags]"] = values
        elif key == "description" and values:
            # Handle description search - direct text search
            params["f[description]"] = values
        elif key != "waiting" and values:
            # Special handling for different parameter types
            if key == "type":
                # Type parameter always needs array format
                if isinstance(values, list):
                    params["f[type][]"] = values
                else:
                    params["f[type][]"] = [values]
            else:
                # Other filters (hof, demo, sa1, collab) use single format when single value
                if isinstance(values, list) and len(values) > 1:
                    # Multiple values - use array format
                    for val in values:
                        params.setdefault(f"f[{key}][]", []).append(val)
                elif isinstance(values, list) and len(values) == 1:
                    # Single value in list - use single format
                    params[f"f[{key}]"] = values[0]
                elif not isinstance(values, list):
                    # Single value - use single format
                    params[f"f[{key}]"] = values
    
    response = smwc_api_get("https://www.smwcentral.net/ajax.php", params=params, log=log)
    response_data = response.json()
    raw_data = response_data.get("data", [])
    
    # Log pagination info on first page
    if page == 1 and log:
        total = response_data.get("total", 0)
        last_page = response_data.get("last_page", 1)
        hack_type = "waiting" if waiting_mode else "moderated"
        log(f"📊 Found {total} {hack_type} hacks across {last_page} pages", level="information")
    
    # Return both data and pagination info
    return {
        "data": raw_data,
        "last_page": response_data.get("last_page", page),
        "current_page": response_data.get("current_page", page)
    }

def fetch_file_metadata(file_id, log=None):
    params = {"a": "getfile", "v": "2", "id": file_id}
    response = smwc_api_get("https://www.smwcentral.net/ajax.php", params=params, log=log)
    
    if response:
        try:
            # The API returns data directly, not nested under "data"
            data = response.json()
            # Wrap in "data" key for backward compatibility with existing code
            return {"data": data}
        except Exception as e:
            if log:
                log(f"Error parsing file metadata JSON: {e}", "Error")
            return None
    return None

def extract_patches_from_zip(zip_path, extract_to, hack_name=""):
    """Extract zip and find patch files (IPS or BPS)"""
    import zipfile
    import re
    
    # Extract zip contents
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Test integrity first
            bad_file = zip_ref.testzip()
            if bad_file:
                raise zipfile.BadZipFile(f"Bad zip file, first bad file: {bad_file}")
            zip_ref.extractall(extract_to)
    except Exception as e:
        raise e
    
    # Find all patch files (IPS and BPS)
    patch_files = []
    for root, _, files in os.walk(extract_to):
        for fname in files:
            if fname.lower().endswith((".ips", ".bps")):
                patch_files.append(os.path.join(root, fname))
    
    if not patch_files:
        return None
    
    # If only one patch file exists, use it
    if len(patch_files) == 1:
        return patch_files[0]
    
    # Multiple patch files found, use selection strategy
    
    # Try to match with hack name if provided
    if hack_name:
        hack_name_simple = re.sub(r'[^a-zA-Z0-9]', '', hack_name.lower())
        for patch_file in patch_files:
            file_name = os.path.basename(patch_file).lower()
            file_name_simple = re.sub(r'[^a-zA-Z0-9]', '', file_name)
            if hack_name_simple in file_name_simple:
                return patch_file
    
    # Look for common main patch indicators
    main_indicators = ["main", "patch", "rom", "smc", "sfc"]
    for indicator in main_indicators:
        for patch_file in patch_files:
            if indicator in os.path.basename(patch_file).lower():
                return patch_file
    
    # Exclude common auxiliary patches
    exclude_indicators = ["music", "graphics", "optional", "extra", "addon"]
    filtered_files = [f for f in patch_files if not any(
        indicator in os.path.basename(f).lower() for indicator in exclude_indicators
    )]
    
    if filtered_files:
        # Use the largest remaining file (often the main patch)
        return max(filtered_files, key=os.path.getsize)
    
    # If all else fails, use the largest patch file
    return max(patch_files, key=os.path.getsize)

def run_pipeline(filter_payload, base_rom_path, output_dir, log=None):
    """
    Main pipeline function using unified patch handler
    """
    # Reset cancellation flag at start
    reset_cancel_flag()
    
    processed = load_processed()
    all_hacks = []
    if log: log("🔎 Starting download...")

    # Check if we need to do post-collection filtering
    difficulties = filter_payload.get("difficulties", [])
    has_no_difficulty = "no difficulty" in difficulties
    regular_difficulties = [d for d in difficulties if d != "no difficulty"]
    needs_post_filtering = has_no_difficulty and not regular_difficulties
    
    # Add warning for "No Difficulty" selections
    if has_no_difficulty:
        if log:
            log("[WRN] 'No Difficulty' selected - downloading ALL hacks then filtering locally due to SMWC API limitations", level="warning")

    # PHASE 1: Fetch all moderated hacks (u=0)
    page = 1
    while True:
        # Check for cancellation
        if is_cancelled():
            if log: log("❌ Operation cancelled by user", "warning")
            return
            
        page_result = fetch_hack_list(filter_payload, page=page, waiting_mode=False, log=log)
        
        hacks = page_result["data"]
        last_page = page_result.get("last_page", page)
        
        if not hacks:
            if log: log("📄 No more moderated pages available", level="information")
            break
        
        all_hacks.extend(hacks)
        
        if log: 
            log(f"📄 Moderated page {page} returned {len(hacks)} entries", level="information")
        
        # Stop if we've reached the last page
        if page >= last_page:
            if log: log(f"📄 Reached last moderated page ({last_page})", level="information")
            break
        
        page += 1

    # PHASE 2: Fetch waiting hacks if enabled (u=1)
    if filter_payload.get("waiting", False):
        page = 1
        while True:
            # Check for cancellation
            if is_cancelled():
                if log: log("❌ Operation cancelled by user", "warning")
                return
                
            page_result = fetch_hack_list(filter_payload, page=page, waiting_mode=True, log=log)
            
            waiting_hacks = page_result["data"]
            last_page = page_result.get("last_page", page)
            
            if not waiting_hacks:
                if log: log("📄 No more waiting pages available", level="information")
                break
            
            all_hacks.extend(waiting_hacks)
            
            if log: 
                log(f"📄 Waiting page {page} returned {len(waiting_hacks)} entries", level="information")
            
            # Stop if we've reached the last page
            if page >= last_page:
                if log: log(f"📄 Reached last waiting page ({last_page})", level="information")
                break
            
            page += 1

    # Remove duplicates (just in case)
    unique_hacks = []
    seen_ids = set()
    for hack in all_hacks:
        hack_id = hack.get('id')
        if hack_id not in seen_ids:
            unique_hacks.append(hack)
            seen_ids.add(hack_id)

    if len(all_hacks) != len(unique_hacks) and log:
        log(f"📦 Removed {len(all_hacks) - len(unique_hacks)} duplicates", level="information")
    
    all_hacks = unique_hacks

    # Post-collection filtering for "No Difficulty" scenarios
    if needs_post_filtering or (has_no_difficulty and regular_difficulties):
        if log:
            log(f"🔍 Filtering {len(all_hacks)} hacks for difficulty criteria...")
        
        filtered_hacks = []
        for hack in all_hacks:
            hack_difficulty = hack.get("raw_fields", {}).get("difficulty", "")
            
            if has_no_difficulty and not regular_difficulties:
                # ONLY "No Difficulty" selected
                if hack_difficulty == "" or hack_difficulty is None or hack_difficulty == "N/A":
                    filtered_hacks.append(hack)
            elif has_no_difficulty and regular_difficulties:
                # MIXED: Both "No Difficulty" AND regular difficulties
                selected_diff_keys = []
                for d in regular_difficulties:
                    if d in DIFFICULTY_KEYMAP:
                        diff_key = DIFFICULTY_KEYMAP[d]
                        if diff_key:
                            selected_diff_keys.append(f"diff_{diff_key}")
                
                # Include if: no difficulty OR matches selected difficulties
                if (hack_difficulty == "" or hack_difficulty is None or hack_difficulty == "N/A") or hack_difficulty in selected_diff_keys:
                    filtered_hacks.append(hack)
        
        if log:
            log(f"✅ Filtered to {len(filtered_hacks)} hacks matching criteria")
        
        all_hacks = filtered_hacks

    if log:
        log(f"📦 Found {len(all_hacks)} total hacks.")
        log("🧪 Starting patching...")

    base_rom_ext = os.path.splitext(base_rom_path)[1]

    # Normalize to internal key, NOT display name
    raw_type = filter_payload["type"][0]
    normalized_type = raw_type.lower().replace("-", "_")

    for hack in all_hacks:
        # Check for cancellation at the start of each hack processing
        if is_cancelled():
            if log: log("❌ Operation cancelled by user", "warning")
            return
            
        hack_id = str(hack["id"])
        raw_title = hack["name"]
        title_clean = title_case(safe_filename(raw_title))
        raw_diff = hack.get("raw_fields", {}).get("difficulty", "")
        
        # Fix: Handle None/empty difficulty values consistently
        if not raw_diff or raw_diff in [None, "N/A"]:
            raw_diff = ""
        
        display_diff = DIFFICULTY_LOOKUP.get(raw_diff, "No Difficulty")  # Changed default from "Unknown" to "No Difficulty"
        folder_name = get_sorted_folder_name(display_diff)

        # OPTIMIZED: Extract only the metadata fields we want to track and update
        raw_fields = hack.get("raw_fields", {})
        page_metadata = {
            "exits": raw_fields.get("length", hack.get("length", 0)) or 0,
            "hall_of_fame": bool(raw_fields.get("hof", False)),
            "sa1_compatibility": bool(raw_fields.get("sa1", False)), 
            "collaboration": bool(raw_fields.get("collab", False)),
            "demo": bool(raw_fields.get("demo", False)),
            "authors": hack.get("authors", []),
            "obsolete": bool(raw_fields.get("obsolete", False))  # NEW: Track obsolete status
        }

        if hack_id in processed:
            actual_diff = processed[hack_id].get("current_difficulty", "")
            actual_path = os.path.join(
                make_output_path(output_dir, normalized_type, get_sorted_folder_name(actual_diff)),
                f"{title_clean}{base_rom_ext}"
            )
            expected_path = os.path.join(
                make_output_path(output_dir, normalized_type, folder_name),
                f"{title_clean}{base_rom_ext}"
            )

            if actual_diff != display_diff and log:
                log(f"✅ Moved: {title_clean} from {actual_diff} to {display_diff} difficulty!")

            if actual_diff != display_diff or not os.path.exists(expected_path):
                if os.path.exists(actual_path):
                    try:
                        os.makedirs(os.path.dirname(expected_path), exist_ok=True)
                        os.rename(actual_path, expected_path)
                        processed[hack_id]["current_difficulty"] = display_diff
                        save_processed(processed)
                    except Exception as e:
                        if log:
                            log(f"❌ Failed to move: {title_clean} → {str(e)}", "Error")
                else:
                    if log:
                        log(f"⚠️ Source Not Found: Redownloading {title_clean}", "Warning")
                    # Don't continue here - fall through to redownload the hack
            else:
                if log:
                    log(f"✅ Skipped: {title_clean}")
                
                # OPTIMIZED: Still update metadata from page data even when skipping download
                existing_hack = processed.get(hack_id, {})
                for key, new_value in page_metadata.items():
                    old_value = existing_hack.get(key)
                    if old_value != new_value:
                        if log:
                            log(f"Updated: {title_clean} attribute {key} updated from {old_value} → {new_value}", "Information")
                        processed[hack_id][key] = new_value
                
                # Update title if it doesn't match the properly formatted version
                # This ensures processed.json gets updated with proper title case formatting
                # when running bulk download, even for hacks that already exist
                current_title = existing_hack.get("title", "")
                proper_title = clean_hack_title(raw_title)
                if current_title != proper_title:
                    if log:
                        log(f"Updated: {title_clean} title formatting updated from '{current_title}' → '{proper_title}'", "Information")
                    processed[hack_id]["title"] = proper_title
                
                # Update difficulty if it changed
                if processed[hack_id].get("current_difficulty") != display_diff:
                    processed[hack_id]["current_difficulty"] = display_diff
                
                save_processed(processed)
                continue

        # OPTIMIZED: Use download_url directly from page data (eliminates API call)
        download_url = hack.get("download_url")
        if not download_url:
            if log:
                log(f"❌ Error: No download URL found for {title_clean}", "Error")
            continue

        temp_dir = tempfile.mkdtemp()
        try:
            zip_path = os.path.join(temp_dir, "hack.zip")
            
            # Add debug logging for file download
            if log:
                log(f"[DEBUG] Downloading file: {download_url}", level="debug")
            
            r = requests.get(download_url)
            with open(zip_path, "wb") as f:
                f.write(r.content)

            patch_path = extract_patches_from_zip(zip_path, temp_dir, title_clean)
            if not patch_path:
                raise Exception("Patch file (.ips or .bps) not found in archive")

            output_filename = f"{title_clean}{base_rom_ext}"
            output_path = os.path.join(make_output_path(output_dir, normalized_type, folder_name), output_filename)

            # Pass log function to patch handler
            success = PatchHandler.apply_patch(patch_path, base_rom_path, output_path, log)
            if not success:
                raise Exception("Patch application failed")

            if log:
                log(f"✅ Patched: {title_clean}")

            # Check if hack exists and compare metadata for sync (v3.1 feature)
            existing_hack = processed.get(hack_id, {})
            metadata_changes = []
            
            # v3.1 OPTIMIZED: Use metadata from page data instead of individual API calls
            new_metadata = page_metadata.copy()  # Use the metadata extracted from page data
            
            # v3.1 NEW: Check for metadata changes and log them
            if existing_hack:
                for key, new_value in new_metadata.items():
                    old_value = existing_hack.get(key)
                    if old_value != new_value:
                        metadata_changes.append(f"{key}: {old_value} → {new_value}")
                        if log:
                            log(f"Updated: {title_clean} attribute {key} updated from {old_value} → {new_value}", "Information")
                
                # Check for title changes and log them
                # This ensures we log when title formatting is updated during re-download
                current_title = existing_hack.get("title", "")
                proper_title = clean_hack_title(raw_title)
                if current_title != proper_title:
                    if log:
                        log(f"Updated: {title_clean} title formatting updated from '{current_title}' → '{proper_title}'", "Information")
            
            # Update processed data
            processed[hack_id] = {
                "title": clean_hack_title(raw_title),  # Clean the title
                "current_difficulty": display_diff,
                "folder_name": folder_name,
                "file_path": output_path,
                "hack_type": normalized_type,
                # Only include the specific metadata fields we want to track
                "hall_of_fame": new_metadata.get("hall_of_fame", False),
                "sa1_compatibility": new_metadata.get("sa1_compatibility", False),
                "collaboration": new_metadata.get("collaboration", False),
                "demo": new_metadata.get("demo", False),
                "exits": new_metadata.get("exits", 0),
                "authors": new_metadata.get("authors", []),
                "obsolete": new_metadata.get("obsolete", False),  # NEW: Track obsolete status
                # History tracking fields - preserve existing values
                "completed": existing_hack.get("completed", False),
                "completed_date": existing_hack.get("completed_date", ""),
                "personal_rating": existing_hack.get("personal_rating", 0),
                "notes": existing_hack.get("notes", ""),
                "time_to_beat": existing_hack.get("time_to_beat", 0)  # v3.1 NEW: preserve existing time
            }
            save_processed(processed)

        except Exception as e:
            if log:
                log(f"❌ Error processing {title_clean}: {str(e)}", "Error")
        finally:
            # Clean up temp files
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

def save_hack_to_processed_json(hack_data, file_path, hack_type):
    """Save hack data with actual SMWC metadata to processed.json"""
    
    # Extract actual boolean values from SMWC API response
    processed_data = {
        "title": clean_hack_title(hack_data.get("title", "Unknown")),  # Clean the title
        "current_difficulty": hack_data.get("difficulty", "Unknown"),
        "folder_name": get_sorted_folder_name(hack_data.get("difficulty", "Unknown")),
        # Removed file_path for privacy - contains usernames
        "hack_type": hack_type.lower(),
        
        # Use actual API metadata as booleans
        "hall_of_fame": bool(hack_data.get("hall_of_fame", False)),
        "sa1_compatibility": bool(hack_data.get("sa1", False)),
        "collaboration": bool(hack_data.get("collaboration", False)), 
        "demo": bool(hack_data.get("demo", False)),
        
        # v3.1 NEW: Additional metadata fields
        "exits": hack_data.get("length", 0),  # API length becomes exits
        "authors": hack_data.get("authors", []),  # Authors array
        
        # History tracking fields
        "completed": False,
        "completed_date": "",
        "personal_rating": 0,
        "notes": "",
        "time_to_beat": 0  # v3.1 NEW: Time to beat in seconds
    }
    
    # Save to processed.json
    # ... existing save logic

def process_individual_hacks(selected_hacks, base_rom_path, output_dir, log=None):
    """Process a list of pre-selected hacks for download and patching"""
    if log: log(f"🎯 Processing {len(selected_hacks)} individually selected hacks...")
    
    processed = load_processed()
    patch_handler = PatchHandler(base_rom_path, output_dir, log)
    
    # Reset cancellation flag at start
    reset_cancel_flag()
    
    total_hacks = len(selected_hacks)
    successful_downloads = 0
    
    for i, hack in enumerate(selected_hacks, 1):
        # Check for cancellation
        if is_cancelled():
            if log: log("❌ Operation cancelled by user", "warning")
            break
        
        hack_id = hack.get("id")
        hack_name = hack.get("name", "Unknown")
        
        if log: log(f"📥 [{i}/{total_hacks}] Processing: {hack_name}")
        
        # Check if already processed
        if hack_id in processed:
            if log: log(f"⏭️ Skipping {hack_name} (already processed)")
            continue
        
        try:
            # Fetch detailed metadata
            file_metadata = fetch_file_metadata(hack_id, log)
            if not file_metadata:
                if log: log(f"❌ Could not fetch metadata for {hack_name}")
                continue
            
            # Merge hack data with detailed metadata
            full_hack_data = {**hack, **file_metadata}
            
            # Download and patch
            success = download_and_patch_hack(full_hack_data, patch_handler, processed, log)
            if success:
                successful_downloads += 1
                # Save progress after each successful download
                save_processed(processed)
            
        except Exception as e:
            if log: log(f"❌ Error processing {hack_name}: {str(e)}", "error")
            continue
    
    # Final report
    if log: 
        log(f"✅ Single download complete! Successfully processed {successful_downloads}/{total_hacks} hacks")
        if successful_downloads > 0:
            log(f"📁 Output location: {output_dir}")

def download_and_patch_hack(hack_data, patch_handler, processed, log=None):
    """Download and patch a single hack"""
    hack_id = hack_data.get("id")
    hack_name = hack_data.get("name", "Unknown")
    
    try:
        # Get download URL from metadata
        download_url = hack_data.get("download_url")
        if not download_url:
            if log: log(f"❌ No download URL for {hack_name}")
            return False
        
        # Create output folder
        difficulty = hack_data.get("difficulty", "")
        difficulty_name = DIFFICULTY_LOOKUP.get(difficulty, "No Difficulty")
        folder_name = get_sorted_folder_name(difficulty_name)
        
        authors = hack_data.get("authors", "Unknown")
        hack_type = hack_data.get("type", "")
        type_name = TYPE_DISPLAY_LOOKUP.get(hack_type, "Unknown")
        
        # Generate safe filename
        safe_name = safe_filename(hack_name)
        output_filename = f"{safe_name}.smc"
        
        # Download the hack file
        if log: log(f"⬇️ Downloading {hack_name}...")
        
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        # Create temporary file for the downloaded hack
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Process the hack file (extract and patch)
            result = patch_handler.process_hack_file(
                temp_path,
                output_filename,
                folder_name,
                {
                    "id": hack_id,
                    "name": hack_name,
                    "authors": authors,
                    "type": type_name,
                    "difficulty": difficulty_name,
                    "rating": hack_data.get("rating", "N/A"),
                    "exit": hack_data.get("exit", "N/A"),
                    "date": hack_data.get("date", "Unknown")
                }
            )
            
            if result["success"]:
                # Mark as processed
                processed[hack_id] = {
                    "name": hack_name,
                    "processed_date": datetime.now().isoformat(),
                    "output_path": result.get("output_path", ""),
                    "type": type_name,
                    "difficulty": difficulty_name,
                    "authors": authors,
                    "obsolete": False  # NEW: Default new hacks to not obsolete
                }
                
                if log: log(f"✅ Successfully processed {hack_name}")
                return True
            else:
                if log: log(f"❌ Failed to patch {hack_name}: {result.get('error', 'Unknown error')}")
                return False
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        if log: log(f"❌ Error downloading {hack_name}: {str(e)}")
        return False
