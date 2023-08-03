import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QListWidget, QLabel, QMenu, QAction, QMessageBox, QFileDialog, QInputDialog, QLineEdit, QDialog, QCheckBox, QScrollArea, QGridLayout
from PyQt5.QtGui import QImage, QPixmap
import fitz  # Import thư viện PyMuPDF (fitz)
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

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
                padding: 10px;
                border: none;
                border-radius: 5px;
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
            QScrollArea {
                background-color: #ffffff;
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

        file_path = self.selected_files[0]  # Get the first selected file
        input_pdf = PdfReader(file_path)
        num_pages = len(input_pdf.pages)

        if num_pages == 1:
            QMessageBox.warning(self, "Warning", "The selected PDF has only one page.")
            return

        dialog = PDFPreviewDialog(file_path, num_pages)
        if dialog.exec_():
            pages_to_split = dialog.get_selected_pages()

            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if not output_dir:
                return

            for i in pages_to_split:
                output_pdf = PdfWriter()
                output_pdf.add_page(input_pdf.pages[i])

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

class PDFPreviewDialog(QDialog):
    def __init__(self, pdf_file, num_pages):
        super().__init__()
        self.setWindowTitle("Preview PDF")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.pdf_document = fitz.open(pdf_file)  # Mở PDF bằng fitz
        self.num_pages = num_pages
        self.selected_pages = []

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.pages_widget = QWidget()
        scroll_area.setWidget(self.pages_widget)

        self.pages_layout = QGridLayout(self.pages_widget)
        self.pages_layout.setSpacing(10)
        self.pages_layout.setContentsMargins(10, 10, 10, 10)

        self.pages_to_show = 2
        self.current_page_index = 0

        self.show_pages()

        self.prev_button = QPushButton("Previous", self)
        self.prev_button.clicked.connect(self.show_previous_pages)

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.show_next_pages)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        layout.addLayout(button_layout)

        self.split_button = QPushButton("Split", self)
        self.split_button.clicked.connect(self.split_pages)
        layout.addWidget(self.split_button)

    def show_pages(self):
        self.clear_checkboxes()
        for i in range(self.current_page_index, min(self.current_page_index + self.pages_to_show, self.num_pages)):
            page = self.pdf_document.load_page(i)
            pixmap = self.convert_to_pixmap(page)
            image_label = QLabel(self)
            image_label.setPixmap(pixmap)
            self.pages_layout.addWidget(image_label, 0, i - self.current_page_index)

            checkbox = QCheckBox(f"Page {i + 1}")
            checkbox.stateChanged.connect(self.checkbox_state_changed)
            checkbox.setProperty("page_index", i)
            self.pages_layout.addWidget(checkbox, 1, i - self.current_page_index)

    def clear_checkboxes(self):
        for i in reversed(range(self.pages_layout.count())):
            item = self.pages_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def convert_to_pixmap(self, page):
        image = page.get_pixmap()
        height, width = image.height, image.width
        bytes_per_line = 3 * width
        return QPixmap.fromImage(QImage(image.samples, width, height, bytes_per_line, QImage.Format_RGB888))

    def show_previous_pages(self):
        if self.current_page_index >= self.pages_to_show:
            self.current_page_index -= self.pages_to_show
            self.show_pages()

    def show_next_pages(self):
        if self.current_page_index + self.pages_to_show < self.num_pages:
            self.current_page_index += self.pages_to_show
            self.show_pages()

    def checkbox_state_changed(self, state):
        checkbox = self.sender()
        page_index = checkbox.property("page_index")
        if state == 2:
            self.selected_pages.append(page_index)
        elif state == 0:
            self.selected_pages.remove(page_index)

    def split_pages(self):
        self.accept()

    def get_selected_pages(self):
        return self.selected_pages

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFMergerApp()
    window.show()
    sys.exit(app.exec_())
