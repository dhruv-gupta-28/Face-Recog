import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QGridLayout,
    QSizePolicy,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtCore import QDate

from datetime import datetime

def connect_db(database = None):
    try:
        if database:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database=database
            )
        else:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password"
            )
        
        if connection.is_connected():
            print("Database connection successful")
            return connection
        else:
            print("Failed to establish database connection")
            return None
            
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Check your MySQL username and password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        return None

def setup_database():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS new")
        cursor.close()
        db.close()
        
        db = connect_db("new")
        cursor = db.cursor()
        
        # Create employee_details table first
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(500) UNIQUE NOT NULL,
            name VARCHAR(1000) NOT NULL,
            phone VARCHAR(15),
            email VARCHAR(100),
            aadhaar VARCHAR(12)
        )""")
        
        # Create attendance table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(500) NOT NULL,
            name VARCHAR(1000) NOT NULL,
            arrival_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_contained TEXT,
            FOREIGN KEY (employee_id) REFERENCES employee_details(employee_id) ON DELETE CASCADE
        )""")
        
        # Clear existing data
        cursor.execute("DELETE FROM employee_attendance")
        cursor.execute("DELETE FROM employee_details")
        
        # Insert sample employee data
        sample_employees = [
            ('EMP001', 'John Doe', '9876543210', 'john.doe@email.com', '123456789012'),
            ('EMP002', 'Jane Smith', '8765432109', 'jane.smith@email.com', '234567890123'),
            ('EMP003', 'Robert Johnson', '7654321098', 'robert.j@email.com', '345678901234'),
            ('EMP004', 'Emily Wilson', '6543210987', 'emily.w@email.com', '456789012345'),
            ('EMP005', 'Michael Brown', '5432109876', 'michael.b@email.com', '567890123456'),
            ('EMP006', 'Sarah Jones', '4321098765', 'sarah.j@email.com', '678901234567')
        ]
        
        cursor.executemany("""
        INSERT INTO employee_details (employee_id, name, phone, email, aadhaar)
        VALUES (%s, %s, %s, %s, %s)
        """, sample_employees)
        
        # Insert sample attendance data
        attendance_data = [
            ('EMP001', 'John Doe', '2024-03-01 08:30:00'),
            ('EMP002', 'Jane Smith', '2024-03-01 09:15:00'),
            ('EMP003', 'Robert Johnson', '2024-03-01 09:45:00'),
            ('EMP001', 'John Doe', '2024-03-02 08:45:00'),
            ('EMP002', 'Jane Smith', '2024-03-02 10:00:00'),
            ('EMP003', 'Robert Johnson', '2024-03-02 08:30:00'),
            ('EMP004', 'Emily Wilson', '2024-03-01 08:15:00'),
            ('EMP005', 'Michael Brown', '2024-03-01 09:00:00'),
            ('EMP004', 'Emily Wilson', '2024-03-02 08:45:00'),
            ('EMP005', 'Michael Brown', '2024-03-02 11:00:00')
        ]
        
        cursor.executemany("""
        INSERT INTO employee_attendance (employee_id, name, arrival_time)
        VALUES (%s, %s, %s)
        """, attendance_data)
        
        db.commit()
        cursor.close()
        db.close()
            
    except mysql.connector.Error as err:
        print(f"Database setup error: {err}")

class AttendancePanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendance Panel System")
        self.setGeometry(0,0,1900,980) # Open in full window
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Main frame
        self.main_frame = QFrame()
        self.main_frame.setFrameShape(QFrame.StyledPanel)
        main_frame_layout = QVBoxLayout()

        # Search Frame
        self.search_frame = QFrame()
        self.search_frame.setFrameShape(QFrame.StyledPanel)
        self.search_frame.setMinimumHeight(320)
        search_layout = QVBoxLayout()

        # Search Heading
        self.search_heading = QLabel("Attendance Panel")
        self.search_heading.setAlignment(Qt.AlignCenter)
        self.search_heading.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            color: black;
            background-color: #ccc;
            border-radius: 10px;
            padding: 12px;
            margin-top: 14px;
            margin-bottom: 14px;
            text-align: center;
            """
        )
        self.search_heading.setFixedHeight(100)
        search_layout.addWidget(self.search_heading)

        # Search Options Grid
        search_grid = QGridLayout()
        search_grid.setSpacing(15)
        label_style = """
                    font-size: 18px;
                    font-weight: bold;
                    color: black;
                    background-color: #ccc;
                    border-radius: 10px;
                    padding: 8px;
                    text-align: center;
                """

        entry_style = """
                        font-size: 18px;
                        font-weight: bold;
                        background-color: white;
                        border-radius: 10px;
                        padding: 8px;
                    """

        # Search By Label
        self.search_by_label = QLabel("Search By:")
        self.search_by_label.setStyleSheet(label_style)
        search_grid.addWidget(self.search_by_label, 0, 0)

        # Search Method Combo Box
        self.search_method = QComboBox()
        self.search_method.addItem("Select Method")
        self.search_method.addItems(["Name", "Employee ID", "Phone Number", "Email ID", "Aadhaar No"])
        self.search_method.setCurrentIndex(0)
        self.search_method.setItemData(0, Qt.ItemIsEnabled, Qt.UserRole - 1)
        self.search_method.setStyleSheet(entry_style)
        self.search_method.setMinimumHeight(60)
        search_grid.addWidget(self.search_method, 0, 1)

        # Search Input
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Enter value to search")
        self.search_entry.setStyleSheet(entry_style)
        self.search_entry.setMinimumHeight(60)
        search_grid.addWidget(self.search_entry, 0, 2)

        # Date range labels and controls
        self.date_from_label = QLabel("Date From:")
        self.date_from_label.setStyleSheet(label_style)
        search_grid.addWidget(self.date_from_label, 1, 0)

        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))  # Default to 30 days ago
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet("""
            QDateEdit {
                font-size: 18px;
                font-weight: bold;
                background-color: white;
                border-radius: 10px;
                padding: 8px;
            }
            QCalendarWidget QWidget { 
                alternate-background-color: #5ea758;
            }
            QCalendarWidget QMenu {
                color: black;
                background-color: white;
            }
            QCalendarWidget QToolButton {
                color: black;
                background-color: #5ea758;
                font-size: 16px;
                font-weight: bold;
            }
            QCalendarWidget QSpinBox {
                color: black;
                background-color: white;
                font-size: 16px;
            }
        """)
        self.date_from.setMinimumHeight(60)
        search_grid.addWidget(self.date_from, 1, 1)

        self.date_to_label = QLabel("Date To:")
        self.date_to_label.setStyleSheet(label_style)
        search_grid.addWidget(self.date_to_label, 2, 0)

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())  # Default to today
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet("""
            QDateEdit {
                font-size: 18px;
                font-weight: bold;
                background-color: white;
                border-radius: 10px;
                padding: 8px;
            }
            QCalendarWidget QWidget { 
                alternate-background-color: #5ea758;
            }
            QCalendarWidget QMenu {
                color: black;
                background-color: white;
            }
            QCalendarWidget QToolButton {
                color: black;
                background-color: #5ea758;
                font-size: 16px;
                font-weight: bold;
            }
            QCalendarWidget QSpinBox {
                color: black;
                background-color: white;
                font-size: 16px;
            }
        """)
        self.date_to.setMinimumHeight(60)
        search_grid.addWidget(self.date_to, 2, 1)

        # Buttons Layout
        buttons_layout = QHBoxLayout()

        # Search Button
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                color: black;
                background-color: #5ea758;
                border-radius: 8px;
                padding: 10px;
                min-width: 200px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #aad688;
            }
            """
        )
        self.search_button.setFixedSize(200, 60)
        self.search_button.clicked.connect(self.search_attendance)
        buttons_layout.addWidget(self.search_button)

        # Show All Button
        self.show_all_button = QPushButton("Show All")
        self.show_all_button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                color: black;
                background-color: #5ea758;
                border-radius: 8px;
                padding: 10px;
                min-width: 200px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #aad688;
            }
            """
        )
        self.show_all_button.setFixedSize(200, 60)
        self.show_all_button.clicked.connect(self.show_all_attendance)
        buttons_layout.addWidget(self.show_all_button)

        # Add buttons layout to grid
        search_grid.addLayout(buttons_layout, 3, 1, 1, 2, Qt.AlignCenter)

        search_layout.addLayout(search_grid)
        self.search_frame.setLayout(search_layout)
        main_frame_layout.addWidget(self.search_frame)

        # Results Frame
        self.results_frame = QFrame()
        self.results_frame.setFrameShape(QFrame.StyledPanel)
        results_layout = QVBoxLayout()

        # Results Heading
        self.results_heading = QLabel("Attendance Results")
        self.results_heading.setAlignment(Qt.AlignCenter)
        self.results_heading.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            color: black;
            background-color: #ccc;
            border-radius: 10px;
            padding: 12px;
            margin-top: 14px;
            margin-bottom: 14px;
            text-align: center;
            """
        )
        self.results_heading.setFixedHeight(100)
        results_layout.addWidget(self.results_heading)

        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "S.No.",
            "Employee ID",
            "Name",
            "Date",
            "Status"
        ])

        # Set table properties
        header = self.results_table.horizontalHeader()
        header.setStyleSheet(
            "QHeaderView::section { background-color: #ccc; font-size: 16px; font-weight: bold; }"
        )
        
        # Set table to stretch and fill window
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Set proportional column widths
        total_width = 1900  # Full window width
        width_ratios = [0.1, 0.2, 0.3, 0.2, 0.2]  # Proportions for each column
        
        for i, ratio in enumerate(width_ratios):
            self.results_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
            self.results_table.setColumnWidth(i, int(total_width * ratio))

        # Enable scrollbars
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Allow column resizing
        header.setSectionResizeMode(QHeaderView.Interactive)

        self.results_table.setStyleSheet(
            "QTableWidget { font-size: 18px; font-weight: bold}"
        )

        results_layout.addWidget(self.results_table)

        # Total Attendance Button
        self.total_button = QPushButton("Total Attendance")
        self.total_button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                color: black;
                background-color: #5ea758;
                border-radius: 8px;
                padding: 10px;
                min-width: 200px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #aad688;
            }
            """
        )
        self.total_button.setFixedSize(250, 60)
        self.total_button.clicked.connect(self.show_total_attendance)

        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(self.total_button)
        total_layout.addStretch()

        results_layout.addLayout(total_layout)

        self.results_frame.setLayout(results_layout)
        main_frame_layout.addWidget(self.results_frame)

        self.main_frame.setLayout(main_frame_layout)
        main_layout.addWidget(self.main_frame)

    def search_attendance(self):
        from_date = self.date_from.date()
        to_date = self.date_to.date()
        
        if from_date > to_date:
            QMessageBox.warning(self, "Date Error", "From date cannot be later than To date.")
            return
        search_method = self.search_method.currentText()
        search_value = self.search_entry.text()
        from_date = self.date_from.date().toString("yyyy-MM-dd")
        to_date = self.date_to.date().toString("yyyy-MM-dd")
    
        if search_method == "Select Method" or not search_value:
            QMessageBox.warning(self, "Search Error", "Please select a search method and enter a search value.")
            return
    
        # Clear existing data
        self.results_table.setRowCount(0)
    
        try:
            db = connect_db("new")
            cursor = db.cursor()
            
            # Base query with join
            query = """
            SELECT ROW_NUMBER() OVER (ORDER BY a.arrival_time) as sno,
                   a.employee_id, a.name, DATE(a.arrival_time) as date,
                   CASE 
                       WHEN TIME(a.arrival_time) <= '09:30:00' THEN 'Present'
                       ELSE 'Late'
                   END as status
            FROM employee_attendance a
            JOIN employee_details e ON a.employee_id = e.employee_id
            WHERE """
    
            # Prepare search parameters
            params = []
            if search_method == "Name":
                query += "a.name LIKE %s"
                params.append(f"%{search_value}%")
            elif search_method == "Employee ID":
                query += "a.employee_id = %s"
                params.append(search_value)
            elif search_method == "Phone Number":
                query += "e.phone = %s"
                params.append(search_value)
            elif search_method == "Email ID":
                query += "e.email = %s"
                params.append(search_value)
            elif search_method == "Aadhaar No":
                query += "e.aadhaar = %s"
                params.append(search_value)
    
            query += " AND DATE(a.arrival_time) BETWEEN %s AND %s"
            params.extend([from_date, to_date])
            
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            
            self.populate_table(results)
            cursor.close()
            db.close()
    
            # Update results heading
            self.results_heading.setText(f"Attendance Results for {search_method}: {search_value}")
    
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error accessing database: {err}")
            return

    def show_all_attendance(self):
        try:
            from_date = self.date_from.date().toString("yyyy-MM-dd")
            to_date = self.date_to.date().toString("yyyy-MM-dd")
            
            db = connect_db("new")
            cursor = db.cursor()
            
            query = """
            SELECT ROW_NUMBER() OVER (ORDER BY arrival_time) as sno,
                   employee_id, name, DATE_FORMAT(arrival_time, '%Y-%m-%d') as date,
                   CASE 
                       WHEN TIME(arrival_time) <= '09:30:00' THEN 'Present'
                       ELSE 'Late'
                   END as status
            FROM employee_attendance
            WHERE DATE(arrival_time) BETWEEN %s AND %s
            ORDER BY arrival_time
            """
            
            cursor.execute(query, (from_date, to_date))
            results = cursor.fetchall()
            
            if not results:
                QMessageBox.information(self, "No Results", "No attendance records found for the selected date range.")
                return
                
            self.populate_table(results)
            self.results_heading.setText(f"All Attendance Records from {from_date} to {to_date}")
            
            cursor.close()
            db.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error accessing database: {err}")
            return

    def show_total_attendance(self):
        """Calculate and display total attendance statistics from database"""
        try:
            from_date = self.date_from.date().toString("yyyy-MM-dd")
            to_date = self.date_to.date().toString("yyyy-MM-dd")
            
            db = connect_db("new")
            cursor = db.cursor()
            
            # Get total unique employees in the date range
            cursor.execute("""
                SELECT COUNT(DISTINCT employee_id) 
                FROM employee_attendance 
                WHERE DATE(arrival_time) BETWEEN %s AND %s
            """, (from_date, to_date))
            total_employees = cursor.fetchone()[0]
            
            # Get present and late counts
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN TIME(arrival_time) <= '09:30:00' THEN 1 ELSE 0 END) as present_count,
                    SUM(CASE WHEN TIME(arrival_time) > '09:30:00' THEN 1 ELSE 0 END) as late_count,
                    COUNT(*) as total_records
                FROM employee_attendance
                WHERE DATE(arrival_time) BETWEEN %s AND %s
            """, (from_date, to_date))
            
            result = cursor.fetchone()
            total_present = result[0] or 0
            total_late = result[1] or 0
            total_records = result[2] or 0
            
            # Calculate percentage
            attendance_percentage = (total_present / total_records * 100) if total_records > 0 else 0
            
            stats_message = f"""
            Total Attendance Statistics ({from_date} to {to_date}):
            
            - Total Employees: {total_employees}
            - Total Present: {total_present}
            - Total Late: {total_late}
            - Total Records: {total_records}
            - On-Time Percentage: {attendance_percentage:.2f}%
            """
        
            QMessageBox.information(self, "Total Attendance", stats_message)
            
            cursor.close()
            db.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error calculating attendance statistics: {err}")
            return

    def populate_table(self, data):
        """Populate the results table with the given data"""
        self.results_table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(Qt.AlignCenter)
                self.results_table.setItem(row_idx, col_idx, item)

                # Set background color for status column
                if col_idx == 4:  # Status column
                    if col_data == "Present":
                        item.setBackground(Qt.green)
                    elif col_data == "Late":
                        item.setBackground(Qt.yellow)
                    elif col_data == "Absent":
                        item.setBackground(Qt.red)

        self.results_table.resizeColumnsToContents()

def main():
    setup_database()  # Add this line to create/setup database
    app = QApplication(sys.argv)
    window = AttendancePanel()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()