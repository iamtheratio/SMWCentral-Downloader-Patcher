# SMWC Downloader & Patcher

🎮 **Download and play Super Mario World ROM hacks with one click**

A simple desktop app that automatically downloads, patches, and organizes ROM hacks from SMWCentral. Works on Windows, Mac, and Linux.

![App Screenshot](images/ss_app_dashboard_v4.3.png)

## 🎯 App Features

### Browse & Download
![Download View](images/ss_app_download_v4.3.png)

### Manage Your Collection
![History View](images/ss_app_history_v4.3.png)

### Customize Settings
![Settings View](images/ss_app_settings_v4.3.png)

## 📥 Download & Install

### Windows (10/11)
1. Download `SMWC-Downloader-Windows-x64.zip` from the [Releases page](../../releases)
2. Extract the ZIP file to any folder you want (like your Desktop or Program Files)
3. Double-click `SMWC Downloader.exe` to run the app
4. **If Windows shows a security warning**: Click "More info" → "Run anyway" (this is normal for new apps)

### Mac (macOS 10.15+)
1. Download `SMWC-Downloader-macOS-Universal.dmg` from the [Releases page](../../releases)
2. Open the DMG file and drag the app to your Applications folder
3. **First time only**: Right-click the app → "Open" → "Open" (to bypass security warning)
4. After that, you can launch it normally from Applications or Spotlight

### Linux (Ubuntu, Debian, Fedora, etc.)
1. Download `SMWC-Downloader-Linux-x64.tar.gz` from the [Releases page](../../releases)
2. Extract: `tar -xzf SMWC-Downloader-*.tar.gz`
3. Run the installer: `./install.sh` (this adds the app to your Applications menu)
4. Launch from Applications menu or run `smwc-downloader` in terminal

## 🚀 How to Use

### First Time Setup
1. **Launch the app** - it will open to the main dashboard
2. **Set your ROM folder**: Click the folder icon to choose where you want your patched ROMs saved
3. **Add your base ROM**: Click "Browse" next to "Super Mario World ROM" and select your clean SMW ROM file
4. **You're ready!** The app will remember these settings

### Downloading ROM Hacks
1. **Browse hacks**: The main screen shows all available hacks from SMWCentral
2. **Filter and search**: Use the search box or filters to find specific hacks
3. **View details**: Click on any hack to see screenshots, description, and ratings
4. **Download**: Click the "Download" button - the app handles everything automatically
5. **Play**: Your patched ROM will be saved to your chosen folder, ready to play in any emulator

### Managing Your Collection
1. **View downloaded hacks**: Click the "History" tab to see all your downloaded ROMs
2. **Organize**: Sort by name, author, date downloaded, or rating
3. **Re-download**: If you lose a ROM, just download it again from your history
4. **Open folder**: Click the folder icon to quickly open where your ROMs are stored

### App Settings
- **Download location**: Change where ROMs are saved
- **Auto-updates**: Choose if you want automatic app updates
- **Theme**: Switch between light and dark modes
- **API settings**: Adjust download speed and connection settings

## ✨ Key Features

- **Automatic patching**: Downloads the hack and applies it to your ROM automatically
- **Smart organization**: Keeps track of what you've downloaded and when
- **Built-in screenshots**: See what hacks look like before downloading
- **Rating system**: Community ratings help you find the best hacks
- **Search and filter**: Find specific hacks by name, author, difficulty, or type
- **Auto-updates**: App keeps itself updated with new features
- **Cross-platform**: Identical experience on Windows, Mac, and Linux

## 🛠️ Troubleshooting

### Windows Security Warning
Windows may show "Windows protected your PC" when running the app. This is normal for new applications. Click "More info" → "Run anyway" to continue.

### Mac Security Warning
macOS may say the app is from an "unidentified developer." Right-click the app → "Open" → "Open" to bypass this. You only need to do this once.

### Linux: App Won't Start
If the app won't launch, install these packages:
- **Ubuntu/Debian**: `sudo apt install python3-tk`
- **Fedora**: `sudo dnf install tkinter`

### Can't Find Downloaded ROMs
Check the folder path shown in Settings. By default, ROMs are saved to:
- **Windows**: `Desktop\SMWCentral Hacks\`
- **Mac**: `Desktop/SMWCentral Hacks/`
- **Linux**: `~/Desktop/SMWCentral Hacks/`

### ROM Won't Patch
Make sure you have a clean, unmodified Super Mario World ROM. The app works with both US and Japanese versions.

## 📝 What You Need

- **Your Operating System**: Windows 10+, macOS 10.15+, or modern Linux
- **A clean SMW ROM**: Unmodified Super Mario World ROM file (.smc or .sfc)
- **Storage space**: About 20 MB for the app, plus space for your ROM collection
- **Internet connection**: Required for downloading hacks and app updates
- **An emulator**: To play your patched ROMs (SNES9x, RetroArch, etc.)

## 🔄 Updates

The app automatically checks for updates when you start it. When an update is available, you'll see a notification. Click "Update" to download and install the latest version. Your settings and downloaded ROMs are preserved during updates.

---

**Made for the Super Mario World ROM hacking community** ❤️