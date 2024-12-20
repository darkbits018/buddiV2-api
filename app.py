import bcrypt
import matplotlib
import os

from contourpy.util import data
from sqlalchemy.dialects.postgresql import psycopg2

matplotlib.use('Agg')  # Set the non-interactive backend

from flask import Flask, request, jsonify, send_file, json
from sqlalchemy import func, extract
from config import Config
from models import db, Farmer, Item, Sale, Appointment, Buyer, User
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import base64
from datetime import datetime, timedelta, timezone
import io
import matplotlib.pyplot as plt
from flask import Flask, request, send_file
from sqlalchemy import extract
from models import Sale  # Import your Sale model
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from flask_cors import CORS  # Import CORS
import uuid
import matplotlib
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

matplotlib.use('Agg')

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)
CORS(app)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

# Initialize S3 client with credentials from .env file
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


# def generate_invoice(sale_id):
#     # Query sale details
#     sale = Sale.query.get(sale_id)
#     if not sale:
#         return None
#
#     item = Item.query.get(sale.item_id)
#     buyer = Buyer.query.get(sale.buyer_id)
#     farmer = Farmer.query.get(item.farmer_id)
#
#     # Create a PDF buffer
#     buffer = io.BytesIO()
#     pdf = canvas.Canvas(buffer, pagesize=A4)
#     pdf.setTitle(f"Invoice_{sale_id}")
#
#     # Add content to PDF
#     pdf.drawString(100, 800, "Invoice")
#     pdf.drawString(100, 780, f"Invoice ID: {sale_id}")
#     pdf.drawString(100, 760, f"Buyer: {buyer.name}")
#     pdf.drawString(100, 740, f"Farmer: {farmer.name}")
#     pdf.drawString(100, 720, f"Item: {item.item_name}")
#     pdf.drawString(100, 700, f"Quantity: {sale.quantity_sold}")
#     pdf.drawString(100, 680, f"Price per Unit: {item.price}")
#     pdf.drawString(100, 660, f"Total Amount: {sale.sale_price * sale.quantity_sold}")
#     pdf.drawString(100, 640, f"Date: {sale.sale_date}")
#
#     pdf.showPage()
#     pdf.save()
#
#     # Move buffer to the beginning so we can return it
#     buffer.seek(0)
#     return buffer
def upload_image_to_s3(img_buffer, prefix='sales-reports/'):
    """
    Upload an image buffer to S3 and return the public URL.

    :param img_buffer: BytesIO buffer containing the image
    :param prefix: S3 key prefix for the file
    :return: S3 URL of the uploaded image
    """
    try:
        # Generate a unique filename
        unique_filename = f"{prefix}{uuid.uuid4()}.png"

        # Upload the image to S3
        s3_client.upload_fileobj(
            img_buffer,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                'ContentType': 'image/png',
                # 'ACL': 'public-read'  # Make the file publicly readable
            }
        )

        # Construct and return the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        return s3_url

    except ClientError as e:
        app.logger.error(f"Error uploading to S3: {e}")
        return None


# def execute_sql_command(query, params=None):
#     conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI.replace('postgresql://', 'postgresql+psycopg2://'))
#     cursor = conn.cursor()
#     try:
#         cursor.execute(query, params)
#         conn.commit()
#         return True
#     except Exception as e:
#         conn.rollback()
#         print(f"Error executing query: {e}")
#         return False
#     finally:
#         cursor.close()
#         conn.close()

import psycopg2


def execute_sql_command(query, params=None):
    try:
        # Connect to the database using psycopg2
        conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()

        # Fetch result if needed
        result = cur.fetchall() if query.strip().lower().startswith("select") else None

        cur.close()
        conn.close()
        return result
    except Exception as e:
        raise e


def upload_invoice_to_s3(pdf_buffer, prefix='invoice/'):
    """
    Upload a PDF buffer to S3 and return the public URL.

    :param pdf_buffer: BytesIO buffer containing the PDF
    :param prefix: S3 key prefix for the file
    :return: S3 URL of the uploaded PDF
    """
    try:
        # Generate a unique filename
        unique_filename = f"{prefix}{uuid.uuid4()}.pdf"

        # Upload the PDF to S3
        s3_client.upload_fileobj(
            pdf_buffer,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                'ContentType': 'application/pdf',
            }
        )

        # Construct and return the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        return s3_url

    except ClientError as e:
        app.logger.error(f"Error uploading to S3: {e}")
        return None


