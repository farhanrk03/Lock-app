# Lock-app
Locker Stampo-Desktop Version
# 🔐 Folder Locker Desktop

A modern, lightweight folder-locking application for Windows — protect your folders with AES-encrypted ZIP files using a sleek graphical interface. Perfect for students, professionals, and anyone who needs privacy.


## 🧰 Features

- 🔒 Lock any folder with a password
- 🔓 Unlock encrypted folders anytime
- 🔁 Change ZIP password easily
- 📜 View folder locking history
- 🎨 Light & Dark Mode switch
- ✅ Auto-delete original folder after locking (optional)
- 🧠 AES encryption via `pyzipper`
- 🖥️ Offline & standalone — no internet required

---

## 🚀 Download & Install

| Type              | File                                         | Use Case                  |
|-------------------|----------------------------------------------|---------------------------|
| 🔹 Portable `.exe` | `folder locker stampo.exe`                       | Just run — no install     |
| 🔹 Installer `.exe` | `FolderLockerInstaller.exe`                 | Adds Start Menu/Desktop   |

> 📁 Files available in the `dist/` folder.

---

## 💡 How to Use

### 🔐 Lock a Folder

1. Open the app
2. Click **"Lock Folder"**
3. Choose any folder
4. Enter your password → folder becomes `.zip`

### 🔓 Unlock a Folder

1. Click **"Unlock Folder"**
2. Select the `.zip` file
3. Enter the same password → folder restored

### 🛠 Change Password

- Use **"Change Password"** to re-encrypt an existing ZIP with a new password

---

## 📦 Requirements (Dev)

- Python 3.8+
- `customtkinter`, `pyzipper`
- Build with:
  ```bash
  pyinstaller --onefile --noconsole --icon=icon.ico folder_locker_en.py
