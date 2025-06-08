import json
import os
import webbrowser
import tempfile
from datetime import date
import base64
import logging
import subprocess
import urllib.parse
import win32com.client
from PySide6.QtWidgets import (QApplication, QMessageBox, QDialog, QSystemTrayIcon, QMenu, QFileDialog, QVBoxLayout)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QCloseEvent, QIcon
import win32clipboard

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
    "email": {"to": "", "cc": "", "recipient": "Team"},
    "notification_time": "18:00",
    "theme": "dark_default"
}

# Define STATUS_COLORS for the email format
STATUS_COLORS = {
    "Completed": "#5e8f59",
    "In Progress": "#c06530",
    "To Be Done": "#029de6",
    "Blocked": "#ff0000"
}

# Setup logging
logging.basicConfig(filename='notification.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Utility Functions
def load_config(config_path, default_path):
    config_path = get_config_or_tasks_path(DEFAULT_CONFIG_FILE, config_path, default_path)
    if not os.path.exists(config_path):
        logging.info(f"No config file found at {config_path}, using default config")
        return DEFAULT_CONFIG.copy(), config_path
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
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
        logging.info(f"Loaded config: email={config['email']}, cc={config['email']['cc']}")
        return config, config_path
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy(), config_path

def save_config(config, config_path):
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        QMessageBox.critical(None, "Save Config Error", f"Failed to save configuration:\n{e}")

def encode_image_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return ""

def preview_email_html(html_content):
    try:
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
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
            pass
        return default_path

def set_clipboard_html(html_content):
    html_bytes = html_content.encode('utf-8')
    html_length = len(html_bytes)

    header = (
        f"Version:0.9\r\n"
        f"StartHTML:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n')}\r\n"
        f"EndHTML:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n') + html_length}\r\n"
        f"StartFragment:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n')}\r\n"
        f"EndFragment:{len('Version:0.9\r\nStartHTML:00000000\r\nEndHTML:00000000\r\nStartFragment:00000000\r\nEndFragment:00000000\r\n') + html_length}\r\n"
    )

    cf_html = header.encode('utf-8') + html_bytes

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat("HTML Format"), cf_html)
        plain_text = html_content.replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n').replace(r'<[^>]+>', '')
        win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, plain_text.encode('utf-8'))
    finally:
        win32clipboard.CloseClipboard()