def generate_invoice(sale_id):
    # Query sale details using session.get()
    sale = db.session.get(Sale, sale_id)
    if not sale:
        return None

    item = db.session.get(Item, sale.item_id)
    buyer = db.session.get(Buyer, sale.buyer_id)
    farmer = db.session.get(Farmer, item.farmer_id)

    # Create a PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Invoice_{sale_id}")

    # Add content to PDF
    pdf.drawString(100, 800, "Invoice")
    pdf.drawString(100, 780, f"Invoice ID: {sale_id}")
    pdf.drawString(100, 760, f"Buyer: {buyer.name}")
    pdf.drawString(100, 740, f"Farmer: {farmer.name}")
    pdf.drawString(100, 720, f"Item: {item.item_name}")
    pdf.drawString(100, 700, f"Quantity: {sale.quantity_sold}")
    pdf.drawString(100, 680, f"Price per Unit: {item.price}")
    pdf.drawString(100, 660, f"Total Amount: {sale.sale_price * sale.quantity_sold}")
    pdf.drawString(100, 640, f"Date: {sale.sale_date}")

    pdf.showPage()
    pdf.save()

    # Reset buffer position
    buffer.seek(0)
    return buffer


def get_jwt_exp_time_utc(access_token):
    from jwt import decode
    from flask import current_app

    secret_key = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')

    decoded_token = decode(access_token, secret_key, algorithms=[algorithm])
    exp_time_utcstamp = decoded_token.get('exp', None)  # Expiration time as timestamp
    if exp_time_utcstamp:
        return datetime.fromtimestamp(exp_time_utcstamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    return None


@app.route('/register', methods=['POST'])
def register_user():
    try:
        # Extract JSON data from the request
        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        # Validate required fields
        required_fields = ['name', 'phone_number', 'email', 'address', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return {"error": f"Field '{field}' is required"}, 400

        # Hash the password
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # Generate the new UID
        uid_query = """
        SELECT CONCAT(
            'u',
            COALESCE(MAX(CAST(SUBSTRING(uid FROM 2) AS INT)), 0) + 1
        ) AS new_uid
        FROM users;
        """
        new_uid_result = execute_sql_command(uid_query)
        new_uid = new_uid_result[0][0] if new_uid_result else None
        if not new_uid:
            raise Exception("Failed to generate new UID.")

        # Insert new user
        insert_user_query = """
        INSERT INTO users (uid, name, phone_number, email, address, password, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING uid;
        """
        params = (
            new_uid,
            data['name'],
            data['phone_number'],
            data['email'],
            data['address'],
            hashed_password,
            data['role']
        )
        print(f"Executing Query: {insert_user_query} with Params: {params}")
        user_uid = execute_sql_command(insert_user_query, params)

        if not user_uid:
            return {"error": "User could not be created"}, 500

        return {"uid": user_uid[0][0]}
    except Exception as e:
        print(f"Error during registration: {e}")
        return {"error": str(e)}, 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Query the User model for the email
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # Define the token expiration duration (e.g., 1 day)
        token_duration = timedelta(days=1)

        # Generate access token
        access_token = create_access_token(identity=user.uid,
                                           expires_delta=token_duration)

        # Convert the duration into a human-readable string
        duration_in_seconds = int(token_duration.total_seconds())
        duration_hours = duration_in_seconds // 3600
        duration_minutes = (duration_in_seconds % 3600) // 60
        duration_str = f"{duration_hours} hours, {duration_minutes} minutes"

        if user.is_farmer():
            farmer = Farmer.query.filter_by(user_id=user.uid).first()
            access_token = create_access_token(
                identity=user.uid)  # Generate JWT token
            exp_time_utc = datetime.now(timezone.utc) + token_duration
            # Convert expiry time to IST
            ist_offset = timedelta(hours=5, minutes=30)
            exp_time_ist = exp_time_utc + ist_offset
            print(f"Access token created: {access_token}, Expiration: {exp_time_ist}")
            return jsonify({
                'message': 'Login successful',
                'role': 'farmer',
                'farmer_id': farmer.user_id if farmer else None,
                'access_token': access_token,
                'token_duration': duration_str,
                'expires_at': exp_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),  # Return formatted expiration time
                'exp_time': exp_time_ist
            })
        elif user.is_buyer():
            buyer = Buyer.query.filter_by(user_id=user.uid).first()
            access_token = create_access_token(
                identity=user.uid)  # Generate JWT token
            exp_time_utc = datetime.now(timezone.utc) + token_duration
            # Convert expiry time to IST
            ist_offset = timedelta(hours=5, minutes=30)
            exp_time_ist = exp_time_utc + ist_offset
            print(f"Access token created: {access_token}, Expiration: {exp_time_utc}")
            return jsonify({
                'message': 'Login successful',
                'role': 'buyer',
                'buyer_id': buyer.user_id if buyer else None,
                'access_token': access_token,
                'token_duration': duration_str,
                'expires_at': exp_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),  # Return formatted expiration time
                'exp_time': exp_time_ist
            })
        else:
            return jsonify({'message': 'Unknown role'}), 400
    return jsonify({'message': 'Invalid email or password'}), 401


# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#
#     # Query the User model for the email
#     user = User.query.filter_by(email=email).first()
#
#     if user and check_password_hash(user.password, password):
#         # Define the token expiration duration (e.g., 1 day)
#         token_duration = timedelta(days=1)
#
#         # Generate access token
#         access_token = create_access_token(
#             identity={"user_id": str(user.uid), "role": user.role},  # Include both user_id and role
#             expires_delta=token_duration
#         )
#
#         # Convert the duration into a human-readable string
#         duration_in_seconds = int(token_duration.total_seconds())
#         duration_hours = duration_in_seconds // 3600
#         duration_minutes = (duration_in_seconds % 3600) // 60
#         duration_str = f"{duration_hours} hours, {duration_minutes} minutes"
#
#         if user.is_farmer():
#             farmer = Farmer.query.filter_by(user_id=user.uid).first()
#             exp_time_utc = datetime.now(timezone.utc) + token_duration
#             ist_offset = timedelta(hours=5, minutes=30)
#             exp_time_ist = exp_time_utc + ist_offset
#             print(f"Access token created: {access_token}, Expiration: {exp_time_ist}")
#             return jsonify({
#                 'message': 'Login successful',
#                 'role': 'farmer',
#                 'farmer_id': farmer.user_id if farmer else None,
#                 'access_token': access_token,
#                 'token_duration': duration_str,
#                 'expires_at': exp_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),
#                 'exp_time': exp_time_ist
#             })
#         elif user.is_buyer():
#             buyer = Buyer.query.filter_by(user_id=user.uid).first()
#             exp_time_utc = datetime.now(timezone.utc) + token_duration
#             ist_offset = timedelta(hours=5, minutes=30)
#             exp_time_ist = exp_time_utc + ist_offset
#             print(f"Access token created: {access_token}, Expiration: {exp_time_ist}")
#             return jsonify({
#                 'message': 'Login successful',
#                 'role': 'buyer',
#                 'buyer_id': buyer.user_id if buyer else None,
#                 'access_token': access_token,
#                 'token_duration': duration_str,
#                 'expires_at': exp_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),
#                 'exp_time': exp_time_ist
#             })
#         else:
#             return jsonify({'message': 'Unknown role'}), 400
#     return jsonify({'message': 'Invalid email or password'}), 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        # If the token is valid and not expired, this endpoint will work
        current_user_role = get_jwt_identity()
        current_user = get_jwt_identity()  # Extract user_id and role
        print(f"Current JWT Identity: {current_user} {current_user_role}")  # Optional, for debugging
        return jsonify({"message": "Token is valid and not expired"}), 200
    except Exception as e:
        # If the token is expired or invalid, return the error
        return jsonify({"message": str(e)}), 401


app.route('/farmers', methods=['POST'])


def create_farmer():
    data = request.get_json()
    farmer = Farmer(name=data['name'], phone_number=data['phone_number'], email=data['email'], address=data['address'])
    db.session.add(farmer)
    db.session.commit()
    return jsonify({"message": "Farmer created successfully", "farmer_id": farmer.farmer_id}), 201


