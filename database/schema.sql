-- =====================================================================
-- FactoryPulse - Smart Manufacturing Performance & OEE Monitoring Platform
-- Database Schema (MySQL 8.0+)
-- Database: factorypulse_db
-- =====================================================================

CREATE DATABASE IF NOT EXISTS factorypulse_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE factorypulse_db;

-- ---------------------------------------------------------------------
-- 1. Users Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('ADMIN', 'OPERATOR', 'MAINTENANCE', 'QUALITY', 'PLANNER') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 2. Plants Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS plants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(150),
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_plants_code (plant_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 3. Production Lines Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS production_lines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    line_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    target_oee DECIMAL(5,2) NOT NULL DEFAULT 85.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_lines_plant FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE RESTRICT,
    INDEX idx_lines_plant (plant_id),
    INDEX idx_lines_code (line_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 4. Machines Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS machines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    line_id INT NOT NULL,
    machine_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    current_status ENUM('RUNNING', 'STOPPED', 'IDLE', 'CHANGEOVER', 'MAINTENANCE', 'BREAK') NOT NULL DEFAULT 'IDLE',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_machines_line FOREIGN KEY (line_id) REFERENCES production_lines(id) ON DELETE RESTRICT,
    INDEX idx_machines_line (line_id),
    INDEX idx_machines_status (current_status),
    INDEX idx_machines_code (machine_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 5. Shifts Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plant_id INT NOT NULL,
    shift_code VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    planned_break_minutes INT NOT NULL DEFAULT 60,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_shifts_plant FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_plant_shift (plant_id, shift_code),
    INDEX idx_shifts_plant (plant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 6. Products Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    ideal_cycle_time_seconds DECIMAL(10,4) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'units',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_products_code (product_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 7. Downtime Reasons Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS downtime_reasons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reason_code VARCHAR(50) NOT NULL UNIQUE,
    category ENUM('UNPLANNED_DOWNTIME', 'PLANNED_DOWNTIME', 'BREAK', 'CHANGEOVER', 'MAINTENANCE') NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_planned BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_downtime_category (category),
    INDEX idx_downtime_code (reason_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 8. Production Orders Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS production_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_code VARCHAR(50) NOT NULL UNIQUE,
    line_id INT NOT NULL,
    product_id INT NOT NULL,
    target_quantity INT NOT NULL,
    produced_quantity INT NOT NULL DEFAULT 0,
    status ENUM('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD', 'CANCELLED') NOT NULL DEFAULT 'PLANNED',
    start_time DATETIME NULL,
    end_time DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_po_line FOREIGN KEY (line_id) REFERENCES production_lines(id) ON DELETE RESTRICT,
    CONSTRAINT fk_po_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    INDEX idx_po_line (line_id),
    INDEX idx_po_product (product_id),
    INDEX idx_po_status (status),
    INDEX idx_po_code (order_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 9. Machine State Events Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS machine_state_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_code VARCHAR(60) NOT NULL UNIQUE,
    machine_id INT NOT NULL,
    production_order_id INT NULL,
    shift_id INT NULL,
    state ENUM('RUNNING', 'STOPPED', 'IDLE', 'CHANGEOVER', 'MAINTENANCE', 'BREAK') NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_seconds INT NOT NULL,
    downtime_reason_id INT NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_events_machine FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
    CONSTRAINT fk_events_po FOREIGN KEY (production_order_id) REFERENCES production_orders(id) ON DELETE SET NULL,
    CONSTRAINT fk_events_shift FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE SET NULL,
    CONSTRAINT fk_events_reason FOREIGN KEY (downtime_reason_id) REFERENCES downtime_reasons(id) ON DELETE SET NULL,
    INDEX idx_events_machine_time (machine_id, start_time, end_time),
    INDEX idx_events_state (state),
    INDEX idx_events_po (production_order_id),
    INDEX idx_events_shift (shift_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 10. Production Counts Table (with Audit & Traceable Corrections)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS production_counts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    count_code VARCHAR(60) NOT NULL UNIQUE,
    production_order_id INT NOT NULL,
    machine_id INT NOT NULL,
    shift_id INT NULL,
    product_id INT NOT NULL,
    count_type ENUM('GOOD', 'SCRAP', 'REWORK', 'CORRECTION') NOT NULL,
    quantity INT NOT NULL,
    timestamp DATETIME NOT NULL,
    operator_id INT NULL,
    reference_count_id INT NULL,
    reason VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_counts_po FOREIGN KEY (production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_counts_machine FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
    CONSTRAINT fk_counts_shift FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE SET NULL,
    CONSTRAINT fk_counts_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    CONSTRAINT fk_counts_operator FOREIGN KEY (operator_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_counts_ref FOREIGN KEY (reference_count_id) REFERENCES production_counts(id) ON DELETE SET NULL,
    INDEX idx_counts_po (production_order_id),
    INDEX idx_counts_machine_time (machine_id, timestamp),
    INDEX idx_counts_type (count_type),
    INDEX idx_counts_ref (reference_count_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 11. Quality Inspections Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS quality_inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_code VARCHAR(60) NOT NULL UNIQUE,
    production_order_id INT NOT NULL,
    machine_id INT NOT NULL,
    shift_id INT NULL,
    sample_size INT NOT NULL,
    passed_count INT NOT NULL,
    failed_count INT NOT NULL,
    defect_type VARCHAR(100) NULL,
    inspector_id INT NULL,
    timestamp DATETIME NOT NULL,
    status ENUM('PASSED', 'FAILED', 'CONDITIONAL') NOT NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_qc_po FOREIGN KEY (production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_qc_machine FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE,
    CONSTRAINT fk_qc_shift FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE SET NULL,
    CONSTRAINT fk_qc_inspector FOREIGN KEY (inspector_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_qc_po (production_order_id),
    INDEX idx_qc_machine_time (machine_id, timestamp),
    INDEX idx_qc_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 12. OEE Aggregates Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS oee_aggregates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aggregation_level ENUM('MACHINE', 'LINE', 'SHIFT', 'PRODUCT', 'PLANT') NOT NULL,
    entity_id INT NOT NULL,
    entity_code VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    shift_id INT NULL,
    planned_production_time_minutes DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    operating_time_minutes DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    planned_downtime_minutes DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    unplanned_downtime_minutes DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    ideal_cycle_time_seconds DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
    total_count INT NOT NULL DEFAULT 0,
    good_count INT NOT NULL DEFAULT 0,
    scrap_count INT NOT NULL DEFAULT 0,
    rework_count INT NOT NULL DEFAULT 0,
    availability DECIMAL(6,4) NOT NULL DEFAULT 0.0000,
    performance DECIMAL(6,4) NOT NULL DEFAULT 0.0000,
    quality DECIMAL(6,4) NOT NULL DEFAULT 0.0000,
    oee DECIMAL(6,4) NOT NULL DEFAULT 0.0000,
    performance_flagged BOOLEAN NOT NULL DEFAULT FALSE,
    calculated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_oee_level_entity (aggregation_level, entity_id),
    INDEX idx_oee_date (date),
    INDEX idx_oee_shift (shift_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- 13. Detected Anomalies Table
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS detected_anomalies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    anomaly_code VARCHAR(60) NOT NULL UNIQUE,
    anomaly_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    timestamp DATETIME NOT NULL,
    severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW') NOT NULL,
    description TEXT NOT NULL,
    expected_value VARCHAR(255) NOT NULL,
    actual_value VARCHAR(255) NOT NULL,
    recommended_action TEXT NOT NULL,
    resolution_status ENUM('OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE') NOT NULL DEFAULT 'OPEN',
    detected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    INDEX idx_anom_type (anomaly_type),
    INDEX idx_anom_severity (severity),
    INDEX idx_anom_status (resolution_status),
    INDEX idx_anom_time (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
