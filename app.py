import PyPDF2
import os
from tkinter import Tk, filedialog, Listbox, Button, Label, Scrollbar, END

selected_files = []

def merge_pdfs(output_filename, *input_filenames):
    pdf_merger = PyPDF2.PdfMerger()
    
    for filename in input_filenames:
        with open(filename, 'rb') as pdf_file:
            pdf_merger.append(pdf_file)
    
    with open(output_filename, 'wb') as output_file:
        pdf_merger.write(output_file)

def select_files():
    global selected_files
    selected_files = filedialog.askopenfilenames(title="Chọn các file PDF cần gộp", filetypes=[("PDF Files", "*.pdf")])
    if selected_files:
        show_selected_files()

def show_selected_files():
    listbox.delete(0, END)
    for path in selected_files:
        listbox.insert(END, path)

def export_files():
    if not selected_files:
        print("Không có file nào được chọn. Kết thúc chương trình.")
        return

    with filedialog.asksaveasfile(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]) as temp_file:
        output_filename = temp_file.name
        merge_pdfs(output_filename, *selected_files)
        print(f"Gộp các file thành công! Kết quả được lưu vào file '{output_filename}'.")

def print_pdf():
    if not selected_files:
        print("Không có file nào được chọn. Kết thúc chương trình.")
        return

    with filedialog.asksaveasfile(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]) as temp_file:
        output_filename = temp_file.name
        merge_pdfs(output_filename, *selected_files)
        os.startfile(output_filename, "print")

def main():
    root = Tk()
    root.title("Ứng dụng gộp PDF")

    label = Label(root, text="Các file đã chọn:")
    label.pack()

    listbox = Listbox(root, selectmode="multiple", height=10, width=50)
    listbox.pack(fill="both", expand=True)

    scrollbar = Scrollbar(root)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    select_button = Button(root, text="Select", command=lambda: select_files())
    select_button.pack()

    export_button = Button(root, text="Export", command=lambda: export_files())
    export_button.pack()

    print_button = Button(root, text="Print", command=lambda: print_pdf())
    print_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
