from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

class PasswordsPage(QWidget):
    def __init__(self, main_window, user_name):
        super().__init__()
        print("pwd page", user_name)
        self.main_window = main_window
        self.setWindowTitle("Passwords")
        # get passwords from the database
        user_data = [("user1", "password1"), ("user2", "password2")]
        self.setup_ui(user_data)

    def setup_ui(self, user_data):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header label
        header = QLabel("Passwords")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header)

        # QTableWidget to display data in a grid with grid lines
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Username", "Password"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setShowGrid(True)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                font-size: 16px;
            }
            QHeaderView::section {
                background-color: #000000;
                padding: 4px;
                border: 1px solid #ccc;
                font-weight: bold;
            }
            QTableWidget::item {
                border: 1px solid #ccc;
                padding: 4px;
            }
        """)

        table.setRowCount(len(user_data))
        for i, (uname, pwd) in enumerate(user_data):
            table.setItem(i, 0, QTableWidgetItem(uname))
            table.setItem(i, 1, QTableWidgetItem(pwd))

        layout.addWidget(table)
        self.setLayout(layout)