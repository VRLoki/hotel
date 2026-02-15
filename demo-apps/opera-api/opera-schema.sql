-- Opera PMS-like Schema for Hotel Intel Sandbox
-- Modeled after Oracle Hospitality Opera PMS database structure

-- ═══ PROPERTY ═══
CREATE TABLE resort (
    resort_id VARCHAR2(20) PRIMARY KEY,
    resort_name VARCHAR2(100) NOT NULL,
    address1 VARCHAR2(200),
    city VARCHAR2(50),
    country VARCHAR2(50),
    phone VARCHAR2(30),
    email VARCHAR2(100),
    currency_code VARCHAR2(3) DEFAULT 'EUR',
    timezone VARCHAR2(50) DEFAULT 'America/St_Barthelemy'
);

-- ═══ ROOM TYPES & ROOMS ═══
CREATE TABLE room_types (
    resort_id VARCHAR2(20) REFERENCES resort(resort_id),
    room_type VARCHAR2(20),
    description VARCHAR2(200),
    short_description VARCHAR2(50),
    max_occupancy NUMBER(3) DEFAULT 2,
    rack_rate NUMBER(10,2),
    sort_order NUMBER(5),
    PRIMARY KEY (resort_id, room_type)
);

CREATE TABLE rooms (
    room_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resort_id VARCHAR2(20) REFERENCES resort(resort_id),
    room_number VARCHAR2(10) NOT NULL,
    room_type VARCHAR2(20) NOT NULL,
    floor_number NUMBER(3),
    room_status VARCHAR2(20) DEFAULT 'CLEAN',  -- CLEAN, DIRTY, INSPECTED, OUT_OF_ORDER, OUT_OF_SERVICE
    fo_status VARCHAR2(20) DEFAULT 'VACANT',   -- VACANT, OCCUPIED
    housekeeping_status VARCHAR2(20) DEFAULT 'CLEAN',
    is_smoking VARCHAR2(1) DEFAULT 'N',
    connecting_room VARCHAR2(10),
    description VARCHAR2(500),
    UNIQUE (resort_id, room_number)
);

-- ═══ GUEST PROFILES ═══
CREATE TABLE name_records (
    name_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name_type VARCHAR2(20) DEFAULT 'GUEST',  -- GUEST, COMPANY, TRAVEL_AGENT, SOURCE
    first_name VARCHAR2(80),
    last_name VARCHAR2(80) NOT NULL,
    title VARCHAR2(20),
    gender VARCHAR2(1),
    nationality VARCHAR2(3),
    language VARCHAR2(5) DEFAULT 'EN',
    vip_status VARCHAR2(20),  -- NULL, VIP, VVIP, CELEBRITY, ROYALTY
    email VARCHAR2(200),
    phone VARCHAR2(30),
    mobile VARCHAR2(30),
    passport_number VARCHAR2(30),
    date_of_birth DATE,
    address1 VARCHAR2(200),
    city VARCHAR2(50),
    state VARCHAR2(50),
    country VARCHAR2(50),
    postal_code VARCHAR2(20),
    membership_type VARCHAR2(30),
    membership_number VARCHAR2(30),
    preferences CLOB,  -- JSON: dietary, pillow, newspaper, etc.
    notes CLOB,
    created_date DATE DEFAULT SYSDATE,
    updated_date DATE DEFAULT SYSDATE
);

-- ═══ RESERVATIONS ═══
CREATE TABLE reservations (
    resv_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resort_id VARCHAR2(20) REFERENCES resort(resort_id),
    confirmation_no VARCHAR2(30) NOT NULL UNIQUE,
    name_id NUMBER REFERENCES name_records(name_id),
    room_number VARCHAR2(10),
    room_type VARCHAR2(20),
    arrival_date DATE NOT NULL,
    departure_date DATE NOT NULL,
    adults NUMBER(3) DEFAULT 1,
    children NUMBER(3) DEFAULT 0,
    resv_status VARCHAR2(20) DEFAULT 'RESERVED',  -- RESERVED, CHECKED_IN, CHECKED_OUT, CANCELLED, NO_SHOW
    rate_code VARCHAR2(20),
    rate_amount NUMBER(10,2),
    guarantee_code VARCHAR2(20),
    payment_method VARCHAR2(30),
    special_requests CLOB,
    eta VARCHAR2(10),  -- estimated time of arrival
    etd VARCHAR2(10),  -- estimated time of departure
    market_code VARCHAR2(20),
    source_code VARCHAR2(20),
    channel VARCHAR2(30),  -- DIRECT, OTA_BOOKING, OTA_EXPEDIA, TRAVEL_AGENT, PHONE
    company_id NUMBER REFERENCES name_records(name_id),
    travel_agent_id NUMBER REFERENCES name_records(name_id),
    group_id NUMBER,
    insert_date DATE DEFAULT SYSDATE,
    update_date DATE DEFAULT SYSDATE
);