@app.route('/items', methods=['POST'])
@jwt_required()
def add_item():
    user = get_jwt_identity()  # Get the user ID from the token
    data = request.get_json()

    # Ensure the user is a farmer
    farmer = Farmer.query.filter_by(user_id=user).first()
    if not farmer:
        return jsonify({'message': 'Unauthorized access'}), 403

    # Add the item
    item = Item(
        farmer_id=farmer.user_id,
        item_name=data.get('item_name'),
        description=data.get('description'),
        quantity=data.get('quantity'),
        price=data.get('price')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Item added successfully', 'item_id': item.id}), 201


from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route('/items/<int:item_id>', methods=['GET'])
@jwt_required()  # Ensure the request is authenticated
def get_item(item_id):
    current_user_id = get_jwt_identity()  # Get the current logged-in user's ID

    # Fetch item details from the database using item_id
    item = Item.query.filter_by(item_id=item_id).first()

    if item is None:
        return jsonify({"message": "Item not found."}), 404

    # Check if the current logged-in user is the owner of the item
    if item.farmer_id != current_user_id:
        return jsonify({"message": "You do not have access to this item."}), 403

    item_data = {
        "item_name": item.item_name,
        "description": item.description,
        "quantity": item.quantity,
        "price": item.price,
        "farmer_id": item.farmer_id
    }

    return jsonify(item_data)


from flask_jwt_extended import get_jwt_identity, jwt_required


@app.route('/items/farmer', methods=['GET'])
@jwt_required()  # Ensure the request is authenticated
def get_items_by_current_farmer():
    current_user_id = get_jwt_identity()  # Get the current logged-in user's ID

    # Fetch all items for the currently logged-in farmer
    items = Item.query.filter_by(farmer_id=current_user_id).all()

    if not items:
        return jsonify({"message": "No items found for this farmer."}), 404

    items_data = []
    for item in items:
        items_data.append({
            "item_name": item.item_name,
            "description": item.description,
            "quantity": item.quantity,
            "price": item.price,
            "item_id": item.item_id
        })

    return jsonify(items_data)


from flask_jwt_extended import get_jwt_identity, jwt_required


@app.route('/sales', methods=['POST'])
@jwt_required()
def record_sale():
    data = request.get_json()

    # Get the logged-in farmer's ID from the JWT token
    current_farmer_id = get_jwt_identity()

    # Validate buyer_id exists in the buyers table
    buyer = Buyer.query.filter_by(user_id=data['buyer_id']).first()
    if not buyer:
        return jsonify({"error": "Invalid buyer_id"}), 400

    # Fetch the item details using item_id
    item = Item.query.filter_by(item_id=data['item_id']).first()

    if not item:
        return jsonify({"message": "Item not found"}), 404

    # Check if the current farmer owns the item
    if item.farmer_id != current_farmer_id:
        return jsonify({"message": "You are not authorized to sell this item"}), 403

    # Create a new sale record
    sale = Sale(
        item_id=data['item_id'],
        buyer_id=data['buyer_id'],
        quantity_sold=data['quantity_sold'],
        sale_price=data['sale_price'],
        farmer_id=current_farmer_id  # Add the current farmer's ID
    )

    db.session.add(sale)
    db.session.commit()

    return jsonify({
        "message": "Sale recorded successfully",
        "sale_id": sale.sale_id
    }), 201


@app.route('/sales/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    current_user_id = get_jwt_identity()  # Get the currently authenticated user's ID

    # Fetch sale details from the database using sale_id
    sale = Sale.query.filter_by(sale_id=sale_id).first()

    if sale is None:
        return jsonify({"message": "Sale not found."}), 404

    # Authorize based on user role and relationship to the sale
    user = User.query.get(current_user_id)

    if user.is_farmer():
        # A farmer can only view sales related to their items
        item = Item.query.get(sale.item_id)
        if item.farmer_id != current_user_id:
            return jsonify({"message": "Unauthorized to view this sale."}), 403
    elif user.is_buyer():
        # A buyer can only view sales they are part of
        if sale.buyer_id != current_user_id:
            return jsonify({"message": "Unauthorized to view this sale."}), 403

    # Create the response data
    sale_data = {
        "sale_id": sale.sale_id,
        "item_id": sale.item_id,
        "buyer_id": sale.buyer_id,
        "quantity_sold": sale.quantity_sold,
        "sale_price": sale.sale_price,
        "total_sale_amount": sale.quantity_sold * sale.sale_price
    }

    return jsonify(sale_data)


@app.route('/sales/farmer/<string:farmer_id>', methods=['GET'])
@jwt_required()  # Protecting the route with JWT authentication
def get_sales_by_farmer(farmer_id):
    # Convert farmer_id to integer if necessary (in case of any validation logic)
    # try:
    #     farmer_id = int(farmer_id)  # If you are using integer IDs, convert to int.
    # except ValueError:
    #     return jsonify({"error": "Invalid farmer ID"}), 400

    # Fetch all sales for a specific farmer
    sales = db.session.query(Sale).join(Item).filter(Item.farmer_id == farmer_id).all()

    if not sales:
        return jsonify({"message": "No sales found for this farmer."}), 404

    sales_data = []
    for sale in sales:
        sales_data.append({
            "sale_id": sale.sale_id,
            "item_id": sale.item_id,
            "buyer_id": sale.buyer_id,
            "quantity_sold": sale.quantity_sold,
            "sale_price": sale.sale_price,
            "total_sale_amount": sale.quantity_sold * sale.sale_price
        })

    return jsonify(sales_data)


@app.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    appointment = Appointment(farmer_id=data['farmer_id'], buyer_id=data['buyer_id'],
                              appointment_date=data['appointment_date'])
    db.session.add(appointment)
    db.session.commit()
    return jsonify({"message": "Appointment created successfully", "appointment_id": appointment.appointment_id}), 201


@app.route('/appointments/<int:id>', methods=['PUT'])
def update_appointment(id):
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404
    appointment.status = request.json.get('status', appointment.status)
    db.session.commit()
    return jsonify({"message": "Appointment status updated"}), 200


@app.route('/buyers', methods=['POST'])
def create_buyer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    # Extract buyer information from the request
    buyer = Buyer(
        name=data['name'],
        phone_number=data.get('phone_number'),
        email=data.get('email'),
        address=data.get('address')
    )
    db.session.add(buyer)
    db.session.commit()
    return jsonify({"message": "Buyer created successfully", "buyer_id": buyer.buyer_id}), 201


@app.route('/invoices/<int:sale_id>', methods=['GET'])
def download_invoice(sale_id):
    # Generate the invoice PDF as a buffer
    buffer = generate_invoice(sale_id)
    if buffer is None:
        return jsonify({"error": "Sale not found"}), 404

    # Generate an S3 prefix for the invoice
    s3_prefix = f"invoices/{sale_id}/"

    # Upload the PDF to S3 and get the URL
    s3_url = upload_invoice_to_s3(buffer, prefix=s3_prefix)
    if s3_url:
        return jsonify({"invoice_url": s3_url})

    return jsonify({"error": "Failed to upload invoice to S3"}), 500


# Utility function to generate charts
def generate_sales_chart(data, title, xlabel, ylabel):
    labels = [record[0].strftime("%B %Y") for record in data]
    values = [record[1] for record in data]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='skyblue')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return chart_base64


# API endpoint for monthly report
import matplotlib.pyplot as plt
import io
from flask import Response


@app.route('/api/sales/report/monthly', methods=['GET'])
def monthly_sales_report_png():
    current_year = datetime.now().year

    # Query sales data for the current year, grouped by month
    sales_data = db.session.query(
        db.func.extract('month', Sale.sale_date).label('month'),
        db.func.sum(Sale.sale_price * Sale.quantity_sold).label('total_sales')
    ).filter(db.func.extract('year', Sale.sale_date) == current_year)  # Filter by current year
    sales_data = sales_data.group_by('month').all()

    # Prepare the data for the chart
    months = [i for i in range(1, 13)]
    sales = {month: 0 for month in months}
    for month, total_sales in sales_data:
        sales[int(month)] = total_sales

    # Create a bar chart for the monthly sales
    fig, ax = plt.subplots()
    ax.bar(sales.keys(), sales.values())

    ax.set_xlabel('Month')
    ax.set_ylabel('Total Sales')
    ax.set_title(f'Monthly Sales Report ({current_year})')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

    # Save the figure to a BytesIO buffer
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)

    # Generate a unique filename for the image
    image_filename = f'monthly_sales_report_{current_year}.png'

    # Upload the image to S3
    s3_client.upload_fileobj(img_io, S3_BUCKET_NAME, image_filename, ExtraArgs={'ContentType': 'image/png'})

    # Generate the URL of the uploaded image
    image_url = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/{image_filename}'

    # Return the URL of the image
    return {'image_url': image_url}, 200


