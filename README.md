## 🛠️ SMWCentral Downloader & Patcher

**SMWCentral Downloader & Patcher** is a Python GUI tool built to automate downloading, patching, and organizing Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net/). It integrates custom filters and Flips patching to help users maintain a clean, difficulty-sorted archive of `.smc` files.

### ✅ Features
- Choose Hack type: Standard, Kaizo, Puzzle, Tool-Assisted, Pit
- Choose Hack difficulty: Newcomer, Casual, Skilled, Advanced, Expert, Master, Grandmaster
- Includes all SMWCentral filter options
  - Hall of Fame
  - SA-1
  - Collab
  - Demo
- Automatically download `.bps` patches from SMWCentral
- Apply patches using [Flips](https://github.com/Alcaro/Flips) (must be installed separately)
- Use SMWCentral metadata to fix incorrect difficulty classification
- Discard unnecessary files—only the patched `.smc` is kept
- Organize output folders by difficulty
- Simple Tkinter interface
- Optional `.exe` build via PyInstaller

### 📦 Requirements
- Python 3.9+
- Recommended: VS Code or any IDE
- Required packages:
  ```bash
  pip install requests beautifulsoup4
  ```

### 🖥️ Usage
1. Launch `main.py`.
2. Select the difficulty and hack type you want.
3. Choose whether to exclude demo hacks.
4. Start the download and patching process.
5. Find your patched `.smc` files sorted in folders by difficulty.

### 🗂️ Folder Structure
Patched hacks are saved based on their type > difficulty attributes:
```
/Output Folder
  /Kaizo
    /01 - Newcomer
      Hack Name.smc
    /02 - Casual
      Hack Name.smc
  /Standard
    /01 - Newcomer
      Hack Name.smc
    /02 - Casual
      Hack Name.smc
```

### 🧪 Optional Executable
To run as a standalone executable:
1. Install [PyInstaller](https://pyinstaller.org/):  
   ```bash
   pip install pyinstaller
   ```
2. Run:  
   ```bash
   pyinstaller main.spec
   ```
3. Use the generated `.exe` in the `dist` folder.

### 🔧 Config and Customization
- `config.json`: tweak folder paths or patching options
- `processed.json`: keeps track of already patched hacks
