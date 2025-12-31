from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sqlite3
import requests

app = FastAPI()
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=".", html=True), name="static")
DB_NAME = "tracking.db"
API_KEY = "c5ad271f27ad4e54c4e262a7071473c4"

def get_db():
    return sqlite3.connect(DB_NAME)

@app.get("/")
def home():
    return {"message": "Flight tracker is running"}

@app.get("/track/{tracking_id}")
def track_flight(tracking_id: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT UNIQUE,
            flight_number TEXT
        )
    """)

    # For now, we use a fixed real flight (example)
    cursor.execute(
        "INSERT OR IGNORE INTO flights (tracking_id, flight_number) VALUES (?, ?)",
        (tracking_id, "AA100")
    )

    cursor.execute(
    "SELECT flight_number FROM flights WHERE tracking_id=?",
    (tracking_id,)
)

row = cursor.fetchone()

if not row:
    return {"error": "Tracking ID not found"}

flight_number = row[0]

    # Call Aviationstack API
    response = requests.get(
        "https://api.aviationstack.com/v1/flights",
        params={
            "access_key": API_KEY,
            "flight_iata": flight_number
        }
    )

    data = response.json()

    if not data.get("data"):
        return {"error": "No flight data found"}

    flight = data["data"][0]

    status = flight["flight_status"]
    departure = flight["departure"]["airport"]
    arrival = flight["arrival"]["airport"]

    conn.close()

    return {
        "tracking_id": tracking_id,
        "flight_number": flight_number,
        "status": status,
        "departure": departure,
        "arrival": arrival
    }

