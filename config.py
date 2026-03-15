"""
Configuration constants and mappings for DD373 D2R Equipment Checker.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import sys
import os
from pathlib import Path


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
# Exchange rate is now managed dynamically in settings_manager.py
# Default: 1 USD = 6.8 CNY


def get_exchange_rate() -> float:
    """Get current exchange rate (1 USD = X CNY)."""
    try:
        from settings_manager import get_exchange_rate as get_rate
        return get_rate()
    except Exception:
        return 6.8  # Default fallback


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
        exchange_rate = get_exchange_rate()
        usd_value = cny_value / exchange_rate  # CNY / rate = USD
        return f"${usd_value:.2f}"
    except (ValueError, AttributeError):
        return "N/A"


def format_price(cny_price: str) -> str:
    """
    Format price to show both CNY and USD.
    
    Args:
        cny_price: Price string in CNY (may contain ¥ symbol)
    
    Returns:
        Formatted string like "¥580 / $85"
    """
    try:
        # Clean the price string
        clean_price = cny_price.replace('¥', '').replace(',', '').strip()
        cny_value = float(clean_price)
        exchange_rate = get_exchange_rate()
        usd_value = cny_value / exchange_rate  # CNY / rate = USD
        return f"¥{cny_value:.0f} / ${usd_value:.2f}"
    except (ValueError, AttributeError):
        return f"¥{cny_price}"


def recalculate_usd_price(cny_value: float) -> float:
    """
    Recalculate USD price from CNY using current exchange rate.
    
    Args:
        cny_value: Price in CNY
    
    Returns:
        Price in USD
    """
    exchange_rate = get_exchange_rate()
    return cny_value / exchange_rate


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
# Generated from Filter Word Mapping Table.xlsx (columns D/E/F)
# 6 special attributes as requested
# =============================================================================
SPECIAL_ATTRIBUTES: Dict[str, List[str]] = {
    'To Attack Rating(Based On Character Level)': ['fools', '愚人', '等级'],
    'Bonus To Attack Rating (Based On Character Level)': ['visio', '幻影', '等级'],
    'teleport': ['tp', '传送'],
    'socket': ['socket', '孔'],
    'Ethereal': ['Eth', '无形'],
    'Life Tap': ['LT', '偷取生命', '生命偷取'],
}


# =============================================================================
# Attribute Mappings (numeric value-based)
# Generated from Filter Word Mapping Table.xlsx (strictly follow Excel columns D/E/F)
# =============================================================================
ATTRIBUTE_MAP: Dict[str, List[str]] = {
    'Faster cast rate': ['fcr', '施法'],
    'Faster Hit Recovery': ['Fhr', '打击'],
    'Faster Run/Walk': ['frw', '跑'],
    'strength': ['str', '力量'],
    'dexterity': ['dex', '敏捷'],
    'life': ['life', '生命'],
    'vitality': ['vit', '体力', '体能'],
    'energy': ['ene', '能量'],
    'all res': ['allres', '全抗', '所有抗性'],
    'fire resistance': ['fr', '火炕', '火焰抗性'],
    'cold resistance': ['cr', '冰抗', '冰冷抗性'],
    'lightning resistance': ['lr', '电抗', '闪电抗性'],
    'poison resistance': ['pr', '毒抗', '毒素抗性'],
    'magic find': ['mf', '寻魔', '寻宝'],
    'extro gold': ['eg', '打钱', '额外金币'],
    'mana': ['mana', '法力'],
    'defense': ['def', '防御'],
    'Increased attack speed': ['ias', '攻击速度', '攻速'],
    'life steal': ['ll', '吸血', '偷取生命'],
    'mana steal': ['lm', '吸蓝', '偷取法力'],
    'Enhanced Damage/': ['ed', '伤害'],
    'Enhanced Defense': ['ed', '防御'],
    'attack rating': ['ar', '准确'],
    'socket': ['socket', '孔'],
    'Chance Of Crushing Blow': ['cb', '压碎', '粉碎'],
    'Replenish Life': ['replife', '生命'],
    'Chance Of Deadly Strike': ['ds', '双倍', '致命'],
    'To Attack Rating(Based On Character Level)': ['fools', '愚人', '等级'],
    'Bonus To Attack Rating (Based On Character Level)': ['visio', '幻影', '等级'],
    'Max dmg': ['max', '最大'],
    'Min dmg': ['min', '最小'],
    'Poison Length Reduced by': ['plr', '毒缩'],
    'to Poison and Bone Skills(Necromancer Only)': ['pnb', '毒'],
    'Ethereal': ['Eth', '无形'],
    'Eth and Repairs durability persecond': ['erep', '无形自回'],
    'Eth and Replenishes Quantity': ['erep', '无形自回'],
    'teleport': ['tp', '传送'],
    'Increased Chance of Blocking': ['icb', '增加格挡'],
    'Mind blast': ['mb', '心灵'],
    'Lightning Sentry': ['ls', '雷光'],
    'Wake of Fire': ['wof', '火焰'],
    'Blade Fury': ['bf', '狂怒', '刃之怒'],
    'Fire Blast': ['FB', '火焰'],
    'Fire ball': ['FB', '火球'],
    'Shadow Master': ['sm', '影子大师'],
    'Venom': ['Venom', '毒牙', '淬毒'],
    'Weapon Block': ['Wb', '武器格挡'],
    'Shadow Warrior': ['sw', '影子战士'],
    'Cloak of Shadows': ['cos', '斗篷'],
    'Fade': ['Fade', '能量消解', '影散'],
    'Claws of Thunder': ['cot', '雷电'],
    'Blades of Ice': ['boi', '寒冰刃'],
    'Phoenix Strike': ['ps', '凤凰'],
    'Dragon Tail': ['dt', '龙摆尾'],
    'assassin': ['sin', '刺客'],
    'Shadow skill': ['Shadow', '暗影'],
    'Trap skill': ['trap', '陷阱'],
    'Blade sheild': ['bs', '刃之盾'],
    'Amplify Damage': ['AMP', '伤害加深'],
    'Terror': ['Terror', '恐惧'],
    'Confuse': ['Confuse', '迷乱'],
    'Life Tap': ['LT', '偷取生命', '生命偷取'],
    'Attract': ['Attract', '吸引'],
    'Decrepify': ['Decrep', '衰老'],
    'Lower Resist': ['LR', '降低抵抗', '降低抗性'],
    'Bone Spear': ['BS', '骨矛'],
    'Bone Spirit': ['BSpirit', '骨魂'],
    'Poison Nova': ['PN', '剧毒新星'],
    'Bone Prison': ['BP', '骨牢'],
    'Blessed Hammer': ['BH', '祝福之锤'],
    'Golem Mastery': ['GM', '支配石魔'],
    'Fire Golem': ['FG', '火焰石魔', '火魔'],
    'Blood Golem': ['Bg', '鲜血石魔', '血魔'],
    'Clay Golem': ['cg', '粘土石魔', '土魔'],
    'Bone Wall': ['BWall', '骨墙'],
    'Charge': ['Charge', '冲锋'],
    'Concentration': ['Conc', '专注'],
    'Conviction': ['Conv', '审判', '信念'],
    'Fist of the Heavens': ['Foh', '天堂'],
    'Combat': ['Combat', '战斗'],
    'Offensive': ['Offensive', '攻击灵气', '进攻灵气'],
    'Shiver Armor': ['SA', '寒冰装甲'],
    'Chilling Armor': ['ca', '碎冰甲', '寒冰装甲'],
    'Frozen Orb': ['fo', '冰封球'],
    'Cold Mastery': ['CM', '支配冰冷', '冰系掌握'],
    'Blizzard': ['blizz', '暴风雪'],
    'Nova': ['Nova', '新星'],
    'Lightning': ['Lightning', '直闪', '闪电'],
    'Chain Lightning': ['CL', '连锁闪电', '连闪'],
    'Thunder Storm': ['ts', '风暴'],
    'Energy Shield': ['es', '能量护盾'],
    'Lightning Mastery': ['lm', '支配闪电', '电支配'],
    'Fire Wall': ['fw', '火墙'],
    'Meteor': ['Meteor', '陨石'],
    'Hydra': ['Hydra', '火蛇'],
    'Enchant': ['Enchant', '强化', '附魔'],
    'Fire Mastery': ['fm', '支配火焰', '火支配'],
    'Frost Nova': ['FN', '冰霜新星', '霜之新星'],
    'Fissure': ['Fissure', '火山爆'],
    'Volcano': ['Volc', '火山爆'],
    'Cyclone Armor': ['Cyclone', '装甲'],
    'Tornado': ['nado', '龙卷风'],
    'Hurricane': ['Hurricane', '飓风'],
    'Maul': ['Maul', '撞槌'],
    'Oak Sage': ['oak', '橡木'],
    'Fury': ['Fury', '狂怒'],
    'Heart of Wolverine': ['HoW', '狼獾之心'],
    'Firestorm': ['FS', '火风暴', '火焰风暴'],
    'ring of fire': ['ring of fire', '火焰之环'],
    'flame wave': ['flame wave', '烈焰涌浪'],
    'apocalypse': ['apocalypse', '天启末日'],
    'sigil:lethargy': ['sigil:lethargy', '昏沉'],
    'sigil:rancor': ['sigil:rancor', '冤仇'],
    'sigil:death': ['sigil:death', '死亡'],
    'miasma bolt': ['miasma bolt', '瘴气弹'],
    'miasma chain': ['miasma chain', '瘴气锁链'],
    'enhanced entropy': ['enhanced entropy', '增强混乱'],
    'abyss': ['abyss', '深渊裂口'],
    'levitation mastery': ['levitation mastery', '悬浮精通'],
    'echoing strike': ['echoing strike', '回响打击'],
    'blade warp': ['blade warp', '飞刀'],
    'cleave': ['cleave', '斩劈'],
    'psychic ward': ['psychic ward', '灵能护盾'],
    'eldritch blast': ['eldritch blast', '邪异轰击'],
    'mirrored blades': ['mirrored blades', '镜像之刃'],
    'hex:bane': ['hex:bane', '灾祸'],
    'hex:purge': ['hex:purge', '消灭'],
    'hex:siphon': ['hex:siphon', '虹吸'],
    'demonic mastery': ['demonic mastery', '恶魔专精'],
    'consume': ['consume', '吞噬'],
    'engorge': ['engorge', '吞食'],
    'blood boil': ['blood boil', '沸血术'],
    'bind demon': ['bind demon', '束缚恶魔'],
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


# =============================================================================
# Keywords Configuration
# =============================================================================

def get_keywords_file_path() -> str:
    """Get the path to keywords.xlsx file."""
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled exe
        return os.path.join(os.path.dirname(sys.executable), 'keywords.xlsx')
    # Running in normal Python environment
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keywords.xlsx')


def load_keyword_mapping(excel_path: str = None) -> Dict[str, str]:
    """
    Load keyword mapping from keywords.xlsx.
    
    Returns:
        Dict mapping English keywords to Chinese keywords.
        Example: {"Amazon": "亚马逊", "Paladin": "圣骑", ...}
    
    Note:
        This function strictly uses the exact text from Excel.
        No auto-completion, no modification, no inference.
    """
    import sys
    import os
    
    if excel_path is None:
        excel_path = get_keywords_file_path()
    
    mapping = {}
    
    # Try alternative path in _MEIPASS for frozen app
    if not os.path.exists(excel_path) and hasattr(sys, '_MEIPASS'):
        alt_path = os.path.join(sys._MEIPASS, 'keywords.xlsx')
        if os.path.exists(alt_path):
            excel_path = alt_path
    
    try:
        from openpyxl import load_workbook
        wb = load_workbook(excel_path, data_only=True)
        ws = wb.active
        
        for row in range(2, ws.max_row + 1):
            en = ws.cell(row=row, column=2).value
            cn = ws.cell(row=row, column=3).value
            if en and cn:
                mapping[str(en)] = str(cn)
        
        return mapping
    
    except Exception as e:
        print(f"Warning: Failed to load keywords from Excel: {e}")
        return {}


# =============================================================================
# Filter Words Configuration (V3.5+)
# =============================================================================

def get_filter_words_file_path() -> str:
    """Get the path to Filter Word Mapping Table.xlsx file."""
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled exe
        return os.path.join(sys._MEIPASS, 'Filter Word Mapping Table.xlsx')
    # Running in normal Python environment
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Filter Word Mapping Table.xlsx')


def load_filter_words(excel_path: str = None) -> List[str]:
    """
    Load all filter words from Filter Word Mapping Table.xlsx.
    
    Returns:
        List of filter words (column B from Excel).
        Example: ["Faster cast rate", "Faster Hit Recovery", "strength", ...]
    """
    import sys
    import os
    
    if excel_path is None:
        excel_path = get_filter_words_file_path()
    
    filter_words = []
    
    # Try alternative path in _MEIPASS for frozen app
    if not os.path.exists(excel_path) and hasattr(sys, '_MEIPASS'):
        alt_path = os.path.join(sys._MEIPASS, 'Filter Word Mapping Table.xlsx')
        if os.path.exists(alt_path):
            excel_path = alt_path
    
    try:
        from openpyxl import load_workbook
        wb = load_workbook(excel_path, data_only=True)
        ws = wb.active
        
        # Read column B (filter word) from row 2 onwards
        for row in range(2, ws.max_row + 1):
            filter_word = ws.cell(row=row, column=2).value
            if filter_word and str(filter_word).strip():
                filter_words.append(str(filter_word).strip())
        
        return filter_words
    
    except Exception as e:
        print(f"Warning: Failed to load filter words from Excel: {e}")
        return []
