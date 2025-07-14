# SMWC Downloader & Patcher v3.1

A comprehensive Python GUI tool that automates downloading, patching, and organizing Super Mario World ROM hacks from [SMWCentral.net](https://www.smwcentral.net/). Features built-in IPS/BPS patching, intelligent filtering, and a powerful hack history management system.

## 🚀 Quick Start

1. **Download** the [latest release](https://github.com/iamtheratio/SMWCentral-Downloader-Patcher/releases/latest)
2. **Extract** to your preferred folder
3. **Run** `SMWC Downloader.exe`
4. **Setup** paths:
   - Clean SMW ROM (headerless .smc recommended)
   - Output directory
   - Optional: Adjust API delay slider if needed
5. **Select** hack type, difficulty, and filters
6. **Click** Download & Patch

![Bulk Interface](/images/ss_app_bulk_v3.1.png)

> [!IMPORTANT]
> ### ⚠️ Security Software Note
> Some antivirus software may flag this program. This is a **false positive** caused by the executable packaging.
> 
> **Solutions:**
> - Add an exclusion in your antivirus for the download folder
> - Use the "More info" → "Run anyway" option in Windows SmartScreen
> - Download the source code and run with Python if concerned
> - Verify the file hash against the published value in the release notes
>
> The application is open-source, and the code can be inspected on GitHub.

## 🆕 v3.1 Migration Guide

### For Existing Users

If you've used a previous version, **v3.1 will automatically upgrade your database** when you first open the app. Here's what to expect:

#### Migration Process

1. **Automatic Detection**: The app detects your old format and shows a migration dialog
2. **Backup Creation**: Your existing data is backed up to `processed.json.pre-v3.1.backup`
3. **API Enhancement**: Fetches real metadata from SMWC (Hall of Fame, SA-1, Collaboration, Demo status)
4. **New Features**: Adds Time to Beat tracking, Authors, and Exit count data
5. **Progress Dialog**: Shows real-time progress with detailed logging
6. **Privacy Cleanup**: Removes file paths from your data for privacy

#### What Changes

**Before v3.0:**
```json
{
  "12345": {
    "title": "Super Mario World",
    "current_difficulty": "Expert", 
    "hack_type": "kaizo"
  }
}
```

**After v3.1:**
```json
{
  "12345": {
    "title": "Super Mario World",
    "current_difficulty": "Expert",
    "hack_type": "kaizo", 
    "hall_of_fame": true,
    "sa1_compatibility": false,
    "collaboration": false,
    "demo": false,
    "exits": 14,
    "authors": [
      {
        "id": 12345,
        "name": "AuthorName"
      }
    ],
    "completed": false,
    "completed_date": "",
    "personal_rating": 0,
    "notes": "",
    "time_to_beat": 0
  }
}
```

#### Migration Results

- ✅ **99.8% API Success Rate**: Fetches real SMWC metadata for nearly all hacks
- 🔐 **Privacy Protected**: File paths removed automatically
- 📊 **Enhanced Data**: Hall of Fame, SA-1, Collaboration, Demo flags added
- 📝 **History Ready**: Completion tracking and rating system enabled
- ⏱️ **Time Tracking**: Time to Beat field added for performance analysis
- 👥 **Author Data**: Author information and IDs from SMWC
- 🚪 **Exit Counts**: Number of exits for each hack when available
- 📊 **Analytics Ready**: Data structure optimized for dashboard analytics

#### If Migration Fails

- Your original data is safely backed up
- You can restore from `processed.json.pre-v3.1.backup`
- Contact support with error details

## ✨ Key Features

### 🏠 Dashboard Page *(Enhanced in v3.1)*

![Dashboard Interface](/images/ss_app_dashboard_v3.1.png)

A comprehensive analytics dashboard providing insights into your hack completion journey:

#### Performance Analytics
- **📊 Overview Cards**: Total hacks, completion rate, average rating, and completion velocity
- **📈 Time Progression Chart**: Visual analysis of completion times by difficulty over 6 months
- **🎯 Efficiency Metrics**: Average time per hack and per exit for performance tracking
- **🔥 Streak Tracking**: Current and longest completion streaks with velocity indicators
- **💡 Smart Guidance**: Helpful messages guide users to enter time data for analytics

#### Advanced Filtering
- **📅 Date Filters**: Last week, month, 3 months, 6 months, or all-time data
- **📊 Interactive Charts**: Line charts with type filtering and difficulty-based color coding
- **🏆 Dynamic Updates**: Real-time recalculation based on selected time periods
- **🎯 Reorganized Layout**: Logical grouping of hack-focused vs exit-focused metrics

### 🏠 Bulk Download Page
- **Types**: Standard, Kaizo, Puzzle, Tool-Assisted, Pit
- **Difficulties**: Newcomer → Grandmaster + **"No Difficulty"** option
- **Filters**: Hall of Fame, SA-1, Collab, Demo
- **Mixed Selection**: Combine multiple difficulties (e.g., "Expert + No Difficulty")
- **Waiting Hacks**: Option to include hacks pending moderation

### 📚 Hack History Page *(NEW in v3.0)*

![Hack History Interface](/images/ss_app_hackhistory_v3.1.png)

A complete hack management system for tracking your ROM hack journey:

#### Table Features
- **Smart Filtering**: Name search, type, difficulty, completion status, rating, and metadata filters
- **Sortable Columns**: Click headers to sort by any field
- **Real-time Search**: Name filter updates as you type
- **Status Overview**: Shows total hacks, filtered count, and completion statistics

#### Interactive Editing
- **✓ Completion Checkbox**: Click to mark hacks complete/incomplete
- **⭐ Star Ratings**: Click stars to rate hacks 1-5 (click same rating to clear)
- **📅 Completion Date**: Click to edit completion dates with smart validation
- **📝 Notes**: Click to add personal notes (280 character limit)
- **🔄 Auto-sync**: Completion date automatically sets when marking complete

#### Advanced Filtering
- **Name Search**: Find hacks by title (partial matching)
- **Type Filter**: Standard, Kaizo, Puzzle, Tool-Assisted, Pit
- **Difficulty Filter**: Newcomer through Grandmaster (logical order)
- **Completion Filter**: Show only completed, incomplete, or all hacks
- **Rating Filter**: Filter by your star ratings (1-5 stars)
- **Metadata Filters**: Hall of Fame, SA-1, Collaboration, Demo status
- **Clear All**: Reset all filters instantly
- **Refresh**: Reload data from file

#### Data Management
- **Double-click Details**: View comprehensive hack information
- **Real-time Updates**: Changes save immediately and update display
- **Smart Validation**: Date format checking and note length limits
- **Undo Protection**: All changes backed up automatically
- **💾 Auto-Save Protection**: Refresh operations automatically save pending changes to prevent data loss

### Smart Processing
- **Built-in Patching**: No external tools needed - handles IPS & BPS formats
- **Auto-Organization**: Files sorted by type/difficulty into numbered folders
- **Update Detection**: Automatically replaces older versions
- **API Rate Control**: Adjustable delay slider (0-3 seconds) to prevent throttling

### Enhanced Experience
- **Tabbed Interface**: Switch between Bulk Download and Hack History
- **Modern UI**: Dark/light themes with Windows titlebar integration
- **Clean Logging**: Organized progress with colored message levels
- **Log Controls**: Clear button and Ctrl+L keyboard shortcut for log management
- **Intelligent Filtering**: Special handling for hacks without difficulty ratings
- **Error Recovery**: Robust handling of network issues and malformed files

## 🗂️ File Organization

```
/Output Folder
  /Kaizo
    /01 - Newcomer/
    /02 - Casual/
    /03 - Skilled/
    /04 - Advanced/
    /05 - Expert/
    /06 - Master/
    /07 - Grandmaster/
    /08 - No Difficulty/    # For unrated hacks
  /Standard
    /01 - Newcomer/
    /08 - No Difficulty/
```

## ⚙️ Configuration

The app saves settings in `config.json`:
```json
{
  "base_rom_path": "path/to/clean.smc",
  "output_dir": "path/to/output",
  "api_delay": 0.8
}
```

**Hack history and progress** saved in `processed.json`:
```json
{
  "12345": {
    "title": "Example Hack",
    "current_difficulty": "Expert",
    "hack_type": "kaizo",
    "hall_of_fame": true,
    "sa1_compatibility": false,
    "collaboration": false,
    "demo": false,
    "exits": 14,
    "authors": [
      {
        "id": 12345,
        "name": "AuthorName"
      }
    ],
    "completed": true,
    "completed_date": "2025-01-15",
    "personal_rating": 4,
    "notes": "Amazing level design!",
    "time_to_beat": 7200
  }
}
```

**API Delay Slider**: Adjust if experiencing rate limiting (higher = slower but more reliable)

## 📋 Requirements

- Windows 10/11
- Clean Super Mario World ROM file
- Internet connection for SMWC API

## 🆕 What's New in v3.1

### 🎯 Major Features
- **📚 Hack History Page**: Complete hack management system with tracking, ratings, notes, and advanced filtering
- **🔄 Smart Database Migration**: Automatic upgrade from previous versions with API enhancement
- **🏷️ Real Metadata**: Hall of Fame, SA-1, Collaboration, and Demo flags fetched from SMWC
- **⭐ Personal Tracking**: Completion status, dates, star ratings, and personal notes
- **🎨 Tabbed Interface**: Navigate between Bulk Download and Hack History pages
- **📊 Advanced Dashboard Analytics**: Time progression charts, completion analytics, and performance metrics
- **⏱️ Time to Beat Tracking**: Record and analyze completion times for hacks
- **🚀 Enhanced Download Pipeline**: Improved cancellation support and Unicode filename handling
- **🛡️ Data Protection**: Auto-save system prevents data loss during operations

### 📊 Dashboard Analytics Features
- **📈 Time Progression Charts**: Visual analysis of completion times by difficulty over 6 months
- **🎯 Performance Metrics**: Average completion time per hack and per exit
- **📋 Completion Analytics**: Breakdown by difficulty, type, and rating distribution
- **🔥 Streak Tracking**: Current and longest completion streaks
- **🏆 Advanced Filtering**: Last week, month, 3 months, 6 months, or all-time data
- **📊 Interactive Charts**: Line charts with type filtering and difficulty-based color coding
- **💡 User Guidance**: Clear instructions when no data is available for analytics
- **📐 Improved Layout**: Reorganized metrics for better logical grouping

### 📚 Hack History Features
- **Interactive Table**: Click to edit completion status, ratings, dates, and notes
- **Smart Filtering**: 9 different filter types including name search and metadata
- **Real-time Validation**: Date format checking and automatic data sync
- **Completion Tracking**: Mark hacks complete with automatic date setting
- **Star Ratings**: 5-star rating system with visual feedback
- **Personal Notes**: Add detailed notes with character limit protection
- **⏱️ Time Recording**: Track completion times for performance analysis
- **🛡️ Data Safety**: Automatic save protection prevents loss during refresh operations

### 🛠️ Technical Improvements
- **Database Migration**: Seamless upgrade from v2.x with 99.8% API success rate
- **Privacy Protection**: File paths automatically removed during migration
- **Enhanced API**: Bulk metadata fetching with rate limiting and retry logic
- **Modular Architecture**: Separated page components for better maintainability
- **Improved Logging**: Enhanced debug output and user-friendly messages
- **🔧 Download Cancellation**: Full cancellation support with proper cleanup
- **🌍 Unicode Support**: Handles special characters and emojis in hack titles
- **🎨 Theme-Aware UI**: Consistent styling across light and dark themes
- **🛡️ Data Integrity**: Auto-save protection and improved error handling
- **📊 Analytics Engine**: Optimized calculations for dashboard metrics

### 🎨 UI/UX Enhancements
- **Navigation Tabs**: Clean tab system for switching between pages
- **Consistent Theming**: Unified dark/light theme across all components
- **Better Iconography**: Application icon on all dialogs and popups
- **Responsive Design**: Improved layout and spacing throughout
- **Status Indicators**: Real-time feedback on data loading and filtering
- **📊 Visual Charts**: Interactive line charts with hover effects and legends

## 🔧 Technical Notes

**"No Difficulty" Processing**: Due to SMWC API limitations, selecting "No Difficulty" downloads ALL hacks then filters locally. This takes longer but finds hacks that weren't properly categorized.

**"Include Waiting" Option**: Fetches both moderated hacks and those pending moderation. Provides access to the newest submissions.

**File Formats**: Supports .smc/.sfc ROMs and .ips/.bps patches with automatic header detection.

**Database Migration**: v3.1 automatically detects older formats and upgrades them with enhanced metadata including Time to Beat tracking, author data, and exit counts. Process is fully automated and includes backup creation.

**Difficulty Ordering**: Logical progression from Newcomer → Casual → Skilled → Advanced → Expert → Master → Grandmaster.

**Time Tracking**: Completion times are stored in seconds and automatically converted to hours for display in analytics. Charts show rolling 6-month averages for trend analysis.

**Unicode Support**: Filename handling supports special characters, emojis, and international text. Files are automatically converted to emulator-compatible formats while preserving original display names.

**Cancellation System**: Full pipeline cancellation with proper cleanup, thread management, and user feedback. Safely stops downloads and file operations without corruption.

## 📦 Building from Source

```bash
pip install -r requirements.txt
python main.py
```

**Dependencies**: `tkinter`, `requests`, `sv-ttk`, `pywinstyles`

## 📄 Full Changelog

<details>
<summary>Click to expand version history</summary>

### v3.1.0 - Enhanced Analytics, Time Tracking & Download Improvements
- **NEW: Advanced Dashboard Analytics** - Time progression charts and performance metrics
  - 📈 Time progression line charts with 6-month rolling analysis
  - 🎯 Average completion time per hack and per exit tracking
  - 📊 Interactive charts with type filtering and difficulty color coding
  - 🔥 Completion streak tracking and velocity calculations
  - 🏆 Advanced date filtering (last week, month, 3 months, 6 months, all-time)
- **NEW: Time to Beat Tracking** - Record and analyze completion times
  - ⏱️ Time recording functionality in hack history
  - 📈 Performance analytics and trend visualization
  - 🎯 Exit-based efficiency calculations
- **NEW: Enhanced Download Pipeline** - Improved user experience
  - 🚀 Full cancellation support with proper cleanup and logging
  - 🌍 Unicode filename support for special characters and emojis
  - 🎨 Theme-aware cancel button styling
  - 📋 Improved error handling and user feedback
- **NEW: Author & Exit Data** - Enhanced hack metadata
  - 👥 Author information with IDs from SMWC API
  - 🚪 Exit count data for difficulty assessment
  - 📊 Comprehensive metadata structure for analytics
- **Enhanced Hack History Page** - Additional functionality
  - ⏱️ Time to beat recording and editing
  - 📊 Performance metrics integration
  - 🔄 Improved data synchronization
  - 🛡️ Auto-save protection during refresh operations
- **Dashboard Analytics Improvements** - Better user experience
  - 📐 Reorganized layout with logical metric grouping
  - 💡 Helpful guidance messages for empty charts
  - 🎯 Fixed completion rate calculations
  - 📊 Improved legend display and chart spacing
- **Technical Improvements**
  - 🏗️ Modular dashboard architecture with analytics engine
  - 📊 Optimized data processing for large datasets
  - 🎨 Consistent theme handling across all components
  - 🔧 Enhanced error handling and validation
  - 🛡️ Data protection with auto-save before refresh operations
  - 📐 Improved chart layouts and legend spacing

### v2.5.0 - Waiting Hacks & UI Improvements
- Added "Include Waiting" option for pending hacks
- Log clearing functionality (button + Ctrl+L)
- Fixed pagination for large result sets
- Centralized color management system
- Automatic duplicate hack detection
- Improved API delay slider precision (0.1 increments)
- Enhanced logging for waiting vs. moderated hacks

### v2.4.0 - "No Difficulty" & API Controls
- Added "No Difficulty" filtering option
- User-configurable API delay slider
- Mixed difficulty selection support
- Enhanced logging with orange warnings
- Improved folder organization for unrated hacks

### v2.3.0 - API Rate Limiting
- Centralized SMWC API proxy
- Dynamic delay calculation
- Improved error handling for large batches

### v2.2.0 - Modern UI & Theming
- Sun Valley dark/light theme system
- Windows titlebar theming
- Built-in IPS/BPS patch support
- Error-only log level
- Modular architecture redesign

### v2.1.0 - Flexible Filtering
- Optional difficulty selection
- Fixed Tool-Assisted hack API keys
- Improved folder naming consistency

### v2.0.0 - Built-in Patching
- Removed Flips dependency
- Unified IPS/BPS patch handler
- Automatic header detection
- Enhanced error recovery
</details>

---

**Note**: This tool respects SMWC's terms of service and implements rate limiting to avoid server overload. Please use responsibly.
