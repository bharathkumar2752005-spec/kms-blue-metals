from flask import Flask, render_template, redirect, url_for, session, request, flash
from models import db, Product, User, Booking, ProductBooked, VehicleRental, VehicleRentalOrder, Granite, GraniteOrder, GraniteOrderItem, Fabrication  # Import db, Product, User, Order, VehicleRental, and VehicleRentalOrder from models.py
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stone_crusher.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

@app.before_request
def populate_vehicle_rental():
    if not VehicleRental.query.first():  # Check if the table is empty
        sample_vehicles = [
            VehicleRental(name="Tractor", hourly_rate=160, daily_rate=1500),
            VehicleRental(name="Lorry", hourly_rate=200, daily_rate=2100),
            VehicleRental(name="JCB", hourly_rate=270, daily_rate=4000),
            VehicleRental(name="Hitach", hourly_rate=250, daily_rate=3550),
            VehicleRental(name="Tipper", hourly_rate=250, daily_rate=2400),
            VehicleRental(name="Crane", hourly_rate=300, daily_rate=3700),
        ]
        db.session.bulk_save_objects(sample_vehicles)
        db.session.commit()

@app.before_request
def populate_granite():
    if not Granite.query.first():  # Check if the table is empty
        granite_types = [
            Granite(name="Black Granite", price_per_sqft=140, image_url="/static/pics/black.jpg"),
            Granite(name="White Granite", price_per_sqft=180, image_url="/static/pics/white.jpg"),
            Granite(name="Red Granite", price_per_sqft=200, image_url="/static/pics/red.jpg"),
            Granite(name="Grey Granite", price_per_sqft=170, image_url="/static/pics/grey.jpg"),
            Granite(name="Brown Granite", price_per_sqft=180, image_url="/static/pics/brown.jpg"),
            Granite(name="Gold Granite", price_per_sqft=210, image_url="/static/pics/gold.jpg"),
        ]
        db.session.bulk_save_objects(granite_types)
        db.session.commit()


@app.route('/granite_shop')
def granite_shop():
    granites = Granite.query.all()  # Fetch all granite types from the database
    return render_template('granite_shop.html', granites=granites)

@app.route('/order_granite', methods=['GET', 'POST'])
def order_granite():
    if request.method == 'GET':
        granite_id = request.args.get('granite_id')
        granite = Granite.query.get(granite_id)
        if not granite:
            flash('Invalid granite selection!', 'error')
            return redirect(url_for('granite_shop'))
        return render_template('order_granite.html', granite=granite)

    # Handle POST request
    granite_id = request.form.get('granite_id')
    square_feet = request.form.get('square_feet')

    granite = Granite.query.get(granite_id)
    if not granite:
        flash('Invalid granite selection!', 'error')
        return redirect(url_for('granite_shop'))

    if 'user_id' not in session:
        flash('You need to log in to place an order.', 'error')
        return redirect(url_for('login'))

    customer_id = session['user_id']
    total_amount = granite.price_per_sqft * float(square_feet)

    # Save the order to the database
    new_order = GraniteOrder(
        customer_id=customer_id,
        granite_id=granite.id,
        square_feet=square_feet,
        total_amount=total_amount
    )
    db.session.add(new_order)
    db.session.commit()

    # Prepare order details for display
    order_details = {
        'granite_name': granite.name,
        'price_per_sqft': granite.price_per_sqft,
        'square_feet': square_feet,
        'total_price': total_amount
    }

    return render_template('order_details.html', order_details=order_details)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')  # Create about.html in the templates folder

@app.route('/help')
def help():
    return render_template('help.html')  # Create helps.html in the templates folder

@app.route('/service')
def service():
    return render_template('service.html')  # Create service.html in the templates folder

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user is an admin
        if email == 'admin@example.com' and password == 'admin123':  # Replace with your admin credentials
            session['user_id'] = 'admin'
            session['user_name'] = 'Admin'
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('home'))  # Redirect admin to profile page

        # Check if the user is a regular user
        user = User.query.filter_by(email=email).first()
        if not user or user.password != password:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['is_admin'] = False
        flash('Login successful! Welcome back, {}.'.format(user.name), 'success')
        return redirect(url_for('home'))  # Redirect customer to profile page

    # If the user is already logged in, redirect to the appropriate page
    if 'user_id' in session:
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))  # Redirect to home page after logout

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/fourcategory')
def fourcategory():
    products = Product.query.all()  # Fetch all products from the database
    return render_template('fourcategory.html', products=products)

