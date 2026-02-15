-- Seed Data: Eden Rock St Barths

-- ═══ RESORT ═══
INSERT INTO resort VALUES ('EDENROCK', 'Eden Rock - St Barths', 'Baie de Saint Jean', 'Saint-Barthélemy', 'France', '+590 590 29 79 99', 'info@edenrockhotel.com', 'EUR', 'America/St_Barthelemy');

-- ═══ ROOM TYPES ═══
INSERT INTO room_types VALUES ('EDENROCK', 'STD', 'Standard Room', 'Standard', 2, 850, 1);
INSERT INTO room_types VALUES ('EDENROCK', 'SUP', 'Superior Room', 'Superior', 2, 1200, 2);
INSERT INTO room_types VALUES ('EDENROCK', 'DLX', 'Deluxe Room', 'Deluxe', 3, 1800, 3);
INSERT INTO room_types VALUES ('EDENROCK', 'JRS', 'Junior Suite', 'Jr Suite', 3, 2500, 4);
INSERT INTO room_types VALUES ('EDENROCK', 'SUI', 'Suite', 'Suite', 4, 3500, 5);
INSERT INTO room_types VALUES ('EDENROCK', 'PSU', 'Premium Suite', 'Prem Suite', 4, 5000, 6);
INSERT INTO room_types VALUES ('EDENROCK', 'VIL', 'Villa', 'Villa', 8, 8000, 7);
INSERT INTO room_types VALUES ('EDENROCK', 'PVL', 'Premium Villa', 'Prem Villa', 10, 15000, 8);

-- ═══ ROOMS (37 rooms/suites/villas) ═══
-- Standard Rooms
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '101', 'STD', 1, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '102', 'STD', 1, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '103', 'STD', 1, 'CLEAN', 'VACANT', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '104', 'STD', 1, 'DIRTY', 'VACANT', 'DIRTY');
-- Superior Rooms
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '201', 'SUP', 2, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '202', 'SUP', 2, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '203', 'SUP', 2, 'CLEAN', 'VACANT', 'INSPECTED');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '204', 'SUP', 2, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '205', 'SUP', 2, 'OUT_OF_SERVICE', 'VACANT', 'DIRTY');
-- Deluxe Rooms
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '301', 'DLX', 3, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '302', 'DLX', 3, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '303', 'DLX', 3, 'CLEAN', 'VACANT', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '304', 'DLX', 3, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '305', 'DLX', 3, 'DIRTY', 'VACANT', 'DIRTY');
-- Junior Suites
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '401', 'JRS', 4, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '402', 'JRS', 4, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '403', 'JRS', 4, 'CLEAN', 'VACANT', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '404', 'JRS', 4, 'CLEAN', 'OCCUPIED', 'CLEAN');
-- Suites
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '501', 'SUI', 5, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '502', 'SUI', 5, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '503', 'SUI', 5, 'CLEAN', 'VACANT', 'INSPECTED');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '504', 'SUI', 5, 'CLEAN', 'OCCUPIED', 'CLEAN');
-- Premium Suites
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '601', 'PSU', 6, 'CLEAN', 'OCCUPIED', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '602', 'PSU', 6, 'CLEAN', 'VACANT', 'CLEAN');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status) VALUES ('EDENROCK', '603', 'PSU', 6, 'CLEAN', 'OCCUPIED', 'CLEAN');
-- Villas
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status, description) VALUES ('EDENROCK', 'V01', 'VIL', 0, 'CLEAN', 'OCCUPIED', 'CLEAN', 'Villa Rockstar - 4 bedrooms, recording studio, cinema');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status, description) VALUES ('EDENROCK', 'V02', 'VIL', 0, 'CLEAN', 'OCCUPIED', 'CLEAN', 'Villa Nina - 3 bedrooms, infinity pool');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status, description) VALUES ('EDENROCK', 'V03', 'VIL', 0, 'CLEAN', 'VACANT', 'CLEAN', 'Villa Lila - 2 bedrooms, garden view');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status, description) VALUES ('EDENROCK', 'V04', 'PVL', 0, 'CLEAN', 'OCCUPIED', 'CLEAN', 'Diamond Villa - 5 bedrooms, private beach, butler service');
INSERT INTO rooms (resort_id, room_number, room_type, floor_number, room_status, fo_status, housekeeping_status, description) VALUES ('EDENROCK', 'V05', 'PVL', 0, 'CLEAN', 'OCCUPIED', 'CLEAN', 'Ultra Villa - 4 bedrooms, helipad, ocean panorama');

