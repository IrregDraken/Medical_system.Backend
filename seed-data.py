from db import get_db
from werkzeug.security import generate_password_hash

conn = get_db()
cursor = conn.cursor()

# =========================
# DOCTORS
# =========================

doctors = [
    ("Dr. Grace Okafor", "General Medicine", "grace.okafor@riversidehc.com", "08031234567", "gokafor"),
    ("Dr. Chinedu Eze", "Cardiology", "chinedu.eze@riversidehc.com", "08042345678", "ceze"),
    ("Dr. Amina Bello", "Pediatrics", "amina.bello@riversidehc.com", "08053456789", "abello"),
    ("Dr. Samuel Adeyemi", "Surgery", "samuel.adeyemi@riversidehc.com", "08064567890", "sadeyemi"),
    ("Dr. Esther Johnson", "Obstetrics & Gynecology", "esther.johnson@riversidehc.com", "08075678901", "ejohnson")
]

for doctor in doctors:

    name, specialty, email, phone, username = doctor

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    if cursor.fetchone():
        continue

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
        name,
        specialty,
        email,
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
        username,
        generate_password_hash("doctor123"),
        "doctor",
        doctor_id
    ))

# =========================
# PATIENTS
# =========================

patients = [
    ("John Doe",25,"Male","08012345678","Port Harcourt","RHC001"),
    ("Mary Williams",32,"Female","08022345678","Port Harcourt","RHC002"),
    ("David Johnson",41,"Male","08032345678","Aba","RHC003"),
    ("Blessing Okoro",28,"Female","08042345679","Owerri","RHC004"),
    ("Michael James",35,"Male","08052345670","Enugu","RHC005"),
    ("Chiamaka Nwosu",22,"Female","08062345671","Umuahia","RHC006"),
    ("Daniel Peters",47,"Male","08072345672","Port Harcourt","RHC007"),
    ("Fatima Yusuf",30,"Female","08082345673","Kano","RHC008"),
    ("Emmanuel Ojo",38,"Male","08092345674","Lagos","RHC009"),
    ("Ruth Solomon",27,"Female","08102345675","Abuja","RHC010")
]

for patient in patients:

    full_name, age, gender, phone, address, card_id = patient

    cursor.execute(
        "SELECT * FROM patients WHERE card_id=?",
        (card_id,)
    )

    existing = cursor.fetchone()

    if existing:
        continue

    cursor.execute("""
    INSERT INTO patients
    (
        full_name,
        age,
        gender,
        phone,
        address,
        card_id
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        full_name,
        age,
        gender,
        phone,
        address,
        card_id
    ))

    patient_id = cursor.lastrowid

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
        generate_password_hash("patient123"),
        "patient",
        patient_id
    ))

# =========================
# APPOINTMENTS
# =========================

appointments = [
    (1,1,"2026-06-10","Fever and Headache","approved"),
    (2,3,"2026-06-11","Child Consultation","pending"),
    (3,2,"2026-06-12","Chest Pain","approved"),
    (4,5,"2026-06-13","Antenatal Checkup","completed"),
    (5,4,"2026-06-14","Surgical Review","pending")
]

for appointment in appointments:

    cursor.execute("""
    INSERT INTO appointments
    (
        patient_id,
        doctor_id,
        date,
        reason,
        status
    )
    VALUES (?, ?, ?, ?, ?)
    """, appointment)

# =========================
# MEDICAL RECORDS
# =========================

records = [
    (1,1,"Malaria","Artemisinin Combination Therapy","2026-06-10"),
    (3,2,"Hypertension","Amlodipine 5mg Daily","2026-06-12"),
    (4,5,"Pregnancy Monitoring","Routine Antenatal Care","2026-06-13"),
    (5,4,"Appendicitis","Surgical Intervention","2026-06-14"),
    (2,3,"Childhood Flu","Symptomatic Treatment","2026-06-11")
]

for record in records:

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
    """, record)

# =========================
# PRESCRIPTIONS
# =========================

prescriptions = [
    (1,"Coartem","2 tablets twice daily"),
    (2,"Amlodipine","5mg once daily"),
    (3,"Prenatal Vitamins","1 tablet daily"),
    (4,"Antibiotics","As prescribed"),
    (5,"Paracetamol","500mg three times daily")
]

for prescription in prescriptions:

    cursor.execute("""
    INSERT INTO prescriptions
    (
        record_id,
        drug_name,
        dosage
    )
    VALUES (?, ?, ?)
    """, prescription)

conn.commit()
conn.close()

print("Database seeded successfully.")