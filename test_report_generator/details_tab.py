from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
                               QDateEdit, QGroupBox, QPushButton, QButtonGroup, QRadioButton, QScrollArea)
from PySide6.QtCore import Qt, QDate

class DetailsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_cases = []
        self.browser_group = QButtonGroup(self)
        self.env_group = QButtonGroup(self)
        self.status_group = QButtonGroup(self)
        self.setup_ui()
        self.load_dynamic_options()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top Bar
        top_bar = QHBoxLayout()
        main_layout.addLayout(top_bar)
        top_bar.addStretch()
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

        # Test Details Frame
        details_frame = QGroupBox("Test Details")
        details_frame.setMinimumWidth(600)
        details_layout = QFormLayout(details_frame)
        details_layout.setLabelAlignment(Qt.AlignRight)
        details_layout.setSpacing(10)
        details_layout.setContentsMargins(15, 20, 15, 15)

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
        self.test_type_combo.addItems(["Manual - Regression", "Manual - Functional", "Automation", "Performance"])
        details_layout.addRow("Type of Test:", self.test_type_combo)

        self.change_id_entry = QLineEdit()
        self.change_id_entry.setPlaceholderText("Enter change ID...")
        details_layout.addRow("Change ID:", self.change_id_entry)

        # Browser Frame
        browser_frame = QGroupBox("Browser")
        browser_frame.setMinimumWidth(500)
        browser_inner_layout = QHBoxLayout(browser_frame)
        browser_inner_layout.setSpacing(10)
        browser_inner_layout.setContentsMargins(15, 10, 15, 10)
        self.browser_layout = QHBoxLayout()
        browser_inner_layout.addLayout(self.browser_layout)
        browser_inner_layout.addStretch()
        details_layout.addRow("", browser_frame)

        # Environment Frame
        env_frame = QGroupBox("Environment")
        env_frame.setMinimumWidth(500)
        env_inner_layout = QHBoxLayout(env_frame)
        env_inner_layout.setSpacing(10)
        env_inner_layout.setContentsMargins(15, 10, 15, 10)
        self.env_layout = QHBoxLayout()
        env_inner_layout.addLayout(self.env_layout)
        env_inner_layout.addStretch()
        details_layout.addRow("", env_frame)

        # Start Date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        details_layout.addRow("Start Date:", self.start_date)

        # End Date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        details_layout.addRow("End Date:", self.end_date)

        # Tester
        self.tester_entry = QLineEdit()
        self.tester_entry.setPlaceholderText("Enter tester name...")
        details_layout.addRow("Tester:", self.tester_entry)

        # Status Frame
        status_frame = QGroupBox("Status")
        status_frame.setMinimumWidth(500)
        status_inner_layout = QHBoxLayout(status_frame)
        status_inner_layout.setSpacing(10)
        status_inner_layout.setContentsMargins(15, 10, 15, 10)
        self.status_layout = QHBoxLayout()
        status_inner_layout.addLayout(self.status_layout)
        status_inner_layout.addStretch()
        details_layout.addRow("", status_frame)

        container_layout.addWidget(details_frame)
        container_layout.addStretch()

        # Next Button
        next_btn = QPushButton("Next")
        next_btn.setToolTip("Go to Test Results")
        next_btn.setFixedWidth(50)
        next_btn.clicked.connect(self.go_to_results_tab)
        self.parent().animate_button(next_btn)
        container_layout.addWidget(next_btn, alignment=Qt.AlignBottom | Qt.AlignRight)

        main_layout.addWidget(scroll)

    def go_to_results_tab(self):
        # Navigate to the Results tab in the TestReportGeneratorWidget's tab_widget
        if hasattr(self.parent(), 'tab_widget'):
            self.parent().tab_widget.setCurrentIndex(1)
        else:
            print("Error: Could not find tab_widget for navigation")

    def load_dynamic_options(self):
        # Store current selections
        current_browser = next((b.text() for b in self.browser_group.buttons() if b.isChecked()), None)
        current_env = next((e.text() for e in self.env_group.buttons() if e.isChecked()), None)
        current_status = next((s.text() for s in self.status_group.buttons() if s.isChecked()), None)

        # Clear existing buttons safely
        for group, layout in [(self.browser_group, self.browser_layout),
                              (self.env_group, self.env_layout),
                              (self.status_group, self.status_layout)]:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    group.removeButton(widget)
                    widget.deleteLater()

        # Load browsers
        browsers = self.parent().config.get("browsers", ["Chrome", "Firefox", "Edge", "Safari"])
        default_browser = self.parent().config.get("browser", browsers[0])
        for browser in browsers:
            radio = QRadioButton(browser)
            radio.setChecked(browser == (current_browser or default_browser))
            self.browser_group.addButton(radio)
            self.browser_layout.addWidget(radio)
        self.browser_layout.addStretch()

        # Load environments
        environments = self.parent().config.get("environments", ["DEV", "QA", "UAT", "PROD"])
        default_env = self.parent().config.get("environment", environments[0])
        for env in environments:
            radio = QRadioButton(env)
            radio.setChecked(env == (current_env or default_env))
            self.env_group.addButton(radio)
            self.env_layout.addWidget(radio)
        self.env_layout.addStretch()

        # Load statuses
        statuses = self.parent().config.get("statuses", ["Passed", "Fail", "Blocked"])
        default_status = self.parent().config.get("status", statuses[0])
        for status in statuses:
            radio = QRadioButton(status)
            radio.setChecked(status == (current_status or default_status))
            self.status_group.addButton(radio)
            self.status_layout.addWidget(radio)
        self.status_layout.addStretch()