-- ═══ GUEST PROFILES ═══
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, vip_status, email, phone, mobile, date_of_birth, address1, city, country, postal_code, membership_type, membership_number, preferences) VALUES ('James', 'Richardson', 'Mr', 'M', 'US', 'EN', 'VVIP', 'j.richardson@gmail.com', '+1-212-555-0101', '+1-917-555-0101', DATE '1968-03-15', '740 Park Avenue', 'New York', 'USA', '10021', 'DIAMOND', 'DM-100234', '{"dietary":"gluten-free","pillow":"firm","newspaper":"WSJ","minibar":"restock-daily","room_temp":"20C"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, vip_status, email, phone, mobile, date_of_birth, address1, city, country, postal_code, preferences) VALUES ('Sophie', 'Laurent', 'Mme', 'F', 'FR', 'FR', 'VIP', 'sophie.laurent@orange.fr', '+33-1-42-55-0102', '+33-6-55-0102', DATE '1975-07-22', '16 Avenue Montaigne', 'Paris', 'France', '75008', '{"dietary":"vegetarian","pillow":"soft","newspaper":"Le Figaro","flowers":"white orchids"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, vip_status, email, phone, mobile, date_of_birth, address1, city, country, postal_code, membership_type, membership_number, preferences) VALUES ('Mohammed', 'Al-Rashid', 'HRH', 'M', 'AE', 'AR', 'ROYALTY', 'private@alrashid.ae', '+971-4-555-0103', '+971-50-555-0103', DATE '1980-11-01', 'Emirates Hills', 'Dubai', 'UAE', '', 'PLATINUM', 'PT-500012', '{"dietary":"halal","room_temp":"18C","butler":"24h","security":"discrete","newspaper":"Gulf News","extra_beds":2}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, email, phone, mobile, date_of_birth, address1, city, country, postal_code, preferences) VALUES ('Emma', 'Thompson', 'Ms', 'F', 'GB', 'EN', 'emma.t@outlook.com', '+44-20-7555-0104', '+44-7700-555104', DATE '1985-09-10', '12 Kensington Gardens', 'London', 'UK', 'W8 4PX', '{"dietary":"none","pillow":"medium","newspaper":"The Times"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, vip_status, email, phone, mobile, date_of_birth, address1, city, country, postal_code, preferences, notes) VALUES ('Leonardo', 'Ferragamo', 'Sig', 'M', 'IT', 'IT', 'CELEBRITY', 'leo.f@ferragamo.it', '+39-055-555-0105', '+39-333-555-0105', DATE '1972-01-28', 'Via Tornabuoni 2', 'Florence', 'Italy', '50123', '{"dietary":"mediterranean","wine":"barolo-reserve","spa":"daily-massage","yacht":"reserve-on-arrival"}', 'Fashion CEO. Prefers absolute privacy. No photos.');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, email, phone, mobile, date_of_birth, address1, city, country, preferences) VALUES ('Yuki', 'Tanaka', 'Ms', 'F', 'JP', 'JA', 'yuki.tanaka@sony.co.jp', '+81-3-5555-0106', '+81-90-5555-0106', DATE '1990-04-05', '1-7-1 Konan, Minato-ku', 'Tokyo', 'Japan', '{"dietary":"pescatarian","tea":"matcha","pillow":"buckwheat","newspaper":"Nikkei"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, vip_status, email, phone, mobile, date_of_birth, address1, city, country, postal_code, preferences) VALUES ('Carlos', 'Mendoza', 'Sr', 'M', 'MX', 'ES', 'VIP', 'carlos.m@mendozagroup.mx', '+52-55-5555-0107', '+52-1-55-5555-0107', DATE '1965-12-20', 'Paseo de la Reforma 505', 'Mexico City', 'Mexico', '06500', '{"dietary":"none","cigar":"humidor-in-room","golf":"arrange-tee-times","car":"luxury-suv"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, email, phone, mobile, date_of_birth, address1, city, country, postal_code, preferences) VALUES ('Anna', 'Petrov', 'Mrs', 'F', 'CH', 'FR', 'anna.petrov@ubs.com', '+41-44-555-0108', '+41-79-555-0108', DATE '1978-06-18', 'Bahnhofstrasse 45', 'Zurich', 'Switzerland', '8001', '{"dietary":"low-carb","spa":"hot-stone-massage","newspaper":"NZZ","champagne":"dom-perignon"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, vip_status, email, phone, mobile, date_of_birth, address1, city, country, preferences, notes) VALUES ('David', 'Chen', 'Mr', 'M', 'SG', 'EN', 'VVIP', 'david.chen@temasek.sg', '+65-6555-0109', '+65-9555-0109', DATE '1970-08-30', '60 Nassim Road', 'Singapore', 'Singapore', '{"dietary":"none","wine":"burgundy","art":"contemporary","butler":"24h","newspaper":"Straits Times"}', 'Major investor. Returning guest (12th stay). Birthday Aug 30.');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, email, phone, mobile, address1, city, country, preferences) VALUES ('Isabel', 'Santos', 'Sra', 'F', 'BR', 'PT', 'isabel.santos@gmail.com', '+55-11-5555-0110', '+55-11-9555-0110', 'Av Paulista 1000', 'São Paulo', 'Brazil', '{"dietary":"vegan","yoga":"morning-session","spa":"ayurvedic","flowers":"tropical"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, email, phone, date_of_birth, address1, city, country, preferences) VALUES ('Alexander', 'Wolff', 'Dr', 'M', 'DE', 'DE', 'a.wolff@bmw.de', '+49-89-555-0111', DATE '1960-02-14', 'Maximilianstrasse 12', 'Munich', 'Germany', '{"dietary":"none","car":"porsche-rental","golf":"daily","newspaper":"FAZ","wine":"riesling"}');
INSERT INTO name_records (first_name, last_name, title, gender, nationality, language, vip_status, email, phone, mobile, address1, city, country, preferences) VALUES ('Fatima', 'Al-Sayed', 'Mrs', 'F', 'QA', 'AR', 'VIP', 'fatima@alsayed.qa', '+974-4455-0112', '+974-5555-0112', 'The Pearl, Tower 1', 'Doha', 'Qatar', '{"dietary":"halal","shopping":"personal-shopper","spa":"daily","childcare":"nanny-service","extra_beds":3}');

-- ═══ RATE CODES ═══
INSERT INTO rate_codes VALUES ('EDENROCK', 'BAR', 'Best Available Rate', 0, 'EUR', 'TRANSIENT');
INSERT INTO rate_codes VALUES ('EDENROCK', 'RACK', 'Rack Rate', 0, 'EUR', 'TRANSIENT');
INSERT INTO rate_codes VALUES ('EDENROCK', 'CORP', 'Corporate Rate', 0, 'EUR', 'CORPORATE');
INSERT INTO rate_codes VALUES ('EDENROCK', 'OTA', 'OTA Rate', 0, 'EUR', 'OTA');
INSERT INTO rate_codes VALUES ('EDENROCK', 'VIP', 'VIP Complimentary', 0, 'EUR', 'COMP');
INSERT INTO rate_codes VALUES ('EDENROCK', 'GRP', 'Group Rate', 0, 'EUR', 'GROUP');
INSERT INTO rate_codes VALUES ('EDENROCK', 'PKG', 'Package Rate (incl. breakfast + spa)', 0, 'EUR', 'PACKAGE');

-- ═══ REVENUE CENTERS ═══
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'ROOMS', 'Room Revenue', 'ROOMS');
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'SAND', 'Sand Bar', 'FOOD_BEV');
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'JEAN', 'Jean-Georges Restaurant', 'FOOD_BEV');
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'RBAR', 'Rock Bar', 'FOOD_BEV');
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'SPA', 'Eden Spa', 'SPA');
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'MINI', 'Minibar', 'FOOD_BEV');
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'BOUT', 'Boutique', 'RETAIL');
INSERT INTO revenue_centers (resort_id, center_code, description, center_type) VALUES ('EDENROCK', 'WATR', 'Watersports', 'OTHER');

