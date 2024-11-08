from app import app, db  # Import your Flask app
from models import Farmer, Buyer, Item, Sale  # Import your models
from datetime import datetime

# Sample sales data
sales_data = [
    {"sale_id": 52, "item_id": 1, "buyer_id": 1, "quantity_sold": 12, "sale_price": 130.00,
     "sale_date": "2015-03-15 10:00:00"},
    {"sale_id": 53, "item_id": 2, "buyer_id": 2, "quantity_sold": 45, "sale_price": 90.00,
     "sale_date": "2016-07-12 14:30:00"},
    {"sale_id": 54, "item_id": 3, "buyer_id": 1, "quantity_sold": 30, "sale_price": 75.00,
     "sale_date": "2016-11-25 09:45:00"},
    {"sale_id": 55, "item_id": 4, "buyer_id": 2, "quantity_sold": 60, "sale_price": 72.00,
     "sale_date": "2017-02-13 12:10:00"},
    {"sale_id": 56, "item_id": 5, "buyer_id": 1, "quantity_sold": 20, "sale_price": 36.00,
     "sale_date": "2018-06-18 16:20:00"},
    {"sale_id": 57, "item_id": 1, "buyer_id": 2, "quantity_sold": 35, "sale_price": 140.00,
     "sale_date": "2019-03-28 08:50:00"},
    {"sale_id": 58, "item_id": 2, "buyer_id": 1, "quantity_sold": 55, "sale_price": 110.00,
     "sale_date": "2020-01-15 11:15:00"},
    {"sale_id": 59, "item_id": 3, "buyer_id": 2, "quantity_sold": 65, "sale_price": 97.50,
     "sale_date": "2021-05-23 13:40:00"},
    {"sale_id": 60, "item_id": 4, "buyer_id": 1, "quantity_sold": 28, "sale_price": 50.40,
     "sale_date": "2022-09-10 10:00:00"},
    {"sale_id": 61, "item_id": 5, "buyer_id": 2, "quantity_sold": 42, "sale_price": 75.60,
     "sale_date": "2023-04-14 16:45:00"},
    {"sale_id": 62, "item_id": 1, "buyer_id": 1, "quantity_sold": 18, "sale_price": 189.00,
     "sale_date": "2024-10-06 09:30:00"},
    {"sale_id": 63, "item_id": 2, "buyer_id": 1, "quantity_sold": 22, "sale_price": 54.00,
     "sale_date": "2024-05-14 08:40:00"},
    {"sale_id": 64, "item_id": 3, "buyer_id": 2, "quantity_sold": 50, "sale_price": 75.00,
     "sale_date": "2024-08-30 11:15:00"},
    {"sale_id": 65, "item_id": 4, "buyer_id": 1, "quantity_sold": 30, "sale_price": 60.00,
     "sale_date": "2024-09-15 10:50:00"},
    {"sale_id": 66, "item_id": 5, "buyer_id": 2, "quantity_sold": 40, "sale_price": 72.00,
     "sale_date": "2024-07-25 09:30:00"},
    {"sale_id": 67, "item_id": 1, "buyer_id": 2, "quantity_sold": 60, "sale_price": 630.00,
     "sale_date": "2023-12-01 12:00:00"},
    {"sale_id": 68, "item_id": 2, "buyer_id": 1, "quantity_sold": 80, "sale_price": 200.00,
     "sale_date": "2023-08-16 10:30:00"},
    {"sale_id": 69, "item_id": 3, "buyer_id": 2, "quantity_sold": 20, "sale_price": 30.00,
     "sale_date": "2023-03-11 14:20:00"},
    {"sale_id": 70, "item_id": 4, "buyer_id": 1, "quantity_sold": 25, "sale_price": 45.00,
     "sale_date": "2022-12-05 09:00:00"},
    {"sale_id": 71, "item_id": 5, "buyer_id": 2, "quantity_sold": 18, "sale_price": 32.40,
     "sale_date": "2022-11-12 13:10:00"},
    {"sale_id": 72, "item_id": 1, "buyer_id": 1, "quantity_sold": 15, "sale_price": 157.50,
     "sale_date": "2022-05-01 11:50:00"},
    {"sale_id": 73, "item_id": 2, "buyer_id": 2, "quantity_sold": 75, "sale_price": 187.50,
     "sale_date": "2024-06-09 10:15:00"},
    {"sale_id": 74, "item_id": 3, "buyer_id": 1, "quantity_sold": 12, "sale_price": 18.00,
     "sale_date": "2024-01-29 15:30:00"},
    {"sale_id": 75, "item_id": 4, "buyer_id": 2, "quantity_sold": 45, "sale_price": 81.00,
     "sale_date": "2023-12-24 09:50:00"},
    {"sale_id": 76, "item_id": 5, "buyer_id": 1, "quantity_sold": 25, "sale_price": 50.00,
     "sale_date": "2023-11-12 14:00:00"},
    {"sale_id": 77, "item_id": 1, "buyer_id": 2, "quantity_sold": 55, "sale_price": 577.50,
     "sale_date": "2023-09-06 12:25:00"},
    {"sale_id": 78, "item_id": 2, "buyer_id": 1, "quantity_sold": 80, "sale_price": 200.00,
     "sale_date": "2023-05-21 10:40:00"},
    {"sale_id": 79, "item_id": 3, "buyer_id": 2, "quantity_sold": 68, "sale_price": 102.00,
     "sale_date": "2022-11-15 17:10:00"},
    {"sale_id": 80, "item_id": 4, "buyer_id": 1, "quantity_sold": 40, "sale_price": 72.00,
     "sale_date": "2021-10-05 13:20:00"},
    {"sale_id": 81, "item_id": 5, "buyer_id": 2, "quantity_sold": 35, "sale_price": 63.00,
     "sale_date": "2020-07-17 11:10:00"},
    {"sale_id": 82, "item_id": 1, "buyer_id": 1, "quantity_sold": 25, "sale_price": 262.50,
     "sale_date": "2020-02-13 09:30:00"},
    {"sale_id": 83, "item_id": 2, "buyer_id": 2, "quantity_sold": 95, "sale_price": 237.50,
     "sale_date": "2019-11-01 12:00:00"},
    {"sale_id": 84, "item_id": 3, "buyer_id": 1, "quantity_sold": 32, "sale_price": 48.00,
     "sale_date": "2019-06-21 15:25:00"},
    {"sale_id": 85, "item_id": 4, "buyer_id": 2, "quantity_sold": 52, "sale_price": 93.60,
     "sale_date": "2018-10-07 16:15:00"},
    {"sale_id": 86, "item_id": 5, "buyer_id": 1, "quantity_sold": 42, "sale_price": 75.60,
     "sale_date": "2017-12-01 11:00:00"},
    {"sale_id": 87, "item_id": 1, "buyer_id": 2, "quantity_sold": 38, "sale_price": 399.00,
     "sale_date": "2017-05-18 14:05:00"},
    {"sale_id": 88, "item_id": 2, "buyer_id": 1, "quantity_sold": 100, "sale_price": 250.00,
     "sale_date": "2016-11-22 08:40:00"},
    {"sale_id": 89, "item_id": 3, "buyer_id": 2, "quantity_sold": 25, "sale_price": 37.50,
     "sale_date": "2016-09-10 09:15:00"},
    {"sale_id": 90, "item_id": 4, "buyer_id": 1, "quantity_sold": 60, "sale_price": 108.00,
     "sale_date": "2015-12-02 11:50:00"},
    {"sale_id": 91, "item_id": 5, "buyer_id": 2, "quantity_sold": 18, "sale_price": 32.40,
     "sale_date": "2015-08-14 13:40:00"},
    {"sale_id": 92, "item_id": 1, "buyer_id": 1, "quantity_sold": 10, "sale_price": 105.00,
     "sale_date": "2015-06-21 17:30:00"},
]

# Initialize application context and database session
with app.app_context():
    # Add sales data
    sales_entries = [
        Sale(sale_id=data["sale_id"], item_id=data["item_id"], buyer_id=data["buyer_id"],
             quantity_sold=data["quantity_sold"], sale_price=data["sale_price"],
             sale_date=datetime.strptime(data["sale_date"], "%Y-%m-%d %H:%M:%S"))
        for data in sales_data
    ]

    # Add all sales entries to the session
    db.session.add_all(sales_entries)
    db.session.commit()

print("Sales dummy data added successfully!")
