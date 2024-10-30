from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                           QLineEdit, QTextEdit, QDialogButtonBox,
                           QComboBox, QMessageBox, QCheckBox,
                           QWidget, QGridLayout, QLabel)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, Any

class ContactDialog(QDialog):
    def __init__(self, parent=None, contact_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.contact_data = contact_data
        self.init_ui()
        if contact_data:
            self.load_contact_data()
    
    def init_ui(self):
        self.setWindowTitle("Add Contact" if not self.contact_data else "Edit Contact")
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        
        # Contact Type and Status
        type_status_layout = QGridLayout()
        
        self.contact_type = QComboBox()
        self.contact_type.addItems(['Individual', 'Company'])
        self.contact_type.currentTextChanged.connect(self.on_contact_type_changed)
        type_status_layout.addWidget(QLabel("Type:"), 0, 0)
        type_status_layout.addWidget(self.contact_type, 0, 1)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Active', 'Inactive', 'Lead', 'Prospect'])
        type_status_layout.addWidget(QLabel("Status:"), 0, 2)
        type_status_layout.addWidget(self.status_combo, 0, 3)
        
        form.addRow(type_status_layout)
        
        # Company Information (initially hidden)
        self.company_widget = QWidget()
        company_layout = QFormLayout(self.company_widget)
        self.company_name = QLineEdit()
        company_layout.addRow("Company Name:", self.company_name)
        form.addRow(self.company_widget)
        self.company_widget.hide()
        
        # Contact Person Information
        contact_group = QWidget()
        contact_layout = QFormLayout(contact_group)
        
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.title = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.mobile_phone = QLineEdit()
        self.address = QTextEdit()
        self.notes = QTextEdit()
        
        contact_layout.addRow("First Name:", self.first_name)
        contact_layout.addRow("Last Name:", self.last_name)
        contact_layout.addRow("Title:", self.title)
        contact_layout.addRow("Email:", self.email)
        contact_layout.addRow("Phone:", self.phone)
        contact_layout.addRow("Mobile:", self.mobile_phone)
        contact_layout.addRow("Address:", self.address)
        contact_layout.addRow("Notes:", self.notes)
        
        form.addRow(contact_group)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def on_contact_type_changed(self, contact_type: str):
        self.company_widget.setVisible(contact_type == 'Company')
        self.title.setPlaceholderText(
            "Job Title" if contact_type == 'Company' else "Title/Designation"
        )
    
    def load_contact_data(self):
        self.contact_type.setCurrentText(self.contact_data.get('contact_type', 'Individual'))
        self.status_combo.setCurrentText(self.contact_data.get('status', 'Active'))
        self.company_name.setText(self.contact_data.get('company_name', ''))
        self.first_name.setText(self.contact_data.get('first_name', ''))
        self.last_name.setText(self.contact_data.get('last_name', ''))
        self.title.setText(self.contact_data.get('title', ''))
        self.email.setText(self.contact_data.get('email', ''))
        self.phone.setText(self.contact_data.get('phone', ''))
        self.mobile_phone.setText(self.contact_data.get('mobile_phone', ''))
        self.address.setText(self.contact_data.get('address', ''))
        self.notes.setText(self.contact_data.get('notes', ''))
    
    def validate_and_accept(self):
        if self.contact_type.currentText() == 'Company' and not self.company_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Company name is required")
            return
        if not self.first_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "First name is required")
            return
        if not self.last_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Last name is required")
            return
        
        self.accept()
    
    def get_data(self) -> Dict[str, Any]:
        return {
            'contact_type': self.contact_type.currentText(),
            'status': self.status_combo.currentText(),
            'company_name': self.company_name.text().strip() if self.contact_type.currentText() == 'Company' else None,
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'title': self.title.text().strip(),
            'email': self.email.text().strip(),
            'phone': self.phone.text().strip(),
            'mobile_phone': self.mobile_phone.text().strip(),
            'address': self.address.toPlainText().strip(),
            'notes': self.notes.toPlainText().strip()
        }