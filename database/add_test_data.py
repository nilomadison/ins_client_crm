import random
from datetime import datetime, timedelta
from .db_manager import DatabaseManager
import os

# Remove existing database if it exists
db_path = os.path.join(os.path.dirname(__file__), "..", "insurance_crm.db")
if os.path.exists(db_path):
    os.remove(db_path)

# Sample data
INDIVIDUAL_NAMES = [
    ("John", "Smith"), ("Mary", "Johnson"), ("Robert", "Williams"),
    ("Patricia", "Brown"), ("Michael", "Jones"), ("Jennifer", "Garcia"),
    ("William", "Miller"), ("Elizabeth", "Davis"), ("David", "Rodriguez"),
    ("Linda", "Martinez")
]

COMPANIES = [
    "ABC Manufacturing Co.", "Tech Solutions Inc.", "Global Logistics LLC",
    "Sunshine Restaurants", "Premier Properties Group", "Valley Construction Inc.",
    "Metro Healthcare Services", "Reliable Transport Corp.", "Green Energy Systems",
    "Summit Financial Group"
]

COMPANY_CONTACTS = [
    ("James", "Wilson"), ("Sarah", "Anderson"), ("Thomas", "Taylor"),
    ("Margaret", "Moore"), ("Richard", "Jackson"), ("Susan", "White"),
    ("Joseph", "Harris"), ("Dorothy", "Martin"), ("Charles", "Thompson"),
    ("Nancy", "Lee")
]

TITLES = [
    "CEO", "CFO", "Operations Manager", "HR Director", "General Manager",
    "Office Manager", "Finance Director", "Operations Director", "President",
    "Vice President"
]

CARRIERS = [
    "State Farm", "Allstate", "Progressive", "Liberty Mutual", "Nationwide",
    "Farmers Insurance", "GEICO", "Travelers", "American Family", "Hartford"
]

COMM_DETAILS = [
    "Discussed policy renewal options",
    "Reviewed coverage details",
    "Updated contact information",
    "Processed policy changes",
    "Handled billing inquiry",
    "Discussed new policy options",
    "Annual policy review",
    "Claims discussion",
    "Premium payment confirmation",
    "Policy documentation request"
]

def generate_phone():
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"

def generate_email(first_name, last_name):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "aol.com", "hotmail.com"]
    return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"

def generate_address():
    streets = ["Main St", "Oak Ave", "Maple Dr", "Washington Blvd", "Park Rd"]
    cities = ["Springfield", "Franklin", "Clinton", "Georgetown", "Salem"]
    states = ["IL", "OH", "MI", "IN", "WI"]
    return f"{random.randint(100, 9999)} {random.choice(streets)}\n{random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}"

def generate_policy_number(carrier):
    return f"{carrier[:3].upper()}-{random.randint(100000, 999999)}"

def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def main():
    db = DatabaseManager()
    
    # Generate individual contacts
    for first_name, last_name in INDIVIDUAL_NAMES:
        contact_data = {
            'contact_type': 'Individual',
            'first_name': first_name,
            'last_name': last_name,
            'email': generate_email(first_name, last_name),
            'phone': generate_phone(),
            'mobile_phone': generate_phone() if random.random() > 0.5 else '',
            'address': generate_address(),
            'status': random.choice(['Active', 'Active', 'Active', 'Inactive', 'Lead']),
            'notes': "Individual client"
        }
        contact_id = db.add_contact(contact_data)
        
        # Add 1-3 policies for each individual
        for _ in range(random.randint(1, 3)):
            carrier = random.choice(CARRIERS)
            start_date = random_date(
                datetime.now() - timedelta(days=365*2),
                datetime.now() - timedelta(days=30)
            )
            renewal_date = start_date + timedelta(days=365)
            
            policy_data = {
                'contact_id': contact_id,
                'policy_type': random.choice(['Auto', 'Home', 'Life', 'Umbrella']),
                'policy_number': generate_policy_number(carrier),
                'carrier': carrier,
                'premium': round(random.uniform(500, 5000), 2),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'renewal_date': renewal_date.strftime('%Y-%m-%d'),
                'notes': "Sample policy"
            }
            db.add_policy(policy_data)
    
    # Generate company contacts
    for idx, company in enumerate(COMPANIES):
        first_name, last_name = COMPANY_CONTACTS[idx]
        contact_data = {
            'contact_type': 'Company',
            'company_name': company,
            'first_name': first_name,
            'last_name': last_name,
            'title': random.choice(TITLES),
            'email': generate_email(first_name, last_name),
            'phone': generate_phone(),
            'mobile_phone': generate_phone(),
            'address': generate_address(),
            'status': random.choice(['Active', 'Active', 'Active', 'Inactive']),
            'notes': "Corporate client"
        }
        contact_id = db.add_contact(contact_data)
        
        # Add 2-5 policies for each company
        for _ in range(random.randint(2, 5)):
            carrier = random.choice(CARRIERS)
            start_date = random_date(
                datetime.now() - timedelta(days=365*2),
                datetime.now() - timedelta(days=30)
            )
            renewal_date = start_date + timedelta(days=365)
            
            policy_data = {
                'contact_id': contact_id,
                'policy_type': random.choice(['Business', 'Liability', 'Workers Comp', 'Property']),
                'policy_number': generate_policy_number(carrier),
                'carrier': carrier,
                'premium': round(random.uniform(2000, 50000), 2),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'renewal_date': renewal_date.strftime('%Y-%m-%d'),
                'notes': "Corporate policy"
            }
            db.add_policy(policy_data)
    
    # Generate communications for all contacts
    contacts = db.get_contacts()
    for contact in contacts:
        # Add 3-8 communications per contact
        for _ in range(random.randint(3, 8)):
            comm_date = random_date(
                datetime.now() - timedelta(days=365),
                datetime.now()
            )
            
            comm_data = {
                'contact_id': contact['id'],
                'comm_type': random.choice([
                    'Phone Call', 'Email', 'Face to Face',
                    'Video Call', 'Text Message'
                ]),
                'comm_date': comm_date.isoformat(),
                'details': random.choice(COMM_DETAILS)
            }
            db.add_communication(comm_data)

if __name__ == "__main__":
    main()
    print("Test data has been generated successfully!") 