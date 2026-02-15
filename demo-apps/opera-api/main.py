"""Opera PMS OHIP-compatible REST API"""
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Optional
import oracledb
import json

DSN = "localhost:1521/XEPDB1"
DB_USER = "opera"
DB_PASS = "Opera2026"
API_KEY = "hotel-intel-2026"

pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = oracledb.create_pool(user=DB_USER, password=DB_PASS, dsn=DSN, min=2, max=10, increment=1)
    yield
    pool.close()

app = FastAPI(title="Opera PMS API", version="1.0.0", lifespan=lifespan)

def auth(key: str = Header(alias="x-api-key")):
    if key != API_KEY:
        raise HTTPException(401, "Invalid API key")

def serialize(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.isoformat()
    if hasattr(val, 'read'):  # CLOB
        return val.read()
    return val

def to_camel(s: str) -> str:
    parts = s.lower().split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

def rows_to_dicts(cur):
    cols = [to_camel(d[0]) for d in cur.description]
    return [dict(zip(cols, [serialize(v) for v in row])) for row in cur]

def paginated(data, offset, limit):
    return {"count": len(data), "offset": offset, "limit": limit, "hasMore": offset + limit < len(data), "results": data[offset:offset+limit]}

def get_conn():
    return pool.acquire()

# --- RESERVATIONS ---
@app.get("/api/v1/hotels/{hotelId}/reservations")
def list_reservations(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    arrivalDate: Optional[str] = None,
    departureDate: Optional[str] = None,
    status: Optional[str] = None,
    room: Optional[str] = None,
    guestName: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = """SELECT r.*, n.FIRST_NAME, n.LAST_NAME, n.VIP_STATUS, n.EMAIL as GUEST_EMAIL
             FROM RESERVATIONS r LEFT JOIN NAME_RECORDS n ON r.NAME_ID = n.NAME_ID
             WHERE r.RESORT_ID = :hotel"""
    params = {"hotel": hotelId}
    if arrivalDate:
        sql += " AND r.ARRIVAL_DATE >= TO_DATE(:arr, 'YYYY-MM-DD')"
        params["arr"] = arrivalDate
    if departureDate:
        sql += " AND r.DEPARTURE_DATE <= TO_DATE(:dep, 'YYYY-MM-DD')"
        params["dep"] = departureDate
    if status:
        sql += " AND r.RESV_STATUS = :st"
        params["st"] = status
    if room:
        sql += " AND r.ROOM_NUMBER = :rm"
        params["rm"] = room
    if guestName:
        sql += " AND (UPPER(n.FIRST_NAME) LIKE UPPER(:gn) OR UPPER(n.LAST_NAME) LIKE UPPER(:gn))"
        params["gn"] = f"%{guestName}%"
    sql += " ORDER BY r.ARRIVAL_DATE DESC"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        data = rows_to_dicts(cur)
    return paginated(data, offset, limit)

@app.get("/api/v1/hotels/{hotelId}/reservations/{confirmationNo}")
def get_reservation(hotelId: str, confirmationNo: str, x_api_key: str = Header(alias="x-api-key")):
    auth(x_api_key)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT r.*, n.FIRST_NAME, n.LAST_NAME, n.TITLE, n.VIP_STATUS, n.EMAIL as GUEST_EMAIL,
                       n.PHONE as GUEST_PHONE, n.NATIONALITY, n.MEMBERSHIP_TYPE, n.MEMBERSHIP_NUMBER,
                       n.PREFERENCES, n.ADDRESS1 as GUEST_ADDRESS, n.CITY as GUEST_CITY, n.COUNTRY as GUEST_COUNTRY
                       FROM RESERVATIONS r LEFT JOIN NAME_RECORDS n ON r.NAME_ID = n.NAME_ID
                       WHERE r.RESORT_ID = :hotel AND r.CONFIRMATION_NO = :conf""",
                    {"hotel": hotelId, "conf": confirmationNo})
        data = rows_to_dicts(cur)
    if not data:
        raise HTTPException(404, "Reservation not found")
    return data[0]

# --- GUESTS ---
@app.get("/api/v1/hotels/{hotelId}/guests")
def list_guests(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    name: Optional[str] = None,
    vipStatus: Optional[str] = None,
    nameType: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = """SELECT n.* FROM NAME_RECORDS n
             WHERE n.NAME_ID IN (SELECT DISTINCT r.NAME_ID FROM RESERVATIONS r WHERE r.RESORT_ID = :hotel)"""
    params = {"hotel": hotelId}
    if name:
        sql += " AND (UPPER(n.FIRST_NAME) LIKE UPPER(:nm) OR UPPER(n.LAST_NAME) LIKE UPPER(:nm))"
        params["nm"] = f"%{name}%"
    if vipStatus:
        sql += " AND n.VIP_STATUS = :vip"
        params["vip"] = vipStatus
    if nameType:
        sql += " AND n.NAME_TYPE = :nt"
        params["nt"] = nameType
    sql += " ORDER BY n.LAST_NAME, n.FIRST_NAME"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        data = rows_to_dicts(cur)
    return paginated(data, offset, limit)

@app.get("/api/v1/hotels/{hotelId}/guests/{nameId}")
def get_guest(hotelId: str, nameId: int, x_api_key: str = Header(alias="x-api-key")):
    auth(x_api_key)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT n.* FROM NAME_RECORDS n WHERE n.NAME_ID = :nid", {"nid": nameId})
        data = rows_to_dicts(cur)
        if not data:
            raise HTTPException(404, "Guest not found")
        guest = data[0]
        cur.execute("""SELECT CONFIRMATION_NO, ARRIVAL_DATE, DEPARTURE_DATE, ROOM_NUMBER, RESV_STATUS
                       FROM RESERVATIONS WHERE NAME_ID = :nid AND RESORT_ID = :hotel ORDER BY ARRIVAL_DATE DESC""",
                    {"nid": nameId, "hotel": hotelId})
        guest["reservationHistory"] = rows_to_dicts(cur)
    return guest

# --- ROOMS ---
@app.get("/api/v1/hotels/{hotelId}/rooms")
def list_rooms(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    roomType: Optional[str] = None,
    status: Optional[str] = None,
    foStatus: Optional[str] = None,
    floor: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = """SELECT rm.*, rt.DESCRIPTION as ROOM_TYPE_DESC, rt.RACK_RATE
             FROM ROOMS rm LEFT JOIN ROOM_TYPES rt ON rm.RESORT_ID = rt.RESORT_ID AND rm.ROOM_TYPE = rt.ROOM_TYPE
             WHERE rm.RESORT_ID = :hotel"""
    params = {"hotel": hotelId}
    if roomType:
        sql += " AND rm.ROOM_TYPE = :rt"
        params["rt"] = roomType
    if status:
        sql += " AND rm.ROOM_STATUS = :rs"
        params["rs"] = status
    if foStatus:
        sql += " AND rm.FO_STATUS = :fs"
        params["fs"] = foStatus
    if floor:
        sql += " AND rm.FLOOR_NUMBER = :fl"
        params["fl"] = floor
    sql += " ORDER BY rm.ROOM_NUMBER"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        data = rows_to_dicts(cur)
    return paginated(data, offset, limit)

@app.get("/api/v1/hotels/{hotelId}/rooms/{roomNumber}")
def get_room(hotelId: str, roomNumber: str, x_api_key: str = Header(alias="x-api-key")):
    auth(x_api_key)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT rm.*, rt.DESCRIPTION as ROOM_TYPE_DESC, rt.RACK_RATE
                       FROM ROOMS rm LEFT JOIN ROOM_TYPES rt ON rm.RESORT_ID = rt.RESORT_ID AND rm.ROOM_TYPE = rt.ROOM_TYPE
                       WHERE rm.RESORT_ID = :hotel AND rm.ROOM_NUMBER = :rn""",
                    {"hotel": hotelId, "rn": roomNumber})
        data = rows_to_dicts(cur)
        if not data:
            raise HTTPException(404, "Room not found")
        room = data[0]
        # Current guest if occupied
        cur.execute("""SELECT r.CONFIRMATION_NO, r.NAME_ID, n.FIRST_NAME, n.LAST_NAME, n.VIP_STATUS,
                       r.ARRIVAL_DATE, r.DEPARTURE_DATE
                       FROM RESERVATIONS r JOIN NAME_RECORDS n ON r.NAME_ID = n.NAME_ID
                       WHERE r.RESORT_ID = :hotel AND r.ROOM_NUMBER = :rn AND r.RESV_STATUS = 'CHECKED_IN'""",
                    {"hotel": hotelId, "rn": roomNumber})
        guests = rows_to_dicts(cur)
        room["currentGuest"] = guests[0] if guests else None
    return room

# --- HOUSEKEEPING ---
@app.get("/api/v1/hotels/{hotelId}/housekeeping")
def list_housekeeping(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    taskDate: Optional[str] = None,
    status: Optional[str] = None,
    room: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM HOUSEKEEPING_TASKS WHERE RESORT_ID = :hotel"
    params = {"hotel": hotelId}
    if taskDate:
        sql += " AND TASK_DATE = TO_DATE(:td, 'YYYY-MM-DD')"
        params["td"] = taskDate
    if status:
        sql += " AND STATUS = :st"
        params["st"] = status
    if room:
        sql += " AND ROOM_NUMBER = :rm"
        params["rm"] = room
    sql += " ORDER BY TASK_DATE DESC, ROOM_NUMBER"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        data = rows_to_dicts(cur)
    return paginated(data, offset, limit)

# --- CASHIER TRANSACTIONS ---
@app.get("/api/v1/hotels/{hotelId}/cashiers/transactions")
def list_transactions(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    room: Optional[str] = None,
    guestNameId: Optional[int] = None,
    folioNumber: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = """SELECT ft.*, r.CONFIRMATION_NO, r.NAME_ID, n.FIRST_NAME, n.LAST_NAME
             FROM FOLIO_TRANSACTIONS ft
             LEFT JOIN RESERVATIONS r ON ft.RESV_ID = r.RESV_ID
             LEFT JOIN NAME_RECORDS n ON r.NAME_ID = n.NAME_ID
             WHERE ft.RESORT_ID = :hotel"""
    params = {"hotel": hotelId}
    if fromDate:
        sql += " AND ft.TRX_DATE >= TO_DATE(:fd, 'YYYY-MM-DD')"
        params["fd"] = fromDate
    if toDate:
        sql += " AND ft.TRX_DATE <= TO_DATE(:td, 'YYYY-MM-DD')"
        params["td"] = toDate
    if room:
        sql += " AND ft.ROOM_NUMBER = :rm"
        params["rm"] = room
    if guestNameId:
        sql += " AND r.NAME_ID = :gn"
        params["gn"] = guestNameId
    if folioNumber:
        sql += " AND ft.FOLIO_NUMBER = :fn"
        params["fn"] = folioNumber
    sql += " ORDER BY ft.TRX_DATE DESC"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        data = rows_to_dicts(cur)
    return paginated(data, offset, limit)

# --- TRACES ---
@app.get("/api/v1/hotels/{hotelId}/traces")
def list_traces(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    traceDate: Optional[str] = None,
    department: Optional[str] = None,
    resolved: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM TRACES WHERE RESORT_ID = :hotel"
    params = {"hotel": hotelId}
    if traceDate:
        sql += " AND TRACE_DATE = TO_DATE(:td, 'YYYY-MM-DD')"
        params["td"] = traceDate
    if department:
        sql += " AND DEPARTMENT = :dep"
        params["dep"] = department
    if resolved:
        sql += " AND RESOLVED = :res"
        params["res"] = resolved
    sql += " ORDER BY TRACE_DATE DESC"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        data = rows_to_dicts(cur)
    return paginated(data, offset, limit)

# --- GROUPS ---
@app.get("/api/v1/hotels/{hotelId}/groups")
def list_groups(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM GROUP_BLOCKS WHERE RESORT_ID = :hotel"
    params = {"hotel": hotelId}
    if status:
        sql += " AND STATUS = :st"
        params["st"] = status
    sql += " ORDER BY ARRIVAL_DATE DESC"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        data = rows_to_dicts(cur)
    return paginated(data, offset, limit)

# --- STATISTICS ---
@app.get("/api/v1/hotels/{hotelId}/statistics")
def get_statistics(
    hotelId: str,
    x_api_key: str = Header(alias="x-api-key"),
    businessDate: Optional[str] = None,
):
    auth(x_api_key)
    bdate = businessDate or date.today().isoformat()
    with get_conn() as conn:
        cur = conn.cursor()
        # Total rooms
        cur.execute("SELECT COUNT(*) FROM ROOMS WHERE RESORT_ID = :h", {"h": hotelId})
        total_rooms = cur.fetchone()[0]
        # Occupied (checked in)
        cur.execute("""SELECT COUNT(DISTINCT ROOM_NUMBER) FROM RESERVATIONS
                       WHERE RESORT_ID = :h AND RESV_STATUS = 'CHECKED_IN'
                       AND ARRIVAL_DATE <= TO_DATE(:d, 'YYYY-MM-DD') AND DEPARTURE_DATE > TO_DATE(:d, 'YYYY-MM-DD')""",
                    {"h": hotelId, "d": bdate})
        occupied = cur.fetchone()[0]
        # Arrivals
        cur.execute("""SELECT COUNT(*) FROM RESERVATIONS
                       WHERE RESORT_ID = :h AND ARRIVAL_DATE = TO_DATE(:d, 'YYYY-MM-DD') AND RESV_STATUS IN ('RESERVED','CHECKED_IN')""",
                    {"h": hotelId, "d": bdate})
        arrivals = cur.fetchone()[0]
        # Departures
        cur.execute("""SELECT COUNT(*) FROM RESERVATIONS
                       WHERE RESORT_ID = :h AND DEPARTURE_DATE = TO_DATE(:d, 'YYYY-MM-DD') AND RESV_STATUS IN ('CHECKED_IN','CHECKED_OUT')""",
                    {"h": hotelId, "d": bdate})
        departures = cur.fetchone()[0]
        # Revenue & ADR
        cur.execute("""SELECT NVL(SUM(rdd.RATE_AMOUNT),0), COUNT(*)
                       FROM RESERVATION_DAILY_DETAILS rdd
                       JOIN RESERVATIONS r ON rdd.RESV_ID = r.RESV_ID
                       WHERE r.RESORT_ID = :h AND rdd.RESERVATION_DATE = TO_DATE(:d, 'YYYY-MM-DD')""",
                    {"h": hotelId, "d": bdate})
        row = cur.fetchone()
        room_revenue = float(row[0])
        sold_rooms = row[1] if row[1] else 0
        # Total revenue from folio
        cur.execute("""SELECT NVL(SUM(AMOUNT),0) FROM FOLIO_TRANSACTIONS
                       WHERE RESORT_ID = :h AND TRX_DATE = TO_DATE(:d, 'YYYY-MM-DD')""",
                    {"h": hotelId, "d": bdate})
        total_revenue = float(cur.fetchone()[0])

    occupancy_pct = round((occupied / total_rooms * 100), 2) if total_rooms else 0
    adr = round(room_revenue / sold_rooms, 2) if sold_rooms else 0
    revpar = round(room_revenue / total_rooms, 2) if total_rooms else 0

    return {
        "businessDate": bdate,
        "hotelId": hotelId,
        "totalRooms": total_rooms,
        "roomsOccupied": occupied,
        "roomsAvailable": total_rooms - occupied,
        "occupancyPercentage": occupancy_pct,
        "arrivals": arrivals,
        "departures": departures,
        "adr": adr,
        "revPar": revpar,
        "roomRevenue": room_revenue,
        "totalRevenue": total_revenue,
    }

@app.get("/health")
def health():
    return {"status": "ok"}
