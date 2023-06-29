# database.py
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import sqlite3
import csv
import os

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)

# Set the gain to 1 (±4.096V range)
ads.gain = 1

# Create input on channel P3
chan = AnalogIn(ads, ADS.P3)



# Get the current working directory
cwd = os.getcwd()

# Define the database and CSV paths
db_path = os.path.join(cwd, 'cm-01b.db')
print(db_path)
csv_path = os.path.join(cwd, 'cm-01b.csv')
print(csv_path)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the channel_p3 table if it does not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS channel_p3
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   raw_value INTEGER,
                   voltage REAL,
                   timestamp TEXT)''')

# Check if the voltage column exists in the table
cursor.execute("PRAGMA table_info(channel_p3)")
table_columns = [column[1] for column in cursor.fetchall()]
if 'voltage' not in table_columns:
    # If the column does not exist, alter the table to add the missing column
    cursor.execute("ALTER TABLE channel_p3 ADD COLUMN voltage REAL")

# Commit the changes
conn.commit()

# File path for CSV export
csv_file = csv_path
# Define a function to read analog values and store in the database and CSV
def read_analog_values():
    # Use a list to store the values before insertion
    values = []

    # Get the current timestamp
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # Read 1024 samples per conversion
    for _ in range(2500):
        raw_value = chan.value
        voltage = chan.voltage
        values.append((raw_value, voltage, timestamp))

    # Insert the values into the database
    conn.executemany('''INSERT INTO channel_p3 (raw_value, voltage, timestamp)
                        VALUES (?, ?, ?)''', values)
    conn.commit()

    # Export to CSV
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([(timestamp, raw_value, voltage) for raw_value, voltage, timestamp in values])

# Set the data rate to 860 samples per second
ads.data_rate = 860

# Continuous loop to read analog values
while True:
    read_analog_values()
    
# Close the database connection
conn.close()
