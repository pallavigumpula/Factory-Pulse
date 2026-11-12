# FactoryPulse — Data Dictionary

This data dictionary outlines all tables, fields, data types, constraints, default values, units, and functional descriptions for the **FactoryPulse** platform.

---

## 1. Table: `users`
System user accounts and role assignments.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Unique user record surrogate key |
| `username` | VARCHAR(50) | NO | None | UNIQUE, INDEX | Unique handle for login |
| `email` | VARCHAR(100) | NO | None | UNIQUE | Corporate email address |
| `password_hash` | VARCHAR(255) | NO | None | | PBKDF2-HMAC-SHA256 salted hash string |
| `full_name` | VARCHAR(100) | NO | None | | User's human full display name |
| `role` | ENUM | NO | None | ADMIN, OPERATOR, MAINTENANCE, QUALITY, PLANNER | Authorization permission role |
| `is_active` | BOOLEAN | NO | 1 (TRUE) | | Account active / suspended toggle |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Timestamp when account was created |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Timestamp of last modification |

---

## 2. Table: `plants`
Physical manufacturing sites and geographical facilities.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Plant surrogate key |
| `plant_code` | VARCHAR(50) | NO | None | UNIQUE, INDEX | Business key (e.g., `PLANT-01`) |
| `name` | VARCHAR(100) | NO | None | | Full plant name |
| `location` | VARCHAR(150) | YES | NULL | | Physical address / city / state |
| `timezone` | VARCHAR(50) | NO | 'UTC' | | IANA standard timezone string |
| `is_active` | BOOLEAN | NO | 1 (TRUE) | | Active facility flag |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Last update timestamp |

---

## 3. Table: `production_lines`
Distinct production and assembly lines within a plant.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Line surrogate key |
| `plant_id` | INT | NO | None | FK -> `plants(id)` | Parent manufacturing plant |
| `line_code` | VARCHAR(50) | NO | None | UNIQUE, INDEX | Business key (e.g., `LINE-01`) |
| `name` | VARCHAR(100) | NO | None | | Line descriptive title |
| `target_oee` | DECIMAL(5,2) | NO | 85.00 | Unit: % | Target benchmark OEE percentage |
| `is_active` | BOOLEAN | NO | 1 (TRUE) | | Line operational status flag |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Record creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Record update timestamp |

---

## 4. Table: `machines`
Individual industrial equipment and work centers situated on lines.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Machine surrogate key |
| `line_id` | INT | NO | None | FK -> `production_lines(id)` | Parent production line |
| `machine_code` | VARCHAR(50) | NO | None | UNIQUE, INDEX | Equipment code (e.g., `M-001`) |
| `name` | VARCHAR(100) | NO | None | | Human readable machine name |
| `model` | VARCHAR(100) | YES | NULL | | Equipment OEM make and model |
| `current_status` | ENUM | NO | 'IDLE' | RUNNING, STOPPED, IDLE, CHANGEOVER, MAINTENANCE, BREAK | Real-time operational state |
| `is_active` | BOOLEAN | NO | 1 (TRUE) | | Machine enabled status |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Modification timestamp |

---

## 5. Table: `shifts`
Operating shifts and schedules per plant.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Shift surrogate key |
| `plant_id` | INT | NO | None | FK -> `plants(id)` | Associated plant facility |
| `shift_code` | VARCHAR(50) | NO | None | UNIQUE(plant_id, shift_code) | Shift identifier (e.g. `SHIFT-A`) |
| `name` | VARCHAR(50) | NO | None | | Shift name (Morning, Afternoon, Night) |
| `start_time` | TIME | NO | None | | Shift start time of day |
| `end_time` | TIME | NO | None | | Shift end time of day |
| `planned_break_minutes` | INT | NO | 60 | Unit: minutes | Statutory unpaid / scheduled break time |
| `is_active` | BOOLEAN | NO | 1 (TRUE) | | Active shift schedule indicator |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Last update timestamp |

---

## 6. Table: `products`
Manufactured goods, SKUs, and standard cycle time specifications.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Product surrogate key |
| `product_code` | VARCHAR(50) | NO | None | UNIQUE, INDEX | SKU code (e.g. `PROD-001`) |
| `name` | VARCHAR(100) | NO | None | | Product commercial name |
| `category` | VARCHAR(50) | YES | NULL | | Product family / classification |
| `ideal_cycle_time_seconds` | DECIMAL(10,4) | NO | None | Unit: seconds/unit | Theoretical minimum time to produce 1 unit |
| `unit_of_measure` | VARCHAR(20) | NO | 'units' | | Quantity unit (e.g. 'pcs', 'units') |
| `is_active` | BOOLEAN | NO | 1 (TRUE) | | Catalog active flag |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Modification timestamp |

---

