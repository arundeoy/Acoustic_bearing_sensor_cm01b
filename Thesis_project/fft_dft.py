# fft_dft.py
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

# Connect to the database
conn = sqlite3.connect('cm-01b.db')
cursor = conn.cursor()

# Retrieve the raw values from the database
cursor.execute("SELECT raw_value FROM channel_p3")
raw_values = cursor.fetchall()

# Close the database connection
conn.close()

# Perform DFT on the raw values
signal = np.array(raw_values).flatten()
dft = np.fft.fft(signal)

# Calculate the frequency values
n = len(dft)
sampling_rate = 860  # Samples per second
frequency = np.fft.fftfreq(n, d=1/sampling_rate)

# Plot the DFT spectrum
plt.figure()
plt.plot(frequency, np.abs(dft))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('DFT Spectrum')
plt.show()
