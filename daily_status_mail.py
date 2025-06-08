import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QDialog, QScrollArea, QGroupBox, 
                               QFormLayout, QLineEdit, QPushButton, QListWidget, QHBoxLayout, QLabel, QFileDialog, 
                               QMessageBox, QTabWidget, QComboBox)
from PySide6.QtCore import Qt
from test_report_generator import TestReportGeneratorWidget
from daily_status_ui import EODUI
from daily_status_logic import EODLogic

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
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # File Locations Section
        file_group = QGroupBox("File Locations")
        file_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        file_layout = QFormLayout(file_group)
        file_layout.setLabelAlignment(Qt.AlignRight)
        file_layout.setSpacing(15)

        self.config_file_entry = QLineEdit(self.config.get("config_file_path", ""))
        self.config_file_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        config_browse_btn = QPushButton("Browse")
        config_browse_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        config_browse_btn.clicked.connect(self.browse_config_file)
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.config_file_entry)
        config_layout.addWidget(config_browse_btn)
        file_layout.addRow("Config File Path:", config_layout)

        self.tasks_file_entry = QLineEdit(self.config.get("tasks_file_path", ""))
        self.tasks_file_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        tasks_browse_btn = QPushButton("Browse")
        tasks_browse_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        tasks_browse_btn.clicked.connect(self.browse_tasks_file)
        tasks_layout = QHBoxLayout()
        tasks_layout.addWidget(self.tasks_file_entry)
        tasks_layout.addWidget(tasks_browse_btn)
        file_layout.addRow("Tasks File Path:", tasks_layout)

        scroll_layout.addWidget(file_group)

        # Logo Path Section
        logo_group = QGroupBox("Logo Path")
        logo_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        logo_layout = QFormLayout(logo_group)
        logo_layout.setLabelAlignment(Qt.AlignRight)
        logo_layout.setSpacing(15)

        self.logo_entry = QLineEdit(self.config["logo_path"])
        self.logo_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        logo_browse_btn = QPushButton("Browse")
        logo_browse_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        logo_browse_btn.clicked.connect(self.browse_logo)
        logo_inner_layout = QHBoxLayout()
        logo_inner_layout.addWidget(self.logo_entry)
        logo_inner_layout.addWidget(logo_browse_btn)
        logo_layout.addRow("Logo File:", logo_inner_layout)

        scroll_layout.addWidget(logo_group)

        # Theme Selection Section
        theme_group = QGroupBox("Theme Selection")
        theme_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        theme_layout = QFormLayout(theme_group)
        theme_layout.setLabelAlignment(Qt.AlignRight)
        theme_layout.setSpacing(15)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Default", "Dark Blue", "Dark Purple", "Dark Green", "Light Gray"])
        current_theme = self.config.get("theme", "dark_default")
        theme_display = {
            "dark_default": "Dark Default",
            "dark_blue": "Dark Blue",
            "dark_purple": "Dark Purple",
            "dark_green": "Dark Green",
            "light_gray": "Light Gray"
        }.get(current_theme, "Dark Default")
        self.theme_combo.setCurrentText(theme_display)
        self.theme_combo.setStyleSheet("font-size: 16px; padding: 8px;")
        theme_layout.addRow("Select Theme:", self.theme_combo)

        scroll_layout.addWidget(theme_group)

        # Main Projects and Sub-Projects Section
        project_group = QGroupBox("Main Projects and Sub-Projects")
        project_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        project_layout = QVBoxLayout(project_group)

        main_project_label = QLabel("Main Projects:")
        main_project_label.setStyleSheet("font-size: 16px;")
        project_layout.addWidget(main_project_label)
        self.main_project_list = QListWidget()
        self.main_project_list.setStyleSheet("font-size: 16px; padding: 8px;")
        for main_project in self.config["main_projects"]:
            self.main_project_list.addItem(main_project)
        self.main_project_list.currentItemChanged.connect(self.update_sub_project_list)
        project_layout.addWidget(self.main_project_list)

        main_project_input_layout = QHBoxLayout()
        new_main_label = QLabel("New Main Project:")
        new_main_label.setStyleSheet("font-size: 16px;")
        main_project_input_layout.addWidget(new_main_label)
        self.new_main_project_entry = QLineEdit()
        self.new_main_project_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        main_project_input_layout.addWidget(self.new_main_project_entry)
        add_main_btn = QPushButton("Add Main Project")
        add_main_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        add_main_btn.clicked.connect(self.add_main_project)
        main_project_input_layout.addWidget(add_main_btn)
        remove_main_btn = QPushButton("Remove Main Project")
        remove_main_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        remove_main_btn.clicked.connect(self.remove_main_project)
        main_project_input_layout.addWidget(remove_main_btn)
        project_layout.addLayout(main_project_input_layout)

        sub_project_label = QLabel("Sub-Projects:")
        sub_project_label.setStyleSheet("font-size: 16px;")
        project_layout.addWidget(sub_project_label)
        self.sub_project_list = QListWidget()
        self.sub_project_list.setStyleSheet("font-size: 16px; padding: 8px;")
        project_layout.addWidget(self.sub_project_list)

        sub_project_input_layout = QHBoxLayout()
        new_sub_label = QLabel("New Sub-Project:")
        new_sub_label.setStyleSheet("font-size: 16px;")
        sub_project_input_layout.addWidget(new_sub_label)
        self.new_sub_project_entry = QLineEdit()
        self.new_sub_project_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        sub_project_input_layout.addWidget(self.new_sub_project_entry)
        add_sub_btn = QPushButton("Add Sub-Project")
        add_sub_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        add_sub_btn.clicked.connect(self.add_sub_project)
        sub_project_input_layout.addWidget(add_sub_btn)
        remove_sub_btn = QPushButton("Remove Sub-Project")
        remove_sub_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        remove_sub_btn.clicked.connect(self.remove_sub_project)
        sub_project_input_layout.addWidget(remove_sub_btn)
        project_layout.addLayout(sub_project_input_layout)

        scroll_layout.addWidget(project_group)

        # Task Types Section
        task_type_group = QGroupBox("Task Types")
        task_type_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        task_type_layout = QVBoxLayout(task_type_group)

        task_type_label = QLabel("Task Types:")
        task_type_label.setStyleSheet("font-size: 16px;")
        task_type_layout.addWidget(task_type_label)
        self.task_type_list = QListWidget()
        self.task_type_list.setStyleSheet("font-size: 16px; padding: 8px;")
        for task_type in self.config["task_types"]:
            self.task_type_list.addItem(task_type)
        task_type_layout.addWidget(self.task_type_list)

        task_type_input_layout = QHBoxLayout()
        new_task_type_label = QLabel("New Task Type:")
        new_task_type_label.setStyleSheet("font-size: 16px;")
        task_type_input_layout.addWidget(new_task_type_label)
        self.new_task_type_entry = QLineEdit()
        self.new_task_type_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        task_type_input_layout.addWidget(self.new_task_type_entry)
        add_task_type_btn = QPushButton("Add Task Type")
        add_task_type_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        add_task_type_btn.clicked.connect(self.add_task_type)
        task_type_input_layout.addWidget(add_task_type_btn)
        remove_task_type_btn = QPushButton("Remove Selected")
        remove_task_type_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        remove_task_type_btn.clicked.connect(self.remove_task_type)
        task_type_input_layout.addWidget(remove_task_type_btn)
        task_type_layout.addLayout(task_type_input_layout)

        scroll_layout.addWidget(task_type_group)

        # Labels Section
        label_group = QGroupBox("Labels")
        label_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        label_layout = QVBoxLayout(label_group)

        labels_label = QLabel("Labels:")
        labels_label.setStyleSheet("font-size: 16px;")
        label_layout.addWidget(labels_label)
        self.label_list = QListWidget()
        self.label_list.setStyleSheet("font-size: 16px; padding: 8px;")
        for label in self.config["labels"]:
            self.label_list.addItem(f"{label} ({self.config['labels'][label]})")
        label_layout.addWidget(self.label_list)

        label_input_layout = QHBoxLayout()
        new_label_label = QLabel("New Label:")
        new_label_label.setStyleSheet("font-size: 16px;")
        label_input_layout.addWidget(new_label_label)
        self.new_label_entry = QLineEdit()
        self.new_label_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        label_input_layout.addWidget(self.new_label_entry)
        color_label = QLabel("Color (Hex):")
        color_label.setStyleSheet("font-size: 16px;")
        label_input_layout.addWidget(color_label)
        self.label_color_entry = QLineEdit("#000000")
        self.label_color_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        label_input_layout.addWidget(self.label_color_entry)
        add_label_btn = QPushButton("Add Label")
        add_label_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        add_label_btn.clicked.connect(self.add_label)
        label_input_layout.addWidget(add_label_btn)
        remove_label_btn = QPushButton("Remove Selected")
        remove_label_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        remove_label_btn.clicked.connect(self.remove_label)
        label_input_layout.addWidget(remove_label_btn)
        label_layout.addLayout(label_input_layout)

        scroll_layout.addWidget(label_group)

        # Signature Details Section
        signature_group = QGroupBox("Signature Details")
        signature_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        signature_layout = QFormLayout(signature_group)
        signature_layout.setLabelAlignment(Qt.AlignRight)
        signature_layout.setSpacing(15)

        self.name_entry = QLineEdit(self.config["signature"]["name"])
        self.name_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        signature_layout.addRow("Name:", self.name_entry)
        self.mobile_entry = QLineEdit(self.config["signature"]["mobile"])
        self.mobile_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        signature_layout.addRow("Mobile:", self.mobile_entry)
        self.email_entry = QLineEdit(self.config["signature"]["email"])
        self.email_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        signature_layout.addRow("Email:", self.email_entry)

        scroll_layout.addWidget(signature_group)

        # Email Recipients Section
        email_group = QGroupBox("Email Recipients")
        email_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        email_layout = QFormLayout(email_group)
        email_layout.setLabelAlignment(Qt.AlignRight)
        email_layout.setSpacing(15)

        self.to_entry = QLineEdit(self.config["email"]["to"])
        self.to_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        email_layout.addRow("To:", self.to_entry)
        self.cc_entry = QLineEdit(self.config["email"]["cc"])
        self.cc_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        email_layout.addRow("CC:", self.cc_entry)

        scroll_layout.addWidget(email_group)

        # Notification Settings Section
        notification_group = QGroupBox("Notification Settings")
        notification_group.setStyleSheet("QGroupBox { font-size: 18px; font-weight: bold; }")
        notification_layout = QFormLayout(notification_group)
        notification_layout.setLabelAlignment(Qt.AlignRight)
        notification_layout.setSpacing(15)

        self.notification_time_entry = QLineEdit(self.config.get("notification_time", "18:00"))
        self.notification_time_entry.setStyleSheet("font-size: 16px; padding: 8px;")
        notification_layout.addRow("Notification Time (HH:MM, 24-hour format):", self.notification_time_entry)

        scroll_layout.addWidget(notification_group)

        # Save and Cancel Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Config")
        save_btn.setStyleSheet("font-size: 16px; padding: 10px;")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("font-size: 16px; padding: 10px;")
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
        # Save the selected theme
        theme_display = self.theme_combo.currentText()
        self.config["theme"] = {
            "Dark Default": "dark_default",
            "Dark Blue": "dark_blue",
            "Dark Purple": "dark_purple",
            "Dark Green": "dark_green",
            "Light Gray": "light_gray"
        }.get(theme_display, "dark_default")

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
            from daily_status_logic import save_config
            save_config(self.config, new_config_path)
            self.on_save_callback(self.config, new_config_path)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.parent.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save settings: {e}")

    def cancel(self):
        if not any(self.config.get(key) for key in ["logo_path", "main_projects", "signature", "email"] if key != "config_file_path" and key != "tasks_file_path"):
            QMessageBox.warning(self, "Configuration Required", "You must save the configuration to proceed.")
            return
        self.parent.reject()

# Main Application Class
class EODTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Status Mail Formatter")
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Daily Status Mail Formatter Tab
        self.eod_ui = EODUI()
        self.eod_logic = EODLogic(self.eod_ui, self)
        self.tab_widget.addTab(self.eod_ui, "Daily Status Mail Formatter")

        # Test Report Generator Tab
        self.test_report_widget = TestReportGeneratorWidget(self)
        self.tab_widget.addTab(self.test_report_widget, "Test Report Generator")

        # Set a neutral background for the QMainWindow
        self.setStyleSheet("QMainWindow { background-color: #2E2E2E; }")

    def apply_theme_to_test_report(self, theme_name):
        self.test_report_widget.apply_theme(theme_name)

    def closeEvent(self, event):
        self.eod_logic.closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EODTool()
    window.showMaximized()
    sys.exit(app.exec())