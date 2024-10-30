from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QTabWidget, QPushButton, QStatusBar)
from .contacts_view import ContactsView
from .policies_view import PoliciesView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insurance CRM")
        self.setMinimumSize(1000, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(ContactsView(), "Contacts")
        tabs.addTab(PoliciesView(), "Policies")
        layout.addWidget(tabs)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar) 