-- ═══ RESERVATIONS (current + upcoming) ═══
-- Using relative dates: today = Feb 14, 2026

-- James Richardson - VVIP in Diamond Villa, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, payment_method, special_requests, eta, channel, market_code) VALUES ('EDENROCK', 'ER-2026-0001', 1, 'V04', 'PVL', DATE '2026-02-10', DATE '2026-02-20', 2, 0, 'CHECKED_IN', 'BAR', 15000, 'AMEX', 'Private chef dinner on Feb 15. Dom Perignon in room. Airport transfer arranged.', '14:00', 'DIRECT', 'TRANSIENT');

-- Sophie Laurent - VIP in Suite, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, payment_method, special_requests, channel) VALUES ('EDENROCK', 'ER-2026-0002', 2, '501', 'SUI', DATE '2026-02-12', DATE '2026-02-18', 1, 0, 'CHECKED_IN', 'BAR', 3500, 'VISA', 'White orchids in room. Vegetarian menu at all restaurants.', 'DIRECT');

-- Mohammed Al-Rashid - ROYALTY in Ultra Villa, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, payment_method, special_requests, channel) VALUES ('EDENROCK', 'ER-2026-0003', 3, 'V05', 'PVL', DATE '2026-02-11', DATE '2026-02-25', 4, 2, 'CHECKED_IN', 'VIP', 15000, 'WIRE', '24h butler. Halal kitchen. Extra security. 3 additional rooms for staff (201, 202, 204).', 'DIRECT');

