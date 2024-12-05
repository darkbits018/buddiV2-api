from flask import Flask, request, jsonify, send_file, json
from sqlalchemy import func, extract
from config import Config
from models import db, Farmer, Item, Sale, Appointment, Buyer
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import base64
from datetime import datetime
import io
import matplotlib.pyplot as plt
from flask import Flask, request, send_file
from sqlalchemy import extract
from models import Sale  # Import your Sale model
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from flask_cors import CORS  # Import CORS
import os
import uuid
import matplotlib
matplotlib.use('Agg')
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app)

# Initialize S3 client with credentials from .env file
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


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


# Example for sales trend for a specific item
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


if __name__ == '__main__':
    app.run(debug=True)
