from flask import Flask, render_template, request, redirect, url_for, send_file

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sqlite3
import io
import os


app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn=sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_number TEXT NOT NULL,
            make TEXT,
            model TEXT,
            colour TEXT,
            fuel TEXT,
            mileage INTEGER,        
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            license TEXT,
            phone TEXT,
            address TEXT,
            from_date TEXT,
            exp_date TEXT,
            dob TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            out_date TEXT,
            out_mileage TEXT,
            out_location TEXT,
            out_time TEXT,
            out_fuel_reading TEXT,
            in_due_date TEXT,
            in_time TEXT,
            in_adblue TEXT,
            in_mileage TEXT,
            in_fuel_reading TEXT,
            extension_to TEXT,
            hirer_signature TEXT,
            on_behalf_of TEXT,
            FOREIGN KEY(vehicle_id) REFERENCES vehicle(id),
            FOREIGN KEY(customer_id) REFERENCES customer(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            address TEXT NOT NULL,
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/vehicle", methods=["GET", "POST"])
def vehicles():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    if request.method == "POST":
        search_term = request.form.get("search")
        if search_term:
            sql_select_query = """
                SELECT * FROM vehicle 
                WHERE registration_number LIKE ? 
                OR make LIKE ? 
                OR model LIKE ?
            """
            cur.execute(sql_select_query, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            sql_select_query = "SELECT * FROM vehicle;"
            cur.execute(sql_select_query)
    else:
        sql_select_query = "SELECT * FROM vehicle;"
        cur.execute(sql_select_query)
    
    vehicles_details = cur.fetchall()
    cur.close()

 
    return render_template("vehicle.html", vehicles=vehicles_details)



@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        registration_number = request.form['registration_number']
        make = request.form['make']
        model = request.form['model']
        colour = request.form['colour']
        fuel = request.form['fuel']
        mileage = request.form['mileage']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicle (registration_number, make, model, colour, fuel, mileage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (registration_number, make, model, colour, fuel, mileage))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_vehicle.html')

@app.route('/update_vehicle/<int:id>', methods=['GET', 'POST'])
def update_vehicle(id):
    if request.method == 'POST':
        registration_number = request.form['registration_number']
        make = request.form['make']
        model = request.form['model']
        colour = request.form['colour']
        fuel = request.form['fuel']
        mileage = request.form['mileage']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vehicle
            SET registration_number=?, make=?, model=?, colour=?, fuel=?, mileage=?
            WHERE id=?
        ''', (registration_number, make, model, colour, fuel, mileage, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    # Fetch vehicle data by id and pass it to the template for editing
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicle WHERE id=?", (id,))
    vehicle = cursor.fetchone()
    conn.close()
    return render_template('update_vehicle.html', vehicle=vehicle)


@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        license = request.form['license']
        phone = request.form['phone']
        address = request.form['address']
        from_date = request.form['from_date']
        exp_date = request.form['exp_date']
        dob = request.form['dob']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customer (name, license, phone, address, from_date, exp_date, dob)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, license, phone, address, from_date, exp_date, dob))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_customer.html')


@app.route('/add_hire', methods=['GET', 'POST'])
def add_hire():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicle')
    vehicles = cursor.fetchall()
    cursor.execute('SELECT * FROM customer')
    customers = cursor.fetchall()
    
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        customer_id = request.form['customer_id']
        out_date = request.form['out_date']
        out_mileage = request.form['out_mileage']
        out_location = request.form['out_location']
        out_time = request.form['out_time']
        out_fuel_reading = request.form['out_fuel_reading']
        in_due_date = request.form['in_due_date']
        in_time = request.form['in_time']
        in_adblue = request.form['in_adblue']
        in_mileage = request.form['in_mileage']
        in_fuel_reading = request.form['in_fuel_reading']
        extension_to = request.form['extension_to']
        hirer_signature = request.form['hirer_signature']
        on_behalf_of = request.form['on_behalf_of']
        agreement_number = request.form['agreement_number']
        
        cursor.execute('''
            INSERT INTO hire (
                vehicle_id, customer_id, out_date, out_mileage, out_location, out_time,
                out_fuel_reading, in_due_date, in_time, in_adblue, in_mileage, in_fuel_reading,
                extension_to, hirer_signature, on_behalf_of, agreement_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vehicle_id, customer_id, out_date, out_mileage, out_location, out_time,
            out_fuel_reading, in_due_date, in_time, in_adblue, in_mileage, in_fuel_reading,
            extension_to, hirer_signature, on_behalf_of, agreement_number
        ))
        conn.commit()
        
        return redirect(url_for('index'))
    
    return render_template('add_hire.html', vehicles=vehicles, customers=customers)
   

@app.route('/print_hire/<int:hire_id>')
def print_hire(hire_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.*, v.registration_number, v.make, v.model, v.colour, v.fuel, 
        c.name, c.license, c.phone, c.address, c.from_date, c.exp_date, c.dob
        FROM hire h
        JOIN vehicle v ON h.vehicle_id = v.id
        JOIN customer c ON h.customer_id = c.id
        WHERE h.id = ?
    ''', (hire_id,))
    hire_details = cursor.fetchone()
    conn.close()

    if hire_details:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Path to the background image
        background_image_path = os.path.join(app.root_path, 'static', 'background_template.jpg')

        # Add background image
        c.drawImage(background_image_path, 0, 0, width=width, height=height)

        # Draw text on the canvas
        y = height - 100
        c.setFont("Helvetica", 12)
        c.drawString(100, y, "Hire Agreement")
        y -= 20

        c.drawString(100, y, f"Registration Number: {hire_details[7]}")
        y -= 15
        c.drawString(100, y, f"Customer Name: {hire_details[8]}")
        y -= 15
        c.drawString(100, y, f"Start Date: {hire_details[3]}")
        y -= 15
        c.drawString(100, y, f"End Date: {hire_details[4]}")
        y -= 30

        c.save()

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="hire_agreement.pdf", mimetype='application/pdf')
    else:
        return "No hire agreement found for the provided ID."



# Dummy data for demonstration purposes
lessors = [
    (1, 'Company A', 'Address A', '1234'),
    (2, 'Company B', 'Address B', '5678'),
]

@app.route('/lessor_data', methods=['GET', 'POST'])
def lessor_data():
    if request.method == 'POST':
        # Handle form submission to add a new lessor
        company_name = request.form.get('company_name')
        address = request.form.get('address')
        agreement_number = request.form.get('agreement_number')
        # Add the new lessor to the list (or save to database)
        lessors.append((len(lessors) + 1, company_name, address, agreement_number))
        return redirect(url_for('lessor_data'))  # Redirect to the lessor_data page after adding

    # Render the lessor_data template with the lessors data
    return render_template('lessor_data.html', lessors=lessors)





@app.route('/lessor', methods=['GET', 'POST'])
def lessor():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        search_query = request.form.get('search')
        if search_query:
            cursor.execute("SELECT * FROM lessor WHERE company_name LIKE ?", ('%' + search_query + '%',))
        else:
            company_name = request.form['company_name']
            address = request.form['address']
            agreement_number = request.form['agreement_number']
            cursor.execute('''
                INSERT INTO lessor (company_name, address, agreement_number)
                VALUES (?, ?, ?)
            ''', (company_name, address, agreement_number))
            conn.commit()

    cursor.execute("SELECT * FROM lessor")
    lessors_data = cursor.fetchall()
    conn.close()
    return render_template('lessor.html', lessors=lessors_data)

@app.route('/update_lessor/<int:id>', methods=['GET', 'POST'])
def update_lessor(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        company_name = request.form['company_name']
        address = request.form['address']
        agreement_number = request.form['agreement_number']
        cursor.execute('''
            UPDATE lessor
            SET company_name = ?, address = ?, agreement_number = ?
            WHERE id = ?
        ''', (company_name, address, agreement_number, id))
        conn.commit()
        conn.close()
        return redirect(url_for('lessor'))

    cursor.execute("SELECT * FROM lessor WHERE id = ?", (id,))
    lessor = cursor.fetchone()
    conn.close()
    return render_template('update_lessor.html', lessor=lessor)

if __name__ == '__main__':
    app.run(debug=True)