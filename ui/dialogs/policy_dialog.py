from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                           QLineEdit, QTextEdit, QDialogButtonBox,
                           QComboBox, QMessageBox, QDateEdit,
                           QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate
from typing import Optional, Dict, Any
from database.db_manager import DatabaseManager

class PolicyDialog(QDialog):
    def __init__(self, parent=None, policy_data: Optional[Dict[str, Any]] = None,
                 preselected_contact_id: Optional[int] = None):
        super().__init__(parent)
        self.policy_data = policy_data
        self.preselected_contact_id = preselected_contact_id
        self.db = DatabaseManager()
        self.init_ui()
        if policy_data:
            self.load_policy_data()
    
    def init_ui(self):
        self.setWindowTitle("Add Policy" if not self.policy_data else "Edit Policy")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Contact selection
        self.contact_combo = QComboBox()
        self.load_contacts()
        if self.preselected_contact_id is not None:
            # Find and set the preselected contact
            index = self.contact_combo.findData(self.preselected_contact_id)
            if index >= 0:
                self.contact_combo.setCurrentIndex(index)
                self.contact_combo.setEnabled(False)  # Lock the selection
        form.addRow("Contact:", self.contact_combo)
        
        # Policy type
        self.policy_type = QComboBox()
        self.policy_type.addItems([
            'Auto', 'Home', 'Life', 'Health', 
            'Business', 'Umbrella', 'Other'
        ])
        form.addRow("Policy Type:", self.policy_type)
        
        # Other fields
        self.policy_number = QLineEdit()
        self.carrier = QLineEdit()
        self.premium = QDoubleSpinBox()
        self.premium.setMaximum(1000000.00)
        self.premium.setPrefix("$")
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        
        self.renewal_date = QDateEdit()
        self.renewal_date.setCalendarPopup(True)
        self.renewal_date.setDate(QDate.currentDate().addYears(1))
        
        self.notes = QTextEdit()
        
        form.addRow("Policy Number:", self.policy_number)
        form.addRow("Carrier:", self.carrier)
        form.addRow("Premium:", self.premium)
        form.addRow("Start Date:", self.start_date)
        form.addRow("Renewal Date:", self.renewal_date)
        form.addRow("Notes:", self.notes)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_contacts(self):
        contacts = self.db.get_contacts()
        for contact in contacts:
            display_name = f"{contact['first_name']} {contact['last_name']}"
            if contact['contact_type'] == 'Company':
                display_name += f" ({contact['company_name']})"
            self.contact_combo.addItem(display_name, contact['id'])
    
    def load_policy_data(self):
        # Find and set the correct contact
        contact_index = self.contact_combo.findData(self.policy_data['contact_id'])
        if contact_index >= 0:
            self.contact_combo.setCurrentIndex(contact_index)
        
        self.policy_type.setCurrentText(self.policy_data['policy_type'])
        self.policy_number.setText(self.policy_data['policy_number'])
        self.carrier.setText(self.policy_data['carrier'])
        self.premium.setValue(float(self.policy_data['premium']))
        
        # Convert string dates to QDate
        start = QDate.fromString(self.policy_data['start_date'], Qt.DateFormat.ISODate)
        renewal = QDate.fromString(self.policy_data['renewal_date'], Qt.DateFormat.ISODate)
        self.start_date.setDate(start)
        self.renewal_date.setDate(renewal)
        
        self.notes.setText(self.policy_data.get('notes', ''))
    
    def validate_and_accept(self):
        if not self.policy_number.text().strip():
            QMessageBox.warning(self, "Validation Error", "Policy number is required")
            return
        if not self.carrier.text().strip():
            QMessageBox.warning(self, "Validation Error", "Carrier is required")
            return
        if self.start_date.date() > self.renewal_date.date():
            QMessageBox.warning(self, "Validation Error", "Start date must be before renewal date")
            return
        
        self.accept()
    
    def get_data(self) -> Dict[str, Any]:
        return {
            'contact_id': self.contact_combo.currentData(),
            'policy_type': self.policy_type.currentText(),
            'policy_number': self.policy_number.text().strip(),
            'carrier': self.carrier.text().strip(),
            'premium': self.premium.value(),
            'start_date': self.start_date.date().toString(Qt.DateFormat.ISODate),
            'renewal_date': self.renewal_date.date().toString(Qt.DateFormat.ISODate),
            'notes': self.notes.toPlainText().strip()
        } 