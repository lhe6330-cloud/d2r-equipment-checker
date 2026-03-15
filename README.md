# D2R Equipment Checker

A desktop application for searching and filtering Diablo 2 Resurrected equipment listings on DD373.com.

## Features

- **Search by gear type**: Amulet, Ring, Charm, Jewel, Weapon, Shield, Hat, Armor, Glove, Belt, Boots
- **Ladder/Non-Ladder filtering**: Search specific game modes
- **Attribute filters**: Filter by FCR, skills, resistances, life, MF, and 100+ other attributes
- **Dual currency display**: Shows prices in both CNY and USD
- **Task list**: Queue multiple searches to run automatically
- **Order list**: Track items you want to buy with filled/unfilled status
- **CSV export**: Export your order list for sharing with sellers

## Quick Start (Using Pre-built EXE)

1. Download `D2R_Equipment_Checker.exe`
2. Double-click to run
3. No installation required!

## Building the EXE Yourself

### Requirements
- Windows 10/11
- Python 3.9 or higher

### Option 1: Easy Build (Recommended)
1. Extract all files to a folder
2. Double-click `build.bat`
3. Wait for the build to complete
4. Find your exe in the `dist` folder

### Option 2: Manual Build
```batch
# Install dependencies
pip install -r requirements.txt

# Build executable
pyinstaller --onefile --windowed --name "D2R_Equipment_Checker" --add-data "d2rcheck.ui;." d2rcheck.py
```

### Option 3: Run from Source
```batch
pip install -r requirements.txt
python d2rcheck.py
```

## Usage Guide

### Basic Search
1. Select **Gear Type** (e.g., Amulet)
2. Check **Non-Ladder** and/or **Ladder**
3. Optionally enter a **Keyword** (e.g., "rare", "crafted")
4. Click **Start Search**

### Using Attribute Filters
Filter results by stat values:
- `fcr` - Faster Cast Rate
- `str` / `dex` / `vit` / `energy` - Attributes
- `life` / `mana` - Life/Mana bonuses
- `all res` / `fire res` / `light res` / `cold res` / `poison res` - Resistances
- `mf` - Magic Find
- `frw` - Faster Run/Walk
- `ed` - Enhanced Damage/Defense
- `+skills` / `+2` / `+3` - Skill bonuses
- `socket` - Number of sockets
- `eth` - Ethereal (use min=1 to filter for eth items)

Example: To find 20+ FCR amulets with 15+ all res:
- Filter 1: `fcr` Min: `20`
- Filter 2: `all res` Min: `15`

### Task List
Queue multiple searches to run automatically:
1. Set up your search criteria
2. Click **Add Task**
3. Repeat for other searches you want
4. Click **Run All** to execute all tasks
5. Results appear in **Task Results**

### Order List
Track items you want to purchase:
1. Click **Add** on any item to add to order list
2. Check the **Filled** box when you've purchased an item
3. Use **Export CSV** to share your list with sellers
4. **Clear Filled** removes purchased items

## Configuration

Edit `config.py` to adjust:
```python
CNY_TO_USD_RATE = 0.14  # Exchange rate (1 CNY = X USD)
PAGE_DELAY_SECONDS = 5   # Delay between page requests
REQUEST_TIMEOUT = 15     # HTTP timeout in seconds
```

## File Structure
```
d2rcheck_refactored/
├── d2rcheck.py          # Main entry point
├── d2rcheck.ui          # UI layout file
├── config.py            # Configuration and constants
├── models.py            # Data structures
├── main_window.py       # UI controller
├── crawler.py           # Web scraping logic
├── data_manager.py      # Data persistence
├── attribute_filter.py  # Filtering logic
├── widgets.py           # Custom UI widgets
├── build.bat            # Windows build script
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Troubleshooting

**"Python is not installed"**
- Download Python from https://python.org
- During install, check "Add Python to PATH"

**"Module not found" errors**
- Run: `pip install -r requirements.txt`

**App doesn't start**
- Make sure `d2rcheck.ui` is in the same folder
- Try running from command line to see error messages

**No search results**
- Check your internet connection
- The site may be temporarily unavailable
- Try a broader search (fewer filters)

## License

For personal use only. Not affiliated with Blizzard Entertainment or DD373.com.
