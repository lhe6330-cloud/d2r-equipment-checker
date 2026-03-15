"""
Data models for DD373 D2R Equipment Checker.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from config import TaskStatus


@dataclass
class ItemData:
    """Represents a single equipment item."""
    stats: str = ""
    price: str = "0"
    link: str = ""
    filled: bool = False  # Whether the order has been filled/completed
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'stats': self.stats,
            'price': self.price,
            'link': self.link,
            'filled': self.filled
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ItemData':
        """Create from dictionary."""
        return cls(
            stats=data.get('stats', ''),
            price=data.get('price', '0'),
            link=data.get('link', ''),
            filled=data.get('filled', False)
        )


@dataclass
class FilterCondition:
    """Represents a single filter condition."""
    filter_word: str
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'filter_word': self.filter_word,
            'min_value': self.min_value or '',
            'max_value': self.max_value or ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FilterCondition':
        """Create from dictionary."""
        return cls(
            filter_word=data.get('filter_word', ''),
            min_value=data.get('min_value') or None,
            max_value=data.get('max_value') or None
        )


@dataclass
class SearchTask:
    """Represents a search task in the task list."""
    name: str
    gear_type: str
    keyword: str = ""
    mode: str = "nonladder"
    filter_conditions: List[FilterCondition] = field(default_factory=list)
    status: str = TaskStatus.WAITING.value
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'gear_type': self.gear_type,
            'keyword': self.keyword,
            'mode': self.mode,
            'filter_conditions': [c.to_dict() for c in self.filter_conditions],
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SearchTask':
        """Create from dictionary."""
        conditions = [
            FilterCondition.from_dict(c) 
            for c in data.get('filter_conditions', [])
        ]
        # Support both old format (include_nl/include_l) and new format (mode)
        mode = data.get('mode', '')
        if not mode:
            # Convert old format to new mode
            include_nl = data.get('include_nl', True)
            include_l = data.get('include_l', False)
            if include_nl and include_l:
                mode = 'all'
            elif include_l:
                mode = 'ladder'
            else:
                mode = 'nonladder'
        
        return cls(
            name=data.get('name', ''),
            gear_type=data.get('gear_type', 'amulet'),
            keyword=data.get('keyword', ''),
            mode=mode,
            filter_conditions=conditions,
            status=data.get('status', TaskStatus.WAITING.value)
        )


@dataclass
class TaskResultItem:
    """Represents an item found during task checking."""
    task_name: str
    stats: str = ""
    price: str = "0"
    link: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'task_name': self.task_name,
            'stats': self.stats,
            'price': self.price,
            'link': self.link
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaskResultItem':
        """Create from dictionary."""
        return cls(
            task_name=data.get('task_name', ''),
            stats=data.get('stats', ''),
            price=data.get('price', '0'),
            link=data.get('link', '')
        )


@dataclass
class SearchParameters:
    """Parameters for a search operation."""
    keyword: str
    gear_type: str
    mode: str
    filter_conditions: List[FilterCondition]
    search_url: str = ""
    
    def build_search_url(self, base_url: str) -> str:
        """Build the full search URL with keyword parameter."""
        import urllib.parse
        
        if self.keyword:
            encoded_keyword = urllib.parse.quote(self.keyword)
            return f"{base_url}?KeyWord={encoded_keyword}"
        return base_url
