from typing import Optional

class CRMError(Exception):
    """Base exception for CRM-specific errors"""
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class DatabaseError(CRMError):
    """Database-related errors"""
    pass

class ValidationError(CRMError):
    """Data validation errors"""
    pass 