from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt, QTimer
from .dialogs.contact_dialog import ContactDialog
from database.db_manager import DatabaseManager
from utils.exceptions import DatabaseError
from .dialogs.contact_communications import ContactCommunicationsDialog
from utils.datetime_helpers import format_datetime
from .dialogs.contact_view_dialog import ContactViewDialog
from typing import Optional

class ContactsView(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search contacts...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        
        # Clear search button
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_button)
        
        layout.addLayout(search_layout)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Contact")
        add_button.clicked.connect(self.add_contact)
        edit_button = QPushButton("Edit Contact")
        edit_button.clicked.connect(self.edit_contact)
        delete_button = QPushButton("Delete Contact")
        delete_button.clicked.connect(self.delete_contact)
        
        comm_button = QPushButton("Communications")
        comm_button.clicked.connect(self.show_communications)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(comm_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Company", "Phone", "Email", "Status", "Last Contacted"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.view_contact)
        
        # Make columns stretch to fill space
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, header.ResizeMode.Stretch)
        header.setSectionResizeMode(4, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, header.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        self.load_contacts()
    
    def on_search_text_changed(self, text: str):
        # Reset the timer
        self.search_timer.stop()
        # Start the timer with a 300ms delay
        self.search_timer.start(300)
    
    def perform_search(self):
        search_text = self.search_input.text().strip()
        self.load_contacts(search_text if search_text else None)
    
    def clear_search(self):
        self.search_input.clear()
        self.load_contacts()
    
    def load_contacts(self, search_term: Optional[str] = None):
        try:
            contacts = self.db.get_contacts(search_term=search_term)
            self.table.setRowCount(len(contacts))
            
            for row, contact in enumerate(contacts):
                name = f"{contact['first_name']} {contact['last_name']}"
                if contact['title']:
                    name += f" ({contact['title']})"
                    
                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, QTableWidgetItem(contact.get('company_name', '')))
                
                # Use mobile phone if available, otherwise use primary phone
                phone = contact['mobile_phone'] or contact['phone'] or ''
                self.table.setItem(row, 2, QTableWidgetItem(phone))
                self.table.setItem(row, 3, QTableWidgetItem(contact['email']))
                self.table.setItem(row, 4, QTableWidgetItem(contact['status']))
                
                # Format the last contacted date
                last_contacted = format_datetime(contact['last_contacted_at']) if contact['last_contacted_at'] else ''
                self.table.setItem(row, 5, QTableWidgetItem(last_contacted))
                
                # Store the contact ID in the first column
                self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, contact['id'])
                
        except DatabaseError as e:
            QMessageBox.critical(self, "Database Error", str(e))
    
    def add_contact(self):
        dialog = ContactDialog(self)
        if dialog.exec():
            try:
                contact_data = dialog.get_data()
                self.db.add_contact(contact_data)
                self.load_contacts()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not add contact: {str(e)}")
    
    def edit_contact(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a contact to edit")
            return
        
        contact_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        contact = self.db.get_contacts(contact_id)[0]
        
        dialog = ContactDialog(self, contact)
        if dialog.exec():
            try:
                contact_data = dialog.get_data()
                self.db.update_contact(contact_id, contact_data)
                self.load_contacts()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not update contact: {str(e)}")
    
    def delete_contact(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a contact to delete")
            return
        
        contact_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this contact?\nThis will also delete all associated policies.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.update_contact(contact_id, {'status': 'Deleted'})
                self.load_contacts()
            except DatabaseError as e:
                QMessageBox.critical(self, "Error", f"Could not delete contact: {str(e)}")
    
    def show_communications(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", 
                              "Please select a contact to view communications")
            return
        
        contact_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        contact_name = self.table.item(current_row, 0).text()
        
        dialog = ContactCommunicationsDialog(self, contact_id, contact_name)
        dialog.exec()
        
        # Reload contacts to update last contacted date
        self.load_contacts()
    
    def view_contact(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        contact_id = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        dialog = ContactViewDialog(self, contact_id)
        dialog.exec()
        
        # Reload contacts in case any data was updated
        self.load_contacts()