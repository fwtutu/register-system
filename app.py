from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
conn = config.connect_to_database()

# Password validation function
def is_valid_password(password):
    return re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['password_check']
        
        # Check if the passwords match
        if password != password_check:
            flash("請確認密碼是否輸入正確")
            return render_template('register.html')
        
        # Validate password strength
        if not is_valid_password(password):
            flash("密碼至少需要8碼且須包含至少一位英文和一位數字")
            return render_template('register.html')
        
        cursor = conn.cursor(dictionary=True)
        # Check if the username already exists
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            flash("該帳號已有人使用!")
            return render_template('register.html')
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Insert new user into the database
        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        cursor.close()
        
        flash("註冊成功! 3秒後將自動跳轉頁面")
        return redirect(url_for('login'), code=302)
    
    return render_template('register.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('welcome'))
        else:
            flash('帳號或密碼錯誤')
    
    return render_template('login.html')

# Welcome page route
@app.route('/welcome')
def welcome():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user_id = session['id']
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS checkin_count FROM checkin WHERE user_id = %s", (user_id,))
    checkin_count = cursor.fetchone()['checkin_count']
    cursor.close()
    
    remaining_time = session.get('remaining_time', None)
    
    return render_template('welcome.html', username=username, checkin_count=checkin_count, remaining_time=remaining_time)




# Check-in route
@app.route('/checkin', methods=['POST'])
def checkin():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['id']
    cursor = conn.cursor(dictionary=True)
    
    # Get the last check-in time
    cursor.execute("SELECT checkin_time FROM checkin WHERE user_id = %s ORDER BY checkin_time DESC LIMIT 1", (user_id,))
    last_checkin = cursor.fetchone()
    
    if last_checkin:
        last_checkin_time = last_checkin['checkin_time']
        now = datetime.now()
        difference = now - last_checkin_time
        if difference < timedelta(minutes=10):
            remaining_time = 10 - (difference.seconds // 60)
            session['remaining_time'] = remaining_time
            return redirect(url_for('welcome'))
    
    # Insert new check-in record
    cursor.execute("INSERT INTO checkin (user_id) VALUES (%s)", (user_id,))
    conn.commit()
    cursor.close()
    
    session.pop('remaining_time', None)
    flash("簽到成功!")
    return redirect(url_for('welcome'))




# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
