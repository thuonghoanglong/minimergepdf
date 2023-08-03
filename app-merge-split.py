import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QListWidget, QLabel, QMenu, QAction, QMessageBox, QFileDialog
from PyPDF2 import PdfMerger, PdfFileReader, PdfFileWriter

class PDFMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.selected_files = []
        self.sort_order = True

    def init_ui(self):
        self.setWindowTitle("PDF Tool")
        self.setGeometry(100, 100, 800, 600)  # Đổi kích thước cửa sổ

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        self.select_button = QPushButton("Select PDFs", self)
        self.select_button.clicked.connect(self.select_files)

        self.sort_button = QPushButton("Sort", self)
        self.sort_button.clicked.connect(self.sort_files)

        self.export_button = QPushButton("Merge PDF", self)
        self.export_button.clicked.connect(self.export_files)

        self.split_button = QPushButton("Split PDF", self)
        self.split_button.clicked.connect(self.split_file)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.sort_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.split_button)

        layout.addLayout(button_layout)

        self.listbox = QListWidget(self)
        layout.addWidget(self.listbox)

        self.count_label = QLabel("Selected PDFs: 0", self)
        layout.addWidget(self.count_label)

        # Context menu for right-click options
        self.context_menu = QMenu(self)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_file)
        self.context_menu.addAction(delete_action)

        delete_all_action = QAction("Delete All", self)
        delete_all_action.triggered.connect(self.delete_all_files)
        self.context_menu.addAction(delete_all_action)

        self.listbox.setContextMenuPolicy(3)  # Set context menu policy to CustomContextMenu
        self.listbox.customContextMenuRequested.connect(self.show_context_menu)

        self.update_ui()

    def update_ui(self):
        style_sheet = """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QListWidget {
                background-color: #f0f0f0;
                border: none;
                padding: 10px;
            }
            QLabel {
                padding: 10px;
            }
            QMenu {
                background-color: #f0f0f0;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #888;
            }
        """
        self.setStyleSheet(style_sheet)

    def select_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("PDF Files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            self.listbox.clear()
            self.selected_files = file_paths
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                self.listbox.addItem(file_name)
            self.update_selected_count()

    def sort_files(self):
        self.listbox.clear()
        if self.sort_order:
            self.selected_files.sort(key=lambda x: os.path.basename(x))
        else:
            self.selected_files.sort(key=lambda x: os.path.basename(x), reverse=True)
        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            self.listbox.addItem(file_name)
        self.sort_order = not self.sort_order

    def export_files(self):
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "Please select PDF files first.")
            return
    
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if not output_file:
            return
    
        merger = PdfMerger()
        for file_path in self.selected_files:
            merger.append(file_path)
    
        with open(output_file, "wb") as output_pdf:
            merger.write(output_pdf)

        QMessageBox.information(self, "Done", "PDFs have been merged successfully!")

    def split_file(self):
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "Please select a PDF file to split.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF to Split", "", "PDF Files (*.pdf)")
        if not file_path:
            return

        input_pdf = PdfFileReader(file_path)
        num_pages = input_pdf.getNumPages()

        if num_pages == 1:
            QMessageBox.warning(self, "Warning", "The selected PDF has only one page.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        for i in range(num_pages):
            output_pdf = PdfFileWriter()
            output_pdf.addPage(input_pdf.getPage(i))

            output_file = os.path.join(output_dir, f"page_{i + 1}.pdf")
            with open(output_file, "wb") as f:
                output_pdf.write(f)

        QMessageBox.information(self, "Done", "PDF has been split successfully!")

    def update_selected_count(self):
        self.count_label.setText(f"Selected PDFs: {len(self.selected_files)}")

    def delete_selected_file(self):
        selected_indices = self.listbox.selectedIndexes()
        if not selected_indices:
            QMessageBox.warning(self, "Warning", "Please select a PDF file to delete.")
            return
    
        for index in selected_indices:
            self.selected_files.pop(index.row())
            self.listbox.takeItem(index.row())
        self.update_selected_count()

    def delete_all_files(self):
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "The list is already empty.")
            return
    
        answer = QMessageBox.question(self, "Delete All Files", "Are you sure you want to delete all files?", QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            self.selected_files.clear()
            self.listbox.clear()
            self.update_selected_count()

    def show_context_menu(self, position):
        selected_items = self.listbox.selectedItems()
        if not selected_items:
            return

        self.context_menu.exec_(self.listbox.viewport().mapToGlobal(position))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec_())
