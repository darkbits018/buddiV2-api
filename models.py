from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'farmer' or 'buyer'

    # Relationship back to Farmer or Buyer models
    farmer = db.relationship('Farmer', backref='user', uselist=False, foreign_keys='Farmer.user_id')
    buyer = db.relationship('Buyer', backref='user', uselist=False, foreign_keys='Buyer.user_id')

    def is_farmer(self):
        return self.role == 'farmer'

    def is_buyer(self):
        return self.role == 'buyer'


class Farmer(db.Model):
    __tablename__ = 'farmers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)


class Buyer(db.Model):
    __tablename__ = 'buyers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), primary_key=True)
    # Other fields if any


class Item(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.String(50), db.ForeignKey('farmers.user_id'), nullable=False)  # Change to VARCHAR
    item_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class Sale(db.Model):
    __tablename__ = 'sales'
    sale_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)  # Updated to reference users.uid
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    farmer_id = db.Column(db.String, db.ForeignKey('users.uid'), nullable=False)

    # Relationships
    buyer = db.relationship('User', backref='purchases', foreign_keys=[buyer_id])  # Add relationship for buyer
    farmer = db.relationship('User', backref='sales', foreign_keys=[farmer_id])  # Existing relationship for farmer
    item = db.relationship('Item', backref='sales')


class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.farmer_id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.buyer_id'))
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Pending')
