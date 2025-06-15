import os
import sys
import shutil
import pyzipper
import hashlib
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog

PASSWORD_FILE = "locker_password.txt"
HISTORY_FILE = "locker_history.txt"

# hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_password(hashed_pw):
    with open(PASSWORD_FILE, 'w') as f:
        f.write(hashed_pw)

def check_password(input_pw):
    if not os.path.exists(PASSWORD_FILE):
        return False
    with open(PASSWORD_FILE, 'r') as f:
        saved_pw = f.read().strip()
    return saved_pw == hash_password(input_pw)

# menyimpan histori folder yang dikunci
def save_history(folder_path):
    with open(HISTORY_FILE, 'a') as f:
        f.write(folder_path + "\n")

# menampilkan histori folder
def show_history():
    if not os.path.exists(HISTORY_FILE):
        messagebox.showinfo("History Empty", "No folder has been locked yet.")
        return
    with open(HISTORY_FILE, 'r') as f:
        history = f.read()
    messagebox.showinfo("History Folder", history)

# Zip folder dengan progress
def zip_folder_secure(folder_path, password, progress_callback):
    zip_path = folder_path + ".zip"
    file_list = []

    # Ambil semua file
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, folder_path)
            file_list.append((full_path, arcname))

    total_files = len(file_list)
    if total_files == 0:
        raise Exception("Folder is Empty!")

    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED,
                              encryption=pyzipper.WZ_AES) as zipf:
        zipf.setpassword(password.encode())
        for i, (full_path, arcname) in enumerate(file_list):
            zipf.write(full_path, arcname)
            progress_callback(i + 1, total_files)

    return zip_path

# Unzip folder
def unzip_folder_secure(zip_path, password):
    folder_path = zip_path.replace(".zip", "")
    with pyzipper.AESZipFile(zip_path, 'r') as zipf:
        zipf.setpassword(password.encode())
        zipf.extractall(folder_path)
    os.remove(zip_path)

def select_zip_from_history_gui():
    if not os.path.exists(HISTORY_FILE):
        messagebox.showinfo("Folder History is Empty", "No Folder has been locked yet.")
        return None

    with open(HISTORY_FILE, 'r') as f:
        entries = [line.strip() for line in f if line.strip()]

    zip_entries = [f"{e}.zip" for e in entries if os.path.exists(f"{e}.zip")]

    if not zip_entries:
        messagebox.showinfo("No zip file found!", "No Zip File Found in History Folder")
        return None

    selected = {"value": None}

    def submit_choice():
        selected["value"] = option_menu.get()
        popup.destroy()

    popup = ctk.CTkToplevel()
    popup.title("Select ZIP File")
    popup.geometry("400x150")
    popup.grab_set()  # Fokus ke popup

    label = ctk.CTkLabel(popup, text="Choose ZIP file to change its password:", font=("Arial", 14))
    label.pack(pady=10)

    zip_filenames = [os.path.basename(z) for z in zip_entries]
    option_menu = ctk.CTkOptionMenu(popup, values=zip_filenames)
    option_menu.pack(pady=10)
    option_menu.set(zip_filenames[0])  # default

    button = ctk.CTkButton(popup, text="Select", command=submit_choice)
    button.pack(pady=5)

    popup.wait_window()  # Tunggu sampai window ditutup
    if selected["value"]:
        # Ambil path lengkap dari zip filename
        for z in zip_entries:
            if os.path.basename(z) == selected["value"]:
                return z
    return None

