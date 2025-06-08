from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QPushButton, QGroupBox, QComboBox, QTextEdit, QLabel)
from PySide6.QtCore import Qt

class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.issues = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Top Bar
        top_bar = QHBoxLayout()
        layout.addLayout(top_bar)
        top_bar.addStretch()
        settings_button = QPushButton("⚙ Settings")
        settings_button.setToolTip("Open settings")
        settings_button.clicked.connect(self.parent().show_settings_dialog)
        self.parent().animate_button(settings_button)
        top_bar.addWidget(settings_button)

        # Results Frame
        results_frame = QGroupBox("Test Results")
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(10)

        button_layout = QHBoxLayout()
        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(self.add_row)
        self.parent().animate_button(add_row_btn)
        button_layout.addWidget(add_row_btn)

        remove_row_btn = QPushButton("Remove Selected Row")
        remove_row_btn.clicked.connect(self.remove_row)
        self.parent().animate_button(remove_row_btn)
        button_layout.addWidget(remove_row_btn)

        button_layout.addStretch()
        results_layout.addLayout(button_layout)

        self.results_table = QTableWidget()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["No", "Ticket ID", "Type", "Status", "Priority"])
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setMinimumHeight(150)
        results_layout.addWidget(self.results_table)

        issues_frame = QGroupBox("Issues")
        issues_layout = QVBoxLayout(issues_frame)
        issues_layout.addWidget(QLabel("Issues Identified:"))

        self.issues_text = QTextEdit()
        self.issues_text.setPlaceholderText("Enter issues here (one per line)...")
        self.issues_text.setFixedHeight(100)
        issues_layout.addWidget(self.issues_text)

        button_layout2 = QHBoxLayout()
        add_issue_btn = QPushButton("Add Issue")
        add_issue_btn.clicked.connect(self.add_issue)
        self.parent().animate_button(add_issue_btn)
        button_layout2.addWidget(add_issue_btn)

        remove_issue_btn = QPushButton("Remove Selected Issue")
        remove_issue_btn.clicked.connect(self.remove_issue)
        self.parent().animate_button(remove_issue_btn)
        button_layout2.addWidget(remove_issue_btn)

        button_layout2.addStretch()
        issues_layout.addLayout(button_layout2)

        self.issues_list = QTableWidget()
        self.issues_list.setRowCount(0)
        self.issues_list.setColumnCount(2)
        self.issues_list.setHorizontalHeaderLabels(["No", "Issue"])
        self.issues_list.setAlternatingRowColors(True)
        self.issues_list.setSelectionMode(QTableWidget.SingleSelection)
        self.issues_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.issues_list.setMinimumHeight(150)
        issues_layout.addWidget(self.issues_list)

        layout.addWidget(results_frame)
        layout.addStretch()

        # Next Button
        next_btn = QPushButton("Next")
        next_btn.setToolTip("Go to Comments")
        next_btn.setFixedWidth(50)
        next_btn.clicked.connect(self.goto_comments_tab)
        self.parent().animate_button(next_btn)
        layout.addWidget(next_btn, alignment=Qt.AlignBottom | Qt.AlignRight)

    def goto_comments_tab(self):
        # Navigate to the Comments tab in the TestReportGeneratorWidget's tab_widget
        if hasattr(self.parent(), 'tab_widget'):
            self.parent().tab_widget.setCurrentIndex(2)
        else:
            print("Error: Could not find tab_widget for navigation")

    def add_row(self):
        row_position = self.results_table.rowCount()
        self.results_table.insertRow(row_position)

        self.results_table.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))
        self.results_table.setItem(row_position, 1, QTableWidgetItem(""))
        type_combo = QComboBox()
        type_combo.addItems(["Bug", "Change Request", "Feature"])
        self.results_table.setCellWidget(row_position, 2, type_combo)
        self.results_table.setItem(row_position, 3, QTableWidgetItem(""))
        priority_combo = QComboBox()
        priority_combo.addItems(["High", "Medium", "Low"])
        self.results_table.setCellWidget(row_position, 4, priority_combo)

    def remove_row(self):
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            self.results_table.removeRow(current_row)
            for row in range(self.results_table.rowCount()):
                self.results_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

    def add_issue(self):
        issue_text = self.issues_text.toPlainText().strip()
        if issue_text:
            for issue in issue_text.split('\n'):
                issue = issue.strip()
                if issue:
                    self.issues.append(issue)
                    row_position = self.issues_list.rowCount()
                    self.issues_list.insertRow(row_position)
                    self.issues_list.setItem(row_position, 0, QTableWidgetItem(str(row_position + 1)))
                    self.issues_list.setItem(row_position, 1, QTableWidgetItem(issue))
            self.issues_text.clear()

    def remove_issue(self):
        current_row = self.issues_list.currentRow()
        if current_row >= 0:
            self.issues.pop(current_row)
            self.issues_list.removeRow(current_row)
            for row in range(self.issues_list.rowCount()):
                self.issues_list.setItem(row, 0, QTableWidgetItem(str(row + 1)))