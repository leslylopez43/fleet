from flask import Flask, request, jsonify
from datetime import datetime
from models import db, Vehicle

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    registration_number = data['registration_number']
    customer_name = data['customer_details']['Name']
    customer_contact = data['customer_details']['Contact']
    hire_start = datetime.strptime(data['hire_start'], '%Y-%m-%d').date()
    hire_end = datetime.strptime(data['hire_end'], '%Y-%m-%d').date()

    if Vehicle.query.filter_by(registration_number=registration_number).first():
        return jsonify({'message': f'Vehicle with registration number {registration_number} already exists.'}), 400

    new_vehicle = Vehicle(
        registration_number=registration_number,
        customer_name=customer_name,
        customer_contact=customer_contact,
        hire_start=hire_start,
        hire_end=hire_end
    )

    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify({'message': f'Vehicle with registration number {registration_number} added.'}), 201

@app.route('/print_vehicles_for_period', methods=['GET'])
def print_vehicles_for_period():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    vehicles = Vehicle.query.filter(
        Vehicle.hire_start <= end_date,
        Vehicle.hire_end >= start_date
    ).all()

    results = []
    for vehicle in vehicles:
        results.append({
            'Registration Number': vehicle.registration_number,
            'Customer Details': {
                'Name': vehicle.customer_name,
                'Contact': vehicle.customer_contact
            },
            'Hire Start': vehicle.hire_start.strftime('%Y-%m-%d'),
            'Hire End': vehicle.hire_end.strftime('%Y-%m-%d')
        })

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True)
