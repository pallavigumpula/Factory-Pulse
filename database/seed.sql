-- =====================================================================
-- FactoryPulse - Seed Master Data
-- Database: factorypulse_db
-- =====================================================================

USE factorypulse_db;

-- ---------------------------------------------------------------------
-- Users Seed Data (Roles: ADMIN, OPERATOR, MAINTENANCE, QUALITY, PLANNER)
-- Default passwords:
--   admin: admin123
--   operator1: operator123
--   maint1: maint123
--   qc1: qc123
--   planner1: planner123
-- ---------------------------------------------------------------------
INSERT INTO users (username, email, password_hash, full_name, role, is_active) VALUES
('admin', 'admin@factorypulse.internal', 'pbkdf2:sha256:100000$9c3427cf11149519434a50b7c05f0b89$82a8ab070927ded2195a0cecd97c249cb1ca80da514f22bc72c46c02b275308b', 'System Administrator', 'ADMIN', 1),
('operator1', 'operator1@factorypulse.internal', 'pbkdf2:sha256:100000$b520e5a3d61011ea3bd49baf77e0a62f$134a6c10c59832ccbcaa8231ceea0c6e86032e9e22391b4dd0e35ded06ff142d', 'Lead Operator John Vance', 'OPERATOR', 1),
('maint1', 'maint1@factorypulse.internal', 'pbkdf2:sha256:100000$b6193de895f9cae8d529a158015f6910$8342e65f0f7c72b4ffac9d20e04933fc59e79212e97d5548ad7904507913c529', 'Maintenance Eng. Sarah Connor', 'MAINTENANCE', 1),
('qc1', 'qc1@factorypulse.internal', 'pbkdf2:sha256:100000$395938954f7cda9f9c6770160edd62f8$2b458755159c917dbcfad6ee6717c8702fc5b0ae2a16eeae347cc48a4ed67927', 'Quality Inspector Alex Chen', 'QUALITY', 1),
('planner1', 'planner1@factorypulse.internal', 'pbkdf2:sha256:100000$8de1cfbac6096513e9ccd5334e0668ca$d1a9cc152944ba4cdf27b3aa61073aa5f156b0329591d1a7163e08352c52004d', 'Production Planner Elena Rostova', 'PLANNER', 1)
ON DUPLICATE KEY UPDATE full_name=VALUES(full_name);

