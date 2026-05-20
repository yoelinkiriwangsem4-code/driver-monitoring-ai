from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
# Enable CORS for SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

# Menerima frame video & data dari script Raspberry Pi
@socketio.on('video_frame')
def handle_video_frame(data):
    # Cek apakah server menerima data
    print(f"Menerima frame dari Raspberry Pi... Status: {data.get('status')}")
    # Menyebarkan (broadcast) data tersebut ke SEMUA client browser yang terkoneksi
    emit('update_dashboard', data, broadcast=True)

if __name__ == '__main__':
    # Railway menyediakan port lewat environment variable PORT
    port = int(os.environ.get("PORT", 5000))
    print(f"Server berjalan di port {port}")
    socketio.run(app, host='0.0.0.0', port=port)
