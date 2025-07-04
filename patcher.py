import requests
import zipfile
import tempfile
import subprocess
import os
from bs4 import BeautifulSoup
from utils import safe_filename, get_sorted_folder_name

def fetch_download_url(hack_page_url):
    res = requests.get(hack_page_url)
    soup = BeautifulSoup(res.content, "html.parser")
    download_tag = soup.find("a", string="Download")
    if download_tag:
        download_url = download_tag["href"]
        if download_url.startswith("http"):
            return download_url
        return f"https://www.smwcentral.net{download_url}"
    return None

def extract_bps_from_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    for root, dirs, files in os.walk(extract_to):
        for fname in files:
            if fname.lower().endswith(".bps"):
                return os.path.join(root, fname)
    return None

def patch_with_flips(flips_path, bps_path, base_rom, output_path):
    subprocess.run([
        flips_path, "--apply",
        bps_path,
        base_rom,
        output_path
    ], check=True)

def title_case(name):
    return ' '.join(word.capitalize() for word in name.split())

def process_and_patch_hack(hack, flips_path, base_rom_path, output_dir, override_difficulty=None):
    print(f"[DEBUG] Starting patch for: '{hack['title']}'")
    print(f"[DEBUG] Difficulty from scrape: '{override_difficulty}'")

    final_diff = get_sorted_folder_name(override_difficulty or "unknown")
    rom_type = hack.get("type", "Unknown")

    print(f"[DEBUG] Final folder will be: '{rom_type}/{final_diff}'")

    temp_dir = tempfile.mkdtemp()
    download_url = fetch_download_url(hack["url"])
    if not download_url:
        raise Exception("Download link not found")

    zip_path = os.path.join(temp_dir, "hack.zip")
    r = requests.get(download_url)
    with open(zip_path, "wb") as f:
        f.write(r.content)

    bps_path = extract_bps_from_zip(zip_path, temp_dir)
    if not bps_path:
        raise Exception(".bps file not found in archive")

    title_clean = title_case(safe_filename(hack["title"]))
    output_filename = f"{title_clean}.smc"

    output_folder = os.path.join(output_dir, rom_type, final_diff)
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, output_filename)
    print(f"[DEBUG] Saving patched ROM to → {output_path}")
    patch_with_flips(flips_path, bps_path, base_rom_path, output_path)

    print(f"✅ Patched: {hack['title']} → Folder: '{final_diff}' → File: '{output_filename}'")
    return True, final_diff
