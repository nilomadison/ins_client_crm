from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox)
from PyQt6.QtCore import Qt
from .dialogs.policy_dialog import PolicyDialog
from database.db_manager import DatabaseManager
from utils.exceptions import DatabaseError
from utils.datetime_helpers import format_date

class PoliciesView(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Policy")
        add_button.clicked.connect(self.add_policy)
        edit_button = QPushButton("Edit Policy")
        edit_button.clicked.connect(self.edit_policy)
        delete_button = QPushButton("Delete Policy")
        delete_button.clicked.connect(self.delete_policy)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Contact", "Policy Number", "Type", "Carrier", 
            "Premium", "Start Date", "Renewal Date"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.edit_policy)
        
        layout.addWidget(self.table)
        
        self.load_policies()
    
    def load_policies(self):
        try:
            policies = self.db.get_policies()
            self.table.setRowCount(len(policies))
            
            for row, policy in enumerate(policies):
                self.table.setItem(row, 0, QTableWidgetItem(policy['contact_name']))
                self.table.setItem(row, 1, QTableWidgetItem(policy['policy_number']))
                self.table.setItem(row, 2, QTableWidgetItem(policy['policy_type']))
                self.table.setItem(row, 3, QTableWidgetItem(policy['carrier']))
                self.table.setItem(row, 4, QTableWidgetItem(f"${policy['premium']:,.2f}"))
                self.table.setItem(row, 5, QTableWidgetItem(format_date(policy['start_date'])))
                self.table.setItem(row, 6, QTableWidgetItem(format_date(policy['renewal_date'])))
                
                # Store the policy ID in the first column
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, policy['id'])
                
        except DatabaseError as e:
            QMessageBox.critical(self, "Database Error", str(e))
    
    def add_policy(self):
        dialog = PolicyDialog(self)
        if dialog.exec():
            try:
                policy_data = dialog.get_data()
                self.db.add_policy(policy_data)
                self.load_policies()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not add policy: {str(e)}")
    
    def edit_policy(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a policy to edit")
            return
        
        policy_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        policy = self.db.get_policies(policy_id)[0]
        
        dialog = PolicyDialog(self, policy)
        if dialog.exec():
            try:
                policy_data = dialog.get_data()
                self.db.update_policy(policy_id, policy_data)
                self.load_policies()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not update policy: {str(e)}")
    
    def delete_policy(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a policy to delete")
            return
        
        policy_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this policy?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.update_policy(policy_id, {'status': 'Deleted'})
                self.load_policies()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not delete policy: {str(e)}")