# patcher.py
import requests
import zipfile
import tempfile
import os
from utils import safe_filename, get_sorted_folder_name, make_output_path
from bps_patcher import patch_bps_safe

def title_case(name):
    return ' '.join(word.capitalize() for word in name.split())

def extract_bps_from_zip(zip_path, extract_to):
    """Extract BPS file from zip archive"""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    for root, _, files in os.walk(extract_to):
        for fname in files:
            if fname.lower().endswith(".bps"):
                return os.path.join(root, fname)
    return None

def patch_with_bps_library(bps_path, base_rom, output_path, log=None):
    """
    Apply BPS patch using the python-bps library
    """
    success, message = patch_bps_safe(base_rom, bps_path, output_path, log=log, verbose=True)
    if not success:
        raise Exception(f"BPS patching failed: {message}")
    
    if log:
        log(f"[DEBUG] BPS patching succeeded: {message}", level="Debug")

def process_and_patch_hack(hack, base_rom_path, output_dir, override_difficulty=None, log=None):
    """
    Process and patch a hack using BPS library (no Flips dependency)
    """
    if log:
        log(f"[DEBUG] Starting patch for: '{hack['title']}'", level="Debug")
        log(f"[DEBUG] Difficulty from config: '{override_difficulty}'", level="Debug")

    final_diff = get_sorted_folder_name(override_difficulty or "unknown")
    rom_type = hack.get("type", "Unknown")

    if log:
        log(f"[DEBUG] Final folder will be: '{rom_type}/{final_diff}'", level="Debug")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "hack.zip")

    # Download the hack
    r = requests.get(hack["download_url"])
    with open(zip_path, "wb") as f:
        f.write(r.content)

    # Extract BPS file
    bps_path = extract_bps_from_zip(zip_path, temp_dir)
    if not bps_path:
        raise Exception("BPS file not found in archive")

    # Get extension from base ROM
    base_rom_ext = os.path.splitext(base_rom_path)[1]  # Get .smc or .sfc
    title_clean = title_case(safe_filename(hack["title"]))
    output_filename = f"{title_clean}{base_rom_ext}"

    output_folder = make_output_path(output_dir, rom_type, final_diff)
    output_path = os.path.join(output_folder, output_filename)

    if log:
        log(f"[DEBUG] Saving patched ROM to → {output_path}", level="Debug")

    # Apply patch using our BPS library
    try:
        patch_with_bps_library(bps_path, base_rom_path, output_path, log)
        if log:
            log(f"[DEBUG] Successfully patched with BPS library", level="Debug")
    except Exception as bps_error:
        raise Exception(f"BPS patching failed: {bps_error}")

    if log:
        log(f"✅ Patched: {hack['title']} → Folder: '{final_diff}' → File: '{output_filename}'", level="Information")

    return True, final_diff
