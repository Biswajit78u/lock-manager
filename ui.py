import customtkinter as ctk
import functions

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Keeps track of the checkbox variable + row widget tied to each locked item
item_rows = []  # list of dicts: 


def add_item_to_list(item):
    """Add a single new locked item as a row with a checkbox in the UI."""
    clear_placeholder_if_any()

    var = ctk.BooleanVar()
    row = ctk.CTkFrame(list_container, fg_color="transparent")
    row.pack(fill="x", padx=10, pady=5)

    cb = ctk.CTkCheckBox(row, text="", variable=var, width=20)
    cb.pack(side="left", padx=(5, 10))

    icon = "📁" if item["type"] == "folder" else "⚙️"
    label = ctk.CTkLabel(row, text=f"{icon}  {item['path']}", font=("Segoe UI", 12), anchor="w")
    label.pack(side="left", fill="x", expand=True)

    item_rows.append({"item": item, "var": var, "row": row})


def get_selected_items():
    """Return the list of item dicts that are currently checked."""
    return [entry["item"] for entry in item_rows if entry["var"].get()]


def remove_items_from_list(items_to_remove):
    """Remove the given items' rows from the UI and show placeholder if empty."""
    for entry in list(item_rows):
        if entry["item"] in items_to_remove:
            entry["row"].destroy()
            item_rows.remove(entry)
    if not item_rows:
        show_placeholder()


def clear_placeholder_if_any():
    global placeholder_label
    if placeholder_label is not None:
        placeholder_label.destroy()
        placeholder_label = None


def show_placeholder():
    global placeholder_label
    placeholder_label = ctk.CTkLabel(
        list_container,
        text="all lock exe and folder\n\nuser must select folder and exe for unlock",
        font=("Segoe UI", 13), text_color="gray"
    )
    placeholder_label.pack(pady=40)


def select_all():
    for entry in item_rows:
        entry["var"].set(True)


def clear_selection():
    for entry in item_rows:
        entry["var"].set(False)


# ---------------- Button click handlers (thin wrappers calling functions.py) ----------------

def on_lock_folder():
    functions.lock_folder(add_item_to_list)


def on_lock_exe():
    functions.lock_exe(add_item_to_list)


def on_unlock():
    functions.unlock_selected(get_selected_items, remove_items_from_list)


def on_reset_password():
    functions.reset_password()


# ---------------- Window ----------------
app = ctk.CTk()
app.geometry("1x1+0+0")  # shrink to a tiny, barely visible window instead of hiding it
app.update()
if not functions.setup_password_first_run():
    app.destroy()
    exit()

app.title("Lock Manager")
app.geometry("950x650")

# Top bar
top_bar = ctk.CTkFrame(app, fg_color="transparent")
top_bar.pack(fill="x", padx=25, pady=(20, 10))

title_label = ctk.CTkLabel(top_bar, text="Lock Manager", font=("Segoe UI", 20, "bold"))
title_label.pack(side="left")

reset_btn = ctk.CTkButton(
    top_bar, text="Reset Password", width=140, height=32,
    fg_color="transparent", border_width=1, command=on_reset_password
)
reset_btn.pack(side="right")

# Button row
btn_row = ctk.CTkFrame(app, fg_color="transparent")
btn_row.pack(fill="x", padx=25, pady=(10, 15))

lock_btn = ctk.CTkButton(
    btn_row, text="Lock Folder", height=45, font=("Segoe UI", 13), command=on_lock_folder
)
lock_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

lock_exe_btn = ctk.CTkButton(
    btn_row, text="Lock Exe", height=45, font=("Segoe UI", 13), command=on_lock_exe
)
lock_exe_btn.pack(side="left", expand=True, fill="x", padx=10)

unlock_btn = ctk.CTkButton(
    btn_row, text="Unlock Selected", height=45, font=("Segoe UI", 14, "bold"),
    fg_color="#2fa572", hover_color="#238a5c", command=on_unlock
)
unlock_btn.pack(side="left", expand=True, fill="x", padx=(10, 0))

# Select all / clear row
select_row = ctk.CTkFrame(app, fg_color="transparent")
select_row.pack(fill="x", padx=25, pady=(0, 10))

select_all_btn = ctk.CTkButton(
    select_row, text="Select All", width=100, height=28,
    fg_color="transparent", border_width=1, font=("Segoe UI", 11), command=select_all
)
select_all_btn.pack(side="left", padx=(0, 10))

clear_btn = ctk.CTkButton(
    select_row, text="Clear Selection", width=120, height=28,
    fg_color="transparent", border_width=1, font=("Segoe UI", 11), command=clear_selection
)
clear_btn.pack(side="left")

# Content box (scrollable list of locked items)
list_container = ctk.CTkScrollableFrame(app, corner_radius=12)
list_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))

placeholder_label = None
show_placeholder()

# ---------------- Load saved items and re-lock them, then start the app ----------------
for item in functions.load_locked_items():
    add_item_to_list(item)
#functions.lock_all_on_startup()

app.mainloop()
