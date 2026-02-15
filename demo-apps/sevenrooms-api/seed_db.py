#!/usr/bin/env python3
"""Seed SevenRooms database with realistic Eden Rock data"""
import sqlite3
import os
from datetime import date, timedelta, datetime
import random

DB_PATH = "/opt/sevenrooms-api/sevenrooms.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.executescript("""
CREATE TABLE venues (
    id INTEGER PRIMARY KEY,
    venue_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    type TEXT,
    capacity INTEGER,
    description TEXT,
    opening_hours TEXT,
    dress_code TEXT,
    cuisine TEXT
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY,
    venue_id TEXT NOT NULL,
    guest_name TEXT NOT NULL,
    room_number TEXT,
    covers INTEGER,
    reservation_date TEXT,
    reservation_time TEXT,
    status TEXT DEFAULT 'confirmed',
    table_number TEXT,
    special_requests TEXT,
    is_vip INTEGER DEFAULT 0,
    occasion TEXT,
    allergy_notes TEXT,
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

CREATE TABLE guest_profiles (
    id INTEGER PRIMARY KEY,
    venue_id TEXT NOT NULL,
    guest_name TEXT NOT NULL,
    room_number TEXT,
    vip_tier TEXT,
    total_visits INTEGER,
    total_spend REAL,
    preferred_table TEXT,
    dietary_preferences TEXT,
    allergies TEXT,
    favorite_items TEXT,
    notes TEXT,
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

CREATE TABLE waitlist (
    id INTEGER PRIMARY KEY,
    venue_id TEXT NOT NULL,
    guest_name TEXT NOT NULL,
    party_size INTEGER,
    estimated_wait_min INTEGER,
    created_at TEXT,
    status TEXT DEFAULT 'waiting',
    notes TEXT,
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);

CREATE TABLE daily_revenue (
    id INTEGER PRIMARY KEY,
    venue_id TEXT NOT NULL,
    revenue_date TEXT,
    total_revenue REAL,
    covers INTEGER,
    avg_check REAL,
    food_revenue REAL,
    beverage_revenue REAL,
    UNIQUE(venue_id, revenue_date),
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);
""")

# Venues
venues = [
    ("jg-restaurant", "Jean-Georges Restaurant", "fine-dining", 60, "Michelin-starred French-Caribbean fine dining by Jean-Georges Vongerichten with panoramic ocean views", "Lunch 12:00-14:30, Dinner 19:00-22:30", "Smart elegant — no beachwear", "French-Caribbean fusion"),
    ("sand-bar", "Sand Bar", "casual-dining", 40, "Barefoot beachside dining with fresh seafood, salads, and Caribbean classics on the sand", "11:00-18:00", "Casual beach attire", "Seafood, Caribbean, Mediterranean"),
    ("rock-bar", "Rock Bar", "cocktail-bar", 30, "Sophisticated cocktail bar with craft cocktails, champagne, and light bites at sunset", "17:00-01:00", "Resort casual", "Cocktails, champagne, tapas"),
]
for v in venues:
    c.execute("INSERT INTO venues (venue_id, name, type, capacity, description, opening_hours, dress_code, cuisine) VALUES (?,?,?,?,?,?,?,?)", v)

# Guests with preferences
guests = [
    ("James Richardson", "201", "VIP", "No shellfish", "Bordeaux wines, steak tartare"),
    ("Isabelle Laurent", "305", "Gold", None, "Vegetarian options, French wines"),
    ("Khalid Al-Rashid", "PH1", "Platinum", "No pork, halal preferred", "Lamb dishes, sparkling water"),
    ("Sofia Ferragamo", "402", "VIP", "Gluten intolerant", "Seafood, Prosecco, light dishes"),
    ("Wei Chen", "118", "Gold", "Mild shellfish allergy", "Sashimi, sake, umami flavors"),
    ("Dmitri Petrov", "510", "VIP", None, "Caviar, vodka, beef dishes"),
    ("Maria Santos", "225", "Gold", "Lactose intolerant", "Grilled fish, tropical cocktails"),
    ("Hiroshi Tanaka", "330", "Gold", None, "Omakase-style, whisky, clean flavors"),
]

# Guest profiles for each venue
for vid, _, vtype, *_ in venues:
    for g in guests:
        visits = random.randint(2, 15)
        spend = round(random.uniform(800, 8000) if vtype == "fine-dining" else random.uniform(200, 2000), 2)
        table_pref = random.choice(["Window", "Terrace", "Corner booth", "Bar adjacent", "Ocean view", None, None])
        notes_options = [
            "Returning guest — always impeccable",
            "Celebrates anniversaries here",
            "Prefers quiet corner",
            "Excellent wine knowledge",
            "Always orders the tasting menu",
            "Regular — knows the staff by name",
            "First visit this season",
            None
        ]
        c.execute("INSERT INTO guest_profiles (venue_id, guest_name, room_number, vip_tier, total_visits, total_spend, preferred_table, dietary_preferences, allergies, favorite_items, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (vid, g[0], g[1], g[2], visits, spend, table_pref, g[4], g[3], g[4], random.choice(notes_options)))

# Reservations
today = date.today()
lunch_times = ["12:00", "12:15", "12:30", "12:45", "13:00", "13:15", "13:30", "13:45", "14:00"]
dinner_times = ["19:00", "19:15", "19:30", "19:45", "20:00", "20:15", "20:30", "20:45", "21:00", "21:30"]
bar_times = ["17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30"]
sand_times = ["11:30", "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00"]

occasions = [None, None, None, "Birthday", "Anniversary", "Valentine's Day", "Business dinner", None]
special_reqs_list = [
    None, None, None,
    "Window table if possible",
    "Quiet area please",
    "Celebrating — please prepare dessert with candle",
    "Need high chair for child",
    "Tasting menu pre-ordered",
    "Valentine's set menu with champagne pairing",
    "Chef's table experience requested",
    "Late arrival — hold table 15 min"
]

tables_jg = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12", "Chef's Table"]
tables_sand = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
tables_rock = ["R1", "R2", "R3", "R4", "R5", "R6"]

for day_offset in range(8):
    d = today + timedelta(days=day_offset)
    ds = d.isoformat()
    
    # Jean-Georges: lunch + dinner
    for meal_times in [lunch_times, dinner_times]:
        n = random.randint(3, 6)
        used = set()
        for _ in range(n):
            g = random.choice(guests)
            t = random.choice([x for x in meal_times if x not in used] or meal_times)
            used.add(t)
            covers = random.choice([2, 2, 2, 2, 3, 4, 4, 6])
            status = "confirmed" if day_offset > 0 else random.choice(["confirmed", "seated", "completed", "confirmed"])
            c.execute("INSERT INTO reservations (venue_id, guest_name, room_number, covers, reservation_date, reservation_time, status, table_number, special_requests, is_vip, occasion, allergy_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                      ("jg-restaurant", g[0], g[1], covers, ds, t, status, random.choice(tables_jg), random.choice(special_reqs_list), 1 if g[2] in ("VIP","Platinum") else 0, random.choice(occasions), g[3]))

    # Sand Bar
    n = random.randint(3, 5)
    for _ in range(n):
        g = random.choice(guests)
        t = random.choice(sand_times)
        c.execute("INSERT INTO reservations (venue_id, guest_name, room_number, covers, reservation_date, reservation_time, status, table_number, special_requests, is_vip, occasion, allergy_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                  ("sand-bar", g[0], g[1], random.choice([2,2,3,4]), ds, t, "confirmed", random.choice(tables_sand), random.choice([None, "Beachfront please", "Shade preferred"]), 0, None, g[3]))

    # Rock Bar
    n = random.randint(2, 4)
    for _ in range(n):
        g = random.choice(guests)
        t = random.choice(bar_times)
        c.execute("INSERT INTO reservations (venue_id, guest_name, room_number, covers, reservation_date, reservation_time, status, table_number, special_requests, is_vip, occasion, allergy_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                  ("rock-bar", g[0], g[1], random.choice([2,2,3,4]), ds, t, "confirmed", random.choice(tables_rock), random.choice([None, "Sunset view", "Near the bar"]), 1 if g[2]=="Platinum" else 0, random.choice([None, None, "Valentine's cocktails"]), None))

# Valentine's Day special reservations (today = Feb 15, but seed for both Feb 14 and 15)
for vday in [today, today - timedelta(days=1)]:
    vds = vday.isoformat()
    c.execute("INSERT INTO reservations (venue_id, guest_name, room_number, covers, reservation_date, reservation_time, status, table_number, special_requests, is_vip, occasion, allergy_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
              ("jg-restaurant", "James Richardson", "201", 2, vds, "20:00", "confirmed", "T4", "Valentine's dinner — 6-course tasting menu with champagne pairing, rose petals on table", 1, "Valentine's Day", "No shellfish"))
    c.execute("INSERT INTO reservations (venue_id, guest_name, room_number, covers, reservation_date, reservation_time, status, table_number, special_requests, is_vip, occasion, allergy_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
              ("jg-restaurant", "Khalid Al-Rashid", "PH1", 2, vds, "20:30", "confirmed", "Chef's Table", "Valentine's special — private chef's table experience, no pork, halal", 1, "Valentine's Day", "No pork, halal preferred"))

# Waitlist (current)
now = datetime.now().isoformat()
waitlist_entries = [
    ("jg-restaurant", "Walk-in Guest — Mr. Dubois", 2, 25, now, "waiting", "Hotel guest from room 115"),
    ("jg-restaurant", "External — Mrs. Beaumont", 4, 40, now, "waiting", "Called ahead, celebrating birthday"),
    ("rock-bar", "Mr. & Mrs. Thompson", 2, 15, now, "waiting", "Waiting for terrace seating"),
    ("sand-bar", "Garcia Family", 5, 20, now, "waiting", "Large party — need combined table"),
]
for w in waitlist_entries:
    c.execute("INSERT INTO waitlist (venue_id, guest_name, party_size, estimated_wait_min, created_at, status, notes) VALUES (?,?,?,?,?,?,?)", w)

# Revenue
for vid, _, vtype, *_ in venues:
    for day_offset in range(-3, 8):
        d = today + timedelta(days=day_offset)
        ds = d.isoformat()
        if vtype == "fine-dining":
            rev = round(random.uniform(8000, 18000), 2)
            cov = random.randint(35, 58)
            food_pct = 0.65
        elif vtype == "casual-dining":
            rev = round(random.uniform(3000, 7000), 2)
            cov = random.randint(20, 38)
            food_pct = 0.7
        else:
            rev = round(random.uniform(4000, 9000), 2)
            cov = random.randint(18, 30)
            food_pct = 0.3
        avg = round(rev / cov, 2)
        food = round(rev * food_pct, 2)
        bev = round(rev * (1 - food_pct), 2)
        c.execute("INSERT OR IGNORE INTO daily_revenue (venue_id, revenue_date, total_revenue, covers, avg_check, food_revenue, beverage_revenue) VALUES (?,?,?,?,?,?,?)",
                  (vid, ds, rev, cov, avg, food, bev))

conn.commit()
conn.close()
print(f"Database seeded at {DB_PATH}")