@app.route('/shop')
def shop():
    products = Product.query.all()  # Fetch all products from the database
    return render_template('shop.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if session.get('is_admin'):
        flash('Admins cannot purchase products.', 'error')
        return redirect(url_for('shop'))

    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    session['cart'] = cart
    return redirect(url_for('shop'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    products = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            products.append({
                'id': product.id,
                'name': product.name,
                'unit': product.unit,
                'price_per_unit': product.price_per_unit,
                'quantity': quantity,
                'total_price': product.price_per_unit * quantity
            })
            total_price += product.price_per_unit * quantity
    return render_template('cart.html', products=products, total_price=total_price)

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/increase_quantity/<int:product_id>')
def increase_quantity(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/decrease_quantity/<int:product_id>')
def decrease_quantity(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            del cart[str(product_id)]  # Remove the product if quantity becomes 0
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if session.get('is_admin'):
        flash('Admins cannot purchase products.', 'error')
        return redirect(url_for('shop'))

    if 'user_id' not in session:
        flash('You need to log in to place an order.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart = session.get('cart', {})
    total_amount = 0
    total_discount = 0
    order_details = []

    try:
        # Calculate total amount and discount
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                if int(product.unit) < quantity:
                    flash(f"Not enough stock for {product.name}.", "error")
                    return redirect(url_for('cart'))

                total_price = product.price_per_unit * quantity
                discount = total_price * 0.10  # 10% discount
                discounted_price = total_price - discount
                total_amount += discounted_price
                total_discount += discount

                # Deduct the purchased quantity from the product's stock
                product.unit = str(int(product.unit) - quantity)

                # Add to order details for display
                order_details.append({
                    'name': product.name,
                    'unit': product.unit,
                    'price_per_unit': product.price_per_unit,
                    'quantity': quantity,
                    'total_price': discounted_price,
                    'discount': discount
                })

        # Create a new Booking
        new_booking = Booking(
            customer_id=user_id,
            total_amount=total_amount,
            discount_amount=total_discount
        )
        db.session.add(new_booking)
        db.session.commit()

        # Add products to ProductBooked
        for product_id, quantity in cart.items():
            new_product_booked = ProductBooked(
                booking_id=new_booking.id,
                product_id=int(product_id),
                quantity=quantity
            )
            db.session.add(new_product_booked)

        db.session.commit()

        # Clear the cart after checkout
        session.pop('cart', None)

        flash('Order placed successfully with a 10% discount!', 'success')
        return render_template('checkout.html', order_details=order_details, total_discount=total_discount)

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred during checkout: {str(e)}", 'error')
        return redirect(url_for('cart'))

@app.route('/granite_cart')
def granite_cart():
    granite_cart = session.get('granite_cart', {})
    total_price = sum(
        item['price_per_sqft'] * item['square_feet'] for item in granite_cart.values()
    )
    return render_template('granite_cart.html', granite_cart=granite_cart, total_price=total_price)

@app.route('/add_granite_to_cart/<int:granite_id>', methods=['POST'])
def add_granite_to_cart(granite_id):
    if 'granite_cart' not in session:
        session['granite_cart'] = {}
    granite_cart = session['granite_cart']
    square_feet = request.form.get('square_feet', 1, type=int)

    if str(granite_id) in granite_cart:
        granite_cart[str(granite_id)]['square_feet'] += square_feet
    else:
        granite = Granite.query.get(granite_id)
        if not granite:
            flash('Invalid granite selection!', 'error')
            return redirect(url_for('granite_shop'))
        granite_cart[str(granite_id)] = {
            'name': granite.name,
            'price_per_sqft': granite.price_per_sqft,
            'square_feet': square_feet
        }
    session['granite_cart'] = granite_cart
    flash('Granite added to cart!', 'success')
    return redirect(url_for('granite_shop'))


@app.route('/remove_granite_from_cart/<int:granite_id>')
def remove_granite_from_cart(granite_id):
    granite_cart = session.get('granite_cart', {})
    if str(granite_id) in granite_cart:
        del granite_cart[str(granite_id)]
    session['granite_cart'] = granite_cart
    flash('Granite removed from cart.', 'success')
    return redirect(url_for('granite_cart'))



@app.route('/details')
def details():
    return render_template('details.html')  # Create details.html in the templates folder

# Add this route to handle adding products
@app.route('/add_product', methods=['POST'])
def add_product():
    if not session.get('is_admin'):
        flash('Access denied! Admins only.', 'error')
        return redirect(url_for('login'))

    name = request.form.get('name')
    unit = request.form.get('unit')
    price_per_unit = request.form.get('price_per_unit')

    # Validate form data
    if not name or not unit or not price_per_unit:
        flash('All fields are required!', 'error')
        return redirect(url_for('add_product_page'))

    try:
        price_per_unit = float(price_per_unit)
    except ValueError:
        flash('Price per unit must be a valid number!', 'error')
        return redirect(url_for('add_product_page'))

    # Create a new product and add it to the database
    new_product = Product(name=name, unit=unit, price_per_unit=price_per_unit)
    db.session.add(new_product)
    db.session.commit()

    flash('Product added successfully!', 'success')
    return redirect(url_for('add_product_page'))

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    address = request.form.get('address')
    phone = request.form.get('phone')
    password = request.form.get('password')

    # Check if the user already exists
    if User.query.filter_by(email=email).first():
        flash('Email already registered!', 'error')
        return redirect(url_for('login'))

    # Create a new user
    new_user = User(name=name, email=email, address=address, phone=phone, password=password)
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful! Please log in.', 'success')
    return redirect(url_for('login'))

@app.route('/vehicle_rent')
def vehicle_rent():
    vehicles = VehicleRental.query.all()  # Fetch all vehicles from the database
    return render_template('vehicle_rent.html', vehicles=vehicles)

@app.route('/rent_vehicle', methods=['POST'])
def rent_vehicle():
    if 'user_id' not in session:
        flash('You need to log in to rent a vehicle.', 'error')
        return redirect(url_for('login'))

    # Get form data
    customer_id = session['user_id']
    vehicle_id = request.form.get('vehicle_id')
    rental_duration = request.form.get('rental_duration')
    driver_required = request.form.get('driver_required') == 'true'
    amount = float(request.form.get('amount'))
    from_date = request.form.get('from_date')  # New field
    to_date = request.form.get('to_date')      # New field

    # Validate dates
    if not from_date or not to_date:
        flash('Please select both "from" and "to" dates.', 'error')
        return redirect(url_for('vehicle_rent'))

    # Save the rental order to the database
    new_order = VehicleRentalOrder(
        rental_id=vehicle_id,
        customer_id=customer_id,
        rental_duration=rental_duration,
        driver_required=driver_required,
        amount=amount,
        from_date=datetime.strptime(from_date, '%Y-%m-%d'),
        to_date=datetime.strptime(to_date, '%Y-%m-%d')
    )
    db.session.add(new_order)
    db.session.commit()

    print(f"Redirecting to bill page with booking_id: {new_order.id}")

    # Redirect to the bill page with the new booking ID
    return redirect(url_for('bill', booking_id=new_order.id))

@app.route('/bill/<int:booking_id>')
def bill(booking_id):
    # Fetch booking details from the database using the booking_id
    booking = VehicleRentalOrder.query.get(booking_id)
    if not booking:
        return "Booking not found", 404

    booking_details = {
        "vehicle_name": booking.rental.name,
        "rental_duration": booking.rental_duration,
        "driver_required": "Yes" if booking.driver_required else "No",
        "total_amount": booking.amount,
        "current_date": booking.order_date.strftime("%B %d, %Y"),
        "from_date": booking.from_date.strftime("%B %d, %Y"),
        "to_date": booking.to_date.strftime("%B %d, %Y")
    }
    return render_template('bill.html', **booking_details)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to log in to view your profile.', 'error')
        return redirect(url_for('login'))

    if session.get('is_admin'):  # Check if the logged-in user is an admin
        return render_template('admin_profile.html')  # Render admin-specific profile page

    user_id = session['user_id']
    user = User.query.get(user_id)  # Fetch the logged-in customer's details
    product_orders = Booking.query.filter_by(customer_id=user_id).all()  # Fetch the customer's product orders
    vehicle_rentals = VehicleRentalOrder.query.filter_by(customer_id=user_id).all()  # Fetch the customer's vehicle rental orders
    granite_orders = GraniteOrder.query.filter_by(customer_id=user_id).all()  # Fetch the customer's granite orders

    return render_template(
        'profile.html',
        user=user,
        product_orders=product_orders,
        vehicle_rentals=vehicle_rentals,
        granite_orders=granite_orders
    )

@app.route('/test_orders')
def test_orders():
    orders = VehicleRentalOrder.query.all()
    return str(orders)

@app.route('/update_granite_cart', methods=['POST'])
def update_granite_cart():
    granite_cart = session.get('granite_cart', {})
    action = request.form.get('action')

    # Update square feet for each item in the cart
    for granite_id in granite_cart.keys():
        square_feet = request.form.get(f'square_feet_{granite_id}', type=int)
        if square_feet and square_feet > 0:
            granite_cart[granite_id]['square_feet'] = square_feet

    session['granite_cart'] = granite_cart

    if action == 'checkout':
        return redirect(url_for('granite_checkout'))

    flash('Cart updated successfully!', 'success')
    return redirect(url_for('granite_cart'))

@app.route('/granite_checkout', methods=['POST'])
def granite_checkout():
    if 'user_id' not in session:
        flash('You need to log in to place an order.', 'error')
        return redirect(url_for('login'))

    customer_id = session['user_id']
    granite_cart = session.get('granite_cart', {})

    if not granite_cart:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('granite_cart'))

    # Calculate total amount
    total_amount = sum(
        item['price_per_sqft'] * item['square_feet'] for item in granite_cart.values()
    )

    # Create a new GraniteOrder
    new_order = GraniteOrder(
        customer_id=customer_id,
        total_amount=total_amount
    )
    db.session.add(new_order)
    db.session.commit()

    # Add items to GraniteOrderItem
    for granite_id, item in granite_cart.items():
        new_order_item = GraniteOrderItem(
            order_id=new_order.id,
            granite_id=int(granite_id),
            square_feet=item['square_feet'],
            amount=item['price_per_sqft'] * item['square_feet']
        )
        db.session.add(new_order_item)

    db.session.commit()

    # Clear the cart after checkout
    session.pop('granite_cart', None)

    flash('Order placed successfully!', 'success')
    return redirect(url_for('granite_order_details', order_id=new_order.id))

@app.route('/granite_order_details/<int:order_id>')
def granite_order_details(order_id):
    order = GraniteOrder.query.get(order_id)
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('granite_shop'))

    return render_template('granite_order_details.html', order=order)

@app.route('/fabricate_granite/<int:order_item_id>', methods=['GET', 'POST'])
def fabricate_granite(order_item_id):
    order_item = GraniteOrderItem.query.get(order_item_id)
    if not order_item:
        flash('Order item not found!', 'error')
        return redirect(url_for('granite_order_details', order_id=order_item.order_id))

    if request.method == 'POST':
        # Prices for fabrication options
        edging_prices = {
            'bullnose': 180,
            'halfbullnose': 140,
            'waterfall': 200,
            'bevealed': 150,
            'ogee': 180
        }
        thickness_prices = {
            '10-14mm': 80,
            '16-20mm': 130,
            '30mm': 200,
            '40-50mm': 250,
            '52-60mm': 400,
            '60-80mm': 600
        }
        shaping_price = 150  # Fixed price for all shapes

        # Get selected options from the form
        edging = request.form.get('edging')
        thickness = request.form.get('thickness')
        shaping = request.form.get('shaping')

        # Calculate total fabrication charges
        total_fabrication_charges = (
            edging_prices.get(edging, 0) +
            thickness_prices.get(thickness, 0) +
            shaping_price
        )

        # Create a new Fabrication record
        new_fabrication = Fabrication(
            order_item_id=order_item_id,
            edging=edging,
            thickness=thickness,
            shaping=shaping,
            fabrication_fee=total_fabrication_charges
        )
        db.session.add(new_fabrication)
        db.session.commit()

        flash('Fabrication details added successfully!', 'success')
        return redirect(url_for('granite_order_details', order_id=order_item.order_id))

    return render_template('fabrication.html', order_item_id=order_item_id)

@app.route('/categories')
def categories():
    if not session.get('is_admin'):
        flash('Access denied! Admins only.', 'error')
        return redirect(url_for('login'))

    return render_template('categories.html')

@app.route('/manage_products', methods=['GET', 'POST'])
def add_product_page():
    if not session.get('is_admin'):
        flash('Access denied! Admins only.', 'error')
        return redirect(url_for('login'))

    # Fetch all products to display on the page
    products = Product.query.all()

    return render_template('manage_products.html', products=products)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('is_admin'):
        flash('Access denied! Admins only.', 'error')
        return redirect(url_for('login'))

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('add_product_page'))

    # Manually delete related rows in ProductBooked
    ProductBooked.query.filter_by(product_id=product_id).delete()

    # Delete the product
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('add_product_page'))

@app.route('/customer_orders/<int:customer_id>')
def customer_orders(customer_id):
    if not session.get('is_admin'):
        flash('Access denied! Admins only.', 'error')
        return redirect(url_for('login'))

    customer = User.query.get(customer_id)
    if not customer:
        flash('Customer not found!', 'error')
        return redirect(url_for('customer_details'))

    product_orders = Booking.query.filter_by(customer_id=customer_id).all()
    granite_orders = GraniteOrder.query.filter_by(customer_id=customer_id).all()
    vehicle_rentals = VehicleRentalOrder.query.filter_by(customer_id=customer_id).all()

    return render_template(
        'customer_orders.html',
        customer=customer,
        product_orders=product_orders,
        granite_orders=granite_orders,
        vehicle_rentals=vehicle_rentals
    )

@app.route('/customer_details')
def customer_details():
    if not session.get('is_admin'):
        flash('Access denied! Admins only.', 'error')
        return redirect(url_for('login'))

    customers = User.query.all()  # Fetch all customers
    return render_template('customer_details.html', customers=customers)

if __name__ == '__main__':
    # Create the database and tables
    with app.app_context():
        db.create_all()  # This will create the new tables

    

   

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)