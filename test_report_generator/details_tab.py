from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
                               QRadioButton, QGroupBox, QPushButton, QDateEdit, QListWidget, QButtonGroup)
from PySide6.QtCore import QDate
import json

class DetailsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_cases = []
        self.setup_ui()
        self.load_configuration()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Test Report Details Frame
        details_frame = QGroupBox("Test Report Details")
        details_layout = QFormLayout(details_frame)

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

        browser_group = QGroupBox("Browser")
        browser_layout = QVBoxLayout(browser_group)
        self.browser_group = QButtonGroup()
        browsers = ["Chrome", "Firefox", "Edge", "Safari"]
        for browser in browsers:
            radio = QRadioButton(browser)
            if browser == "Chrome":
                radio.setChecked(True)
            self.browser_group.addButton(radio)
            browser_layout.addWidget(radio)
        details_layout.addRow(browser_group)

        self.change_id_entry = QLineEdit()
        self.change_id_entry.setPlaceholderText("Enter change ID...")
        details_layout.addRow("Change ID:", self.change_id_entry)

        env_group = QGroupBox("Environment")
        env_layout = QVBoxLayout(env_group)
        self.env_group = QButtonGroup()
        envs = ["DEV", "QA", "UAT", "PROD"]
        for env in envs:
            radio = QRadioButton(env)
            if env == "DEV":
                radio.setChecked(True)
            self.env_group.addButton(radio)
            env_layout.addWidget(radio)
        details_layout.addRow(env_group)

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

        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        self.status_group = QButtonGroup()
        statuses = ["Passed", "Fail", "Blocked"]
        for status in statuses:
            radio = QRadioButton(status)
            if status == "Passed":
                radio.setChecked(True)
            self.status_group.addButton(radio)
            status_layout.addWidget(radio)
        details_layout.addRow(status_group)

        layout.addWidget(details_frame)

        # Test Cases Frame
        test_cases_frame = QGroupBox("Test Cases")
        test_cases_layout = QVBoxLayout(test_cases_frame)

        self.test_case_entry = QLineEdit()
        self.test_case_entry.setPlaceholderText("Enter test case description...")
        test_cases_layout.addWidget(self.test_case_entry)

        add_test_case_btn = QPushButton("Add Test Case")
        add_test_case_btn.clicked.connect(self.add_test_case)
        test_cases_layout.addWidget(add_test_case_btn)

        self.test_case_list = QListWidget()
        test_cases_layout.addWidget(self.test_case_list)

        remove_test_case_btn = QPushButton("Remove Selected Test Case")
        remove_test_case_btn.clicked.connect(self.remove_test_case)
        test_cases_layout.addWidget(remove_test_case_btn)

        layout.addWidget(test_cases_frame)

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