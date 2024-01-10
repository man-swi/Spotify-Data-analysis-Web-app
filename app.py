from flask import Flask, render_template, request, jsonify
import pyodbc
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import plotly.express as px

app = Flask(__name__)

server = 'LAPTOP-TV4RL7A7\SQLEXPRESS'
database = 'Spotify'
username = 'SA'
password = 'Varroc@123'

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_filters', methods=['POST'])
def get_filters():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT Released_year FROM Spotify")
    years = [str(year[0]) for year in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT Songs FROM Spotify")
    songs = [song[0] for song in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT Artist_name FROM Spotify")
    artists = [artist[0] for artist in cursor.fetchall()]

    return jsonify({'years': years, 'songs': songs, 'artists': artists})

@app.route('/get_results', methods=['POST'])
def get_results():
    conn = get_db_connection()
    cursor = conn.cursor()

    chosen_filter = request.json['chosen_filter']
    chosen_value = request.json['chosen_value']

    if chosen_filter == 'Period':
        query = f"SELECT * FROM Spotify WHERE Released_year = {chosen_value}"
    elif chosen_filter == 'Tracks':
        query = f"SELECT * FROM Spotify WHERE Songs = '{chosen_value}'"
    elif chosen_filter == 'Artists':
        query = f"SELECT * FROM Spotify WHERE Artist_name = '{chosen_value}'"

    results = pd.read_sql(query, conn).to_dict(orient='records')

    return jsonify({'results': results})


@app.route('/get_top_years_streams', methods=['POST'])
def get_top_years_streams():
    conn = get_db_connection()
    cursor = conn.cursor()

    chosen_filter = request.json['chosen_filter']
    chosen_value = request.json['chosen_value']

    query = f"SELECT TOP 10 Songs, Streams FROM Spotify WHERE Released_year = ? ORDER BY Streams DESC"
    results = cursor.execute(query, chosen_value).fetchall()

    top_songs_streams = [{'song': result[0], 'streams': result[1]} for result in results]

    return jsonify({'top_songs_streams': top_songs_streams})


@app.route('/get_energy_plot', methods=['POST'])
def get_energy_plot():
    conn = get_db_connection()
    cursor = conn.cursor()

    chosen_song = request.json.get('chosen_value', '')
    if not chosen_song:
        return jsonify({'error': 'Please select a song.'}), 400

    cursor.execute("SELECT Released_year, Energy FROM Spotify WHERE Songs = ? ORDER BY Released_year", chosen_song)
    results = cursor.fetchall()

    released_years = [result[0] for result in results]
    energy_values = [result[1] for result in results]

    return jsonify({'released_years': released_years, 'energy_values': energy_values})




if __name__ == '__main__':
    app.run(debug=True)
