from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db
import os

app = Flask(__name__, instance_relative_config=True)

# Basic config
app.config['SECRET_KEY'] = 'change_this_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'machinewash.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Init DB
db.init_app(app)

# Import models after db is set up
import models
from models import User, Offer, Car, ServiceRecord

# ---------- Public pages ----------
@app.route('/')
def index():
    offers = Offer.query.order_by(Offer.id.desc()).all()
    return render_template('index.html', offers=offers)

# ---------- Auth ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form['phone'].strip()
        password = request.form['password']

        if User.query.filter((User.email==email) | (User.phone==phone)).first():
            flash('Email or phone already registered.', 'danger')
            return redirect(url_for('register'))
        u = User(name=name, email=email, phone=phone, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

# ---------- User dashboard ----------
def require_login():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return False
    return True

@app.route('/dashboard')
def dashboard():
    if not require_login():
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    offers = Offer.query.order_by(Offer.id.desc()).all()
    cars = Car.query.filter_by(user_id=user.id).all()
    # Collect service records for user's cars
    records = ServiceRecord.query.join(Car).filter(Car.user_id==user.id).order_by(ServiceRecord.date.desc()).all()
    return render_template('dashboard.html', user=user, offers=offers, cars=cars, records=records)

# Add a car (for logged-in user)
@app.route('/cars/add', methods=['POST'])
def add_car():
    if not require_login():
        return redirect(url_for('login'))
    plate = request.form['plate'].strip().upper()
    model = request.form['model'].strip()
    if Car.query.filter_by(plate=plate).first():
        flash('This car plate already exists.', 'danger')
    else:
        c = Car(user_id=session['user_id'], plate=plate, model=model)
        db.session.add(c)
        db.session.commit()
        flash('Car added.', 'success')
    return redirect(url_for('dashboard'))

# Add a service record (visit/payment) for a user's car
@app.route('/records/add', methods=['POST'])
def add_record():
    if not require_login():
        return redirect(url_for('login'))
    car_id = int(request.form['car_id'])
    service_type = request.form['service_type'].strip()
    amount = float(request.form['amount'])
    paid = True if request.form.get('paid') == 'on' else False
    notes = request.form.get('notes','').strip()
    sr = ServiceRecord(car_id=car_id, service_type=service_type, amount=amount, paid=paid, notes=notes, date=datetime.utcnow())
    db.session.add(sr)
    db.session.commit()
    flash('Service record added.', 'success')
    return redirect(url_for('dashboard'))

# ---------- Offers ----------
@app.route('/offers')
def offers():
    all_offers = Offer.query.order_by(Offer.id.desc()).all()
    return render_template('offers.html', offers=all_offers)

# ---------- Admin (simple demo) ----------
@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/panel', methods=['GET','POST'])
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        if title and description:
            db.session.add(Offer(title=title, description=description))
            db.session.commit()
            flash('Offer added.', 'success')
    offers = Offer.query.order_by(Offer.id.desc()).all()
    return render_template('admin_panel.html', offers=offers)

@app.route('/admin/offers/<int:offer_id>/delete', methods=['POST'])
def delete_offer(offer_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    o = Offer.query.get_or_404(offer_id)
    db.session.delete(o)
    db.session.commit()
    flash('Offer deleted.', 'info')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
