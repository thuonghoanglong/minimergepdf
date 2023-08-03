import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PyPDF2 import PdfMerger

def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    listbox.delete(0, tk.END)
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        listbox.insert(tk.END, file_name)
        selected_files.append(file_path)
    update_selected_count()

def sort_files():
    global sort_order
    listbox.delete(0, tk.END)
    if sort_order:
        selected_files.sort(key=lambda x: os.path.basename(x))
    else:
        selected_files.sort(key=lambda x: os.path.basename(x), reverse=True)
    for file_path in selected_files:
        file_name = os.path.basename(file_path)
        listbox.insert(tk.END, file_name)
    sort_order = not sort_order

def export_files():
    if not selected_files:
        tk.messagebox.showwarning("Warning", "Please select PDF files first.")
        return
    
    output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not output_file:
        return
    
    merger = PdfMerger()
    for file_path in selected_files:
        merger.append(file_path)
    
    merger.write(output_file)
    merger.close()

    tk.messagebox.showinfo("Done", "PDFs have been merged successfully!")

def update_selected_count():
    count_label.config(text=f"Selected PDFs: {len(selected_files)}")

def delete_selected_file():
    selected_indices = listbox.curselection()
    if not selected_indices:
        tk.messagebox.showwarning("Warning", "Please select a PDF file to delete.")
        return
    
    for index in selected_indices[::-1]:  # Delete from the end to avoid shifting indexes
        selected_files.pop(index)
        listbox.delete(index)
    update_selected_count()

def delete_all_files():
    if not selected_files:
        tk.messagebox.showwarning("Warning", "The list is already empty.")
        return
    
    answer = tk.messagebox.askyesno("Delete All Files", "Are you sure you want to delete all files?")
    if answer:
        selected_files.clear()
        listbox.delete(0, tk.END)
        update_selected_count()

# Create the main application window
root = tk.Tk()
root.title("PDF Merger")

# Create GUI components
select_button = tk.Button(root, text="Select", command=select_files)
sort_button = tk.Button(root, text="Sort", command=sort_files)
export_button = tk.Button(root, text="Export", command=export_files)
listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50)  # Change selectmode to SINGLE
count_label = tk.Label(root, text="Selected PDFs: 0")

# Context menu for right-click options
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Delete", command=delete_selected_file)
context_menu.add_command(label="Delete All", command=delete_all_files)

# Bind context menu to listbox
def show_context_menu(event):
    if listbox.curselection():
        context_menu.post(event.x_root, event.y_root)

listbox.bind("<Button-3>", show_context_menu)

# Grid layout
select_button.grid(row=0, column=0, padx=10, pady=5)
sort_button.grid(row=0, column=1, padx=10, pady=5)
export_button.grid(row=0, column=2, padx=10, pady=5)
listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
count_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

# A list to store selected file paths
selected_files = []

# A variable to keep track of the sort order
sort_order = True

# Start the main event loop
root.mainloop()
