"""
Crawler thread for DD373 D2R Equipment Checker.
Handles web scraping in a background thread.
"""
import time
import logging
import urllib.parse
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QThread, Signal

from config import USER_AGENT, REQUEST_TIMEOUT, PAGE_DELAY_SECONDS
from models import ItemData, FilterCondition
from attribute_filter import AttributeFilter

logger = logging.getLogger(__name__)


class CrawlerThread(QThread):
    """
    Background thread for crawling DD373 equipment listings.
    
    Signals:
        progress_signal: Emits (current_page, total_pages, total_items)
        page_items_signal: Emits list of items found on current page
        finished_signal: Emits all items when crawling completes
        error_signal: Emits error message string
        stopped_signal: Emits items found before stopping
    """
    
    progress_signal = Signal(int, int, int)
    page_items_signal = Signal(list)
    finished_signal = Signal(list)
    error_signal = Signal(str)
    stopped_signal = Signal(list)
    
    def __init__(
        self, 
        search_url: str, 
        keyword: str, 
        filter_conditions: List[FilterCondition]
    ):
        super().__init__()
        self.search_url = search_url
        self.keyword = keyword
        self.filter_conditions = filter_conditions
        
        # Control flags
        self.running = True
        self.paused = False
        self.stopped = False
        
        # Data storage
        self.all_items: List[ItemData] = []
        
        # Attribute filter
        self.attr_filter = AttributeFilter()
        
        # HTTP headers
        self.headers = {'User-Agent': USER_AGENT}
    
    def run(self):
        """Main thread function."""
        try:
            total_pages = self._get_total_pages()
            if total_pages is None:
                self.error_signal.emit("Cannot get total pages")
                return
            
            logger.info(f"Total pages: {total_pages}")
            self.all_items = []
            
            for page in range(1, total_pages + 1):
                if not self.running:
                    logger.info("Crawling stopped")
                    break
                
                # Handle pause
                while self.paused and self.running:
                    time.sleep(0.1)
                
                if not self.running:
                    break
                
                logger.info(f"Crawling page {page}/{total_pages}...")
                self._crawl_page(page, total_pages)
                
                # Delay between pages (with pause/stop checks)
                if page < total_pages:
                    self._wait_between_pages()
            
            # Emit appropriate completion signal
            if self.stopped:
                logger.info(f"Crawling stopped by user, found {len(self.all_items)} items")
                self.stopped_signal.emit([item.to_dict() for item in self.all_items])
            else:
                logger.info(f"Crawling completed! Total {len(self.all_items)} items found")
                self.finished_signal.emit([item.to_dict() for item in self.all_items])
                
        except Exception as e:
            logger.exception(f"Crawling error: {e}")
            self.error_signal.emit(f"Crawling error: {e}")
    
    def _get_total_pages(self) -> Optional[int]:
        """Determine the total number of pages to crawl."""
        try:
            response = requests.get(
                self.search_url, 
                headers=self.headers, 
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get total pages, status code: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Method 1: hot-sum span
            hot_sum_span = soup.find('span', class_='hot-sum')
            if hot_sum_span:
                try:
                    return int(hot_sum_span.text.strip())
                except ValueError:
                    pass
            
            # Method 2: font12 color666 span
            font_spans = soup.find_all('span', class_='font12')
            for span in font_spans:
                if 'color666' in span.get('class', []):
                    try:
                        return int(span.text.strip())
                    except ValueError:
                        pass
            
            # Method 3: pagination links
            pagination = soup.find('div', class_='pagination')
            if pagination:
                page_links = pagination.find_all('a')
                page_numbers = []
                for link in page_links:
                    try:
                        num = int(link.text.strip())
                        page_numbers.append(num)
                    except ValueError:
                        pass
                
                if page_numbers:
                    return max(page_numbers)
            
            # Default to 1 page if no pagination info found
            logger.warning("No pagination info found, defaulting to 1 page")
            return 1
            
        except Exception as e:
            logger.exception(f"Error getting total pages: {e}")
            return None
    
    def _build_page_url(self, page_num: int) -> str:
        """Build the URL for a specific page number."""
        if 'dd373.com' not in self.search_url:
            logger.warning(f"Non-standard URL format: {self.search_url}")
            return self.search_url
        
        parsed_url = urllib.parse.urlparse(self.search_url)
        path = parsed_url.path
        
        # Check for paginated URL format
        if '1psrbm-u6w1hm-' in path and '5tgw08-' in path:
            path_parts = path.split('-')
            if len(path_parts) >= 15:
                path_parts[13] = str(page_num)
                new_path = '-'.join(path_parts)
            else:
                new_path = path.replace('-1-0-0-0.html', f'-{page_num}-0-0-0.html')
        else:
            base_pattern = "-1-0-0-0.html"
            if base_pattern in path:
                new_path = path.replace(base_pattern, f"-{page_num}-0-0-0.html")
            else:
                new_path = path
        
        # Rebuild URL
        new_url = f"https://www.dd373.com{new_path}"
        
        # Add query parameters
        if parsed_url.query:
            new_url += f"?{parsed_url.query}"
        
        return new_url
    
    def _parse_goods_data(self, soup: BeautifulSoup) -> List[ItemData]:
        """Parse item data from page HTML."""
        items = []
        
        goods_list = soup.find('div', class_='good-list-box')
        if not goods_list:
            logger.warning("No goods list container found")
            return items
        
        goods_items = goods_list.find_all('div', class_='goods-list-item')
        
        for goods_item in goods_items:
            try:
                item = self._parse_single_item(goods_item)
                if item:
                    items.append(item)
            except Exception as e:
                logger.error(f"Error parsing single item: {e}")
                continue
        
        return items
    
    def _parse_single_item(self, goods_item) -> Optional[ItemData]:
        """Parse a single item from its HTML element."""
        # Extract stats
        stats = ""
        game_account_flag = goods_item.find('div', class_='game-account-flag')
        if game_account_flag:
            stats = game_account_flag.get_text(strip=True)
        
        # Extract price
        price = ""
        price_div = goods_item.find('div', class_='goods-price')
        if price_div:
            price_text = price_div.get_text(strip=True)
            price = price_text.replace('￥', '').strip()
        
        # Extract link
        link = ""
        img_link = goods_item.find('a', href=True)
        if img_link and 'href' in img_link.attrs:
            link = img_link['href']
        else:
            title_link = goods_item.find('a', class_='goods-list-title')
            if title_link and 'href' in title_link.attrs:
                link = title_link['href']
        
        # Normalize link
        if link.startswith('/'):
            link = f"https://www.dd373.com{link}"
        
        # Only return if we have valid data
        if stats or price or link:
            return ItemData(stats=stats, price=price, link=link)
        
        return None
    
    def _crawl_page(self, page: int, total_pages: int):
        """Crawl a single page and process items."""
        page_url = self._build_page_url(page)
        
        try:
            response = requests.get(
                page_url, 
                headers=self.headers, 
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.warning(f"Page {page} request failed, status: {response.status_code}")
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = self._parse_goods_data(soup)
            
            # Apply filters
            if self.filter_conditions and items:
                filtered_items = self.attr_filter.filter_items(
                    items, 
                    self.filter_conditions
                )
            else:
                filtered_items = items
            
            # Add to results
            self.all_items.extend(filtered_items)
            
            # Emit signals
            self.progress_signal.emit(page, total_pages, len(self.all_items))
            
            if filtered_items:
                self.page_items_signal.emit([item.to_dict() for item in filtered_items])
            
            logger.info(
                f"Page {page} completed, found {len(filtered_items)} items, "
                f"total {len(self.all_items)} items"
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Page {page} request exception: {e}")
        except Exception as e:
            logger.error(f"Page {page} processing exception: {e}")
    
    def _wait_between_pages(self):
        """Wait between page requests with pause/stop support."""
        for _ in range(PAGE_DELAY_SECONDS):
            if not self.running:
                break
            while self.paused and self.running:
                time.sleep(0.1)
            if not self.running:
                break
            time.sleep(1)
    
    def pause(self):
        """Pause the crawling operation."""
        self.paused = True
    
    def resume(self):
        """Resume the crawling operation."""
        self.paused = False
    
    def stop(self):
        """Stop the crawling operation."""
        self.stopped = True
        self.running = False
        self.paused = False
