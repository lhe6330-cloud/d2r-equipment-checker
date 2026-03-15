"""
Data persistence manager for DD373 D2R Equipment Checker.
Handles saving/loading order lists and task lists.
"""
import json
import logging
import time
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from config import ORDERLIST_FILE, OUTPUT_FILE
from models import ItemData, SearchTask, FilterCondition

logger = logging.getLogger(__name__)


class DataManager:
    """Manages data persistence for the application."""
    
    def __init__(self, orderlist_path: str = ORDERLIST_FILE):
        self.orderlist_path = Path(orderlist_path)
        self.order_list: List[ItemData] = []
        self.task_list: List[SearchTask] = []
    
    # =========================================================================
    # Order List Management
    # =========================================================================
    
    def load_orderlist(self) -> List[ItemData]:
        """Load order list from file."""
        try:
            if self.orderlist_path.exists():
                with open(self.orderlist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.order_list = [ItemData.from_dict(item) for item in data]
                logger.info(f"Order list loaded: {len(self.order_list)} items")
        except Exception as e:
            logger.error(f"Error loading order list: {e}")
            self.order_list = []
        
        return self.order_list
    
    def save_orderlist(self) -> bool:
        """Save order list to file."""
        try:
            data = [item.to_dict() for item in self.order_list]
            with open(self.orderlist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Order list saved: {len(self.order_list)} items")
            return True
        except Exception as e:
            logger.error(f"Error saving order list: {e}")
            return False
    
    def add_to_orderlist(self, item: ItemData) -> bool:
        """
        Add an item to the order list if not already present.
        
        Returns:
            True if added, False if already exists
        """
        # Check for duplicates by link
        if any(existing.link == item.link for existing in self.order_list):
            logger.info(f"Item already in order list: {item.link}")
            return False
        
        self.order_list.append(item)
        self.save_orderlist()
        logger.info(f"Item added to order list: {item.link}")
        return True
    
    def remove_from_orderlist(self, index: int) -> bool:
        """Remove an item from the order list by index."""
        if 0 <= index < len(self.order_list):
            self.order_list.pop(index)
            self.save_orderlist()
            logger.info(f"Order item {index} deleted")
            return True
        return False
    
    def set_item_filled(self, index: int, filled: bool) -> bool:
        """Set the filled status of an order item."""
        if 0 <= index < len(self.order_list):
            self.order_list[index].filled = filled
            self.save_orderlist()
            logger.info(f"Order item {index} filled status: {filled}")
            return True
        return False
    
    def mark_all_unfilled(self) -> None:
        """Mark all order items as unfilled."""
        for item in self.order_list:
            item.filled = False
        self.save_orderlist()
        logger.info("All order items marked as unfilled")
    
    def clear_filled_items(self) -> int:
        """Remove all filled items from the order list. Returns count removed."""
        original_count = len(self.order_list)
        self.order_list = [item for item in self.order_list if not item.filled]
        removed_count = original_count - len(self.order_list)
        self.save_orderlist()
        logger.info(f"Cleared {removed_count} filled items")
        return removed_count
    
    def export_orderlist_csv(self, file_path: str) -> bool:
        """
        Export order list to CSV file.
        
        Args:
            file_path: Path to save the CSV file
            
        Returns:
            True if export successful
        """
        import csv
        from config import CNY_TO_USD_RATE
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # Header row
                writer.writerow(['Status', 'Stats', 'Price (CNY)', 'Price (USD)', 'Link'])
                
                # Data rows
                for item in self.order_list:
                    status = "FILLED" if item.filled else "NEEDED"
                    
                    # Calculate USD price
                    try:
                        cny_value = float(item.price.replace(',', ''))
                        usd_value = cny_value * CNY_TO_USD_RATE
                        usd_str = f"${usd_value:.2f}"
                    except (ValueError, AttributeError):
                        usd_str = "N/A"
                    
                    writer.writerow([
                        status, 
                        item.stats, 
                        f"¥{item.price}", 
                        usd_str,
                        item.link
                    ])
            
            logger.info(f"Order list exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting order list: {e}")
            return False
    
    # =========================================================================
    # Task List Management
    # =========================================================================
    
    def add_task(self, task: SearchTask) -> None:
        """Add a task to the task list."""
        self.task_list.append(task)
        logger.info(f"Task added: {task.name}")
    
    def remove_task(self, index: int) -> bool:
        """Remove a task from the task list by index."""
        if 0 <= index < len(self.task_list):
            self.task_list.pop(index)
            logger.info(f"Task {index} deleted")
            return True
        return False
    
    def clear_tasks(self) -> None:
        """Clear all tasks from the task list."""
        self.task_list.clear()
        logger.info("Task list cleared")
    
    def update_task_status(self, index: int, status: str) -> None:
        """Update the status of a task."""
        if 0 <= index < len(self.task_list):
            self.task_list[index].status = status
    
    def save_task_list(self, file_path: str) -> bool:
        """Save task list to a file."""
        try:
            data = [task.to_dict() for task in self.task_list]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Task list saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving task list: {e}")
            return False
    
    def load_task_list(self, file_path: str) -> bool:
        """Load task list from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.task_list = [SearchTask.from_dict(task) for task in data]
            logger.info(f"Task list loaded: {len(self.task_list)} tasks")
            return True
        except Exception as e:
            logger.error(f"Error loading task list: {e}")
            return False
    
    # =========================================================================
    # Search Results Export
    # =========================================================================
    
    def save_search_results(
        self,
        items: List[ItemData],
        keyword: str,
        gear_type: str,
        mode: str,
        search_url: str,
        filter_conditions: List[FilterCondition],
        stopped: bool = False,
        output_path: str = OUTPUT_FILE
    ) -> bool:
        """
        Save search results to a text file.
        
        Args:
            items: List of items found
            keyword: Search keyword used
            gear_type: Type of gear searched
            mode: Search mode (all, ladder, warlock ladder, warlock nonladder, nonladder)
            search_url: The search URL used
            filter_conditions: Filter conditions applied
            stopped: Whether search was stopped by user
            output_path: Path to output file
            
        Returns:
            True if saved successfully
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("=" * 80 + "\n")
                status = "(Stopped by user)" if stopped else "(Multi-page Crawling)"
                f.write(f"DD373 D2R Equipment Search Report {status}\n")
                f.write("=" * 80 + "\n")
                
                # Metadata
                f.write(f"Search time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Search status: {'STOPPED by user' if stopped else 'COMPLETED'}\n")
                f.write(f"Gear type: {gear_type}\n")
                f.write(f"Mode: {mode}\n")
                f.write(f"Search keyword: {keyword}\n")
                f.write(f"Search URL: {search_url}\n")
                
                # Filter conditions
                if filter_conditions:
                    f.write("Filter conditions:\n")
                    for i, condition in enumerate(filter_conditions, 1):
                        f.write(f"  Condition{i}: {condition.filter_word}")
                        if condition.min_value:
                            f.write(f" Min: {condition.min_value}")
                        if condition.max_value:
                            f.write(f" Max: {condition.max_value}")
                        f.write("\n")
                
                f.write(f"Items found: {len(items)}\n")
                f.write("=" * 80 + "\n\n")
                
                # Items
                if items:
                    for i, item in enumerate(items, 1):
                        f.write(f"【Item #{i}】\n")
                        f.write(f"Stats: {item.stats}\n")
                        f.write(f"Price: ¥{item.price}\n")
                        f.write(f"Link: {item.link}\n")
                        f.write("-" * 60 + "\n\n")
                else:
                    f.write("No items found matching the conditions\n")
                
                # Footer
                f.write("=" * 80 + "\n")
                f.write("Search stopped by user\n" if stopped else "Search completed\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"Data saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return False
    
    @staticmethod
    def generate_task_filename() -> str:
        """Generate a default filename for task list export."""
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"搜索任务_{current_time}.d2rlist"
