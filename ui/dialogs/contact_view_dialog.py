from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QLabel, QFrame, QMessageBox, QTabWidget, QWidget)
from PyQt6.QtCore import Qt
from datetime import datetime
from .contact_dialog import ContactDialog
from .communication_dialog import CommunicationDialog
from database.db_manager import DatabaseManager
from utils.exceptions import DatabaseError
from utils.datetime_helpers import format_datetime, format_date
from .policy_dialog import PolicyDialog

class ContactViewDialog(QDialog):
    def __init__(self, parent=None, contact_id: int = None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.db = DatabaseManager()
        self.contact_data = None
        self.info_labels = {}  # Store references to labels
        self.init_ui()
        self.load_contact_data()
        
    def init_ui(self):
        self.setWindowTitle("Contact Details")  # Will be updated in load_contact_data
        self.resize(1000, 600)
        layout = QVBoxLayout(self)
        
        # Top buttons
        button_layout = QHBoxLayout()
        edit_button = QPushButton("Edit Contact")
        edit_button.clicked.connect(self.edit_contact)
        add_comm_button = QPushButton("Add Communication")
        add_comm_button.clicked.connect(self.add_communication)
        add_policy_button = QPushButton("Add Policy")
        add_policy_button.clicked.connect(self.add_policy)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(add_comm_button)
        button_layout.addWidget(add_policy_button)
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Contact Info Section
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.info_layout = QGridLayout(info_frame)
        layout.addWidget(info_frame)
        
        # Tabs for Policies and Communications
        tabs = QTabWidget()
        
        # Active Policies Tab
        policies_widget = QWidget()
        policies_layout = QVBoxLayout(policies_widget)
        
        self.policies_table = QTableWidget()
        self.policies_table.setColumnCount(6)
        self.policies_table.setHorizontalHeaderLabels([
            "Policy Number", "Type", "Carrier", "Premium", 
            "Start Date", "Renewal Date"
        ])
        self.policies_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.policies_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        policies_layout.addWidget(self.policies_table)
        tabs.addTab(policies_widget, "Active Policies")
        
        # Communications Tab
        comms_widget = QWidget()
        comms_layout = QVBoxLayout(comms_widget)
        
        self.comms_table = QTableWidget()
        self.comms_table.setColumnCount(4)
        self.comms_table.setHorizontalHeaderLabels([
            "Date & Time", "Type", "Details", "Created"
        ])
        self.comms_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.comms_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        comms_layout.addWidget(self.comms_table)
        tabs.addTab(comms_widget, "Communications History")
        
        layout.addWidget(tabs)

    def load_contact_data(self):
        self.contact_data = self.db.get_contacts(self.contact_id)[0]
        self.setWindowTitle(f"Contact Details - {self.contact_data['first_name']} {self.contact_data['last_name']}")
        
        # Clear existing labels
        for i in reversed(range(self.info_layout.count())): 
            self.info_layout.itemAt(i).widget().setParent(None)
        
        # Basic Info
        row = 0
        if self.contact_data['contact_type'] == 'Company':
            self.info_layout.addWidget(QLabel("Company:"), row, 0)
            self.info_layout.addWidget(QLabel(self.contact_data['company_name']), row, 1)
            row += 1
        
        self.info_layout.addWidget(QLabel("Name:"), row, 0)
        self.info_layout.addWidget(QLabel(f"{self.contact_data['first_name']} {self.contact_data['last_name']}"), row, 1)
        
        if self.contact_data['title']:
            self.info_layout.addWidget(QLabel("Title:"), row, 2)
            self.info_layout.addWidget(QLabel(self.contact_data['title']), row, 3)
        row += 1
        
        self.info_layout.addWidget(QLabel("Status:"), row, 0)
        self.info_layout.addWidget(QLabel(self.contact_data['status']), row, 1)
        row += 1
        
        if self.contact_data['email']:
            self.info_layout.addWidget(QLabel("Email:"), row, 0)
            self.info_layout.addWidget(QLabel(self.contact_data['email']), row, 1)
            row += 1
            
        if self.contact_data['phone']:
            self.info_layout.addWidget(QLabel("Phone:"), row, 0)
            self.info_layout.addWidget(QLabel(self.contact_data['phone']), row, 1)
            row += 1
            
        if self.contact_data['mobile_phone']:
            self.info_layout.addWidget(QLabel("Mobile:"), row, 0)
            self.info_layout.addWidget(QLabel(self.contact_data['mobile_phone']), row, 1)
            row += 1
            
        if self.contact_data['address']:
            self.info_layout.addWidget(QLabel("Address:"), row, 0)
            self.info_layout.addWidget(QLabel(self.contact_data['address']), row, 1, 1, 3)
            row += 1
        
        # Refresh the tables
        self.load_policies()
        self.load_communications()
    
    def edit_contact(self):
        dialog = ContactDialog(self, self.contact_data)
        if dialog.exec():
            try:
                contact_data = dialog.get_data()
                self.db.update_contact(self.contact_id, contact_data)
                self.load_contact_data()  # Refresh the display
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not update contact: {str(e)}")
    
    def load_policies(self):
        try:
            policies = self.db.get_policies(self.contact_id)
            # Filter for active policies
            current_date = datetime.now().date()
            active_policies = [p for p in policies 
                             if datetime.strptime(p['renewal_date'], '%Y-%m-%d').date() >= current_date
                             and p['status'] == 'Active']
            
            self.policies_table.setRowCount(len(active_policies))
            
            for row, policy in enumerate(active_policies):
                self.policies_table.setItem(row, 0, QTableWidgetItem(policy['policy_number']))
                self.policies_table.setItem(row, 1, QTableWidgetItem(policy['policy_type']))
                self.policies_table.setItem(row, 2, QTableWidgetItem(policy['carrier']))
                self.policies_table.setItem(row, 3, QTableWidgetItem(f"${policy['premium']:,.2f}"))
                self.policies_table.setItem(row, 4, QTableWidgetItem(format_date(policy['start_date'])))
                self.policies_table.setItem(row, 5, QTableWidgetItem(format_date(policy['renewal_date'])))
                
        except DatabaseError as e:
            QMessageBox.critical(self, "Database Error", str(e))
    
    def load_communications(self):
        try:
            communications = self.db.get_communications(self.contact_id)
            self.comms_table.setRowCount(len(communications))
            
            for row, comm in enumerate(communications):
                self.comms_table.setItem(row, 0, QTableWidgetItem(format_datetime(comm['comm_date'])))
                self.comms_table.setItem(row, 1, QTableWidgetItem(comm['comm_type']))
                self.comms_table.setItem(row, 2, QTableWidgetItem(comm['details']))
                self.comms_table.setItem(row, 3, QTableWidgetItem(format_datetime(comm['created_at'])))
                
        except DatabaseError as e:
            QMessageBox.critical(self, "Database Error", str(e))
    
    def add_communication(self):
        name = f"{self.contact_data['first_name']} {self.contact_data['last_name']}"
        dialog = CommunicationDialog(self, self.contact_id, name)
        if dialog.exec():
            try:
                comm_data = dialog.get_data()
                self.db.add_communication(comm_data)
                self.load_communications()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not add communication: {str(e)}")
    
    def add_policy(self):
        dialog = PolicyDialog(self, preselected_contact_id=self.contact_id)
        if dialog.exec():
            try:
                policy_data = dialog.get_data()
                self.db.add_policy(policy_data)
                self.load_policies()  # Refresh the policies table
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not add policy: {str(e)}")