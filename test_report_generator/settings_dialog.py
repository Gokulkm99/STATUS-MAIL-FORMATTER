from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFormLayout, QGroupBox
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test Report Settings")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Settings Form
        settings_frame = QGroupBox("Settings")
        settings_layout = QFormLayout(settings_frame)

        self.default_project_entry = QLineEdit()
        self.default_project_entry.setPlaceholderText("Enter default project name...")
        settings_layout.addRow("Default Project Name:", self.default_project_entry)

        self.default_version_entry = QLineEdit()
        self.default_version_entry.setPlaceholderText("Enter default project version...")
        settings_layout.addRow("Default Project Version:", self.default_version_entry)

        self.default_tester_entry = QLineEdit()
        self.default_tester_entry.setPlaceholderText("Enter default tester name...")
        settings_layout.addRow("Default Tester:", self.default_tester_entry)

        layout.addWidget(settings_frame)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.load_settings()

    def save(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("SettingsDialog")
            settings.setValue("default_project", self.default_project_entry.text())
            settings.setValue("default_version", self.default_version_entry.text())
            settings.setValue("default_tester", self.default_tester_entry.text())
            settings.endGroup()
        self.accept()

    def load_settings(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("SettingsDialog")
            self.default_project_entry.setText(settings.value("default_project", ""))
            self.default_version_entry.setText(settings.value("default_version", ""))
            self.default_tester_entry.setText(settings.value("default_tester", ""))
            settings.endGroup()