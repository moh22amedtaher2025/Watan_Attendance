STYLE_SHEET = """
QMainWindow, QWidget {
    background-color: #f4f7f6;
    font-family: 'Segoe UI', Arial;
    font-size: 14px; /* خط متوسط */
}
QFrame#MainCard {
    background-color: white;
    border-radius: 20px;
    border: 1px solid #d1d8e0;
}
QPushButton {
    background-color: #2d3436;
    color: white;
    border-radius: 10px;
    padding: 12px;
    font-weight: bold;
}
QPushButton:hover { background-color: #636e72; }
QPushButton#ActionBtn { background-color: #0984e3; }
QPushButton#DeleteBtn { background-color: #d63031; }
QLineEdit {
    padding: 12px;
    border: 2px solid #dfe6e9;
    border-radius: 10px;
    background: white;
}
QTableWidget {
    background-color: white;
    border-radius: 10px;
}
"""