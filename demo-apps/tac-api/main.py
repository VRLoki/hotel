#!/usr/bin/env python3
"""TAC Spa Management API - Mock for Eden Rock St Barths"""

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Optional

DB_PATH = "/opt/tac-api/tac.db"
API_KEY = "tac-demo-2026"
LOCATION_ID = "EDENROCK-SPA"

app = FastAPI(title="TAC Spa API", version="2.0.0")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def require_auth(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def require_location(locationId: str):
    if locationId != LOCATION_ID:
        raise HTTPException(status_code=404, detail="Location not found")

def rows_to_list(rows):
    return [dict(r) for r in rows]

@app.get("/health")
def health():
    return {"status": "healthy", "service": "tac-spa-api", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.get("/api/v2/locations/{locationId}/treatments")
def get_treatments(locationId: str, category: Optional[str] = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), x_api_key: str = Header(None)):
    require_auth(x_api_key)
    require_location(locationId)
    db = get_db()
    q = "SELECT * FROM treatments"
    params = []
    if category:
        q += " WHERE category = ?"
        params.append(category)
    total = db.execute(q.replace("*", "COUNT(*)"), params).fetchone()[0]
    q += " ORDER BY category, name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(q, params).fetchall()
    treatments = []
    for r in rows:
        treatments.append({
            "treatmentId": r["id"],
            "name": r["name"],
            "category": r["category"],
            "description": r["description"],
            "durationMinutes": r["duration_minutes"],
            "priceEur": r["price_eur"],
            "isSignature": bool(r["is_signature"]),
            "isAvailable": bool(r["is_available"])
        })
    db.close()
    return {"data": treatments, "pagination": {"total": total, "limit": limit, "offset": offset}}

@app.get("/api/v2/locations/{locationId}/therapists")
def get_therapists(locationId: str, specialty: Optional[str] = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), x_api_key: str = Header(None)):
    require_auth(x_api_key)
    require_location(locationId)
    db = get_db()
    q = "SELECT * FROM therapists"
    params = []
    if specialty:
        q += " WHERE specialties LIKE ?"
        params.append(f"%{specialty}%")
    total = db.execute(q.replace("*", "COUNT(*)"), params).fetchone()[0]
    q += " ORDER BY name LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(q, params).fetchall()
    therapists = []
    for r in rows:
        therapists.append({
            "therapistId": r["id"],
            "name": r["name"],
            "specialties": r["specialties"].split(",") if r["specialties"] else [],
            "certifications": r["certifications"].split(",") if r["certifications"] else [],
            "yearsExperience": r["years_experience"],
            "rating": r["rating"],
            "isAvailableToday": bool(r["is_available_today"]),
            "schedule": r["schedule"]
        })
    db.close()
    return {"data": therapists, "pagination": {"total": total, "limit": limit, "offset": offset}}

@app.get("/api/v2/locations/{locationId}/bookings")
def get_bookings(locationId: str, date: Optional[str] = None, status: Optional[str] = None, guestName: Optional[str] = None, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), x_api_key: str = Header(None)):
    require_auth(x_api_key)
    require_location(locationId)
    db = get_db()
    q = "SELECT b.*, t.name as treatment_name, t.price_eur, t.duration_minutes, th.name as therapist_name FROM bookings b JOIN treatments t ON b.treatment_id = t.id JOIN therapists th ON b.therapist_id = th.id"
    conditions = []
    params = []
    if date:
        conditions.append("b.booking_date = ?")
        params.append(date)
    if status:
        conditions.append("b.status = ?")
        params.append(status)
    if guestName:
        conditions.append("b.guest_name LIKE ?")
        params.append(f"%{guestName}%")
    if conditions:
        q += " WHERE " + " AND ".join(conditions)
    count_q = q.replace("b.*, t.name as treatment_name, t.price_eur, t.duration_minutes, th.name as therapist_name", "COUNT(*)")
    total = db.execute(count_q, params).fetchone()[0]
    q += " ORDER BY b.booking_date, b.booking_time LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(q, params).fetchall()
    bookings = []
    for r in rows:
        bookings.append({
            "bookingId": r["id"],
            "guestName": r["guest_name"],
            "roomNumber": r["room_number"],
            "treatmentName": r["treatment_name"],
            "therapistName": r["therapist_name"],
            "bookingDate": r["booking_date"],
            "bookingTime": r["booking_time"],
            "durationMinutes": r["duration_minutes"],
            "priceEur": r["price_eur"],
            "status": r["status"],
            "specialRequests": r["special_requests"],
            "isCouplesTreatment": bool(r["is_couples"])
        })
    db.close()
    return {"data": bookings, "pagination": {"total": total, "limit": limit, "offset": offset}}

@app.get("/api/v2/locations/{locationId}/revenue")
def get_revenue(locationId: str, startDate: Optional[str] = None, endDate: Optional[str] = None, x_api_key: str = Header(None)):
    require_auth(x_api_key)
    require_location(locationId)
    db = get_db()
    q = "SELECT * FROM daily_revenue"
    conditions = []
    params = []
    if startDate:
        conditions.append("revenue_date >= ?")
        params.append(startDate)
    if endDate:
        conditions.append("revenue_date <= ?")
        params.append(endDate)
    if conditions:
        q += " WHERE " + " AND ".join(conditions)
    q += " ORDER BY revenue_date DESC"
    rows = db.execute(q, params).fetchall()
    revenue = []
    for r in rows:
        revenue.append({
            "date": r["revenue_date"],
            "totalRevenue": r["total_revenue"],
            "bookingsCount": r["bookings_count"],
            "averageBookingValue": r["avg_booking_value"],
            "occupancyRate": r["occupancy_rate"]
        })
    db.close()
    return {"data": revenue, "currency": "EUR", "locationId": LOCATION_ID}

@app.get("/api/v2/locations/{locationId}/statistics")
def get_statistics(locationId: str, x_api_key: str = Header(None)):
    require_auth(x_api_key)
    require_location(locationId)
    db = get_db()
    today = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    
    total_bookings = db.execute("SELECT COUNT(*) FROM bookings WHERE booking_date BETWEEN ? AND ?", (week_ago, today)).fetchone()[0]
    total_revenue = db.execute("SELECT COALESCE(SUM(total_revenue),0) FROM daily_revenue WHERE revenue_date BETWEEN ? AND ?", (week_ago, today)).fetchone()[0]
    popular = db.execute("""
        SELECT t.name, COUNT(*) as cnt FROM bookings b 
        JOIN treatments t ON b.treatment_id = t.id 
        WHERE b.booking_date BETWEEN ? AND ?
        GROUP BY t.name ORDER BY cnt DESC LIMIT 5
    """, (week_ago, today)).fetchall()
    therapist_util = db.execute("""
        SELECT th.name, COUNT(*) as cnt FROM bookings b
        JOIN therapists th ON b.therapist_id = th.id
        WHERE b.booking_date BETWEEN ? AND ?
        GROUP BY th.name ORDER BY cnt DESC
    """, (week_ago, today)).fetchall()
    
    db.close()
    return {
        "period": {"startDate": week_ago, "endDate": today},
        "totalBookings": total_bookings,
        "totalRevenue": total_revenue,
        "currency": "EUR",
        "popularTreatments": [{"name": r["name"], "bookings": r["cnt"]} for r in popular],
        "therapistUtilization": [{"name": r["name"], "bookings": r["cnt"]} for r in therapist_util],
        "averageOccupancyRate": 78.5,
        "guestSatisfactionScore": 4.8
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