## 7. Table: `downtime_reasons`
Standardized categorization taxonomy for machine stoppages and planned losses.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Reason surrogate key |
| `reason_code` | VARCHAR(50) | NO | None | UNIQUE, INDEX | Code (e.g., `DTR-JAM-01`) |
| `category` | ENUM | NO | None | UNPLANNED_DOWNTIME, PLANNED_DOWNTIME, BREAK, CHANGEOVER, MAINTENANCE | High-level categorization |
| `name` | VARCHAR(100) | NO | None | | Reason name |
| `description` | TEXT | YES | NULL | | Detailed engineering description |
| `is_planned` | BOOLEAN | NO | 0 (FALSE) | | True if planned loss, False if unplanned |
| `is_active` | BOOLEAN | NO | 1 (TRUE) | | Active selection flag |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Modification timestamp |

---

## 8. Table: `production_orders`
Scheduled manufacturing work orders assigned to lines.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Order surrogate key |
| `order_code` | VARCHAR(50) | NO | None | UNIQUE, INDEX | Format: `PO-YYYY-NNNNNN` |
| `line_id` | INT | NO | None | FK -> `production_lines(id)` | Target production line |
| `product_id` | INT | NO | None | FK -> `products(id)` | Target manufactured product |
| `target_quantity` | INT | NO | None | Unit: units | Planned production batch count |
| `produced_quantity` | INT | NO | 0 | Unit: units | Cumulative good items completed |
| `status` | ENUM | NO | 'PLANNED' | PLANNED, IN_PROGRESS, COMPLETED, ON_HOLD, CANCELLED | Production order lifecycle state |
| `start_time` | DATETIME | YES | NULL | | Work order execution start |
| `end_time` | DATETIME | YES | NULL | | Work order execution completion |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Record timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Modification timestamp |

---

## 9. Table: `machine_state_events`
Chronological state transition logs for all machines.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | State event surrogate key |
| `event_code` | VARCHAR(60) | NO | None | UNIQUE | Format: `EVT-M001-NNNNNN` |
| `machine_id` | INT | NO | None | FK -> `machines(id)` | Machine experiencing event |
| `production_order_id`| INT | YES | NULL | FK -> `production_orders(id)` | Associated PO in progress |
| `shift_id` | INT | YES | NULL | FK -> `shifts(id)` | Associated shift |
| `state` | ENUM | NO | None | RUNNING, STOPPED, IDLE, CHANGEOVER, MAINTENANCE, BREAK | Operational machine state |
| `start_time` | DATETIME | NO | None | | Start timestamp of event |
| `end_time` | DATETIME | NO | None | | End timestamp of event |
| `duration_seconds` | INT | NO | None | Unit: seconds | Duration of continuous state |
| `downtime_reason_id`| INT | YES | NULL | FK -> `downtime_reasons(id)` | Downtime root cause classification |
| `notes` | TEXT | YES | NULL | | Technician / operator logs |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Insertion timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Modification timestamp |

---

## 10. Table: `production_counts`
Discrete production counts and audit trail of corrections.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Count record surrogate key |
| `count_code` | VARCHAR(60) | NO | None | UNIQUE | Format: `CNT-PO000001-NNNNNN` |
| `production_order_id`| INT | NO | None | FK -> `production_orders(id)` | Associated order |
| `machine_id` | INT | NO | None | FK -> `machines(id)` | Machine producing items |
| `shift_id` | INT | YES | NULL | FK -> `shifts(id)` | Active shift |
| `product_id` | INT | NO | None | FK -> `products(id)` | Product SKU |
| `count_type` | ENUM | NO | None | GOOD, SCRAP, REWORK, CORRECTION | Type of count event |
| `quantity` | INT | NO | None | Unit: units | Units produced or adjusted |
| `timestamp` | DATETIME | NO | None | | Time recorded |
| `operator_id` | INT | YES | NULL | FK -> `users(id)` | Operator entering count |
| `reference_count_id` | INT | YES | NULL | FK -> `production_counts(id)` | Traceable reference for CORRECTION |
| `reason` | VARCHAR(255) | YES | NULL | | Justification for correction |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Insertion timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Modification timestamp |

---

