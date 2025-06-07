from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class NotificationDialog(QDialog):
    def __init__(self, message, title, is_error=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.is_error = is_error
        self.setup_ui(message)

    def setup_ui(self, message):
        layout = QVBoxLayout(self)

        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

        self.setStyleSheet("""
            QLabel {
                color: #D32F2F if self.is_error else #388E3C;
                font-size: 14pt;
                padding: 10px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12pt;
            }
        """)