import sqlite3

# Підключення до бази даних
conn = sqlite3.connect('equipment.db')

# Створення курсора
cursor = conn.cursor()

# Виконання SQL-запитів для створення таблиць
# Обладнання
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Equipment (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price INT NOT NULL
    )
''')
# Категорія датчика
cursor.execute('''
    CREATE TABLE IF NOT EXISTS SensorCategory (
        id INTEGER PRIMARY KEY,
        category TEXT NOT NULL
    )
''')
# Датчик
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sensor (
        id INTEGER PRIMARY KEY,
        sensor_category INTEGER REFERENCES SensorCategory(category),
        sensor_name TEXT NOT NULL,
        max_value INT,
        min_value INT
    )
''')
# Вимірювання
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Measurement (
        id INTEGER PRIMARY KEY,
        equipment_name TEXT NOT NULL,
        sensor_name TEXT NOT NULL,
        sensor_id INTEGER REFERENCES Sensor(id),
        equipment_id INTEGER REFERENCES Equipment(id),
        value REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
# Запит користувача
cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY,
        email TEXT,
        equipment_id INTEGER REFERENCES Equipment(id),
        quantity INT,
        usage_hours INT,
        start_date DATE
    )
''')

# Збереження змін
conn.commit()
# Закриття з'єднання
conn.close()
