#!/usr/bin/env python3
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

def search_flatpak(query):
    url = "https://flathub.org/api/v1/apps"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"Debug: Received data: {data}")  # Debug print
            return data
        else:
            messagebox.showerror("Error", f"Failed to fetch data from Flathub: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to connect to Flathub: {e}")
        return []

def filter_apps(data, query):
    query_lower = query.lower()
    filtered_apps = [
        app for app in data 
        if query_lower in app.get('name', '').lower() or query_lower in app.get('summary', '').lower()
    ]
    return filtered_apps

def install_flatpak(app_id):
    try:
        result = subprocess.run(["flatpak", "install", "-y", "flathub", app_id], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            messagebox.showinfo("Success", f"Successfully installed {app_id}")
        else:
            messagebox.showerror("Error", f"Failed to install {app_id}: {result.stderr}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to install {app_id}: {e}")

def on_search():
    query = search_entry.get().strip()
    if query:
        results = search_flatpak(query)
        listbox.delete(0, tk.END)
        filtered_results = filter_apps(results, query)
        if filtered_results:
            for app in filtered_results:
                app_name = app.get('name', 'Unknown App')
                app_summary = app.get('summary', 'No summary available')
                app_id = app.get('flatpakAppId', 'Unknown ID')
                listbox.insert(tk.END, f"{app_name} - {app_summary} - {app_id}")
        else:
            messagebox.showinfo("No Results", f"No results found for '{query}'")
    else:
        messagebox.showwarning("Empty Query", "Please enter a search query")

def on_install():
    selection = listbox.curselection()
    if selection:
        app_id = listbox.get(selection[0]).split(' - ')[-1]
        install_flatpak(app_id)
    else:
        messagebox.showwarning("Selection Error", "No application selected")

app = tk.Tk()
app.title("FlatFinder")

# Set window size
app.geometry("600x400")

# Add padding
padding = {'padx': 10, 'pady': 10}

# Search label and entry
search_label = ttk.Label(app, text="Search for Flatpak apps:")
search_label.pack(**padding)

search_entry = ttk.Entry(app)
search_entry.pack(fill=tk.X, **padding)

# Search button
search_button = ttk.Button(app, text="Search", command=on_search)
search_button.pack(**padding)

# Listbox with scrollbar
frame = ttk.Frame(app)
frame.pack(fill=tk.BOTH, expand=True, **padding)

listbox = tk.Listbox(frame, selectmode=tk.SINGLE)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox.config(yscrollcommand=scrollbar.set)

# Install button
install_button = ttk.Button(app, text="Install", command=on_install)
install_button.pack(**padding)

app.mainloop()