-- Emma Thompson - Standard room, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, payment_method, channel) VALUES ('EDENROCK', 'ER-2026-0004', 4, '101', 'STD', DATE '2026-02-13', DATE '2026-02-17', 2, 0, 'CHECKED_IN', 'OTA', 850, 'MASTERCARD', 'OTA_BOOKING');

-- Leonardo Ferragamo - CELEBRITY in Premium Suite, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, payment_method, special_requests, channel) VALUES ('EDENROCK', 'ER-2026-0005', 5, '601', 'PSU', DATE '2026-02-13', DATE '2026-02-19', 2, 0, 'CHECKED_IN', 'BAR', 5000, 'AMEX', 'Absolute privacy. No room service knocks - call first. Yacht reserved for Feb 16.', 'TRAVEL_AGENT');

-- Yuki Tanaka - Deluxe, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, channel) VALUES ('EDENROCK', 'ER-2026-0006', 6, '301', 'DLX', DATE '2026-02-14', DATE '2026-02-21', 1, 0, 'CHECKED_IN', 'PKG', 1800, 'DIRECT');

-- Carlos Mendoza - VIP in Villa Rockstar, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, payment_method, special_requests, channel) VALUES ('EDENROCK', 'ER-2026-0007', 7, 'V01', 'VIL', DATE '2026-02-12', DATE '2026-02-22', 2, 0, 'CHECKED_IN', 'BAR', 8000, 'AMEX', 'Cigars: Cohiba Behike. Golf at 7am daily. Black SUV on standby.', 'DIRECT');

-- Anna Petrov - Suite, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, channel) VALUES ('EDENROCK', 'ER-2026-0008', 8, '502', 'SUI', DATE '2026-02-13', DATE '2026-02-16', 1, 0, 'CHECKED_IN', 'CORP', 3200, 'DIRECT');

-- David Chen - VVIP in Premium Suite, checked in
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, payment_method, special_requests, channel) VALUES ('EDENROCK', 'ER-2026-0009', 9, '603', 'PSU', DATE '2026-02-10', DATE '2026-02-17', 2, 0, 'CHECKED_IN', 'BAR', 5000, 'AMEX', 'Contemporary art catalog in room. Burgundy wine selection. 12th stay - anniversary gift.', 'DIRECT');

-- Isabel Santos - Deluxe, checked in today
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, channel) VALUES ('EDENROCK', 'ER-2026-0010', 10, '302', 'DLX', DATE '2026-02-14', DATE '2026-02-20', 1, 0, 'CHECKED_IN', 'BAR', 1800, 'DIRECT');

-- Dr. Wolff - Junior Suite, arriving tomorrow
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, eta, channel) VALUES ('EDENROCK', 'ER-2026-0011', 11, '401', 'JRS', DATE '2026-02-15', DATE '2026-02-22', 1, 0, 'RESERVED', 'BAR', 2500, '11:00', 'DIRECT');