@app.route('/api/sales/report/yearly', methods=['GET'])
def yearly_sales_report_s3():
    # Query sales data for all years
    sales_data = db.session.query(
        db.func.extract('year', Sale.sale_date).label('year'),
        db.func.sum(Sale.sale_price * Sale.quantity_sold).label('total_sales')
    ).group_by('year').order_by('year').all()  # Group by year and sort by year

    # Prepare the data for the chart
    yearly_sales = {}
    for year, total_sales in sales_data:
        yearly_sales[int(year)] = total_sales  # Ensure the year is an integer

    # Create a line chart for the yearly sales
    fig, ax = plt.subplots()
    ax.plot(list(yearly_sales.keys()), list(yearly_sales.values()), marker='o', linestyle='-', color='blue')

    ax.set_xlabel('Year')
    ax.set_ylabel('Total Sales')
    ax.set_title('Yearly Sales Report')

    # Save the figure to a BytesIO buffer
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close(fig)

    # Upload to S3 and get the URL
    s3_url = upload_image_to_s3(img_io)

    if s3_url:
        return jsonify({
            "report_url": s3_url,
            "years": list(yearly_sales.keys())
        })
    else:
        return jsonify({
            "error": "Failed to generate or upload sales report"
        }), 500


# API endpoint for quarterly report
@app.route('/api/sales/report/quarterly', methods=['GET'])
def quarterly_sales_report_s3():
    current_year = datetime.now().year

    # Query sales data for the current year, grouped by quarter
    sales_data = db.session.query(
        db.case(
            (db.func.extract('month', Sale.sale_date).in_([1, 2, 3]), 1),  # Q1
            (db.func.extract('month', Sale.sale_date).in_([4, 5, 6]), 2),  # Q2
            (db.func.extract('month', Sale.sale_date).in_([7, 8, 9]), 3),  # Q3
            (db.func.extract('month', Sale.sale_date).in_([10, 11, 12]), 4),  # Q4
            else_=0
        ).label('quarter'),
        db.func.sum(Sale.sale_price * Sale.quantity_sold).label('total_sales')
    ).filter(db.func.extract('year', Sale.sale_date) == current_year)  # Filter by current year
    sales_data = sales_data.group_by('quarter').all()

    # Prepare the data for the chart
    quarters = [1, 2, 3, 4]
    quarterly_sales = {quarter: 0 for quarter in quarters}
    for quarter, total_sales in sales_data:
        quarterly_sales[quarter] = total_sales

    # Create a bar chart for the quarterly sales
    fig, ax = plt.subplots()
    ax.bar(quarterly_sales.keys(), quarterly_sales.values())

    ax.set_xlabel('Quarter')
    ax.set_ylabel('Total Sales')
    ax.set_title(f'Quarterly Sales Report ({current_year})')
    ax.set_xticks(range(1, 5))
    ax.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])

    # Save the figure to a BytesIO buffer
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close(fig)

    # Upload to S3 and get the URL
    s3_url = upload_image_to_s3(img_io)

    if s3_url:
        return jsonify({
            "report_url": s3_url,
            "year": current_year
        })
    else:
        return jsonify({
            "error": "Failed to generate or upload sales report"
        }), 500


