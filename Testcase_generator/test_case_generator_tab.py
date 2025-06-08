from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class TestCaseGeneratorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_cases = [
            {
                "id": "TC001",
                "description": "Sample test case",
                "steps": "1. Open app\n2. Click button",
                "expected_result": "Button clicked",
                "status": "Passed"
            }
        ]
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Test Cases Table
        self.test_case_table = QTableWidget()
        self.test_case_table.setRowCount(0)
        self.test_case_table.setColumnCount(5)
        self.test_case_table.setHorizontalHeaderLabels(["ID", "Description", "Steps", "Expected Result", "Status"])
        self.test_case_table.setAlternatingRowColors(True)
        self.test_case_table.setSelectionMode(QTableWidget.SingleSelection)
        self.test_case_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.test_case_table.setMinimumHeight(300)
        layout.addWidget(self.test_case_table)

        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Test Case")
        add_btn.clicked.connect(self.add_test_case)
        button_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_test_case)
        button_layout.addWidget(remove_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.update_table()

    def update_table(self):
        self.test_case_table.setRowCount(0)
        for test_case in self.test_cases:
            row_position = self.test_case_table.rowCount()
            self.test_case_table.insertRow(row_position)
            self.test_case_table.setItem(row_position, 0, QTableWidgetItem(test_case["id"]))
            self.test_case_table.setItem(row_position, 1, QTableWidgetItem(test_case["description"]))
            self.test_case_table.setItem(row_position, 2, QTableWidgetItem(test_case["steps"]))
            self.test_case_table.setItem(row_position, 3, QTableWidgetItem(test_case["expected_result"]))
            self.test_case_table.setItem(row_position, 4, QTableWidgetItem(test_case["status"]))

    def add_test_case(self):
        new_test_case = {
            "id": f"TC{len(self.test_cases) + 1:03d}",
            "description": "New test case",
            "steps": "1. Step 1\n2. Step 2",
            "expected_result": "Expected outcome",
            "status": "Not Run"
        }
        self.test_cases.append(new_test_case)
        self.update_table()

    def remove_test_case(self):
        current_row = self.test_case_table.currentRow()
        if current_row >= 0:
            self.test_cases.pop(current_row)
            self.update_table()