# FactoryPulse — Anomaly Detection Methodology & Evaluation

## 1. Overview
The Anomaly Detection Engine scans manufacturing execution data for sensor faults, operational violations, scheduling conflicts, and data integrity corruption without modifying raw database records.

---

## 2. Core Anomaly Rules

### Rule 1: Overlapping Machine-State Events
- **Definition**: Telemetry records two distinct operational states for the same physical machine at the same timestamp.
- **Expected Condition**: For any machine \(M\) and events \(e_1, e_2\), \(e_1.\text{end\_time} \le e_2.\text{start\_time}\).
- **Severity**: `HIGH`
- **Recommended Action**: Inspect edge PLC telemetry clock synchronization and verify sensor debounce timing.

### Rule 2: Unjustified Production Count Drop
- **Definition**: Sequential production counts decrease without an explicit `CORRECTION` event linking to the source record.
- **Expected Condition**: Cumulative produced count must monotonically increase unless accompanied by an auditable `count_type = 'CORRECTION'` record.
- **Severity**: `CRITICAL`
- **Recommended Action**: Enforce traceability constraints; require operators to submit count adjustments through the `/production-counts/correct` endpoint.

### Rule 3: Scrap Quantity Exceeding Total Production
- **Definition**: Discrete scrap count or rejected unit count is strictly greater than the recorded batch production size.
- **Expected Condition**: \(\text{Scrap Count} \le \text{Total Production Count}\).
- **Severity**: `CRITICAL`
- **Recommended Action**: Quarantine batch for re-inspection; audit operator manual counting entries.

### Rule 4: Incorrect / Discordant Ideal Cycle Time
- **Definition**: Product ideal cycle time is recorded as non-positive (\(\le 0\)) or machine operating speed exceeds theoretical physics limit by \(> 300\%\), signifying erroneous BOM setup.
- **Expected Condition**: \(\text{Ideal Cycle Time} > 0\) and \(\text{Performance} \le 125\%\).
- **Severity**: `MEDIUM`
- **Recommended Action**: Review Master Production Schedule (MPS) and re-benchmark product engineering time study.

### Rule 5: Downtime Overlapping Planned Shift Break
- **Definition**: An unplanned stoppage or breakdown is reported concurrently during a statutory planned shift break.
- **Expected Condition**: Equipment during scheduled break must be tagged with `BREAK` state; unplanned downtime must not double-charge availability during non-working statutory pauses.
- **Severity**: `MEDIUM`
- **Recommended Action**: Adjust downtime timestamps to pause during lunch/shift breaks or reclassify reason code.

---

## 3. Evaluation Metrics Against Ground Truth

Evaluation compares purely algorithmic detection against independently maintained ground-truth test labels (`ground_truth.json` / `ground_truth.csv`):

$$\text{Precision} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Positives (FP)}}$$

$$\text{Recall} = \frac{\text{True Positives (TP)}}{\text{True Positives (TP)} + \text{False Negatives (FN)}}$$

$$F_1\text{-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
