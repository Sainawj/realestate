from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import bcrypt
import os

app = Flask(__name__)
app.secret_key = '9b3106234d87f82e33ca407254cc7aac'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'reuser'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'real_estate_db'

mysql = MySQL(app)

@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', loggedin=True)
    else:
        return render_template('index.html', loggedin=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database for the user
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['loggedin'] = True
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert user into the database
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO user (email, password) VALUES (%s, %s)', (email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        email = session['email']
        if request.method == 'POST':
            full_name = request.form['full_name']
            location = request.form['location']
            phone = request.form['phone']
            properties_owned = request.form['properties_owned']
            properties_leased = request.form['properties_leased']
            profile_image = request.files['profile_image']
            profile_image_path = None
            
            if profile_image:
                profile_image_path = os.path.join('static/uploads', profile_image.filename)
                profile_image.save(profile_image_path)

            # Update user details in the database
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE user SET full_name = %s, location = %s, phone = %s, properties_owned = %s, properties_leased = %s, profile_image = %s WHERE email = %s',
                           (full_name, location, phone, properties_owned, properties_leased, profile_image_path, email))
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('profile'))

        # Fetch current profile details
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
