from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, init_db

app = Flask(__name__)
CORS(app)

init_db()


@app.route("/")
def home():
    return jsonify({
        "message": "Riverside General Hospital Backend Running"
    })


# ==========================================
# PATIENT REGISTRATION
# ==========================================

@app.route("/register_patient", methods=["POST"])
def register_patient():

    data = request.json

    phone = data.get("phone") or data.get("phone_number")
    card_id = data.get("card_id") or data.get("hospital_card_number")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients
    (full_name, age, gender, phone, address, card_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["full_name"],
        data["age"],
        data["gender"],
        phone,
        data["address"],
        card_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Patient Registered Successfully"
    })


# ==========================================
# PATIENT SIGNUP
# ==========================================

@app.route("/signup", methods=["POST"])
def signup():

    data = request.json

    card_id = (
        data.get("card_id")
        or data.get("hospital_card_number")
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE card_id=?",
        (card_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        conn.close()

        return jsonify({
            "error": "Patient not found"
        }), 404

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (card_id,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()

        return jsonify({
            "error": "Account already exists"
        }), 400

    hashed_password = generate_password_hash(
        data["password"]
    )

    cursor.execute("""
    INSERT INTO users
    (
        username,
        password,
        role,
        patient_id
    )
    VALUES (?, ?, ?, ?)
    """, (
        card_id,
        hashed_password,
        "patient",
        patient["id"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Account Created Successfully"
    })


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data.get("username")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    if not user:

        return jsonify({
            "error": "Invalid Credentials"
        }), 401

    if not check_password_hash(
        user["password"],
        data["password"]
    ):

        return jsonify({
            "error": "Invalid Credentials"
        }), 401

    if user["role"] == "patient":

        return jsonify({
            "role": "patient",
            "patient_id": user["patient_id"]
        })

    if user["role"] == "doctor":

        return jsonify({
            "role": "doctor",
            "doctor_id": user["doctor_id"]
        })

    return jsonify({
        "role": "admin"
    })
# ==========================================
# GET ALL PATIENTS
# ==========================================

@app.route("/patients")
def patients():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients"
    )

    data = cursor.fetchall()

    conn.close()

    result = []

    for patient in data:

        p = dict(patient)

        p["hospital_card_number"] = p["card_id"]
        p["phone_number"] = p["phone"]

        result.append(p)

    return jsonify(result)


# ==========================================
# GET SINGLE PATIENT
# ==========================================

@app.route("/patient/<int:id>")
def patient(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (id,)
    )

    patient = cursor.fetchone()

    conn.close()

    if not patient:

        return jsonify({
            "error": "Patient Not Found"
        }), 404

    patient_data = dict(patient)

    patient_data["hospital_card_number"] = patient_data["card_id"]
    patient_data["phone_number"] = patient_data["phone"]

    return jsonify(patient_data)


# ==========================================
# UPDATE PATIENT
# ==========================================

@app.route("/patient/<int:id>", methods=["PUT"])
def update_patient(id):

    data = request.json

    phone = data.get("phone") or data.get("phone_number")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE patients
    SET
        full_name=?,
        age=?,
        gender=?,
        phone=?,
        address=?
    WHERE id=?
    """, (
        data["full_name"],
        data["age"],
        data["gender"],
        phone,
        data["address"],
        id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Patient Updated Successfully"
    })


# ==========================================
# GET ALL DOCTORS
# ==========================================

@app.route("/doctors")
def doctors():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM doctors"
    )

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# GET SINGLE DOCTOR
# ==========================================

@app.route("/doctor/<int:id>")
def doctor(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM doctors WHERE id=?",
        (id,)
    )

    doctor = cursor.fetchone()

    conn.close()

    if not doctor:

        return jsonify({
            "error": "Doctor Not Found"
        }), 404

    return jsonify(
        dict(doctor)
    )


# ==========================================
# CREATE DOCTOR
# ADMIN CREATES DOCTOR ACCOUNT
# ==========================================

@app.route("/doctor", methods=["POST"])
def add_doctor():

    data = request.json

    print(data)

    phone = data.get("phone") or data.get("phone_number")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO doctors
    (
        name,
        specialty,
        email,
        phone
    )
    VALUES (?, ?, ?, ?)
    """, (
        data.get("name") or data.get("full_name"),
        data["specialty"],
        data["email"],
        phone
    ))

    doctor_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO users
    (
        username,
        password,
        role,
        doctor_id
    )
    VALUES (?, ?, ?, ?)
    """, (
        data["username"],
        generate_password_hash(
            data["password"]
        ),
        "doctor",
        doctor_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Doctor Added Successfully",
        "doctor_id": doctor_id
    })


# ==========================================
# DOCTOR PATIENTS
# ==========================================

@app.route("/doctor_patients/<int:id>")
def doctor_patients(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT patients.*
    FROM patients
    JOIN appointments
    ON patients.id = appointments.patient_id
    WHERE appointments.doctor_id = ?
    """, (id,))

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# DOCTOR APPOINTMENTS
# ==========================================

@app.route("/doctor_appointments/<int:id>")
def doctor_appointments(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM appointments
    WHERE doctor_id=?
    """, (id,))

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )
# ==========================================
# CREATE APPOINTMENT
# ==========================================

@app.route("/appointment", methods=["POST"])
def create_appointment():

    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO appointments
    (
        patient_id,
        doctor_id,
        date,
        reason
    )
    VALUES (?, ?, ?, ?)
    """, (
        data["patient_id"],
        data["doctor_id"],
        data["date"],
        data["reason"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Appointment Booked Successfully"
    })


# ==========================================
# GET ALL APPOINTMENTS
# ==========================================

@app.route("/appointments")
def appointments():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM appointments
    """)

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# UPDATE APPOINTMENT STATUS
# ==========================================

@app.route("/appointment/<int:id>", methods=["PUT"])
def update_appointment(id):

    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE appointments
    SET status=?
    WHERE id=?
    """, (
        data["status"].lower(),
        id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Appointment Updated Successfully"
    })


# ==========================================
# PATIENT APPOINTMENTS
# ==========================================

@app.route("/patient_appointments/<int:id>")
def patient_appointments(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM appointments
    WHERE patient_id=?
    """, (id,))

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# CREATE RECORD
# ==========================================

@app.route("/record", methods=["POST"])
def add_record():

    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO records
    (
        patient_id,
        doctor_id,
        diagnosis,
        treatment,
        date
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        data["patient_id"],
        data["doctor_id"],
        data["diagnosis"],
        data["treatment"],
        data["date"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Medical Record Added Successfully"
    })


# ==========================================
# GET ALL RECORDS
# ==========================================

@app.route("/records")
def all_records():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM records
    """)

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# GET PATIENT RECORDS
# ==========================================

@app.route("/records/<int:id>")
def patient_records(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM records
    WHERE patient_id=?
    """, (id,))

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# CREATE PRESCRIPTION
# ==========================================

@app.route("/prescription", methods=["POST"])
def create_prescription():

    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO prescriptions
    (
        record_id,
        drug_name,
        dosage
    )
    VALUES (?, ?, ?)
    """, (
        data["record_id"],
        data["drug_name"],
        data["dosage"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Prescription Added Successfully"
    })


# ==========================================
# GET ALL PRESCRIPTIONS
# ==========================================

@app.route("/prescriptions")
def all_prescriptions():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM prescriptions
    """)

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# GET PATIENT PRESCRIPTIONS
# ==========================================

@app.route("/prescriptions/<int:patient_id>")
def patient_prescriptions(patient_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT prescriptions.*
    FROM prescriptions
    JOIN records
    ON prescriptions.record_id = records.id
    WHERE records.patient_id = ?
    """, (patient_id,))

    data = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in data]
    )


# ==========================================
# ADMIN DASHBOARD STATS
# ==========================================

@app.route("/stats")
def stats():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM patients")
    patients = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM doctors")
    doctors = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM appointments")
    appointments = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM records")
    records = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM prescriptions")
    prescriptions = cursor.fetchone()["total"]

    conn.close()

    return jsonify({
        "patients": patients,
        "doctors": doctors,
        "appointments": appointments,
        "records": records,
        "prescriptions": prescriptions
    })

@app.route("/debug_users")
def debug_users():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, role, doctor_id, patient_id FROM users"
    )

    users = cursor.fetchall()

    conn.close()

    return jsonify(
        [dict(x) for x in users]
    )
# ==========================================
# RUN APP
# ==========================================

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )