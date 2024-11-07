import matplotlib

matplotlib.use('Agg')  # Set the non-interactive backend

from flask import Flask, request, jsonify, send_file
from sqlalchemy import func, extract
from config import Config
from models import db, Farmer, Item, Sale, Appointment, Buyer
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import base64
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


def generate_invoice(sale_id):
    # Query sale details
    sale = Sale.query.get(sale_id)
    if not sale:
        return None

    item = Item.query.get(sale.item_id)
    buyer = Buyer.query.get(sale.buyer_id)
    farmer = Farmer.query.get(item.farmer_id)

    # Create a PDF buffer
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

    # Move buffer to the beginning so we can return it
    buffer.seek(0)
    return buffer


@app.route('/farmers', methods=['POST'])
def create_farmer():
    data = request.get_json()
    farmer = Farmer(name=data['name'], phone_number=data['phone_number'], email=data['email'], address=data['address'])
    db.session.add(farmer)
    db.session.commit()
    return jsonify({"message": "Farmer created successfully", "farmer_id": farmer.farmer_id}), 201


@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    item = Item(farmer_id=data['farmer_id'], item_name=data['item_name'], description=data.get('description', ''),
                quantity=data['quantity'], price=data['price'])
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Item added successfully", "item_id": item.item_id}), 201


@app.route('/sales', methods=['POST'])
def record_sale():
    data = request.get_json()
    sale = Sale(item_id=data['item_id'], buyer_id=data['buyer_id'], quantity_sold=data['quantity_sold'],
                sale_price=data['sale_price'])
    db.session.add(sale)
    db.session.commit()
    return jsonify({"message": "Sale recorded successfully", "sale_id": sale.sale_id}), 201


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
    buffer = generate_invoice(sale_id)
    if buffer is None:
        return jsonify({"error": "Sale not found"}), 404

    return send_file(buffer, as_attachment=True, download_name=f"Invoice_{sale_id}.pdf", mimetype='application/pdf')


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

    # Save the figure to a BytesIO buffer and send it as PNG
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')


# API endpoint for yearly report
@app.route('/api/sales/report/yearly', methods=['GET'])
def yearly_sales_report_png():
    current_year = datetime.now().year

    # Query sales data for the current year
    sales_data = db.session.query(
        db.func.extract('year', Sale.sale_date).label('year'),
        db.func.sum(Sale.sale_price * Sale.quantity_sold).label('total_sales')
    ).filter(db.func.extract('year', Sale.sale_date) == current_year)  # Filter by current year
    sales_data = sales_data.group_by('year').all()

    # Prepare the data for the chart
    yearly_sales = {}
    for year, total_sales in sales_data:
        yearly_sales[year] = total_sales

    # Create a bar chart for the yearly sales
    fig, ax = plt.subplots()
    ax.bar(yearly_sales.keys(), yearly_sales.values())

    ax.set_xlabel('Year')
    ax.set_ylabel('Total Sales')
    ax.set_title(f'Yearly Sales Report ({current_year})')

    # Save the figure to a BytesIO buffer and send it as PNG
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')


# API endpoint for quarterly report
@app.route('/api/sales/report/quarterly', methods=['GET'])
def quarterly_sales_report_png():
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

    # Save the figure to a BytesIO buffer and send it as PNG
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')


# API endpoint for specific month/year report

@app.route('/api/sales/report/specific-month-png', methods=['GET'])
def sales_report_for_month_of_year_png():
    # Retrieve year and month from the query parameters
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    # Ensure both parameters are provided
    if not year or not month:
        return jsonify({"error": "Both 'year' and 'month' parameters are required."}), 400

    # Your query logic here
    # Generate the sales report for a specific month of a specific year
    sales_data = db.session.query(
        func.extract('month', Sale.sale_date).label('month'),
        func.sum(Sale.quantity_sold).label('total_quantity_sold')
    ).filter(
        func.extract('year', Sale.sale_date) == year,
        func.extract('month', Sale.sale_date) == month
    ).group_by('month').all()

    # If no data found, return an error
    if not sales_data:
        return jsonify({"error": "No sales data found for the specified month and year."}), 404

    # Here, create the chart (PNG image) from the `sales_data`
    # Example of creating a basic bar chart and saving it as a PNG image
    months = [str(record.month) for record in sales_data]
    quantities_sold = [record.total_quantity_sold for record in sales_data]

    plt.bar(months, quantities_sold)
    plt.title(f"Sales Report for {month}/{year}")
    plt.xlabel("Month")
    plt.ylabel("Total Quantity Sold")

    # Save the plot to a BytesIO object instead of a file
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Return the PNG image
    return send_file(img, mimetype='image/png')


# API endpoint for specific year report
@app.route('/api/sales/report/year/<int:year>', methods=['GET'])
def sales_report_for_year_png(year):
    # Query sales data for the specified year
    sales_data = db.session.query(
        db.func.extract('year', Sale.sale_date).label('year'),
        db.func.sum(Sale.sale_price * Sale.quantity_sold).label('total_sales')
    ).filter(db.func.extract('year', Sale.sale_date) == year)  # Filter by specified year
    sales_data = sales_data.group_by('year').all()

    # Prepare the data for the chart
    yearly_sales = {}
    for year, total_sales in sales_data:
        yearly_sales[year] = total_sales

    # Create a bar chart for the specified year
    fig, ax = plt.subplots()
    ax.bar(yearly_sales.keys(), yearly_sales.values())

    ax.set_xlabel('Year')
    ax.set_ylabel('Total Sales')
    ax.set_title(f'Sales Report for {year}')

    # Save the figure to a BytesIO buffer and send it as PNG
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)

    return Response(img_io, mimetype='image/png')


@app.route('/api/sales/item-report/monthly', methods=['GET'])
def item_sales_report_monthly():
    # Get the current year (you can modify this to take from request if needed)
    current_year = datetime.now().year

    # Query the database to get sales data by item and month
    sales = db.session.query(
        extract('month', Sale.sale_date).label('month'),
        Item.item_name,
        db.func.sum(Sale.quantity_sold).label('total_quantity')
    ).join(Sale, Sale.item_id == Item.item_id) \
        .filter(extract('year', Sale.sale_date) == current_year) \
        .group_by(extract('month', Sale.sale_date), Item.item_name) \
        .order_by(extract('month', Sale.sale_date)).all()

    # Prepare data for the chart
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    items = list(set(sale.item_name for sale in sales))

    # Create a dictionary to hold monthly sales for each item
    item_monthly_sales = {item: [0] * 12 for item in items}

    # Populate the dictionary with sales data
    for sale in sales:
        month = int(sale.month) - 1  # Convert month to integer and adjust to 0-indexed
        item_monthly_sales[sale.item_name][month] = sale.total_quantity

    # Create the chart
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot data for each item
    for item, quantities in item_monthly_sales.items():
        ax.plot(months, quantities, label=item)

    # Set chart labels and title
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Quantity Sold')
    ax.set_title(f"Monthly Sales Report for {current_year}")
    ax.legend(title='Items')

    # Save the figure to a PNG buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Return the PNG image as a response
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
