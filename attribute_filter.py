"""
Attribute filtering logic for DD373 D2R Equipment Checker.
"""
import re
import logging
from typing import List, Optional, Tuple

from config import SPECIAL_ATTRIBUTES, ATTRIBUTE_MAP
from models import FilterCondition, ItemData

logger = logging.getLogger(__name__)


class AttributeFilter:
    """Handles attribute matching and item filtering."""
    
    # Regex patterns for extracting numeric values
    VALUE_PATTERNS = [
        r'[+＋](\d+)\s*{pattern}',      # +20施法
        r'{pattern}\s*[+＋](\d+)',       # 施法+20
        r'{pattern}\s*[:：]\s*(\d+)%?',  # 施法:20%
        r'\b(\d+)\s*{pattern}\b',        # 20施法
    ]
    
    def is_special_attribute(self, filter_word: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Check if the filter word is a special attribute (existence-based).
        
        Args:
            filter_word: The attribute to check
            
        Returns:
            Tuple of (special_key, synonyms) if special, else (None, None)
        """
        filter_lower = filter_word.lower()
        
        for special_key, synonyms in SPECIAL_ATTRIBUTES.items():
            if filter_lower == special_key.lower() or filter_lower in [s.lower() for s in synonyms]:
                return special_key, synonyms
        
        return None, None
    
    def get_filter_patterns(self, filter_word: str) -> List[str]:
        """
        Get all possible matching patterns for a filter word.
        
        Args:
            filter_word: The attribute to get patterns for
            
        Returns:
            List of pattern strings to match against
        """
        # Check for special attributes first
        special_key, synonyms = self.is_special_attribute(filter_word)
        if special_key:
            return synonyms
        
        # Check attribute map
        filter_lower = filter_word.lower()
        for key, variants in ATTRIBUTE_MAP.items():
            if filter_lower == key.lower() or filter_lower in [v.lower() for v in variants]:
                return list(set([key] + variants))
        
        # Return original word if no mapping found
        return [filter_word]
    
    def check_special_attribute(self, stats: str, filter_patterns: List[str]) -> Optional[float]:
        """
        Check if a special attribute exists in the stats string.
        
        Args:
            stats: The item stats string
            filter_patterns: List of patterns to match
            
        Returns:
            1.0 if attribute exists, None otherwise
        """
        stats_lower = stats.lower()
        
        for pattern in filter_patterns:
            # Use word boundary matching to avoid partial matches
            if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', stats_lower):
                return 1.0
        
        return None
    
    def extract_numeric_value(self, stats: str, filter_patterns: List[str]) -> Optional[float]:
        """
        Extract a numeric value for an attribute from the stats string.
        
        Args:
            stats: The item stats string
            filter_patterns: List of patterns to match
            
        Returns:
            The extracted numeric value, or None if not found
        """
        for pattern in filter_patterns:
            for regex_template in self.VALUE_PATTERNS:
                regex = regex_template.format(pattern=re.escape(pattern))
                match = re.search(regex, stats, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except (ValueError, IndexError):
                        continue
        
        return None
    
    def check_value_range(
        self, 
        value: float, 
        min_value: Optional[str], 
        max_value: Optional[str]
    ) -> bool:
        """
        Check if a value falls within the specified range.
        
        Args:
            value: The value to check
            min_value: Minimum value (as string, may be empty)
            max_value: Maximum value (as string, may be empty)
            
        Returns:
            True if value is within range, False otherwise
        """
        try:
            if min_value:
                if value < float(min_value):
                    return False
            if max_value:
                if value > float(max_value):
                    return False
            return True
        except ValueError:
            return False
    
    def item_matches_condition(self, item: ItemData, condition: FilterCondition) -> bool:
        """
        Check if an item matches a single filter condition.
        
        Args:
            item: The item to check
            condition: The filter condition to apply
            
        Returns:
            True if item matches the condition
        """
        stats = item.stats
        filter_word = condition.filter_word
        
        # Check for special attributes (existence-based)
        special_key, synonyms = self.is_special_attribute(filter_word)
        
        if special_key:
            # Special attribute: just needs to exist
            attribute_value = self.check_special_attribute(stats, synonyms)
            
            if attribute_value is None:
                return False
            
            # Check range if specified (usually not for special attributes)
            if condition.min_value or condition.max_value:
                return self.check_value_range(
                    attribute_value, 
                    condition.min_value, 
                    condition.max_value
                )
            return True
        
        # Regular attribute: needs numeric value
        filter_patterns = self.get_filter_patterns(filter_word)
        matched_value = self.extract_numeric_value(stats, filter_patterns)
        
        if matched_value is None:
            # Couldn't find the attribute at all
            return False
        
        # Check range if specified
        if condition.min_value or condition.max_value:
            return self.check_value_range(
                matched_value, 
                condition.min_value, 
                condition.max_value
            )
        
        return True
    
    def filter_items(
        self, 
        items: List[ItemData], 
        conditions: List[FilterCondition]
    ) -> List[ItemData]:
        """
        Filter a list of items by multiple conditions (AND logic).
        
        Args:
            items: List of items to filter
            conditions: List of conditions that must all be met
            
        Returns:
            Filtered list of items matching all conditions
        """
        if not conditions:
            return items
        
        filtered = []
        for item in items:
            if all(self.item_matches_condition(item, c) for c in conditions):
                filtered.append(item)
        
        return filtered


# Singleton instance for convenience
attribute_filter = AttributeFilter()
