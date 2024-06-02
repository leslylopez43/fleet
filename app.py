from flask import Flask, render_template, request, redirect, url_for, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3
import io

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle (
            id INTEGER PRIMARY KEY,
            registration_number TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hire (
            id INTEGER PRIMARY KEY,
            vehicle_id INTEGER,
            customer_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            FOREIGN KEY(vehicle_id) REFERENCES vehicle(id),
            FOREIGN KEY(customer_id) REFERENCES customer(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        registration_number = request.form['registration_number']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO vehicle (registration_number) VALUES (?)', (registration_number,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_vehicle.html')

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO customer (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_customer.html')

@app.route('/add_hire', methods=['GET', 'POST'])
def add_hire():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicle')
    vehicles = cursor.fetchall()
    cursor.execute('SELECT * FROM customer')
    customers = cursor.fetchall()
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        customer_id = request.form['customer_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        cursor.execute('INSERT INTO hire (vehicle_id, customer_id, start_date, end_date) VALUES (?, ?, ?, ?)',
                       (vehicle_id, customer_id, start_date, end_date))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('add_hire.html', vehicles=vehicles, customers=customers)

@app.route('/print_hire', methods=['GET', 'POST'])
def print_hire():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.registration_number, c.name, h.start_date, h.end_date
            FROM hire h
            JOIN vehicle v ON h.vehicle_id = v.id
            JOIN customer c ON h.customer_id = c.id
            WHERE h.start_date >= ? AND h.end_date <= ?
        ''', (start_date, end_date))
        hires = cursor.fetchall()
        conn.close()

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Add background image
        c.drawImage("static/background_template.jpg", 0, 0, width=width, height=height)

        # Draw text on the canvas
        y = height - 100
        c.setFont("Helvetica", 12)
        c.drawString(100, y, "Hire Agreements")
        y -= 20

        for hire in hires:
            c.drawString(100, y, f"Registration Number: {hire[0]}")
            y -= 15
            c.drawString(100, y, f"Customer Name: {hire[1]}")
            y -= 15
            c.drawString(100, y, f"Start Date: {hire[2]}")
            y -= 15
            c.drawString(100, y, f"End Date: {hire[3]}")
            y -= 30

        c.save()

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="hire_agreements.pdf", mimetype='application/pdf')

    return render_template('print_hire.html', hires=None)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
