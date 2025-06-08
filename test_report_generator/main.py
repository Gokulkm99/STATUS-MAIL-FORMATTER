import sys
import os
import json
import webbrowser
import tempfile
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QPushButton, QScrollArea)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSettings
from PySide6.QtGui import QFont, QFontDatabase
from test_report_generator.details_tab import DetailsTab
from test_report_generator.results_tab import ResultsTab
from test_report_generator.comments_tab import CommentsTab
from test_report_generator.settings_dialog import SettingsDialog
from test_report_generator.utils import NotificationDialog

# Default Configuration
DEFAULT_TEST_CONFIG = {
    "project_name": "",
    "project_version": "",
    "type_of_test": "Manual - Regression",
    "browser": "Chrome",
    "browsers": ["Chrome", "Firefox", "Edge", "Safari"],
    "change_id": "",
    "environment": "DEV",
    "environments": ["DEV", "QA", "UAT", "PROD"],
    "start_date": "",
    "end_date": "",
    "tester": "",
    "status": "Passed",
    "statuses": ["Passed", "Fail", "Blocked"],
    "test_cases": [],
    "test_results": [],
    "issues": [],
    "notes": "",
    "recommendations": "",
    "conclusion": ""
}

class TestReportGeneratorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = DEFAULT_TEST_CONFIG.copy()
        self.settings = QSettings("xAI", "TestReportGenerator")
        self.theme = self.settings.value("theme", "dark_default")
        
        # Create test_report_config.json if it doesn't exist
        config_path = "test_report_config.json"
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_TEST_CONFIG, f, indent=4)
        
        self.setObjectName("EODTaskTracker")
        self.setup_ui()
        self.load_fonts()
        self.load_configuration()
        self.apply_theme(self.theme)

    def load_fonts(self):
        font_db = QFontDatabase()
        families = font_db.families()
        if "Roboto" in families:
            self.setFont(QFont("Roboto", 12))
        elif "Calibri" in families:
            self.setFont(QFont("Calibri", 12))
        else:
            self.setFont(QFont("Arial", 12))

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Scroll Area for Main Content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        sub_widget = QWidget()
        scroll_layout = QVBoxLayout(sub_widget)
        scroll_layout.setContentsMargins(15, 10, 15, 5)
        scroll_area.setWidget(sub_widget)
        main_layout.addWidget(scroll_area)

        # Tab Widget
        self.tab_widget = QTabWidget()
        scroll_layout.addWidget(self.tab_widget)

        # Tab 1: Test Report Details
        self.details_tab = DetailsTab(self)
        self.tab_widget.addTab(self.details_tab, "Test Report Details")

        # Tab 2: Test Results
        self.results_tab = ResultsTab(self)
        self.tab_widget.addTab(self.results_tab, "Test Results")

        # Tab 3: Comments
        self.comments_tab = CommentsTab(self)
        self.tab_widget.addTab(self.comments_tab, "Comments")

        # Bottom-right layout
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        scroll_layout.addLayout(bottom_layout)

    def show_info_dialog(self):
        NotificationDialog("Test Report Generator v1.0\nDeveloped by Gokul\nFor support, contact support@", "Info", parent=self).exec()

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

    def apply_theme(self, theme_name):
        themes = {
            "dark_default": {
                "background": "#212121",
                "frame_background": "#272727",
                "text_color": "#E0E0E0",
                "label_color": "#B0BEC5",
                "input_background": "#333333",
                "border_color": "#424242",
                "button_background": "#1976D2",
                "button_hover": "#1565C0",
                "button_disabled": "#424242",
                "list_background": "#272727",
                "list_alternate": "#303030"
            },
            "dark_blue": {
                "background": "#1A2526",
                "frame_background": "#2A3B3D",
                "text_color": "#DDEEFF",
                "label_color": "#A1C1D2",
                "input_background": "#3A4B4D",
                "border_color": "#526364",
                "button_background": "#2A7B9B",
                "button_hover": "#1F5A73",
                "button_disabled": "#3A4B4D",
                "list_background": "#2A3B3D",
                "list_alternate": "#3A4B4D"
            },
            "dark_purple": {
                "background": "#2A1D34",
                "frame_background": "#3A2D44",
                "text_color": "#E6D8F0",
                "label_color": "#BBA8CC",
                "input_background": "#4A3D54",
                "border_color": "#62556C",
                "button_background": "#7B2CBF",
                "button_hover": "#5A1F8F",
                "button_disabled": "#4A3D54",
                "list_background": "#3A2D44",
                "list_alternate": "#4A3D54"
            },
            "dark_green": {
                "background": "#1A2F26",
                "frame_background": "#2A3F34",
                "text_color": "#D0E6D8",
                "label_color": "#A0C1B0",
                "input_background": "#3A4F44",
                "border_color": "#506354",
                "button_background": "#2A9B5B",
                "button_hover": "#1F733F",
                "button_disabled": "#3A4F44",
                "list_background": "#2A3F34",
                "list_alternate": "#3A4F44"
            },
            "light_gray": {
                "background": "#E0E0E0",
                "frame_background": "#F0F0F0",
                "text_color": "#212121",
                "label_color": "#616161",
                "input_background": "#FFFFFF",
                "border_color": "#B0BEC5",
                "button_background": "#1976D2",
                "button_hover": "#1565C0",
                "button_disabled": "#B0BEC5",
                "list_background": "#F0F0F0",
                "list_alternate": "#E5E5E5"
            }
        }

        theme = themes.get(theme_name, themes["dark_default"])
        stylesheet = f"""
            QWidget#EODTaskTracker {{
                background-color: {theme['background']};
                color: {theme['text_color']};
            }}
            QWidget#EODTaskTracker QFrame#sectionFrame {{
                background-color: {theme['frame_background']};
                border: 1px solid {theme['border_color']};
                border-radius: 10px;
                margin-top: 10px;
            }}
            QWidget#EODTaskTracker QLabel#sectionLabel {{
                color: {theme['text_color']};
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
            }}
            QWidget#EODTaskTracker QLabel {{
                color: {theme['label_color']};
                font-family: Roboto;
                font-size: 16px;
            }}
            QWidget#EODTaskTracker QLineEdit,
            QWidget#EODTaskTracker QTextEdit,
            QWidget#EODTaskTracker QComboBox,
            QWidget#EODTaskTracker QDateEdit {{
                background-color: {theme['input_background']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }}
            QWidget#EODTaskTracker QPushButton {{
                background-color: {theme['button_background']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-family: Roboto;
                font-size: 16px;
                font-weight: bold;
            }}
            QWidget#EODTaskTracker QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QWidget#EODTaskTracker QPushButton:disabled {{
                background-color: {theme['button_disabled']};
                color: #666666;
            }}
            QWidget#EODTaskTracker QRadioButton {{
                color: {theme['label_color']};
                font-family: Roboto;
                font-size: 16px;
            }}
            QWidget#EODTaskTracker QTableWidget,
            QWidget#EODTaskTracker QListWidget {{
                background-color: {theme['list_background']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 5px;
                padding: 8px;
                font-family: Roboto;
                font-size: 16px;
            }}
            QWidget#EODTaskTracker QTableWidget::item:selected,
            QWidget#EODTaskTracker QListWidget::item:selected {{
                background-color: {theme['button_background']};
                color: white;
            }}
            QWidget#EODTaskTracker QTableWidget::item:alternate {{
                background-color: {theme['list_alternate']};
            }}
            QWidget#EODTaskTracker QTabWidget::pane {{
                border: 1px solid {theme['border_color']};
                background-color: {theme['background']};
            }}
            QWidget#EODTaskTracker QTabBar::tab {{
                background-color: {theme['frame_background']};
                color: {theme['text_color']};
                padding: 8px 20px;
                border: 1px solid {theme['border_color']};
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QWidget#EODTaskTracker QTabBar::tab:selected {{
                background-color: {theme['button_background']};
                color: white;
            }}
            QWidget#EODTaskTracker QScrollArea,
            QWidget#EODTaskTracker QScrollArea > QWidget > QWidget {{
                background-color: {theme['background']};
                color: {theme['text_color']};
            }}
        """
        self.setStyleSheet(stylesheet)

    def toggle_theme(self):
        themes = ["dark_default", "dark_blue", "dark_purple", "dark_green", "light_gray"]
        current_index = themes.index(self.theme) if self.theme in themes else 0
        self.theme = themes[(current_index + 1) % len(themes)]
        self.settings.setValue("theme", self.theme)
        self.apply_theme(self.theme)

    def show_settings_dialog(self):
        try:
            print("Opening settings dialog")
            dialog = SettingsDialog(self)
            if dialog.exec():
                print("Settings dialog closed with accept")
                self.details_tab.load_dynamic_options()
                self.load_configuration()
                self.apply_theme(self.theme)
        except Exception as e:
            print(f"Error in show_settings_dialog: {e}")
            NotificationDialog(f"Failed to open settings dialog:\n{e}", "Error", is_error=True, parent=self).exec()

    def load_configuration(self):
        try:
            self.settings.beginGroup("Configuration")
            self.comments_tab.notes_text.setText(self.settings.value("notes", ""))
            self.comments_tab.recommendations_text.setText(self.settings.value("recommendations", ""))
            self.comments_tab.conclusion_text.setText(self.settings.value("conclusion", ""))
            self.config["browsers"] = json.loads(self.settings.value("browsers", json.dumps(["Chrome", "Firefox", "Edge", "Safari"])))
            self.config["environments"] = json.loads(self.settings.value("environments", json.dumps(["DEV", "QA", "UAT", "PROD"])))
            self.config["statuses"] = json.loads(self.settings.value("statuses", json.dumps(["Passed", "Fail", "Blocked"])))
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
        environment = next((e.text() for e in self.details_tab.env_group.buttons() if e.isChecked()), "DEV")
        start_date = self.details_tab.start_date.date().toString("dd/MM/yyyy")
        end_date = self.details_tab.end_date.date().toString("dd/MM/yyyy")
        tester = self.details_tab.tester_entry.text().strip()
        status = next((s.text() for s in self.details_tab.status_group.buttons() if s.isChecked()), "Passed")
        test_cases = []  # No TestCaseGeneratorTab provided
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
        notes = self.comments_tab.notes_text.toPlainText().strip()
        recommendations = self.comments_tab.recommendations_text.toPlainText().strip()
        conclusion = self.comments_tab.conclusion_text.toPlainText().strip()

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
    <p>No test cases provided.</p>

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