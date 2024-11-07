from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, Farmer, Item, Sale, Appointment, Buyer
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from flask import send_file

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


if __name__ == '__main__':
    app.run(debug=True)
