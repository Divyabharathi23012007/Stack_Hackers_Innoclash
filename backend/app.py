# app.py
# Main Flask application for Water Level Prediction System

from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash

from backend.config import SECRET_KEY
from backend.db import get_db_connection
from backend.weather import get_weather_forecast
from backend.predict import run_prediction
from backend.tts import generate_tts
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, supports_credentials=True)

# -------------------- HEALTH CHECK --------------------
@app.route("/health")
def health():
    return jsonify({"status": "Backend running"})


# -------------------- REGISTER --------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not all([email, password, role]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_pw = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
            (email, hashed_pw, role)
        )
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "User registered successfully"})


# -------------------- LOGIN --------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user["id"]
    session["role"] = user["role"]

    return jsonify({"message": "Login successful", "role": user["role"]})


# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


# -------------------- ADD BOREWELL --------------------
@app.route("/add-borewell", methods=["POST"])
def add_borewell():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO borewells (user_id, latitude, longitude) VALUES (%s, %s, %s)",
        (session["user_id"], latitude, longitude)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Borewell added"})


# -------------------- SET THRESHOLD --------------------
@app.route("/set-threshold", methods=["POST"])
def set_threshold():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    threshold = request.json.get("threshold")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "REPLACE INTO settings (user_id, threshold) VALUES (%s, %s)",
        (session["user_id"], threshold)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Threshold saved"})


# -------------------- RUN PREDICTION --------------------
@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT latitude, longitude FROM borewells WHERE user_id=%s",
        (session["user_id"],)
    )
    borewell = cursor.fetchone()

    cursor.execute(
        "SELECT threshold FROM settings WHERE user_id=%s",
        (session["user_id"],)
    )
    setting = cursor.fetchone()

    cursor.close()
    conn.close()

    if not borewell:
        return jsonify({"error": "No borewell found"}), 404

    # Weather data
    weather = get_weather_forecast(
        borewell["latitude"],
        borewell["longitude"]
    )

    # Prediction
    prediction = run_prediction(
    borewell["latitude"],
    borewell["longitude"],
    weather["temperature"],
    weather["rainfall"]
)

    

    

    # Alert check
    alert = False
    if setting and min(prediction) < setting["threshold"]:
        alert = True

    return jsonify({
        "prediction": prediction,
        "alert": alert
    })


# -------------------- TEXT TO SPEECH --------------------
@app.route("/tts", methods=["POST"])
def tts():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    text = request.json.get("text")

    if not text:
        return jsonify({"error": "Text required"}), 400

    audio_path = generate_tts(text)

    return jsonify({
        "audio_path": audio_path
    })






if __name__ == "__main__":
    app.run(debug=True)
