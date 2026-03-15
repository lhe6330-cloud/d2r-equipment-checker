"""
Configuration constants and mappings for DD373 D2R Equipment Checker.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import sys
import os


# =============================================================================
# File Paths - Handle both dev and bundled exe environments
# =============================================================================
def get_data_dir():
    """Get the directory for storing user data files."""
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled exe - store data next to the exe
        return os.path.dirname(sys.executable)
    # Running in normal Python environment
    return os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.'

DATA_DIR = get_data_dir()
OUTPUT_FILE = os.path.join(DATA_DIR, "output.txt")
ORDERLIST_FILE = os.path.join(DATA_DIR, "orderlist.json")
UI_FILE = "d2rcheck.ui"


# =============================================================================
# HTTP Configuration
# =============================================================================
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)
REQUEST_TIMEOUT = 15
PAGE_DELAY_SECONDS = 5

# =============================================================================
# Currency Configuration
# =============================================================================
CNY_TO_USD_RATE = 0.14  # 1 CNY ≈ 0.14 USD (adjust as needed)


def format_cny(price: str) -> str:
    """Format price as CNY."""
    try:
        clean_price = price.replace('¥', '').replace(',', '').strip()
        cny_value = float(clean_price)
        return f"¥{cny_value:.2f}"
    except (ValueError, AttributeError):
        return f"¥{price}"


def format_usd(price: str) -> str:
    """Convert CNY price to USD."""
    try:
        clean_price = price.replace('¥', '').replace(',', '').strip()
        cny_value = float(clean_price)
        usd_value = cny_value * CNY_TO_USD_RATE
        return f"${usd_value:.2f}"
    except (ValueError, AttributeError):
        return "N/A"


def format_price(cny_price: str) -> str:
    """
    Format price to show both CNY and USD.
    
    Args:
        cny_price: Price string in CNY (may contain ¥ symbol)
    
    Returns:
        Formatted string like "¥580 / $81"
    """
    try:
        # Clean the price string
        clean_price = cny_price.replace('¥', '').replace(',', '').strip()
        cny_value = float(clean_price)
        usd_value = cny_value * CNY_TO_USD_RATE
        return f"¥{cny_value:.0f} / ${usd_value:.2f}"
    except (ValueError, AttributeError):
        return f"¥{cny_price}"


# =============================================================================
# Task Status Icons
# =============================================================================
class TaskStatus(Enum):
    WAITING = "◯ waiting"
    CHECKING = "▶ checking"
    PAUSED = "⏸ pause"
    FINISHED = "✓ finished"
    STOPPED = "✗ stop"
    SKIPPED = "user skipped"


# =============================================================================
# Special Attributes (existence-based, no numeric value required)
# =============================================================================
SPECIAL_ATTRIBUTES: Dict[str, List[str]] = {
    'tp': ['tp', '传送', 'teleport', 'tele'],
    'erep': ['erep', '自动修复', '自回', '无形自回'],
    'eth': ['eth', '无形'],
    'lt': ['lt', 'lifetap', '偷取生命', '吸取生命'],
    'visio': ['visio', 'viso', '幻影', '幻视', '角色等级'],
    'fools': ['fools', 'visio', 'viso', '幻影'],
}


# =============================================================================
# Attribute Mappings (numeric value-based)
# =============================================================================
ATTRIBUTE_MAP: Dict[str, List[str]] = {
    # Basic stats
    'fcr': ['施法', '施法速度', 'fcr', '快速施法', '快速施法速度'],
    'str': ['力量', 'str', 'strength'],
    'dex': ['敏捷', 'dex', 'dexterity'],
    'vit': ['体能', 'vit', 'vitality', '生命', '体力'],
    'ene': ['精力', 'ene', 'energy', '法力', '能量'],
    
    # Resistances
    'all res': ['allres', 'resistance', '所有抗性'],
    'fr': ['火焰抗性', '火抗', 'fr', 'fire resistance'],
    'cr': ['冰冷抗性', '冰抗', 'cr', 'cold resistance'],
    'lr': ['闪电抗性', '电抗', 'lr', 'lightning resistance'],
    'pr': ['毒素抗性', '毒抗', 'pr', 'poison resistance'],
    
    # Magic find and gold
    'mf': ['mf', '寻宝', '魔法物品获得', '掉宝率', '寻魔'],
    'eg': ['eg', '打钱', '额外金币', '金币获得'],
    
    # Life and mana
    'life': ['生命', 'life', 'hp'],
    'mana': ['法力', 'mana', '魔法值'],
    
    # Defense and attack
    'def': ['防御', 'def', 'defense'],
    'ias': ['攻击速度', 'ias', 'attack speed'],
    'll': ['吸血', 'll', 'life steal', 'life leach', '生命偷取'],
    'lm': ['吸蓝', 'lm', 'mana steal', 'mana leach', '法力偷取', '魔法偷取'],
    'ed': ['伤害', 'damage', 'ed', '增强伤害'],
    'ar': ['准确率', 'ar', 'attack rating'],
    
    # Movement and recovery
    'frw': ['frw', '高跑', '跑'],
    'fhr': ['fhr', '打击恢复', '打击回复'],
    'replife': ['replife', '生命恢复', '生命回复', '回血'],
    
    # Special combat
    'cb': ['cb', '压碎打击', '粉碎性打击'],
    'ds': ['ds', '致命打击'],
    'socket': ['孔', 'socket', 'os'],
    
    # Damage
    'max': ['max', '最大伤害'],
    'min': ['min', '最小伤害'],
    
    # Necro/poison
    'pnb': ['pnb', '毒骨', '毒系'],
    'plr': ['plr', '毒缩', '中毒时间'],
    
    # Block
    'icb': ['icb', '增加格挡', 'ctb', '格挡'],
    
    # Ethereal
    'edef': ['edef', '防御强化', 'ed'],
    
    # Assassin skills
    'ls': ['ls', '雷光', 'Lightning Sentry'],
    'wof': ['wof', 'Wake of Fire', '火复苏', '火焰复生'],
    'bf': ['bf', 'blade fury', '狂怒旋刃', '飞镖', '刃之怒'],
    'sm': ['sm', '影子大师', 'Shadow Master'],
    'Venom': ['Venom', '毒牙', '淬毒'],
    'cos': ['cos', 'Cloak of Shadows', '魔影斗篷', '斗篷'],
    'Fade': ['Fade', '能量消解', '影散'],
    'cot': ['cot', 'Claws of Thunder', '雷电爪', '雷爪'],
    'boi': ['boi', 'Blades of Ice', '寒冰刃', '冰刃'],
    'ps': ['ps', 'Phoenix Strike', '凤凰击', '凤凰'],
    'dt': ['dt', 'Dragon Tail', '神龙摆尾', '龙尾'],
    'sin': ['sin', 'asn', '刺客'],
    'Shadow': ['Shadow', '暗影修行'],
    'trap': ['trap', '陷阱'],
    'bs': ['bs', '刃之盾', '刀刃之盾', '利刃之盾'],
    'Wb': ['Wb', '武器格挡', 'Weapon Block'],
    'sw': ['sw', '影子战士'],
    'FB': ['FB', 'Fire Blast', '火焰震爆', '火球'],
    
    # Curses
    'AMP': ['AMP', 'Amplify Damage', '伤害加深'],
    'Terror': ['Terror', '恐惧'],
    'Confuse': ['Confuse', '迷乱'],
    'Attract': ['Attract', '吸引'],
    'LT': ['Life Tap', 'LT', '偷取生命', '吸取生命'],
    'Decrep': ['Decrep', 'Decrepify', '衰老'],
    
    # Necro skills
    'BS': ['BS', 'bone spear', '骨矛'],
    'BSpirit': ['BSpirit', 'Bone Spirit', '骨魂'],
    'BP': ['BP', 'Bone Prison', '骨牢'],
    'BW': ['BW', 'Bone Wall', '骨墙'],
    
    # Paladin skills
    'Charge': ['Charge', '冲锋'],
    'Bh': ['Bh', 'Blessed Hammer', '祝福之锤'],
    'Conc': ['conc', 'Concentration', '专注'],
    'conv': ['conv', 'Conviction', '信念', '审判'],
    'Foh': ['Foh', 'Fist of the Heavens', '天堂之拳'],
    'Combat': ['Combat', '战斗技能'],
    'Offensive': ['Offensive', '攻击灵气'],
    
    # Sorceress cold skills
    'sa': ['sa', 'Shiver Armor', '碎冰甲'],
    'FN': ['fn', 'Frost Nova', '霜之新星'],
    'ca': ['ca', 'Chilling Armor', '寒冰装甲'],
    'Blizz': ['Blizz', 'Blizzard', '暴风雪'],
    'FO': ['FO', 'frozen orb', '冰封球'],
    'CM': ['CM', 'Cold Mastery', '寒冰专精', '冰冷掌握', '冰冷精通'],
    
    # Sorceress lightning skills
    'Nova': ['Nova', '新星', '闪电新星'],
    'Lightning': ['Lightning', '闪电', '闪电箭'],
    'CL': ['CL', 'Chain Lightning', '连锁闪电', '连闪'],
    'ts': ['ts', 'Thunder Storm', '雷云风暴'],
    'es': ['es', 'Energy Shield', '能量护盾'],
    'lmas': ['lmas', 'Lightning Mastery', '闪电专精', '闪电掌握', '闪电精通'],
    
    # Sorceress fire skills
    'fw': ['fw', 'Fire Wall', '火墙'],
    'Enchant': ['Enchant', '火焰强化', '强化'],
    'Meteor': ['Meteor', '陨石'],
    'Hydra': ['Hydra', '九头海蛇'],
    'fm': ['fm', 'Fire Mastery', '火焰专精', '火焰掌握', '火焰精通'],
    
    # Druid skills
    'Fissure': ['Fissure', '火山爆'],
    'Volc': ['Volc', 'Volcano', '火山'],
    'Cyclone': ['Cyclone', 'Cyclone ARMOR', '飓风装甲'],
    'nado': ['Tornado', 'nado', '龙卷风'],
    'Hurricane': ['Hurricane', '暴风'],
    'FS': ['Firestorm', 'FS', '火风暴'],
    'Maul': ['Maul', '撞槌'],
    'oak': ['oak', 'Oak Sage', '橡木'],
    'how': ['how', 'Heart of Wolverine', '狼獾'],
    'fury': ['fury', '狂怒'],
    
    # Golem skills
    'gm': ['gm', 'Golem Mastery', '石魔掌握', '魔像'],
    'fg': ['fg', 'Fire Golem', '火焰魔像'],
    'bg': ['bg', 'Blood Golem', '鲜血'],
    'cg': ['cg', 'Clay Golem', '黏土魔像'],
}


# =============================================================================
# Gear Type URL Templates
# =============================================================================
@dataclass
class GearTypeUrls:
    """URLs for a specific gear type with 5 mode options."""
    all: str
    ladder: str
    warlock_ladder: str
    warlock_nonladder: str
    nonladder: str


GEAR_TYPE_URLS: Dict[str, GearTypeUrls] = {
    'weapon': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-915cc3-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-915cc3-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-915cc3-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-915cc3-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-915cc3-0-0-0-0-0-0-0-0.html'
    ),
    'hat': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-fg6vuh-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-fg6vuh-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-fg6vuh-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-fg6vuh-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-fg6vuh-0-0-0-0-0-0-0-0.html'
    ),
    'shield': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-krwbfs-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-krwbfs-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-krwbfs-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-krwbfs-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-krwbfs-0-0-0-0-0-0-0-0.html'
    ),
    'armor': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-39bt7g-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-39bt7g-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-39bt7g-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-39bt7g-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-39bt7g-0-0-0-0-0-0-0-0.html'
    ),
    'belt': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-f3q9tg-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-f3q9tg-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-f3q9tg-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-f3q9tg-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-f3q9tg-0-0-0-0-0-0-0-0.html'
    ),
    'glove': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-uhd8dt-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-uhd8dt-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-uhd8dt-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-uhd8dt-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-uhd8dt-0-0-0-0-0-0-0-0.html'
    ),
    'boots': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-3s1baw-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-3s1baw-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-3s1baw-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-3s1baw-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-3s1baw-0-0-0-0-0-0-0-0.html'
    ),
    'ring': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-hquct0-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-hquct0-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-hquct0-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-hquct0-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-hquct0-0-0-0-0-0-0-0-0.html'
    ),
    'amulet': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-v41x85-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-v41x85-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-v41x85-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-v41x85-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-v41x85-0-0-0-0-0-0-0-0.html'
    ),
    'charm': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-uv1bd8-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-uv1bd8-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-uv1bd8-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-uv1bd8-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-uv1bd8-0-0-0-0-0-0-0-0.html'
    ),
    'jewel': GearTypeUrls(
        all='https://www.dd373.com/s-1psrbm-u6w1hm-0-0-0-0-5tgw08-0tc73c-0-0-0-0-0-0-0-0.html',
        ladder='https://www.dd373.com/s-1psrbm-u6w1hm-7wme4a-0-0-0-5tgw08-0tc73c-0-0-0-0-0-0-0-0.html',
        warlock_ladder='https://www.dd373.com/s-1psrbm-u6w1hm-hx35xs-0-0-0-5tgw08-0tc73c-0-0-0-0-0-0-0-0.html',
        warlock_nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-6mu7b4-0-0-0-5tgw08-0tc73c-0-0-0-0-0-0-0-0.html',
        nonladder='https://www.dd373.com/s-1psrbm-u6w1hm-dkcdwk-0-0-0-5tgw08-0tc73c-0-0-0-0-0-0-0-0.html'
    ),
}


def get_gear_type_url(gear_type: str, mode: str) -> str:
    """
    Get the search URL for a given gear type and mode.
    
    Args:
        gear_type: Type of gear (weapon, hat, shield, etc.) - case insensitive
        mode: Mode string (all, ladder, warlock ladder, warlock nonladder, nonladder)
    
    Returns:
        The appropriate search URL
    """
    gear_type_lower = gear_type.lower()
    
    # Handle alternate names
    gear_type_aliases = {
        'sheild': 'shield',  # Common typo
        'helm': 'hat',
        'helmet': 'hat',
        'circlet': 'hat',
        'gloves': 'glove',
        'boot': 'boots',
    }
    gear_type_lower = gear_type_aliases.get(gear_type_lower, gear_type_lower)
    
    # Normalize mode string (handle variations in input)
    mode_key = mode.lower().replace(' ', '_').replace('-', '_').replace(')', '')
    
    # Map common variations to standard keys
    mode_mapping = {
        'all': 'all',
        'ladder': 'ladder',
        'warlock_ladder': 'warlock_ladder',
        'warlock_nonladder': 'warlock_nonladder',
        'nonladder': 'nonladder',
        'nl_only': 'nonladder',
        'l_only': 'ladder',
        'both': 'all',
        'nonladder_ladder': 'all',  # Legacy support
    }
    mode_key = mode_mapping.get(mode_key, mode_key)
    
    # Get URLs for gear type
    gear_urls = GEAR_TYPE_URLS.get(gear_type_lower)
    if gear_urls:
        return getattr(gear_urls, mode_key, gear_urls.nonladder)
    
    # Default to amulet nonladder
    return GEAR_TYPE_URLS['amulet'].nonladder


# =============================================================================
# Column Width Configuration
# =============================================================================
@dataclass
class TableColumnWidths:
    """Column widths for table widgets."""
    main_table: Dict[int, int] = field(default_factory=lambda: {
        0: 300,  # stats
        1: 80,   # price
        2: 150,  # link
        3: 120,  # add to order
    })
    order_list: Dict[int, int] = field(default_factory=lambda: {
        0: 300,  # stats
        1: 80,   # price
        2: 150,  # link
        3: 80,   # copy link
        4: 60,   # delete
    })
    task_list: Dict[int, int] = field(default_factory=lambda: {
        0: 200,  # name
        1: 100,  # status
        2: 60,   # delete
    })
    task_result: Dict[int, int] = field(default_factory=lambda: {
        0: 150,  # task name
        1: 250,  # stats
        2: 80,   # price
        3: 150,  # link
        4: 120,  # add to order
        5: 60,   # delete
    })


COLUMN_WIDTHS = TableColumnWidths()
