"""
Settings management for D2R Equipment Checker.
"""
import json
import os


DEFAULT_SETTINGS = {
    'exchange_rate': 6.8,  # 1 USD = 6.8 CNY
}


def get_settings_file_path() -> str:
    """Get the path to settings.json file."""
    import sys
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled exe - store data next to the exe
        return os.path.join(os.path.dirname(sys.executable), 'settings.json')
    # Running in normal Python environment
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')


def load_settings() -> dict:
    """Load settings from settings.json."""
    settings_file = get_settings_file_path()
    
    if not os.path.exists(settings_file):
        # Create default settings file
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Merge with defaults to ensure all keys exist
        merged = DEFAULT_SETTINGS.copy()
        merged.update(settings)
        return merged
    
    except Exception as e:
        print(f"Warning: Failed to load settings: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> bool:
    """Save settings to settings.json."""
    settings_file = get_settings_file_path()
    
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error: Failed to save settings: {e}")
        return False


def get_exchange_rate() -> float:
    """Get current exchange rate (1 USD = X CNY)."""
    settings = load_settings()
    return settings.get('exchange_rate', DEFAULT_SETTINGS['exchange_rate'])


def set_exchange_rate(rate: float) -> bool:
    """Set exchange rate and save to settings.json."""
    settings = load_settings()
    settings['exchange_rate'] = rate
    return save_settings(settings)
