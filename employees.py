import os
import sys
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from styles import STYLE_SHEET

# 1. دالة تحديد المسار للملفات الداخلية (مثل الصور المدمجة)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 2. دالة تحديد مسار قاعدة البيانات (لتكون بجانب ملف الـ EXE دائماً)
def get_db_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), "attendance.db")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")

class EmployeesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إدارة الموظفين - مؤسسة وطن")
        self.resize(950, 700)
        self.setStyleSheet(STYLE_SHEET)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. الترويسة (العنوان + زر الرجوع)
        header_layout = QHBoxLayout()
        
        btn_back = QPushButton("🔙 رجوع")
        btn_back.setFixedWidth(100)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #636e72;
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d3436;
            }
        """)
        btn_back.clicked.connect(self.close) 
        
        title = QLabel("👥 سجل وإدارة الموظفين")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2d3436; margin-right: 15px;")
        
        header_layout.addWidget(btn_back)
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. شريط البحث والعمليات
        action_layout = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 ابحث عن موظف بالاسم أو الرقم...")
        self.search_box.setFixedWidth(300)
        self.search_box.textChanged.connect(self.search_data)
        
        btn_add = QPushButton("➕ إضافة موظف")
        btn_add.setObjectName("PrimaryBtn")
        btn_add.clicked.connect(self.add_employee)

        btn_edit = QPushButton("✏️ تعديل")
        btn_edit.setFixedWidth(100)
        btn_edit.setStyleSheet("background-color: #f1c40f; color: white; font-weight: bold; border-radius: 8px; padding: 10px;")
        btn_edit.clicked.connect(self.edit_employee)

        btn_delete = QPushButton("🗑️ حذف")
        btn_delete.setObjectName("DangerBtn")
        btn_delete.setFixedWidth(100)
        btn_delete.clicked.connect(self.delete_employee)

        action_layout.addWidget(self.search_box)
        action_layout.addStretch()
        action_layout.addWidget(btn_add)
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        layout.addLayout(action_layout)

        # 3. الجدول
        self.table = QTableWidget()
        self.table.setColumnCount(2) 
        self.table.setHorizontalHeaderLabels(["رقم البصمة (ID)", "اسم الموظف الكامل"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        try:
            # تم التعديل هنا لاستخدام get_db_path()
            conn = sqlite3.connect(get_db_path())
            query = "SELECT finger_id, name FROM employees ORDER BY finger_id ASC"
            data = conn.execute(query).fetchall()
            self.table.setRowCount(len(data))
            for i, row in enumerate(data):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل تحميل البيانات: {str(e)}")

    def add_employee(self):
        name, ok1 = QInputDialog.getText(self, "إضافة موظف", "اسم الموظف:")
        f_id, ok2 = QInputDialog.getInt(self, "إضافة موظف", "رقم البصمة في الجهاز:")
        
        if ok1 and ok2 and name:
            try:
                # تم التعديل هنا لاستخدام get_db_path()
                conn = sqlite3.connect(get_db_path())
                conn.execute("INSERT INTO employees (finger_id, name) VALUES (?, ?)", (f_id, name))
                conn.commit()
                conn.close()
                self.load_data()
                QMessageBox.information(self, "نجاح", "تمت إضافة الموظف بنجاح")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"رقم البصمة موجود مسبقاً أو هناك مشكلة: {str(e)}")

    def edit_employee(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى تحديد موظف من الجدول أولاً!")
            return

        old_id = self.table.item(current_row, 0).text()
        old_name = self.table.item(current_row, 1).text()

        new_name, ok = QInputDialog.getText(self, "تعديل بيانات", "تعديل الاسم:", text=old_name)
        if ok and new_name:
            try:
                # تم التعديل هنا لاستخدام get_db_path()
                conn = sqlite3.connect(get_db_path())
                conn.execute("UPDATE employees SET name = ? WHERE finger_id = ?", (new_name, old_id))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل التعديل: {str(e)}")

    def delete_employee(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "يرجى تحديد موظف لحذفه!")
            return

        emp_id = self.table.item(current_row, 0).text()
        confirm = QMessageBox.question(self, "تأكيد الحذف", f"هل أنت متأكد من حذف الموظف صاحب البصمة رقم {emp_id}؟",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            try:
                # تم التعديل هنا لاستخدام get_db_path()
                conn = sqlite3.connect(get_db_path())
                conn.execute("DELETE FROM employees WHERE finger_id = ?", (emp_id,))
                conn.commit()
                conn.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل الحذف: {str(e)}")

    def search_data(self, text):
        for i in range(self.table.rowCount()):
            match = False
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(i, not match)