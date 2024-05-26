import threading
from random import uniform
import paho.mqtt.client as mqtt
import time


class Sensor:
    count = 0

    def __init__(self, name, scenario_func):
        Sensor.count += 1
        self.name = f"{name}_0{Sensor.count}"
        self.scenario_func = scenario_func

    def generate_data(self, i):
        return self.scenario_func(i)
    

class KnockSensor(Sensor):
    def __init__(self):
        super().__init__('Датчик детонації', self.random_knock_scenario)

    @staticmethod
    def random_knock_scenario(i):
        if i <= 10:
            return uniform(10, 15)
        elif 10 < i <= 20:
            interval_length = 93 - 15
            progress_within_interval = (i - 10) / 10
            return 15 + progress_within_interval * interval_length
        elif 20 < i <= 70:
            return uniform(93, 110)
        else:
            interval_length = 170 - 130
            progress_within_interval = (i - 40) / 30
            return min(130 + progress_within_interval * interval_length, 170)


class CoolantTempSensor(Sensor):
    def __init__(self):
        super().__init__('Датчик температури охолоджуючої рідини', self.random_coolant_temp_scenario)

    @staticmethod
    def random_coolant_temp_scenario(i):
        if i <= 10:
            return uniform(10, 15)
        elif 10 < i <= 20:
            interval_length = 75 - 15
            progress_within_interval = (i - 10) / 10
            return 15 + progress_within_interval * interval_length
        elif 20 < i <= 80:
            return uniform(75, 100)
        else:
            interval_length = 150 - 100
            progress_within_interval = (i - 50) / 30
            return min(100 + progress_within_interval * interval_length, 150)


class EngineOilTempSensor(Sensor):
    def __init__(self):
        super().__init__('Датчик температури моторного масла', self.random_engine_oil_temp_scenario)

    @staticmethod
    def random_engine_oil_temp_scenario(i):
        if i <= 10:
            return uniform(10, 15)
        elif 10 < i <= 20:
            interval_length = 75 - 15
            progress_within_interval = (i - 10) / 10
            return 15 + progress_within_interval * interval_length
        elif 20 < i <= 75:
            return uniform(85, 120)
        else:
            interval_length = 140 - 120
            progress_within_interval = (i - 20) / 30
            return min(120 + progress_within_interval * interval_length, 140)


class FuelLevelSensor(Sensor):
    fuel_level = 200

    def __init__(self):
        super().__init__('Датчик рівня палива', self.random_fuel_level_scenario)

    @staticmethod
    def random_fuel_level_scenario(i):
        if i % 4 == 0:
            FuelLevelSensor.fuel_level -= 1
        if i > 50:
            FuelLevelSensor.fuel_level -= 10
            FuelLevelSensor.fuel_level = max(FuelLevelSensor.fuel_level, 0)
        return FuelLevelSensor.fuel_level


class TensionSensor(Sensor):
    def __init__(self):
        super().__init__('Тензодатчик', self.random_tension_scenario)

    @staticmethod
    def random_tension_scenario(i):
        values = [0, 45, 60, 130, 200, 260, 340, 340, 300, 250, 140, 60, 3, 20, 90,
                  150, 290, 380, 450, 400, 320, 210, 100, 20, 0, 0, 0, 0, 0, 0, 100,
                  160, 240, 400, 400, 210, 130, 15]
        return values[(i - 1) % len(values)]


class InclineSensor(Sensor):
    def __init__(self):
        super().__init__('Інклінометр', self.random_incline_scenario)

    @staticmethod
    def random_incline_scenario(i):
        angle_incline = [0, 10, 20, 15, 25, 40, -5, 5, 10, 9, -9, 0, 3]
        return angle_incline[(i - 1) % len(angle_incline)]


class ProximitySensor1(Sensor):
    def __init__(self):
        super().__init__('Датчик наближення', self.random_proximity_scenario_1)

    @staticmethod
    def random_proximity_scenario_1(i):
        if i <= 10:
            return 13 - i
        elif 10 < i <= 15:
            return 3 + i
        elif 15 < i <= 30:
            return 17 - i / 3
        elif 30 < i <= 40:
            return i - 15
        elif 40 < i < 50:
            return 11 - i / 5
        else:
            return 5


class ProximitySensor2(Sensor):
    def __init__(self):
        super().__init__('Датчик наближення', self.random_proximity_scenario_2)

    @staticmethod
    def random_proximity_scenario_2(i):
        if i <= 10:
            return 15 - i
        elif 10 < i <= 15:
            return 3 + i
        elif 15 < i <= 30:
            return 20 - i / 3
        elif 30 < i <= 40:
            return i - 15 * 0.9
        elif 40 < i < 50:
            return 20 - i / 5
        else:
            return 4


