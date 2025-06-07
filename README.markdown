# Daily Status Mail - Executable Creation

This guide explains how to convert the `daily_status_mail.py` Python script into a standalone `.exe` file for Windows using **PyInstaller**, as well as how to set up and run the resulting executable.

## Prerequisites

To create and run the `.exe` file, you need the following installed on your Windows system:

- **Python**: Version 3.6 or higher (recommended: 3.11 or latest stable version).
- **Python Packages**:
  - `tkinter`: Included with standard Python installations for the GUI.
  - `pywin32`: For clipboard operations (`win32clipboard`).
  - `pyinstaller`: To convert the Python script into an `.exe` file.
- **Optional Files**:
  - A logo image file (e.g., PNG) specified in `config.json` (default: `C:\Users\USER\Desktop\GM TOOLS AND FILES\MAIL AUTOMATION\Caparizonlogo.png`).
  - `pwa.py`: A script referenced for opening the email client (not provided; ensure it exists or modify the script to remove this functionality if not needed).
- **Configuration Files**:
  - `config.json`: Stores user settings (created automatically with defaults if not present).
  - `tasks.json`: Stores task data (created when tasks are saved).
- **Operating System**: Windows (due to `win32clipboard` dependency).

## Installation

Follow these steps to set up the environment and create the `.exe` file:

1. **Install Python**:
   - Download and install Python from [python.org](https://www.python.org/downloads/). Ensure you check "Add Python to PATH" during installation.
   - Verify installation:
     ```bash
     python --version
     ```
     or
     ```bash
     python3 --version
     ```

2. **Install Required Python Packages**:
   - Install `pywin32` and `pyinstaller` using pip:
     ```bash
     pip install pywin32 pyinstaller
     ```
   - Verify Tkinter is available (included with Python):
     ```bash
     python -m tkinter
     ```
     This should open a test window if Tkinter is installed correctly.
   - Verify installed packages:
     ```bash
     pip list
     ```
     Look for `pywin32` and `pyinstaller` in the output.

3. **Prepare the Logo File** (Optional):
   - The program expects a logo image at the path specified in `config.json`. If the default path is invalid, update it in the Settings window or `config.json` to point to a valid image file (PNG, JPG, etc.).

4. **Prepare `pwa.py` (Optional)**:
   - The script references `pwa.py` for opening an email client. If you have this script, place it in the same directory as `daily_status_mail.py`.
   - If `pwa.py` is unavailable or unnecessary, comment out or remove the `open_outlook_email` method in `daily_status_mail.py` to avoid errors.

5. **Save the Program**:
   - Save the provided code as `daily_status_mail.py` in a directory of your choice.

## Creating the `.exe` File

1. **Navigate to the Script Directory**:
   - Open a command prompt or terminal and navigate to the directory containing `daily_status_mail.py`:
     ```bash
     cd path/to/your/directory
     ```

2. **Run PyInstaller**:
   - Use PyInstaller to create a standalone `.exe` file:
     ```bash
     pyinstaller --onefile --windowed daily_status_mail.py
     ```
     - `--onefile`: Packages everything into a single `.exe` file.
     - `--windowed`: Prevents a console window from appearing (suitable for GUI applications like this one).
   - This command creates two folders (`build` and `dist`) and a `.spec` file in the directory. The executable will be located in the `dist` folder as `EODTaskTracker.exe`.

3. **(Optional) Include Additional Files**:
   - If you want to include the logo file or `pwa.py` with the executable, copy them to the `dist` folder or modify the PyInstaller command to include them:
     ```bash
     pyinstaller --onefile --windowed --add-data "path/to/logo.png;." --add-data "pwa.py;." daily_status_mail.py
     ```
     - Replace `path/to/logo.png` with the actual path to your logo file.
     - Use semicolons (`;`) for Windows paths in the `--add-data` option.
   - Note: Ensure the logo file path in `config.json` is relative to the `.exe` or accessible on the target system.

## Running the Executable

1. **Locate the Executable**:
   - After running PyInstaller, find `EODTaskTracker.exe` in the `dist` folder.

2. **Run the Executable**:
   - Double-click `EODTaskTracker.exe` to launch the application, or run it from the command prompt:
     ```bash
     dist\EODTaskTracker.exe
     ```
   - The GUI should open, allowing you to add, edit, delete, and export tasks.

3. **Usage**:
   - **Add/Edit Tasks**: Select a project, enter a task description, choose a status, and add or edit tasks.
   - **Settings**: Configure the logo path, projects, signature, and email recipients via the "Settings" button.
   - **Export**: Export tasks as HTML or text, copy HTML to the clipboard, or preview the EOD email.
   - **Email Client**: Use the "Open in Email Client" button to open your default email client (requires `pwa.py` and prior copying of HTML body).
   - Configuration and tasks are saved to `config.json` and `tasks.json` in the same directory as the `.exe`.

## Notes

- **Windows Dependency**: The `win32clipboard` module requires Windows. To make the program cross-platform, replace the `copy_html_to_clipboard` function with a library like `pyperclip`.
- **Logo File**: Ensure the logo file path in `config.json` is valid on the target system. If not, update it via the Settings window or manually in `config.json`.
- **pwa.py**: If `pwa.py` is not included, the "Open in Email Client" feature will fail. Remove or comment out the `open_outlook_email` method if not needed.
- **Executable Size**: The `.exe` file may be large due to bundled dependencies (e.g., Tkinter, pywin32). Using `--onefile` ensures portability but increases size.
- **File Paths**: If the logo or `pwa.py` is included with `--add-data`, ensure `config.json` uses relative paths (e.g., `./Caparizonlogo.png`) to locate them correctly.
- **Antivirus**: Some antivirus programs may flag the `.exe` as suspicious. This is common for PyInstaller executables. Add an exception or sign the executable if needed.

## Troubleshooting

- **PyInstaller Fails**:
   - Ensure `pyinstaller` and `pywin32` are installed (`pip install pyinstaller pywin32`).
   - Check for errors in the terminal output and verify Python version compatibility.
- **Executable Doesn’t Run**:
   - Run `EODTaskTracker.exe` from the command prompt to see error messages.
   - Ensure the logo file path is valid and accessible.
   - Verify that `pwa.py` exists if the email client feature is used.
- **Clipboard Issues**:
   - If copying HTML to the clipboard fails, ensure `pywin32` is installed and you have sufficient permissions.
- **Missing Files**:
   - If `config.json` or `tasks.json` are missing, they will be created automatically with defaults or when saving tasks.
- **Logo Not Found**:
   - Update the `logo_path` in `config.json` or via the Settings window to a valid path.

For further assistance, refer to the [PyInstaller documentation](https://pyinstaller.org/) or contact the developer.