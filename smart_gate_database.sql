-- ==========================================================
-- CREATE DATABASE
-- ==========================================================
CREATE DATABASE IF NOT EXISTS smart_gate_project;
USE smart_gate_project;

-- ==========================================================
-- TABLE 1: staff_details (All admins & security members)
-- ==========================================================
CREATE TABLE staff_details (
  staff_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  role ENUM('admin', 'security') DEFAULT 'security',
  phone_number VARCHAR(20),
  email VARCHAR(255),
  created_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================
-- TABLE 2: allowed_vehicles (Vehicles allowed to enter gate)
-- ==========================================================
CREATE TABLE allowed_vehicles (
  vehicle_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  vehicle_number VARCHAR(20) NOT NULL UNIQUE,
  owner_name VARCHAR(255),
  approved_by INT,
  approved_on DATETIME DEFAULT CURRENT_TIMESTAMP,
  valid_until DATETIME,
  FOREIGN KEY (approved_by) REFERENCES staff_details(staff_id)
);

-- ==========================================================
-- TABLE 3: waiting_vehicles (New vehicles waiting for approval)
-- ==========================================================
CREATE TABLE waiting_vehicles (
  request_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  vehicle_number VARCHAR(20) NOT NULL UNIQUE,
  detected_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  status ENUM('waiting', 'approved', 'rejected') DEFAULT 'waiting',
  reviewed_by INT,
  reviewed_on DATETIME,
  FOREIGN KEY (reviewed_by) REFERENCES staff_details(staff_id)
);

-- ==========================================================
-- TABLE 4: blocked_vehicles (Vehicles rejected or denied)
-- ==========================================================
CREATE TABLE blocked_vehicles (
  block_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  vehicle_number VARCHAR(20) NOT NULL UNIQUE,
  reason TEXT,
  blocked_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  blocked_by INT,
  FOREIGN KEY (blocked_by) REFERENCES staff_details(staff_id)
);

-- ==========================================================
-- TABLE 5: gate_logs (Stores all gate activities)
-- ==========================================================
CREATE TABLE gate_logs (
  log_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  vehicle_number VARCHAR(20) NOT NULL,
  event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  event_type ENUM('entry', 'exit') NOT NULL,
  status ENUM('granted', 'denied', 'waiting') DEFAULT 'waiting',
  gate_action ENUM('opened', 'closed') DEFAULT 'closed',
  remarks TEXT
);

-- ==========================================================
-- INSERT SAMPLE STAFF DATA
-- ==========================================================
INSERT INTO staff_details (name, role, phone_number, email) VALUES
('Aishwarya Nandeshwar', 'admin', '9876500000', 'aishwarya.admin@gate.com'),
('xyz', 'security', '9876511111', 'xyz.sec@gate.com');

-- ==========================================================
-- ADD ONE PRE-APPROVED VEHICLE
-- ==========================================================
INSERT INTO allowed_vehicles (vehicle_number, owner_name, approved_by)
VALUES ('KA01AB1234', 'Aishwarya Nandeshwar', 2);

-- ==========================================================
-- SIMULATION: NEW VEHICLE ARRIVES (KA09XY5678)
-- ==========================================================

-- Step 1: New vehicle detected and stored as waiting
INSERT INTO waiting_vehicles (vehicle_number) VALUES ('KA09XY5678');

-- Step 2: Log denied entry because not yet approved
INSERT INTO gate_logs (vehicle_number, event_type, status, gate_action, remarks)
VALUES ('KA09XY5678', 'entry', 'waiting', 'closed', 'Access denied - waiting for approval');

-- Step 3: Admin reviews and approves the vehicle
UPDATE waiting_vehicles
SET status = 'approved', reviewed_by = 1, reviewed_on = NOW()
WHERE vehicle_number = 'KA09XY5678';

-- Step 4: Move the approved vehicle into allowed_vehicles
INSERT INTO allowed_vehicles (vehicle_number, owner_name, approved_by)
SELECT vehicle_number, 'Guest Vehicle', reviewed_by
FROM waiting_vehicles
WHERE vehicle_number = 'KA09XY5678';

-- Step 5: Remove from waiting list
DELETE FROM waiting_vehicles WHERE vehicle_number = 'KA09XY5678';

-- Step 6: When the approved vehicle comes again, allow entry
INSERT INTO gate_logs (vehicle_number, event_type, status, gate_action, remarks)
VALUES ('KA09XY5678', 'entry', 'granted', 'opened', 'Authorized vehicle entry granted');

-- ==========================================================
-- OPTIONAL: BLOCK A VEHICLE
-- ==========================================================
INSERT INTO blocked_vehicles (vehicle_number, reason, blocked_by)
VALUES ('KA05ZZ9999', 'Unauthorized vehicle detected', 1);

-- ==========================================================
-- CHECK ALL TABLES (RUN THESE ONE BY ONE)
-- ==========================================================
SELECT * FROM staff_details;
SELECT * FROM allowed_vehicles;
SELECT * FROM waiting_vehicles;
SELECT * FROM blocked_vehicles;
SELECT * FROM gate_logs;
