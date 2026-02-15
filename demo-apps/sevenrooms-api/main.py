#!/usr/bin/env python3
"""SevenRooms Restaurant/Bar API - Mock for Eden Rock St Barths"""

from fastapi import FastAPI, Header, HTTPException, Query
import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Optional

DB_PATH = "/opt/sevenrooms-api/sevenrooms.db"
API_KEY = "7rooms-demo-2026"

app = FastAPI(title="SevenRooms API", version="1.0.0")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def require_auth(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def check_venue(db, venueId):
    v = db.execute("SELECT * FROM venues WHERE venue_id = ?", (venueId,)).fetchone()
    if not v:
        raise HTTPException(status_code=404, detail="Venue not found")
    return v

@app.get("/health")
def health():
    return {"status": "healthy", "service": "sevenrooms-api", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.get("/api/v1/venues")
def list_venues(x_api_key: str = Header(None)):
    require_auth(x_api_key)
    db = get_db()
    rows = db.execute("SELECT * FROM venues").fetchall()
    venues = []
    for r in rows:
        venues.append({
            "venueId": r["venue_id"],
            "name": r["name"],
            "type": r["type"],
            "capacity": r["capacity"],
            "description": r["description"],
            "openingHours": r["opening_hours"],
            "dressCode": r["dress_code"],
            "cuisine": r["cuisine"]
        })
    db.close()
    return {"data": venues, "venueGroupId": "edenrock-fb"}

@app.get("/api/v1/venues/{venueId}/reservations")
def get_reservations(venueId: str, date: Optional[str] = None, status: Optional[str] = None, guestName: Optional[str] = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), x_api_key: str = Header(None)):
    require_auth(x_api_key)
    db = get_db()
    check_venue(db, venueId)
    q = "SELECT * FROM reservations WHERE venue_id = ?"
    params = [venueId]
    if date:
        q += " AND reservation_date = ?"
        params.append(date)
    if status:
        q += " AND status = ?"
        params.append(status)
    if guestName:
        q += " AND guest_name LIKE ?"
        params.append(f"%{guestName}%")
    count_q = q.replace("*", "COUNT(*)")
    total = db.execute(count_q, params).fetchone()[0]
    q += " ORDER BY reservation_date, reservation_time LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(q, params).fetchall()
    reservations = []
    for r in rows:
        reservations.append({
            "reservationId": r["id"],
            "guestName": r["guest_name"],
            "roomNumber": r["room_number"],
            "covers": r["covers"],
            "reservationDate": r["reservation_date"],
            "reservationTime": r["reservation_time"],
            "status": r["status"],
            "tableNumber": r["table_number"],
            "specialRequests": r["special_requests"],
            "isVip": bool(r["is_vip"]),
            "occasion": r["occasion"],
            "allergyNotes": r["allergy_notes"]
        })
    db.close()
    return {"data": reservations, "pagination": {"total": total, "limit": limit, "offset": offset}}

@app.get("/api/v1/venues/{venueId}/guests")
def get_guests(venueId: str, guestName: Optional[str] = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), x_api_key: str = Header(None)):
    require_auth(x_api_key)
    db = get_db()
    check_venue(db, venueId)
    q = "SELECT * FROM guest_profiles WHERE venue_id = ?"
    params = [venueId]
    if guestName:
        q += " AND guest_name LIKE ?"
        params.append(f"%{guestName}%")
    total = db.execute(q.replace("*", "COUNT(*)"), params).fetchone()[0]
    q += " ORDER BY guest_name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(q, params).fetchall()
    guests = []
    for r in rows:
        guests.append({
            "guestId": r["id"],
            "guestName": r["guest_name"],
            "roomNumber": r["room_number"],
            "vipTier": r["vip_tier"],
            "totalVisits": r["total_visits"],
            "totalSpend": r["total_spend"],
            "preferredTable": r["preferred_table"],
            "dietaryPreferences": r["dietary_preferences"],
            "allergies": r["allergies"],
            "favoriteItems": r["favorite_items"],
            "notes": r["notes"]
        })
    db.close()
    return {"data": guests, "pagination": {"total": total, "limit": limit, "offset": offset}}

