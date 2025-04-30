from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for rides
rides = []

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle ride-sharing form submission
@app.route('/share', methods=['POST'])
def share():
    ride = {
        "name": request.form['name'],
        "vehicle": request.form['vehicle'],
        "seats": int(request.form['seats']),
        "from": request.form['from'],
        "to": request.form['to']
    }
    rides.append(ride)
    return redirect(url_for('view_rides'))

# Route to view existing rides
@app.route('/rides')
def view_rides():
    return render_template('rides.html', rides=rides)

# Route to book a ride
@app.route('/book/<int:ride_id>', methods=['POST'])
def book_ride(ride_id):
    if 0 <= ride_id < len(rides):
        if rides[ride_id]['seats'] > 0:
            rides[ride_id]['seats'] -= 1
            return f"Successfully booked a ride to {rides[ride_id]['to']}!"  # Fixed key
        else:
            return "No seats available for this ride."
    return "Ride not found."

if __name__ == '__main__':
    app.run(debug=True)
