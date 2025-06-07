import sys
import json
import os
import webbrowser
import tempfile
from datetime import date
import base64
import urllib.parse
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLabel, QComboBox, QLineEdit, QRadioButton, QPushButton, QListWidget,
                               QScrollArea, QFileDialog, QMessageBox, QFrame, QTabWidget, QGroupBox,
                               QListWidgetItem, QSizePolicy, QSystemTrayIcon, QMenu, QDialog)
from PySide6.QtCore import Qt, QSize, QTimer, QDateTime
from PySide6.QtGui import QClipboard, QCloseEvent
import win32clipboard  # For clipboard handling to support Outlook HTML pasting
import datetime
# Import the Test Report Generator widget
from test_report_generator import TestReportGeneratorWidget

# Setup logging to debug notifications
logging.basicConfig(filename='notification.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration File Paths
DEFAULT_CONFIG_FILE = "config.json"
DEFAULT_TASKS_FILE = "tasks.json"

# Set the default persistent directory to STATUS MAIL FORMATTER/Json subdirectory
DEFAULT_PERSISTENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Json")
if not os.path.exists(DEFAULT_PERSISTENT_DIR):
    os.makedirs(DEFAULT_PERSISTENT_DIR)

DEFAULT_PERSISTENT_CONFIG_PATH = os.path.join(DEFAULT_PERSISTENT_DIR, DEFAULT_CONFIG_FILE)
DEFAULT_PERSISTENT_TASKS_PATH = os.path.join(DEFAULT_PERSISTENT_DIR, DEFAULT_TASKS_FILE)

# Default Configuration
DEFAULT_CONFIG = {
    "config_file_path": DEFAULT_PERSISTENT_CONFIG_PATH,
    "tasks_file_path": DEFAULT_PERSISTENT_TASKS_PATH,
    "logo_path": "",
    "main_projects": {},
    "task_types": ["Dev", "Bugfix", "Test"],
    "labels": {},
    "signature": {"name": "", "mobile": "", "email": ""},
    "email": {"to": "", "cc": ""},
    "notification_time": "18:00"  # Default to 6:00 PM
}

# Status Labels and Colors
STATUS_LABELS = {
    "Completed": "Completed",
    "In Progress": "In Progress",
    "To Be Done": "To Be Done",
    "Blocked": "Blocked"
}
STATUS_COLORS = {
    "Completed": "#5e8f59",
    "In Progress": "#c06530",
    "To Be Done": "#029de6",
    "Blocked": "#ff0000"
}

# Utility Functions
def load_config(config_path, default_path):
    config_path = get_config_or_tasks_path(DEFAULT_CONFIG_FILE, config_path, default_path)
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG.copy(), config_path
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        for subkey in DEFAULT_CONFIG["signature"]:
            if subkey not in config["signature"]:
                config["signature"][subkey] = DEFAULT_CONFIG["signature"][subkey]
        for subkey in DEFAULT_CONFIG["email"]:
            if subkey not in config["email"]:
                config["email"][subkey] = DEFAULT_CONFIG["email"][subkey]
        return config, config_path
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy(), config_path

def save_config(config, config_path):
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        QMessageBox.critical(None, "Save Config Error", f"Failed to save configuration:\n{e}")

def encode_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding image: {e}")
        return ""

def preview_email_html(html_content):
    try:
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html_content)
            webbrowser.open('file://' + os.path.realpath(f.name))
    except Exception as e:
        QMessageBox.critical(None, "Preview Error", f"Failed to preview email:\n{e}")

def get_config_or_tasks_path(filename, user_specified_path, default_path):
    if user_specified_path and os.path.dirname(user_specified_path) and os.path.exists(os.path.dirname(user_specified_path)):
        if not os.path.exists(user_specified_path):
            if os.path.exists(default_path):
                try:
                    os.makedirs(os.path.dirname(user_specified_path), exist_ok=True)
                    with open(default_path, 'rb') as src, open(user_specified_path, 'wb') as dst:
                        dst.write(src.read())
                except Exception as e:
                    print(f"Error copying {filename} to user-specified location: {e}")
        return user_specified_path
    else:
        if not os.path.exists(default_path):
            pass  # In this simplified version, we assume the default config is sufficient
        return default_path

# Function to set HTML content to clipboard in CF_HTML format for Outlook compatibility
def set_clipboard_html(html_content):
    # Construct the CF_HTML header
    html_bytes = html_content.encode('utf-8')
    html_length = len(html_bytes)

    # CF_HTML header format (required by Outlook and other Windows applications)
    header = (
        f"Version:0.9\r\n"
        f"StartHTML:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n')}\r\n"
        f"EndHTML:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n') + html_length}\r\n"
        f"StartFragment:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n<!DOCTYPE html><html><body>')}\r\n"
        f"EndFragment:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n<!DOCTYPE html><html><body>') + html_length}\r\n"
    )

    # Combine header and HTML content
    cf_html = header.encode('utf-8') + html_bytes

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat("HTML Format"), cf_html)
        # Also set plain text as a fallback
        plain_text = html_content.replace('<br>', '\n').replace('</p>', '\n').replace('</li>', '\n').replace(r'<[^>]+>', '')
        win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, plain_text.encode('utf-8'))
    finally:
        win32clipboard.CloseClipboard()

