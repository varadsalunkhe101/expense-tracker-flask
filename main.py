from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"   # needed for session

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # your MySQL password
        database="expensetracker"
    )

# ---------------- INDEX PAGE ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- LOGIN PAGE ----------------
@app.route('/login')
def login_page():
    return render_template('login.html')

# ---------------- LOGIN LOGIC ----------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    db = get_db_connection()
    cursor = db.cursor()

    query = "SELECT * FROM admin_login WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    db.close()

    if user:
        session['user'] = username
        return redirect('/dashboard')
    else:
        return "Invalid Username or Password"

# ---------------- REGISTER PAGE ----------------
@app.route('/register')
def register_page():
    return render_template('register.html')

# ---------------- REGISTER LOGIC ----------------
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    db = get_db_connection()
    cursor = db.cursor()

    query = "INSERT INTO admin_login (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, password))
    db.commit()
    db.close()

    return redirect('/')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    else:
        return redirect('/')

# ---------------- ADD EXPENSE PAGE ----------------
@app.route('/add')
def add_page():
    if 'user' in session:
        return render_template('add_expense.html')
    else:
        return redirect('/')

# ---------------- ADD EXPENSE LOGIC ----------------
@app.route('/add', methods=['POST'])
def add_expense():
    if 'user' not in session:
        return redirect('/')

    amount = request.form['amount']
    reason = request.form['reason']

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    db = get_db_connection()
    cursor = db.cursor()

    query = "INSERT INTO expense (amount, reason, date, time) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (amount, reason, date, time))
    db.commit()
    db.close()

    return redirect('/dashboard')

# ---------------- VIEW EXPENSE ----------------
@app.route('/view')
def view_expense():
    if 'user' not in session:
        return redirect('/')

    db = get_db_connection()
    cursor = db.cursor()

    query = "SELECT * FROM expense"
    cursor.execute(query)
    data = cursor.fetchall()

    db.close()

    return render_template('view_expense.html', expenses=data)

# ---------------- DELETE PAGE ----------------
@app.route('/delete')
def delete_page():
    if 'user' in session:
        return render_template('delete_expenses.html')
    else:
        return redirect('/')

# ---------------- DELETE LOGIC ----------------
@app.route('/delete', methods=['POST'])
def delete_expense():
    if 'user' not in session:
        return redirect('/')

    expense_id = request.form['id']

    db = get_db_connection()
    cursor = db.cursor()

    query = "DELETE FROM expense WHERE id=%s"
    cursor.execute(query, (expense_id,))
    db.commit()
    db.close()

    return redirect('/dashboard')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)