# API endpoint for specific year report
@app.route('/api/sales/report/year/<int:year>', methods=['GET'])
def sales_report_for_year_png(year):
    sales_data = db.session.query(
        db.func.extract('year', Sale.sale_date).label('year'),
        db.func.sum(Sale.sale_price * Sale.quantity_sold).label('total_sales')
    ).filter(db.func.extract('year', Sale.sale_date) == year).group_by('year').all()

    yearly_sales = {year: total_sales for year, total_sales in sales_data}

    fig, ax = plt.subplots()
    ax.bar(yearly_sales.keys(), yearly_sales.values())
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Sales')
    ax.set_title(f'Sales Report for {year}')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    s3_url = upload_image_to_s3(buf, prefix='sales-year-report/')
    if s3_url:
        return jsonify({"report_url": s3_url})
    return {"error": "Failed to upload sales report to S3"}, 500


@app.route('/api/sales/item-report/monthly', methods=['GET'])
def item_sales_report_monthly():
    current_year = datetime.now().year
    sales = db.session.query(
        extract('month', Sale.sale_date).label('month'),
        Item.item_name,
        db.func.sum(Sale.quantity_sold).label('total_quantity')
    ).join(Sale, Sale.item_id == Item.item_id) \
        .filter(extract('year', Sale.sale_date) == current_year) \
        .group_by(extract('month', Sale.sale_date), Item.item_name) \
        .order_by(extract('month', Sale.sale_date)).all()

    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    items = list(set(sale.item_name for sale in sales))
    item_monthly_sales = {item: [0] * 12 for item in items}

    for sale in sales:
        month = int(sale.month) - 1
        item_monthly_sales[sale.item_name][month] = sale.total_quantity

    fig, ax = plt.subplots(figsize=(10, 6))
    for item, quantities in item_monthly_sales.items():
        ax.plot(months, quantities, label=item)

    ax.set_xlabel('Month')
    ax.set_ylabel('Total Quantity Sold')
    ax.set_title(f"Monthly Sales Report for {current_year}")
    ax.legend(title='Items')

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    # Upload the chart to S3
    s3_url = upload_image_to_s3(buf, prefix='monthly-sales/')
    if s3_url:
        return jsonify({"report_url": s3_url})
    return {"error": "Failed to upload sales report to S3"}, 500


