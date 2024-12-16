import psycopg2
from config import Config


def execute_sql_command(query, params=None):
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        print("Query executed successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error executing query: {e}")
    finally:
        cursor.close()
        conn.close()


# Create farmers table
create_farmers_table_query = """
CREATE TABLE farmers (
    farmer_id VARCHAR(10) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(uid)
);
"""

# Create buyers table
create_buyers_table_query = """
CREATE TABLE buyers (
    buyer_id VARCHAR(10) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(uid)
);
"""

# Insert farmers
insert_farmers_query = """
INSERT INTO farmers (farmer_id, user_id)
SELECT 'f' || row_number() over()::text, uid
FROM users
WHERE role = 'farmer';
"""

# Insert buyers
insert_buyers_query = """
INSERT INTO buyers (buyer_id, user_id)
SELECT 'b' || row_number() over()::text, uid
FROM users
WHERE role = 'buyer';
"""

# Execute the queries
execute_sql_command(create_farmers_table_query)
execute_sql_command(create_buyers_table_query)
execute_sql_command(insert_farmers_query)
execute_sql_command(insert_buyers_query)
