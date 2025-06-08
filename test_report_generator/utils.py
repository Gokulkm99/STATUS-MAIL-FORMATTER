from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class NotificationDialog(QDialog):
    def __init__(self, message, title, is_error=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 150)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        button = QPushButton("OK")
        button.clicked.connect(self.accept)
        layout.addWidget(button, alignment=Qt.AlignCenter)
        if is_error:
            self.setStyleSheet("""
                background-color: #FFCDD2;
                color: #B71C1C;
                QWidget { font-family: Calibri, Arial, sans-serif; font-size: 12px; }
                QPushButton { padding: 8px; }
            """)
        else:
            self.setStyleSheet("""
                background-color: #C8E6C9;
                color: #1B5E20;
                QWidget { font-family: Calibri, Arial, sans-serif; font-size: 12px; }
                QPushButton { padding: 8px; }
            """)