@app.route('/api/sales/item-report/yearly', methods=['GET'])
def item_sales_report_yearly():
    sales = db.session.query(
        extract('year', Sale.sale_date).label('year'),
        Item.item_name,
        db.func.sum(Sale.quantity_sold).label('total_quantity')
    ).join(Sale, Sale.item_id == Item.item_id) \
        .group_by(extract('year', Sale.sale_date), Item.item_name) \
        .order_by(extract('year', Sale.sale_date)).all()

    years = sorted(list(set(sale.year for sale in sales)))
    items = sorted(list(set(sale.item_name for sale in sales)))
    item_yearly_sales = {item: [0] * len(years) for item in items}

    for sale in sales:
        year_index = years.index(sale.year)
        item_yearly_sales[sale.item_name][year_index] = sale.total_quantity

    bar_width = 0.8 / len(items)
    x_positions = range(len(years))

    fig, ax = plt.subplots(figsize=(12, 8))
    for i, (item, quantities) in enumerate(item_yearly_sales.items()):
        offsets = [pos + i * bar_width for pos in x_positions]
        ax.bar(offsets, quantities, bar_width, label=item)

    ax.set_xticks([pos + (len(items) - 1) * bar_width / 2 for pos in x_positions])
    ax.set_xticklabels(years)
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Quantity Sold')
    ax.set_title("Yearly Sales Report")
    ax.legend(title='Items')

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    # Upload the chart to S3
    s3_url = upload_image_to_s3(buf, prefix='yearly-sales/')
    if s3_url:
        return jsonify({"report_url": s3_url})
    return {"error": "Failed to upload sales report to S3"}, 500


@app.route('/api/sales/item-report/quarterly', methods=['GET'])
def item_sales_report_quarterly():
    sales = db.session.query(
        extract('quarter', Sale.sale_date).label('quarter'),
        Item.item_name,
        db.func.sum(Sale.quantity_sold).label('total_quantity')
    ).join(Sale, Sale.item_id == Item.item_id) \
        .group_by(extract('quarter', Sale.sale_date), Item.item_name) \
        .order_by(extract('quarter', Sale.sale_date)).all()

    quarters = [1, 2, 3, 4]
    items = sorted(list(set(sale.item_name for sale in sales)))
    item_quarterly_sales = {item: [0] * 4 for item in items}

    for sale in sales:
        quarter = int(sale.quarter) - 1
        item_quarterly_sales[sale.item_name][quarter] = sale.total_quantity

    bar_width = 0.8 / len(items)
    x_positions = range(len(quarters))

    fig, ax = plt.subplots(figsize=(12, 8))
    for i, (item, quantities) in enumerate(item_quarterly_sales.items()):
        offsets = [pos + i * bar_width for pos in x_positions]
        ax.bar(offsets, quantities, bar_width, label=item)

    ax.set_xticks([pos + (len(items) - 1) * bar_width / 2 for pos in x_positions])
    ax.set_xticklabels([f"Q{q}" for q in quarters])
    ax.set_xlabel('Quarter')
    ax.set_ylabel('Total Quantity Sold')
    ax.set_title("Quarterly Sales Report")
    ax.legend(title='Items')

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    # Upload the chart to S3
    s3_url = upload_image_to_s3(buf, prefix='quarterly-sales/')
    if s3_url:
        return jsonify({"report_url": s3_url})
    return {"error": "Failed to upload sales report to S3"}, 500


@app.route('/api/sales/item-report/year/<int:year>', methods=['GET'])
def item_sales_report_specific_year(year):
    sales = db.session.query(
        Item.item_name,
        db.func.sum(Sale.quantity_sold).label('total_quantity')
    ).join(Sale, Sale.item_id == Item.item_id) \
        .filter(extract('year', Sale.sale_date) == year) \
        .group_by(Item.item_name) \
        .order_by(Item.item_name).all()

    items = [sale.item_name for sale in sales]
    quantities = [sale.total_quantity for sale in sales]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(items, quantities, color='skyblue')
    ax.set_xlabel('Items')
    ax.set_ylabel('Total Quantity Sold')
    ax.set_title(f"Sales Report for {year}")
    ax.set_xticks(range(len(items)))
    ax.set_xticklabels(items, rotation=45, ha='right')

    for i, quantity in enumerate(quantities):
        ax.text(i, quantity + 0.5, str(quantity), ha='center', va='bottom')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    # Upload the chart to S3
    s3_url = upload_image_to_s3(buf, prefix=f'yearly-sales/{year}/')
    if s3_url:
        return jsonify({"report_url": s3_url})
    return {"error": "Failed to upload sales report to S3"}, 500