# Ganti Password
def change_password():
    if not os.path.exists(PASSWORD_FILE):
        messagebox.showwarning("Error", "No password saved yet!")
        return

    zip_path = select_zip_from_history_gui()
    if not zip_path:
        return

    old_password = simpledialog.askstring("Old Password", "Enter your old password:", show="*")
    if not old_password:
        return

    temp_folder = zip_path.replace(".zip", "_temp_extract")
    try:
        with pyzipper.AESZipFile(zip_path, 'r') as zipf:
            zipf.setpassword(old_password.encode())
            zipf.extractall(temp_folder)
    except Exception:
        messagebox.showerror("Error", "Wrong old password or damaged zip!")
        return

    new_password = simpledialog.askstring("New Password", "Enter your new password:", show="*")
    if not new_password:
        shutil.rmtree(temp_folder)
        return

    try:
        def dummy_progress(_, __): pass
        new_zip_path = zip_folder_secure(temp_folder, new_password, dummy_progress)

        os.remove(zip_path)
        os.rename(new_zip_path, zip_path)

        save_password(hash_password(new_password))
        messagebox.showinfo("Success", f"Password changed for: {os.path.basename(zip_path)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to change password: {str(e)}")
    finally:
        shutil.rmtree(temp_folder)
        
# Kunci folder
def lock_folder():
    folder = filedialog.askdirectory(mustexist=True, title="Select Folder to Lock")
    if not folder:
        return
    password = simpledialog.askstring("Password", "Enter password to lock:", show="*")
    if not password:
        return

    save_password(hash_password(password))
    save_history(folder)

    progress = ctk.CTkProgressBar(master=root)
    progress.set(0)
    progress.pack(pady=10)

    def update_progress(current, total):
        progress.set(current / total)
        root.update_idletasks()

    try:
        zip_path = zip_folder_secure(folder, password, update_progress)

        confirm = messagebox.askyesno("Confirmation", "Delete original folder?")
        if confirm:
            shutil.rmtree(folder)
            messagebox.showinfo("Success", f"Folder locked and original File deleted.\nFile: {zip_path}")
        else:
            messagebox.showinfo("Success", f"Folder locked.\nFile: {zip_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to lock folder: {str(e)}")
    finally:
        progress.destroy()

# Buka folder
def unlock_folder():
    zip_path = filedialog.askopenfilename(title="Select Locked ZIP File", filetypes=[("ZIP Files", "*.zip")])
    if not zip_path:
        return

    password = simpledialog.askstring("Password", "Enter password to unlock:", show="*")
    if not check_password(password):
        messagebox.showerror("Error", "Wrong password!")
        return

    try:
        unzip_folder_secure(zip_path, password)
        os.remove(PASSWORD_FILE)
        messagebox.showinfo("Success", "Folder unlocked successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to unlock: {str(e)}")

# Pilihan tema warna
def change_theme():
    
    current_mode = ctk.get_appearance_mode()
    if current_mode == "Light":
        ctk.set_appearance_mode("Dark")
        switch_theme.configure(text="Dark Mode")
    else:
        ctk.set_appearance_mode("Light")
        switch_theme.configure(text="Light Mode")
        
# Setup customtkinter
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()

if sys.platform.startswith('win'):
    try:
        root.iconbitmap("icon.ico")
    except Exception as e:
        print("Failed to set window icon:", e)

root.title("Folder Locker STAMPO")
root.geometry("420x450")
root.resizable(False, False)

title = ctk.CTkLabel(root, text="STAMPO LOCKER", font=("Times New Roman", 22))
title.pack(pady=20)

lock_button = ctk.CTkButton(root, text="🔐 Lock Folder", width=300, height=40, command=lock_folder)
lock_button.pack(pady=10)

unlock_button = ctk.CTkButton(root, text="🔓 Open Folder", width=300, height=40, command=unlock_folder)
unlock_button.pack(pady=10)

history_button = ctk.CTkButton(root, text="📜 History", width=300, height=40, command=show_history)
history_button.pack(pady=10)

changepw_button = ctk.CTkButton(root, text="🔑 Change Password", width=300, height=40, command=change_password)
changepw_button.pack(pady=10)



# Switch untuk ubah mode
switch_theme = ctk.CTkSwitch(root, text="Light Mode", command=change_theme)
switch_theme.pack(pady=10)

footer = ctk.CTkLabel(root, text="Made By FRK | Not For Commercial Use", font=("Arial", 10),text_color="blue")
footer.pack(side="bottom", pady=10)

root.mainloop()
