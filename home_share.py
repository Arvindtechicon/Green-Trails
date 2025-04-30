from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for listings
listings = []

@app.route('/')
def home():
    return render_template('index.html', listings=listings)

@app.route('/post', methods=['POST'])
def post_listing():
    data = request.form
    image_file = request.files['image_file']
    
    # Save the uploaded image
    if image_file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(image_path)
        image_url = f'/{image_path}'
    else:
        image_url = '/static/default.jpg'  # Default image if none is uploaded

    # Add the new listing to the in-memory storage
    listings.append({
        'title': data['title'],
        'description': data['description'],
        'days': data['days'],
        'address': data['address'],
        'image_url': image_url
    })
    return redirect(url_for('home'))

@app.route('/book/<int:listing_id>', methods=['POST'])
def book_listing(listing_id):
    # Handle booking logic here (e.g., mark as booked or notify the owner)
    return f"Booking confirmed for listing ID: {listing_id}"

if __name__ == '__main__':
    app.run(debug=True)
