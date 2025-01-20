import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import keyboard
import subprocess
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Icon

# Dictionary to store the configuration of folders and hotkeys
folders_config = {}

# Load configuration from a JSON file if it exists
if os.path.exists('Quick_Folder_Finder.json'):
    with open('Quick_Folder_Finder.json', 'r') as f:
        folders_config = json.load(f)

def save_configuration():
    """Save the configuration of folders and keys to a JSON file."""
    with open('Quick_Folder_Finder.json', 'w') as f:
        json.dump(folders_config, f)

def open_folder(folder_path):
    """Open a folder using the provided path."""
    try:
        os.startfile(folder_path)  # This will open the folder in the default file explorer
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open {folder_path}: {e}")

def select_folder():
    """Open a dialog window to select a folder."""
    path = filedialog.askdirectory(title="Select a Folder")
    if path:
        add_folder_space(path)

def add_folder_space(path="", key=""):
    """Add a new space for a folder in the list."""
    folder_frame = tk.Frame(window, bg='#f0f0f0')
    folder_frame.pack(pady=5)

    path_entry = tk.Entry(folder_frame, width=50, font=('Arial', 12))
    path_entry.pack(side=tk.LEFT, padx=5)
    path_entry.insert(0, path)

    key_entry = tk.Entry(folder_frame, width=20, font=('Arial', 12))
    key_entry.pack(side=tk.LEFT, padx=5)
    key_entry.insert(0, key)  # Pre-fill the field with the already assigned key

    assign_button = tk.Button(folder_frame, text="Assign Key", font=('Arial', 12),
                               command=lambda: assign_key(path_entry.get(), key_entry.get()))
    assign_button.pack(side=tk.LEFT, padx=5)

    delete_button = tk.Button(folder_frame, text="Delete", font=('Arial', 12),
                              command=lambda: delete_folder(folder_frame, key_entry.get()))
    delete_button.pack(side=tk.LEFT, padx=5)

def assign_key(path, key):
    """Assign a hotkey to the selected folder."""
    key = key.strip().lower()

    if path and key:
        folders_config[key] = path
        save_configuration()
        keyboard.add_hotkey(key, lambda p=path: open_folder(p))
        status_label.config(text=f"Key '{key}' assigned to {os.path.basename(path)}", fg="green")
    else:
        status_label.config(text="Please enter a valid path and key", fg="red")

def delete_folder(frame, key):
    """Delete a folder and its hotkey."""
    key = key.strip().lower()
    if key in folders_config:
        del folders_config[key]
        save_configuration()
        keyboard.remove_hotkey(key)

    frame.destroy()  # Remove the frame from the UI
    status_label.config(text=f"Folder and key '{key}' removed", fg="blue")

def minimize():
    """Minimize the window and put the icon in the system tray."""
    window.withdraw()  # Hide the main window
    show_icon_tray()

def show_icon_tray():
    """Show the icon in the system tray."""
    icon = Icon("folder_icon", create_image())
    icon.menu = pystray.Menu(
        MenuItem("Open", lambda: show_window(icon)),
        MenuItem("Exit", lambda: exit_app(icon))
    )
    icon.run(setup)

def setup(icon):
    icon.visible = True

def show_window(icon):
    """Restore the main window and allow it to interact."""
    icon.stop()  # Remove the icon from the system tray
    window.deiconify()  # Restore the window
    window.focus_force()  # Ensure the window has focus

def exit_app(icon):
    """Exit the application."""
    icon.stop()
    save_configuration()
    window.quit()

def create_image():
    """Create a simple icon."""
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill=(0, 128, 255))
    return image

def start_key_listening():
    """Start listening to key configurations."""
    for key, path in folders_config.items():
        keyboard.add_hotkey(key, lambda p=path: open_folder(p))

# Create the main window
window = tk.Tk()
window.title("Quick Folder Finder - Hotkey Management for Folders")
window.geometry("900x400")  # Widen the window
window.configure(bg='#e0e0e0')  # Change background color

# Handle the close and minimize behavior
window.protocol("WM_DELETE_WINDOW", lambda: (save_configuration(), window.destroy()))  # Save and close on X
window.bind("<Unmap>", lambda event: minimize() if window.state() == "iconic" else None)  # Minimize on "Minimize"

# Create interface elements
path_label = tk.Label(window, text="Select a folder:", bg='#e0e0e0', font=('Arial', 12))
path_label.pack(pady=5)

select_button = tk.Button(window, text="Select Folder", command=select_folder,
                          font=('Arial', 12), bg='#5cb85c', fg='white')
select_button.pack(pady=5)

# Adding a brief explanation on how to use the software
explanation_label = tk.Label(window, text="Select a folder and assign a hotkey.\nEx: a, alt+b, ctrl+c, shift+d.",
                              bg='#e0e0e0', font=('Arial', 10))
explanation_label.pack(pady=5)

status_label = tk.Label(window, text="", bg='#e0e0e0', font=('Arial', 12))
status_label.pack(pady=5)

# Add spaces for already saved folders
for key, path in folders_config.items():
    add_folder_space(path, key)

# Start listening to key configurations
start_key_listening()

# Start the interface
window.mainloop()
