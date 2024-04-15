from flask import Flask, render_template
import requests
import json
import csv
from datetime import datetime, timedelta
from colorama import init, Fore

app = Flask(__name__, template_folder='D:\\PythonProject\\one-hour-two-year-collect-pair-data\\')

# Tambahkan variabel global untuk menyimpan timestamp sebelumnya
previous_timestamp = None

init()

def create_csv(data):
    # Menyimpan data ke file CSV
    with open('output.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:  # Cek apakah file CSV kosong
            writer.writerow(data.keys())  # Menulis judul kolom
        writer.writerow(data.values())  # Menulis data

def get_historical_data(symbol, interval, start_time, end_time):
    print(Fore.YELLOW + "[LOGS]: " + Fore.WHITE + "collecting data...")

    url = f"https://fapi.binance.com/fapi/v1/continuousKlines?pair={symbol}&interval={interval}&limit=1500&startTime={start_time}&endTime={end_time}&contractType=PERPETUAL"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-pair-two-years-ago')
def interaction_button_to_get_data():
    print(Fore.GREEN + "[LOGS]: " + Fore.WHITE + "Starting to collect data...")
    global previous_timestamp

    # Inisialisasi array untuk menampung semua data
    all_data = []

    # Menghitung waktu 2 tahun yang lalu dari sekarang
    two_years_ago = datetime.now() - timedelta(days=365*2)
    start_time = int(two_years_ago.timestamp()) * 1000
    end_time = int(datetime.now().timestamp()) * 1000

    while True:
        # Panggil API untuk rentang waktu saat ini
        candle = get_historical_data("BTCUSDT", "1h", start_time, end_time)

        # Cek apakah panggilan API mengembalikan data
        if not candle:
            break

        for candlePerItem in candle:
            openCandle = candlePerItem[1]
            highCandle = candlePerItem[2]
            lowCandle = candlePerItem[3]
            closeCandle = candlePerItem[4]
            volumeCandle = candlePerItem[5]
            endTime = candlePerItem[6]

            timestamp = endTime / 1000
            date_time_hour_shifted = datetime.fromtimestamp(timestamp) + timedelta(seconds=1) - timedelta(hours=1)
            date_hour = date_time_hour_shifted.strftime('%d-%m-%Y, %H:%M:%S')

            # Tambahkan data ke dalam array all_data
            all_data.append({
                "Pair": "BTCUSDT",
                "Contract Type": "PERPETUAL",
                "Time Stamp": date_hour,
                "Open Price": openCandle,
                "Close Price": closeCandle,
                "High Price": highCandle,
                "Low Price": lowCandle,
                "Volume": volumeCandle
            })

            previous_timestamp = endTime

        # Tentukan waktu mulai untuk panggilan API berikutnya
        if candle:
            last_candle_end_time = candle[-1][6]
            start_time = last_candle_end_time + 1  # Tambahkan 1 agar tidak memperoleh candle yang sama lagi
        else:
            break  # Jika tidak ada candle yang diperoleh, berhenti

    # Menyimpan data ke file CSV
    with open('output.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:  # Cek apakah file CSV kosong
            writer.writerow(["Pair", "Contract Type", "Time Stamp", "Open Price", "Close Price", "High Price", "Low Price", "Volume"])  # Menulis judul kolom
        for data in all_data:
            writer.writerow(data.values())

    print(Fore.GREEN + "[LOGS]: " + Fore.WHITE + "Successfully collected data!")
    return "Successfully collected data!"

if __name__ == '__main__':
    app.run(port=3000)
