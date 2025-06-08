from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QFormLayout,
                               QGroupBox, QListWidget, QMessageBox)
from PySide6.QtCore import Qt
import json

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test Report Settings")
        self.browsers = self.parent().config.get("browsers", ["Chrome", "Firefox", "Edge", "Safari"])
        self.environments = self.parent().config.get("environments", ["DEV", "QA", "UAT", "PROD"])
        self.statuses = self.parent().config.get("statuses", ["Passed", "Fail", "Blocked"])
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Top Bar
        top_bar = QHBoxLayout()
        layout.addLayout(top_bar)
        top_bar.addStretch()
        theme_button = QPushButton("☀" if self.parent().theme == "dark" else "🌙")
        theme_button.setFixedSize(48, 48)
        theme_button.setToolTip("Toggle Theme")
        theme_button.clicked.connect(self.parent().toggle_theme)
        self.parent().animate_button(theme_button)
        top_bar.addWidget(theme_button)

        settings_frame = QGroupBox("Default Settings")
        settings_layout = QFormLayout(settings_frame)
        settings_layout.setLabelAlignment(Qt.AlignRight)

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

        browsers_frame = QGroupBox("Browsers")
        browsers_layout = QVBoxLayout(browsers_frame)

        self.browser_list = QListWidget()
        for browser in self.browsers:
            self.browser_list.addItem(browser)
        browsers_layout.addWidget(self.browser_list)

        browser_input_layout = QHBoxLayout()
        self.new_browser_entry = QLineEdit()
        self.new_browser_entry.setPlaceholderText("Enter new browser...")
        browser_input_layout.addWidget(self.new_browser_entry)
        add_browser_btn = QPushButton("Add Browser")
        add_browser_btn.clicked.connect(self.add_browser)
        browser_input_layout.addWidget(add_browser_btn)
        remove_browser_btn = QPushButton("Remove Selected")
        remove_browser_btn.clicked.connect(self.remove_browser)
        browser_input_layout.addWidget(remove_browser_btn)
        browsers_layout.addLayout(browser_input_layout)

        layout.addWidget(browsers_frame)

        env_frame = QGroupBox("Environments")
        env_layout = QVBoxLayout(env_frame)

        self.env_list = QListWidget()
        for env in self.environments:
            self.env_list.addItem(env)
        env_layout.addWidget(self.env_list)

        env_input_layout = QHBoxLayout()
        self.new_env_entry = QLineEdit()
        self.new_env_entry.setPlaceholderText("Enter new environment...")
        env_input_layout.addWidget(self.new_env_entry)
        add_env_btn = QPushButton("Add Environment")
        add_env_btn.clicked.connect(self.add_environment)
        env_input_layout.addWidget(add_env_btn)
        remove_env_btn = QPushButton("Remove Selected")
        remove_env_btn.clicked.connect(self.remove_environment)
        env_input_layout.addWidget(remove_env_btn)
        env_layout.addLayout(env_input_layout)

        layout.addWidget(env_frame)

        status_frame = QGroupBox("Statuses")
        status_layout = QVBoxLayout(status_frame)

        self.status_list = QListWidget()
        for status in self.statuses:
            self.status_list.addItem(status)
        status_layout.addWidget(self.status_list)

        status_input_layout = QHBoxLayout()
        self.new_status_entry = QLineEdit()
        self.new_status_entry.setPlaceholderText("Enter new status...")
        status_input_layout.addWidget(self.new_status_entry)
        add_status_btn = QPushButton("Add Status")
        add_status_btn.clicked.connect(self.add_status)
        status_input_layout.addWidget(add_status_btn)
        remove_status_btn = QPushButton("Remove Selected")
        remove_status_btn.clicked.connect(self.remove_status)
        status_input_layout.addWidget(remove_status_btn)
        status_layout.addLayout(status_input_layout)

        layout.addWidget(status_frame)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        info_btn = QPushButton("ℹ Info")
        info_btn.setToolTip("Show application info")
        info_btn.setFixedSize(40, 40)
        info_btn.clicked.connect(self.parent().show_info_dialog)
        self.parent().animate_button(info_btn)
        button_layout.addWidget(info_btn)

        layout.addLayout(button_layout)

        self.load_settings()

    def add_browser(self):
        browser = self.new_browser_entry.text().strip()
        if not browser:
            QMessageBox.warning(self, "Input Error", "Browser name is required.")
            return
        if browser in self.browsers:
            QMessageBox.warning(self, "Duplicate", "Browser already exists.")
            return
        self.browsers.append(browser)
        self.browser_list.addItem(browser)
        self.new_browser_entry.clear()

    def remove_browser(self):
        current = self.browser_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Selection Error", "Please select a browser to remove.")
            return
        browser = current.text()
        self.browsers.remove(browser)
        row = self.browser_list.row(current)
        self.browser_list.takeItem(row)

    def add_environment(self):
        env = self.new_env_entry.text().strip()
        if not env:
            QMessageBox.warning(self, "Input Error", "Environment name is required.")
            return
        if env in self.environments:
            QMessageBox.warning(self, "Duplicate", "Environment already exists.")
            return
        self.environments.append(env)
        self.env_list.addItem(env)
        self.new_env_entry.clear()

    def remove_environment(self):
        current = self.env_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Selection Error", "Please select an environment to remove.")
            return
        env = current.text()
        self.environments.remove(env)
        row = self.env_list.row(current)
        self.env_list.takeItem(row)

    def add_status(self):
        status = self.new_status_entry.text().strip()
        if not status:
            QMessageBox.warning(self, "Input Error", "Status name is required.")
            return
        if status in self.statuses:
            QMessageBox.warning(self, "Duplicate", "Status already exists.")
            return
        self.statuses.append(status)
        self.status_list.addItem(status)
        self.new_status_entry.clear()

    def remove_status(self):
        current = self.status_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Selection Error", "Please select a status to remove.")
            return
        status = current.text()
        self.statuses.remove(status)
        row = self.status_list.row(current)
        self.status_list.takeItem(row)

    def save(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("Configuration")
            settings.setValue("browsers", json.dumps(self.browsers))
            settings.setValue("environments", json.dumps(self.environments))
            settings.setValue("statuses", json.dumps(self.statuses))
            settings.setValue("default_project", self.default_project_entry.text().strip())
            settings.setValue("default_version", self.default_version_entry.text().strip())
            settings.setValue("default_tester", self.default_tester_entry.text().strip())
            settings.endGroup()
        self.accept()

    def load_settings(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("Configuration")
            self.default_project_entry.setText(settings.value("default_project", ""))
            self.default_version_entry.setText(settings.value("default_version", ""))
            self.default_tester_entry.setText(settings.value("default_tester", ""))
            settings.endGroup()