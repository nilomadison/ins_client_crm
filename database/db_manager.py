import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from utils.exceptions import DatabaseError

class DatabaseManager:
    def __init__(self):
        try:
            db_path = Path("insurance_crm.db")
            self.conn = sqlite3.connect(str(db_path))
            # Enable foreign key support
            self.conn.execute("PRAGMA foreign_keys = ON")
            # Return rows as dictionaries
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        self.conn.close()

    def create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'Active',
                contact_type TEXT NOT NULL DEFAULT 'Individual',
                company_name TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                title TEXT,
                email TEXT,
                phone TEXT,
                mobile_phone TEXT,
                address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Add indexes for search fields
            CREATE INDEX IF NOT EXISTS idx_contacts_name 
                ON contacts(last_name, first_name);
            CREATE INDEX IF NOT EXISTS idx_contacts_email 
                ON contacts(email);
            CREATE INDEX IF NOT EXISTS idx_contacts_phone 
                ON contacts(phone, mobile_phone);
            CREATE INDEX IF NOT EXISTS idx_contacts_company 
                ON contacts(company_name);

            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY,
                contact_id INTEGER NOT NULL,
                policy_type TEXT NOT NULL,
                policy_number TEXT NOT NULL UNIQUE,
                carrier TEXT NOT NULL,
                premium REAL NOT NULL,
                start_date DATE NOT NULL,
                renewal_date DATE NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS communications (
                id INTEGER PRIMARY KEY,
                contact_id INTEGER NOT NULL,
                comm_type TEXT NOT NULL,
                comm_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT NOT NULL,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_policies_contact 
                ON policies(contact_id);
            CREATE INDEX IF NOT EXISTS idx_policies_renewal 
                ON policies(renewal_date);
            CREATE INDEX IF NOT EXISTS idx_communications_contact 
                ON communications(contact_id);
            CREATE INDEX IF NOT EXISTS idx_communications_date 
                ON communications(comm_date);
        """)
        self.conn.commit()

    # Contact methods
    def add_contact(self, contact_data: Dict[str, Any]) -> int:
        query = """
            INSERT INTO contacts (
                contact_type, company_name, first_name, last_name, 
                title, email, phone, mobile_phone, address, 
                notes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            contact_data['contact_type'],
            contact_data.get('company_name'),
            contact_data['first_name'],
            contact_data['last_name'],
            contact_data.get('title'),
            contact_data.get('email'),
            contact_data.get('phone'),
            contact_data.get('mobile_phone'),
            contact_data.get('address'),
            contact_data.get('notes'),
            contact_data.get('status', 'Active')
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_contacts(self, contact_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        query = """
            SELECT c.*,
                   (SELECT MAX(comm_date)
                    FROM communications
                    WHERE contact_id = c.id) as last_contacted_at
            FROM contacts c
            WHERE c.status != 'Deleted'
        """
        params = []
        
        if contact_id is not None:
            query += " AND c.id = ?"
            params.append(contact_id)
        elif search_term:  # Only use search term if no specific ID is provided
            query += """ 
                AND (
                    c.first_name LIKE ? OR 
                    c.last_name LIKE ? OR 
                    c.company_name LIKE ? OR
                    c.email LIKE ? OR 
                    c.phone LIKE ? OR
                    c.mobile_phone LIKE ?
                )
            """
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern] * 6)
        
        query += " ORDER BY c.last_name, c.first_name"
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def update_contact(self, contact_id: int, contact_data: Dict[str, Any]) -> bool:
        query = """
            UPDATE contacts 
            SET contact_type=?, company_name=?, first_name=?, last_name=?,
                title=?, email=?, phone=?, mobile_phone=?, address=?,
                notes=?, status=?
            WHERE id=?
        """
        self.cursor.execute(query, (
            contact_data['contact_type'],
            contact_data.get('company_name'),
            contact_data['first_name'],
            contact_data['last_name'],
            contact_data.get('title'),
            contact_data.get('email'),
            contact_data.get('phone'),
            contact_data.get('mobile_phone'),
            contact_data.get('address'),
            contact_data.get('notes'),
            contact_data.get('status', 'Active'),
            contact_id
        ))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Policy methods
    def add_policy(self, policy_data: Dict[str, Any]) -> int:
        query = """
            INSERT INTO policies (
                contact_id, policy_type, policy_number, carrier,
                premium, start_date, renewal_date, notes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            policy_data['contact_id'],
            policy_data['policy_type'],
            policy_data['policy_number'],
            policy_data['carrier'],
            policy_data['premium'],
            policy_data['start_date'],
            policy_data['renewal_date'],
            policy_data.get('notes'),
            policy_data.get('status', 'Active')
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_policies(self, policy_id: Optional[int] = None, contact_id: Optional[int] = None) -> List[Dict]:
        query = """
            SELECT p.*, 
                   c.first_name || ' ' || c.last_name as contact_name,
                   c.company_name
            FROM policies p
            JOIN contacts c ON p.contact_id = c.id
            WHERE p.status != 'Deleted'
        """
        params = []
        
        if policy_id is not None:
            query += " AND p.id = ?"
            params.append(policy_id)
        elif contact_id is not None:
            query += " AND p.contact_id = ?"
            params.append(contact_id)
        
        query += " ORDER BY p.renewal_date"
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def update_policy(self, policy_id: int, policy_data: Dict[str, Any]) -> bool:
        query = """
            UPDATE policies 
            SET contact_id=?, policy_type=?, policy_number=?, carrier=?,
                premium=?, start_date=?, renewal_date=?, notes=?, status=?
            WHERE id=?
        """
        self.cursor.execute(query, (
            policy_data['contact_id'],
            policy_data['policy_type'],
            policy_data['policy_number'],
            policy_data['carrier'],
            policy_data['premium'],
            policy_data['start_date'],
            policy_data['renewal_date'],
            policy_data.get('notes'),
            policy_data.get('status', 'Active'),
            policy_id
        ))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Communication methods
    def add_communication(self, comm_data: Dict[str, Any]) -> int:
        query = """
            INSERT INTO communications (
                contact_id, comm_type, comm_date, details
            ) VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            comm_data['contact_id'],
            comm_data['comm_type'],
            comm_data['comm_date'],
            comm_data['details']
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_communications(self, contact_id: int) -> List[Dict]:
        query = """
            SELECT c.*, 
                   ct.first_name || ' ' || ct.last_name as contact_name,
                   CASE 
                       WHEN ct.contact_type = 'Company' 
                       THEN ct.company_name 
                       ELSE NULL 
                   END as company_name
            FROM communications c
            JOIN contacts ct ON c.contact_id = ct.id
            WHERE c.contact_id = ?
            ORDER BY c.comm_date DESC
        """
        self.cursor.execute(query, (contact_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def fix_last_contacted_dates(self):
        """One-time fix to update all contacts' last_contacted_at fields"""
        self.cursor.execute("""
            UPDATE contacts
            SET last_contacted_at = (
                SELECT MAX(comm_date)
                FROM communications
                WHERE communications.contact_id = contacts.id
            )
            WHERE EXISTS (
                SELECT 1
                FROM communications
                WHERE communications.contact_id = contacts.id
            )
        """)
        self.conn.commit()