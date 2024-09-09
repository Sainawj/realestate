from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = '9b3106234d87f82e33ca407254cc7aac'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'reuser'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'real_estate_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

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

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 400

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form.get('full_name')
        location = request.form.get('location')
        phone = request.form.get('phone')

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert user into the database
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO user (email, password, full_name, location, phone) VALUES (%s, %s, %s, %s, %s)',
            (email, hashed_password, full_name, location, phone)
        )
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if request.method == 'POST':
            new_email = request.form['email']
            new_full_name = request.form['full_name']
            new_location = request.form['location']
            new_phone = request.form['phone']
            new_password = request.form['password']

            # Hash new password if provided
            if new_password:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            else:
                hashed_password = user['password']  # Keep the old password if not changed

            # Update user details in the database
            cursor = mysql.connection.cursor()
            cursor.execute('''
                UPDATE user SET email = %s, password = %s, full_name = %s, location = %s, phone = %s 
                WHERE id = %s
            ''', (new_email, hashed_password, new_full_name, new_location, new_phone, user_id))
            mysql.connection.commit()
            cursor.close()

            session['email'] = new_email  # Update session email

            return redirect(url_for('profile'))

        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
