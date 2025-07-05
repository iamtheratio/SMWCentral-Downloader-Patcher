import requests
import os
import tempfile
import subprocess
import time
from utils import (
    safe_filename, get_sorted_folder_name,
    DIFFICULTY_LOOKUP, DIFFICULTY_KEYMAP,
    load_processed, save_processed, make_output_path,
    TYPE_KEYMAP, TYPE_DISPLAY_LOOKUP
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

        file_meta = fetch_file_metadata(hack_id)
        download_url = file_meta.get("download_url")

        temp_dir = tempfile.mkdtemp()
        try:
            zip_path = os.path.join(temp_dir, "hack.zip")
            r = requests.get(download_url)
            with open(zip_path, "wb") as f:
                f.write(r.content)

            bps_path = extract_bps_from_zip(zip_path, temp_dir)
            if not bps_path:
                raise Exception(".bps file not found")

            output_filename = f"{title_clean}{base_rom_ext}"
            output_path = os.path.join(make_output_path(output_dir, normalized_type, folder_name), output_filename)

            patch_with_flips(flips_path, bps_path, base_rom_path, output_path)

            if log:
                log(f"✅ Patched: {title_clean}")

            processed[hack_id] = {
                "title": title_clean,
                "current_difficulty": display_diff,
                "type": TYPE_DISPLAY_LOOKUP.get(normalized_type, normalized_type)
            }
            save_processed(processed)

        except Exception as e:
            if log:
                log(f"❌ Failed: {title_clean} → {e}", level="Error")