class TyrePressureSensor(Sensor):
    def __init__(self):
        super().__init__('Датчик тиску шин', self.random_tyre_pressure_scenario)

    @staticmethod
    def random_tyre_pressure_scenario(i):
        if i <= 60:
            return 32 - i / 30
        else:
            return 30


class TyrePressureSensorError(Sensor):
    def __init__(self):
        super().__init__('Датчик тиску шин', self.random_tyre_pressure_scenario_error)

    @staticmethod
    def random_tyre_pressure_scenario_error(i):
        if i <= 60:
            return 32 - i / 30
        elif 60 < i <= 90:
            return 29 - i / 15
        else:
            return 23


class Equipment:
    # Додамо змінну для зберігання порядкового номера
    count = 0

    def __init__(self, name):
        Equipment.count += 1
        self.name = f"{name}_0{Equipment.count}"
        self.sensors = []

    def add_sensor(self, sensor_type):
        self.sensors.append(sensor_type)

    def connect_to_mqtt_broker(self):
        self.mqttBroker = "mqtt.eclipseprojects.io"
        self.client = mqtt.Client(self.name)
        self.client.connect(self.mqttBroker)

    def disconnect_from_mqtt_broker(self):
        self.client.disconnect()


# Створення класів для кожної одиниці техніки
class Crane(Equipment):
    def __init__(self):
        super().__init__("Кран")
        self.i = 0
        self.add_sensor(KnockSensor())
        self.add_sensor(CoolantTempSensor())
        self.add_sensor(EngineOilTempSensor())
        self.add_sensor(FuelLevelSensor())
        self.add_sensor(TensionSensor())
        self.add_sensor(InclineSensor())
        self.add_sensor(ProximitySensor1())
        self.add_sensor(ProximitySensor2())
        self.add_sensor(TyrePressureSensor())
        self.add_sensor(TyrePressureSensorError())

        self.connect_to_mqtt_broker()


    def update_i(self):
        max_i = 105
        self.i += 1
        if self.i > max_i:
            self.i = 0

    def send_sensor_data(self):
        while True:
            for sensor in self.sensors:
                sensor_data = sensor.generate_data(self.i)
                self.client.publish(f"Equipments/{self.name}/{sensor.name}", sensor_data)
            self.update_i()
            time.sleep(1)


class DumpTruck(Equipment):
    def __init__(self):
        super().__init__("Самоскид")
        self.i = 0
        self.add_sensor(KnockSensor())
        self.add_sensor(CoolantTempSensor())
        self.add_sensor(EngineOilTempSensor())
        self.add_sensor(FuelLevelSensor())
        self.add_sensor(TensionSensor())
        self.add_sensor(InclineSensor())
        self.add_sensor(ProximitySensor1())
        self.add_sensor(ProximitySensor2())
        self.add_sensor(TyrePressureSensor())
        self.add_sensor(TyrePressureSensorError())
        self.connect_to_mqtt_broker()

    # def update_fuel_level(self):
    #     if self.i % 4 == 0:
    #         self.fuel_level -= 1
    #     if self.i > 50:
    #         self.fuel_level -= 10
    #         self.fuel_level = max(self.fuel_level, 0)
    #     return self.fuel_level

    def update_i(self):
        max_i = 105
        self.i += 1
        if self.i > max_i:
            self.i = 0

    def send_sensor_data(self):
        while True:
            # Генерація та надсилання даних для кожного датчика
            for sensor in self.sensors:
                sensor_data = sensor.generate_data(self.i)
                self.client.publish(f"Equipments/{self.name}/{sensor.name}", sensor_data)
                print(f"Equipments/{self.name}/{sensor.name}", sensor_data)

            self.update_i()
            time.sleep(1)


def create_equipments(num_equipments, equipment_class):
    equipments = []
    for _ in range(num_equipments):
        new_equipment = equipment_class()
        equipments.append(new_equipment)
    return equipments


def start_sensor_data_threads(list):
    for item in list:
        thread_item = threading.Thread(target=item.send_sensor_data)
        thread_item.start()


cranes = [Crane() for _ in range(2)]
start_sensor_data_threads(cranes)


dumptrucks = [DumpTruck() for _ in range(1)]
start_sensor_data_threads(dumptrucks)
