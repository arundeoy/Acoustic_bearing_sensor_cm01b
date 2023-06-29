# Acoustic_bearing_sensor_cm01b
Development of acoustic bearing sensor using Single board computer Raspberry pi, Web visualization for detection and conditioning and monitoring using python and Dash plotly, And using Matlab for the spectral analyzer

# Acoustic Signal Analysis Dashboard

This project is a web-based dashboard for analyzing and visualizing acoustic signals. It allows users to upload acoustic signal data, preprocess the data, and perform various analysis tasks such as waveform visualization, FFT analysis, RMS calculation, and threshold adjustment. The dashboard is built using the Dash framework and includes interactive components for data exploration and analysis.

## Installation

To run this project, make sure you have Python 3.x installed. Clone the repository and navigate to the project directory. Then, install the required dependencies using the following command:

pip install -r requirements.txt

## Usage

To run the project, execute the following command in the terminal:

python app.py

This will start the web server, and you can access the dashboard in your web browser at http://127.0.0.1:8050/.

## Additional Information

- The database.py file is responsible for reading analog values from an ADC and storing them in a SQLite database and CSV file.

- The preprocessing_RT.py file contains data preprocessing logic for real-time data.

- The fft_dft.py file includes functions for performing FFT (Fast Fourier Transform) analysis on data.

- The rms_psd.py file calculates the RMS (Root Mean Square) value and power spectral density of the data.

- Make sure to have the necessary libraries installed by running pip install -r requirements.txt.



