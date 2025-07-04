# 🕹️ SMW Hack Patcher

A Python-based GUI tool to scrape, patch, and organize Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net). It uses user-defined filters and patching logic via Flips to create a clean, difficulty-sorted archive of patched `.smc` files.

---

## ⚙️ Features

- ✅ Select difficulty tiers and hack type (Kaizo, Standard, Pit)
- 🚫 Filter out demo hacks
- 🔽 Download `.bps` patches directly from SMWCentral
- 🧠 Detect and correct difficulty classification based on SMWC metadata
- 🧼 Only retain patched `.smc`; all other files discarded
- 🪜 Organize hacks into clean folders by difficulty
- 🖥️ Simple Tkinter GUI
- 📦 Packaged into an `.exe` with PyInstaller (optional)

---

## 🧪 Setup Instructions

### Requirements

- Python 3.9+
- VS Code (recommended)
- Required modules:
  ```bash
  pip install requests beautifulsoup4
