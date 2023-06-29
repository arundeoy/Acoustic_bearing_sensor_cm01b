# rms_psd.py
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from scipy.signal import welch

# Connect to the database
conn = sqlite3.connect('cm-01b.db')
cursor = conn.cursor()

# Retrieve the raw values from the database
cursor.execute("SELECT raw_value FROM channel_p3")
raw_values = cursor.fetchall()

# Close the database connection
conn.close()

# Convert the raw values to a NumPy array
signal = np.array(raw_values).flatten()

# Calculate the RMS
rms = np.sqrt(np.mean(signal**2))

# Calculate the PSD
frequencies, psd = welch(signal)

# Plot the PSD graph
plt.figure()
plt.plot(frequencies, psd)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power Spectral Density')
plt.title('Power Spectral Density')
plt.show()

# Predict the threshold
threshold = np.max(psd) * 0.8  # Example threshold value, adjust as needed

print(f"RMS: {rms}")
print(f"Threshold: {threshold}")

