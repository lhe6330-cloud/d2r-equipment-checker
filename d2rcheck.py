"""
DD373 D2R Equipment Checker - Refactored
A PySide6 application for searching and filtering Diablo 2 Resurrected equipment on DD373.com
"""
import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled exe
        return os.path.join(sys._MEIPASS, relative_path)
    # Running in normal Python environment
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def main():
    """Application entry point."""
    try:
        ui_file = get_resource_path("d2rcheck.ui")
        
        if not os.path.exists(ui_file):
            logger.error(f"Cannot find {ui_file} file")
            print("Please ensure d2rcheck.ui is in the same directory as the executable.")
            input("Press Enter to exit...")
            return 1
        
        app = QApplication(sys.argv)
        app.setApplicationName("D2R Equipment Checker")
        app.setApplicationVersion("1.0.0")
        
        # Load UI file
        loader = QUiLoader()
        file = QFile(ui_file)
        if not file.open(QFile.ReadOnly):
            logger.error(f"Failed to open {ui_file}")
            input("Press Enter to exit...")
            return 1
        
        window = loader.load(file)
        file.close()
        
        if not window:
            logger.error("Failed to load UI file")
            input("Press Enter to exit...")
            return 1
        
        # Initialize main window controller
        main_window = MainWindow(window)
        main_window.setup()
        
        window.show()
        return app.exec()
        
    except Exception as e:
        logger.exception(f"Program startup error: {e}")
        input("Press Enter to exit...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
