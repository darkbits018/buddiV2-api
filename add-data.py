from app import app, db  # Import your Flask app
from models import Farmer, Buyer
from datetime import datetime

with app.app_context():  # Set up application context
    # Add farmers
    farmer1 = Farmer(name="John Doe", phone_number="1234567890", email="johndoe@example.com", address="123 Farm Lane, Springfield")
    farmer2 = Farmer(name="Emma Brown", phone_number="2345678901", email="emmabrown@example.com", address="456 Orchard Ave, Shelbyville")

    db.session.add_all([farmer1, farmer2])
    db.session.commit()

    # Add buyers
    buyer1 = Buyer(name="Alice Smith", phone_number="3456789012", email="alicesmith@example.com", address="789 Market St, Shelbyville")
    buyer2 = Buyer(name="Bob Johnson", phone_number="4567890123", email="bobjohnson@example.com", address="321 Commerce Rd, Springfield")

    db.session.add_all([buyer1, buyer2])
    db.session.commit()

print("Dummy data added successfully!")
