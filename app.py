from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
import joblib
import sqlite3
from datetime import datetime

# ===============================
# FLASK & SOCKETIO
# ===============================
app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

# ===============================
# LOAD MACHINE LEARNING MODEL
# ===============================
print("Loading model_ngantuk3.pkl...")

model = joblib.load("model_ngantuk3.pkl")

print("Model berhasil dimuat!")

# ===============================
# SQLITE DATABASE
# ===============================
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(
    "database/history.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu TEXT,
    ear REAL,
    mar REAL,
    head REAL,
    status TEXT
)
""")

conn.commit()

# ===============================
# DASHBOARD PAGE
# ===============================
@app.route('/')
def index():
    return render_template('index.html')

# ===============================
# TERIMA DATA DARI RASPBERRY PI
# ===============================
@socketio.on('video_frame')
def handle_video_frame(data):

    try:
        # ===============================
        # AMBIL DATA DARI RASPBERRY
        # ===============================
        ear = float(data.get('ear', 0))
        mar = float(data.get('mar', 0))
        head = float(data.get('head', 0))

        # ===============================
        # MACHINE LEARNING PREDICTION
        # ===============================
        features = [[ear, mar, head]]

        pred = model.predict(features)[0]

        if pred == 1:
            status = "MENGANTUK!"
        else:
            status = "AMAN"

        print(f"Prediksi: {status}")

        # ===============================
        # SIMPAN KE DATABASE
        # ===============================
        cursor.execute("""
        INSERT INTO history (
            waktu,
            ear,
            mar,
            head,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ear,
            mar,
            head,
            status
        ))

        conn.commit()

        # ===============================
        # KIRIM KE DASHBOARD
        # ===============================
        socketio.emit('update_dashboard', {
            'image': data.get('image'),
            'ear': ear,
            'mar': mar,
            'head': head,
            'status': status
        }, broadcast=True)

    except Exception as e:
        print(f"ERROR: {e}")

# ===============================
# MAIN
# ===============================
if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    print(f"Server berjalan di port {port}")

    socketio.run(
        app,
        host='0.0.0.0',
        port=port
    )