from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                               QComboBox, QPushButton, QLineEdit, QGroupBox, QListWidget)
from PySide6.QtCore import Qt
import json

class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.issues = []
        self.setup_ui()
        self.load_configuration()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Test Results Table
        results_frame = QGroupBox("Test Results")
        results_layout = QVBoxLayout(results_frame)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["No", "Ticket ID", "Type", "Status", "Priority"])
        self.results_table.setColumnWidth(0, 50)
        self.results_table.setColumnWidth(1, 150)
        self.results_table.setColumnWidth(2, 150)
        self.results_table.setColumnWidth(3, 100)
        self.results_table.setColumnWidth(4, 100)
        results_layout.addWidget(self.results_table)

        # Add Result Row
        add_result_layout = QHBoxLayout()
        self.ticket_id_entry = QLineEdit()
        self.ticket_id_entry.setPlaceholderText("Enter ticket ID...")
        add_result_layout.addWidget(self.ticket_id_entry)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Bug", "Change Request", "Feature"])
        add_result_layout.addWidget(self.type_combo)

        self.status_entry = QLineEdit()
        self.status_entry.setPlaceholderText("Enter status...")
        add_result_layout.addWidget(self.status_entry)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        add_result_layout.addWidget(self.priority_combo)

        add_result_btn = QPushButton("Add Result")
        add_result_btn.clicked.connect(self.add_result)
        add_result_layout.addWidget(add_result_btn)

        results_layout.addLayout(add_result_layout)

        remove_result_btn = QPushButton("Remove Selected Result")
        remove_result_btn.clicked.connect(self.remove_result)
        results_layout.addWidget(remove_result_btn)

        layout.addWidget(results_frame)

        # Issues Frame
        issues_frame = QGroupBox("Issues Identified")
        issues_layout = QVBoxLayout(issues_frame)

        self.issue_entry = QLineEdit()
        self.issue_entry.setPlaceholderText("Enter issue description...")
        issues_layout.addWidget(self.issue_entry)

        add_issue_btn = QPushButton("Add Issue")
        add_issue_btn.clicked.connect(self.add_issue)
        issues_layout.addWidget(add_issue_btn)

        self.issues_list = QListWidget()
        issues_layout.addWidget(self.issues_list)

        remove_issue_btn = QPushButton("Remove Selected Issue")
        remove_issue_btn.clicked.connect(self.remove_issue)
        issues_layout.addWidget(remove_issue_btn)

        layout.addWidget(issues_frame)

    def add_result(self):
        ticket_id = self.ticket_id_entry.text().strip()
        type_text = self.type_combo.currentText()
        status = self.status_entry.text().strip()
        priority = self.priority_combo.currentText()

        if not ticket_id or not status:
            return

        row_count = self.results_table.rowCount()
        self.results_table.insertRow(row_count)

        self.results_table.setItem(row_count, 0, QTableWidgetItem(str(row_count + 1)))
        self.results_table.setItem(row_count, 1, QTableWidgetItem(ticket_id))

        type_combo = QComboBox()
        type_combo.addItems(["Bug", "Change Request", "Feature"])
        type_combo.setCurrentText(type_text)
        self.results_table.setCellWidget(row_count, 2, type_combo)

        self.results_table.setItem(row_count, 3, QTableWidgetItem(status))

        priority_combo = QComboBox()
        priority_combo.addItems(["High", "Medium", "Low"])
        priority_combo.setCurrentText(priority)
        self.results_table.setCellWidget(row_count, 4, priority_combo)

        self.ticket_id_entry.clear()
        self.status_entry.clear()
        self.save_configuration()

    def remove_result(self):
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            self.results_table.removeRow(current_row)
            for row in range(self.results_table.rowCount()):
                self.results_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.save_configuration()

    def add_issue(self):
        issue = self.issue_entry.text().strip()
        if issue:
            self.issues.append(issue)
            self.issues_list.addItem(issue)
            self.issue_entry.clear()
            self.save_configuration()

    def remove_issue(self):
        current_item = self.issues_list.currentItem()
        if current_item:
            row = self.issues_list.row(current_item)
            self.issues.pop(row)
            self.issues_list.takeItem(row)
            self.save_configuration()

    def save_configuration(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("ResultsTab")
            results = []
            for row in range(self.results_table.rowCount()):
                ticket_id = self.results_table.item(row, 1).text() if self.results_table.item(row, 1) else ""
                type_text = self.results_table.cellWidget(row, 2).currentText()
                status = self.results_table.item(row, 3).text() if self.results_table.item(row, 3) else ""
                priority = self.results_table.cellWidget(row, 4).currentText()
                results.append({
                    "ticket_id": ticket_id,
                    "type": type_text,
                    "status": status,
                    "priority": priority
                })
            settings.setValue("test_results", json.dumps(results))
            settings.setValue("issues", json.dumps(self.issues))
            settings.endGroup()

    def load_configuration(self):
        settings = self.parent().settings if hasattr(self.parent(), 'settings') else None
        if settings:
            settings.beginGroup("ResultsTab")
            results_json = settings.value("test_results", "[]")
            issues_json = settings.value("issues", "[]")
            try:
                results = json.loads(results_json)
                for i, result in enumerate(results):
                    self.results_table.insertRow(i)
                    self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    self.results_table.setItem(i, 1, QTableWidgetItem(result["ticket_id"]))

                    type_combo = QComboBox()
                    type_combo.addItems(["Bug", "Change Request", "Feature"])
                    type_combo.setCurrentText(result["type"])
                    self.results_table.setCellWidget(i, 2, type_combo)

                    self.results_table.setItem(i, 3, QTableWidgetItem(result["status"]))

                    priority_combo = QComboBox()
                    priority_combo.addItems(["High", "Medium", "Low"])
                    priority_combo.setCurrentText(result["priority"])
                    self.results_table.setCellWidget(i, 4, priority_combo)

                self.issues = json.loads(issues_json)
                for issue in self.issues:
                    self.issues_list.addItem(issue)
            except json.JSONDecodeError:
                pass
            settings.endGroup()