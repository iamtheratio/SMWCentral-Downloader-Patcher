import requests
import os
import tempfile
import time

from utils import (
    safe_filename, get_sorted_folder_name,
    DIFFICULTY_LOOKUP, DIFFICULTY_KEYMAP,
    load_processed, save_processed, make_output_path,
    TYPE_KEYMAP, TYPE_DISPLAY_LOOKUP,
    title_case  # REMOVED: get_api_delay - import from smwc_api_proxy instead
)
from smwc_api_proxy import smwc_api_get, get_api_delay  # ADDED: get_api_delay import
from patch_handler import PatchHandler

def fetch_hack_list(config, page=1, log=None):
    params = {"a": "getsectionlist", "s": "smwhacks", "n": page}
    for key, values in config.items():
        if key == "difficulties" and values:
            converted = [f"diff_{DIFFICULTY_KEYMAP[d]}" for d in values if d in DIFFICULTY_KEYMAP]
            params["f[difficulty][]"] = converted
        elif values:
            for val in values:
                params.setdefault(f"f[{key}][]", []).append(val)
    if log:
        req = requests.Request("GET", "https://www.smwcentral.net/ajax.php", params=params).prepare()
        log(f"[DEBUG] API Request URL:\n{req.url}", level="debug")
    response = smwc_api_get("https://www.smwcentral.net/ajax.php", params=params, log=log)
    return response.json().get("data", [])

def fetch_file_metadata(file_id, log=None):
    params = {"a": "getfile", "v": "2", "id": file_id}
    response = smwc_api_get("https://www.smwcentral.net/ajax.php", params=params, log=log)
    return response.json()

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
    page = 1
    if log: log("🔎 Starting download...")

    while True:
        hacks = fetch_hack_list(filter_payload, page=page, log=log)
        if log: log(f"📄 Page {page} returned {len(hacks)} entries")
        if not hacks or len(hacks) < 50:
            all_hacks.extend(hacks)
            break
        all_hacks.extend(hacks)
        page += 1

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
        display_diff = DIFFICULTY_LOOKUP.get(raw_diff, "Unknown")
        folder_name = get_sorted_folder_name(display_diff)

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
                        log(f"⚠️ Expected to move {title_clean}, but source file not found: {actual_path}", "Error")
            else:
                if log:
                    log(f"✅ Skipped: {title_clean}")
            continue

        file_meta = fetch_file_metadata(hack_id, log=log)
        download_url = file_meta.get("download_url")

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

            # Update processed data
            processed[hack_id] = {
                "title": raw_title,
                "current_difficulty": display_diff,
                "folder_name": folder_name,
                "file_path": output_path
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

        # Add delay logging for file downloads
        delay = get_api_delay()
        if log:
            log(f"[DEBUG] Waiting {delay:.1f} seconds before next request.", level="debug")
        time.sleep(delay)
