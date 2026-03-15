"""
Custom UI widgets for DD373 D2R Equipment Checker.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class ButtonWidget(QWidget):
    """
    Custom button widget for use in table cells.
    
    Signals:
        button_clicked: Emits (row, column) when button is clicked
    """
    
    button_clicked = Signal(int, int)
    
    def __init__(
        self, 
        button_text: str, 
        row: int, 
        col: int, 
        parent: QWidget = None
    ):
        super().__init__(parent)
        self.row = row
        self.col = col
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Create button
        self.button = QPushButton(button_text)
        self.button.clicked.connect(self._on_button_clicked)
        
        layout.addWidget(self.button)
        self.setLayout(layout)
    
    def _on_button_clicked(self):
        """Handle button click and emit signal with row/column."""
        self.button_clicked.emit(self.row, self.col)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the button."""
        self.button.setEnabled(enabled)
    
    def set_text(self, text: str):
        """Set the button text."""
        self.button.setText(text)
