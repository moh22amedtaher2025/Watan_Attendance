import sqlite3
import os
import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import *
from zk import ZK 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_db_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), "attendance.db")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")

class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مزامنة البصمات - مؤسسة وطن")
        self.resize(1150, 750)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تحميل الإعدادات أولاً لتسمية الأعمدة
        self.config = self.load_settings_only()
        
        self.setStyleSheet("""
            QWidget { background-color: #f1f2f6; font-family: 'Segoe UI'; }
            QPushButton { border-radius: 6px; font-weight: bold; font-size: 14px; }
            QTableWidget { background-color: white; border: 1px solid #dcdde1; }
            QHeaderView::section { background-color: #2f3640; color: white; font-weight: bold; padding: 5px; }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header UI
        header = QFrame()
        header.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
        h_lay = QHBoxLayout(header)
        
        self.btn_back = QPushButton("🔙 رجوع")
        self.btn_back.setFixedSize(120, 40)
        self.btn_back.setStyleSheet("background-color: #7f8c8d; color: white;")
        self.btn_back.clicked.connect(self.close)
        
        self.status_lbl = QLabel("جهاز البصمة: جاهز للإتصال")
        self.status_lbl.setStyleSheet("font-size: 16px; color: #2c3e50; font-weight: bold;")

        self.btn_refresh = QPushButton("🔄 تحديث الجدول")
        self.btn_refresh.setFixedSize(150, 40)
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white;")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_sync = QPushButton("📥 سحب بيانات الجهاز")
        self.btn_sync.setFixedSize(180, 40)
        self.btn_sync.setStyleSheet("background-color: #e67e22; color: white;")
        self.btn_sync.clicked.connect(self.sync_from_device)

        self.btn_clear = QPushButton("🧹 تنظيف الجهاز")
        self.btn_clear.setFixedSize(150, 40)
        self.btn_clear.setStyleSheet("background-color: #c0392b; color: white;")
        self.btn_clear.clicked.connect(self.clear_device_logs)
        
        h_lay.addWidget(self.btn_back)
        h_lay.addStretch()
        h_lay.addWidget(self.status_lbl)
        h_lay.addStretch()
        h_lay.addWidget(self.btn_refresh) 
        h_lay.addWidget(self.btn_sync)
        h_lay.addWidget(self.btn_clear) 
        layout.addWidget(header)

        # Table Section
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.update_table_headers()
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_settings_only(self):
        settings_file = resource_path("settings_data.json")
        default_config = {
            "ip": "192.168.1.205",
            "in_limit_1": "08:00", "out_limit_1": "14:00",
            "in_limit_2": "20:00", "out_limit_2": "01:00"
        }
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    default_config.update(data)
            except: pass
        return default_config

    def update_table_headers(self):
        h1 = f"دخول ({self.config.get('in_limit_1', '08:00')})"
        o1 = f"خروج ({self.config.get('out_limit_1', '14:00')})"
        h2 = f"دخول ({self.config.get('in_limit_2', '20:00')})"
        o2 = f"خروج ({self.config.get('out_limit_2', '01:00')})"
        
        self.table.setHorizontalHeaderLabels([
            "ID البصمة", "اسم الموظف", "التاريخ", h1, o1, h2, o2
        ])

    def is_time_between(self, target_str, start_str, end_str):
        fmt = '%H:%M'
        try:
            target = datetime.strptime(target_str, fmt).time()
            start = datetime.strptime(start_str, fmt).time()
            end = datetime.strptime(end_str, fmt).time()
            
            if start <= end:
                return start <= target <= end
            else: # دوام ليلي عابر لمنتصف الليل
                return target >= start or target <= end
        except: return False

    def sync_from_device(self):
        self.config = self.load_settings_only()
        self.update_table_headers()
        
        zk = ZK(self.config['ip'], port=4370, timeout=10)
        conn = None

        try:
            self.status_lbl.setText("⏳ جاري الإتصال بالجهاز...")
            QApplication.processEvents()
            
            conn = zk.connect()
            conn.disable_device()
            records = conn.get_attendance()
            
            db = sqlite3.connect(get_db_path())
            cursor = db.cursor()
            
            for record in records:
                u_id = str(record.user_id)
                d_str = record.timestamp.strftime('%Y-%m-%d')
                t_str = record.timestamp.strftime('%H:%M')

                is_p1 = self.is_time_between(t_str, self.config['in_limit_1'], self.config['out_limit_1'])
                is_p2 = self.is_time_between(t_str, self.config['in_limit_2'], self.config['out_limit_2'])

                cursor.execute("SELECT id, check_in, check_out, check_in_2, check_out_2 FROM attendance WHERE employee_id=? AND date=?", (u_id, d_str))
                existing = cursor.fetchone()
                
                if not existing:
                    if is_p1:
                        cursor.execute("INSERT INTO attendance (employee_id, date, check_in) VALUES (?, ?, ?)", (u_id, d_str, t_str))
                    elif is_p2:
                        cursor.execute("INSERT INTO attendance (employee_id, date, check_in_2) VALUES (?, ?, ?)", (u_id, d_str, t_str))
                else:
                    rec_id, c1_in, c1_out, c2_in, c2_out = existing
                    if is_p1:
                        if not c1_in:
                            cursor.execute("UPDATE attendance SET check_in=? WHERE id=?", (t_str, rec_id))
                        elif t_str != c1_in:
                            cursor.execute("UPDATE attendance SET check_out=? WHERE id=?", (t_str, rec_id))
                    elif is_p2:
                        if not c2_in:
                            cursor.execute("UPDATE attendance SET check_in_2=? WHERE id=?", (t_str, rec_id))
                        elif t_str != c2_in:
                            cursor.execute("UPDATE attendance SET check_out_2=? WHERE id=?", (t_str, rec_id))
            
            db.commit()
            db.close()
            self.status_lbl.setText("✅ تم السحب بنجاح")
            QMessageBox.information(self, "نجاح", f"تم سحب {len(records)} بصمة وتوزيعها بنجاح.")
            self.load_data()
            
        except Exception as e:
            self.status_lbl.setText("❌ فشل الإتصال")
            QMessageBox.warning(self, "خطأ", f"فشل السحب: {str(e)}")
        finally:
            if conn:
                try: conn.enable_device(); conn.disconnect()
                except: pass

    def clear_device_logs(self):
        reply = QMessageBox.question(self, 'تأكيد الحذف', 
                                   'هل أنت متأكد من حذف جميع البصمات من الجهاز؟\n(يجب سحب البيانات أولاً)',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            zk = ZK(self.config['ip'], port=4370, timeout=10)
            conn = None
            try:
                conn = zk.connect()
                conn.clear_attendance()
                QMessageBox.information(self, "تم", "تم تنظيف ذاكرة الجهاز بنجاح.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل التنظيف: {str(e)}")
            finally:
                if conn: conn.disconnect()

    def load_data(self):
        try:
            conn = sqlite3.connect(get_db_path())
            query = """
                SELECT a.employee_id, COALESCE(e.name, 'غير مسجل'), a.date, a.check_in, a.check_out, a.check_in_2, a.check_out_2 
                FROM attendance a 
                LEFT JOIN employees e ON a.employee_id = e.finger_id 
                ORDER BY a.date DESC, a.employee_id ASC LIMIT 1000
            """
            data = conn.execute(query).fetchall()
            self.table.setRowCount(len(data))
            for i, row in enumerate(data):
                for j in range(7):
                    val = str(row[j]) if row[j] is not None and row[j] != "" else "--"
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignCenter)
                    if val == "--": item.setForeground(QColor("#bdc3c7"))
                    self.table.setItem(i, j, item)
            conn.close()
        except Exception as e:
            print(f"Error loading data: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceWindow()
    window.show()
    sys.exit(app.exec_())