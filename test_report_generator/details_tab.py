from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
                               QRadioButton, QGroupBox, QPushButton, QDateEdit, QListWidget, QButtonGroup,
                               QScrollArea)
from PySide6.QtCore import QDate, Qt
import json

class DetailsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_cases = []
        self.setup_ui()
        self.load_configuration()
        self.load_dynamic_options()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # Top Bar
        top_bar = QHBoxLayout()
        main_layout.addLayout(top_bar)
        top_bar.addStretch()
        theme_button = QPushButton("☀" if self.parent().theme == "dark" else "🌙")
        theme_button.setFixedSize(48, 48)
        theme_button.setToolTip("Toggle Theme")
        theme_button.clicked.connect(self.parent().toggle_theme)
        self.parent().animate_button(theme_button)
        top_bar.addWidget(theme_button)

        settings_button = QPushButton("⚙ Settings")
        settings_button.setToolTip("Open settings")
        settings_button.clicked.connect(self.parent().show_settings_dialog)
        self.parent().animate_button(settings_button)
        top_bar.addWidget(settings_button)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        scroll.setWidget(container)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(15)

        # Test Report Details Frame
        details_frame = QGroupBox("Test Report Details")
        details_layout = QFormLayout(details_frame)
        details_layout.setLabelAlignment(Qt.AlignRight)
        details_layout.setSpacing(10)

        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("Enter report title...")
        details_layout.addRow("Report Title:", self.title_entry)

        self.project_name_entry = QLineEdit()
        self.project_name_entry.setPlaceholderText("Enter project name...")
        details_layout.addRow("Project Name:", self.project_name_entry)

        self.project_version_entry = QLineEdit()
        self.project_version_entry.setPlaceholderText("Enter project version...")
        details_layout.addRow("Project Version:", self.project_version_entry)

        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(["Manual - Regression", "Manual - Smoke", "Automation", "Performance"])
        details_layout.addRow("Type of Test:", self.test_type_combo)

        self.change_id_entry = QLineEdit()
        self.change_id_entry.setPlaceholderText("Enter change ID...")
        details_layout.addRow("Change ID:", self.change_id_entry)

        browser_group = QGroupBox("Browser")
        browser_group.setMinimumHeight(80)
        browser_layout = QHBoxLayout(browser_group)
        browser_layout.setSpacing(20)
        browser_layout.setContentsMargins(15, 5, 15, 5)
        self.browser_group = QButtonGroup()
        self.browser_layout = browser_layout
        details_layout.addRow(browser_group)

        env_group = QGroupBox("Environment")
        env_group.setMinimumHeight(80)
        env_layout = QHBoxLayout(env_group)
        env_layout.setSpacing(20)
        env_layout.setContentsMargins(15, 5, 15, 5)
        self.env_group = QButtonGroup()
        self.env_layout = env_layout
        details_layout.addRow(env_group)

        status_group = QGroupBox("Status")
        status_group.setMinimumHeight(80)
        status_layout = QHBoxLayout(status_group)
        status_layout.setSpacing(20)
        status_layout.setContentsMargins(15, 5, 15, 5)
        self.status_group = QButtonGroup()
        self.status_layout = status_layout
        details_layout.addRow(status_group)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        details_layout.addRow("Start Date:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        details_layout.addRow("End Date:", self.end_date)

        self.tester_entry = QLineEdit()
        self.tester_entry.setPlaceholderText("Enter tester name...")
        details_layout.addRow("Tester:", self.tester_entry)

        container_layout.addWidget(details_frame)

        test_cases_frame = QGroupBox("Test Cases")
        test_cases_layout = QVBoxLayout(test_cases_frame)
        test_cases_layout.setSpacing(10)

        self.test_case_entry = QLineEdit()
        self.test_case_entry.setPlaceholderText("Enter test case description...")
        test_cases_layout.addWidget(self.test_case_entry)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        add_test_case_btn = QPushButton("Add Test Case")
        add_test_case_btn.clicked.connect(self.add_test_case)
        button_layout.addWidget(add_test_case_btn)

        remove_test_case_btn = QPushButton("Remove Selected Test Case")
        remove_test_case_btn.clicked.connect(self.remove_test_case)
        button_layout.addWidget(remove_test_case_btn)
        button_layout.addStretch()
        test_cases_layout.addLayout(button_layout)

        self.test_case_list = QListWidget()
        self.test_case_list.setMinimumHeight(150)
        test_cases_layout.addWidget(self.test_case_list)

        container_layout.addWidget(test_cases_frame)
        container_layout.addStretch()

        main_layout.addWidget(scroll)

    def load_dynamic_options(self):
        for button in self.browser_group.buttons():
            self.browser_group.removeButton(button)
            self.browser_layout.removeWidget(button)
            button.deleteLater()
        for button in self.env_group.buttons():
            self.env_group.removeButton(button)
            self.env_layout.removeWidget(button)
            button.deleteLater()
        for button in self.status_group.buttons():
            self.status_group.removeButton(button)
            self.status_layout.removeWidget(button)
            button.deleteLater()

        browsers = self.parent().config.get("browsers", ["Chrome", "Firefox", "Edge", "Safari"])
        for browser in browsers:
            radio = QRadioButton(browser)
            if browser == self.parent().config.get("browser", "Chrome"):
                radio.setChecked(True)
            self.browser_group.addButton(radio)
            self.browser_layout.addWidget(radio)
        self.browser_layout.addStretch()

        environments = self.parent().config.get("environments", ["DEV", "QA", "UAT", "PROD"])
        for env in environments:
            radio = QRadioButton(env)
            if env == self.parent().config.get("environment", "DEV"):
                radio.setChecked(True)
            self.env_group.addButton(radio)
            self.env_layout.addWidget(radio)
        self.env_layout.addStretch()

        statuses = self.parent().config.get("statuses", ["Passed", "Fail", "Blocked"])
        for status in statuses:
            radio = QRadioButton(status)
            if status == self.parent().config.get("status", "Passed"):
                radio.setChecked(True)
            self.status_group.addButton(radio)
            self.status_layout.addWidget(radio)
        self.status_layout.addStretch()

    def add_test_case(self):
        test_case = self.test_case_entry.text().strip()
        if test_case:
            self.test_cases.append(test_case)
            self.test_case_list.addItem(test_case)
            self.test_case_entry.clear()
            self.save_configuration()

    def remove_test_case(self):
        current_item = self.test_case_list.currentItem()
        if current_item:
            row = self.test_case_list.row(current_item)
            self.test_cases.pop(row)
            self.test_case_list.takeItem(row)
            self.save_configuration()

    def save_configuration(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("DetailsTab")
            settings.setValue("title", self.title_entry.text())
            settings.setValue("project_name", self.project_name_entry.text())
            settings.setValue("project_version", self.project_version_entry.text())
            settings.setValue("test_type", self.test_type_combo.currentText())
            browser = next((b.text() for b in self.browser_group.buttons() if b.isChecked()), "Chrome")
            settings.setValue("browser", browser)
            settings.setValue("change_id", self.change_id_entry.text())
            env = next((e.text() for b in self.env_group.buttons() if b.isChecked()), "DEV")
            settings.setValue("environment", env)
            settings.setValue("start_date", self.start_date.date().toString("yyyy-MM-dd"))
            settings.setValue("end_date", self.end_date.date().toString("yyyy-MM-dd"))
            settings.setValue("tester", self.tester_entry.text())
            status = next((s.text() for s in self.status_group.buttons() if s.isChecked()), "Passed")
            settings.setValue("status", status)
            settings.setValue("test_cases", json.dumps(self.test_cases))
            settings.endGroup()

    def load_configuration(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("DetailsTab")
            self.title_entry.setText(settings.value("title", ""))
            self.project_name_entry.setText(settings.value("project_name", ""))
            self.project_version_entry.setText(settings.value("project_version", ""))
            self.test_type_combo.setCurrentText(settings.value("test_type", "Manual - Regression"))
            browser = settings.value("browser", "Chrome")
            for button in self.browser_group.buttons():
                if button.text() == browser:
                    button.setChecked(True)
                    break
            self.change_id_entry.setText(settings.value("change_id", ""))
            env = settings.value("environment", "DEV")
            for button in self.env_group.buttons():
                if button.text() == env:
                    button.setChecked(True)
                    break
            start_date = QDate.fromString(settings.value("start_date", QDate.currentDate().toString("yyyy-MM-dd")), "yyyy-MM-dd")
            self.start_date.setDate(start_date if start_date.isValid() else QDate.currentDate())
            end_date = QDate.fromString(settings.value("end_date", QDate.currentDate().toString("yyyy-MM-dd")), "yyyy-MM-dd")
            self.end_date.setDate(end_date if end_date.isValid() else QDate.currentDate())
            self.tester_entry.setText(settings.value("tester", ""))
            status = settings.value("status", "Passed")
            for button in self.status_group.buttons():
                if button.text() == status:
                    button.setChecked(True)
                    break
            test_cases_json = settings.value("test_cases", "[]")
            try:
                self.test_cases = json.loads(test_cases_json)
                for test_case in self.test_cases:
                    self.test_case_list.addItem(test_case)
            except json.JSONDecodeError:
                self.test_cases = []
                self.test_case_list.clear()
            finally:
                settings.endGroup()