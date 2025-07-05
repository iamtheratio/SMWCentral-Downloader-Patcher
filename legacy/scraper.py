import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from patcher import process_and_patch_hack
from utils import load_processed, save_processed, sanitize_name, DIFFICULTY_LOOKUP

BASE_URL = "https://www.smwcentral.net/?p=section&s=smwhacks"

def normalize_key(key):
    return key.lower().replace("_", "").replace("-", "").replace(" ", "")

def build_filtered_url(config, page_number=1):
    query_params = {
        "n": page_number,
        "f[type][]": config.get("type", [])
    }

    for key in ["hof", "sa1", "collab", "demo"]:
        val = config.get(key)
        if val in ("1", "0"):
            query_params[f"f[{key}]"] = val

    normalized_lookup = {
        normalize_key(k): v for k, v in DIFFICULTY_LOOKUP.items()
    }

    query_params["f[difficulty][]"] = [
        normalized_lookup[normalize_key(d)]
        for d in config.get("difficulties", [])
        if normalize_key(d) in normalized_lookup
    ]

    return f"{BASE_URL}&{urlencode(query_params, doseq=True)}"

def scrape_hack_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    hack_rows = soup.select("table.list tbody tr")

    hacks = []
    for row in hack_rows:
        columns = row.find_all("td")
        if len(columns) < 3:
            continue

        title_tag = columns[0].find("a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        href = title_tag["href"]
        full_url = f"https://www.smwcentral.net{href}" if href.startswith("/") else href
        hack_id = href.split("id=")[-1] if "id=" in href else href.split("/")[-1]

        folder_difficulty = columns[2].text.strip()
        print(f"[TRACE] '{title}' → Difficulty: '{folder_difficulty}'")

        hacks.append({
            "id": hack_id,
            "title": title,
            "url": full_url,
            "difficulty": folder_difficulty
        })
    return hacks

def run_scraper_pipeline(config, flips_path, base_rom_path, output_dir, log=None):
    processed = load_processed()
    all_hacks = []
    page = 1

    while True:
        url = build_filtered_url(config, page_number=page)
        if log:
            log(f"📄 Fetching page {page}: {url}")
        hacks = scrape_hack_page(url)

        if not hacks:
            if log:
                log(f"⚠️ No more hacks on page {page}. Stopping.")
            break

        all_hacks.extend(hacks)
        if len(hacks) < 50:
            if log:
                log(f"✅ Page {page} returned fewer than 50 entries.")
            break
        page += 1

    if log:
        log(f"📦 Found {len(all_hacks)} total hacks.")

    hack_type = config["type"][0] if isinstance(config["type"], list) else config["type"]
    display_type = hack_type.capitalize()

    for hack in all_hacks:
        hack_id = hack["id"]
        title = sanitize_name(hack["title"])
        difficulty = hack["difficulty"]

        print(f"[TRACE] Patching '{title}' → Difficulty: '{difficulty}'")

        if hack_id in processed:
            msg = f"✅ Already processed: {title}"
            print(msg)
            if log: log(msg)
            continue

        hack["type"] = display_type

        try:
            success, final_difficulty = process_and_patch_hack(
                hack, flips_path, base_rom_path, output_dir, override_difficulty=difficulty
            )
            if success:
                processed[hack_id] = {
                    "title": title,
                    "current_difficulty": final_difficulty,
                    "type": display_type
                }
                save_processed(processed)
                msg = f"✅ Success: {title} → '{hack['type']} / {final_difficulty}'"
                print(msg)
                if log: log(msg)
            else:
                msg = f"❌ Failed to patch: {title}"
                print(msg)
                if log: log(msg)
        except Exception as e:
            msg = f"❌ Error processing {title}: {e}"
            print(msg)
            if log: log(msg)
