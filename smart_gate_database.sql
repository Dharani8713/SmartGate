-- =====================================================
-- DATABASE: smart_gate_final (Fully Optimized + Safe Reset)
-- =====================================================
CREATE DATABASE IF NOT EXISTS smart_gate_final;
USE smart_gate_final;

-- =====================================================
-- SAFE RESET SECTION
-- =====================================================
-- Disable FK checks to safely drop old tables if re-running script
SET FOREIGN_KEY_CHECKS = 0;

-- Drop tables in dependency-safe order
DROP TABLE IF EXISTS access_logs;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS temp_requests;
DROP TABLE IF EXISTS user_1;

-- Re-enable FK checks
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- TABLE 1️⃣ : user_1
-- =====================================================
CREATE TABLE IF NOT EXISTS user_1 (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    role ENUM('admin', 'family', 'delivery') DEFAULT 'family',
    priority INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================
-- TABLE 2️⃣ : vehicles
-- =====================================================
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    owner_user_id INT,
    vehicle_number VARCHAR(50) NOT NULL UNIQUE,
    status ENUM('allowed', 'temporary') DEFAULT 'temporary',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_user_id) REFERENCES user_1(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ✅ Add index for faster lookup
CREATE INDEX idx_vehicle_number ON vehicles(vehicle_number);

-- =====================================================
-- TABLE 3️⃣ : access_logs
-- =====================================================
CREATE TABLE IF NOT EXISTS access_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    vehicle_id INT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action ENUM('allowed', 'denied') DEFAULT 'denied',
    image_url VARCHAR(500),
    request_status ENUM('new', 'pending', 'approved', 'denied') DEFAULT 'new',
    FOREIGN KEY (user_id) REFERENCES user_1(user_id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- TABLE 4️⃣ : temp_requests
-- =====================================================
CREATE TABLE IF NOT EXISTS temp_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    image_url VARCHAR(500),
    phone_sent_to VARCHAR(20),
    email_sent_to VARCHAR(255),
    response_status ENUM('new', 'pending', 'approved', 'denied') DEFAULT 'new',
    timeout_deadline DATETIME DEFAULT (CURRENT_TIMESTAMP + INTERVAL 1 HOUR),
    processed_by INT NULL,
    FOREIGN KEY (processed_by) REFERENCES user_1(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- SAMPLE DATA
-- =====================================================
INSERT INTO user_1 (name, phone, email, role, priority) VALUES
('Ravi Shastry', '9876543210', 'ravi@smartgate.com', 'admin', 1),
('Aishwarya N', '9998887776', 'aish@smartgate.com', 'family', 2),
('Delivery Boy 1', '8887776665', 'del1@smartgate.com', 'delivery', 3);

INSERT INTO vehicles (owner_user_id, vehicle_number, status)
VALUES
(1, 'KA01AB1234', 'allowed'),
(2, 'KA02CD5678', 'temporary');

INSERT INTO temp_requests (image_url, phone_sent_to, email_sent_to, response_status)
VALUES
('images/unknown_vehicle1.jpg', '9876543210', 'ravi@smartgate.com', 'pending'),
('images/unknown_vehicle2.jpg', '9998887776', 'aish@smartgate.com', 'pending');

-- =====================================================
-- ADMIN ACTIONS (Simulation Examples)
-- =====================================================

-- ✅ Approve Request (Case 3)
UPDATE temp_requests
SET response_status = 'approved', processed_by = 1
WHERE request_id = 1;
INSERT INTO vehicles (owner_user_id, vehicle_number, status)
VALUES (1, CONCAT('REQ-', 1), 'allowed');
INSERT INTO access_logs (user_id, vehicle_id, action, image_url, request_status)
VALUES (1, LAST_INSERT_ID(), 'allowed', 'images/unknown_vehicle1.jpg', 'approved');

-- ✅ Deny Request (Case 4)
UPDATE temp_requests
SET response_status = 'denied', processed_by = 1
WHERE request_id = 2;
INSERT INTO access_logs (user_id, vehicle_id, action, image_url, request_status)
VALUES (1, NULL, 'denied', 'images/unknown_vehicle2.jpg', 'denied');

-- ✅ Auto-deny timed-out requests (Case 5)
SET SQL_SAFE_UPDATES = 0;
UPDATE temp_requests
SET response_status = 'denied'
WHERE response_status = 'pending' AND timeout_deadline < NOW();
SET SQL_SAFE_UPDATES = 1;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
SELECT * FROM user_1;
SELECT * FROM vehicles;
SELECT * FROM access_logs;
SELECT * FROM temp_requests;
