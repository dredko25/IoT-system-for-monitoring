from flask import Flask, render_template, request, send_file, jsonify
import sqlite3
import json
import csv

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'


def get_equipments():
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Equipment")
    equipment = cursor.fetchall()
    conn.close()
    return equipment


def get_count_sensors(equipment_name):
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT COUNT(DISTINCT sensor_name) 
        FROM Measurement 
        WHERE Measurement.equipment_name=?;
    ''', (equipment_name,))
    count = cursor.fetchone()[0]

    cursor.execute('''
            SELECT DISTINCT sensor_name 
            FROM Measurement 
            WHERE Measurement.equipment_name=?;
        ''', (equipment_name,))
    sensors = cursor.fetchall()

    return count, sensors


def get_measurements(sensor, equipment_name):
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()
    cursor.execute('''
            SELECT Measurement.id, Measurement.equipment_name, Measurement.sensor_name, 
            Measurement.equipment_id, Measurement.value, Measurement.timestamp, 
            Sensor.max_value, Sensor.min_value, Sensor.sensor_category, 
            SensorCategory.category
            FROM Measurement INNER JOIN Sensor
            ON Measurement.sensor_id = Sensor.id
            INNER JOIN SensorCategory
            ON Sensor.sensor_category = SensorCategory.id
            WHERE Measurement.sensor_name=? AND Measurement.equipment_name = ?;
        ''', (sensor, equipment_name,))
    measurements = cursor.fetchall()
    json_data = format_measurements_to_json(measurements)
    conn.close()
    return json_data


def format_measurements_to_json(measurements):
    formatted_data = []
    for measurement in measurements:
        measurement_dict = {
            "id": measurement[0],
            "equipment_name": measurement[1],
            "sensor": measurement[2],
            "equipment_id": measurement[3],
            "value": measurement[4],
            "timestamp": measurement[5],
            "max_value": measurement[6],
            "min_value": measurement[7],
            "category_id": measurement[8],
            "category_name": measurement[9]
        }
        formatted_data.append(measurement_dict)
    return json.dumps(formatted_data)


def format_data_to_json(data, count):
    formatted_data = {
        "count": count,
        **{f"data{i+1}": json.loads(data[i]) for i in range(len(data))}
    }
    return json.dumps(formatted_data)


def get_equipment_list():
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()
    cursor.execute('''
            SELECT DISTINCT equipment_name 
            FROM Measurement;
        ''')
    equipments_names = cursor.fetchall()
    conn.close()
    return equipments_names


@app.route('/get_data_from_db')
def get_data():
    equipment_name = request.args.get('equipment_name', '')
    count, sensors = get_count_sensors(equipment_name=equipment_name)
    data = []

    for sensor in sensors:
        data.append(get_measurements(sensor=sensor[0], equipment_name=equipment_name))

    return format_data_to_json(data, count)


@app.route('/get_danger_history')
def get_danger_history():
    equipment_name = request.args.get('equipment_name', '')
    save_data_to_csv(equipment_name)
    return send_file('danger_history.csv', as_attachment=True)


@app.route('/view_danger_history')
def view_danger_history():
    equipment_name = request.args.get('equipment_name', '')
    history = query(equipment_name)
    return jsonify(history)


def query(equipment_name):
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()
    cursor.execute('''
            SELECT equipment_name, sensor_name,  
            value, timestamp 
            FROM Measurement 
            WHERE equipment_name=? 
            ORDER BY sensor_name;
    ''', (equipment_name,))
    history = cursor.fetchall()
    conn.close()
    return history


def save_data_to_csv(equipment_name):
    history = query(equipment_name)

    with open('danger_history.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Equipment Name", "Sensor name", "Value", "Timestamp"])  # Опис колонок
        writer.writerows(history)


@app.route('/analytics')
def analytics():
    equipment_list = get_equipment_list()
    return render_template('analytics.html', equipment_list=equipment_list)


@app.route('/requests')
def requests():
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()
    cursor.execute('''
                SELECT User.id, User.email, Equipment.name,  
                User.quantity, User.usage_hours, User.start_date  
                FROM User LEFT JOIN Equipment 
                ON User.equipment_id=Equipment.id;
        ''')
    requests = cursor.fetchall()
    conn.close()
    return render_template('requests.html', requests=requests)


@app.route('/', methods=['GET', 'POST'])
def home():
    equipments_data = get_equipments()
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('equipment.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO User (email) VALUES (?)', (email,))
        conn.commit()
        conn.close()
    return render_template('main.html', equipments=equipments_data)


@app.route('/form')
def form():
    equipments_data = get_equipments()
    return render_template('form.html', equipments=equipments_data)


@app.route('/submit_order', methods=['POST'])
def submit_order():
    equipments_data = get_equipments()
    if request.method == 'POST':
        equipment = request.form.getlist('equipment')
        quantity = request.form.getlist('quantity')
        usage_hours = request.form.getlist('usageHours')
        start_date = request.form.getlist('startDate')
        email = request.form.getlist('email')

        for i in range(len(equipment)):
            save_order_to_database(equipment[i], int(quantity[i]), int(usage_hours[i]), start_date[i], email[i])

        return render_template('main.html', equipments=equipments_data)


def save_order_to_database(equipment, quantity, usage_hours, start_date, email):
    conn = sqlite3.connect('equipment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Equipment WHERE name=?", (equipment,))
    equipment_id = cursor.fetchone()[0]
    cursor.execute('''
        INSERT INTO User (email, equipment_id, quantity, usage_hours, start_date) 
        VALUES (?, ?, ?, ?, ?)''', (email, equipment_id, quantity, usage_hours, start_date))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
