from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Define the Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'



# Define the VehicleRental model
class VehicleRental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    # Removed the image field

    def __repr__(self):
        return f'<VehicleRental {self.name}>'

# Define the VehicleRentalOrder model
class VehicleRentalOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('vehicle_rental.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rental_duration = db.Column(db.String(50), nullable=False)
    driver_required = db.Column(db.Boolean, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    from_date = db.Column(db.Date, nullable=False)  # New field
    to_date = db.Column(db.Date, nullable=False)    # New field
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    rental = db.relationship('VehicleRental', backref='rental_orders')
    customer = db.relationship('User', backref='vehicle_rental_orders')


class Granite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price_per_sqft = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)  # New column for image URL

    def __repr__(self):
        return f'<Granite {self.name}>'

class GraniteOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    order_date = db.Column(db.DateTime, default=datetime.utcnow)  # Order date
    total_amount = db.Column(db.Float, nullable=False)  # Total amount for the order

    # Relationships
    customer = db.relationship('User', backref='granite_orders')

    def __repr__(self):
        return f'<GraniteOrder {self.id}>'


class GraniteOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('granite_order.id'), nullable=False)  # Foreign key to GraniteOrder
    granite_id = db.Column(db.Integer, db.ForeignKey('granite.id'), nullable=False)  # Foreign key to Granite
    square_feet = db.Column(db.Float, nullable=False)  # Square feet of granite ordered
    amount = db.Column(db.Float, nullable=False)  # Amount for this item

    # Relationships
    order = db.relationship('GraniteOrder', backref='order_items')
    granite = db.relationship('Granite', backref='order_items')
    fabrication = db.relationship('Fabrication', back_populates='order_item', uselist=False)

    def __repr__(self):
        return f'<GraniteOrderItem {self.id}>'

class Fabrication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey('granite_order_item.id'), nullable=False)
    edging = db.Column(db.String(50), nullable=False)
    thickness = db.Column(db.String(50), nullable=False)
    shaping = db.Column(db.String(50), nullable=False)
    fabrication_fee = db.Column(db.Float, nullable=False)

    # Relationship with GraniteOrderItem
    order_item = db.relationship('GraniteOrderItem', back_populates='fabrication')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    total_amount = db.Column(db.Float, nullable=False)  # Total amount for the booking
    discount_amount = db.Column(db.Float, nullable=False, default=0.0)  # Discount applied to the booking

    # Relationship with User and ProductBooked
    customer = db.relationship('User', backref='bookings')
    products_booked = db.relationship('ProductBooked', back_populates='booking', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Booking {self.id}>'


class ProductBooked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)  # Foreign key to Booking
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete="CASCADE"), nullable=False)  # Foreign key to Product
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the product booked

    # Relationships
    booking = db.relationship('Booking', back_populates='products_booked')
    product = db.relationship('Product', backref=db.backref('products_booked', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<ProductBooked {self.id}>'

