"""Unifocus (Knowcross) Hotel Operations Mock API"""
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, date
from typing import Optional
import sqlite3, json, os

DB_PATH = "/opt/unifocus-api/unifocus.db"
API_KEY = "unifocus-demo-2026"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def to_camel(s):
    parts = s.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

def rows_to_dicts(rows):
    return [{to_camel(k): v for k, v in dict(r).items()} for r in rows]

def paginated(data, offset, limit):
    return {"count": len(data), "offset": offset, "limit": limit, "hasMore": offset + limit < len(data), "results": data[offset:offset+limit]}

def auth(key):
    if key != API_KEY:
        raise HTTPException(401, "Invalid API key")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY, name TEXT, department TEXT, role TEXT, phone TEXT, status TEXT DEFAULT 'ACTIVE'
    );
    CREATE TABLE IF NOT EXISTS work_orders (
        id INTEGER PRIMARY KEY, order_number TEXT UNIQUE, title TEXT, description TEXT,
        priority TEXT, status TEXT, department TEXT, room_number TEXT, location TEXT,
        guest_name TEXT, reported_by TEXT, assigned_to INTEGER,
        created_at TEXT, updated_at TEXT, completed_at TEXT, estimated_minutes INTEGER,
        FOREIGN KEY(assigned_to) REFERENCES staff(id)
    );
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY, ticket_number TEXT UNIQUE, guest_name TEXT, room_number TEXT,
        category TEXT, description TEXT, severity TEXT, status TEXT,
        reported_at TEXT, responded_at TEXT, resolved_at TEXT, response_minutes INTEGER,
        assigned_to INTEGER, resolution_notes TEXT,
        FOREIGN KEY(assigned_to) REFERENCES staff(id)
    );
    CREATE TABLE IF NOT EXISTS housekeeping (
        id INTEGER PRIMARY KEY, task_number TEXT UNIQUE, room_number TEXT, floor INTEGER,
        task_type TEXT, status TEXT, assigned_to INTEGER, priority TEXT,
        scheduled_at TEXT, started_at TEXT, completed_at TEXT, duration_minutes INTEGER, notes TEXT,
        FOREIGN KEY(assigned_to) REFERENCES staff(id)
    );
    CREATE TABLE IF NOT EXISTS preventive_maintenance (
        id INTEGER PRIMARY KEY, pm_number TEXT UNIQUE, title TEXT, description TEXT,
        frequency TEXT, location TEXT, department TEXT, assigned_to INTEGER,
        last_completed TEXT, next_due TEXT, status TEXT,
        FOREIGN KEY(assigned_to) REFERENCES staff(id)
    );
    """)

    # Check if data exists
    if c.execute("SELECT COUNT(*) FROM staff").fetchone()[0] > 0:
        conn.close()
        return

    # Staff
    staff = [
        (1,'Jean-Pierre Moreau','Maintenance','Chief Engineer','0590-111-001','ACTIVE'),
        (2,'Marc Antoine','Maintenance','Maintenance Tech','0590-111-002','ACTIVE'),
        (3,'Lucas Bertrand','Maintenance','Maintenance Tech','0590-111-003','ACTIVE'),
        (4,'Philippe Garnier','Maintenance','Pool Technician','0590-111-004','ACTIVE'),
        (5,'Marie Dubois','Housekeeping','Executive Housekeeper','0590-112-001','ACTIVE'),
        (6,'Camille Petit','Housekeeping','Floor Supervisor','0590-112-002','ACTIVE'),
        (7,'Nathalie Roux','Housekeeping','Room Attendant','0590-112-003','ACTIVE'),
        (8,'Sylvie Bernard','Housekeeping','Room Attendant','0590-112-004','ACTIVE'),
        (9,'Isabelle Martin','Housekeeping','Room Attendant','0590-112-005','ACTIVE'),
        (10,'Claire Lefevre','Housekeeping','Turndown Attendant','0590-112-006','ACTIVE'),
        (11,'Thomas Duval','Engineering','Supervisor','0590-113-001','ACTIVE'),
        (12,'Antoine Blanc','Engineering','Electrician','0590-113-002','ACTIVE'),
    ]
    c.executemany("INSERT INTO staff VALUES (?,?,?,?,?,?)", staff)

    # Work orders (25+)
    wo = [
        (1,'WO-2026-001','AC not cooling - Villa 4','Guest Richardson reports AC unit in master bedroom not reaching set temperature. Unit blowing warm air.','CRITICAL','IN_PROGRESS','Maintenance','V04','Villa 4 - Master Bedroom','James Richardson','Front Desk',2,'2026-02-14T09:30:00','2026-02-14T10:15:00',None,120),
        (2,'WO-2026-002','Bathroom faucet leak - Room 501','Slow drip from bathroom sink faucet in Suite 501.','MEDIUM','OPEN','Maintenance','501','Suite 501 - Bathroom','Sophie Laurent','Housekeeping',3,'2026-02-14T11:00:00','2026-02-14T11:00:00',None,60),
        (3,'WO-2026-003','Pool pump pressure low','Main infinity pool pump showing below-normal pressure readings. Filtration may be affected.','HIGH','IN_PROGRESS','Maintenance','POOL','Main Infinity Pool',None,'Engineering',4,'2026-02-13T07:00:00','2026-02-13T08:00:00',None,180),
        (4,'WO-2026-004','TV no signal - Room 301','Smart TV in Room 301 showing no signal on HDMI inputs. Streaming apps working.','LOW','OPEN','Maintenance','301','Room 301','Yuki Tanaka','Guest',2,'2026-02-15T08:45:00','2026-02-15T08:45:00',None,45),
        (5,'WO-2026-005','Minibar restock - Room 601','Full minibar restock needed. Guest consumed all items.','LOW','COMPLETED','Housekeeping','601','Penthouse 601','Leonardo Ferragamo','Room Service',7,'2026-02-14T16:00:00','2026-02-14T16:30:00','2026-02-14T17:00:00',30),
        (6,'WO-2026-006','Exterior lighting - Garden path','Three pathway lights along garden path to beach not functioning.','MEDIUM','OPEN','Engineering','EXT','Garden Path to Beach',None,'Security',12,'2026-02-14T20:00:00','2026-02-14T20:00:00',None,90),
        (7,'WO-2026-007','Jacuzzi jets malfunction - Villa 5','Two jets in private jacuzzi not functioning. Water feature also intermittent.','HIGH','IN_PROGRESS','Maintenance','V05','Villa 5 - Private Jacuzzi','Mohammed Al-Rashid','Butler',3,'2026-02-14T14:00:00','2026-02-14T14:30:00',None,120),
        (8,'WO-2026-008','Replace showerhead - Room 302','Guest requests rainfall showerhead replacement - current one has low pressure.','LOW','COMPLETED','Maintenance','302','Room 302 - Bathroom','Isabel Santos','Guest',2,'2026-02-14T10:00:00','2026-02-14T10:30:00','2026-02-14T11:30:00',45),
        (9,'WO-2026-009','AC filter replacement - Floor 2','Scheduled AC filter replacement for all Floor 2 rooms during low occupancy.','MEDIUM','COMPLETED','Maintenance','F2','Floor 2 - All Rooms',None,'Engineering',2,'2026-02-12T08:00:00','2026-02-12T08:00:00','2026-02-12T14:00:00',360),
        (10,'WO-2026-010','Safe malfunction - Room 401','In-room safe not accepting new code. Electronic keypad unresponsive.','HIGH','OPEN','Maintenance','401','Room 401','Alexander Wolff','Front Desk',None,'2026-02-15T10:00:00','2026-02-15T10:00:00',None,30),
        (11,'WO-2026-011','Ceiling fan noise - Room 502','Ceiling fan making clicking noise at all speeds.','MEDIUM','COMPLETED','Maintenance','502','Suite 502','Anna Petrov','Guest',3,'2026-02-13T15:00:00','2026-02-13T15:30:00','2026-02-13T16:30:00',60),
        (12,'WO-2026-012','Beach cabana repair','Canvas tear on beach cabana #3. Needs patching or replacement.','LOW','OPEN','Maintenance','BCH','Beach Cabana #3',None,'Beach Staff',None,'2026-02-15T07:00:00','2026-02-15T07:00:00',None,120),
        (13,'WO-2026-013','Toilet running - Room 103','Toilet in Room 103 continuously running. Flapper valve likely needs replacement.','MEDIUM','COMPLETED','Maintenance','103','Room 103 - Bathroom',None,'Housekeeping',3,'2026-02-13T09:00:00','2026-02-13T09:30:00','2026-02-13T10:30:00',45),
        (14,'WO-2026-014','Replace minibar fridge - Room 203','Minibar fridge not maintaining temperature. Compressor may be failing.','MEDIUM','IN_PROGRESS','Maintenance','203','Room 203',None,'Housekeeping',2,'2026-02-14T12:00:00','2026-02-14T13:00:00',None,90),
        (15,'WO-2026-015','Spa sauna heater issue','Sauna not reaching proper temperature. Heating element may need replacement.','HIGH','OPEN','Engineering','SPA','Spa - Sauna Room',None,'Spa Manager',12,'2026-02-15T06:00:00','2026-02-15T06:00:00',None,180),
        (16,'WO-2026-016','Door lock battery - Room 204','Electronic door lock showing low battery indicator.','LOW','COMPLETED','Maintenance','204','Room 204',None,'Front Desk',2,'2026-02-14T08:00:00','2026-02-14T08:15:00','2026-02-14T08:30:00',15),
        (17,'WO-2026-017','Plumbing - Kitchen drain slow','Main kitchen drain running slow. Possible grease buildup.','HIGH','COMPLETED','Maintenance','KIT','Main Kitchen',None,'Chef',3,'2026-02-12T22:00:00','2026-02-12T22:30:00','2026-02-13T01:00:00',150),
        (18,'WO-2026-018','Repaint balcony railing - Room 303','Balcony railing showing rust spots and paint peeling.','LOW','OPEN','Maintenance','303','Room 303 - Balcony',None,'Housekeeping',None,'2026-02-15T09:00:00','2026-02-15T09:00:00',None,240),
        (19,'WO-2026-019','WiFi AP replacement - Pool area','Wireless access point at pool area showing intermittent connectivity.','HIGH','IN_PROGRESS','Engineering','POOL','Pool Deck',None,'IT',12,'2026-02-15T08:00:00','2026-02-15T08:30:00',None,60),
        (20,'WO-2026-020','Broken towel rack - Room 603','Wall-mounted towel rack pulled from wall. Needs re-anchoring.','MEDIUM','COMPLETED','Maintenance','603','Penthouse 603 - Bathroom','David Chen','Housekeeping',2,'2026-02-14T11:00:00','2026-02-14T11:30:00','2026-02-14T12:30:00',45),
        (21,'WO-2026-021','Generator monthly test','Monthly generator load test and inspection.','MEDIUM','COMPLETED','Engineering','GEN','Generator Room',None,'Engineering',11,'2026-02-10T06:00:00','2026-02-10T06:00:00','2026-02-10T08:00:00',120),
        (22,'WO-2026-022','Replace bathroom exhaust fan - V01','Bathroom exhaust fan in Villa 1 not functioning.','MEDIUM','OPEN','Maintenance','V01','Villa 1 - Bathroom','Carlos Mendoza','Guest',None,'2026-02-15T11:00:00','2026-02-15T11:00:00',None,60),
        (23,'WO-2026-023','Ice machine maintenance - Floor 4','Ice machine on 4th floor producing less ice. Needs descaling.','LOW','OPEN','Maintenance','F4','Floor 4 - Service Area',None,'F&B',None,'2026-02-15T07:30:00','2026-02-15T07:30:00',None,90),
        (24,'WO-2026-024','Irrigation system leak - Garden','Irrigation pipe leaking near main garden. Water pooling on pathway.','MEDIUM','IN_PROGRESS','Maintenance','EXT','Main Garden',None,'Grounds',4,'2026-02-15T06:30:00','2026-02-15T07:00:00',None,120),
        (25,'WO-2026-025','Elevator door sensor - Bldg A','Elevator door hesitating on close. Sensor may need alignment.','HIGH','OPEN','Engineering','ELEV','Building A - Elevator',None,'Front Desk',None,'2026-02-15T09:30:00','2026-02-15T09:30:00',None,90),
        (26,'WO-2026-026','Minibar restock - Room 502','Restock water and champagne in Suite 502.','LOW','COMPLETED','Housekeeping','502','Suite 502','Anna Petrov','Butler',8,'2026-02-14T18:00:00','2026-02-14T18:00:00','2026-02-14T18:30:00',20),
    ]
    c.executemany("INSERT INTO work_orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", wo)

    # Complaints
    complaints = [
        (1,'CMP-2026-001','Anna Petrov','502','Noise','Loud music from adjacent room late at night. Guest unable to sleep.','HIGH','RESOLVED','2026-02-13T23:30:00','2026-02-13T23:45:00','2026-02-14T00:15:00',15,6,'Security addressed noise. Complimentary breakfast offered.'),
        (2,'CMP-2026-002','Emma Thompson','101','Cleanliness','Found hair in bathtub upon check-in. Room not properly cleaned.','MEDIUM','RESOLVED','2026-02-13T15:00:00','2026-02-13T15:10:00','2026-02-13T15:45:00',10,5,'Room re-cleaned immediately. Complimentary amenity basket delivered.'),
        (3,'CMP-2026-003','Sophie Laurent','501','Temperature','Room temperature fluctuating. AC turning off intermittently.','MEDIUM','IN_PROGRESS','2026-02-14T22:00:00','2026-02-14T22:15:00',None,15,2,'Maintenance dispatched. Portable AC unit provided as interim.'),
        (4,'CMP-2026-004','David Chen','603','Service Delay','Room service order took 55 minutes (promised 30). Food arrived lukewarm.','HIGH','RESOLVED','2026-02-14T20:30:00','2026-02-14T20:35:00','2026-02-14T21:00:00',5,6,'Order re-prepared and delivered. Meal comped. F&B manager apologized.'),
        (5,'CMP-2026-005','James Richardson','V04','Wrong Order','Butler delivered wrong wine. Ordered 2015 Pétrus, received 2018 vintage.','LOW','RESOLVED','2026-02-14T19:00:00','2026-02-14T19:05:00','2026-02-14T19:30:00',5,6,'Correct bottle sourced and delivered. Sommelier visit arranged.'),
        (6,'CMP-2026-006','Yuki Tanaka','301','Maintenance','TV remote not working and no replacement available on floor.','LOW','RESOLVED','2026-02-14T21:00:00','2026-02-14T21:10:00','2026-02-14T21:25:00',10,2,'New remote delivered. TV system checked.'),
        (7,'CMP-2026-007','Mohammed Al-Rashid','V05','Service','Security escort not arranged for beach dinner as requested.','CRITICAL','RESOLVED','2026-02-13T18:00:00','2026-02-13T18:05:00','2026-02-13T18:30:00',5,6,'Security team immediately dispatched. Personal apology from GM.'),
        (8,'CMP-2026-008','Isabel Santos','302','Cleanliness','Minibar items past expiration date. Chips and crackers expired Jan 2026.','MEDIUM','RESOLVED','2026-02-14T16:00:00','2026-02-14T16:15:00','2026-02-14T16:45:00',15,5,'All minibar items replaced. Full floor audit initiated.'),
        (9,'CMP-2026-009','Carlos Mendoza','V01','Noise','Construction noise from nearby property starting at 7 AM.','MEDIUM','IN_PROGRESS','2026-02-15T07:30:00','2026-02-15T07:45:00',None,15,6,'Contacted neighboring property. Noise barriers being arranged.'),
        (10,'CMP-2026-010','Leonardo Ferragamo','601','Temperature','Penthouse terrace misting system not working during afternoon heat.','MEDIUM','OPEN','2026-02-15T14:00:00','2026-02-15T14:00:00',None,None,None,'Reported to maintenance. Awaiting dispatch.'),
        (11,'CMP-2026-011','Alexander Wolff','401','Service Delay','Requested extra pillows 2 hours ago, still not delivered.','HIGH','OPEN','2026-02-15T16:00:00',None,None,None,None,'Escalated to housekeeping supervisor.'),
    ]
    c.executemany("INSERT INTO complaints VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", complaints)

    # Housekeeping
    hk = [
        (1,'HK-2026-001','V04','0','STAYOVER','COMPLETED',7,'HIGH','2026-02-15T08:00:00','2026-02-15T08:30:00','2026-02-15T10:00:00',90,'VIP villa - extra attention. Fresh flowers, premium amenities restocked.'),
        (2,'HK-2026-002','501','5','STAYOVER','COMPLETED',8,'HIGH','2026-02-15T08:00:00','2026-02-15T08:15:00','2026-02-15T09:30:00',75,'Suite stayover. Guest requested late service after 8AM.'),
        (3,'HK-2026-003','V05','0','STAYOVER','IN_PROGRESS',7,'CRITICAL','2026-02-15T09:00:00','2026-02-15T09:15:00',None,None,'VVIP villa. Security clearance required. 3-person team assigned.'),
        (4,'HK-2026-004','601','6','STAYOVER','COMPLETED',9,'HIGH','2026-02-15T08:00:00','2026-02-15T08:00:00','2026-02-15T09:15:00',75,'Penthouse service. Guest out for morning.'),
        (5,'HK-2026-005','301','3','STAYOVER','COMPLETED',8,'MEDIUM','2026-02-15T09:00:00','2026-02-15T09:45:00','2026-02-15T10:30:00',45,'Standard stayover.'),
        (6,'HK-2026-006','302','3','STAYOVER','SCHEDULED',9,'MEDIUM','2026-02-15T11:00:00',None,None,None,'Awaiting guest departure for cleaning window.'),
        (7,'HK-2026-007','603','6','STAYOVER','COMPLETED',7,'HIGH','2026-02-15T08:30:00','2026-02-15T08:30:00','2026-02-15T09:45:00',75,'Penthouse stayover.'),
        (8,'HK-2026-008','101','1','STAYOVER','SCHEDULED',9,'MEDIUM','2026-02-15T11:00:00',None,None,None,'Standard room stayover.'),
        (9,'HK-2026-009','V01','0','STAYOVER','SCHEDULED',8,'HIGH','2026-02-15T10:00:00',None,None,None,'Villa stayover. Guest requested 10AM service.'),
        (10,'HK-2026-010','502','5','DEPARTURE','SCHEDULED',7,'HIGH','2026-02-16T08:00:00',None,None,None,'Departure clean. Guest Petrov checking out Feb 16.'),
        (11,'HK-2026-011','V04','0','TURNDOWN','SCHEDULED',10,'HIGH','2026-02-15T18:00:00',None,None,None,'VIP turndown. Premium chocolates, rose petals per preference.'),
        (12,'HK-2026-012','V05','0','TURNDOWN','SCHEDULED',10,'CRITICAL','2026-02-15T18:30:00',None,None,None,'VVIP turndown. Coordinate with security for access.'),
        (13,'HK-2026-013','601','6','TURNDOWN','SCHEDULED',10,'HIGH','2026-02-15T18:00:00',None,None,None,'Penthouse turndown service.'),
        (14,'HK-2026-014','104','1','DEEP_CLEAN','COMPLETED',7,'MEDIUM','2026-02-13T10:00:00','2026-02-13T10:00:00','2026-02-13T13:00:00',180,'Post-checkout deep clean. Room 104 was checked out by Thompson.'),
        (15,'HK-2026-015','201','2','DEEP_CLEAN','SCHEDULED',8,'LOW','2026-02-16T08:00:00',None,None,None,'Vacant room deep clean. Quarterly schedule.'),
        (16,'HK-2026-016','401','4','STAYOVER','SCHEDULED',9,'MEDIUM','2026-02-15T12:00:00',None,None,None,'New arrival stayover - Wolff checking in today.'),
        (17,'HK-2026-017','V02','0','DEPARTURE','SCHEDULED',7,'HIGH','2026-02-15T10:00:00',None,None,None,'Prepare for Al-Sayed arrival. Full villa prep with welcome amenities.'),
    ]
    c.executemany("INSERT INTO housekeeping VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", hk)

    # Preventive maintenance
    pm = [
        (1,'PM-2026-001','Elevator Annual Inspection','Full safety inspection of all elevators per regulatory requirements.','ANNUAL','Building A & B Elevators','Engineering',11,'2025-06-15','2026-06-15','SCHEDULED'),
        (2,'PM-2026-002','Pool Chemical Balance Check','Daily pool water chemistry testing and chemical adjustment.','DAILY','Main Pool & Spa Pool','Maintenance',4,'2026-02-15','2026-02-16','COMPLETED'),
        (3,'PM-2026-003','Fire Suppression System Test','Quarterly fire alarm and sprinkler system inspection.','QUARTERLY','All Buildings','Engineering',11,'2025-12-01','2026-03-01','SCHEDULED'),
        (4,'PM-2026-004','Generator Load Test','Monthly backup generator full-load test and maintenance.','MONTHLY','Generator Room','Engineering',11,'2026-02-10','2026-03-10','COMPLETED'),
        (5,'PM-2026-005','HVAC Filter Replacement','Quarterly replacement of all HVAC filters property-wide.','QUARTERLY','All Rooms & Common Areas','Maintenance',2,'2026-02-12','2026-05-12','IN_PROGRESS'),
        (6,'PM-2026-006','Kitchen Hood Cleaning','Monthly deep cleaning of all kitchen exhaust hoods.','MONTHLY','Main Kitchen & Beach Restaurant','Maintenance',3,'2026-01-20','2026-02-20','SCHEDULED'),
        (7,'PM-2026-007','Landscape Irrigation Audit','Monthly inspection of all irrigation zones and sprinkler heads.','MONTHLY','Grounds','Maintenance',4,'2026-01-15','2026-02-15','OVERDUE'),
    ]
    c.executemany("INSERT INTO preventive_maintenance VALUES (?,?,?,?,?,?,?,?,?,?,?)", pm)

    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Unifocus Operations API", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "unifocus-api", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1/properties/{propertyId}/work-orders")
def list_work_orders(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    department: Optional[str] = None,
    room: Optional[str] = None,
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT wo.*, s.name as assigned_to_name FROM work_orders wo LEFT JOIN staff s ON wo.assigned_to = s.id WHERE 1=1"
    params = []
    if status:
        sql += " AND wo.status = ?"; params.append(status)
    if priority:
        sql += " AND wo.priority = ?"; params.append(priority)
    if department:
        sql += " AND wo.department = ?"; params.append(department)
    if room:
        sql += " AND wo.room_number = ?"; params.append(room)
    if dateFrom:
        sql += " AND wo.created_at >= ?"; params.append(dateFrom)
    if dateTo:
        sql += " AND wo.created_at <= ?"; params.append(dateTo)
    sql += " ORDER BY wo.created_at DESC"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    data = rows_to_dicts(rows)
    return paginated(data, offset, limit)

@app.get("/api/v1/properties/{propertyId}/work-orders/{orderId}")
def get_work_order(propertyId: str, orderId: str, x_api_key: str = Header(alias="x-api-key")):
    auth(x_api_key)
    db = get_db()
    row = db.execute("SELECT wo.*, s.name as assigned_to_name FROM work_orders wo LEFT JOIN staff s ON wo.assigned_to = s.id WHERE wo.order_number = ? OR wo.id = ?", (orderId, orderId)).fetchone()
    db.close()
    if not row:
        raise HTTPException(404, "Work order not found")
    return {to_camel(k): v for k, v in dict(row).items()}

@app.get("/api/v1/properties/{propertyId}/complaints")
def list_complaints(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT c.*, s.name as assigned_to_name FROM complaints c LEFT JOIN staff s ON c.assigned_to = s.id WHERE 1=1"
    params = []
    if status:
        sql += " AND c.status = ?"; params.append(status)
    if severity:
        sql += " AND c.severity = ?"; params.append(severity)
    if dateFrom:
        sql += " AND c.reported_at >= ?"; params.append(dateFrom)
    if dateTo:
        sql += " AND c.reported_at <= ?"; params.append(dateTo)
    sql += " ORDER BY c.reported_at DESC"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/housekeeping")
def list_housekeeping(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    status: Optional[str] = None,
    floor: Optional[int] = None,
    date: Optional[str] = None,
    taskType: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT h.*, s.name as assigned_to_name FROM housekeeping h LEFT JOIN staff s ON h.assigned_to = s.id WHERE 1=1"
    params = []
    if status:
        sql += " AND h.status = ?"; params.append(status)
    if floor is not None:
        sql += " AND h.floor = ?"; params.append(floor)
    if date:
        sql += " AND h.scheduled_at LIKE ?"; params.append(f"{date}%")
    if taskType:
        sql += " AND h.task_type = ?"; params.append(taskType)
    sql += " ORDER BY h.scheduled_at DESC"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/staff")
def list_staff(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    department: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM staff WHERE 1=1"
    params = []
    if department:
        sql += " AND department = ?"; params.append(department)
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/preventive-maintenance")
def list_pm(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT pm.*, s.name as assigned_to_name FROM preventive_maintenance pm LEFT JOIN staff s ON pm.assigned_to = s.id WHERE 1=1"
    params = []
    if status:
        sql += " AND pm.status = ?"; params.append(status)
    sql += " ORDER BY pm.next_due"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/statistics")
def statistics(propertyId: str, x_api_key: str = Header(alias="x-api-key")):
    auth(x_api_key)
    db = get_db()
    open_wo = db.execute("SELECT COUNT(*) FROM work_orders WHERE status IN ('OPEN','IN_PROGRESS')").fetchone()[0]
    total_wo = db.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0]
    completed_wo = db.execute("SELECT COUNT(*) FROM work_orders WHERE status = 'COMPLETED'").fetchone()[0]
    open_complaints = db.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('OPEN','IN_PROGRESS')").fetchone()[0]
    resolved_complaints = db.execute("SELECT COUNT(*) FROM complaints WHERE status = 'RESOLVED'").fetchone()[0]
    avg_response = db.execute("SELECT AVG(response_minutes) FROM complaints WHERE response_minutes IS NOT NULL").fetchone()[0]
    hk_completed = db.execute("SELECT COUNT(*) FROM housekeeping WHERE status = 'COMPLETED'").fetchone()[0]
    hk_pending = db.execute("SELECT COUNT(*) FROM housekeeping WHERE status IN ('SCHEDULED','IN_PROGRESS')").fetchone()[0]
    overdue_pm = db.execute("SELECT COUNT(*) FROM preventive_maintenance WHERE status = 'OVERDUE'").fetchone()[0]
    db.close()
    return {
        "workOrders": {"open": open_wo, "total": total_wo, "completed": completed_wo},
        "complaints": {"open": open_complaints, "resolved": resolved_complaints, "avgResponseMinutes": round(avg_response or 0, 1)},
        "housekeeping": {"completed": hk_completed, "pending": hk_pending},
        "preventiveMaintenance": {"overdue": overdue_pm},
        "slaCompliance": round((resolved_complaints / max(resolved_complaints + open_complaints, 1)) * 100, 1),
        "generatedAt": datetime.utcnow().isoformat()
    }
