-- FIFA World Cup AI Command Center - Database Seed Data

-- 1. Insert Initial Users
-- Password for all mock profiles is 'password123' (hashed mock values matching backend prefix)
INSERT INTO users (username, email, hashed_password, role, is_active) VALUES
('ops_admin', 'operator@fifa.org', 'pbkdf2:password123', 'operator', true),
('volunteer_sarah', 'sarah.connor@fifa.org', 'pbkdf2:password123', 'volunteer', true),
('volunteer_bob', 'bob.smith@fifa.org', 'pbkdf2:password123', 'volunteer', true),
('fan_alex', 'alex.j@gmail.com', 'pbkdf2:password123', 'fan', true),
('fan_maria', 'maria.g@yahoo.com', 'pbkdf2:password123', 'fan', true);

-- 2. Insert Match Fixtures (FIFA World Cup 2026 - MetLife Stadium NY/NJ)
INSERT INTO matches (team_a, team_b, match_time, status, risk_level) VALUES
('USA', 'England', CURRENT_TIMESTAMP + INTERVAL '2 hours', 'scheduled', 'medium'),
('Mexico', 'Argentina', CURRENT_TIMESTAMP + INTERVAL '2 days', 'scheduled', 'high'),
('Canada', 'France', CURRENT_TIMESTAMP + INTERVAL '5 days', 'scheduled', 'low'),
('Brazil', 'Germany', CURRENT_TIMESTAMP + INTERVAL '8 days', 'scheduled', 'high');

-- 3. Insert Fan Tickets
INSERT INTO tickets (user_id, match_id, seat_sector, seat_row, seat_number, qr_code, status) VALUES
(4, 1, '112', '12', '4', 'FIFA-2026-1-SEC112-R12-S4', 'active'),
(5, 1, '112', '12', '5', 'FIFA-2026-1-SEC112-R12-S5', 'active'),
(4, 2, '204', 'A', '10', 'FIFA-2026-2-SEC204-RA-S10', 'active');

-- 4. Insert Operational Incidents
INSERT INTO incidents (title, description, category, status, location, severity, assigned_volunteer_id, created_at) VALUES
('Medical assistance: Sector 109', 'Dehydration and dizziness reported by spectator in Row 4.', 'medical', 'closed', 'Sector 109 Concourse', 'low', 2, CURRENT_TIMESTAMP - INTERVAL '1 hour'),
('Scanner Congestion at Gate B Entrance', 'Ticket reader scanners running extremely slowly causing backlog.', 'crowd', 'dispatched', 'Gate B Scanners', 'medium', 2, CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
('Localized trash container overflow', 'Recycling bins overflowing near Sector 220 food courts.', 'technical', 'open', 'Sector 220 Concourse', 'low', NULL, CURRENT_TIMESTAMP - INTERVAL '5 minutes');

-- 5. Insert Volunteer Tasks
INSERT INTO tasks (title, description, assigned_to_user_id, status, created_at) VALUES
('Assist elderly seating Gate C', 'Escort VIP ticketholders with wheelchair constraints to lift access.', 2, 'completed', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
('Scanner assistance at Gate B', 'Congestion building at Gate B scanners. Mobilize hand scanners.', 2, 'in_progress', CURRENT_TIMESTAMP - INTERVAL '20 minutes'),
('Conduct ESG Waste Checks', 'Verify smart waste bin levels in Sector C and log anomalies.', 3, 'pending', CURRENT_TIMESTAMP - INTERVAL '10 minutes');

-- 6. Insert Telemetry Sensor Records
INSERT INTO sensor_data (sensor_type, value, location, recorded_at) VALUES
('crowd_count', 1420.0, 'Gate A Concourse', CURRENT_TIMESTAMP - INTERVAL '10 minutes'),
('crowd_count', 3200.0, 'Gate B Entrance', CURRENT_TIMESTAMP - INTERVAL '10 minutes'),
('crowd_count', 950.0, 'Gate C Corridor', CURRENT_TIMESTAMP - INTERVAL '10 minutes'),
('electricity', 420.0, 'Stadium Main Grid (kW)', CURRENT_TIMESTAMP - INTERVAL '5 minutes'),
('water', 18450.0, 'Recycled Greywater Reservoir (Gal)', CURRENT_TIMESTAMP - INTERVAL '5 minutes'),
('waste', 82.0, 'Smart Bins Diversion Rate (%)', CURRENT_TIMESTAMP - INTERVAL '5 minutes');

-- 7. Insert Carbon Emissions
INSERT INTO emissions (category, value, recorded_at) VALUES
('scope1', 12.4, CURRENT_TIMESTAMP - INTERVAL '1 day'), -- Direct combustion / fuels
('scope2', 45.2, CURRENT_TIMESTAMP - INTERVAL '1 day'), -- Indirect grid electricity purchased
('scope3', 40.6, CURRENT_TIMESTAMP - INTERVAL '1 day'); -- Attendee transit footprint
