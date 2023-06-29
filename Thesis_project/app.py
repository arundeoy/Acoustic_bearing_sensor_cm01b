import dash
import pandas as pd
import base64
import io
from dash import dcc, html
from dash.dependencies import Input, Output, MATCH, State, ALL
import plotly.graph_objects as go
import datetime
import time
import dash_daq as daq
import dash_table
import dash_renderer
import numpy as np

# Create a Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Acoustic Signal Dashboard'

def calculate_fft(time, amplitude, N, T):
    # Perform the FFT operation
    yf = np.fft.fft(amplitude)
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    return xf, 2.0/N * np.abs(yf[0:N//2])

# Define the layout of the app
app.layout = html.Div(
    [
        html.A(
            html.Img(
                src=app.get_asset_url('vt.png'),
                style={'width': '200px', 'display': 'inline-block ', 'float': 'left'}
            ),
            href="/",
            style={'text-decoration': 'none', 'margin-top': '20px'}
        ),
        html.H1(
            html.A(
                'Acoustic Signal Dashboard',
                href="/",
                style={'text-decoration': 'none', 'color': '#00bbf0'}
            ),
            style={'textAlign': 'center', 'fontSize': '54px', 'margin-top': '20px'}
        ),
        html.Div(
            id='timer',
            style={'float': 'right', 'margin-right': '20px'}
        ),

        dcc.Tabs(
            id="tabs",
            value='tab-1',
            children=[
                dcc.Tab(
                    label='Home',
                    value='tab-1',
                    style={'background': '#ff9a3c', 'color': '#FFFFFF', 'borderRadius': '10px'}
                ),
                dcc.Tab(
                    label='About',
                    value='tab-2',
                    style={'background': '#ff9a3c', 'color': '#FFFFFF', 'borderRadius': '10px'}
                ),
            ],
        ),
        html.Div(id='tabs-content'),
    ],
)

@app.callback(
    Output('timer', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_time(n):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return html.P(current_time, style={'font-size': '20px', 'margin': '0'})


@app.callback(
    Output(component_id='tabs-content', component_property='children'),
    [Input(component_id='tabs', component_property='value')]
)
def update_tabs_content(tab_value):
    if tab_value == 'tab-1':
        return html.Div(
            [
                html.H1('ACOUSTIC ANALYZER', style={'text-align': 'center', 'font-weight': 'bold', 'font-size': '34px'}),
                html.Div(
                    [
                        html.Label('Data Source'),
                        dcc.RadioItems(
                            id='data-source',
                            options=[
                                {'label': 'File', 'value': 'file'},
                                {'label': 'Real-Time', 'value': 'real-time'}
                            ],
                            value='file',
                            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                        )
                    ],
                    style={'margin-bottom': '10px'}
                ),
                html.Div(id='upload-container'),
                html.Div(id='preprocess-container'),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label('Threshold'),
                                dcc.Input(
                                    id='threshold-input',
                                    type='number',
                                    value=50,
                                    min=0,
                                    max=100,
                                    step=1
                                )
                            ],
                            style={'margin-bottom': '10px'}
                        ),
                        html.Div(
                            [
                                html.Label(''),
                                daq.Slider(
                                    id='threshold-slider',
                                    min=0,
                                    max=100,
                                    value=50,
                                    marks={i: str(i) for i in range(0, 101, 10)},
                                    step=1,
                                    vertical=True
                                )
                            ],
                            style={'display': 'inline-block', 'width': '50%', 'margin-right': '20px'}
                        ),
                        html.Div(
                            [
                                html.Label('Frequency'),
                                html.Div(id='frequency-output')
                            ],
                            style={'display': 'inline-block', 'width': '30%', 'margin-top': '10px'}
                        )
                    ],
                    style={'margin-bottom': '20px'}
                ),
                
                html.Div(id='waveform-container', style={'display': 'inline-block', 'width': '49%'}),
                html.Div(id='fft-container', style={'display': 'inline-block', 'width': '49%', 'margin-left': '2%'}),
                html.Div(id='rms-container', style={'text-align': 'center'})
            ],
            style={'padding': '20px'}
        )
    elif tab_value == 'tab-2':
        return html.Div(
            [
                html.H2('About Content'),
                html.H3('Summary of Acoustic Bearing Analysis'),
                html.P(
                    'The acoustic bearing analysis in this dashboard focuses on identifying anomalies and '
                    'abnormalities in the acoustic signal of bearings. By applying threshold values and alerts, '
                    'we can detect specific events and patterns that indicate potential issues in the bearings.'
                ),
                html.H3('Thresholds and Alerts'),
                html.P(
                    'Thresholds are predefined values that serve as reference points for identifying abnormal '
                    'conditions. The acoustic signal is continuously monitored, and any data point that exceeds '
                    'the threshold is flagged as an alert. These alerts can be further analyzed to determine the '
                    'severity and potential impact on bearing performance.'
                ),
                html.H3('Point-wise Analysis'),
                html.P(
                    'The analysis of the acoustic signal is performed on a point-wise basis. Each data point, '
                    'including its amplitude, frequency, and time, is considered to identify patterns and '
                    'abnormalities.'
                ),
            ],
            style={'padding': '20px'}
        )


