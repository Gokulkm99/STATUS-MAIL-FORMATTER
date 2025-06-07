import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import webbrowser
import tempfile
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QPushButton, QTextEdit, QGroupBox, QLabel)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSettings
from PySide6.QtGui import QFont, QIcon, QFontDatabase
from qt_material import apply_stylesheet  # For theming
from test_report_generator.details_tab import DetailsTab
from test_report_generator.results_tab import ResultsTab
from test_report_generator.settings_dialog import SettingsDialog
from test_report_generator.utils import NotificationDialog

# Default Configuration
DEFAULT_TEST_CONFIG = {
    "project_name": "",
    "project_version": "",
    "type_of_test": "Manual - Regression",
    "browser": "Chrome",
    "change_id": "",
    "environment": "DEV",
    "start_date": "",
    "end_date": "",
    "tester": "",
    "status": "Passed",
    "test_cases": [],
    "test_results": [],
    "issues": [],
    "notes": "",
    "recommendations": "",
    "conclusion": ""
}

class TestReportGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Report Generator")
        self.setMinimumSize(800, 600)
        self.config = DEFAULT_TEST_CONFIG.copy()
        self.theme = "dark_teal.xml"  # Synchronized with EODTool
        self.settings = QSettings("xAI", "TestReportGenerator")
        self.setup_ui()
        self.load_fonts()
        self.load_configuration()

    def load_fonts(self):
        font_db = QFontDatabase()
        families = font_db.families()
        if "Roboto" in families:
            self.setFont(QFont("Roboto", 10))
        elif "Calibri" in families:
            self.setFont(QFont("Calibri", 10))
        else:
            self.setFont(QFont("Arial", 10))

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top Bar
        top_bar = QHBoxLayout()
        main_layout.addLayout(top_bar)
        top_bar.addStretch()
        self.theme_button = QPushButton()
        self.theme_button.setIcon(QIcon.fromTheme("weather-clear"))
        self.theme_button.setFixedSize(48, 48)
        self.theme_button.setToolTip("Toggle Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.animate_button(self.theme_button)
        top_bar.addWidget(self.theme_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setIcon(QIcon.fromTheme("settings-configure"))
        self.settings_button.setToolTip("Open settings")
        self.settings_button.clicked.connect(self.show_settings_dialog)
        self.animate_button(self.settings_button)
        top_bar.addWidget(self.settings_button)

        # Tab Widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Tab 1: Test Report Details
        self.details_tab = DetailsTab(self)
        self.tab_widget.addTab(self.details_tab, "Test Report Details")

        # Tab 2: Test Results
        self.results_tab = ResultsTab(self)
        self.tab_widget.addTab(self.results_tab, "Test Results")

        # Tab 3: Comments
        comments_widget = QWidget()
        comments_layout = QVBoxLayout(comments_widget)
        comments_frame = QGroupBox("Comments")
        comments_inner = QVBoxLayout(comments_frame)

        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Enter notes here...")
        self.notes_text.setToolTip("Enter additional notes")
        self.notes_text.setFixedHeight(150)
        comments_inner.addWidget(QLabel("Notes:"))
        comments_inner.addWidget(self.notes_text)

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setPlaceholderText("Enter remarks here...")
        self.recommendations_text.setToolTip("Remarks")
        self.recommendations_text.setFixedHeight(150)
        comments_inner.addWidget(QLabel("Remarks:"))
        comments_inner.addWidget(self.recommendations_text)

        self.conclusion_text = QTextEdit()
        self.conclusion_text.setPlaceholderText("Enter conclusion here...")
        self.conclusion_text.setToolTip("Enter the conclusion")
        self.conclusion_text.setFixedHeight(150)
        comments_inner.addWidget(QLabel("Conclusion:"))
        comments_inner.addWidget(self.conclusion_text)
        comments_layout.addWidget(comments_frame)
        self.tab_widget.addTab(comments_widget, "Comments")

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate Report")
        generate_btn.setIcon(QIcon.fromTheme("document-save"))
        generate_btn.setToolTip("Generate and open the test report")
        generate_btn.clicked.connect(self.generate_report)
        self.animate_button(generate_btn)
        bottom_layout.addWidget(generate_btn)
        main_layout.addLayout(bottom_layout)

        # Apply theme initially
        self.apply_theme()

    def animate_button(self, button):
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        button.clicked.connect(lambda: self.start_button_animation(button, animation))

    def start_button_animation(self, button, animation):
        original_geometry = button.geometry()
        scaled_geometry = original_geometry.adjusted(-2, -2, 2, 2)
        animation.setStartValue(original_geometry)
        animation.setEndValue(scaled_geometry)
        animation.start()
        animation.finished.connect(lambda: button.setGeometry(original_geometry))

    def toggle_theme(self):
        # Delegate to the parent EODTool to toggle the application-wide theme
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'toggle_theme'):
                parent.toggle_theme()
                break
            parent = parent.parent()

    def apply_theme(self):
        # Synchronize with the parent's theme
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'theme'):
                self.theme = parent.theme
                break
            parent = parent.parent()
        # Apply minimal custom styles on top of qt-material theme
        extra_styles = """
            QTabWidget::pane {
                border: 1px solid #B0BEC5;
                border-radius: 4px;
            }
            QTabBar::tab {
                padding: 12px;
                margin-right: 4px;
                border-radius: 4px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14pt;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border-radius: 4px;
            }
            QComboBox, QDateEdit {
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12pt;
                min-height: 32px;
            }
            QTableWidget, QListWidget {
                padding: 8px;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 12px;
                min-height: 48px;
            }
        """
        self.setStyleSheet(extra_styles)
        self.theme_button.setIcon(QIcon.fromTheme("weather-clear" if "dark" in self.theme else "weather-clear-night"))

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def load_configuration(self):
        try:
            self.settings.beginGroup("Configuration")
            self.notes_text.setText(self.settings.value("notes", ""))
            self.recommendations_text.setText(self.settings.value("recommendations", ""))
            self.conclusion_text.setText(self.settings.value("conclusion", ""))
            self.settings.endGroup()
        except Exception as e:
            print(f"Failed to load configuration: {e}")

    def generate_report(self):
        title = self.details_tab.title_entry.text().strip() or "Test Report"
        project_name = self.details_tab.project_name_entry.text().strip()
        project_version = self.details_tab.project_version_entry.text().strip()
        test_type = self.details_tab.test_type_combo.currentText()
        browser = next((b.text() for b in self.details_tab.browser_group.buttons() if b.isChecked()), "Chrome")
        change_id = self.details_tab.change_id_entry.text().strip()
        environment = next((e.text() for b in self.details_tab.env_group.buttons() if b.isChecked()), "DEV")
        start_date = self.details_tab.start_date.date().toString("dd/MM/yyyy")
        end_date = self.details_tab.end_date.date().toString("dd/MM/yyyy")
        tester = self.details_tab.tester_entry.text().strip()
        status = next((s.text() for s in self.details_tab.status_group.buttons() if s.isChecked()), "Passed")
        test_cases = self.details_tab.test_cases
        test_results = []
        for row in range(self.results_tab.results_table.rowCount()):
            ticket_id = self.results_tab.results_table.item(row, 1).text() if self.results_tab.results_table.item(row, 1) else ""
            type_text = self.results_tab.results_table.cellWidget(row, 2).currentText()
            status_text = self.results_tab.results_table.item(row, 3).text() if self.results_tab.results_table.item(row, 3) else ""
            priority_text = self.results_tab.results_table.cellWidget(row, 4).currentText()
            test_results.append({
                "no": str(row + 1),
                "ticket_id": ticket_id,
                "type": type_text,
                "status": status_text,
                "priority": priority_text
            })
        issues = self.results_tab.issues
        notes = self.notes_text.toPlainText().strip()
        recommendations = self.recommendations_text.toPlainText().strip()
        conclusion = self.conclusion_text.toPlainText().strip()

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Calibri, Arial, sans-serif; font-size: 12pt; margin: 40px; max-width: 1000px; }}
        .header {{ background-color: #1976D2; color: white; padding: 20px; border-radius: 8px; }}
        .header h1 {{ margin: 0; font-size: 24pt; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #B0BEC5; padding: 12px; text-align: left; }}
        th {{ background-color: #1976D2; color: white; }}
        h2 {{ color: #1976D2; font-size: 18pt; margin-top: 20px; }}
        .status-passed {{ color: #388E3C; font-weight: bold; }}
        .status-fail {{ color: #D32F2F; font-weight: bold; }}
        .status-blocked {{ color: #FBC02D; font-weight: bold; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
        .footer {{ text-align: center; color: #616161; margin-top: 40px; padding-top: 20px; border-top: 1px solid #B0BEC5; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
    </div>
    <h2>Test Report Details</h2>
    <p><b>Project Name & Version:</b> {project_name} {project_version}</p>
    <p><b>Type of Test:</b> {test_type}</p>
    <p><b>Browser:</b> {browser}</p>
    <p><b>Change ID:</b> {change_id}</p>
    <p><b>Environment:</b> {environment}</p>
    <p><b>Start Date:</b> {start_date}</p>
    <p><b>End Date:</b> {end_date}</p>
    <p><b>Tester:</b> {tester}</p>
    <p><b>Status:</b> <span class="status-{status.lower()}">{status}</span></p>

    <h2>Summary</h2>
    <p>The QA team tested <b>{project_name}</b> to ensure its functionality, reliability, and performance. This report summarizes the test results and any issues encountered during testing.</p>

    <h2>Test Cases</h2>
    <ul>
"""
        for i, test_case in enumerate(test_cases, 1):
            html_content += f"<li><b>Test Case {i}:</b> {test_case}</li>\n"
        html_content += """
    </ul>

    <h2>Test Results</h2>
    <table>
        <thead>
            <tr>
                <th>No</th>
                <th>Ticket ID</th>
                <th>Type</th>
                <th>Status</th>
                <th>Priority</th>
            </tr>
        </thead>
        <tbody>
"""
        for result in test_results:
            type_color = {"Bug": "#EF5350", "Change Request": "#42A5F5", "Feature": "#66BB6A"}.get(result["type"], "#000000")
            html_content += f"""
            <tr>
                <td>{result['no']}</td>
                <td>{result['ticket_id']}</td>
                <td style="color: {type_color};">{result['type']}</td>
                <td>{result['status']}</td>
                <td>{result['priority']}</td>
            </tr>
"""
        html_content += """
        </tbody>
    </table>

    <h2>Issues Identified</h2>
    <ul>
"""
        for issue in issues:
            html_content += f"<li>{issue}</li>\n"
        html_content += """
    </ul>

    <h2>Comments</h2>
    <p><b>Notes:</b> {notes}</p>
    <p><b>Remarks:</b> {recommendations}</p>
    <p><b>Conclusion:</b> {conclusion}</p>
    <div class="footer">
        <p>Generated by Test Report Generator on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
                f.write(html_content)
                webbrowser.open('file://' + os.path.realpath(f.name))
            NotificationDialog("Test report generated and opened in browser!", "Success", parent=self).exec()
        except Exception as e:
            NotificationDialog(f"Failed to generate report:\n{e}", "Error", is_error=True, parent=self).exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_teal.xml")
    widget = TestReportGeneratorWidget()
    widget.show()
    sys.exit(app.exec())