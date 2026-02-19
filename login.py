import json
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from styles import STYLE_SHEET

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("دخول - مؤسسة وطن")
        self.setFixedSize(350, 450)
        self.setStyleSheet(STYLE_SHEET)
        self.setLayoutDirection(Qt.RightToLeft) # لضمان اتجاه الكتابة العربي
        
        # تحديد نفس مسار الملف المستخدم في الإعدادات لضمان القراءة الصحيحة
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_data.json")
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🏢\nتسجيل الدخول")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        self.user = QLineEdit()
        self.user.setPlaceholderText("اسم المستخدم")
        
        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("كلمة المرور")
        self.pwd.setEchoMode(QLineEdit.Password)
        
        btn = QPushButton("دخول")
        btn.setObjectName("PrimaryBtn") 
        btn.clicked.connect(self.handle_login)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.user)
        layout.addWidget(self.pwd)
        layout.addWidget(btn)
        layout.addStretch()
        self.setLayout(layout)

    def handle_login(self):
        """التحقق من البيانات المدخلة مقارنة بالملف المحفوظ"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    # نجلب القيم المحفوظة، وإذا لم تكن موجودة نستخدم "123"
                    saved_user = str(data.get("username", "123")).strip()
                    saved_pwd = str(data.get("password", "123")).strip()
            else:
                # إذا الملف غير موجود نهائياً، القيمة الافتراضية هي 123
                saved_user = "123"
                saved_pwd = "123"
        except Exception:
            # في حال وجود أي خطأ في قراءة الملف
            saved_user = "123"
            saved_pwd = "123"

        # التحقق من المطابقة (مع إزالة المسافات الزائدة من المدخلات أيضاً)
        if self.user.text().strip() == saved_user and self.pwd.text().strip() == saved_pwd:
            self.accept() 
        else:
            QMessageBox.warning(self, "خطأ في الدخول", "اسم المستخدم أو كلمة المرور غير صحيحة!")