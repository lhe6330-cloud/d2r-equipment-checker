# D2R Equipment Checker User Guide

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Features](#features)
4. [Getting Started](#getting-started)
5. [Exchange Rate Settings](#exchange-rate-settings)
6. [Keyword Search](#keyword-search)
7. [Attribute Filters](#attribute-filters)
8. [Task List](#task-list)
9. [Order List](#order-list)
10. [FAQ](#faq)

---

## Introduction

**D2R Equipment Checker** is a specialized tool designed for Diablo 2 Resurrected players to search and filter equipment from the DD373 platform. It supports multi-condition filtering, batch search, price monitoring, and more.

**Version**: V3.7.0  
**Platform**: Windows 10/11  
**Language**: Chinese/English

---

## Installation

### Method 1: Direct EXE (Recommended)

1. Download `D2R_Equipment_Checker.exe`
2. Double-click to run
3. No installation or Python required

### Method 2: Run from Source

```bash
# 1. Install Python 3.9+
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the program
python d2rcheck.py
```

---

## Features

### ✅ Core Features

- **Equipment Search**: Automatically search D2R equipment from DD373
- **Keyword Filtering**: 175+ preset keywords (Amazon, Paladin, Sorceress, etc.)
- **Attribute Filtering**: 100+ attributes (FCR, MF, Resistances, Skills, etc.)
- **Dual Currency**: Display prices in both CNY and USD
- **Custom Exchange Rate**: Support custom rate with real-time refresh
- **Task List**: Batch search tasks with auto-execution
- **Order Management**: Save interested items and export order list

### ✅ V3.7.0 New Features

- **Chinese Keyword Input**: Auto-fill Chinese when English keyword selected
- **Manual Input Support**: Support custom keyword search
- **Real-time Rate Refresh**: One-click refresh all prices after rate change

---

## Getting Started

### 1. Launch Program

Double-click `D2R_Equipment_Checker.exe` to start

### 2. Select Gear Type

Choose from dropdown:
- Amulet
- Ring
- Charm
- Jewel
- Weapon
- Shield
- Hat
- Armor
- Glove
- Belt
- Boots

### 3. Select Mode

- **nonladder**: Non-Ladder mode
- **ladder**: Ladder mode
- **warlock ladder**: Warlock Ladder
- **warlock nonladder**: Warlock Non-Ladder

### 4. Enter Keyword

**Method 1: Select English Keyword**
1. Select English keyword from Keyword dropdown (e.g., "Amazon")
2. Chinese input box auto-fills corresponding Chinese (e.g., "亚马逊")
3. Search uses Chinese content

**Method 2: Manual Chinese Input**
1. Directly type Chinese keyword in the right input box
2. Example: "法师", "德鲁伊"
3. Press Enter to confirm

**Method 3: Custom Keyword**
1. If your keyword is not in Excel
2. Directly type in Chinese input box
3. Program will use input content for search

### 5. Set Attribute Filters (Optional)

Up to 3 filter conditions:

| Attribute | Min | Max |
|-----------|-----|-----|
| fcr       | 20  |     |
| all res   | 15  |     |
| mf        | 100 | 200 |

**Common Attributes**:
- `fcr`: Faster Cast Rate
- `mf`: Magic Find
- `all res`: All Resistances
- `str`: Strength
- `vit`: Vitality
- `life`: Life
- `socket`: Sockets
- `eth`: Ethereal

### 6. Start Search

Click **Start Search** button

### 7. View Results

Search results displayed in table:
- **Stats**: Detailed attribute list
- **Price (CNY)**: Chinese Yuan price
- **Price (USD)**: US Dollar price (auto-converted by exchange rate)
- **Link**: Click to open item page
- **Add**: Add to order list

---

## Exchange Rate Settings

### Modify Exchange Rate

1. Find exchange rate input box in **Exchange Rate** section
2. Enter new rate (default: 6.8, meaning 1 USD = 6.8 CNY)
3. Click **🔄 Refresh Prices** button
4. All prices will update automatically

### Rate Persistence

- Rate auto-saves to `settings.json`
- Auto-loads on next program start
- Can be modified anytime

---

## Keyword Search

### Preset Keywords

Program includes 175+ keywords:

#### Class Keywords
- Amazon
- Paladin
- Sorceress
- Necromancer
- Barbarian
- Druid
- Assassin

#### Attribute Keywords
- Faster cast rate
- Magic find
- All res
- Life steal
- Enhanced Damage

### Usage Tips

1. **Quick Search**: Type first few letters, dropdown auto-filters
   - Type "ama" → Shows "Amazon", "Amulet", etc.
   - Type "res" → Shows "all res", "fire resistance", etc.

2. **Chinese Search**: Select English keyword, Chinese auto-fills
   - Select "Amazon" → Auto-fills "亚马逊"
   - Can directly modify Chinese content

3. **Custom Keywords**: If preset keywords don't meet needs
   - Directly type in Chinese input box
   - Example: "暗黑", "毁灭", etc.

---

## Attribute Filters

### Special Attributes (No Value Required)

These attributes only need to exist:
- `socket`: Has sockets
- `eth`: Ethereal
- `tp`: Teleport
- `erep`: Auto-repair

### Numeric Attributes (Value Required)

These attributes need numeric range:
- `fcr`: Faster Cast Rate (e.g., 20-30)
- `mf`: Magic Find (e.g., 100-200)
- `life`: Life (e.g., 50-)
- `all res`: All Resistances (e.g., 15-)

### Filter Logic

- Multiple filter conditions use **AND** logic
- Equipment must match ALL conditions to display

---

## Task List

### Add Task

1. Set search conditions (gear type, keyword, mode, filters)
2. Click **Add Task** button
3. Task added to task list

### Execute Tasks

1. **Run All**: Execute all tasks
2. **Skip**: Skip current task
3. **Next**: Next task
4. **Stop**: Stop execution

### Task Management

- **Save Task List**: Save tasks to file
- **Import Task List**: Import tasks from file
- **Clear Task List**: Clear all tasks

---

## Order List

### Add Item to Order

1. Find interested item in search results
2. Click **Add** button
3. Item added to order list

### Order Management

- **Mark as Filled**: Check "Filled" checkbox
- **Export CSV**: Click **Export CSV** to export order list
- **Clear Filled**: Click **Clear Filled** to remove purchased items
- **Mark All Unfilled**: Click **Mark All Unfilled**

### Export Format

Exported CSV includes:
- Item stats
- Price (CNY/USD)
- Link
- Purchase status

---

## FAQ

### Q1: Program won't start?

**A**: Ensure Windows 10/11 is installed. For source run, Python 3.9+ required.

### Q2: Search results empty?

**A**: 
- Check network connection
- Try reducing filter conditions
- Confirm keyword spelling is correct

### Q3: Exchange rate not updating?

**A**: 
- After entering new rate, click **🔄 Refresh Prices**
- Ensure rate is positive number

### Q4: How to save settings?

**A**: 
- Exchange rate auto-saves to `settings.json`
- Task list requires manual save

### Q5: Keyword not in list?

**A**: 
- Directly type custom keyword in Chinese input box
- Program will use input content for search

### Q6: How to report issues?

**A**: 
- GitHub Issues: https://github.com/lhe6330-cloud/d2r-equipment-checker/issues

---

## 📞 Technical Support

- **GitHub**: https://github.com/lhe6330-cloud/d2r-equipment-checker
- **Version**: V3.7.0
- **Last Updated**: 2026-03-15

---

**Happy Gaming! 🎮**
