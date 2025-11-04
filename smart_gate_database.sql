-- ==========================================
-- DATABASE: smart_gate_v2 (Simplified Model)
-- ==========================================
CREATE DATABASE IF NOT EXISTS smart_gate_v2;
USE smart_gate_v2;

-- ==========================================
-- TABLE: users1
-- ==========================================
CREATE TABLE IF NOT EXISTS users1 (
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    role ENUM('admin', 'family', 'delivery') DEFAULT 'family',
    priority INT DEFAULT 0
) ENGINE=InnoDB;

-- ==========================================
-- TABLE: vehicles2
-- ==========================================
CREATE TABLE IF NOT EXISTS vehicles2 (
    vehicle_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    owner_user_id INT,
    vehicle_number VARCHAR(50) NOT NULL UNIQUE,
    status ENUM('allowed', 'denied', 'temporary') DEFAULT 'denied',
    FOREIGN KEY (owner_user_id) REFERENCES users1(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ==========================================
-- TABLE: access_logs3
-- ==========================================
CREATE TABLE IF NOT EXISTS access_logs3 (
    log_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    vehicle_id INT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action ENUM('allowed', 'denied') DEFAULT 'denied',
    image_url VARCHAR(500),
    request_status ENUM('new', 'pending', 'approved', 'denied') DEFAULT 'new',
    FOREIGN KEY (user_id) REFERENCES users1(user_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles2(vehicle_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ==========================================
-- TABLE: temp_requests4
-- ==========================================
CREATE TABLE IF NOT EXISTS temp_requests4 (
    request_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_url VARCHAR(500),
    phone_sent_to VARCHAR(20),
    email_sent_to VARCHAR(255),
    response_status ENUM('new', 'pending', 'approved', 'denied') DEFAULT 'new',
    timeout_deadline DATETIME
) ENGINE=InnoDB;

-- ==========================================
-- SAMPLE DATA FOR TESTING
-- ==========================================
INSERT INTO users1 (name, phone, email, role, priority)
VALUES
('Ravi Shastry', '9876543210', 'ravi@smartgate.com', 'admin', 1),
('Aishwarya N', '9998887776', 'aish@smartgate.com', 'family', 2),
('Delivery Boy 1', '8887776665', 'del1@smartgate.com', 'delivery', 3);

INSERT IGNORE INTO vehicles2 (owner_user_id, vehicle_number, status)
VALUES
(1, 'KA01AB1234', 'allowed'),
(2, 'KA02CD5678', 'temporary'),
(3, 'KA03EF9999', 'denied');

INSERT INTO temp_requests4 (image_url, phone_sent_to, email_sent_to, response_status, timeout_deadline)
VALUES
('images/unknown_vehicle1.jpg', '9876543210', 'ravi@smartgate.com', 'pending', '2025-11-05 18:00:00'),
('images/unknown_vehicle2.jpg', '9998887776', 'aish@smartgate.com', 'pending', '2025-11-05 19:00:00');

-- ==========================================
-- MANUAL ADMIN ACTIONS (Simulated)
-- ==========================================
-- Case 1: Approve first request
UPDATE temp_requests4 SET response_status = 'approved' WHERE request_id = 1;
INSERT INTO vehicles2 (owner_user_id, vehicle_number, status)
VALUES (1, CONCAT('REQ', 1), 'allowed');
INSERT INTO access_logs3 (user_id, vehicle_id, action, image_url, request_status)
VALUES (1, LAST_INSERT_ID(), 'allowed', 'images/unknown_vehicle1.jpg', 'approved');

-- Case 2: Deny second request
UPDATE temp_requests4 SET response_status = 'denied' WHERE request_id = 2;
INSERT INTO access_logs3 (user_id, vehicle_id, action, image_url, request_status)
VALUES (1, NULL, 'denied', 'images/unknown_vehicle2.jpg', 'denied');

-- ==========================================
-- CHECK RESULTS
-- ==========================================
SELECT * FROM vehicles2;      -- Approved and existing vehicles
SELECT * FROM access_logs3;   -- All access activity logs
SELECT * FROM temp_requests4; -- Requests with updated statuses
