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
    
    # 1. إنشاء جدول الموظفين (أضفنا كل الأعمدة التي تطلبها ملفاتك الأخرى)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        finger_id INTEGER PRIMARY KEY, -- العمود الرئيسي للبصمة
        employee_id INTEGER,           -- عمود إضافي لضمان عمل بعض الشاشات
        name TEXT NOT NULL,
        privilege INTEGER DEFAULT 0,
        password TEXT,
        department TEXT,
        active INTEGER DEFAULT 1       -- مهم لعمل التقارير
    )""")
    
    # 2. إنشاء جدول الحضور (أضفنا finger_id و employee_id معاً)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        finger_id INTEGER,
        employee_id INTEGER,
        date TEXT,
        time TEXT,      -- لملف سحب البصمة
        check_in TEXT,  -- لفترات الدوام
        check_out TEXT,
        check_in_2 TEXT, 
        check_out_2 TEXT,
        status TEXT,
        FOREIGN KEY(finger_id) REFERENCES employees(finger_id) ON DELETE CASCADE
    )""")

    # 3. إنشاء جدول الإجازات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS holidays (
        holiday_date DATE UNIQUE
    )""")
    
    conn.commit()
    conn.close()
    print(f"✅ تم بناء القاعدة الشاملة بنجاح!")

if __name__ == "__main__":
    init_clean_db()
