import time
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from scipy.signal import welch
from sklearn.preprocessing import StandardScaler

# Connect to the database
conn = sqlite3.connect('cm-01b.db')
cursor = conn.cursor()

# Define the interval in seconds
interval = 5  # Example: 5 seconds

while True:
    # Retrieve the raw values from the database
    cursor.execute("SELECT raw_value FROM channel_p3")
    raw_values = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the raw values to a NumPy array
    signal = np.array(raw_values).flatten()

    # Perform preprocessing - Standardization
    scaler = StandardScaler()
    signal_scaled = scaler.fit_transform(signal.reshape(-1, 1)).flatten()

    # Calculate the RMS
    rms = np.sqrt(np.mean(signal_scaled**2))

    # Calculate the PSD
    frequencies, psd = welch(signal_scaled)

    # Plot the PSD graph
    plt.figure()
    plt.plot(frequencies, psd)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density')
    plt.title('Power Spectral Density')
    plt.show()

    # Predict the threshold
    threshold = np.max(psd) * 0.8  # Example threshold value, adjust as needed

    # Print the results
    print(f"RMS: {rms}")
    print(f"Threshold: {threshold}")

    # Wait for the specified interval
    time.sleep(interval)

    # Reconnect to the database for the next iteration
    conn = sqlite3.connect('cm-01b.db')
    cursor = conn.cursor()