## 11. Table: `quality_inspections`
Quality control inspections and defect audits.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Inspection surrogate key |
| `inspection_code` | VARCHAR(60) | NO | None | UNIQUE | Format: `QC-YYYY-NNNNNN` |
| `production_order_id`| INT | NO | None | FK -> `production_orders(id)` | Target production batch |
| `machine_id` | INT | NO | None | FK -> `machines(id)` | Machine inspected |
| `shift_id` | INT | YES | NULL | FK -> `shifts(id)` | Active shift |
| `sample_size` | INT | NO | None | Unit: units | Total parts inspected |
| `passed_count` | INT | NO | None | Unit: units | Good parts conforming to spec |
| `failed_count` | INT | NO | None | Unit: units | Defective parts |
| `defect_type` | VARCHAR(100) | YES | NULL | | Defect taxonomy classification |
| `inspector_id` | INT | YES | NULL | FK -> `users(id)` | Quality engineer |
| `timestamp` | DATETIME | NO | None | | Inspection test timestamp |
| `status` | ENUM | NO | None | PASSED, FAILED, CONDITIONAL | Inspection outcome |
| `notes` | TEXT | YES | NULL | | Observations & corrective measures |
| `created_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Creation timestamp |
| `updated_at` | DATETIME | NO | CURRENT_TIMESTAMP ON UPDATE | | Modification timestamp |

---

## 12. Table: `oee_aggregates`
Aggregated OEE KPIs calculated and cached across dimensions.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Aggregate surrogate key |
| `aggregation_level` | ENUM | NO | None | MACHINE, LINE, SHIFT, PRODUCT, PLANT | Hierarchy level |
| `entity_id` | INT | NO | None | | ID of machine, line, plant, etc. |
| `entity_code` | VARCHAR(50) | NO | None | | Human readable entity code |
| `date` | DATE | NO | None | | Calendar date of aggregation |
| `shift_id` | INT | YES | NULL | | Specific shift or NULL for daily |
| `planned_production_time_minutes` | DECIMAL(10,2) | NO | 0.00 | Unit: minutes | Total shift time minus planned breaks |
| `operating_time_minutes` | DECIMAL(10,2) | NO | 0.00 | Unit: minutes | Actual time running |
| `planned_downtime_minutes` | DECIMAL(10,2) | NO | 0.00 | Unit: minutes | Retooling, planned PM |
| `unplanned_downtime_minutes` | DECIMAL(10,2) | NO | 0.00 | Unit: minutes | Breakdowns, micro-stops |
| `ideal_cycle_time_seconds` | DECIMAL(10,4) | NO | 0.0000 | Unit: seconds | Baseline theoretical cycle time |
| `total_count` | INT | NO | 0 | Unit: units | Good + Scrap + Rework |
| `good_count` | INT | NO | 0 | Unit: units | Conforming parts |
| `scrap_count` | INT | NO | 0 | Unit: units | Non-conforming discarded parts |
| `rework_count` | INT | NO | 0 | Unit: units | Items needing rework |
| `availability` | DECIMAL(6,4) | NO | 0.0000 | Unit: ratio (0.0000 - 1.0000) or % | Operating / Planned Time |
| `performance` | DECIMAL(6,4) | NO | 0.0000 | Unit: ratio (0.0000 - 1.0000+) | (Ideal Cycle * Total) / Operating |
| `quality` | DECIMAL(6,4) | NO | 0.0000 | Unit: ratio (0.0000 - 1.0000) | Good / Total Count |
| `oee` | DECIMAL(6,4) | NO | 0.0000 | Unit: ratio (0.0000 - 1.0000) | Availability * Performance * Quality |
| `performance_flagged` | BOOLEAN | NO | 0 (FALSE) | | True if Performance > 100% |
| `calculated_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Calculation run timestamp |

---

## 13. Table: `detected_anomalies`
Identified operational and data consistency anomalies with audit details.

| Field | Data Type | Nullable | Default | Constraints | Description |
|---|---|---|---|---|---|
| `id` | INT | NO | AUTO_INCREMENT | PK | Anomaly surrogate key |
| `anomaly_code` | VARCHAR(60) | NO | None | UNIQUE | Format: `ANOM-YYYY-NNNNNN` |
| `anomaly_type` | VARCHAR(100) | NO | None | | Specific rule violated |
| `entity_type` | VARCHAR(50) | NO | None | | Target entity (MACHINE, PO, etc.) |
| `entity_id` | VARCHAR(100) | NO | None | | Target entity identifier |
| `timestamp` | DATETIME | NO | None | | Timestamp anomaly occurred |
| `severity` | ENUM | NO | None | CRITICAL, HIGH, MEDIUM, LOW | Severity classification |
| `description` | TEXT | NO | None | | Plain English description |
| `expected_value` | VARCHAR(255) | NO | None | | Baseline or expected state |
| `actual_value` | VARCHAR(255) | NO | None | | Recorded anomalous state |
| `recommended_action`| TEXT | NO | None | | Prescribed engineering resolution |
| `resolution_status` | ENUM | NO | 'OPEN' | OPEN, INVESTIGATING, RESOLVED, FALSE_POSITIVE | Remediation workflow status |
| `detected_at` | DATETIME | NO | CURRENT_TIMESTAMP | | Timestamp detected |
| `resolved_at` | DATETIME | YES | NULL | | Timestamp resolved |
