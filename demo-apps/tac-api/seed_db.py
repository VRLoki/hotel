#!/usr/bin/env python3
"""Seed TAC Spa database with realistic Eden Rock data"""
import sqlite3
import os
from datetime import date, timedelta
import random

DB_PATH = "/opt/tac-api/tac.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.executescript("""
CREATE TABLE treatments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    duration_minutes INTEGER,
    price_eur REAL,
    is_signature INTEGER DEFAULT 0,
    is_available INTEGER DEFAULT 1
);

CREATE TABLE therapists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    specialties TEXT,
    certifications TEXT,
    years_experience INTEGER,
    rating REAL,
    is_available_today INTEGER DEFAULT 1,
    schedule TEXT
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    guest_name TEXT NOT NULL,
    room_number TEXT,
    treatment_id INTEGER,
    therapist_id INTEGER,
    booking_date TEXT,
    booking_time TEXT,
    status TEXT DEFAULT 'confirmed',
    special_requests TEXT,
    is_couples INTEGER DEFAULT 0,
    FOREIGN KEY (treatment_id) REFERENCES treatments(id),
    FOREIGN KEY (therapist_id) REFERENCES therapists(id)
);

CREATE TABLE daily_revenue (
    id INTEGER PRIMARY KEY,
    revenue_date TEXT UNIQUE,
    total_revenue REAL,
    bookings_count INTEGER,
    avg_booking_value REAL,
    occupancy_rate REAL
);
""")

# Treatments
treatments = [
    ("Deep Tissue Sculpting Massage", "massage", "Intensive deep tissue work targeting chronic tension with warm volcanic stones", 90, 320, 1),
    ("Caribbean Relaxation Massage", "massage", "Full-body Swedish massage with coconut and monoi oil blend", 60, 195, 0),
    ("Hot Stone Harmony", "massage", "Heated basalt stones combined with flowing massage techniques", 75, 265, 0),
    ("Couples Ocean Breeze Massage", "massage", "Side-by-side relaxation massage in our couples suite overlooking the bay", 90, 480, 1),
    ("Bamboo Fusion Massage", "massage", "Heated bamboo sticks used for deep rolling and kneading", 60, 210, 0),
    ("Eden Rock Signature Facial", "facial", "Customized facial using La Mer products with LED light therapy", 90, 385, 1),
    ("Hydra-Lift Gold Facial", "facial", "24k gold mask with hyaluronic acid infusion and micro-current lifting", 75, 350, 0),
    ("After-Sun Rescue Facial", "facial", "Cooling aloe and cucumber treatment with collagen boost", 45, 165, 0),
    ("Gentleman's Precision Facial", "facial", "Deep cleansing and anti-aging treatment designed for men", 60, 195, 0),
    ("Volcanic Sand Body Scrub", "body", "Exfoliating scrub with local volcanic sand and sea salt crystals", 45, 155, 0),
    ("Coconut Milk Body Wrap", "body", "Nourishing full-body wrap with organic coconut milk and shea butter", 60, 225, 0),
    ("Detox Sea Algae Wrap", "body", "Marine algae wrap for detoxification and remineralization", 75, 275, 1),
    ("Thalassotherapy Circuit", "hydrotherapy", "Heated seawater pool circuit with jet massage stations", 90, 195, 0),
    ("Private Vitality Pool Session", "hydrotherapy", "Exclusive use of hydrotherapy pool with chromotherapy", 60, 245, 0),
    ("Valentine's Couples Retreat", "couples", "Champagne, couples massage, facial, and private pool — our Valentine's special", 120, 890, 1),
    ("Sunset Yoga & Meditation", "wellness", "Private guided session on the terrace at golden hour", 60, 145, 0),
    ("Prenatal Serenity Massage", "massage", "Gentle massage adapted for expectant mothers with organic oils", 60, 210, 0),
]

for t in treatments:
    c.execute("INSERT INTO treatments (name, category, description, duration_minutes, price_eur, is_signature) VALUES (?,?,?,?,?,?)", t)

# Therapists
therapists = [
    ("Isabelle Moreau", "massage,deep tissue,hot stone", "CIDESCO,Swedish Massage", 12, 4.9, 1, "09:00-18:00"),
    ("Jean-Marc Dupont", "massage,sports,bamboo", "Sports Massage,Deep Tissue", 8, 4.7, 1, "10:00-19:00"),
    ("Lucia Fernandez", "facial,body,anti-aging", "CIDESCO,La Mer Certified", 15, 4.9, 1, "09:00-17:00"),
    ("Amara Okafor", "massage,couples,prenatal", "Prenatal Certified,Aromatherapy", 6, 4.8, 1, "08:00-16:00"),
    ("Yuki Sato", "facial,hydrotherapy,wellness", "Japanese Skincare,Thalassotherapy", 10, 4.8, 1, "10:00-19:00"),
    ("Pierre Lefèvre", "hydrotherapy,body,scrub", "Thalassotherapy,Marine Biology", 9, 4.6, 0, "09:00-18:00"),
    ("Camille Beaumont", "massage,facial,couples", "CIDESCO,Holistic Therapy", 7, 4.7, 1, "11:00-20:00"),
    ("Rafael Costa", "massage,deep tissue,sports", "Myofascial Release,Kinesiology", 5, 4.5, 1, "08:00-17:00"),
]

for t in therapists:
    c.execute("INSERT INTO therapists (name, specialties, certifications, years_experience, rating, is_available_today, schedule) VALUES (?,?,?,?,?,?,?)", t)

# Bookings - next 7 days
today = date.today()
guests = [
    ("James Richardson", "201"), ("Isabelle Laurent", "305"), ("Khalid Al-Rashid", "PH1"),
    ("Sofia Ferragamo", "402"), ("Wei Chen", "118"), ("Dmitri Petrov", "510"),
    ("Maria Santos", "225"), ("Hiroshi Tanaka", "330"),
    ("Mrs. Richardson", "201"), ("Mrs. Al-Rashid", "PH1"),
]

times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"]
statuses = ["confirmed", "confirmed", "confirmed", "confirmed", "completed", "confirmed", "in-progress"]
special_reqs = [None, None, None, "Extra firm pressure please", "Allergic to nuts — no almond oil", "Prefers female therapist", "Birthday celebration — add champagne", "Valentine's surprise for wife", None, "Late arrival — please hold 15 min"]

booking_id = 0
for day_offset in range(8):
    d = today + timedelta(days=day_offset)
    ds = d.isoformat()
    num_bookings = random.randint(3, 6)
    used_times = set()
    for _ in range(num_bookings):
        booking_id += 1
        guest = random.choice(guests)
        treatment_id = random.randint(1, len(treatments))
        therapist_id = random.randint(1, len(therapists))
        t = random.choice([x for x in times if x not in used_times])
        used_times.add(t)
        status = "confirmed" if day_offset > 0 else random.choice(statuses)
        sr = random.choice(special_reqs)
        is_couples = 1 if treatment_id in (4, 15) else 0
        c.execute("INSERT INTO bookings (guest_name, room_number, treatment_id, therapist_id, booking_date, booking_time, status, special_requests, is_couples) VALUES (?,?,?,?,?,?,?,?,?)",
                  (guest[0], guest[1], treatment_id, therapist_id, ds, t, status, sr, is_couples))

# Ensure Valentine's Day bookings (Feb 15 is today in this scenario)
valentine = today.isoformat()
c.execute("INSERT INTO bookings (guest_name, room_number, treatment_id, therapist_id, booking_date, booking_time, status, special_requests, is_couples) VALUES (?,?,?,?,?,?,?,?,?)",
          ("James Richardson", "201", 15, 7, valentine, "16:00", "confirmed", "Valentine's surprise — champagne and roses in suite", 1))
c.execute("INSERT INTO bookings (guest_name, room_number, treatment_id, therapist_id, booking_date, booking_time, status, special_requests, is_couples) VALUES (?,?,?,?,?,?,?,?,?)",
          ("Khalid Al-Rashid", "PH1", 15, 1, valentine, "17:00", "confirmed", "Valentine's couples retreat — wife's birthday too", 1))
c.execute("INSERT INTO bookings (guest_name, room_number, treatment_id, therapist_id, booking_date, booking_time, status, special_requests, is_couples) VALUES (?,?,?,?,?,?,?,?,?)",
          ("Sofia Ferragamo", "402", 6, 3, valentine, "11:00", "confirmed", "Valentine's pampering day", 0))

# Revenue
for day_offset in range(-3, 8):
    d = today + timedelta(days=day_offset)
    ds = d.isoformat()
    rev = round(random.uniform(2800, 6500), 2)
    cnt = random.randint(6, 14)
    avg = round(rev / cnt, 2)
    occ = round(random.uniform(65, 95), 1)
    c.execute("INSERT OR IGNORE INTO daily_revenue (revenue_date, total_revenue, bookings_count, avg_booking_value, occupancy_rate) VALUES (?,?,?,?,?)",
              (ds, rev, cnt, avg, occ))

conn.commit()
conn.close()
print(f"Database seeded at {DB_PATH}")
