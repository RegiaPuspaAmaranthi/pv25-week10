import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget, QFileDialog,
    QMenuBar, QAction, QDialog, QDialogButtonBox, QFormLayout, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class EditJudulDialog(QDialog):
    def __init__(self, current_value):
        super().__init__()
        self.setWindowTitle("Edit Judul")
        self.setFixedSize(300, 100)

        self.input = QLineEdit(current_value)
        layout = QFormLayout()
        layout.addRow("Judul:", self.input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def getData(self):
        return self.input.text()

class EditPengarangDialog(QDialog):
    def __init__(self, current_value):
        super().__init__()
        self.setWindowTitle("Edit Pengarang")
        self.setFixedSize(300, 100)

        self.input = QLineEdit(current_value)
        layout = QFormLayout()
        layout.addRow("Pengarang:", self.input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def getData(self):
        return self.input.text()

class EditTahunDialog(QDialog):
    def __init__(self, current_value):
        super().__init__()
        self.setWindowTitle("Edit Tahun")
        self.setFixedSize(300, 100)

        self.input = QLineEdit(current_value)
        layout = QFormLayout()
        layout.addRow("Tahun:", self.input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def getData(self):
        return self.input.text()

class BookManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku - Regia Puspa Amaranthi (F1D022156)")
        self.resize(600, 600)

        self.conn = sqlite3.connect("books.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                pengarang TEXT,
                tahun INTEGER
            )
        ''')
        self.conn.commit()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Menu
        menubar = QMenuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Simpan", self.save_data)
        file_menu.addAction("Ekspor ke CSV", self.export_csv)
        file_menu.addAction("Keluar", self.close)

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Cari Judul", lambda: self.search_input.setFocus())
        edit_menu.addAction("Hapus Data", self.delete_data)

        layout.setMenuBar(menubar)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_data = QWidget()
        self.tab_export = QWidget()

        self.tabs.addTab(self.tab_data, "Data Buku")
        self.tabs.addTab(self.tab_export, "Ekspor")

        self.initDataTab()
        self.initExportTab()

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.load_data()

    def initDataTab(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.judul_input = QLineEdit()
        self.pengarang_input = QLineEdit()
        self.tahun_input = QLineEdit()
        form_layout.addRow("Judul:", self.judul_input)
        form_layout.addRow("Pengarang:", self.pengarang_input)
        form_layout.addRow("Tahun:", self.tahun_input)

        layout.addLayout(form_layout)

        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setFixedSize(120, 35)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul...")
        self.search_input.textChanged.connect(self.load_data)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.cellChanged.connect(self.update_data)
        self.table.cellDoubleClicked.connect(self.edit_cell_dialog)
        layout.addWidget(self.table)

        self.delete_button = QPushButton("Hapus Data")
        self.delete_button.setFixedSize(120, 35)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.delete_button.clicked.connect(self.delete_data)
        layout.addWidget(self.delete_button)

        self.tab_data.setLayout(layout)

    def initExportTab(self):
        layout = QVBoxLayout()
        self.export_button = QPushButton("Ekspor ke CSV")
        self.export_button.setStyleSheet("background-color: #88D66C")
        self.export_button.clicked.connect(self.export_csv)
        layout.addWidget(self.export_button)
        self.tab_export.setLayout(layout)

    def save_data(self):
        judul = self.judul_input.text().strip()
        pengarang = self.pengarang_input.text().strip()
        tahun = self.tahun_input.text().strip()

        if not (judul and pengarang and tahun.isdigit()):
            QMessageBox.warning(self, "Input Salah", "Pastikan semua data diisi dengan benar.")
            return

        self.cursor.execute(
            "INSERT INTO books (judul, pengarang, tahun) VALUES (?, ?, ?)",
            (judul, pengarang, int(tahun))
        )
        self.conn.commit()
        self.judul_input.clear()
        self.pengarang_input.clear()
        self.tahun_input.clear()
        self.load_data()

    def load_data(self):
        keyword = self.search_input.text().strip()
        query = "SELECT * FROM books"
        if keyword:
            query += " WHERE judul LIKE ?"
            self.cursor.execute(query, (f"%{keyword}%",))
        else:
            self.cursor.execute(query)

        data = self.cursor.fetchall()

        self.table.blockSignals(True)
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                if col_idx == 0:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row_idx, col_idx, item)
        self.table.blockSignals(False)

    def update_data(self, row, col):
        id_item = self.table.item(row, 0)
        if not id_item:
            return
        id_val = int(id_item.text())
        value = self.table.item(row, col).text()
        column = ["id", "judul", "pengarang", "tahun"][col]
        if column == "id":
            return
        self.cursor.execute(f"UPDATE books SET {column} = ? WHERE id = ?", (value, id_val))
        self.conn.commit()

    def delete_data(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Pilih Baris", "Silakan pilih data yang akan dihapus.")
            return

        id_item = self.table.item(selected, 0)
        judul_item = self.table.item(selected, 1) 

        if id_item and judul_item:
            id_val = int(id_item.text())
            judul_buku = judul_item.text()

            self.cursor.execute("DELETE FROM books WHERE id = ?", (id_val,))
            self.conn.commit()
            self.load_data()

            QMessageBox.information(self, "Data Dihapus", f"Buku '{judul_buku}' berhasil dihapus.")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan CSV",
            "file_export.csv",
            "CSV Files (*.csv)"
        )
        if path:
            self.cursor.execute("SELECT * FROM books")
            data = self.cursor.fetchall()
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(data)
            QMessageBox.information(self, "Export Sukses", f"Data berhasil diekspor ke:\n{path}")

    def edit_cell_dialog(self, row, col):
        if col == 0:
            return  # ID tidak diedit
        id_val = int(self.table.item(row, 0).text())
        current_value = self.table.item(row, col).text()

        if col == 1:
            dialog = EditJudulDialog(current_value)
        elif col == 2:
            dialog = EditPengarangDialog(current_value)
        elif col == 3:
            dialog = EditTahunDialog(current_value)
        else:
            return

        if dialog.exec_() == QDialog.Accepted:
            new_value = dialog.getData()
            if col == 3 and not new_value.isdigit():
                QMessageBox.warning(self, "Input Salah", "Tahun harus angka.")
                return

            column = ["id", "judul", "pengarang", "tahun"][col]
            self.cursor.execute(f"UPDATE books SET {column} = ? WHERE id = ?", (new_value, id_val))
            self.conn.commit()
            self.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))  
    window = BookManager()
    window.show()
    sys.exit(app.exec_())
