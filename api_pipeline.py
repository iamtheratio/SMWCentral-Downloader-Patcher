import requests
import os
import tempfile
import subprocess
import time
from utils import (
    safe_filename, get_sorted_folder_name,
    DIFFICULTY_LOOKUP, DIFFICULTY_KEYMAP,
    load_processed, save_processed, make_output_path
)
from patcher import title_case

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
        log(f"[DEBUG] API Request URL:\n{req.url}", level="Debug")

    for attempt in range(3):
        try:
            response = requests.get("https://www.smwcentral.net/ajax.php", params=params)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 5))
                if log:
                    log(f"[WARN] Rate limited. Retrying in {wait_time}s...", level="Error")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Failed to fetch data from SMWC API after retries.")

def fetch_file_metadata(file_id):
    r = requests.get("https://www.smwcentral.net/ajax.php", params={"a": "getfile", "v": "2", "id": file_id})
    r.raise_for_status()
    return r.json()

def patch_with_flips(flips_path, bps_path, base_rom, output_path):
    subprocess.run([flips_path, "--apply", bps_path, base_rom, output_path], check=True)

def extract_bps_from_zip(zip_path, extract_to):
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    for root, _, files in os.walk(extract_to):
        for fname in files:
            if fname.lower().endswith(".bps"):
                return os.path.join(root, fname)
    return None

def run_pipeline(filter_payload, flips_path, base_rom_path, output_dir, log=None):
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

    title_to_id = {entry["title"]: pid for pid, entry in processed.items()}

    for hack in all_hacks:
        hack_id = str(hack["id"])
        raw_title = hack["name"]
        title_clean = title_case(safe_filename(raw_title))
        raw_diff = hack.get("raw_fields", {}).get("difficulty", "")
        display_diff = DIFFICULTY_LOOKUP.get(raw_diff, "Unknown")
        type_str = filter_payload["type"][0].capitalize()

        file_meta = fetch_file_metadata(hack_id)
        download_url = file_meta.get("download_url")

        # Detect replacements
        existing_id = title_to_id.get(title_clean)
        if existing_id and existing_id != hack_id:
            processed.pop(existing_id)
            if log:
                log(f"✅ Patched: {title_clean} - Replaced with a new version!")
            continue

        if hack_id in processed:
            if log:
                log(f"✅ Skipped: {title_clean}")
            continue

        temp_dir = tempfile.mkdtemp()
        try:
            zip_path = os.path.join(temp_dir, "hack.zip")
            r = requests.get(download_url)
            with open(zip_path, "wb") as f:
                f.write(r.content)

            bps_path = extract_bps_from_zip(zip_path, temp_dir)
            if not bps_path:
                raise Exception(".bps file not found")

            output_filename = f"{title_clean}.smc"
            folder_name = get_sorted_folder_name(display_diff)
            output_path = os.path.join(make_output_path(output_dir, type_str, folder_name), output_filename)

            # Patch the ROM
            patch_with_flips(flips_path, bps_path, base_rom_path, output_path)

            # Log success
            if log:
                log(f"✅ Patched: {title_clean}")

            processed[hack_id] = {
                "title": title_clean,
                "current_difficulty": display_diff,
                "type": type_str
            }
            save_processed(processed)

        except Exception as e:
            if log: log(f"❌ Failed: {title_clean} → {e}", level="Error")
