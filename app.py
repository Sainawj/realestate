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
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 400

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insert user into the database
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        username = session['username']
        if request.method == 'POST':
            new_username = request.form.get('username')
            new_password = request.form.get('password')

            # Hash new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update user details in the database
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE users SET username = %s, password = %s WHERE username = %s',
                           (new_username, hashed_password, username))
            mysql.connection.commit()
            cursor.close()

            session['username'] = new_username

            return redirect(url_for('profile'))

        return render_template('profile.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