# Settings Widget Class
class SettingsWidget(QWidget):
    def __init__(self, parent, config, config_path, on_save_callback):
        super().__init__(parent)
        self.parent = parent
        self.config = config.copy()
        self.config_path = config_path
        self.on_save_callback = on_save_callback
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Scroll Area for Settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # File Locations Section
        file_group = QGroupBox("File Locations")
        file_layout = QFormLayout(file_group)
        file_layout.setLabelAlignment(Qt.AlignRight)

        self.config_file_entry = QLineEdit(self.config.get("config_file_path", DEFAULT_PERSISTENT_CONFIG_PATH))
        config_browse_btn = QPushButton("Browse")
        config_browse_btn.clicked.connect(self.browse_config_file)
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.config_file_entry)
        config_layout.addWidget(config_browse_btn)
        file_layout.addRow("Config File Path:", config_layout)

        self.tasks_file_entry = QLineEdit(self.config.get("tasks_file_path", DEFAULT_PERSISTENT_TASKS_PATH))
        tasks_browse_btn = QPushButton("Browse")
        tasks_browse_btn.clicked.connect(self.browse_tasks_file)
        tasks_layout = QHBoxLayout()
        tasks_layout.addWidget(self.tasks_file_entry)
        tasks_layout.addWidget(tasks_browse_btn)
        file_layout.addRow("Tasks File Path:", tasks_layout)

        scroll_layout.addWidget(file_group)

        # Logo Path Section
        logo_group = QGroupBox("Logo Path")
        logo_layout = QFormLayout(logo_group)
        logo_layout.setLabelAlignment(Qt.AlignRight)

        self.logo_entry = QLineEdit(self.config["logo_path"])
        logo_browse_btn = QPushButton("Browse")
        logo_browse_btn.clicked.connect(self.browse_logo)
        logo_inner_layout = QHBoxLayout()
        logo_inner_layout.addWidget(self.logo_entry)
        logo_inner_layout.addWidget(logo_browse_btn)
        logo_layout.addRow("Logo File:", logo_inner_layout)

        scroll_layout.addWidget(logo_group)

        # Main Projects and Sub-Projects Section
        project_group = QGroupBox("Main Projects and Sub-Projects")
        project_layout = QVBoxLayout(project_group)

        # Main Project List
        project_layout.addWidget(QLabel("Main Projects:"))
        self.main_project_list = QListWidget()
        for main_project in self.config["main_projects"]:
            self.main_project_list.addItem(main_project)
        self.main_project_list.currentItemChanged.connect(self.update_sub_project_list)
        project_layout.addWidget(self.main_project_list)

        # Add Main Project
        main_project_input_layout = QHBoxLayout()
        main_project_input_layout.addWidget(QLabel("New Main Project:"))
        self.new_main_project_entry = QLineEdit()
        main_project_input_layout.addWidget(self.new_main_project_entry)
        add_main_btn = QPushButton("Add Main Project")
        add_main_btn.clicked.connect(self.add_main_project)
        main_project_input_layout.addWidget(add_main_btn)
        remove_main_btn = QPushButton("Remove Main Project")
        remove_main_btn.clicked.connect(self.remove_main_project)
        main_project_input_layout.addWidget(remove_main_btn)
        project_layout.addLayout(main_project_input_layout)

        # Sub-Project List
        project_layout.addWidget(QLabel("Sub-Projects:"))
        self.sub_project_list = QListWidget()
        project_layout.addWidget(self.sub_project_list)

        # Add Sub-Project
        sub_project_input_layout = QHBoxLayout()
        sub_project_input_layout.addWidget(QLabel("New Sub-Project:"))
        self.new_sub_project_entry = QLineEdit()
        sub_project_input_layout.addWidget(self.new_sub_project_entry)
        add_sub_btn = QPushButton("Add Sub-Project")
        add_sub_btn.clicked.connect(self.add_sub_project)
        sub_project_input_layout.addWidget(add_sub_btn)
        remove_sub_btn = QPushButton("Remove Sub-Project")
        remove_sub_btn.clicked.connect(self.remove_sub_project)
        sub_project_input_layout.addWidget(remove_sub_btn)
        project_layout.addLayout(sub_project_input_layout)

        scroll_layout.addWidget(project_group)

        # Task Types Section
        task_type_group = QGroupBox("Task Types")
        task_type_layout = QVBoxLayout(task_type_group)

        self.task_type_list = QListWidget()
        for task_type in self.config["task_types"]:
            self.task_type_list.addItem(task_type)
        task_type_layout.addWidget(self.task_type_list)

        task_type_input_layout = QHBoxLayout()
        task_type_input_layout.addWidget(QLabel("New Task Type:"))
        self.new_task_type_entry = QLineEdit()
        task_type_input_layout.addWidget(self.new_task_type_entry)
        add_task_type_btn = QPushButton("Add Task Type")
        add_task_type_btn.clicked.connect(self.add_task_type)
        task_type_input_layout.addWidget(add_task_type_btn)
        remove_task_type_btn = QPushButton("Remove Selected")
        remove_task_type_btn.clicked.connect(self.remove_task_type)
        task_type_input_layout.addWidget(remove_task_type_btn)
        task_type_layout.addLayout(task_type_input_layout)

        scroll_layout.addWidget(task_type_group)

        # Labels Section
        label_group = QGroupBox("Labels")
        label_layout = QVBoxLayout(label_group)

        self.label_list = QListWidget()
        for label in self.config["labels"]:
            self.label_list.addItem(f"{label} ({self.config['labels'][label]})")
        label_layout.addWidget(self.label_list)

        label_input_layout = QHBoxLayout()
        label_input_layout.addWidget(QLabel("New Label:"))
        self.new_label_entry = QLineEdit()
        label_input_layout.addWidget(self.new_label_entry)
        label_input_layout.addWidget(QLabel("Color (Hex):"))
        self.label_color_entry = QLineEdit("#000000")
        label_input_layout.addWidget(self.label_color_entry)
        add_label_btn = QPushButton("Add Label")
        add_label_btn.clicked.connect(self.add_label)
        label_input_layout.addWidget(add_label_btn)
        remove_label_btn = QPushButton("Remove Selected")
        remove_label_btn.clicked.connect(self.remove_label)
        label_input_layout.addWidget(remove_label_btn)
        label_layout.addLayout(label_input_layout)

        scroll_layout.addWidget(label_group)

        # Signature Details Section
        signature_group = QGroupBox("Signature Details")
        signature_layout = QFormLayout(signature_group)
        signature_layout.setLabelAlignment(Qt.AlignRight)

        self.name_entry = QLineEdit(self.config["signature"]["name"])
        signature_layout.addRow("Name:", self.name_entry)
        self.mobile_entry = QLineEdit(self.config["signature"]["mobile"])
        signature_layout.addRow("Mobile:", self.mobile_entry)
        self.email_entry = QLineEdit(self.config["signature"]["email"])
        signature_layout.addRow("Email:", self.email_entry)

        scroll_layout.addWidget(signature_group)

        # Email Recipients Section
        email_group = QGroupBox("Email Recipients")
        email_layout = QFormLayout(email_group)
        email_layout.setLabelAlignment(Qt.AlignRight)

        self.to_entry = QLineEdit(self.config["email"]["to"])
        email_layout.addRow("To:", self.to_entry)
        self.cc_entry = QLineEdit(self.config["email"]["cc"])
        email_layout.addRow("CC:", self.cc_entry)

        scroll_layout.addWidget(email_group)

        # Notification Time Section
        notification_group = QGroupBox("Notification Settings")
        notification_layout = QFormLayout(notification_group)
        notification_layout.setLabelAlignment(Qt.AlignRight)

        self.notification_time_entry = QLineEdit(self.config.get("notification_time", "18:00"))
        notification_layout.addRow("Notification Time (HH:MM, 24-hour format):", self.notification_time_entry)

        scroll_layout.addWidget(notification_group)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel)
        btn_layout.addWidget(cancel_btn)
        scroll_layout.addLayout(btn_layout)

    def update_sub_project_list(self, current, previous):
        self.sub_project_list.clear()
        if not current:
            return
        main_project = current.text()
        sub_projects = self.config["main_projects"].get(main_project, [])
        for sub_project in sub_projects:
            self.sub_project_list.addItem(sub_project)

    def browse_config_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Config File", "config.json", "JSON Files (*.json)")
        if path:
            self.config_file_entry.setText(path)

    def browse_tasks_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Tasks File", "tasks.json", "JSON Files (*.json)")
        if path:
            self.tasks_file_entry.setText(path)

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)")
        if path:
            self.logo_entry.setText(path)

    def add_main_project(self):
        main_project = self.new_main_project_entry.text().strip()
        if not main_project:
            QMessageBox.warning(self, "Input Error", "Main project name is required.")
            return
        if main_project in self.config["main_projects"]:
            QMessageBox.warning(self, "Duplicate", "Main project already exists.")
            return
        self.config["main_projects"][main_project] = []
        self.main_project_list.addItem(main_project)
        self.new_main_project_entry.clear()

    def remove_main_project(self):
        current = self.main_project_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Selection Error", "Please select a main project to remove.")
            return
        main_project = current.text()
        del self.config["main_projects"][main_project]
        row = self.main_project_list.row(current)
        self.main_project_list.takeItem(row)
        self.sub_project_list.clear()

    def add_sub_project(self):
        current = self.main_project_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Selection Error", "Please select a main project to add a sub-project to.")
            return
        main_project = current.text()
        sub_project = self.new_sub_project_entry.text().strip()
        if not sub_project:
            QMessageBox.warning(self, "Input Error", "Sub-project name is required.")
            return
        if sub_project in self.config["main_projects"][main_project]:
            QMessageBox.warning(self, "Duplicate", "Sub-project already exists in this main project.")
            return
        self.config["main_projects"][main_project].append(sub_project)
        self.sub_project_list.addItem(sub_project)
        self.new_sub_project_entry.clear()

    def remove_sub_project(self):
        main_item = self.main_project_list.currentItem()
        sub_item = self.sub_project_list.currentItem()
        if not main_item:
            QMessageBox.warning(self, "Selection Error", "Please select a main project.")
            return
        if not sub_item:
            QMessageBox.warning(self, "Selection Error", "Please select a sub-project to remove.")
            return
        main_project = main_item.text()
        sub_project = sub_item.text()
        self.config["main_projects"][main_project].remove(sub_project)
        row = self.sub_project_list.row(sub_item)
        self.sub_project_list.takeItem(row)

    def add_task_type(self):
        task_type = self.new_task_type_entry.text().strip()
        if not task_type:
            QMessageBox.warning(self, "Input Error", "Task type name is required.")
            return
        if task_type.lower() == "normal":
            QMessageBox.warning(self, "Input Error", "'Normal' is a reserved task type and cannot be added.")
            return
        if task_type in self.config["task_types"]:
            QMessageBox.warning(self, "Duplicate", "Task type already exists.")
            return
        self.config["task_types"].append(task_type)
        self.task_type_list.addItem(task_type)
        self.new_task_type_entry.clear()

    def remove_task_type(self):
        current = self.task_type_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Selection Error", "Please select a task type to remove.")
            return
        task_type = current.text()
        self.config["task_types"].remove(task_type)
        row = self.task_type_list.row(current)
        self.task_type_list.takeItem(row)

    def add_label(self):
        label = self.new_label_entry.text().strip()
        color = self.label_color_entry.text().strip()
        if not label:
            QMessageBox.warning(self, "Input Error", "Label name is required.")
            return
        if not color.startswith("#") or len(color) != 7:
            QMessageBox.warning(self, "Input Error", "Color must be a valid hex code (e.g., #FF0000).")
            return
        if label in self.config["labels"]:
            QMessageBox.warning(self, "Duplicate", "Label already exists.")
            return
        self.config["labels"][label] = color
        self.label_list.addItem(f"{label} ({color})")
        self.new_label_entry.clear()
        self.label_color_entry.setText("#000000")

    def remove_label(self):
        current = self.label_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Selection Error", "Please select a label to remove.")
            return
        label_info = current.text()
        label = label_info.split(" (")[0]
        del self.config["labels"][label]
        row = self.label_list.row(current)
        self.label_list.takeItem(row)

    def save(self):
        self.config["config_file_path"] = self.config_file_entry.text().strip()
        self.config["tasks_file_path"] = self.tasks_file_entry.text().strip()
        self.config["logo_path"] = self.logo_entry.text().strip()
        self.config["signature"]["name"] = self.name_entry.text().strip()
        self.config["signature"]["mobile"] = self.mobile_entry.text().strip()
        self.config["signature"]["email"] = self.email_entry.text().strip()
        self.config["email"]["to"] = self.to_entry.text().strip()
        self.config["email"]["cc"] = self.cc_entry.text().strip()
        self.config["notification_time"] = self.notification_time_entry.text().strip()

        # Validate notification time format (HH:MM, 24-hour)
        try:
            notification_time = self.config["notification_time"]
            if not notification_time:
                raise ValueError("Notification time is required.")
            hours, minutes = map(int, notification_time.split(":"))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError("Invalid time format.")
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Notification time must be in HH:MM (24-hour) format (e.g., 18:00).\nError: {e}")
            return

        if not self.config["logo_path"]:
            QMessageBox.warning(self, "Input Error", "Logo path is required.")
            return
        if not self.config["signature"]["name"]:
            QMessageBox.warning(self, "Input Error", "Signature name is required.")
            return
        if not self.config["signature"]["email"]:
            QMessageBox.warning(self, "Input Error", "Signature email is required.")
            return
        if not self.config["email"]["to"]:
            QMessageBox.warning(self, "Input Error", "To email addresses are required.")
            return

        try:
            new_config_path = self.config["config_file_path"]
            save_config(self.config, new_config_path)
            self.on_save_callback(self.config, new_config_path)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.parent.accept()  # Close the dialog
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save settings: {e}")

    def cancel(self):
        if not any(self.config.get(key) for key in ["logo_path", "main_projects", "signature", "email"] if key != "config_file_path" and key != "tasks_file_path"):
            QMessageBox.warning(self, "Configuration Required", "You must save the configuration to proceed.")
            return
        self.parent.reject()  # Close the dialog