-- Fatima Al-Sayed - VIP, Villa Nina, arriving tomorrow
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, special_requests, eta, channel) VALUES ('EDENROCK', 'ER-2026-0012', 12, 'V02', 'VIL', DATE '2026-02-15', DATE '2026-02-28', 2, 3, 'RESERVED', 'BAR', 8000, 'Nanny service needed. Kids club enrollment. Halal meals for children. Personal shopper on Feb 17.', '15:30', 'DIRECT');

-- Checked out yesterday
INSERT INTO reservations (resort_id, confirmation_no, name_id, room_number, room_type, arrival_date, departure_date, adults, children, resv_status, rate_code, rate_amount, channel) VALUES ('EDENROCK', 'ER-2026-0013', 4, '104', 'STD', DATE '2026-02-08', DATE '2026-02-13', 2, 0, 'CHECKED_OUT', 'OTA', 850, 'OTA_EXPEDIA');

-- ═══ FOLIO TRANSACTIONS (last few days) ═══
-- Richardson (V04)
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (1, 'EDENROCK', 'V04', DATE '2026-02-13', 'ROOM', 'Room Charge - Diamond Villa', 15000);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (1, 'EDENROCK', 'V04', DATE '2026-02-13', 'FB_REST', 'Jean-Georges - Dinner for 2', 890);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (1, 'EDENROCK', 'V04', DATE '2026-02-13', 'FB_BAR', 'Rock Bar - Dom Perignon x2', 780);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (1, 'EDENROCK', 'V04', DATE '2026-02-13', 'SPA', 'Couples Massage 90min', 450);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (1, 'EDENROCK', 'V04', DATE '2026-02-14', 'ROOM', 'Room Charge - Diamond Villa', 15000);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (1, 'EDENROCK', 'V04', DATE '2026-02-14', 'FB_REST', 'Sand Bar - Lunch', 320);

-- Laurent (501)
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (2, 'EDENROCK', '501', DATE '2026-02-13', 'ROOM', 'Room Charge - Suite', 3500);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (2, 'EDENROCK', '501', DATE '2026-02-13', 'SPA', 'Aromatherapy Facial', 280);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (2, 'EDENROCK', '501', DATE '2026-02-14', 'ROOM', 'Room Charge - Suite', 3500);

-- Al-Rashid (V05)
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (3, 'EDENROCK', 'V05', DATE '2026-02-13', 'ROOM', 'Room Charge - Ultra Villa', 15000);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (3, 'EDENROCK', 'V05', DATE '2026-02-13', 'FB_REST', 'Private Dining - Halal Menu (8 pax)', 2200);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (3, 'EDENROCK', 'V05', DATE '2026-02-14', 'ROOM', 'Room Charge - Ultra Villa', 15000);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (3, 'EDENROCK', 'V05', DATE '2026-02-14', 'WATR', 'Private Yacht Charter - Full Day', 8500);

-- Ferragamo (601)
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (5, 'EDENROCK', '601', DATE '2026-02-13', 'ROOM', 'Room Charge - Premium Suite', 5000);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (5, 'EDENROCK', '601', DATE '2026-02-13', 'SPA', 'Deep Tissue Massage 60min', 320);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (5, 'EDENROCK', '601', DATE '2026-02-14', 'ROOM', 'Room Charge - Premium Suite', 5000);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (5, 'EDENROCK', '601', DATE '2026-02-14', 'BOUT', 'Boutique - Sunglasses', 650);

-- Chen (603)
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (9, 'EDENROCK', '603', DATE '2026-02-13', 'ROOM', 'Room Charge - Premium Suite', 5000);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (9, 'EDENROCK', '603', DATE '2026-02-13', 'FB_REST', 'Jean-Georges - Dinner + Wine Pairing', 1150);
INSERT INTO folio_transactions (resv_id, resort_id, room_number, trx_date, trx_code, description, amount) VALUES (9, 'EDENROCK', '603', DATE '2026-02-14', 'ROOM', 'Room Charge - Premium Suite', 5000);

