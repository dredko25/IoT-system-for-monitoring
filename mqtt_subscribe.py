import paho.mqtt.client as mqtt
import sqlite3
import re
from datetime import datetime
import pytz

# Встановлення часового поясу
local_tz = pytz.timezone('Europe/Kiev')  # Встановлення часового поясу на Київ


def on_message(client, userdata, message):
    print(f"Отримане повідомлення: {message.payload.decode()} на тему {message.topic}")

    # Розділити тему на частини, щоб отримати дані про інструмент та тип датчика
    parts = message.topic.split("/")
    if len(parts) == 3:  # Перевіряємо, чи в темі є потрібна кількість частин
        equipment_type = re.sub(r'_\d+$', '', parts[1])
        sensor_type = re.sub(r'_\d+$', '', parts[2])
        sensor_name = parts[2]
        equipment_name = parts[1]
        sensor_value = message.payload.decode()
        current_time = datetime.now(local_tz)

        # Додаємо дані до бази даних
        conn = sqlite3.connect('equipment.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Measurement (equipment_name, sensor_name, sensor_id, equipment_id, value, timestamp) 
            VALUES (
                ?,
                ?,
                (SELECT id FROM Sensor WHERE sensor_name=?), 
                (SELECT id FROM Equipment WHERE name=?), 
                ?,
                ?
            )
        ''', (equipment_name, sensor_name, sensor_type, equipment_type, sensor_value, current_time))
        conn.commit()
        conn.close()

def subscribe_to_sensor_data(broker):
    client = mqtt.Client("SensorSubscriber")
    client.on_message = on_message
    client.connect(broker)
    client.subscribe("Equipments/#")  # Підписка на всі теми, які починаються з "Equipments/"
    client.loop_forever()

if __name__ == "__main__":
    mqttBroker = "mqtt.eclipseprojects.io"
    subscribe_to_sensor_data(mqttBroker)
