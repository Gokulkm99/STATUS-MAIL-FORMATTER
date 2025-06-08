from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea,
                               QLabel, QComboBox, QLineEdit, QRadioButton, QPushButton, QListWidget,
                               QFrame, QTabWidget, QSizePolicy)
from PySide6.QtCore import Qt

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

class EODUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_theme("dark_default")  # Apply default dark theme on initialization

    def setup_ui(self):
        main_tab_layout = QVBoxLayout(self)
        main_tab_layout.setContentsMargins(20, 20, 20, 20)
        main_tab_layout.setSpacing(15)

        # Top Bar (Settings Button Only)
        top_bar = QHBoxLayout()
        main_tab_layout.addLayout(top_bar)
        top_bar.addStretch()
        self.settings_button = QPushButton("⚙ Settings")
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
        project_layout.addRow(main_label_label, self.main_project)

        sub_label = QLabel("Sub-Project: <span style='color: red;'>*</span>")
        sub_label.setTextFormat(Qt.TextFormat.RichText)
        self.sub_project = QComboBox()
        project_layout.addRow(sub_label, self.sub_project)

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
        task_layout.addRow(task_type_label, self.task_type)

        # Add Task Button (below Task Type)
        self.add_task_btn = QPushButton("➕ Add Task")
        self.add_task_btn.setEnabled(False)  # Disabled by default
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
        list_buttons_layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("⬇ Move Down")
        list_buttons_layout.addWidget(self.move_down_button)

        self.edit_task_button = QPushButton("✏ Edit Task")
        list_buttons_layout.addWidget(self.edit_task_button)

        self.delete_task_button = QPushButton("🗑 Delete")
        list_buttons_layout.addWidget(self.delete_task_button)

        self.clear_all_button = QPushButton("🗑 Clear All")
        list_buttons_layout.addWidget(self.clear_all_button)

        self.save_tasks_button = QPushButton("💾 Save Tasks")
        list_buttons_layout.addWidget(self.save_tasks_button)

        self.load_tasks_button = QPushButton("📂 Load Tasks")
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
        export_buttons_layout.addWidget(self.export_html_button)

        self.copy_button = QPushButton("Copy HTML Body")
        export_buttons_layout.addWidget(self.copy_button)

        self.export_text_button = QPushButton("Export as Text")
        export_buttons_layout.addWidget(self.export_text_button)

        self.preview_button = QPushButton("Preview EOD Email")
        export_buttons_layout.addWidget(self.preview_button)

        self.open_outlook_button = QPushButton("Open in Email Client")
        self.open_outlook_button.setEnabled(True)  # Enabled since HTML body is set directly
        export_buttons_layout.addWidget(self.open_outlook_button)

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
                "border_color": "#62566C",
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
                font-size: 18px;  /* Increased font size */
                font-weight: bold;
                padding: 8px;  /* Increased padding */
            }}
            QWidget#EODTaskTracker QLabel {{
                color: {theme['label_color']};
                font-family: Roboto;
                font-size: 16px;  /* Increased font size */
            }}
            QWidget#EODTaskTracker QLineEdit,
            QWidget#EODTaskTracker QComboBox {{
                background-color: {theme['input_background']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 5px;
                padding: 8px;  /* Increased padding */
                font-size: 16px;  /* Increased font size */
            }}
            QWidget#EODTaskTracker QPushButton {{
                background-color: {theme['button_background']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;  /* Increased padding */
                font-family: Roboto;
                font-size: 16px;  /* Increased font size */
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
                font-size: 16px;  /* Increased font size */
            }}
            QWidget#EODTaskTracker QRadioButton#status-Completed {{ color: #5e8f59; }}
            QWidget#EODTaskTracker QRadioButton#status-In\\ Progress {{ color: #c06530; }}
            QWidget#EODTaskTracker QRadioButton#status-To\\ Be\\ Done {{ color: #029de6; }}
            QWidget#EODTaskTracker QRadioButton#status-Blocked {{ color: #ff0000; }}
            QWidget#EODTaskTracker QListWidget {{
                background-color: {theme['list_background']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 5px;
                padding: 8px;  /* Increased padding */
                font-family: Roboto;
                font-size: 16px;  /* Increased font size */
            }}
            QWidget#EODTaskTracker QListWidget::item:selected {{
                background-color: {theme['button_background']};
                color: white;
            }}
            QWidget#EODTaskTracker QListWidget::item:alternate {{
                background-color: {theme['list_alternate']};
            }}
        """
        self.setObjectName("EODTaskTracker")
        self.setStyleSheet(stylesheet)