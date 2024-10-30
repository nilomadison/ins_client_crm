from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                           QTextEdit, QDialogButtonBox,
                           QComboBox, QMessageBox, QDateTimeEdit)
from PyQt6.QtCore import Qt, QDateTime
from typing import Optional, Dict, Any
import pytz
from utils.config import ConfigManager

class CommunicationDialog(QDialog):
    COMM_TYPES = [
        'Unspecified',
        'Phone Call',
        'Video Call',
        'Face to Face',
        'Text Message',
        'Email',
        'Mail'
    ]

    def __init__(self, parent=None, contact_id: int = None, 
                 contact_name: str = None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.contact_name = contact_name
        self.config = ConfigManager()
        self.local_tz = pytz.timezone(self.config.get('ui', 'timezone'))
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Add Communication - {self.contact_name}")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Communication type
        self.comm_type = QComboBox()
        self.comm_type.addItems(self.COMM_TYPES)
        form.addRow("Type:", self.comm_type)
        
        # Date and time
        self.comm_date = QDateTimeEdit(QDateTime.currentDateTime())
        self.comm_date.setCalendarPopup(True)
        self.comm_date.setTimeSpec(Qt.TimeSpec.LocalTime)  # Explicitly set to local time
        form.addRow("Date & Time:", self.comm_date)
        
        # Details
        self.details = QTextEdit()
        self.details.setPlaceholderText("Enter communication details...")
        form.addRow("Details:", self.details)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def validate_and_accept(self):
        if not self.details.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", 
                              "Please enter communication details")
            return
        
        self.accept()
    
    def get_data(self) -> Dict[str, Any]:
        # Get the datetime from the widget
        local_dt = self.comm_date.dateTime().toPyDateTime()
        
        # Localize the datetime to the user's timezone
        local_dt = self.local_tz.localize(local_dt)
        
        # Convert to UTC for storage
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        return {
            'contact_id': self.contact_id,
            'comm_type': self.comm_type.currentText(),
            'comm_date': utc_dt.isoformat(),
            'details': self.details.toPlainText().strip()
        } 