# Main Application Class
class EODTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EOD Tool")
        self.config, self.config_path = load_config(DEFAULT_PERSISTENT_CONFIG_PATH, DEFAULT_PERSISTENT_CONFIG_PATH)
        self.tasks = []
        self.editing_index = None
        self.html_copied = False
        self.theme = "dark"  # Set default theme to dark

        # Initialize system tray for notifications
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())  # Use the app's icon
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show Window")
        show_action.triggered.connect(self.show)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.setup_ui()
        self.load_tasks()

        # Setup timer to check for notification time (check every 10 seconds)
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_notification_time)
        self.notification_timer.start(10000)  # Check every 10 seconds (10000 ms)

    def closeEvent(self, event: QCloseEvent):
        # Minimize to system tray instead of closing
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "EOD Tool",
            "Application minimized to tray.",
            QSystemTrayIcon.Information,
            2000  # Display for 2 seconds
        )

    def setup_ui(self):
        # Central Widget with a QTabWidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create QTabWidget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Main UI Widget (EOD Task Tracker Tab)
        self.main_widget = QWidget()
        main_tab_layout = QVBoxLayout(self.main_widget)
        main_tab_layout.setContentsMargins(20, 20, 20, 20)
        main_tab_layout.setSpacing(15)

        # Top Bar (Theme Toggle and Settings)
        top_bar = QHBoxLayout()
        main_tab_layout.addLayout(top_bar)
        top_bar.addStretch()
        self.theme_button = QPushButton("☀")  # Start with dark theme, show light theme toggle button
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_button)

        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.clicked.connect(self.show_settings_dialog)
        top_bar.addWidget(self.settings_button)

        # Scroll Area for Main Content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.sub_widget = QWidget()
        scroll_layout = QVBoxLayout(self.sub_widget)
        scroll_area.setWidget(self.sub_widget)
        main_tab_layout.addWidget(scroll_area)

        # Project Selection Section
        project_frame = QFrame()
        project_frame.setObjectName("sectionFrame")
        project_layout = QFormLayout(project_frame)
        scroll_layout.addWidget(project_frame)

        scroll_layout.setContentsMargins(15, 10, 15, 5)
        project_layout.setLabelAlignment(Qt.AlignRight)

        project_label = QLabel("Project Selection")
        project_label.setObjectName("sectionLabel")
        scroll_layout.addWidget(project_label)

        main_label_label = QLabel("Main Project: <span style='color: red;'>*</span>")
        main_label_label.setTextFormat(Qt.TextFormat.RichText)
        self.main_project = QComboBox()
        self.main_project.addItems(self.config["main_projects"].keys())
        project_layout.addRow(main_label_label, self.main_project)

        sub_label = QLabel("Sub-Project: <span style='color: red;'>*</span>")
        sub_label.setTextFormat(Qt.TextFormat.RichText)
        self.sub_project = QComboBox()
        project_layout.addRow(sub_label, self.sub_project)

        if self.config["main_projects"]:
            self.main_project.setCurrentIndex(0)
            self.update_sub_project_combo()

        # Task Details Section
        task_frame = QFrame()
        task_frame.setObjectName("sectionFrame")
        task_layout = QFormLayout(task_frame)
        scroll_layout.addWidget(task_frame)

        task_label = QLabel("Task Details")
        task_label.setObjectName("sectionLabel")
        scroll_layout.addWidget(task_label)

        task_layout.setContentsMargins(15, 10, 15, 5)

        task_desc_label = QLabel("Task Description: <span style='color: red;'>*</span>")
        task_desc_label.setTextFormat(Qt.TextFormat.RichText)
        self.task_entry = QLineEdit()
        task_layout.addRow(task_desc_label, self.task_entry)

        self.label_combo = QComboBox()
        self.label_combo.addItem("")
        self.label_combo.addItems(self.config["labels"].keys())
        task_layout.addRow("Select Label:", self.label_combo)

        self.comment_entry = QLineEdit()
        task_layout.addRow("Comments:", self.comment_entry)

        # Status Selection
        status_label = QLabel("Select Status: <span style='color: red;'>*</span>")
        status_label.setTextFormat(Qt.TextFormat.RichText)
        status_layout = QHBoxLayout()
        self.status_group = {}
        for status in STATUS_LABELS:
            radio_button = QRadioButton(status)
            radio_button.setObjectName(f"status-{status.replace(' ', '\\ ')}")
            if status == "Completed":
                radio_button.setChecked(True)
            status_layout.addWidget(radio_button)
            self.status_group[status] = radio_button
        task_layout.addRow(status_label, status_layout)

        task_type_label = QLabel("Task Type: <span style='color: red;'>*</span>")
        task_type_label.setTextFormat(Qt.TextFormat.RichText)
        self.task_type = QComboBox()
        self.task_type.addItem("")
        self.task_type.addItems(self.config["task_types"])
        task_layout.addRow(task_type_label, self.task_type)

        # Add Task Button (below Task Type)
        self.add_task_btn = QPushButton("➕ Add Task")
        self.add_task_btn.setEnabled(False)  # Disabled by default
        self.add_task_btn.clicked.connect(self.add_task)
        task_layout.addRow("", self.add_task_btn)

        # Task List Section
        list_frame = QFrame()
        list_frame.setObjectName("sectionFrame")
        list_layout = QVBoxLayout(list_frame)
        scroll_layout.addWidget(list_frame)

        list_label = QLabel("Task List")
        list_label.setObjectName("sectionLabel")
        scroll_layout.addWidget(list_label)

        list_layout.setContentsMargins(15, 10, 15, 5)

        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        list_layout.addWidget(self.task_list)

        list_buttons_layout = QHBoxLayout()
        list_layout.addLayout(list_buttons_layout)

        self.move_up_button = QPushButton("⬆ Move Up")
        self.move_up_button.clicked.connect(self.move_task_up)
        list_buttons_layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("⬇ Move Down")
        self.move_down_button.clicked.connect(self.move_task_down)
        list_buttons_layout.addWidget(self.move_down_button)

        self.edit_task_button = QPushButton("✏ Edit Task")
        self.edit_task_button.clicked.connect(self.edit_task)
        list_buttons_layout.addWidget(self.edit_task_button)

        self.delete_task_button = QPushButton("🗑 Delete")
        self.delete_task_button.clicked.connect(self.delete_task)
        list_buttons_layout.addWidget(self.delete_task_button)

        self.clear_all_button = QPushButton("🗑 Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_tasks)
        list_buttons_layout.addWidget(self.clear_all_button)

        self.save_tasks_button = QPushButton("💾 Save Tasks")
        self.save_tasks_button.clicked.connect(self.save_tasks)
        list_buttons_layout.addWidget(self.save_tasks_button)

        self.load_tasks_button = QPushButton("📂 Load Tasks")
        self.load_tasks_button.clicked.connect(self.load_tasks)
        list_buttons_layout.addWidget(self.load_tasks_button)

        # Export Options Section
        export_frame = QFrame()
        export_frame.setObjectName("sectionFrame")
        export_layout = QVBoxLayout(export_frame)
        scroll_layout.addWidget(export_frame)

        export_label = QLabel("Export Options")
        export_label.setObjectName("sectionLabel")
        scroll_layout.addWidget(export_label)

        export_layout.setContentsMargins(15, 10, 15, 5)

        export_buttons_layout = QHBoxLayout()
        export_layout.addLayout(export_buttons_layout)

        self.export_html_button = QPushButton("Export as HTML")
        self.export_html_button.clicked.connect(self.export_html)
        export_buttons_layout.addWidget(self.export_html_button)

        self.copy_button = QPushButton("Copy HTML Body")
        self.copy_button.clicked.connect(self.copy_html_body)
        export_buttons_layout.addWidget(self.copy_button)

        self.export_text_button = QPushButton("Export as Text")
        self.export_text_button.clicked.connect(self.export_text)
        export_buttons_layout.addWidget(self.export_text_button)

        self.preview_button = QPushButton("Preview EOD Email")
        self.preview_button.clicked.connect(self.preview_email)
        export_buttons_layout.addWidget(self.preview_button)

        self.open_outlook_button = QPushButton("Open in Email Client")
        self.open_outlook_button.clicked.connect(self.open_outlook_email)
        self.open_outlook_button.setEnabled(True)  # Enabled since we now set HTML body directly
        export_buttons_layout.addWidget(self.open_outlook_button)

        # Connect signals to validate mandatory fields after all widgets are initialized
        self.main_project.currentTextChanged.connect(self.update_sub_project_combo)
        self.sub_project.currentTextChanged.connect(self.validate_mandatory_fields)
        self.task_entry.textChanged.connect(self.validate_mandatory_fields)
        self.task_type.currentTextChanged.connect(self.validate_mandatory_fields)

        # Initial validation after setup
        self.validate_mandatory_fields()

        # Add the main widget as a tab
        self.tab_widget.addTab(self.main_widget, "EOD Task Tracker")

        # Add the Test Report Generator tab
        self.test_report_widget = TestReportGeneratorWidget()
        self.tab_widget.addTab(self.test_report_widget, "Test Report Generator")

        # Settings Dialog
        self.settings_dialog = QDialog(self)
        self.settings_dialog.setWindowTitle("Settings")
        dialog_layout = QVBoxLayout(self.settings_dialog)
        self.settings_widget = SettingsWidget(self.settings_dialog, self.config, self.config_path, self.update_config)
        dialog_layout.addWidget(self.settings_widget)
        self.settings_dialog.resize(800, 600)

        # Apply Theme
        self.apply_theme()

    def show_settings_dialog(self):
        self.settings_dialog.exec()

    def check_notification_time(self):
        # Get current time and day
        current_time = QDateTime.currentDateTime().time().toString("HH:mm")
        current_day = datetime.datetime.today().weekday()  # 0 = Monday, 5 = Saturday, 6 = Sunday

        # Skip notifications on Saturday (5) and Sunday (6)
        if current_day in (5, 6):
            logging.debug(f"Skipping notification - Today is {'Saturday' if current_day == 5 else 'Sunday'}")
            return

        # Get configured notification time
        notification_time = self.config.get("notification_time", "18:00")

        # Log the comparison for debugging
        logging.debug(f"Current time: {current_time}, Notification time: {notification_time}")

        # Compare current time with configured time
        if current_time == notification_time:
            logging.info("Notification triggered.")
            # Show system tray notification
            self.tray_icon.showMessage(
                "EOD Task Tracker",
                "It's time to send your daily status email!",
                QSystemTrayIcon.Information,
                5000  # Display for 5 seconds
            )
        else:
            logging.debug("Time does not match - no notification sent.")

    def apply_theme(self):
        if self.theme == "dark":
            stylesheet = """
                QMainWindow, QWidget { background-color: #212121; color: #E0E0E0; }
                QTabWidget::pane {
                    border: 1px solid #333333;
                    background-color: #212121;
                }
                QTabBar::tab {
                    background-color: #272727;
                    color: #E0E0E0;
                    padding: 8px 20px;
                    border: 1px solid #333333;
                    border-bottom: none;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #1976D2;
                    color: white;
                }
                QGroupBox, QFrame#sectionFrame {
                    background-color: #272727;
                    border: 1px solid #333333;
                    border-radius: 10px;
                    margin-top: 10px;
                }
                QGroupBox::title, QLabel#sectionLabel {
                    color: #E0E0E0;
                    font-size: 16px;
                    font-weight: bold;
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 5px;
                }
                QLabel { color: #B0BEC5; font-family: Roboto; font-size: 14px; }
                QLineEdit, QComboBox {
                    background-color: #333333;
                    color: #E0E0E0;
                    border: 1px solid #424242;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                    font-family: Roboto;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #1565C0; }
                QPushButton:disabled { background-color: #424242; color: #666666; }
                QRadioButton { color: #B0BEC5; font-family: Roboto; font-size: 14px; }
                QRadioButton#status-Completed { color: #5e8f59; }
                QRadioButton#status-In\\ Progress { color: #c06530; }
                QRadioButton#status-To\\ Be\\ Done { color: #029de6; }
                QRadioButton#status-Blocked { color: #ff0000; }
                QListWidget {
                    background-color: #272727;
                    color: #E0E0E0;
                    border: 1px solid #333333;
                    border-radius: 5px;
                    padding: 5px;
                    font-family: Roboto;
                    font-size: 14px;
                }
                QListWidget::item:selected { background-color: #1976D2; color: white; }
                QListWidget::item:alternate { background-color: #303030; }
            """
        else:
            stylesheet = """
                QMainWindow, QWidget { background-color: #FFFFFF; color: #212121; }
                QTabWidget::pane {
                    border: 1px solid #000000;
                    background-color: #FFFFFF;
                }
                QTabBar::tab {
                    background-color: #F0F0F0;
                    color: #212121;
                    padding: 8px 20px;
                    border: 1px solid #000000;
                    border-bottom: none;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #1976D2;
                    color: white;
                }
                QGroupBox, QFrame#sectionFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #000000;
                    border-radius: 5px;
                    margin-top: 15px;
                }
                QGroupBox::title, QLabel#sectionLabel {
                    color: #212121;
                    background-color: transparent;
                    font-size: 14px;
                    font-weight: bold;
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                    margin-left: 5px;
                }
                QLabel { color: #212121; font-family: Calibri, Arial, sans-serif; font-size: 12px; }
                QLineEdit, QComboBox {
                    background-color: white;
                    border: 1px solid #000000;
                    border-radius: 4px;
                    padding: 5px;
                    color: #212121;
                    font-family: Calibri, Arial, sans-serif;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    font-family: Calibri, Arial, sans-serif;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #1565C0; }
                QPushButton:disabled { background-color: #E0E0E0; color: #B0BEC5; }
                QRadioButton { color: #616161; font-family: Calibri, Arial, sans-serif; font-size: 12px; }
                QRadioButton#status-Completed { color: #5e8f59; }
                QRadioButton#status-In\\ Progress { color: #c06530; }
                QRadioButton#status-To\\ Be\\ Done { color: #029de6; }
                QRadioButton#status-Blocked { color: #ff0000; }
                QHBoxLayout { border: 1px solid #000000; }
                QListWidget {
                    background-color: white;
                    color: #212121;
                    border: 1px solid #000000;
                    border-radius: 4px;
                    padding: 5px;
                    font-family: Calibri, Arial, sans-serif;
                    font-size: 12px;
                }
                QListWidget::item:selected { background-color: #1976D2; color: white; }
                QListWidget::item:alternate { background-color: #F9F9F9; }
            """
        self.setStyleSheet(stylesheet)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.theme_button.setText("☀" if self.theme == "dark" else "🌙")
        self.apply_theme()

    def update_config(self, new_config, new_config_path):
        self.config = new_config
        self.config_path = new_config_path
        self.main_project.clear()
        self.main_project.addItems(self.config["main_projects"].keys())
        self.label_combo.clear()
        self.label_combo.addItem("")
        self.label_combo.addItems(self.config["labels"].keys())
        self.task_type.clear()
        self.task_type.addItem("")
        self.task_type.addItems(self.config["task_types"])
        if self.config["main_projects"]:
            self.main_project.setCurrentIndex(0)
            self.update_sub_project_combo()
        else:
            self.main_project.setCurrentIndex(-1)
            self.sub_project.clear()
        self.validate_mandatory_fields()

    def update_sub_project_combo(self):
        main_project = self.main_project.currentText()
        sub_projects = self.config["main_projects"].get(main_project, [])
        self.sub_project.clear()
        self.sub_project.addItems(sub_projects)
        if sub_projects:
            self.sub_project.setCurrentIndex(0)

    def validate_mandatory_fields(self):
        main_project = self.main_project.currentText().strip()
        sub_project = self.sub_project.currentText().strip()
        task = self.task_entry.text().strip()
        task_type = self.task_type.currentText().strip()

        # Ensure all_filled is a boolean by explicitly checking for non-empty strings
        all_filled = bool(main_project and sub_project and task and task_type)
        self.add_task_btn.setEnabled(all_filled)

    def update_button_states(self):
        state = not self.tasks
        self.move_up_button.setDisabled(state)
        self.move_down_button.setDisabled(state)
        self.edit_task_button.setDisabled(state)
        self.delete_task_button.setDisabled(state)
        self.clear_all_button.setDisabled(state)
        self.save_tasks_button.setDisabled(state)
        self.export_html_button.setEnabled(not state)
        self.copy_button.setEnabled(not state)
        self.export_text_button.setEnabled(not state)

    def add_task(self):
        main_project = self.main_project.currentText()
        sub_project = self.sub_project.currentText()
        task = self.task_entry.text().strip()
        status = next(status for status, radio in self.status_group.items() if radio.isChecked())
        task_type = self.task_type.currentText()
        label = self.label_combo.currentText()
        comment = self.comment_entry.text().strip()

        # Since button is only enabled when mandatory fields are filled, no need for validation here
        # However, we still need to check label-comment dependency
        if label and not comment:
            QMessageBox.warning(self, "Input Error", "Comment is required when a label is selected.")
            return

        task_type = "Normal" if not task_type else task_type
        task_data = {
            "main_project": main_project,
            "sub_project": sub_project,
            "task": task,
            "status": status,
            "task_type": task_type
        }
        if label:
            task_data["label"] = label
        if comment:
            task_data["comment"] = comment

        if self.editing_index is not None:
            self.tasks[self.editing_index] = task_data
            self.editing_index = None
            self.add_task_btn.setText("➕ Add Task")
        else:
            self.tasks.append(task_data)

        self.update_task_list()
        self.task_entry.clear()
        self.label_combo.setCurrentIndex(0)
        self.comment_entry.clear()
        self.task_type.setCurrentIndex(0)
        self.save_tasks()
        self.update_button_states()
        self.validate_mandatory_fields()  # Update button state after clearing fields

    def edit_task(self):
        if self.task_list.currentRow() < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a task to edit.")
            return
        self.editing_index = self.task_list.currentRow()
        task = self.tasks[self.editing_index]
        self.main_project.setCurrentText(task["main_project"])
        self.update_sub_project_combo()
        self.sub_project.setCurrentText(task["sub_project"])
        self.task_entry.setText(task["task"])
        self.status_group[task["status"]].setChecked(True)
        self.task_type.setCurrentText("" if task["task_type"] == "Normal" else task["task_type"])
        self.label_combo.setCurrentText(task.get("label", ""))
        self.comment_entry.setText(task.get("comment", ""))
        self.add_task_btn.setText("💾 Save Edit")
        self.validate_mandatory_fields()  # Update button state after loading task data

    def delete_task(self):
        if self.task_list.currentRow() >= 0:
            del self.tasks[self.task_list.currentRow()]
            self.update_task_list()
            self.save_tasks()
            self.update_button_states()

    def clear_all_tasks(self):
        if QMessageBox.question(self, "Confirm", "Clear all tasks?") == QMessageBox.Yes:
            self.tasks.clear()
            self.update_task_list()
            self.save_tasks()
            self.update_button_states()

    def move_task_up(self):
        idx = self.task_list.currentRow()
        if idx > 0:
            self.tasks[idx - 1], self.tasks[idx] = self.tasks[idx], self.tasks[idx - 1]
            self.update_task_list()
            self.task_list.setCurrentRow(idx - 1)
            self.save_tasks()

    def move_task_down(self):
        idx = self.task_list.currentRow()
        if idx < len(self.tasks) - 1:
            self.tasks[idx + 1], self.tasks[idx] = self.tasks[idx + 1], self.tasks[idx]
            self.update_task_list()
            self.task_list.setCurrentRow(idx + 1)
            self.save_tasks()

    def update_task_list(self):
        self.task_list.clear()
        for t in self.tasks:
            label = t.get("label", "")
            label_display = f" [{label}]" if label else ""
            task_type_display = f" ({t['task_type']})" if t['task_type'] != "Normal" else ""
            self.task_list.addItem(f"[{t['main_project']}][{t['sub_project']}] {t['status']}{task_type_display}{label_display} - {t['task']}")
        self.update_button_states()

    def save_tasks(self):
        try:
            with open(self.config["tasks_file_path"], 'w') as f:
                json.dump(self.tasks, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save tasks:\n{e}")

    def load_tasks(self):
        if os.path.exists(self.config["tasks_file_path"]):
            try:
                with open(self.config["tasks_file_path"], 'r') as f:
                    self.tasks = json.load(f)
                for task in self.tasks:
                    if task["status"] == "Pending":
                        task["status"] = "In Progress"
                    if "task_type" not in task:
                        task["task_type"] = "Normal"
                self.update_task_list()
                self.save_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load tasks:\n{e}")
                self.tasks = []
                self.update_task_list()
        else:
            QMessageBox.information(self, "No Tasks", "No tasks file found. Starting with an empty task list.")
            self.tasks = []
            self.update_task_list()
        self.update_button_states()

    def generate_email_body(self):
        today = date.today().strftime("%d/%m/%Y")
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Daily Status Update - {today}</title>
</head>
<body style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000000; margin: 0; padding: 0;">
    <p style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000000; margin-bottom: 5px;">Hi Hari,</p>
    <p style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000000; margin-top: 0;">Please find the below status update for today ({today}):</p>
    <table style="border-collapse: collapse; width: 100%; font-family: Calibri, Arial, sans-serif; font-size: 11pt;">
        <thead>
            <tr style="background-color: #D3D3D3;">
                <th style="border: 1px solid #000000; padding: 8px;">Main Project</th>
                <th style="border: 1px solid #000000; padding: 8px;">Sub-Project</th>
                <th style="border: 1px solid #000000; padding: 8px;">Task Description</th>
                <th style="border: 1px solid #000000; padding: 8px;">Status</th>
                <th style="border: 1px solid #000000; padding: 8px;">Task Type</th>
                <th style="border: 1px solid #000000; padding: 8px;">Label</th>
                <th style="border: 1px solid #000000; padding: 8px;">Comment</th>
            </tr>
        </thead>
        <tbody>
"""
        for task in self.tasks:
            label = task.get("label", "")
            label_color = self.config["labels"].get(label, "#000000") if label else "#000000"
            comment = task.get("comment", "")
            status_color = STATUS_COLORS.get(task["status"], "#000000")
            task_type = task["task_type"]
            html_content += f"""
            <tr>
                <td style="border: 1px solid #000000; padding: 8px;">{task['main_project']}</td>
                <td style="border: 1px solid #000000; padding: 8px;">{task['sub_project']}</td>
                <td style="border: 1px solid #000000; padding: 8px;">{task['task']}</td>
                <td style="border: 1px solid #000000; padding: 8px; color: {status_color};">{task['status']}</td>
                <td style="border: 1px solid #000000; padding: 8px;">{task_type}</td>
                <td style="border: 1px solid #000000; padding: 8px; color: {label_color};">{label}</td>
                <td style="border: 1px solid #000000; padding: 8px;">{comment}</td>
            </tr>
"""
        html_content += """
        </tbody>
    </table>
    <p style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000000; margin-top: 10px;">Thanks,</p>
</body>
</html>
"""
        return html_content

    def generate_signature(self, preview=True):
        signature = self.config["signature"]
        logo_base64 = encode_image_base64(self.config["logo_path"])
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Logo" style="width: 100px; height: auto; margin-right: 10px; vertical-align: middle;">' if logo_base64 else ''
        signature_html = f"""
    <table style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000000; margin-top: 10px;">
        <tr>
            <td style="vertical-align: middle;">{logo_html}</td>
            <td style="vertical-align: middle;">
                <p style="margin: 0; font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000000;">
                    {signature["name"]}<br>
                    {signature["mobile"]}<br>
                    <a href="mailto:{signature["email"]}" style="color: #0000FF; text-decoration: none;">{signature["email"]}</a>
                </p>
            </td>
        </tr>
    </table>
"""
        if preview:
            signature_html = f"""
    <p style="font-family: Calibri, Arial, sans-serif; font-size: 11pt; color: #000000; margin-top: 10px;">Thanks,</p>
    {signature_html}
"""
        return signature_html

    def generate_copy_html(self):
        html_body = self.generate_email_body()
        signature = self.generate_signature(preview=False)
        full_html = html_body.rsplit("</body>", 1)[0] + signature + "</body></html>"
        return full_html

    def export_html(self):
        if not self.tasks:
            QMessageBox.warning(self, "No Tasks", "No tasks to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export HTML", f"Daily_Status_{date.today().strftime('%d%m%Y')}.html", "HTML Files (*.html)")
        if path:
            try:
                html_content = self.generate_copy_html()
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                QMessageBox.information(self, "Success", "HTML exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export HTML:\n{e}")

    def copy_html_body(self):
        if not self.tasks:
            QMessageBox.warning(self, "No Tasks", "No tasks to copy.")
            return
        try:
            html_content = self.generate_copy_html()
            set_clipboard_html(html_content)
            self.html_copied = True
            self.open_outlook_button.setEnabled(True)
            QMessageBox.information(self, "Success", "HTML body copied to clipboard!")
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Failed to copy HTML body:\n{e}")

    def export_text(self):
        if not self.tasks:
            QMessageBox.warning(self, "No Tasks", "No tasks to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Text", f"Daily_Status_{date.today().strftime('%d%m%Y')}.txt", "Text Files (*.txt)")
        if path:
            try:
                text_content = f"Daily Status Update - {date.today().strftime('%d/%m/%Y')}\n\n"
                text_content += "Hi Hari,\n\n"
                text_content += f"Please find the below status update for today ({date.today().strftime('%d/%m/%Y')}):\n\n"
                for task in self.tasks:
                    label = task.get("label", "")
                    label_display = f" [{label}]" if label else ""
                    comment = task.get("comment", "")
                    comment_display = f" - {comment}" if comment else ""
                    text_content += f"[{task['main_project']}][{task['sub_project']}] {task['task']} - {task['status']} ({task['task_type']}){label_display}{comment_display}\n"
                text_content += "\nThanks,\n"
                signature = self.config["signature"]
                text_content += f"{signature['name']}\n{signature['mobile']}\n{signature['email']}\n"
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                QMessageBox.information(self, "Success", "Text exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export text:\n{e}")

    def preview_email(self):
        if not self.tasks:
            QMessageBox.warning(self, "No Tasks", "No tasks to preview.")
            return
        html_content = self.generate_copy_html()
        preview_email_html(html_content)

    def open_outlook_email(self):
        try:
            # Generate the HTML body
            html_body = self.generate_copy_html()
            signature = self.generate_signature(preview=False)
            full_html = html_body.rsplit("</body>", 1)[0] + signature + "</body></html>"

            # Use win32com to interact with Outlook
            import win32com.client

            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)  # 0 = olMailItem

            today = date.today().strftime("%d/%m/%Y")
            subject = f"Daily Status {today}"
            to_emails = self.config["email"]["to"]
            cc_emails = self.config["email"]["cc"]

            mail.Subject = subject
            mail.To = to_emails
            mail.CC = cc_emails
            mail.HTMLBody = full_html

            # Display the email to the user (does not send it automatically)
            mail.Display()

            QMessageBox.information(self, "Success", "Email opened in Outlook with the HTML body inserted!")
        except Exception as e:
            QMessageBox.critical(self, "Email Error", f"Failed to open email in Outlook:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EODTool()
    window.showMaximized()  # Open the application maximized
    sys.exit(app.exec())