-- ---------------------------------------------------------------------
-- Plants Seed Data
-- ---------------------------------------------------------------------
INSERT INTO plants (id, plant_code, name, location, timezone, is_active) VALUES
(1, 'PLANT-01', 'Austin Advanced Electronics Plant', 'Austin, TX, USA', 'America/Chicago', 1),
(2, 'PLANT-02', 'Detroit Precision Machining Works', 'Detroit, MI, USA', 'America/Detroit', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ---------------------------------------------------------------------
-- Production Lines Seed Data (5 Lines)
-- ---------------------------------------------------------------------
INSERT INTO production_lines (id, plant_id, line_code, name, target_oee, is_active) VALUES
(1, 1, 'LINE-01', 'SMT High-Speed Surface Mount Line 1', 88.00, 1),
(2, 1, 'LINE-02', 'Through-Hole Wave Soldering Line 2', 85.00, 1),
(3, 1, 'LINE-03', 'Final Assembly & Packaging Line 3', 90.00, 1),
(4, 2, 'LINE-04', '5-Axis CNC Precision Milling Cell', 82.00, 1),
(5, 2, 'LINE-05', 'High-Tonnage Progressive Stamping Line', 86.00, 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ---------------------------------------------------------------------
-- Machines Seed Data (30 Machines: 6 per line)
-- ---------------------------------------------------------------------
INSERT INTO machines (id, line_id, machine_code, name, model, current_status, is_active) VALUES
-- Line 1 Machines (SMT)
(1, 1, 'M-001', 'Solder Paste Printer SP-1', 'Dek Horizon 03iX', 'RUNNING', 1),
(2, 1, 'M-002', '3D Solder Paste Inspector SPI-1', 'Koh Young KY8030-3', 'RUNNING', 1),
(3, 1, 'M-003', 'High-Speed Chip Placer CP-1', 'Fuji NXT III', 'RUNNING', 1),
(4, 1, 'M-004', 'Multi-Function Odd-Form Placer OF-1', 'Yamaha YSM20R', 'RUNNING', 1),
(5, 1, 'M-005', 'Nitrogen Reflow Oven RO-1', 'Heller 1913 MK5', 'RUNNING', 1),
(6, 1, 'M-006', 'Automated Optical Inspector AOI-1', 'Omron VT-S730', 'RUNNING', 1),

-- Line 2 Machines (Wave Soldering)
(7, 2, 'M-007', 'Radial Lead Inserter RI-1', 'Universal Instruments 6380B', 'RUNNING', 1),
(8, 2, 'M-008', 'Axial Component Inserter AI-1', 'Universal Instruments 6241F', 'RUNNING', 1),
(9, 2, 'M-009', 'Lead Trimmer & Former LT-1', 'Hepco 8000', 'IDLE', 1),
(10, 2, 'M-010', 'Dual-Wave Selective Soldering WS-1', 'Electrovert Electra 500', 'RUNNING', 1),
(11, 2, 'M-011', 'In-Line Deionized Board Washer BW-1', 'Aqueous Technologies Trident', 'RUNNING', 1),
(12, 2, 'M-012', 'X-Ray BGA Quality Station AXI-1', 'Nordson Dage Quadra 5', 'RUNNING', 1),

-- Line 3 Machines (Assembly & Pack)
(13, 3, 'M-013', 'Automated Screw Fastening Robot AR-1', 'Atlas Copco MicroTorque', 'RUNNING', 1),
(14, 3, 'M-014', 'Thermal Interface Dispenser TD-1', 'Nordson ASYMTEK Quantum', 'RUNNING', 1),
(15, 3, 'M-015', 'Ultrasonic Plastic Welder UW-1', 'Branson 2000X', 'RUNNING', 1),
(16, 3, 'M-016', 'Functional Circuit Tester FCT-1', 'Keysight i3070 Series 5', 'RUNNING', 1),
(17, 3, 'M-017', 'Laser Marking & Labeling LM-1', 'Trumpf TruMark 5000', 'RUNNING', 1),
(18, 3, 'M-018', 'Automated Case Erector & Pack PK-1', 'Lantech CI-1000', 'RUNNING', 1),

-- Line 4 Machines (CNC Milling)
(19, 4, 'M-019', 'CNC Vertical Machining Center VMC-1', 'Haas VF-4SS', 'RUNNING', 1),
(20, 4, 'M-020', 'CNC Horizontal Machining Center HMC-1', 'Makino a61nx', 'RUNNING', 1),
(21, 4, 'M-021', '5-Axis Simultaneous Mill 5AX-1', 'DMG MORI DMU 50', 'RUNNING', 1),
(22, 4, 'M-022', 'CNC Lathe & Turning Center TC-1', 'Mazak Quick Turn 250MSY', 'RUNNING', 1),
(23, 4, 'M-023', 'High-Pressure Precision Deburring DB-1', 'Sugino Jet-Clean Center', 'RUNNING', 1),
(24, 4, 'M-024', 'Coordinate Measuring Machine CMM-1', 'Zeiss CONTURA 9/12/8', 'RUNNING', 1),

-- Line 5 Machines (Stamping)
(25, 5, 'M-025', 'Hydraulic Blanking Press HP-1', 'Schuler Hydraulic 400T', 'RUNNING', 1),
(26, 5, 'M-026', 'Progressive Die Stamping Press PS-1', 'Minster E2 HeviStamper 300T', 'RUNNING', 1),
(27, 5, 'M-027', 'Automatic Coil Feeder & Straightener CF-1', 'Coe Press Feed Line', 'RUNNING', 1),
(28, 5, 'M-028', 'Tumble Finishing & Degreasing Station TF-1', 'Rosler R 320 EC', 'RUNNING', 1),
(29, 5, 'M-029', 'Continuous Heat Treat Annealing Oven HO-1', 'Surface Combustion Mesh Belt', 'RUNNING', 1),
(30, 5, 'M-030', 'Eddy Current Surface Flaw Detector EF-1', 'Foerster Defectomat CI', 'RUNNING', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ---------------------------------------------------------------------
-- Shifts Seed Data (3 Shifts per day)
-- ---------------------------------------------------------------------
INSERT INTO shifts (id, plant_id, shift_code, name, start_time, end_time, planned_break_minutes, is_active) VALUES
(1, 1, 'SHIFT-A', 'Morning Shift (06:00 - 14:00)', '06:00:00', '14:00:00', 60, 1),
(2, 1, 'SHIFT-B', 'Afternoon Shift (14:00 - 22:00)', '14:00:00', '22:00:00', 60, 1),
(3, 1, 'SHIFT-C', 'Night Shift (22:00 - 06:00)', '22:00:00', '06:00:00', 60, 1),
(4, 2, 'SHIFT-A', 'Morning Shift (06:00 - 14:00)', '06:00:00', '14:00:00', 60, 1),
(5, 2, 'SHIFT-B', 'Afternoon Shift (14:00 - 22:00)', '14:00:00', '22:00:00', 60, 1),
(6, 2, 'SHIFT-C', 'Night Shift (22:00 - 06:00)', '22:00:00', '06:00:00', 60, 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ---------------------------------------------------------------------
-- Products Seed Data (20 Products with Ideal Cycle Times in Seconds)
-- ---------------------------------------------------------------------
INSERT INTO products (id, product_code, name, category, ideal_cycle_time_seconds, unit_of_measure, is_active) VALUES
(1, 'PROD-001', 'Automotive ECU Control Unit v3', 'Electronics', 18.5000, 'pcs', 1),
(2, 'PROD-002', 'Industrial IoT Gateway Module', 'Electronics', 14.2000, 'pcs', 1),
(3, 'PROD-003', 'High-Torque BLDC Motor Driver Board', 'Power Electronics', 22.0000, 'pcs', 1),
(4, 'PROD-004', 'Medical Sensor Signal Conditioner', 'Medical', 28.0000, 'pcs', 1),
(5, 'PROD-005', 'EV Battery Management Slave Board', 'Automotive', 16.0000, 'pcs', 1),
(6, 'PROD-006', 'Precision Servo Actuator Housing', 'Mechanical', 35.0000, 'pcs', 1),
(7, 'PROD-007', 'Titanium Orthopedic Screw Implant', 'Medical', 45.0000, 'pcs', 1),
(8, 'PROD-008', 'Hydraulic Valve Spool Sleeve', 'Hydraulics', 30.0000, 'pcs', 1),
(9, 'PROD-009', 'Aerospace Bracket Alloy 7075-T6', 'Aerospace', 55.0000, 'pcs', 1),
(10, 'PROD-010', 'High-Pressure Fuel Injection Nozzle', 'Automotive', 40.0000, 'pcs', 1),
(11, 'PROD-011', 'Multi-Layer Copper Heat Sink Plate', 'Thermal', 12.5000, 'pcs', 1),
(12, 'PROD-012', 'Stainless Steel Stamped Sensor Shield', 'Stamping', 6.5000, 'pcs', 1),
(13, 'PROD-013', 'High-Speed Optical Transceiver Cage', 'Telecom', 8.0000, 'pcs', 1),
(14, 'PROD-014', 'Micro-Inverter Filter Choke Assembly', 'Renewable', 19.5000, 'pcs', 1),
(15, 'PROD-015', 'Radar Transceiver Front-End Board', 'Aerospace', 32.0000, 'pcs', 1),
(16, 'PROD-016', 'Pneumatic Manifold Block 4-Station', 'Pneumatics', 48.0000, 'pcs', 1),
(17, 'PROD-017', 'EMI Shielding Can Enclosure', 'Stamping', 5.0000, 'pcs', 1),
(18, 'PROD-018', 'Rugged Display Touch Controller PCB', 'Electronics', 17.5000, 'pcs', 1),
(19, 'PROD-019', 'Turbine Impeller Blade Segment', 'Aerospace', 65.0000, 'pcs', 1),
(20, 'PROD-020', 'Precision Ground Spur Gear Ring', 'Transmission', 38.0000, 'pcs', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ---------------------------------------------------------------------
-- Downtime Reasons Seed Data (Planned vs Unplanned)
-- ---------------------------------------------------------------------
INSERT INTO downtime_reasons (id, reason_code, category, name, description, is_planned, is_active) VALUES
(1, 'DTR-BRK-01', 'BREAK', 'Scheduled Meal / Shift Break', 'Standard 60-minute statutory operator lunch or dinner break', 1, 1),
(2, 'DTR-CHG-01', 'CHANGEOVER', 'Product Tooling & Feeder Changeover', 'Planned retooling, tape feeder setup, and solder stencil swap', 1, 1),
(3, 'DTR-MNT-01', 'MAINTENANCE', 'Preventive Scheduled Maintenance', 'Weekly calibration, nozzle inspection, lubrication, filter check', 1, 1),
(4, 'DTR-MNT-02', 'MAINTENANCE', 'Autonomous Maintenance & Cleaning', 'Operator 5S cleaning and line hygiene routine', 1, 1),
(5, 'DTR-JAM-01', 'UNPLANNED_DOWNTIME', 'Component Feeder Jam', 'Part tape jammed in feeder rack or mechanical pick error', 0, 1),
(6, 'DTR-MEC-01', 'UNPLANNED_DOWNTIME', 'Mechanical Drive / Spindle Failure', 'Drive motor, belt breakage, pneumatic drop or axis failure', 0, 1),
(7, 'DTR-ELE-01', 'UNPLANNED_DOWNTIME', 'Sensor / Vision System Fault', 'Camera calibration fault, optical error, safety curtain tripped', 0, 1),
(8, 'DTR-MAT-01', 'UNPLANNED_DOWNTIME', 'Raw Material Starvation', 'Upstream inventory depleted or delayed delivery to workstation', 0, 1),
(9, 'DTR-TMP-01', 'UNPLANNED_DOWNTIME', 'Process Temperature Out-of-Spec', 'Reflow thermal runaway or chiller cooling malfunction', 0, 1),
(10, 'DTR-ENV-01', 'UNPLANNED_DOWNTIME', 'Facility Power Surge / Utility Interruption', 'Compressed air drop or plant electrical voltage dip', 0, 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);
