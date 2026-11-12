-- =====================================================================
-- Migration 001: Add Shift Instances and Associate with Operational Tables
-- Platform: FactoryPulse Smart Manufacturing & OEE Platform
-- Target: MySQL 8.0+ / SQLite 3.35+
-- =====================================================================

-- 1. Create Shift Instances Table for Dated Operational Shifts
CREATE TABLE IF NOT EXISTS shift_instances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instance_code VARCHAR(60) NOT NULL,
    shift_template_id INT NOT NULL,
    plant_id INT NOT NULL,
    shift_date DATE NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    planned_break_minutes INT NOT NULL DEFAULT 60,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_shift_instances_template FOREIGN KEY (shift_template_id) REFERENCES shifts(id) ON DELETE CASCADE,
    CONSTRAINT fk_shift_instances_plant FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_plant_shift_instance (plant_id, instance_code),
    INDEX idx_shift_instances_date (shift_date),
    INDEX idx_shift_instances_window (start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Add shift_instance_id to machine_state_events
ALTER TABLE machine_state_events
    ADD COLUMN shift_instance_id INT NULL AFTER shift_id,
    ADD CONSTRAINT fk_events_shift_instance FOREIGN KEY (shift_instance_id) REFERENCES shift_instances(id) ON DELETE SET NULL,
    ADD INDEX idx_events_shift_instance (shift_instance_id);

-- 3. Add shift_instance_id to production_counts
ALTER TABLE production_counts
    ADD COLUMN shift_instance_id INT NULL AFTER shift_id,
    ADD CONSTRAINT fk_counts_shift_instance FOREIGN KEY (shift_instance_id) REFERENCES shift_instances(id) ON DELETE SET NULL,
    ADD INDEX idx_counts_shift_instance (shift_instance_id);

-- 4. Add shift_instance_id to quality_inspections
ALTER TABLE quality_inspections
    ADD COLUMN shift_instance_id INT NULL AFTER shift_id,
    ADD CONSTRAINT fk_qc_shift_instance FOREIGN KEY (shift_instance_id) REFERENCES shift_instances(id) ON DELETE SET NULL,
    ADD INDEX idx_qc_shift_instance (shift_instance_id);
