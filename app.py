from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
conn = config.connect_to_database()

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
@app.route('/', methods=['GET', 'POST'])
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
    return render_template('welcome.html', username=username)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
