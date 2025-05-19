from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, Train, Booking
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from algorithms import merge_sort, TrainGraph, BookingRequest, process_booking_requests
import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.secret_key = Config.SECRET_KEY

# Initialize train graph for route planning
graph = TrainGraph()
graph.add_route('City1', 'City2', 3, 'T101')
graph.add_route('City1', 'City3', 5, 'T102')
graph.add_route('City2', 'City3', 2, 'T103')

# Queue for VIP booking processing
booking_queue = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password, pwd):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('search'))
        flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        is_vip = 'is_vip' in request.form  #  Check if the VIP checkbox was selected
        if User.query.filter_by(username=uname).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        hashed_pwd = generate_password_hash(pwd)
        new_user = User(username=uname, password=hashed_pwd, is_vip=is_vip)  # ✅ Include the is_vip attribute
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        trains = Train.query.filter_by(source=source, destination=destination).all()
        train_list = [{
            'id': t.id,
            'name': t.name,
            'source': t.source,
            'destination': t.destination,
            'departure_time': t.departure_time,
            'arrival_time': t.arrival_time,
            'seats': t.seats
        } for t in trains]
        sorted_trains = merge_sort(train_list, key=lambda x: x['departure_time'])
        return render_template('results.html', trains=sorted_trains)
    return render_template('search.html')

@app.route('/book/<train_id>', methods=['GET', 'POST'])
def book(train_id):
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    train = Train.query.get(train_id)
    if not train:
        flash('Train not found.')
        return redirect(url_for('search'))
    if request.method == 'POST':
        if train.seats > 0:
            train.seats -= 1
            booking = Booking(
                user_id=session['user_id'],
                train_id=train.id,
                booking_time=datetime.datetime.now(),
                payment_status="Pending"
            )
            db.session.add(booking)
            db.session.commit()
            flash('Booking successful! Proceed to payment.')
            return redirect(url_for('payment', booking_id=booking.id))
        else:
            flash('No seats available.')
            return redirect(url_for('search'))
    return render_template('booking.html', train=train)

@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    booking = Booking.query.get(booking_id)
    if request.method == 'POST':
        booking.payment_status = "Completed"
        db.session.commit()
        flash('Payment successful! Your ticket is confirmed.')
        return redirect(url_for('booking_history'))
    return render_template('payment.html', booking=booking)

@app.route('/booking_history')
def booking_history():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('booking_history.html', bookings=bookings)

@app.route('/cancel/<int:booking_id>', methods=['GET', 'POST'])
def cancel(booking_id):
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    booking = Booking.query.get(booking_id)
    if not booking or booking.user_id != session['user_id']:
        flash('Booking not found.')
        return redirect(url_for('booking_history'))
    if request.method == 'POST':
        train = Train.query.get(booking.train_id)
        if train:
            train.seats += 1
        db.session.delete(booking)
        db.session.commit()
        flash('Booking cancelled successfully.')
        return redirect(url_for('booking_history'))
    return render_template('cancel.html', booking=booking)

@app.route('/plan_route', methods=['POST'])
def plan_route():
    data = request.json
    source = data['source']
    destination = data['destination']
    strategy = data.get('strategy', 'shortest')
    if strategy == 'fewest_transfers':
        changes = graph.fewest_trains_dp(source, destination)
        return jsonify({'min_train_changes': changes})
    else:
        dist, prev = graph.dijkstra(source)
        path = graph.reconstruct_path(prev, destination)
        return jsonify({'shortest_distance': dist[destination], 'path': path})

@app.route('/book_ticket', methods=['POST'])
def book_ticket():
    data = request.json
    user_id = data['user_id']
    is_vip = data['is_vip']
    request_time = datetime.datetime.now().timestamp()
    request_obj = BookingRequest(user_id, is_vip, request_time)
    booking_queue.append(request_obj)
    sorted_queue = process_booking_requests(booking_queue.copy())
    queue_display = [{'user_id': req.user_id, 'vip': req.is_vip} for req in sorted_queue]
    return jsonify({'booking_order': queue_display})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Train.query.count() == 0:
            sample_trains = [
                Train(id='T101', name='Express A', source='City1', destination='City2', departure_time='09:00', arrival_time='12:00', seats=50),
                Train(id='T102', name='Express B', source='City1', destination='City3', departure_time='10:00', arrival_time='13:00', seats=40),
                Train(id='T103', name='Express C', source='City2', destination='City3', departure_time='11:00', arrival_time='14:00', seats=30)
            ]
            for t in sample_trains:
                db.session.add(t)
            db.session.commit()
    app.run(debug=True)
