from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox)
from PyQt6.QtCore import Qt
from .communication_dialog import CommunicationDialog
from database.db_manager import DatabaseManager
from utils.exceptions import DatabaseError
from utils.datetime_helpers import format_datetime

class ContactCommunicationsDialog(QDialog):
    def __init__(self, parent=None, contact_id: int = None, 
                 contact_name: str = None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.contact_name = contact_name
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Communications - {self.contact_name}")
        self.resize(800, 400)
        
        layout = QVBoxLayout(self)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Communication")
        add_button.clicked.connect(self.add_communication)
        button_layout.addWidget(add_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Date & Time", "Type", "Details", "Created"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.load_communications()
    
    def load_communications(self):
        try:
            communications = self.db.get_communications(self.contact_id)
            self.table.setRowCount(len(communications))
            
            for row, comm in enumerate(communications):
                self.table.setItem(row, 0, QTableWidgetItem(format_datetime(comm['comm_date'])))
                self.table.setItem(row, 1, QTableWidgetItem(comm['comm_type']))
                self.table.setItem(row, 2, QTableWidgetItem(comm['details']))
                self.table.setItem(row, 3, QTableWidgetItem(format_datetime(comm['created_at'])))
                
        except DatabaseError as e:
            QMessageBox.critical(self, "Database Error", str(e))
    
    def add_communication(self):
        dialog = CommunicationDialog(self, self.contact_id, self.contact_name)
        if dialog.exec():
            try:
                comm_data = dialog.get_data()
                self.db.add_communication(comm_data)
                self.load_communications()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", 
                                   f"Could not add communication: {str(e)}") 