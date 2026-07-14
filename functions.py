"""
functions.py
All logic for the Lock Manager app lives here.
The UI file only imports and calls these functions — it contains no logic itself.
"""

from tkinter import filedialog, messagebox, simpledialog
import json
import os
import ctypes
import win32crypt

APP_DATA_DIR = os.path.join(os.environ["APPDATA"], "LockManager")
os.makedirs(APP_DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(APP_DATA_DIR, "locked_items.json")
PASSWORD_FILE = os.path.join(APP_DATA_DIR, "password.dat")

# Holds all locked items: [{"path": str, "type": "folder"/"exe"}, ...]
locked_items = []

# ---------------- Load the C DLL once when this module starts ----------------
lock_tool = ctypes.CDLL("./lock_tool.dll")

lock_tool.lock_path.argtypes = [ctypes.c_char_p]
lock_tool.lock_path.restype = ctypes.c_int

lock_tool.unlock_path.argtypes = [ctypes.c_char_p]
lock_tool.unlock_path.restype = ctypes.c_int


def lock_path_c(path):
    lock_tool.lock_path(path.encode("utf-8"))


def unlock_path_c(path):
    lock_tool.unlock_path(path.encode("utf-8"))


# ---------------- Storage: locked items list (JSON) ----------------

def save_locked_items():
    """Save the current locked_items list to a JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(locked_items, f, indent=2)


def load_locked_items():
    """Load locked_items from the JSON file, if it exists."""
    global locked_items
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            locked_items = json.load(f)
    return locked_items


# ---------------- Password (DPAPI encrypted) ----------------

def has_password():
    return os.path.exists(PASSWORD_FILE)


def set_password(password):
    """Encrypt and save the password using Windows DPAPI."""
    encrypted = win32crypt.CryptProtectData(password.encode(), None, None, None, None, 0)
    with open(PASSWORD_FILE, "wb") as f:
        f.write(encrypted)


def check_password(entered_password):
    """Decrypt the saved password and compare it to what was entered."""
    if not has_password():
        return False
    try:
        with open(PASSWORD_FILE, "rb") as f:
            encrypted = f.read()
        decrypted = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)
        saved_password = decrypted[1].decode()
        return entered_password == saved_password
    except Exception:
        return False


def reset_password():
    """Ask for a new password (twice, to confirm) and save it."""
    new_pass = simpledialog.askstring("Set Password", "Enter new password:", show="*")
    if not new_pass:
        return
    confirm = simpledialog.askstring("Confirm Password", "Re-enter password:", show="*")
    if new_pass != confirm:
        messagebox.showerror("Error", "Passwords do not match.")
        return
    set_password(new_pass)
    messagebox.showinfo("Password Set", "Password has been saved.")


def setup_password_first_run():
    """
    Called once when the app starts, before the main window is usable.
    Forces the user to set a password if one doesn't exist yet.
    Returns True if a password now exists, False if the user cancelled.
    """
    if has_password():
        return True

    messagebox.showinfo(
        "Welcome",
        "No password has been set yet.\nPlease create one now to use Lock Manager."
    )

    while not has_password():
        new_pass = simpledialog.askstring("Create Password", "Enter a new password:", show="*")
        if not new_pass:
            if messagebox.askyesno("Cancel Setup", "No password set. Exit the app?"):
                return False
            continue

        confirm = simpledialog.askstring("Confirm Password", "Re-enter password:", show="*")
        if new_pass != confirm:
            messagebox.showerror("Error", "Passwords do not match. Try again.")
            continue

        set_password(new_pass)
        messagebox.showinfo("Password Set", "Your password has been saved.")

    return True


# ---------------- Button-facing functions (called from ui.py) ----------------

import threading


def lock_folder(add_item_callback):
    if not has_password():
        messagebox.showwarning("No Password Set", "Please set a password first (Reset Password).")
        return

    path = filedialog.askdirectory(title="Select folder to lock")
    if not path:
        return
    if any(item["path"] == path for item in locked_items):
        messagebox.showinfo("Lock Folder", "This folder is already locked.")
        return

    def do_lock():
        lock_path_c(path)
        item = {"path": path, "type": "folder"}
        locked_items.append(item)
        save_locked_items()
        add_item_callback(item)
        print("Locked folder:", path)

    threading.Thread(target=do_lock, daemon=True).start()


def lock_exe(add_item_callback):
    """Open a file picker (exe), lock it via the C DLL, and add it to the locked list."""
    if not has_password():
        messagebox.showwarning("No Password Set", "Please set a password first (Reset Password).")
        return

    path = filedialog.askopenfilename(
        title="Select exe to lock",
        filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
    )
    if not path:
        return
    if any(item["path"] == path for item in locked_items):
        messagebox.showinfo("Lock Exe", "This exe is already locked.")
        return

    def do_lock():
        lock_path_c(path)
        item = {"path": path, "type": "exe"}
        locked_items.append(item)
        save_locked_items()
        add_item_callback(item)
        print("Locked exe:", path)

    threading.Thread(target=do_lock, daemon=True).start()


def unlock_selected(get_selected_callback, remove_items_callback):
    """Ask for password, then unlock (via the C DLL) whichever items are checked in the UI."""
    selected = get_selected_callback()
    if not selected:
        messagebox.showinfo("Unlock", "Select at least one folder or exe to unlock.")
        return

    if not has_password():
        messagebox.showwarning("No Password Set", "Please set a password first (Reset Password).")
        return

    entered = simpledialog.askstring("Password Required", "Enter password to unlock:", show="*")
    if not entered:
        return
    if not check_password(entered):
        messagebox.showerror("Unlock", "Incorrect password.")
        return

    names = "\n".join(item["path"] for item in selected)
    confirm = messagebox.askyesno("Unlock", f"Unlock these items?\n\n{names}")
    if not confirm:
        return

    def do_unlock():
        for item in selected:
            unlock_path_c(item["path"])
            print("Unlocked:", item["path"])
            if item in locked_items:
                locked_items.remove(item)
        save_locked_items()
        remove_items_callback(selected)

    threading.Thread(target=do_unlock, daemon=True).start()


def lock_all_on_startup():
    """Called once when the app starts — re-locks every saved item via the C DLL."""
    for item in locked_items:
        lock_path_c(item["path"])
       