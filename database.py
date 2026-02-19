import sqlite3
import os
import sys

def get_db_path():
    """تحديد مسار قاعدة البيانات بجانب ملف التشغيل دائماً"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), "attendance.db")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")

def init_clean_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # تفعيل قيود المفاتيح الخارجية
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. إنشاء جدول الموظفين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        finger_id INTEGER UNIQUE,
        active INTEGER DEFAULT 1
    )""")
    
    # 2. إنشاء جدول الحضور (معدل)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        check_in TEXT,
        check_out TEXT,
        check_in_2 TEXT, 
        check_out_2 TEXT,
        UNIQUE(employee_id, date),
        FOREIGN KEY(employee_id) REFERENCES employees(finger_id) ON DELETE CASCADE
    )""")

    # 3. إنشاء جدول الإجازات الرسمية (ليعمل مع نظام التقارير)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS holidays (
        holiday_date DATE UNIQUE
    )""")
    
    conn.commit()
    conn.close()
    print(f"✅ تم إنشاء وتجهيز قاعدة البيانات بنجاح في:\n{db_path}")

if __name__ == "__main__":
    init_clean_db()