-- ═══ HOUSEKEEPING TASKS (today) ═══
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status) VALUES ('EDENROCK', '104', DATE '2026-02-14', 'DEPARTURE_CLEAN', 'Marie', 'COMPLETED');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status) VALUES ('EDENROCK', '305', DATE '2026-02-14', 'DEPARTURE_CLEAN', 'Jean', 'IN_PROGRESS');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status) VALUES ('EDENROCK', '101', DATE '2026-02-14', 'STAYOVER', 'Marie', 'COMPLETED');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status) VALUES ('EDENROCK', '102', DATE '2026-02-14', 'STAYOVER', 'Sophie', 'PENDING');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status) VALUES ('EDENROCK', '301', DATE '2026-02-14', 'STAYOVER', 'Sophie', 'COMPLETED');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status) VALUES ('EDENROCK', 'V04', DATE '2026-02-14', 'STAYOVER', 'Team A', 'COMPLETED');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status) VALUES ('EDENROCK', 'V05', DATE '2026-02-14', 'STAYOVER', 'Team B', 'IN_PROGRESS');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status, notes) VALUES ('EDENROCK', '205', DATE '2026-02-14', 'DEEP_CLEAN', 'Jean', 'PENDING', 'AC unit repair completed. Deep clean before returning to service.');
-- Tomorrow prep for arrivals
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status, notes) VALUES ('EDENROCK', '401', DATE '2026-02-15', 'STAYOVER', 'Marie', 'PENDING', 'VIP arrival: Dr. Wolff. Prepare Porsche rental docs on desk.');
INSERT INTO housekeeping_tasks (resort_id, room_number, task_date, task_type, assigned_to, status, notes) VALUES ('EDENROCK', 'V02', DATE '2026-02-15', 'STAYOVER', 'Team A', 'PENDING', 'VIP arrival: Al-Sayed family. 3 extra beds, childproofing, halal welcome amenities.');

-- ═══ TRACES / ALERTS ═══
INSERT INTO traces (resort_id, resv_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', 1, DATE '2026-02-14', 'Private chef dinner tonight at 20:00 for Mr. Richardson. Menu approved. Wine: Chateau Margaux 2015.', 'FB', 'Concierge');
INSERT INTO traces (resort_id, resv_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', 1, DATE '2026-02-15', 'Airport transfer arranged for Feb 20 departure. Private jet ETA 10:00.', 'FRONT_DESK', 'Reservations');
INSERT INTO traces (resort_id, resv_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', 3, DATE '2026-02-14', 'Security detail rotation at 18:00. New team arriving from Dubai.', 'MANAGEMENT', 'GM');
INSERT INTO traces (resort_id, resv_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', 5, DATE '2026-02-16', 'Yacht charter confirmed. 42ft Sunseeker. Pickup at hotel dock 09:00.', 'CONCIERGE', 'Concierge');
INSERT INTO traces (resort_id, resv_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', 9, DATE '2026-02-14', '12th stay anniversary. Complimentary upgrade approved by GM. Gift basket + handwritten note.', 'FRONT_DESK', 'FOM');
INSERT INTO traces (resort_id, resv_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', 12, DATE '2026-02-15', 'VIP arrival tomorrow. Nanny confirmed. Kids club notified. Halal welcome amenities in villa.', 'CONCIERGE', 'Concierge');
INSERT INTO traces (resort_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', DATE '2026-02-14', 'Room 205 AC repair completed. Ready for deep clean and inspection before returning to inventory.', 'HOUSEKEEPING', 'Maintenance');
INSERT INTO traces (resort_id, trace_date, trace_text, department, created_by) VALUES ('EDENROCK', DATE '2026-02-14', 'Jean-Georges: Special Valentine dinner menu tonight. Full house expected. Extra staff called in.', 'FB', 'F&B Manager');

-- ═══ GROUP BLOCK ═══
INSERT INTO group_blocks (resort_id, group_name, contact_name, arrival_date, departure_date, rooms_blocked, rooms_picked_up, status, notes) VALUES ('EDENROCK', 'Cartier Private Event', 'Marie Duval', DATE '2026-02-20', DATE '2026-02-23', 12, 8, 'DEFINITE', 'Annual VIP client event. Requires: ballroom setup, branded welcome amenities, private dinner on Feb 21.');

COMMIT;
