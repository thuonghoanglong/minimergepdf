import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfMerger

def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    listbox.delete(0, tk.END)
    for file_path in file_paths:
        listbox.insert(tk.END, file_path)

def sort_files():
    items = listbox.get(0, tk.END)
    items.sort()
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)

def export_files():
    output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not output_file:
        return
    
    merger = PdfMerger()
    for item in listbox.get(0, tk.END):
        file_path = item
        merger.append(file_path)
    
    merger.write(output_file)
    merger.close()

    tk.messagebox.showinfo("Done", "PDFs have been merged successfully!")

# Create the main application window
root = tk.Tk()
root.title("PDF Merger")

# Create GUI components
select_button = tk.Button(root, text="Select", command=select_files)
sort_button = tk.Button(root, text="Sort", command=sort_files)
export_button = tk.Button(root, text="Export", command=export_files)
listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=50)

# Grid layout
select_button.grid(row=0, column=0, padx=10, pady=5)
sort_button.grid(row=0, column=1, padx=10, pady=5)
export_button.grid(row=0, column=2, padx=10, pady=5)
listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

# Start the main event loop
root.mainloop()
