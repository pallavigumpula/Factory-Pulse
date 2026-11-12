# FactoryPulse — Synthetic Manufacturing Dataset Methodology

## 1. Objective and Determinism
The FactoryPulse synthetic data generator simulates real-world telemetry and MES (Manufacturing Execution System) transaction logs across multi-stage discrete manufacturing.

To ensure 100% scientific reproducibility:
- **Seed**: `20261022`
- **Pseudorandom Generation**: Python's standard `random.Random(20261022)` and `numpy.random.default_rng(20261022)`.
- Idempotent and deterministic: Running the generator with identical arguments guarantees byte-for-byte identical output datasets, record counts, and checksums.

---

## 2. Dataset Modes

| Parameter | Starter Mode (Development/Testing) | Full Mode (Benchmark Scale) |
|---|---|---|
| Plants | 2 Plants | 2 Plants |
| Production Lines | 5 Lines | 5 Lines |
| Active Machines | 30 Machines (6 per line) | 30 Machines (6 per line) |
| Product Catalog | 20 Products | 20 Products |
| Timeline Horizon | 5 Days (15 shifts) | 90 Days (270 shifts) |
| Shifts per Day | 3 Shifts (Morning, Afternoon, Night) | 3 Shifts (Morning, Afternoon, Night) |
| Machine State Events | ~2,500 events | 100,000+ events |
| Counts & Inspections | ~6,000 records | 500,000+ records |
| Generation Runtime | < 10 seconds | ~60 seconds (bulk buffered batches) |

---

## 3. Operational Simulation Engine

1. **Shift Schedule**:
   - Shift A: 06:00 – 14:00 (Break at 11:30 – 12:30)
   - Shift B: 14:00 – 22:00 (Break at 17:30 – 18:30)
   - Shift C: 22:00 – 06:00 (Break at 01:30 – 02:30)
2. **State Event Sequencing**:
   - `RUNNING`: Major operational phase (70–85% duration).
   - `BREAK`: Exactly aligns with shift planned break.
   - `CHANGEOVER`: Scheduled between product transitions.
   - `MAINTENANCE`: Preventive weekly maintenance windows.
   - `STOPPED`: Random Poisson micro-stops (1–5 min) and component jams.
3. **Discrete Count Generation**:
   - Yield conforms to ideal cycle time with realistic minor variance.
   - Split: ~95% `GOOD`, ~3.5% `SCRAP`, ~1.5% `REWORK`.
   - Traceable `CORRECTION` events generated with reference count IDs.
4. **Anomaly Injection & Ground Truth Separation**:
   - Anomaly types injected deterministically:
     1. Overlapping machine state timestamps.
     2. Negative quantities logged under non-correction count types.
     3. Quality inspections where defect count exceeds sample size.
     4. Zero / negative ideal cycle times.
     5. Unplanned breakdown logs overlapping statutory shift breaks.
   - Labels are written strictly to `data/ground_truth.json` and `data/ground_truth.csv` without exposing flags to the runtime detection algorithm.