@app.route('/api/sales/item-report/month/<int:year>/<int:month>', methods=['GET'])
def item_sales_report_specific_month(year, month):
    sales = db.session.query(
        Item.item_name,
        db.func.sum(Sale.quantity_sold).label('total_quantity')
    ).join(Sale, Sale.item_id == Item.item_id) \
        .filter(extract('year', Sale.sale_date) == year) \
        .filter(extract('month', Sale.sale_date) == month) \
        .group_by(Item.item_name) \
        .order_by(Item.item_name).all()

    items = [sale.item_name for sale in sales]
    quantities = [sale.total_quantity for sale in sales]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(items, quantities, color='skyblue')
    ax.set_xlabel('Items')
    ax.set_ylabel('Total Quantity Sold')
    ax.set_title(f"Sales Report for {month}/{year}")
    ax.set_xticks(range(len(items)))
    ax.set_xticklabels(items, rotation=45, ha='right')

    for i, quantity in enumerate(quantities):
        ax.text(i, quantity + 0.5, str(quantity), ha='center', va='bottom')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    # Upload the chart to S3
    s3_url = upload_image_to_s3(buf, prefix=f'monthly-sales/{year}/{month}/')
    if s3_url:
        return jsonify({"report_url": s3_url})
    return {"error": "Failed to upload sales report to S3"}, 500


@app.route('/sales_trends/<int:item_id>', methods=['GET'])
def sales_trend_s3(item_id):
    # Query for the item name and its sales
    item = Item.query.get(item_id)
    if not item:
        return {"error": "Item not found"}, 404

    sales_data = (
        db.session.query(Sale.sale_date, Sale.quantity_sold)
        .filter(Sale.item_id == item_id)
        .order_by(Sale.sale_date)
        .all()
    )

    # Organize sales data by year
    sales_by_year = {}
    for sale in sales_data:
        year = sale.sale_date.year
        sales_by_year[year] = sales_by_year.get(year, 0) + sale.quantity_sold

    # Generate plot
    years = list(sales_by_year.keys())
    quantities = list(sales_by_year.values())

    fig, ax = plt.subplots()
    ax.plot(years, quantities, marker='o', color='b')
    ax.set_title(f'Sales Trend for {item.item_name}')
    ax.set_xlabel('Year')
    ax.set_ylabel('Quantity Sold')
    ax.grid(True)

    # Save the plot to a BytesIO object as PNG
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close(fig)
    img_buffer.seek(0)

    # Upload to S3 and get the URL
    s3_url = upload_image_to_s3(img_buffer)

    if s3_url:
        return jsonify({
            "report_url": s3_url,
            "item_name": item.item_name,
            "item_id": item_id
        })
    else:
        return jsonify({
            "error": "Failed to generate or upload sales trend"
        }), 500


@app.route('/sales-trends-all', methods=['GET'])
def sales_trends_all():
    with app.app_context():
        items = db.session.query(Item).all()
        if not items:
            return {"error": "No items found in the database"}, 404

        sales_data = {}
        for item in items:
            item_id = item.item_id
            item_name = item.item_name
            yearly_sales = db.session.query(
                extract('year', Sale.sale_date).label('year'),
                db.func.sum(Sale.quantity_sold).label('total_quantity')
            ).filter(Sale.item_id == item_id).group_by('year').order_by('year').all()

            if not yearly_sales:
                continue
            df = pd.DataFrame(yearly_sales, columns=['Year', 'Total Quantity Sold'])
            sales_data[item_name] = df

    fig, axs = plt.subplots(len(sales_data), 1, figsize=(10, 6 * len(sales_data)), squeeze=False)
    fig.subplots_adjust(hspace=0.4)

    for idx, (item_name, df) in enumerate(sales_data.items()):
        ax = axs[idx, 0]
        ax.bar(df['Year'], df['Total Quantity Sold'], color='skyblue')
        ax.set_title(f'Sales Trend for {item_name}')
        ax.set_xlabel('Year')
        ax.set_ylabel('Total Quantity Sold')
        ax.grid(axis='y')
        for i, quantity in enumerate(df['Total Quantity Sold']):
            ax.text(df['Year'][i], quantity + 0.5, str(quantity), ha='center', va='bottom')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    # Upload to S3
    s3_url = upload_image_to_s3(buf, prefix='sales-trends/')
    if s3_url:
        return jsonify({"report_url": s3_url})
    return {"error": "Failed to upload sales report to S3"}, 500


if __name__ == '__main__':
    app.run(debug=True)
