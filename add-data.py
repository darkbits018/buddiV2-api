import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Load environment variables for DATABASE_URL
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Fetch all item_ids and buyer_ids
item_ids = session.execute(text("SELECT item_id FROM items")).fetchall()
buyer_ids = session.execute(text("SELECT user_id FROM buyers")).fetchall()

# Flatten fetched data
item_ids = [row.item_id for row in item_ids]
buyer_ids = [row.user_id for row in buyer_ids]

# Generate random sales data
sales_data = []
for _ in range(1000):
    random_item_id = random.choice(item_ids)
    random_buyer_id = random.choice(buyer_ids)
    random_quantity_sold = random.randint(1, 10)  # Between 1 and 10
    random_sale_price = round(random.uniform(5.0, 25.0), 2)  # Between 5.00 and 25.00

    # Random sale_date between 2021-01-01 and 2024-12-31
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 12, 31)
    random_sale_date = start_date + timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds()))
    )

    # Append to sales data list
    sales_data.append(
        {
            "item_id": random_item_id,
            "buyer_id": random_buyer_id,
            "quantity_sold": random_quantity_sold,
            "sale_price": random_sale_price,
            "sale_date": random_sale_date,
        }
    )

# Insert data into the sales table
try:
    for sale in sales_data:
        session.execute(
            text(
                """
                INSERT INTO sales (item_id, buyer_id, quantity_sold, sale_price, sale_date)
                VALUES (:item_id, :buyer_id, :quantity_sold, :sale_price, :sale_date)
                """
            ),
            sale,
        )
    session.commit()
    print("Successfully seeded sales data!")
except Exception as e:
    session.rollback()
    print(f"Error occurred: {e}")
finally:
    session.close()