-- ═══ RESERVATION DAILY DETAILS ═══
CREATE TABLE reservation_daily_details (
    rdd_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resv_id NUMBER REFERENCES reservations(resv_id),
    reservation_date DATE NOT NULL,
    room_number VARCHAR2(10),
    rate_amount NUMBER(10,2),
    rate_code VARCHAR2(20),
    adults NUMBER(3),
    children NUMBER(3)
);

-- ═══ FOLIOS / BILLING ═══
CREATE TABLE folio_transactions (
    trx_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resv_id NUMBER REFERENCES reservations(resv_id),
    resort_id VARCHAR2(20),
    room_number VARCHAR2(10),
    trx_date DATE DEFAULT SYSDATE,
    trx_code VARCHAR2(20) NOT NULL,  -- ROOM, FB_REST, FB_BAR, SPA, MINIBAR, PHONE, LAUNDRY, PARKING, TAX
    description VARCHAR2(200),
    amount NUMBER(10,2) NOT NULL,
    currency VARCHAR2(3) DEFAULT 'EUR',
    folio_number NUMBER(5) DEFAULT 1,
    cashier_id NUMBER,
    posted_by VARCHAR2(50)
);

-- ═══ HOUSEKEEPING ═══
CREATE TABLE housekeeping_tasks (
    task_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resort_id VARCHAR2(20),
    room_number VARCHAR2(10),
    task_date DATE DEFAULT SYSDATE,
    task_type VARCHAR2(30),  -- DEPARTURE_CLEAN, STAYOVER, TURNDOWN, DEEP_CLEAN, INSPECTION
    assigned_to VARCHAR2(50),
    status VARCHAR2(20) DEFAULT 'PENDING',  -- PENDING, IN_PROGRESS, COMPLETED, INSPECTED
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    notes VARCHAR2(500)
);

-- ═══ RATE CODES ═══
CREATE TABLE rate_codes (
    resort_id VARCHAR2(20),
    rate_code VARCHAR2(20),
    description VARCHAR2(100),
    base_amount NUMBER(10,2),
    currency VARCHAR2(3) DEFAULT 'EUR',
    market_code VARCHAR2(20),
    PRIMARY KEY (resort_id, rate_code)
);

-- ═══ CASHIERS / REVENUE CENTERS ═══
CREATE TABLE revenue_centers (
    center_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resort_id VARCHAR2(20),
    center_code VARCHAR2(20),
    description VARCHAR2(100),
    center_type VARCHAR2(30)  -- ROOMS, FOOD_BEV, SPA, RETAIL, OTHER
);

-- ═══ ALERTS / TRACES ═══
CREATE TABLE traces (
    trace_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resort_id VARCHAR2(20),
    resv_id NUMBER REFERENCES reservations(resv_id),
    trace_date DATE NOT NULL,
    trace_text VARCHAR2(500),
    department VARCHAR2(30),  -- FRONT_DESK, HOUSEKEEPING, CONCIERGE, FB, SPA, MANAGEMENT
    resolved VARCHAR2(1) DEFAULT 'N',
    resolved_by VARCHAR2(50),
    resolved_date DATE,
    created_by VARCHAR2(50),
    created_date DATE DEFAULT SYSDATE
);

-- ═══ GROUP BLOCKS ═══
CREATE TABLE group_blocks (
    group_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resort_id VARCHAR2(20),
    group_name VARCHAR2(100),
    contact_name VARCHAR2(100),
    arrival_date DATE,
    departure_date DATE,
    rooms_blocked NUMBER(5),
    rooms_picked_up NUMBER(5) DEFAULT 0,
    status VARCHAR2(20) DEFAULT 'TENTATIVE',  -- TENTATIVE, DEFINITE, CANCELLED
    notes CLOB
);

-- ═══ INDEXES ═══
CREATE INDEX idx_resv_resort_dates ON reservations(resort_id, arrival_date, departure_date);
CREATE INDEX idx_resv_status ON reservations(resv_status);
CREATE INDEX idx_resv_name ON reservations(name_id);
CREATE INDEX idx_resv_room ON reservations(room_number);
CREATE INDEX idx_resv_confirmation ON reservations(confirmation_no);
CREATE INDEX idx_folio_resv ON folio_transactions(resv_id);
CREATE INDEX idx_folio_date ON folio_transactions(trx_date);
CREATE INDEX idx_hk_date ON housekeeping_tasks(task_date);
CREATE INDEX idx_traces_date ON traces(trace_date);
CREATE INDEX idx_names_email ON name_records(email);
CREATE INDEX idx_names_lastname ON name_records(last_name);