class EODLogic:
    def __init__(self, ui, parent=None):
        self.ui = ui
        self.parent = parent
        self.config, self.config_path = load_config(DEFAULT_PERSISTENT_CONFIG_PATH, DEFAULT_PERSISTENT_CONFIG_PATH)
        self.tasks = []
        self.editing_index = None
        self.html_copied = False

        # Initialize system tray for notifications
        self.tray_icon = QSystemTrayIcon(self.parent)
        self.tray_icon.setIcon(QIcon.fromTheme("mail-message"))
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show Window")
        show_action.triggered.connect(self.parent.show)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(lambda: QApplication.quit())
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Setup timer for notifications
        self.notification_timer = QTimer(self.parent)
        self.notification_timer.timeout.connect(self.check_notification_time)
        self.notification_timer.start(10000)  # Check every 10 seconds

        # Connect UI signals
        self.connect_signals()
        self.update_config_widgets()

    def connect_signals(self):
        self.ui.settings_button.clicked.connect(self.show_settings_dialog)
        self.ui.main_project.currentTextChanged.connect(self.update_sub_project_combo)
        self.ui.sub_project.currentTextChanged.connect(self.validate_mandatory_fields)
        self.ui.task_entry.textChanged.connect(self.validate_mandatory_fields)
        self.ui.task_type.currentTextChanged.connect(self.validate_mandatory_fields)
        self.ui.add_task_btn.clicked.connect(self.add_task)
        self.ui.move_up_button.clicked.connect(self.move_task_up)
        self.ui.move_down_button.clicked.connect(self.move_task_down)
        self.ui.edit_task_button.clicked.connect(self.edit_task)
        self.ui.delete_task_button.clicked.connect(self.delete_task)
        self.ui.clear_all_button.clicked.connect(self.clear_all_tasks)
        self.ui.save_tasks_button.clicked.connect(self.save_tasks)
        self.ui.load_tasks_button.clicked.connect(self.load_tasks)
        self.ui.export_html_button.clicked.connect(self.export_html)
        self.ui.copy_button.clicked.connect(self.copy_html_body)
        self.ui.export_text_button.clicked.connect(self.export_text)
        self.ui.preview_button.clicked.connect(self.preview_email)
        self.ui.open_outlook_button.clicked.connect(self.open_outlook_email)

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.parent.hide()
        self.tray_icon.showMessage(
            "Daily Status Mail Formatter",
            "Application minimized to tray.",
            QSystemTrayIcon.Information,
            2000
        )

    def check_notification_time(self):
        current_time = QDateTime.currentDateTime().time().toString("HH:mm")
        current_day = date.today().weekday()
        if current_day in (5, 6):
            logging.debug(f"Skipping notification - Today is {'Saturday' if current_day == 5 else 'Sunday'}")
            return
        notification_time = self.config.get("notification_time", "18:00")
        logging.debug(f"Current time: {current_time}, Notification time: {notification_time}")
        if current_time == notification_time:
            logging.info("Notification triggered.")
            self.tray_icon.showMessage(
                "Daily Status Mail Formatter",
                "It's time to send your daily status email!",
                QSystemTrayIcon.Information,
                5000
            )

    def update_config(self, new_config, new_config_path):
        self.config = new_config
        self.config_path = new_config_path
        logging.info(f"Updated config: cc={new_config['email']['cc']}")
        self.update_config_widgets()
        self.ui.apply_theme(self.config.get("theme", "dark_default"))

    def update_config_widgets(self):
        self.ui.main_project.clear()
        self.ui.main_project.addItems(self.config["main_projects"].keys())
        self.ui.label_combo.clear()
        self.ui.label_combo.addItem("")
        self.ui.label_combo.addItems(self.config["labels"].keys())
        self.ui.task_type.clear()
        self.ui.task_type.addItem("")
        self.ui.task_type.addItems(self.config["task_types"])
        if self.config["main_projects"]:
            self.ui.main_project.setCurrentIndex(0)
            self.update_sub_project_combo()
        else:
            self.ui.main_project.setCurrentIndex(-1)
            self.ui.sub_project.clear()
        self.validate_mandatory_fields()

    def update_sub_project_combo(self):
        main_project = self.ui.main_project.currentText()
        sub_projects = self.config["main_projects"].get(main_project, [])
        self.ui.sub_project.clear()
        self.ui.sub_project.addItems(sub_projects)
        if sub_projects:
            self.ui.sub_project.setCurrentIndex(0)

    def validate_mandatory_fields(self):
        main_project = self.ui.main_project.currentText().strip()
        sub_project = self.ui.sub_project.currentText().strip()
        task = self.ui.task_entry.text().strip()
        task_type = self.ui.task_type.currentText().strip()
        all_filled = bool(main_project and sub_project and task and task_type)
        self.ui.add_task_btn.setEnabled(all_filled)

    def update_button_states(self):
        state = not self.tasks
        self.ui.move_up_button.setDisabled(state)
        self.ui.move_down_button.setDisabled(state)
        self.ui.edit_task_button.setDisabled(state)
        self.ui.delete_task_button.setDisabled(state)
        self.ui.clear_all_button.setDisabled(state)
        self.ui.save_tasks_button.setDisabled(state)
        self.ui.export_html_button.setEnabled(not state)
        self.ui.copy_button.setEnabled(not state)
        self.ui.export_text_button.setEnabled(not state)

    def add_task(self):
        main_project = self.ui.main_project.currentText()
        sub_project = self.ui.sub_project.currentText()
        task = self.ui.task_entry.text().strip()
        status = next(status for status, radio in self.ui.status_group.items() if radio.isChecked())
        task_type = self.ui.task_type.currentText()
        label = self.ui.label_combo.currentText()
        comment = self.ui.comment_entry.text().strip()

        if label and not comment:
            QMessageBox.warning(self.parent, "Input Error", "Comment is required when a label is selected.")
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
            self.ui.add_task_btn.setText("➕ Add Task")
        else:
            self.tasks.append(task_data)

        self.update_task_list()
        self.ui.task_entry.clear()
        self.ui.label_combo.setCurrentIndex(0)
        self.ui.comment_entry.clear()
        self.ui.task_type.setCurrentIndex(0)
        self.save_tasks()
        self.update_button_states()
        self.validate_mandatory_fields()

    def edit_task(self):
        if self.ui.task_list.currentRow() < 0:
            QMessageBox.warning(self.parent, "Selection Error", "Please select a task to edit.")
            return
        self.editing_index = self.ui.task_list.currentRow()
        task = self.tasks[self.editing_index]
        self.ui.main_project.setCurrentText(task["main_project"])
        self.update_sub_project_combo()
        self.ui.sub_project.setCurrentText(task["sub_project"])
        self.ui.task_entry.setText(task["task"])
        self.ui.status_group[task["status"]].setChecked(True)
        self.ui.task_type.setCurrentText("" if task["task_type"] == "Normal" else task["task_type"])
        self.ui.label_combo.setCurrentText(task.get("label", ""))
        self.ui.comment_entry.setText(task.get("comment", ""))
        self.ui.add_task_btn.setText("💾 Save Edit")
        self.validate_mandatory_fields()

    def delete_task(self):
        if self.ui.task_list.currentRow() >= 0:
            del self.tasks[self.ui.task_list.currentRow()]
            self.update_task_list()
            self.save_tasks()
            self.update_button_states()

    def clear_all_tasks(self):
        if QMessageBox.question(self.parent, "Confirm", "Clear all tasks?") == QMessageBox.Yes:
            self.tasks.clear()
            self.update_task_list()
            self.save_tasks()
            self.update_button_states()

    def move_task_up(self):
        idx = self.ui.task_list.currentRow()
        if idx > 0:
            self.tasks[idx - 1], self.tasks[idx] = self.tasks[idx], self.tasks[idx - 1]
            self.update_task_list()
            self.ui.task_list.setCurrentRow(idx - 1)
            self.save_tasks()

    def move_task_down(self):
        idx = self.ui.task_list.currentRow()
        if idx >= 0 and idx < len(self.tasks) - 1:
            self.tasks[idx], self.tasks[idx + 1] = self.tasks[idx + 1], self.tasks[idx]
            self.update_task_list()
            self.ui.task_list.setCurrentRow(idx + 1)
            self.save_tasks()

    def update_task_list(self):
        self.ui.task_list.clear()
        for t in self.tasks:
            label = t.get("label", "")
            label_display = f" [{label}]" if label else ""
            task_type_display = f" ({t['task_type']})" if t['task_type'] != "Normal" else ""
            self.ui.task_list.addItem(f"[{t['main_project']}][{t['sub_project']}] {t['status']}{task_type_display}{label_display} - {t['task']}")
        self.update_button_states()

    def save_tasks(self):
        try:
            with open(self.config["tasks_file_path"], 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=4)
            logging.info("Tasks saved successfully")
            self.tray_icon.showMessage(
                "Daily Status Mail Formatter",
                "Tasks saved successfully!",
                QSystemTrayIcon.Information,
                2000
            )
            QMessageBox.information(self.parent, "Success", "Tasks saved successfully!")
        except Exception as e:
            logging.error(f"Failed to save tasks: {e}")
            QMessageBox.critical(self.parent, "Save Error", f"Failed to save tasks:\n{e}")

    def load_tasks(self):
        if os.path.exists(self.config["tasks_file_path"]):
            try:
                with open(self.config["tasks_file_path"], 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                for task in self.tasks:
                    if task["status"] == "Pending":
                        task["status"] = "In Progress"
                    if "task_type" not in task:
                        task["task_type"] = "Normal"
                self.update_task_list()
                logging.info("Tasks loaded successfully")
                self.tray_icon.showMessage(
                    "Daily Status Mail Formatter",
                    "Tasks loaded successfully!",
                    QSystemTrayIcon.Information,
                    2000
                )
                QMessageBox.information(self.parent, "Success", "Tasks loaded successfully!")
            except Exception as e:
                logging.error(f"Failed to load tasks: {e}")
                QMessageBox.critical(self.parent, "Load Error", f"Failed to load tasks:\n{e}")
                self.tasks = []
                self.update_task_list()
        else:
            QMessageBox.information(self.parent, "No Tasks", "No tasks file found. Starting with an empty task list.")
            self.tasks = []
            self.update_task_list()
        self.update_button_states()

    def generate_email_body(self, preview=False):
        today = date.today().strftime("%d/%m/%Y")
        recipient = self.config.get("email", {}).get("recipient", "Team")
        html = f"""<!DOCTYPE html><html><body style="font-family: Calibri; color: #000; background-color: #fff;">
        <p>Hi {recipient},</p><p>Please find below today's task updates:</p>"""

        grouped = {}
        for task in self.tasks:
            main_proj = task["main_project"]
            sub_proj = task["sub_project"]
            if main_proj not in grouped:
                grouped[main_proj] = {}
            grouped[main_proj].setdefault(sub_proj, [])
            text = task["task"]
            if "http" in text:
                words = text.split()
                text = " ".join(f'<a href="{word}">{word}</a>' if word.startswith("http") else word for word in words)
            task_type_display = f" ({task['task_type']})" if task["task_type"] != "Normal" else ""
            status_display = f"{task['status']}{task_type_display}"
            status = f'<span style="color:{STATUS_COLORS[task["status"]]}">{status_display}</span>'
            label = task.get("label", "")
            comment = task.get("comment", "")
            if "http" in comment:
                words = comment.split()
                comment = " ".join(f'<a href="{word}">{word}</a>' if word.startswith("http") else word for word in words)
            label_part = f'<span style="color:{self.config["labels"][label]}">{label}</span>' if label else ""
            comment_part = f'<span style="color:#666666">{comment}</span>' if comment else ""
            label_comment = f"{label_part} - {comment_part}" if label and comment else label_part or comment_part
            subpoints = f'<ul><li>{label_comment}</li></ul>' if label_comment else ""
            grouped[main_proj][sub_proj].append((status, text, subpoints))

        main_idx = 1
        for main_proj in grouped:
            html += f"<h4><u>{main_idx}. {main_proj}</u></h4>"
            sub_idx = 1
            for sub_proj in grouped[main_proj]:
                html += f"<h5>{main_idx}.{sub_idx} {sub_proj}</h5><ul>"
                for status, text, subpoints in grouped[main_proj][sub_proj]:
                    html += f"<li>{status} - {text}{subpoints}</li>"
                html += "</ul>"
                sub_idx += 1
            main_idx += 1

        html += "</body></html>"
        return html

    def generate_signature(self, preview=True):
        signature = self.config["signature"]
        logo_base64 = encode_image_base64(self.config["logo_path"])
        logo_img = f'<img src="data:image/png;base64,{logo_base64}" style="height:40px;">' if logo_base64 and preview else ''
        signature_html = f"""
        <p><br>--<br>Thanks & Regards,<br><b>{signature['name']}</b><br>
        {logo_img}<br>
        Caparizon Software Ltd<br>
        D-75, 8th Floor, Infra Futura, Kakkanaad, Kochi - 682021<br>
        Mobile: {signature['mobile']}<br>
        Office: +91 - 9400359991<br>
        <a href="mailto:{signature['email']}">{signature['email']}</a><br>
        <a href="http://www.caparizon.com">www.caparizon.com</a>
        </p>
        """
        return signature_html

    def generate_copy_html(self):
        html_body = self.generate_email_body(preview=False)
        signature = self.generate_signature(preview=False)
        full_html = html_body.rsplit("</body>", 1)[0] + signature + "</body></html>"
        return full_html

    def export_html(self):
        if not self.tasks:
            QMessageBox.warning(self.parent, "No Tasks", "No tasks to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self.parent, "Export HTML", f"Daily_Status_{date.today().strftime('%d%m%Y')}.html", "HTML Files (*.html)")
        if not path:
            return
        try:
            html_content = self.generate_copy_html()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            QMessageBox.information(self.parent, "Success", "HTML exported successfully!")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Error", f"Failed to export HTML:\n{e}")

    def copy_html_body(self):
        if not self.tasks:
            QMessageBox.warning(self.parent, "No Tasks", "No tasks to copy.")
            return
        try:
            html_content = self.generate_email_body(preview=False)
            set_clipboard_html(html_content)
            self.html_copied = True
            self.ui.open_outlook_button.setEnabled(True)
            QMessageBox.information(
                self.parent,
                "Success",
                "HTML body (without signature) copied to clipboard!\n"
                "You can now click 'Open in Email Client' and paste (Ctrl+V) the content into the email body."
            )
        except Exception as e:
            QMessageBox.critical(self.parent, "Copy Error", f"Failed to copy HTML body:\n{e}")

    def export_text(self):
        if not self.tasks:
            QMessageBox.warning(self.parent, "No Tasks", "No tasks to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self.parent, "Export Text", f"Daily_Status_{date.today().strftime('%d%m%Y')}.txt", "Text Files (*.txt)")
        if not path:
            return
        try:
            text_content = f"Daily Status Update - {date.today().strftime('%d/%m/%Y')}\n\n"
            text_content += "Hi Team,\n\n"
            text_content += f"Please find the below status update for today ({date.today().strftime('%d%m%Y')}):\n\n"
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
            QMessageBox.information(self.parent, "Success", "Text exported successfully!")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Error", f"Failed to export text:\n{e}")

    def preview_email(self):
        if not self.tasks:
            QMessageBox.warning(self.parent, "No Tasks", "No tasks to preview.")
            return
        html_content = self.generate_email_body(preview=True)
        signature = self.generate_signature(preview=True)
        full_html = html_content.rsplit("</body>", 1)[0] + signature + "</body></html>"
        preview_email_html(full_html)

    def open_outlook_email(self):
        if not self.tasks:
            QMessageBox.warning(self.parent, "No Tasks", "No tasks to include in the email.")
            return
        if not self.config["email"]["to"].strip():
            QMessageBox.warning(self.parent, "Configuration Error", "Please configure at least one 'To' email address in Settings.")
            return

        try:
            # Copy HTML content without signature for manual pasting
            html_content = self.generate_email_body(preview=False)
            set_clipboard_html(html_content)
            self.html_copied = True

            # Generate full HTML with signature for Outlook fallbacks
            full_html = self.generate_copy_html()

            today = date.today().strftime("%d/%m/%Y")
            subject = f"Daily Status {today}"
            to_emails = self.config["email"]["to"].strip()
            cc_emails_raw = self.config["email"]["cc"].strip()

            # Normalize and validate CC emails
            if cc_emails_raw:
                cc_list = [email.strip() for email in cc_emails_raw.replace(',', ';').split(';') if email.strip()]
                cc_emails_com = ';'.join(cc_list)  # For COM interface
                cc_emails = cc_emails_raw  # For mailto
                logging.info(f"Processed CC emails: raw='{cc_emails_raw}', com='{cc_emails_com}'")
            else:
                cc_list = []
                cc_emails_com = ''
                cc_emails = ''
                logging.warning(f"No CC emails configured: raw='{cc_emails_raw}'")
                QMessageBox.information(self.parent, "Warning", "No CC emails configured. Proceeding with only To emails.")

            # Try mailto URL first
            try:
                params = {
                    "to": to_emails,
                    "cc": cc_emails,
                    "subject": subject,
                    "body": ""  # Body is empty since HTML is on clipboard
                }
                mailto_url = (
                    f"mailto:{urllib.parse.quote(params['to'])}?"
                    f"cc={urllib.parse.quote(params['cc'])}&"
                    f"subject={urllib.parse.quote(params['subject'])}&"
                    f"body={urllib.parse.quote(params['body'])}"
                )
                logging.info(f"Opening email with To: {to_emails}, CC: {cc_emails}, Subject: {subject}, URL: {mailto_url}")
                webbrowser.open(mailto_url)
                QMessageBox.information(
                    self.parent,
                    "Success",
                    "Email client opened with pre-filled To, CC, and Subject.\n"
                    "The HTML body (without signature) is copied to the clipboard. Please paste (Ctrl+V) into the email body.\n"
                    "Add your signature in Outlook if needed."
                )
                return
            except Exception as e:
                logging.info(f"Failed to open email client via mailto: {e}")

            # Try Outlook New
            try:
                outlook = win32com.client.Dispatch("Outlook.Application.16")
                mail = outlook.CreateItem(0)  # 0 = olMailItem
                mail.Subject = subject
                mail.To = to_emails
                mail.CC = cc_emails_com
                mail.HTMLBody = full_html
                mail.Display()
                QMessageBox.information(self.parent, "Success", "Email opened in Outlook New with pre-filled fields!")
                return
            except Exception as e:
                logging.info(f"Failed to open Outlook New: {e}")

            # Fall back to classic Outlook
            try:
                outlook = win32com.client.Dispatch("Outlook.Application")
                mail = outlook.CreateItem(0)  # 0 = olMailItem
                mail.Subject = subject
                mail.To = to_emails
                mail.CC = cc_emails_com
                mail.HTMLBody = full_html
                mail.Display()
                QMessageBox.information(self.parent, "Success", "Email opened in classic Outlook with pre-filled fields!")
            except Exception as e:
                QMessageBox.critical(
                    self.parent,
                    "Email Error",
                    f"Failed to open email in any Outlook version.\n"
                    f"Ensure Outlook is installed.\nError: {str(e)}\n"
                    "The HTML body (without signature) is copied to the clipboard. Please open Outlook manually and paste the content."
                )

        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Email Error",
                f"Failed to prepare email:\n{e}\n"
                "Please try copying the HTML body and pasting it into Outlook manually."
            )

    def show_settings_dialog(self):
        from daily_status_mail import SettingsWidget
        self.settings_dialog = QDialog(self.parent)
        self.settings_dialog.setWindowTitle("Settings")
        dialog_layout = QVBoxLayout(self.settings_dialog)
        self.settings_widget = SettingsWidget(self.settings_dialog, self.config, self.config_path, self.update_config)
        dialog_layout.addWidget(self.settings_widget)
        self.settings_dialog.resize(900, 700)
        self.settings_dialog.exec()