@app.get("/api/v1/venues/{venueId}/waitlist")
def get_waitlist(venueId: str, x_api_key: str = Header(None)):
    require_auth(x_api_key)
    db = get_db()
    check_venue(db, venueId)
    rows = db.execute("SELECT * FROM waitlist WHERE venue_id = ? ORDER BY created_at", (venueId,)).fetchall()
    entries = []
    for r in rows:
        entries.append({
            "waitlistId": r["id"],
            "guestName": r["guest_name"],
            "partySize": r["party_size"],
            "estimatedWaitMinutes": r["estimated_wait_min"],
            "createdAt": r["created_at"],
            "status": r["status"],
            "notes": r["notes"]
        })
    db.close()
    return {"data": entries}

@app.get("/api/v1/venues/{venueId}/revenue")
def get_revenue(venueId: str, startDate: Optional[str] = None, endDate: Optional[str] = None, x_api_key: str = Header(None)):
    require_auth(x_api_key)
    db = get_db()
    check_venue(db, venueId)
    q = "SELECT * FROM daily_revenue WHERE venue_id = ?"
    params = [venueId]
    if startDate:
        q += " AND revenue_date >= ?"
        params.append(startDate)
    if endDate:
        q += " AND revenue_date <= ?"
        params.append(endDate)
    q += " ORDER BY revenue_date DESC"
    rows = db.execute(q, params).fetchall()
    revenue = []
    for r in rows:
        revenue.append({
            "date": r["revenue_date"],
            "totalRevenue": r["total_revenue"],
            "covers": r["covers"],
            "averageCheck": r["avg_check"],
            "foodRevenue": r["food_revenue"],
            "beverageRevenue": r["beverage_revenue"]
        })
    db.close()
    return {"data": revenue, "currency": "EUR", "venueId": venueId}

@app.get("/api/v1/venues/{venueId}/statistics")
def get_statistics(venueId: str, x_api_key: str = Header(None)):
    require_auth(x_api_key)
    db = get_db()
    v = check_venue(db, venueId)
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    total_covers = db.execute("SELECT COALESCE(SUM(covers),0) FROM daily_revenue WHERE venue_id=? AND revenue_date BETWEEN ? AND ?", (venueId, week_ago, today)).fetchone()[0]
    total_rev = db.execute("SELECT COALESCE(SUM(total_revenue),0) FROM daily_revenue WHERE venue_id=? AND revenue_date BETWEEN ? AND ?", (venueId, week_ago, today)).fetchone()[0]
    avg_check = db.execute("SELECT COALESCE(AVG(avg_check),0) FROM daily_revenue WHERE venue_id=? AND revenue_date BETWEEN ? AND ?", (venueId, week_ago, today)).fetchone()[0]
    total_res = db.execute("SELECT COUNT(*) FROM reservations WHERE venue_id=? AND reservation_date BETWEEN ? AND ?", (venueId, week_ago, today)).fetchone()[0]
    
    # Popular times
    popular_times = db.execute("""
        SELECT reservation_time, COUNT(*) as cnt FROM reservations 
        WHERE venue_id=? AND reservation_date BETWEEN ? AND ?
        GROUP BY reservation_time ORDER BY cnt DESC LIMIT 5
    """, (venueId, week_ago, today)).fetchall()

    db.close()
    return {
        "period": {"startDate": week_ago, "endDate": today},
        "venueId": venueId,
        "venueName": v["name"],
        "totalCovers": total_covers,
        "totalRevenue": round(total_rev, 2),
        "averageCheck": round(avg_check, 2),
        "totalReservations": total_res,
        "currency": "EUR",
        "popularTimes": [{"time": r["reservation_time"], "reservations": r["cnt"]} for r in popular_times],
        "occupancyRate": 82.3,
        "noShowRate": 4.2,
        "averageDiningDuration": 95
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
