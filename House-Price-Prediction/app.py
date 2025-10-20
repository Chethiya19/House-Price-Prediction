from flask import Flask, request, render_template, redirect, url_for, session, flash
import pandas as pd
import pickle
import secrets
import mysql.connector

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key for session management

# Load the model, scaler, and label encoders
with open('random_forest_model.pkl', 'rb') as file:
    model = pickle.load(file)

with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

with open('label_encoders.pkl', 'rb') as file:
    label_encoders = pickle.load(file)

# MySQL database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Replace with your actual MySQL password
    'database': 'house'  # Ensure the 'house' database is created in your MySQL server
}

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    return mysql.connector.connect(**db_config)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home route that handles house price prediction."""
    if 'user' in session:
        return redirect(url_for('add_house'))

    prediction = None
    if request.method == 'POST':
        # Collect form data
        ms_sub_class = int(request.form['MSSubClass'])
        lot_area = float(request.form['LotArea'])
        house_style = request.form['HouseStyle']
        roof_style = request.form['RoofStyle']
        total_bsmt_sf = float(request.form['TotalBsmtSF'])
        full_bath = int(request.form['FullBath'])
        bedroom_abv_gr = int(request.form['BedroomAbvGr'])
        garage_cars = int(request.form['GarageCars'])

        # Encode categorical data
        try:
            house_style_encoded = label_encoders['HouseStyle'].transform([house_style])[0]
            roof_style_encoded = label_encoders['RoofStyle'].transform([roof_style])[0]
        except KeyError:
            return "House Style or Roof Style not recognized."

        # Prepare the input data
        input_data = pd.DataFrame({
            'MSSubClass': [ms_sub_class],
            'LotArea': [lot_area],
            'HouseStyle': [house_style_encoded],
            'RoofStyle': [roof_style_encoded],
            'TotalBsmtSF': [total_bsmt_sf],
            'FullBath': [full_bath],
            'BedroomAbvGr': [bedroom_abv_gr],
            'GarageCars': [garage_cars]
        })

        # Apply scaling to the numeric features
        input_data[['LotArea', 'TotalBsmtSF', 'FullBath', 'BedroomAbvGr', 'GarageCars']] = scaler.transform(
            input_data[['LotArea', 'TotalBsmtSF', 'FullBath', 'BedroomAbvGr', 'GarageCars']]
        )

        # Make prediction
        prediction = model.predict(input_data)[0]

    return render_template('index.html', prediction=prediction)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose another one.', 'danger')
            return render_template('register.html')  # Stay on the register page

        # Insert new user into the database
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful! You can now log in.', 'success')
        # Optionally, you could render the register page again to show the success message.
        return render_template('register.html')  # Stay on the register page

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('add_house'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Handles user logout."""
    session.pop('user', None)  # Clear the session
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))  # Redirect to login page


@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    """Handles adding house details and displaying the list of houses."""
    if 'user' not in session:  # Check if user is logged in
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        address = request.form['address']
        price = request.form['price']
        bedrooms = request.form['bedrooms']
        bathrooms = request.form['bathrooms']
        square_feet = request.form['square_feet']

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """INSERT INTO houses (address, price, bedrooms, bathrooms, square_feet)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (address, price, bedrooms, bathrooms, square_feet))
        conn.commit()
        cursor.close()
        conn.close()

        flash('House details added successfully!', 'success')
        return redirect(url_for('add_house'))  # Redirect to the same page to refresh the list

    # Fetching house details from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary=True to get rows as dictionaries
    cursor.execute('SELECT * FROM houses')
    houses = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('add_house.html', houses=houses)

@app.route('/edit_house/<int:id>', methods=['GET', 'POST'])
def edit_house(id):
    """Handles editing house details."""
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            address = request.form['address']
            price = request.form['price']
            bedrooms = request.form['bedrooms']
            bathrooms = request.form['bathrooms']
            square_feet = request.form['square_feet']
            
            cursor.execute('UPDATE houses SET address=%s, price=%s, bedrooms=%s, bathrooms=%s, square_feet=%s WHERE id=%s',
                           (address, price, bedrooms, bathrooms, square_feet, id))
            conn.commit()
            cursor.close()
            conn.close()

            flash('House details updated successfully!', 'success')
            return redirect(url_for('add_house'))

        cursor.execute('SELECT * FROM houses WHERE id=%s', (id,))
        house = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template('edit_house.html', house=house)

    return redirect(url_for('login'))

@app.route('/delete_house/<int:id>', methods=['POST'])
def delete_house(id):
    """Handles deleting house details."""
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM houses WHERE id=%s', (id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash('House details deleted successfully!', 'success')
        return redirect(url_for('add_house'))

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
