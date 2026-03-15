"""
Main window controller for DD373 D2R Equipment Checker.
"""
import logging
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import os

from PySide6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QPushButton,
    QComboBox, QCheckBox, QLineEdit, QFileDialog, QApplication,
    QStatusBar, QWidget, QCompleter
)
from PySide6.QtCore import Qt, QTimer, QUrl, QStringListModel
from PySide6.QtGui import QDesktopServices

from config import (
    TaskStatus, COLUMN_WIDTHS, get_gear_type_url, format_cny, format_usd,
    load_keyword_mapping, load_filter_words, recalculate_usd_price
)
from settings_manager import load_settings, set_exchange_rate, get_exchange_rate
from models import ItemData, FilterCondition, SearchTask, TaskResultItem
from data_manager import DataManager
from crawler import CrawlerThread
from widgets import ButtonWidget

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Main window controller that manages all UI interactions.
    
    This class connects the UI widgets to the business logic,
    handling user input, displaying results, and managing the
    crawler thread.
    """
    
    def __init__(self, window: QMainWindow):
        self.window = window
        self.data_manager = DataManager()
        
        # Crawler state
        self.crawler_thread: Optional[CrawlerThread] = None
        self.is_paused = False
        self.all_crawled_items: List[ItemData] = []
        
        # Task list state
        self.task_check_result_data: List[TaskResultItem] = []
        self.current_task_index = -1
        self.is_task_list_running = False
        
        # UI widgets (initialized in setup)
        self._init_widgets()
    
    def _init_widgets(self):
        """Initialize widget references."""
        w = self.window
        
        # Main controls
        self.start_button: QPushButton = w.findChild(QPushButton, "start_button")
        self.pause_button: QPushButton = w.findChild(QPushButton, "pause_button")
        self.stop_button: QPushButton = w.findChild(QPushButton, "stop_button")
        self.keyword_combo: QComboBox = w.findChild(QComboBox, "keyword_combo")
        self.gear_type_combo: QComboBox = w.findChild(QComboBox, "gear_type")
        self.mode_combo: QComboBox = w.findChild(QComboBox, "mode_combo")
        
        # Keyword selection tracking
        self._keyword_selected_from_dropdown = False
        self.keyword_mapping: Dict[str, str] = {}
        self._all_keywords: List[str] = []  # All English keywords for filtering
        
        # Tables
        self.table_widget: QTableWidget = w.findChild(QTableWidget, "tableWidget")
        self.orderlist_widget: QTableWidget = w.findChild(QTableWidget, "orderlist")
        self.task_list_widget: QTableWidget = w.findChild(QTableWidget, "rask_list")
        self.task_result_widget: QTableWidget = w.findChild(QTableWidget, "task_check_result")
        
        # Exchange rate controls
        self.exchange_rate_input: QLineEdit = w.findChild(QLineEdit, "exchange_rate_input")
        self.refresh_rate_button: QPushButton = w.findChild(QPushButton, "refresh_rate_button")
        
        # Task list buttons
        self.add_task_btn: QPushButton = w.findChild(QPushButton, "add_task_list")
        self.start_list_btn: QPushButton = w.findChild(QPushButton, "start_list_check")
        self.next_task_btn: QPushButton = w.findChild(QPushButton, "next_list_check")
        self.stop_list_btn: QPushButton = w.findChild(QPushButton, "stop_list_check")
        self.save_task_btn: QPushButton = w.findChild(QPushButton, "save_task_list")
        self.import_task_btn: QPushButton = w.findChild(QPushButton, "import_task_list")
        self.clear_task_btn: QPushButton = w.findChild(QPushButton, "clear_task_list")
        
        # Order list buttons
        self.export_orderlist_btn: QPushButton = w.findChild(QPushButton, "export_orderlist")
        self.mark_all_unfilled_btn: QPushButton = w.findChild(QPushButton, "mark_all_unfilled")
        self.clear_filled_btn: QPushButton = w.findChild(QPushButton, "clear_filled")
        
        # Filter inputs (V3.5+: QComboBox for filter words with real-time filtering)
        self.filter_inputs: List[Tuple[QComboBox, QLineEdit, QLineEdit]] = []
        for i in range(1, 4):  # 3 rows instead of 4
            filter_word = w.findChild(QComboBox, f"filter_word_{i}")
            fw_min = w.findChild(QLineEdit, f"fw_{i}_min")
            fw_max = w.findChild(QLineEdit, f"fw_{i}_max")
            self.filter_inputs.append((filter_word, fw_min, fw_max))
        
        # Filter words list for auto-completion
        self._all_filter_words: List[str] = []
        
        # Status bar
        self.statusbar: QStatusBar = w.statusbar
    
    def setup(self):
        """Set up all UI connections and initial state."""
        self._load_keywords()
        self._load_filter_words()
        self._setup_exchange_rate()
        self._connect_signals()
        self._setup_initial_state()
        self._load_data()
        logger.info("Main window setup complete")
    
    def _load_keywords(self):
        """Load keywords from Excel and populate combo box with real-time filtering."""
        self.keyword_mapping = load_keyword_mapping()
        
        if self.keyword_combo and self.keyword_mapping:
            # Get sorted list of English keywords
            self._all_keywords = sorted(self.keyword_mapping.keys())
            
            # Populate combo box with all keywords
            self.keyword_combo.addItems(self._all_keywords)
            
            # Enable editing for real-time filtering
            self.keyword_combo.setEditable(True)
            
            # Set up completer for real-time fuzzy filtering
            completer = QCompleter(self._all_keywords, self.keyword_combo)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            completer.setMaxVisibleItems(15)  # Show max 15 items in dropdown
            
            self.keyword_combo.setCompleter(completer)
            
            logger.info(f"✓ Loaded {len(self.keyword_mapping)} keywords with real-time filtering")
        else:
            logger.warning("✗ Failed to load keywords")
            self._all_keywords = []
    
    def _load_filter_words(self):
        """Load filter words from Excel and populate filter combo boxes with real-time filtering."""
        self._all_filter_words = load_filter_words()
        
        if self._all_filter_words:
            # Sort filter words for better UX
            self._all_filter_words = sorted(self._all_filter_words)
            
            # Setup each filter combo box (3 rows)
            for filter_combo, _, _ in self.filter_inputs:
                if filter_combo:
                    # Populate combo box with all filter words
                    filter_combo.addItems(self._all_filter_words)
                    
                    # Enable editing for real-time filtering
                    filter_combo.setEditable(True)
                    
                    # Set up completer for real-time fuzzy filtering
                    completer = QCompleter(self._all_filter_words, filter_combo)
                    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                    completer.setFilterMode(Qt.MatchFlag.MatchContains)
                    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
                    completer.setMaxVisibleItems(15)  # Show max 15 items in dropdown
                    
                    filter_combo.setCompleter(completer)
            
            logger.info(f"✓ Loaded {len(self._all_filter_words)} filter words with real-time filtering")
        else:
            logger.warning("✗ Failed to load filter words")
    
    def _setup_exchange_rate(self):
        """Initialize exchange rate input with saved value."""
        if self.exchange_rate_input:
            current_rate = get_exchange_rate()
            self.exchange_rate_input.setText(str(current_rate))
            logger.info(f"✓ Exchange rate initialized: 1 USD = {current_rate} CNY")
    
    def _connect_signals(self):
        """Connect all UI signals to handlers."""
        # Keyword combo box signals
        if self.keyword_combo:
            # Track when user types (not selecting from dropdown)
            self.keyword_combo.editTextChanged.connect(self._on_keyword_text_changed)
            # Track when user selects from dropdown
            self.keyword_combo.currentIndexChanged.connect(self._on_keyword_index_changed)
            logger.info("✓ keyword_combo signals connected")
        
        # Main search buttons
        if self.start_button:
            self.start_button.clicked.connect(self._on_start_clicked)
            logger.info("✓ start button connected")
        
        if self.pause_button:
            self.pause_button.clicked.connect(self._on_pause_clicked)
            logger.info("✓ pause button connected")
        
        if self.stop_button:
            self.stop_button.clicked.connect(self._on_stop_clicked)
            logger.info("✓ stop button connected")
        
        # Task list buttons
        if self.add_task_btn:
            self.add_task_btn.clicked.connect(self._on_add_task_clicked)
        if self.start_list_btn:
            self.start_list_btn.clicked.connect(self._on_start_list_clicked)
        if self.next_task_btn:
            self.next_task_btn.clicked.connect(self._on_next_task_clicked)
        if self.stop_list_btn:
            self.stop_list_btn.clicked.connect(self._on_stop_list_clicked)
        if self.save_task_btn:
            self.save_task_btn.clicked.connect(self._on_save_task_list_clicked)
        if self.import_task_btn:
            self.import_task_btn.clicked.connect(self._on_import_task_list_clicked)
        if self.clear_task_btn:
            self.clear_task_btn.clicked.connect(self._on_clear_task_list_clicked)
        
        # Exchange rate controls
        if self.refresh_rate_button:
            self.refresh_rate_button.clicked.connect(self._on_refresh_exchange_rate_clicked)
            logger.info("✓ refresh_rate_button connected")
        
        # Order list buttons
        if self.export_orderlist_btn:
            self.export_orderlist_btn.clicked.connect(self._on_export_orderlist_clicked)
        if self.mark_all_unfilled_btn:
            self.mark_all_unfilled_btn.clicked.connect(self._on_mark_all_unfilled_clicked)
        if self.clear_filled_btn:
            self.clear_filled_btn.clicked.connect(self._on_clear_filled_clicked)
        
        # Table click handlers
        if self.table_widget:
            self.table_widget.cellClicked.connect(self._on_table_cell_clicked)
        if self.task_list_widget:
            self.task_list_widget.cellChanged.connect(self._on_task_list_cell_changed)
        
        # Window close event
        self.window.closeEvent = self._on_close
    
    def _on_keyword_text_changed(self, text: str):
        """Called when user types in the combo box (not selecting)."""
        # User is typing, not selecting from dropdown
        self._keyword_selected_from_dropdown = False
    
    def _on_keyword_index_changed(self, index: int):
        """Called when user selects an item from dropdown."""
        if index >= 0:
            # User selected from dropdown
            self._keyword_selected_from_dropdown = True
    
    def _get_search_keyword(self) -> str:
        """
        Get the actual search keyword based on user action.
        
        Rules:
        - If user selected from dropdown: use Chinese keyword from Excel
        - If user typed manually: use the typed text as-is
        
        Returns:
            The keyword to search for
        """
        if not self.keyword_combo:
            return ""
        
        text = self.keyword_combo.currentText().strip()
        
        if self._keyword_selected_from_dropdown:
            # User selected from dropdown - use Chinese keyword
            chinese_keyword = self.keyword_mapping.get(text, text)
            logger.info(f"Keyword selected from dropdown: '{text}' -> '{chinese_keyword}'")
            return chinese_keyword
        else:
            # User typed manually - use as-is
            logger.info(f"Keyword typed manually: '{text}'")
            return text
    
    def _setup_initial_state(self):
        """Set up initial button states."""
        if self.pause_button:
            self.pause_button.setEnabled(False)
        if self.stop_button:
            self.stop_button.setEnabled(False)
        if self.next_task_btn:
            self.next_task_btn.setEnabled(False)
        if self.stop_list_btn:
            self.stop_list_btn.setEnabled(False)
    
    def _load_data(self):
        """Load persisted data."""
        self.data_manager.load_orderlist()
        self._update_orderlist_table()
    
    # =========================================================================
    # Filter Condition Helpers
    # =========================================================================
    
    def _get_filter_conditions(self) -> List[FilterCondition]:
        """Get filter conditions from UI inputs."""
        conditions = []
        for filter_word_widget, min_widget, max_widget in self.filter_inputs:
            if filter_word_widget:
                # QComboBox uses currentText() instead of text()
                filter_word = filter_word_widget.currentText().strip()
                if filter_word:
                    conditions.append(FilterCondition(
                        filter_word=filter_word,
                        min_value=min_widget.text().strip() if min_widget else None,
                        max_value=max_widget.text().strip() if max_widget else None
                    ))
        return conditions
    
    def _set_filter_conditions(self, conditions: List[FilterCondition]):
        """Set filter conditions in UI inputs."""
        for i, (filter_word_widget, min_widget, max_widget) in enumerate(self.filter_inputs):
            if i < len(conditions):
                condition = conditions[i]
                if filter_word_widget:
                    # QComboBox uses setCurrentText() instead of setText()
                    filter_word_widget.setCurrentText(condition.filter_word)
                if min_widget:
                    min_widget.setText(condition.min_value or '')
                if max_widget:
                    max_widget.setText(condition.max_value or '')
            else:
                # Clear unused inputs
                if filter_word_widget:
                    filter_word_widget.setCurrentText('')
                if min_widget:
                    min_widget.setText('')
                if max_widget:
                    max_widget.setText('')
    
    # =========================================================================
    # Main Search Handlers
    # =========================================================================
    
    def _on_start_clicked(self):
        """Handle start button click."""
        try:
            keyword = self._get_search_keyword()
            gear_type = self.gear_type_combo.currentText() if self.gear_type_combo else "amulet"
            mode = self.mode_combo.currentText() if self.mode_combo else "nonladder"
            
            logger.info("=" * 60)
            logger.info(f"Starting search - Gear: {gear_type}, Keyword: {keyword}, Mode: {mode}")
            
            # Get search URL
            base_url = get_gear_type_url(gear_type, mode)
            
            # Build full URL with keyword
            import urllib.parse
            if keyword:
                search_url = f"{base_url}?KeyWord={urllib.parse.quote(keyword)}"
            else:
                search_url = base_url
            
            logger.info(f"Search URL: {search_url}")
            
            # Get filter conditions
            filter_conditions = self._get_filter_conditions()
            if filter_conditions:
                logger.info(f"Filters: {[c.filter_word for c in filter_conditions]}")
            
            # Stop existing crawler
            if self.crawler_thread and self.crawler_thread.isRunning():
                self.crawler_thread.stop()
                self.crawler_thread.wait()
            
            # Clear table
            self.table_widget.setRowCount(0)
            self.all_crawled_items = []
            
            # Update status
            self._show_status("Crawling data, please wait...")
            
            # Create and start crawler
            self.crawler_thread = CrawlerThread(search_url, keyword, filter_conditions)
            self.crawler_thread.progress_signal.connect(self._on_crawl_progress)
            self.crawler_thread.page_items_signal.connect(self._on_page_items)
            self.crawler_thread.finished_signal.connect(self._on_crawl_finished)
            self.crawler_thread.error_signal.connect(self._on_crawl_error)
            self.crawler_thread.stopped_signal.connect(self._on_crawl_stopped)
            
            # Update button states
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.pause_button.setText("Pause")
            
            # Store search params for saving
            self._current_search = {
                'keyword': keyword,
                'gear_type': gear_type,
                'mode': mode,
                'search_url': search_url,
                'filter_conditions': filter_conditions,
                'keyword_display': self.keyword_combo.currentText() if self.keyword_combo else keyword
            }
            
            self.crawler_thread.start()
            
        except Exception as e:
            logger.exception(f"Start search error: {e}")
            self._show_status(f"Error: {e}")
    
    def _on_pause_clicked(self):
        """Handle pause/resume button click."""
        if self.crawler_thread and self.crawler_thread.isRunning():
            if not self.is_paused:
                self.crawler_thread.pause()
                self.pause_button.setText("Continue")
                self.is_paused = True
                self._show_status("Crawling paused")
            else:
                self.crawler_thread.resume()
                self.pause_button.setText("Pause")
                self.is_paused = False
                self._show_status("Crawling resumed")
    
    def _on_stop_clicked(self):
        """Handle stop button click."""
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.crawler_thread.stop()
            self._show_status("Stopping crawler...")
    
    # =========================================================================
    # Crawler Callbacks
    # =========================================================================
    
    def _on_crawl_progress(self, current_page: int, total_pages: int, total_items: int):
        """Handle crawler progress update."""
        self._show_status(
            f"Crawling page {current_page}/{total_pages}, "
            f"found {total_items} items..."
        )
    
    def _on_page_items(self, items: list):
        """Handle items received from current page."""
        for item_dict in items:
            item = ItemData.from_dict(item_dict)
            self.all_crawled_items.append(item)
            self._add_item_to_table(item)
    
    def _on_crawl_finished(self, items: list):
        """Handle crawler completion."""
        logger.info(f"Crawl finished with {len(items)} items")
        self._reset_search_buttons()
        
        # Save results
        if hasattr(self, '_current_search'):
            self.data_manager.save_search_results(
                items=[ItemData.from_dict(i) for i in items],
                keyword=self._current_search.get('keyword', ''),
                gear_type=self._current_search.get('gear_type', ''),
                mode=self._current_search.get('mode', 'nonladder'),
                search_url=self._current_search.get('search_url', ''),
                filter_conditions=self._current_search.get('filter_conditions', [])
            )
        
        self._show_status(f"Search complete! Found {len(items)} items")
    
    def _on_crawl_stopped(self, items: list):
        """Handle crawler stopped by user."""
        logger.info(f"Crawl stopped with {len(items)} items")
        self._reset_search_buttons()
        
        # Save partial results
        if hasattr(self, '_current_search'):
            self.data_manager.save_search_results(
                items=[ItemData.from_dict(i) for i in items],
                keyword=self._current_search.get('keyword', ''),
                gear_type=self._current_search.get('gear_type', ''),
                mode=self._current_search.get('mode', 'nonladder'),
                search_url=self._current_search.get('search_url', ''),
                filter_conditions=self._current_search.get('filter_conditions', []),
                stopped=True
            )
        
        self._show_status(f"Search stopped. Found {len(items)} items")
    
    def _on_crawl_error(self, error_msg: str):
        """Handle crawler error."""
        logger.error(f"Crawl error: {error_msg}")
        self._reset_search_buttons()
        self._show_status(f"Error: {error_msg}")
    
    def _reset_search_buttons(self):
        """Reset button states after search ends."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.is_paused = False
    
    # =========================================================================
    # Table Management
    # =========================================================================
    
    def _add_item_to_table(self, item: ItemData):
        """Add an item to the main results table."""
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)
        
        # Stats column (0)
        stats_text = item.stats
        if len(stats_text) > 55:
            display_text = stats_text[:52] + "..."
        else:
            display_text = stats_text
        stats_item = QTableWidgetItem(display_text)
        if len(stats_text) > 55:
            stats_item.setToolTip(stats_text)
        self.table_widget.setItem(row, 0, stats_item)
        
        # CNY column (1)
        cny_item = QTableWidgetItem(format_cny(item.price))
        self.table_widget.setItem(row, 1, cny_item)
        
        # USD column (2)
        usd_item = QTableWidgetItem(format_usd(item.price))
        self.table_widget.setItem(row, 2, usd_item)
        
        # Link column (3)
        link_item = QTableWidgetItem("Click to view")
        link_item.setData(Qt.UserRole, item.link)
        self.table_widget.setItem(row, 3, link_item)
        
        # Add to order button (4)
        add_btn = ButtonWidget("Add", row, 4, self.table_widget)
        add_btn.full_data = item  # Store full item data
        add_btn.button_clicked.connect(self._on_add_to_order_clicked)
        self.table_widget.setCellWidget(row, 4, add_btn)
    
    def _on_table_cell_clicked(self, row: int, column: int):
        """Handle table cell click (for opening links)."""
        if column == 3:  # Link column
            item = self.table_widget.item(row, column)
            if item and item.text() == "Click to view":
                link = item.data(Qt.UserRole)
                if link:
                    logger.info(f"Opening link: {link}")
                    QDesktopServices.openUrl(QUrl(link))
    
    def _on_add_to_order_clicked(self, row: int, col: int):
        """Handle add to order button click."""
        btn_widget = self.table_widget.cellWidget(row, col)
        if btn_widget and hasattr(btn_widget, 'full_data'):
            item = btn_widget.full_data
            if self.data_manager.add_to_orderlist(item):
                self._update_orderlist_table()
                self._show_status(f"Added to order list ({len(self.data_manager.order_list)} items)")
            else:
                self._show_status("Item already in order list")
    
    # =========================================================================
    # Order List Management
    # =========================================================================
    
    def _update_orderlist_table(self):
        """Update the order list table display."""
        if not self.orderlist_widget:
            return
        
        self.orderlist_widget.setRowCount(0)
        self.orderlist_widget.setRowCount(len(self.data_manager.order_list))
        
        # Set column widths for new layout (7 columns)
        self.orderlist_widget.setColumnWidth(0, 50)   # Filled checkbox
        self.orderlist_widget.setColumnWidth(1, 220)  # Stats
        self.orderlist_widget.setColumnWidth(2, 75)   # CNY
        self.orderlist_widget.setColumnWidth(3, 65)   # USD
        self.orderlist_widget.setColumnWidth(4, 120)  # Link
        self.orderlist_widget.setColumnWidth(5, 50)   # Copy
        self.orderlist_widget.setColumnWidth(6, 45)   # Delete
        
        for row, item in enumerate(self.data_manager.order_list):
            # Filled checkbox (column 0)
            filled_checkbox = QCheckBox()
            filled_checkbox.setChecked(item.filled)
            filled_checkbox.setStyleSheet("margin-left: 15px;")
            filled_checkbox.stateChanged.connect(
                lambda state, r=row: self._on_filled_changed(r, state)
            )
            self.orderlist_widget.setCellWidget(row, 0, filled_checkbox)
            
            # Stats (column 1)
            stats_text = item.stats
            if len(stats_text) > 40:
                display_text = stats_text[:37] + "..."
            else:
                display_text = stats_text
            stats_item = QTableWidgetItem(display_text)
            if len(stats_text) > 40:
                stats_item.setToolTip(stats_text)
            if item.filled:
                stats_item.setForeground(Qt.gray)
            self.orderlist_widget.setItem(row, 1, stats_item)
            
            # CNY (column 2)
            cny_item = QTableWidgetItem(format_cny(item.price))
            if item.filled:
                cny_item.setForeground(Qt.gray)
            self.orderlist_widget.setItem(row, 2, cny_item)
            
            # USD (column 3)
            usd_item = QTableWidgetItem(format_usd(item.price))
            if item.filled:
                usd_item.setForeground(Qt.gray)
            self.orderlist_widget.setItem(row, 3, usd_item)
            
            # Link (column 4)
            link = item.link
            link_item = QTableWidgetItem(link[:18] + "..." if len(link) > 21 else link)
            if len(link) > 21:
                link_item.setToolTip(link)
            if item.filled:
                link_item.setForeground(Qt.gray)
            self.orderlist_widget.setItem(row, 4, link_item)
            
            # Copy link button (column 5)
            copy_btn = ButtonWidget("Copy", row, 5, self.orderlist_widget)
            copy_btn.button_clicked.connect(self._on_copy_link_clicked)
            self.orderlist_widget.setCellWidget(row, 5, copy_btn)
            
            # Delete button (column 6)
            del_btn = ButtonWidget("Del", row, 6, self.orderlist_widget)
            del_btn.button_clicked.connect(self._on_delete_order_clicked)
            self.orderlist_widget.setCellWidget(row, 6, del_btn)
    
    def _on_filled_changed(self, row: int, state: int):
        """Handle filled checkbox state change."""
        filled = state == Qt.Checked.value if hasattr(Qt.Checked, 'value') else state == 2
        self.data_manager.set_item_filled(row, filled)
        self._update_orderlist_table()  # Refresh to update styling
    
    def _on_copy_link_clicked(self, row: int, col: int):
        """Copy order item link to clipboard."""
        if 0 <= row < len(self.data_manager.order_list):
            link = self.data_manager.order_list[row].link
            QApplication.clipboard().setText(link)
            self._show_status("Link copied to clipboard")
    
    def _on_delete_order_clicked(self, row: int, col: int):
        """Delete order item."""
        if self.data_manager.remove_from_orderlist(row):
            self._update_orderlist_table()
            self._show_status(f"Item deleted ({len(self.data_manager.order_list)} remaining)")
    
    def _on_export_orderlist_clicked(self):
        """Export order list to CSV."""
        if not self.data_manager.order_list:
            self._show_status("Order list is empty")
            return
        
        from datetime import datetime
        default_name = f"d2r_orderlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Export Order List",
            default_name,
            "CSV Files (*.csv);;All Files (*.*)"
        )
        
        if file_path:
            if self.data_manager.export_orderlist_csv(file_path):
                self._show_status(f"Exported to {file_path}")
            else:
                self._show_status("Export failed")
    
    def _on_mark_all_unfilled_clicked(self):
        """Mark all order items as unfilled."""
        self.data_manager.mark_all_unfilled()
        self._update_orderlist_table()
        self._show_status("All items marked as unfilled")
    
    def _on_clear_filled_clicked(self):
        """Clear all filled items from order list."""
        count = self.data_manager.clear_filled_items()
        self._update_orderlist_table()
        self._show_status(f"Cleared {count} filled items")
    
    def _on_refresh_exchange_rate_clicked(self):
        """Handle exchange rate refresh button click."""
        try:
            # Get new exchange rate from input
            rate_text = self.exchange_rate_input.text().strip()
            if not rate_text:
                self._show_status("Error: Exchange rate cannot be empty")
                return
            
            new_rate = float(rate_text)
            
            if new_rate <= 0:
                self._show_status("Error: Exchange rate must be positive")
                return
            
            # Save to settings
            success = set_exchange_rate(new_rate)
            
            # Refresh all displayed prices
            self._refresh_all_prices()
            self._show_status(f"✓ Exchange rate updated: 1 USD = {new_rate} CNY")
        
        except ValueError:
            self._show_status("Error: Invalid exchange rate format. Please enter a number.")
        except Exception as e:
            logger.error(f"Failed to update exchange rate: {e}")
            self._show_status(f"Error: {str(e)}")
    
    def _refresh_all_prices(self):
        """Refresh all displayed prices with new exchange rate."""
        # Refresh main results table by re-adding all items
        self._refresh_main_table()
        
        # Refresh task results table
        self._update_task_result_table()
        
        # Refresh order list table
        self._update_orderlist_table()
        
        logger.info("✓ All prices refreshed with new exchange rate")
    
    def _refresh_main_table(self):
        """Refresh main results table with new exchange rate."""
        if not self.table_widget or not self.all_crawled_items:
            return
        
        # Clear current table
        self.table_widget.setRowCount(0)
        
        # Re-add all items with updated USD prices
        for item in self.all_crawled_items:
            self._add_item_to_table(item)
        
        logger.info(f"✓ Main table refreshed with {len(self.all_crawled_items)} items")
    
    # =========================================================================
    # Task List Management
    # =========================================================================
    
    def _on_add_task_clicked(self):
        """Add current search settings as a task."""
        keyword = self._get_search_keyword()
        gear_type = self.gear_type_combo.currentText() if self.gear_type_combo else "amulet"
        mode = self.mode_combo.currentText() if self.mode_combo else "nonladder"
        keyword_display = self.keyword_combo.currentText() if self.keyword_combo else keyword
        
        task_name = f"{gear_type}_{keyword_display}_{mode}" if keyword_display else f"{gear_type}_{mode}"
        
        task = SearchTask(
            name=task_name,
            gear_type=gear_type,
            keyword=keyword,
            mode=mode,
            keyword_display=keyword_display,
            filter_conditions=self._get_filter_conditions()
        )
        
        self.data_manager.add_task(task)
        self._update_task_list_table()
        self._show_status(f"Task added ({len(self.data_manager.task_list)} tasks)")
    
    def _update_task_list_table(self):
        """Update the task list table display."""
        if not self.task_list_widget:
            return
        
        self.task_list_widget.setRowCount(0)
        self.task_list_widget.setRowCount(len(self.data_manager.task_list))
        
        for col, width in COLUMN_WIDTHS.task_list.items():
            self.task_list_widget.setColumnWidth(col, width)
        
        for row, task in enumerate(self.data_manager.task_list):
            # Name (editable)
            name_item = QTableWidgetItem(task.name)
            self.task_list_widget.setItem(row, 0, name_item)
            
            # Status
            status_item = QTableWidgetItem(task.status)
            self._set_status_color(status_item, task.status)
            self.task_list_widget.setItem(row, 1, status_item)
            
            # Delete button
            del_btn = ButtonWidget("Del", row, 2, self.task_list_widget)
            del_btn.button_clicked.connect(self._on_delete_task_clicked)
            self.task_list_widget.setCellWidget(row, 2, del_btn)
    
    def _set_status_color(self, item: QTableWidgetItem, status: str):
        """Set status item color based on status value."""
        colors = {
            TaskStatus.WAITING.value: Qt.gray,
            TaskStatus.CHECKING.value: Qt.blue,
            TaskStatus.PAUSED.value: Qt.darkYellow,
            TaskStatus.FINISHED.value: Qt.green,
            TaskStatus.STOPPED.value: Qt.red,
            TaskStatus.SKIPPED.value: Qt.red,
        }
        item.setForeground(colors.get(status, Qt.black))
    
    def _on_task_list_cell_changed(self, row: int, column: int):
        """Handle task name edit."""
        if column == 0 and row < len(self.data_manager.task_list):
            new_name = self.task_list_widget.item(row, column).text()
            self.data_manager.task_list[row].name = new_name
    
    def _on_delete_task_clicked(self, row: int, col: int):
        """Delete task from list."""
        if self.data_manager.remove_task(row):
            if row == self.current_task_index:
                self.current_task_index = -1
            elif row < self.current_task_index:
                self.current_task_index -= 1
            self._update_task_list_table()
            self._show_status(f"Task deleted ({len(self.data_manager.task_list)} remaining)")
    
    # =========================================================================
    # Task List Execution
    # =========================================================================
    
    def _on_start_list_clicked(self):
        """Start executing task list."""
        if not self.data_manager.task_list:
            self._show_status("Task list is empty")
            return
        
        if self.is_task_list_running:
            return
        
        self.is_task_list_running = True
        self._set_ui_for_task_running(True)
        
        self.current_task_index = 0
        self._execute_next_task()
        
        self._show_status("Task list started")
    
    def _execute_next_task(self):
        """Execute the next task in the list."""
        if (not self.is_task_list_running or 
            self.current_task_index < 0 or 
            self.current_task_index >= len(self.data_manager.task_list)):
            self._finish_task_list()
            return
        
        task = self.data_manager.task_list[self.current_task_index]
        task.status = TaskStatus.CHECKING.value
        self._update_task_list_table()
        
        # Clear results table
        self.table_widget.setRowCount(0)
        
        # Set UI to match task
        self.gear_type_combo.setCurrentText(task.gear_type)
        # Use keyword_display if available (shows what user originally typed/selected)
        if task.keyword_display:
            self.keyword_combo.setCurrentText(task.keyword_display)
        else:
            self.keyword_combo.setCurrentText(task.keyword)
        self.mode_combo.setCurrentText(task.mode)
        self._set_filter_conditions(task.filter_conditions)
        
        # Execute search for task
        self._execute_task_search(task)
    
    def _execute_task_search(self, task: SearchTask):
        """Execute search for a specific task."""
        try:
            base_url = get_gear_type_url(task.gear_type, task.mode)
            
            import urllib.parse
            if task.keyword:
                search_url = f"{base_url}?KeyWord={urllib.parse.quote(task.keyword)}"
            else:
                search_url = base_url
            
            # Stop existing crawler
            if self.crawler_thread and self.crawler_thread.isRunning():
                self.crawler_thread.stop()
                self.crawler_thread.wait()
            
            self.table_widget.setRowCount(0)
            self.all_crawled_items = []
            
            self._show_status(f"Task: {task.name} - Crawling...")
            
            self.crawler_thread = CrawlerThread(
                search_url, 
                task.keyword, 
                task.filter_conditions
            )
            self.crawler_thread.progress_signal.connect(self._on_task_progress)
            self.crawler_thread.page_items_signal.connect(self._on_page_items)
            self.crawler_thread.finished_signal.connect(self._on_task_finished)
            self.crawler_thread.error_signal.connect(self._on_task_error)
            self.crawler_thread.stopped_signal.connect(self._on_task_stopped)
            
            self.pause_button.setEnabled(True)
            self.pause_button.setText("Pause")
            
            self.crawler_thread.start()
            
        except Exception as e:
            logger.exception(f"Task execution error: {e}")
            self._mark_current_task_stopped()
            self.current_task_index += 1
            QTimer.singleShot(1000, self._execute_next_task)
    
    def _on_task_progress(self, current_page: int, total_pages: int, total_items: int):
        """Handle task crawl progress."""
        task_name = ""
        if 0 <= self.current_task_index < len(self.data_manager.task_list):
            task_name = self.data_manager.task_list[self.current_task_index].name
        self._show_status(
            f"Task {task_name}: Page {current_page}/{total_pages}, {total_items} items"
        )
    
    def _on_task_finished(self, items: list):
        """Handle task completion."""
        if 0 <= self.current_task_index < len(self.data_manager.task_list):
            task = self.data_manager.task_list[self.current_task_index]
            task.status = TaskStatus.FINISHED.value
            self._update_task_list_table()
            
            # Collect results
            self._collect_task_results(task.name)
        
        self.table_widget.setRowCount(0)
        self.current_task_index += 1
        QTimer.singleShot(1000, self._execute_next_task)
    
    def _on_task_stopped(self, items: list):
        """Handle task stopped."""
        self._mark_current_task_stopped()
        
        if self.is_task_list_running:
            self.current_task_index += 1
            QTimer.singleShot(1000, self._execute_next_task)
        else:
            self._finish_task_list()
    
    def _on_task_error(self, error_msg: str):
        """Handle task error."""
        logger.error(f"Task error: {error_msg}")
        self._mark_current_task_stopped()
        self.current_task_index += 1
        QTimer.singleShot(1000, self._execute_next_task)
    
    def _mark_current_task_stopped(self):
        """Mark current task as stopped."""
        if 0 <= self.current_task_index < len(self.data_manager.task_list):
            self.data_manager.task_list[self.current_task_index].status = TaskStatus.STOPPED.value
            self._update_task_list_table()
    
    def _collect_task_results(self, task_name: str):
        """Collect items from table widget into task results."""
        for row in range(self.table_widget.rowCount()):
            stats_item = self.table_widget.item(row, 0)
            price_item = self.table_widget.item(row, 1)
            link_item = self.table_widget.item(row, 2)
            
            if stats_item and price_item and link_item:
                self.task_check_result_data.append(TaskResultItem(
                    task_name=task_name,
                    stats=stats_item.text(),
                    price=price_item.text().replace('¥', ''),
                    link=link_item.data(Qt.UserRole) or link_item.text()
                ))
        
        self._update_task_result_table()
    
    def _on_next_task_clicked(self):
        """Skip to next task."""
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.crawler_thread.stop()
            self.crawler_thread.wait()
        
        # Collect current results before skipping
        if 0 <= self.current_task_index < len(self.data_manager.task_list):
            task_name = self.data_manager.task_list[self.current_task_index].name
            self._collect_task_results(task_name)
            self.data_manager.task_list[self.current_task_index].status = TaskStatus.SKIPPED.value
            self._update_task_list_table()
        
        if self.current_task_index >= len(self.data_manager.task_list) - 1:
            self._finish_task_list()
            return
        
        self.table_widget.setRowCount(0)
        self.current_task_index += 1
        self._execute_next_task()
        self._show_status("Skipped to next task")
    
    def _on_stop_list_clicked(self):
        """Stop task list execution."""
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.crawler_thread.stop()
        
        # Collect current results
        if 0 <= self.current_task_index < len(self.data_manager.task_list):
            task_name = self.data_manager.task_list[self.current_task_index].name
            self._collect_task_results(task_name)
        
        self.is_task_list_running = False
        self.current_task_index = -1
        self._set_ui_for_task_running(False)
        self.table_widget.setRowCount(0)
        self._show_status("Task list stopped")
    
    def _finish_task_list(self):
        """Finish task list execution."""
        self.is_task_list_running = False
        self._set_ui_for_task_running(False)
        self._show_status("Task list finished")
    
    def _set_ui_for_task_running(self, running: bool):
        """Enable/disable UI elements based on task list state."""
        # Main controls
        self.gear_type_combo.setEnabled(not running)
        self.key_word_input.setEnabled(not running)
        self.mode_combo.setEnabled(not running)
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(not running)
        
        # Filter inputs
        for fw, min_w, max_w in self.filter_inputs:
            if fw: fw.setEnabled(not running)
            if min_w: min_w.setEnabled(not running)
            if max_w: max_w.setEnabled(not running)
        
        # Task controls
        self.pause_button.setEnabled(running)
        self.next_task_btn.setEnabled(running)
        self.stop_list_btn.setEnabled(running)
        
        self.add_task_btn.setEnabled(not running)
        self.start_list_btn.setEnabled(not running)
        self.save_task_btn.setEnabled(not running)
        self.import_task_btn.setEnabled(not running)
        self.clear_task_btn.setEnabled(not running)
    
    # =========================================================================
    # Task Result Management
    # =========================================================================
    
    def _update_task_result_table(self):
        """Update task result table display."""
        if not self.task_result_widget:
            return
        
        self.task_result_widget.setRowCount(0)
        self.task_result_widget.setRowCount(len(self.task_check_result_data))
        
        # Set column widths (7 columns)
        self.task_result_widget.setColumnWidth(0, 90)   # Task name
        self.task_result_widget.setColumnWidth(1, 200)  # Stats
        self.task_result_widget.setColumnWidth(2, 75)   # CNY
        self.task_result_widget.setColumnWidth(3, 65)   # USD
        self.task_result_widget.setColumnWidth(4, 100)  # Link
        self.task_result_widget.setColumnWidth(5, 50)   # Add to order
        self.task_result_widget.setColumnWidth(6, 45)   # Delete
        
        for row, item in enumerate(self.task_check_result_data):
            # Task name (column 0)
            self.task_result_widget.setItem(row, 0, QTableWidgetItem(item.task_name))
            
            # Stats (column 1)
            stats_text = item.stats
            if len(stats_text) > 35:
                display_text = stats_text[:32] + "..."
            else:
                display_text = stats_text
            stats_item = QTableWidgetItem(display_text)
            if len(stats_text) > 35:
                stats_item.setToolTip(stats_text)
            self.task_result_widget.setItem(row, 1, stats_item)
            
            # CNY (column 2)
            self.task_result_widget.setItem(row, 2, QTableWidgetItem(format_cny(item.price)))
            
            # USD (column 3)
            self.task_result_widget.setItem(row, 3, QTableWidgetItem(format_usd(item.price)))
            
            # Link (column 4)
            link = item.link
            link_item = QTableWidgetItem(link[:15] + "..." if len(link) > 18 else link)
            if len(link) > 18:
                link_item.setToolTip(link)
            self.task_result_widget.setItem(row, 4, link_item)
            
            # Add to order button (column 5)
            add_btn = ButtonWidget("Add", row, 5, self.task_result_widget)
            add_btn.full_data = ItemData(
                stats=item.stats,
                price=item.price,
                link=item.link
            )
            add_btn.button_clicked.connect(self._on_add_task_result_to_order)
            self.task_result_widget.setCellWidget(row, 5, add_btn)
            
            # Delete button (column 6)
            del_btn = ButtonWidget("Del", row, 6, self.task_result_widget)
            del_btn.button_clicked.connect(self._on_delete_task_result)
            self.task_result_widget.setCellWidget(row, 6, del_btn)
    
    def _on_add_task_result_to_order(self, row: int, col: int):
        """Add task result item to order list."""
        btn_widget = self.task_result_widget.cellWidget(row, col)
        if btn_widget and hasattr(btn_widget, 'full_data'):
            if self.data_manager.add_to_orderlist(btn_widget.full_data):
                self._update_orderlist_table()
                self._show_status(f"Added to order list ({len(self.data_manager.order_list)} items)")
            else:
                self._show_status("Item already in order list")
    
    def _on_delete_task_result(self, row: int, col: int):
        """Delete task result item."""
        if 0 <= row < len(self.task_check_result_data):
            self.task_check_result_data.pop(row)
            self._update_task_result_table()
    
    # =========================================================================
    # Task List File Operations
    # =========================================================================
    
    def _on_save_task_list_clicked(self):
        """Save task list to file."""
        if not self.data_manager.task_list:
            self._show_status("Task list is empty")
            return
        
        default_name = DataManager.generate_task_filename()
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_name)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Save Task List",
            default_path,
            "D2R Task List (*.d2rlist);;All Files (*.*)"
        )
        
        if file_path:
            if self.data_manager.save_task_list(file_path):
                self._show_status(f"Task list saved to {file_path}")
            else:
                self._show_status("Failed to save task list")
    
    def _on_import_task_list_clicked(self):
        """Import task list from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.window,
            "Import Task List",
            "",
            "D2R Task List (*.d2rlist);;All Files (*.*)"
        )
        
        if file_path:
            if self.data_manager.load_task_list(file_path):
                self._update_task_list_table()
                self._show_status(f"Loaded {len(self.data_manager.task_list)} tasks")
            else:
                self._show_status("Failed to load task list")
    
    def _on_clear_task_list_clicked(self):
        """Clear all tasks from list and task results."""
        self.data_manager.clear_tasks()
        self._update_task_list_table()
        
        # Also clear task results
        self.task_check_result_data.clear()
        self._update_task_result_table()
        
        self._show_status("Task list and results cleared")
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _show_status(self, message: str):
        """Show status message."""
        logger.info(message)
        if self.statusbar:
            self.statusbar.showMessage(message)
    
    def _on_close(self, event):
        """Handle window close."""
        if self.crawler_thread and self.crawler_thread.isRunning():
            logger.info("Stopping crawler thread...")
            self.crawler_thread.stop()
            self.crawler_thread.wait()
        event.accept()
