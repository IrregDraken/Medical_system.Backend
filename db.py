import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "hospital.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()
    cursor = conn.cursor()

    # PATIENTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        address TEXT,
        card_id TEXT UNIQUE NOT NULL
    )
    """)

    # USERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        patient_id INTEGER,
        doctor_id INTEGER
    )
    """)

    # DOCTORS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialty TEXT,
        email TEXT,
        phone TEXT
    )
    """)

    # APPOINTMENTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT,
        reason TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # RECORDS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        diagnosis TEXT,
        treatment TEXT,
        date TEXT
    )
    """)

    # PRESCRIPTIONS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        drug_name TEXT,
        dosage TEXT
    )
    """)

    # DEFAULT ADMIN

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )

    admin = cursor.fetchone()

    if not admin:

        cursor.execute("""
        INSERT INTO users
        (username, password, role)
        VALUES (?, ?, ?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            "admin"
        ))

    conn.commit()
    conn.close()