@app.callback(
    Output('upload-container', 'children'),
    [Input('data-source', 'value')]
)
def update_upload_container(data_source):
    if data_source == 'file':
        return dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'marginBottom': '10px'
            },
            multiple=False
        )
    else:
        return html.Div()


@app.callback(
    Output('preprocess-container', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')]
)
def preprocess_data(contents, filename, last_modified):
    if contents is not None:
        # Preprocess the data here (replace this with your preprocessing logic)
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        columns = list(df.columns)
        return html.Div(
            [
                html.Div(
                    [
                        html.Label('Timestamp Column'),
                        dcc.Dropdown(
                            id='timestamp-column-dropdown',
                            options=[{'label': col, 'value': col} for col in columns],
                            value=''
                        )
                    ],
                    style={'margin-bottom': '10px'}
                ),
                html.Div(
                    [
                        html.Label('Raw Value Column'),
                        dcc.Dropdown(
                            id='raw-value-column-dropdown',
                            options=[{'label': col, 'value': col} for col in columns],
                            value=''
                        )
                    ],
                    style={'margin-bottom': '10px'}
                ),
                html.Div(
                    [
                        html.Label('Voltage Column'),
                        dcc.Dropdown(
                            id='voltage-column-dropdown',
                            options=[{'label': col, 'value': col} for col in columns],
                            value=''
                        )
                    ],
                    style={'margin-bottom': '10px'}
                ),
                html.Button('Preprocess Data', id='preprocess-btn', n_clicks=0)
            ]
        )
    else:
        return html.Div()


@app.callback(
    Output('waveform-container', 'children'),
    Output('fft-container', 'children'),
    Output('rms-container', 'children'),
    [Input('preprocess-btn', 'n_clicks')],
    [State('upload-data', 'contents'),
     State('timestamp-column-dropdown', 'value'),
     State('raw-value-column-dropdown', 'value'),
     State('voltage-column-dropdown', 'value')]
)
def update_waveform_fft_container(n_clicks, contents, timestamp_column, raw_value_column, voltage_column):
    if n_clicks > 0 and contents is not None and timestamp_column and raw_value_column and voltage_column:
        # Preprocess the data here (replace this with your preprocessing logic)
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df = df[[timestamp_column, raw_value_column, voltage_column]]  # Select relevant columns
        df['timestamp'] = pd.to_datetime(df[timestamp_column])  # Convert timestamp column to datetime

        # Preprocessing logic (replace with your actual preprocessing logic)
        preprocessed_data = df.rename(columns={raw_value_column: 'amplitude', voltage_column: 'voltage'})
        preprocessed_data['time'] = (preprocessed_data['timestamp'] - preprocessed_data['timestamp'].min()).dt.total_seconds()

        waveform_graph = dcc.Graph(
            id='waveform-graph',
            figure={
                'data': [
                    {'x': preprocessed_data['time'], 'y': preprocessed_data['amplitude'], 'type': 'line', 'name': 'Waveform'}
                ],
                'layout': {
                    'title': 'Waveform',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Amplitude'}
                }
            }
        )
        # Calculate the FFT of the data
        xf, yf = calculate_fft(preprocessed_data['time'], preprocessed_data['amplitude'], len(preprocessed_data), preprocessed_data['time'].iloc[-1])
        fft_graph = dcc.Graph(
            id='fft-graph',
            figure={
                'data': [
                    {'x': xf, 'y': yf, 'type': 'line', 'name': 'FFT'}
                ],
                'layout': {
                    'title': 'FFT',
                    'xaxis': {'title': 'Frequency'},
                    'yaxis': {'title': 'Amplitude'}
                }
            }
        )
        rms_value = preprocessed_data['amplitude'].mean()  # Calculate RMS value

        return waveform_graph, fft_graph, html.Div(f'RMS Value: {rms_value:.2f}')
    else:
        return html.Div(), html.Div(), html.Div()


@app.callback(
    Output('threshold-slider', 'value'),
    Output('threshold-input', 'value'),
    Input('threshold-slider', 'value'),
    Input('threshold-input', 'value')
)
def update_threshold_value(slider_value, input_value):
    ctx = dash.callback_context
    triggered_component = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_component == 'threshold-slider':
        return slider_value, slider_value
    else:
        return input_value, input_value


@app.callback(
    Output('frequency-output', 'children'),
    Input('threshold-slider', 'value'),
    Input('threshold-input', 'value')
)
def update_frequency_output(slider_value, input_value):
    threshold = slider_value if slider_value is not None else input_value
    return f'Threshold: {threshold}'


# Additional callbacks for the added features


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
