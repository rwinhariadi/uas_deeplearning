import base64
import logging
import os
import time
from io import BytesIO

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS  # Untuk menangani CORS
from PIL import Image
from prometheus_client import Counter, Gauge, Histogram, make_wsgi_app
from tensorflow.keras.models import load_model
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Aktifkan CORS untuk mengizinkan permintaan dari frontend
CORS(app)

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Path model
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "pisang_DNN+MobileNetV21.0.h5")
logging.info(f"Loading model from: {model_path}")
try:
    model = load_model(model_path)
    logging.info("Model loaded successfully")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None


# Data history (disimpan dalam memori untuk sementara)
history = []  # type: ignore


# Prometheus Metrics
REQUEST_COUNT = Counter(
    "flask_app_requests_total",
    "Total number of requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "flask_app_request_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["endpoint"],
)
PREDICTION_COUNT = Counter("model_predictions_total",
                           "Total number of predictions")
PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds", "Latency of predictions in seconds"
)
CONFIDENCE_SCORE = Histogram(
    "model_confidence_score",
    "Confidence score of predictions",
    buckets=[0.1, 0.2, 0.5, 0.8, 1.0],
)
UNIQUE_IMAGES_PROCESSED = Counter(
    "unique_images_processed", "Number of unique images processed"
)
DUPLICATE_IMAGES_DETECTED = Counter(
    "duplicate_images_detected", "Number of duplicate images detected"
)
HISTORY_SIZE = Gauge("history_size", "Number of entries in history")

FRONTEND_METRIC_COUNTER = Counter(
    "frontend_metrics_total",
    "Total metrics received from frontend", ["metric_name"]
)


# Fungsi untuk preprocessing gambar
def preprocess_image(image, target_size=(224, 224)):
    try:
        image = image.resize(target_size)
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        return image_array
    except Exception as e:
        logging.error(f"Error in image preprocessing: {e}")
        raise


# Middleware untuk metrik
@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def log_request(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.path,
                         response.status_code).inc()
    REQUEST_LATENCY.labels(request.path).observe(latency)
    return response


# Endpoint untuk menerima unggahan gambar dan melakukan prediksi
@app.route("/upload", methods=["POST"])
def upload_image():
    logging.info("Received a file upload request")

    if "file" not in request.files:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    try:
        file = request.files["file"]
        image = Image.open(file)
        logging.info("Image file opened successfully")

        # Preprocess image
        processed_image = preprocess_image(image)
        logging.info("Image preprocessed successfully")

        # Perform prediction
        if model is None:
            raise ValueError("Model is not loaded")

        with PREDICTION_LATENCY.time():
            prediction = model.predict(processed_image)

        confidence = prediction[0][0]
        result = "Matang" if confidence > 0.5 else "Belum Matang"
        color = "Kuning" if result == "Matang" else "Hijau"

        CONFIDENCE_SCORE.observe(confidence)
        PREDICTION_COUNT.inc()

        # Convert image to base64 for storing in history
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_data = f"data:image/jpeg;base64,{image_base64}"

        # Cek apakah data sudah ada di history
        if not any(item["image"] == image_data for item in history):
            UNIQUE_IMAGES_PROCESSED.inc()
            history.append({"image": image_data,
                            "color": color, "status": result})
            HISTORY_SIZE.set(len(history))
            logging.info("Data added to history")
        else:
            DUPLICATE_IMAGES_DETECTED.inc()
            logging.info("Duplicate image detected, not added to history")

        # Return response to frontend
        return jsonify({"prediction": result,
                        "accuracy": round(confidence * 100, 2)})
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": "Gagal memproses gambar"}), 500


@app.route("/add-history", methods=["POST"])
def add_history():
    try:
        data = request.json  # Ambil data JSON dari request
        if not any(item["image"] == data["image"] for item in history):
            history.append(data)
            HISTORY_SIZE.set(len(history))
            logging.info("History added successfully")
            return jsonify({"message": "History added successfully"}), 200
        else:
            logging.info("Duplicate image detected in add-history, not added")
            return jsonify({"message": "Duplicate image detected"}), 200
    except Exception as e:
        logging.error(f"Error adding history: {e}")
        return jsonify({"error": "Failed to add history"}), 500


# Endpoint untuk mengambil data history
@app.route("/get-history", methods=["GET"])
def get_history():
    logging.info("History data fetched successfully")
    return jsonify(history), 200


# Endpoint untuk menerima metrik dari frontend
@app.route("/metrics/frontend", methods=["POST"])
def receive_frontend_metrics():
    """
    Endpoint untuk menerima metrik dari frontend.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Log metrik yang diterima
        logging.info(f"Frontend metric received: {data}")

        # Ekstrak data metrik
        metric_name = data.get("metric")
        value = data.get("value")

        # Validasi data
        if not metric_name or value is None:
            return jsonify({"error": "Invalid metric data"}), 400

        # Tambahkan metrik ke Prometheus
        FRONTEND_METRIC_COUNTER.labels(metric_name=metric_name).inc(value)

        # Respons sukses
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error receiving frontend metrics: {e}")
        return jsonify({"error":
                        "Internal server error"}), 500


# Integrasi Prometheus dengan Flask
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/metrics": make_wsgi_app()
    })

# Jalankan aplikasi Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
