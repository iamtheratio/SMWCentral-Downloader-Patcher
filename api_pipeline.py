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
    title_case, clean_hack_title  # ADDED: Import the new function
)
from smwc_api_proxy import smwc_api_get, get_api_delay
from patch_handler import PatchHandler

def fetch_hack_list(config, page=1, waiting_mode=False, log=None):
    """Fetch hack list - separated for moderated vs waiting hacks"""
    params = {"a": "getsectionlist", "s": "smwhacks", "n": page, "u": "1" if waiting_mode else "0"}
    
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
        elif key != "waiting" and values:
            # FIXED: Special handling for different parameter types
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
            "authors": hack.get("authors", [])
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

            # CHANGED: Pass log function to patch handler
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
            
            # Update processed data
            processed[hack_id] = {
                "title": clean_hack_title(raw_title),  # CHANGED: Clean the title
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
                # ADDED: History tracking fields - preserve existing values
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
        "title": clean_hack_title(hack_data.get("title", "Unknown")),  # CHANGED: Clean the title
        "current_difficulty": hack_data.get("difficulty", "Unknown"),
        "folder_name": get_sorted_folder_name(hack_data.get("difficulty", "Unknown")),
        # Removed file_path for privacy - contains usernames
        "hack_type": hack_type.lower(),
        
        # CHANGED: Use actual API metadata as booleans
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
