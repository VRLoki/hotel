"""Concierge Organizer Mock API"""
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import sqlite3, os

DB_PATH = "/opt/concierge-api/concierge.db"
API_KEY = "concierge-demo-2026"

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
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY, request_number TEXT UNIQUE, guest_name TEXT, room_number TEXT,
        type TEXT, description TEXT, status TEXT, priority TEXT,
        created_at TEXT, confirmed_at TEXT, completed_at TEXT, notes TEXT, cost_estimate REAL
    );
    CREATE TABLE IF NOT EXISTS transportation (
        id INTEGER PRIMARY KEY, transport_number TEXT UNIQUE, guest_name TEXT, room_number TEXT,
        type TEXT, pickup_location TEXT, dropoff_location TEXT,
        scheduled_at TEXT, vehicle TEXT, driver TEXT, status TEXT, pax INTEGER, notes TEXT, cost REAL
    );
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY, name TEXT, category TEXT, provider TEXT, description TEXT,
        duration_hours REAL, price_per_person REAL, max_capacity INTEGER, location TEXT,
        available_days TEXT, start_times TEXT
    );
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY, name TEXT, category TEXT, cuisine_or_type TEXT, description TEXT,
        address TEXT, phone TEXT, price_range TEXT, rating REAL, distance_km REAL,
        reservation_required INTEGER, notes TEXT
    );
    """)

    if c.execute("SELECT COUNT(*) FROM requests").fetchone()[0] > 0:
        conn.close()
        return

    # Guest requests (30+)
    reqs = [
        (1,'REQ-2026-001','James Richardson','V04','restaurant','Dinner reservation at Bonito for 4 guests, Feb 15 at 8PM. Ocean view table preferred.','CONFIRMED','HIGH','2026-02-14T10:00:00','2026-02-14T10:30:00',None,'Table 12 confirmed - ocean terrace. Car arranged for 7:45PM.',None),
        (2,'REQ-2026-002','James Richardson','V04','private_jet','Private jet transfer from Teterboro (TEB) to SBH. Gulfstream G650 or equivalent. Feb 10 departure.','COMPLETED','CRITICAL','2026-02-05T14:00:00','2026-02-05T16:00:00','2026-02-10T15:00:00','NetJets confirmed. G650 tail N650RR. Customs pre-cleared.',95000.00),
        (3,'REQ-2026-003','Mohammed Al-Rashid','V05','yacht','Weekly yacht charter. 40m+ with full crew. Feb 14-21. Security berth required.','CONFIRMED','CRITICAL','2026-02-08T09:00:00','2026-02-09T11:00:00',None,'M/Y Serenity (42m Benetti) confirmed. Crew of 8. Security vessel arranged alongside. Berth at Gustavia port.',45000.00),
        (4,'REQ-2026-004','Mohammed Al-Rashid','V05','security','Additional security detail coordination for beach dinner Feb 15. 2 close protection officers.','CONFIRMED','CRITICAL','2026-02-14T08:00:00','2026-02-14T09:00:00',None,'Island Security SBH confirmed 2 CPOs. Briefed on principal protocols.',2800.00),
        (5,'REQ-2026-005','Sophie Laurent','501','restaurant','Lunch at Eden Rock restaurant for 2, Feb 15. Vegetarian menu preference.','CONFIRMED','MEDIUM','2026-02-14T18:00:00','2026-02-14T18:15:00',None,'Table for 2 at 12:30PM. Chef notified of vegetarian preference.',None),
        (6,'REQ-2026-006','Leonardo Ferragamo','601','yacht','Day charter for Feb 16. Sailing yacht preferred. 6 guests. Lunch on board. Route: Colombier, Gouverneur.','CONFIRMED','HIGH','2026-02-14T09:00:00','2026-02-14T11:00:00',None,'S/Y Luna Rossa (24m) confirmed. Depart 10AM Gustavia. Lunch by onboard chef. Champagne & wine stocked.',8500.00),
        (7,'REQ-2026-007','Leonardo Ferragamo','601','restaurant','Dinner at Le Sereno restaurant for 6 on Feb 16 evening. Post-sailing.','CONFIRMED','HIGH','2026-02-14T09:30:00','2026-02-14T12:00:00',None,'Table for 6 at 8:30PM confirmed. Sommelier notified for Italian wine selection.',None),
        (8,'REQ-2026-008','Emma Thompson','101','activity','Scuba diving intro course for 2, any day Feb 14-16.','CONFIRMED','MEDIUM','2026-02-13T16:00:00','2026-02-13T17:00:00',None,'Plongée Caraïbes - Discover Scuba for 2 on Feb 15 at 9AM. Pickup at hotel 8:30AM.',350.00),
        (9,'REQ-2026-009','Anna Petrov','502','shopping','Personal shopping assistant for afternoon in Gustavia. Focus on luxury boutiques.','COMPLETED','MEDIUM','2026-02-14T08:00:00','2026-02-14T09:00:00','2026-02-14T17:00:00','Arranged Isabelle (personal shopper). Visited Hermès, Louis Vuitton, Chopard. Car service provided.',500.00),
        (10,'REQ-2026-010','Yuki Tanaka','301','activity','Sunset sailing cruise for 2 on Feb 15.','CONFIRMED','MEDIUM','2026-02-14T11:00:00','2026-02-14T12:00:00',None,'Jicky Marine sunset cruise. Depart 4:30PM from Gustavia. Champagne included.',280.00),
        (11,'REQ-2026-011','David Chen','603','private_chef','Private chef dinner in penthouse for 4 on Feb 16. Asian fusion menu.','CONFIRMED','HIGH','2026-02-14T15:00:00','2026-02-14T16:30:00',None,'Chef Kenji Yamamoto confirmed. 7-course tasting menu. Arrives 5PM for prep. Wine pairing included.',3200.00),
        (12,'REQ-2026-012','Carlos Mendoza','V01','activity','Deep sea fishing charter for Feb 16. Full day. 4 guests.','CONFIRMED','MEDIUM','2026-02-14T10:00:00','2026-02-14T11:00:00',None,'Nautica FWI - 38ft Bertram. Captain Jean-Luc. Depart 6:30AM. Lunch & drinks included.',2200.00),
        (13,'REQ-2026-013','Isabel Santos','302','spa','Couples massage at Spa - Feb 15 afternoon.','COMPLETED','MEDIUM','2026-02-14T09:00:00','2026-02-14T09:15:00','2026-02-15T16:00:00','3PM slot confirmed at Eden Rock Spa. 90-min hot stone massage for 2.',650.00),
        (14,'REQ-2026-014','James Richardson','V04','flowers','Fresh flower arrangement for villa daily. White orchids and tropical mix.','IN_PROGRESS','MEDIUM','2026-02-10T08:00:00','2026-02-10T09:00:00',None,'Fleuriste Gustavia - daily delivery at 7AM. Premium arrangement with white orchids, bird of paradise, frangipani.',180.00),
        (15,'REQ-2026-015','Mohammed Al-Rashid','V05','car_rental','Luxury SUV rental for duration of stay. Range Rover or G-Wagon with driver on standby.','CONFIRMED','HIGH','2026-02-09T10:00:00','2026-02-09T14:00:00',None,'Top Loc SBH - Mercedes G63 AMG. Driver Antoine on 24h standby. Parked at villa.',850.00),
        (16,'REQ-2026-016','Sophie Laurent','501','activity','Island tour - half day. Photography focused. Feb 16.','PENDING','MEDIUM','2026-02-15T09:00:00',None,None,'Searching for English-speaking photography guide.',250.00),
        (17,'REQ-2026-017','Alexander Wolff','401','airport_transfer','Airport pickup SBH Feb 15. Arriving 2PM on private charter from SXM.','CONFIRMED','HIGH','2026-02-14T20:00:00','2026-02-14T20:30:00',None,'Premium SUV at airport. Driver Marc. Welcome package in car.',150.00),
        (18,'REQ-2026-018','Fatima Al-Sayed','V02','airport_transfer','Airport pickup SBH Feb 15. Party of 6 arriving 4PM from Riyadh via SXM.','CONFIRMED','HIGH','2026-02-14T21:00:00','2026-02-14T21:30:00',None,'2x premium SUVs arranged. Arabic-speaking greeter. Villa pre-stocked with halal amenities.',300.00),
        (19,'REQ-2026-019','Anna Petrov','502','restaurant','Reservation at Maya\'s for 2, Feb 15 lunch.','CONFIRMED','MEDIUM','2026-02-15T08:00:00','2026-02-15T08:30:00',None,'Table for 2 at 12PM. Beachside seating.',None),
        (20,'REQ-2026-020','David Chen','603','activity','Jet ski rental for 2 hours on Feb 15 afternoon.','CONFIRMED','LOW','2026-02-15T07:00:00','2026-02-15T07:30:00',None,'Carib Waterplay - 2 jet skis at 2PM from St Jean beach. Helmets and safety briefing included.',300.00),
        (21,'REQ-2026-021','Leonardo Ferragamo','601','babysitting','Babysitter needed Feb 16 evening 7PM-midnight for 2 children (ages 4, 7).','CONFIRMED','HIGH','2026-02-15T10:00:00','2026-02-15T11:00:00',None,'Marie-Claire (certified, hotel-approved). References provided. Italian-speaking.',250.00),
        (22,'REQ-2026-022','Carlos Mendoza','V01','restaurant','Table at L\'Isola for 4, Feb 15 dinner 7:30PM.','CONFIRMED','MEDIUM','2026-02-15T09:00:00','2026-02-15T09:30:00',None,'Corner table confirmed. Italian wine list highlighted per guest request.',None),
        (23,'REQ-2026-023','James Richardson','V04','activity','Golf at St Barth Golf Club Feb 16. Tee time for 2 at 7AM.','CONFIRMED','MEDIUM','2026-02-15T08:00:00','2026-02-15T08:30:00',None,'Tee time confirmed. Clubs available for rent. Cart included.',200.00),
        (24,'REQ-2026-024','Yuki Tanaka','301','car_rental','Mini Moke rental for 3 days starting Feb 15.','CONFIRMED','LOW','2026-02-14T14:00:00','2026-02-14T15:00:00',None,'Barth Loc - Red Mini Moke. Delivered to hotel at 9AM. Insurance included.',210.00),
        (25,'REQ-2026-025','Emma Thompson','101','activity','Paddleboard yoga session Feb 16 morning.','PENDING','LOW','2026-02-15T10:00:00',None,None,'Checking availability with St Barth Paddle instructor.',120.00),
        (26,'REQ-2026-026','Isabel Santos','302','flowers','Bouquet of red roses delivered to room 302. With card: "Happy Anniversary"','COMPLETED','LOW','2026-02-14T07:00:00','2026-02-14T07:30:00','2026-02-14T10:00:00','Delivered at 10AM. 24 long-stem roses with handwritten card.',220.00),
        (27,'REQ-2026-027','Mohammed Al-Rashid','V05','helicopter','Helicopter tour of St Barths and neighboring islands. Feb 17, 2 hours. 4 pax.','CONFIRMED','HIGH','2026-02-15T11:00:00','2026-02-15T13:00:00',None,'Caribbean Helicopters - AS350 B3. Pilot certified. Depart Gustavia helipad 10AM.',4500.00),
        (28,'REQ-2026-028','Sophie Laurent','501','activity','Tennis lesson with pro, Feb 16 at 8AM.','PENDING','LOW','2026-02-15T14:00:00',None,None,'Contacting ASES tennis club for private lesson.',150.00),
        (29,'REQ-2026-029','David Chen','603','restaurant','Private dining room at Tamarin for 8 guests, Feb 17. Wine pairing dinner.','PENDING','HIGH','2026-02-15T12:00:00',None,None,'Awaiting confirmation from Tamarin. Requested sommelier-led wine pairing.',None),
        (30,'REQ-2026-030','James Richardson','V04','activity','Sailing lesson for family of 4, Feb 17.','PENDING','MEDIUM','2026-02-15T15:00:00',None,None,'Checking availability with Saint Barth Voile.',400.00),
        (31,'REQ-2026-031','Fatima Al-Sayed','V02','private_chef','Halal private chef for villa dinner Feb 16. 8 guests. Middle Eastern cuisine.','CONFIRMED','HIGH','2026-02-15T08:00:00','2026-02-15T10:00:00',None,'Chef Hassan (specialized in Lebanese/Gulf cuisine). Arrives 4PM. All ingredients halal-certified.',4200.00),
    ]
    c.executemany("INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", reqs)

    # Transportation
    transport = [
        (1,'TR-2026-001','James Richardson','V04','private_jet_transfer','Teterboro NJ','SBH Airport','2026-02-10T10:00:00','Gulfstream G650','NetJets Crew','COMPLETED',4,'Met at FBO. Customs pre-cleared. Luggage transferred directly to villa.',95000.00),
        (2,'TR-2026-002','Mohammed Al-Rashid','V05','airport_transfer','SXM Airport','Eden Rock Hotel','2026-02-11T14:00:00','Mercedes V-Class x2','Antoine + Marc','COMPLETED',8,'Security advance team arrived 2 hours prior. VIP protocol at SXM.',600.00),
        (3,'TR-2026-003','Alexander Wolff','401','airport_transfer','SBH Airport','Eden Rock Hotel','2026-02-15T14:00:00','Range Rover Sport','Marc','CONFIRMED',2,'Private charter from SXM. Welcome package in vehicle.',150.00),
        (4,'TR-2026-004','Fatima Al-Sayed','V02','airport_transfer','SBH Airport','Eden Rock Hotel','2026-02-15T16:00:00','Mercedes V-Class x2','Antoine + Pierre','CONFIRMED',6,'Arabic-speaking greeter. 2 vehicles for party + luggage.',300.00),
        (5,'TR-2026-005','Anna Petrov','502','car_service','Eden Rock Hotel','Gustavia Shopping','2026-02-14T10:00:00','Mercedes E-Class','Pierre','COMPLETED',1,'Personal shopping trip. Driver on standby for 4 hours.',280.00),
        (6,'TR-2026-006','James Richardson','V04','car_service','Eden Rock Hotel','Bonito Restaurant','2026-02-15T19:45:00','Range Rover Sport','Marc','CONFIRMED',4,'Dinner reservation 8PM. Return pickup arranged.',120.00),
        (7,'TR-2026-007','Leonardo Ferragamo','601','car_service','Eden Rock Hotel','Gustavia Port','2026-02-16T09:30:00','Mercedes E-Class','Antoine','CONFIRMED',6,'Yacht charter departure. Return from port ~6PM.',120.00),
        (8,'TR-2026-008','Carlos Mendoza','V01','car_service','Eden Rock Hotel','Gustavia Port','2026-02-16T06:00:00','Toyota Land Cruiser','Pierre','CONFIRMED',4,'Fishing charter early departure. Cooler for catch on return.',80.00),
        (9,'TR-2026-009','Mohammed Al-Rashid','V05','helicopter','Gustavia Helipad','Island Tour','2026-02-17T10:00:00','AS350 B3','Capt. Dubois','CONFIRMED',4,'2-hour scenic tour. Security coordination with helipad.',4500.00),
        (10,'TR-2026-010','Sophie Laurent','501','airport_transfer','Eden Rock Hotel','SBH Airport','2026-02-18T10:00:00','Mercedes E-Class','Marc','CONFIRMED',2,'Departure transfer. Flight at 12PM to SXM.',120.00),
        (11,'TR-2026-011','Emma Thompson','101','car_service','Eden Rock Hotel','Plongée Caraïbes','2026-02-15T08:30:00','Mini Cooper','Pierre','CONFIRMED',2,'Scuba diving pickup. Return ~1PM.',60.00),
    ]
    c.executemany("INSERT INTO transportation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", transport)

    # Activities
    acts = [
        (1,'Discover Scuba Diving','water_sports','Plongée Caraïbes','Introductory scuba diving experience in the crystal-clear waters of St Barths. Includes equipment, instruction, and guided dive to 12m.',3.0,175.00,4,'Colombier Bay','Mon,Tue,Wed,Thu,Fri,Sat','09:00,14:00'),
        (2,'Certified Dive Trip','water_sports','Plongée Caraïbes','Two-tank dive for certified divers. Sites include Pain de Sucre, Île Fourchue, and the Kayali wreck.',4.0,150.00,8,'Various sites','Mon,Tue,Wed,Thu,Fri,Sat','08:00'),
        (3,'Sunset Sailing Cruise','sailing','Jicky Marine','2.5-hour sunset cruise along the coast of St Barths. Champagne, wine, and canapés included.',2.5,140.00,12,'Gustavia Harbor','Daily','16:30'),
        (4,'Full Day Sailing Charter','sailing','Jicky Marine','Private full-day sailing charter. Visit Colombier, Île Fourchue, and hidden coves. Lunch on board.',8.0,2800.00,8,'Gustavia Harbor','Daily','09:00'),
        (5,'Island Tour - Half Day','tours','St Barth Tours','Guided tour of St Barths highlights: Gustavia, Saline, Gouverneur, Colombier viewpoint. Photo stops.',4.0,125.00,6,'Hotel pickup','Mon,Wed,Fri,Sat','09:00,14:00'),
        (6,'Jet Ski Rental','water_sports','Carib Waterplay','Guided jet ski tour along the coast or free rental. Safety briefing included.',1.0,150.00,2,'St Jean Beach','Daily','09:00,10:30,12:00,14:00,15:30'),
        (7,'Deep Sea Fishing','fishing','Nautica FWI','Full-day deep sea fishing charter. Target: wahoo, mahi-mahi, marlin, tuna. All equipment included.',8.0,550.00,6,'Gustavia Port','Daily','06:30'),
        (8,'Tennis Private Lesson','sports','ASES Tennis Club','Private tennis lesson with certified professional. All levels welcome. Equipment provided.',1.0,150.00,2,'ASES Tennis Club','Mon,Tue,Wed,Thu,Fri','07:00,08:00,09:00,17:00,18:00'),
        (9,'Golf at SBG','sports','St Barth Golf Club','9-hole round at the only golf course in St Barths. Stunning ocean views. Cart and clubs available.',2.0,100.00,4,'St Barth Golf Club, Grand Cul de Sac','Daily','07:00,08:00,09:00,10:00'),
        (10,'Yoga on the Beach','wellness','Harmonia SBH','Private beach yoga session. Sunrise or sunset timing. Mats and props provided.',1.5,120.00,6,'Eden Rock Beach','Daily','06:30,17:30'),
        (11,'Paddleboard Yoga','wellness','St Barth Paddle','SUP yoga session in calm waters. Unique experience combining paddleboarding and yoga.',1.5,120.00,4,'Grand Cul de Sac','Tue,Thu,Sat','08:00'),
        (12,'Helicopter Tour','air','Caribbean Helicopters','Scenic helicopter tour of St Barths and neighboring islands. Breathtaking aerial views.',1.0,1500.00,4,'Gustavia Helipad','Daily','09:00,11:00,14:00'),
        (13,'Catamaran Day Trip to Anguilla','sailing','Ocean Must','Full-day catamaran trip to Anguilla. Beach time, lunch at Blanchard\'s, snorkeling.',10.0,350.00,12,'Gustavia Harbor','Mon,Wed,Fri','08:00'),
        (14,'Snorkeling Tour','water_sports','Carib Waterplay','Guided snorkeling at top St Barths sites. Equipment provided. See turtles, rays, tropical fish.',3.0,85.00,8,'St Jean Beach','Daily','09:00,14:00'),
        (15,'Private Sailing Lesson','sailing','Saint Barth Voile','Learn to sail in the beautiful waters of St Barths. Hobie Cat or small keelboat.',2.0,200.00,4,'St Jean Bay','Mon,Tue,Wed,Thu,Fri,Sat','09:00,14:00'),
    ]
    c.executemany("INSERT INTO activities VALUES (?,?,?,?,?,?,?,?,?,?,?)", acts)

    # Recommendations
    recs = [
        (1,'Bonito','restaurant','French-South American','Trendy hilltop restaurant with stunning harbor views. Creative fusion cuisine. Outstanding cocktails and ceviche.','Gustavia','0590-27-96-96','$$$$',4.7,2.5,1,'Reserve 2+ days ahead for dinner. Sunset terrace is the best seat.'),
        (2,'Le Sereno Restaurant','restaurant','Mediterranean','Elegant beachfront dining at Le Sereno hotel. Fresh seafood and Mediterranean flavors.','Grand Cul de Sac','0590-29-83-00','$$$$',4.6,3.0,1,'Beachfront tables book fast. Lunch is more relaxed than dinner.'),
        (3,'Maya\'s','restaurant','Creole-French','Iconic beachfront restaurant run by Maya Gurley. Simple, stunning seafood. Casual chic.','Gustavia (Public Beach)','0590-27-75-73','$$$',4.8,2.0,1,'Cash only for some items. Lunch is legendary.'),
        (4,'L\'Isola','restaurant','Italian','Authentic Italian restaurant in Gustavia. Handmade pasta, fresh fish, excellent wine list.','Gustavia','0590-51-00-05','$$$',4.5,2.5,1,'Try the truffle pasta. Good for families.'),
        (5,'Tamarin','restaurant','French-Asian','Beautiful garden setting under tamarind trees. French-Asian fusion. Great for groups.','Saline','0590-27-72-12','$$$$',4.6,4.0,1,'Private dining room available. Garden ambiance is magical at night.'),
        (6,'Orega','restaurant','Japanese','Top sushi and Japanese cuisine in St Barths. Omakase available. Intimate setting.','Gustavia','0590-52-45-31','$$$$',4.7,2.5,1,'Omakase must be reserved 3+ days ahead. Counter seats are best.'),
        (7,'Shellona','restaurant','Greek-Mediterranean','Beach club restaurant at Shell Beach. Greek-influenced menu. Stunning sunset views.','Shell Beach','0590-29-06-66','$$$$',4.5,1.5,0,'Walk-ins possible for lunch. Sunset drinks are a must.'),
        (8,'Le Ti St Barth','restaurant','French-Caribbean','Legendary nightlife restaurant. Cabaret shows, dancing on tables. Unforgettable experience.','Pointe Milou','0590-27-97-71','$$$$',4.4,3.5,1,'Dinner show starts at 10PM. Dress to impress. Book 3+ days ahead.'),
        (9,'Gyp Sea Beach','restaurant','Seafood','Casual beachfront seafood spot. Great lobster, fresh catch. Feet in the sand dining.','Anse des Cayes','0590-52-46-09','$$$',4.3,4.5,0,'Perfect for a relaxed lunch. Try the lobster roll.'),
        (10,'Bagatelle','restaurant','French','Lively French restaurant with party atmosphere on weekends. Great steak and seafood.','Gustavia','0590-27-51-51','$$$$',4.5,2.5,1,'Weekend brunch is famous. Book for Saturday night.'),
        (11,'Le Select','bar','Caribbean Bar','Legendary casual bar in Gustavia. Rumored inspiration for Cheeseburger in Paradise. Simple, iconic.','Gustavia','0590-27-86-87','$',4.2,2.5,0,'Cash only. Best cheeseburger on the island. Pure island vibes.'),
        (12,'Bagatelle Bar','bar','Cocktail Bar','Upscale cocktail bar with creative mixology. DJ sets on weekends.','Gustavia','0590-27-51-51','$$$',4.4,2.5,0,'Happy hour 5-7PM. Great espresso martini.'),
        (13,'Nikki Beach','bar','Beach Club','Famous beach club with pool, music, and party atmosphere. Sunday is the main event.','St Jean','0590-27-64-64','$$$$',4.3,1.0,0,'Sunday brunch party is legendary. Reserve daybeds in advance.'),
        (14,'Bar de l\'Oubli','bar','Wine Bar','Charming wine bar on the harbor. Excellent French wine selection. Perfect pre-dinner spot.','Gustavia','0590-27-70-06','$$',4.5,2.5,0,'Great people-watching spot. Affordable by SBH standards.'),
        (15,'Modjo','bar','Cocktail Lounge','Stylish lounge bar with harbor views. Craft cocktails and tapas. DJ weekends.','Gustavia','0590-27-77-70','$$$',4.3,2.5,0,'Best rum cocktails. Rooftop terrace is stunning at sunset.'),
        (16,'Colombier Beach Hike','activity','Hiking','30-minute scenic hike to one of the most beautiful beaches in the Caribbean. Pristine, undeveloped.','Colombier',None,'Free',4.9,5.0,0,'Bring water and snorkel gear. No facilities. Best visited by morning.'),
        (17,'Saline Beach','activity','Beach','Famous natural beach. Clothing optional far end. Beautiful wild setting with sand dunes.','Saline',None,'Free',4.8,4.0,0,'Short walk from parking. No umbrellas or vendors. Bring supplies.'),
        (18,'Gustavia Shopping','activity','Shopping','Luxury shopping in the charming capital. Hermès, Louis Vuitton, Chopard, Cartier and more.','Gustavia',None,'Varies',4.5,2.5,0,'Most shops open 9AM-1PM, 3PM-7PM. Closed Sundays.'),
        (19,'Fort Karl Viewpoint','activity','Sightseeing','Historic fort ruins with panoramic views of Gustavia harbor. Great for photos.','Gustavia',None,'Free',4.4,2.5,0,'Best light for photos in morning. 10-minute walk from harbor.'),
        (20,'Inter Oceans Museum','activity','Culture','Small but fascinating shell museum with 9000+ specimens from around the world.','Corossol','0590-27-62-97','$',4.1,3.0,0,'Open Tue-Sat 9AM-12:30PM, 2PM-5PM. Allow 1 hour.'),
    ]
    c.executemany("INSERT INTO recommendations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", recs)

    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Concierge Organizer API", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "concierge-api", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1/properties/{propertyId}/requests")
def list_requests(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    status: Optional[str] = None,
    type: Optional[str] = None,
    guest: Optional[str] = None,
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM requests WHERE 1=1"
    params = []
    if status:
        sql += " AND status = ?"; params.append(status)
    if type:
        sql += " AND type = ?"; params.append(type)
    if guest:
        sql += " AND UPPER(guest_name) LIKE UPPER(?)"; params.append(f"%{guest}%")
    if dateFrom:
        sql += " AND created_at >= ?"; params.append(dateFrom)
    if dateTo:
        sql += " AND created_at <= ?"; params.append(dateTo)
    sql += " ORDER BY created_at DESC"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/requests/{requestId}")
def get_request(propertyId: str, requestId: str, x_api_key: str = Header(alias="x-api-key")):
    auth(x_api_key)
    db = get_db()
    row = db.execute("SELECT * FROM requests WHERE request_number = ? OR id = ?", (requestId, requestId)).fetchone()
    db.close()
    if not row:
        raise HTTPException(404, "Request not found")
    return {to_camel(k): v for k, v in dict(row).items()}

@app.get("/api/v1/properties/{propertyId}/transportation")
def list_transportation(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    date: Optional[str] = None,
    status: Optional[str] = None,
    guest: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM transportation WHERE 1=1"
    params = []
    if date:
        sql += " AND scheduled_at LIKE ?"; params.append(f"{date}%")
    if status:
        sql += " AND status = ?"; params.append(status)
    if guest:
        sql += " AND UPPER(guest_name) LIKE UPPER(?)"; params.append(f"%{guest}%")
    sql += " ORDER BY scheduled_at"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/activities")
def list_activities(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM activities WHERE 1=1"
    params = []
    if category:
        sql += " AND category = ?"; params.append(category)
    sql += " ORDER BY name"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/recommendations")
def list_recommendations(
    propertyId: str,
    x_api_key: str = Header(alias="x-api-key"),
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    auth(x_api_key)
    sql = "SELECT * FROM recommendations WHERE 1=1"
    params = []
    if category:
        sql += " AND category = ?"; params.append(category)
    sql += " ORDER BY rating DESC"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    db.close()
    return paginated(rows_to_dicts(rows), offset, limit)

@app.get("/api/v1/properties/{propertyId}/statistics")
def statistics(propertyId: str, x_api_key: str = Header(alias="x-api-key")):
    auth(x_api_key)
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    by_status = {}
    for row in db.execute("SELECT status, COUNT(*) as cnt FROM requests GROUP BY status"):
        by_status[row[0].lower()] = row[1]
    by_type = {}
    for row in db.execute("SELECT type, COUNT(*) as cnt FROM requests GROUP BY type ORDER BY cnt DESC"):
        by_type[row[0]] = row[1]
    total_cost = db.execute("SELECT SUM(cost_estimate) FROM requests WHERE cost_estimate IS NOT NULL").fetchone()[0] or 0
    avg_fulfillment = db.execute("""
        SELECT AVG((julianday(completed_at) - julianday(created_at)) * 24)
        FROM requests WHERE completed_at IS NOT NULL
    """).fetchone()[0]
    transport_count = db.execute("SELECT COUNT(*) FROM transportation").fetchone()[0]
    db.close()
    return {
        "totalRequests": total,
        "byStatus": by_status,
        "popularServices": by_type,
        "totalRevenueEstimate": round(total_cost, 2),
        "avgFulfillmentHours": round(avg_fulfillment or 0, 1),
        "totalTransportations": transport_count,
        "generatedAt": datetime.utcnow().isoformat()
    }
