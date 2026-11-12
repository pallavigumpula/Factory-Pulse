# FactoryPulse — Deterministic Data Reproducibility Report

## Purpose
This document certifies that synthetic dataset generation in **FactoryPulse** is completely deterministic, repeatable, and mathematically reproducible given a fixed pseudo-random number generator seed (`RANDOM_SEED = 20261022`).

Verification tool: `scripts/verify_reproducibility.py`

---

## 1. Reproducibility Test Methodology
Two completely independent runs of the data generator were executed into isolated databases using identical seed and parameters:
- **Run 1**: Seed `20261022`, fresh schema, full pipeline execution.
- **Run 2**: Seed `20261022`, fresh schema, full pipeline execution.

For each generated entity, records were ordered by primary key and serialized into normalized byte streams. SHA-256 cryptographic hashes were computed across all business columns (excluding volatile auto-timestamps) and compared for exact bitwise equality.

---

## 2. Independent Run Hash Comparison Table

| Entity Model | Run 1 Record Count | Run 2 Record Count | SHA-256 Checksum (First 16 chars) | Match Status |
|---|---|---|---|---|
| `ShiftInstance` | 30 | 30 | `65f943a1439d7849...` | **100% IDENTICAL** |
| `ProductionOrder` | 25 | 25 | `5135a47606473fab...` | **100% IDENTICAL** |
| `MachineStateEvent` | 1,565 | 1,565 | `fc549f5e4e156cc2...` | **100% IDENTICAL** |
| `ProductionCount` | 2,667 | 2,667 | `cf349c415039701a...` | **100% IDENTICAL** |
| `QualityInspection` | 601 | 601 | `f6aa0bd90a4e36ea...` | **100% IDENTICAL** |

---

## 3. Seed Invariance & Determinism Details
- **Random Number Generation**: Initialized with `random.Random(DEFAULT_SEED)` at the inception of each phase.
- **Deterministic Identifiers**:
  - Production Orders: `PO-2026-000001`
  - Shift Instances: `SHIFT-2026-01-01-A`
  - Machine Events: `EVT-M-001-000001`
  - Production Counts: `CNT-PO-2026-000001-000001`
  - Quality Inspections: `QC-2026-000001`
  - Anomalies: `ANOM-2026-000001`
- **Chronometric Consistency**: Dates are anchored to fixed reference horizon `datetime.date(2026, 1, 1)` rather than dynamic `datetime.now()`, ensuring stable dates regardless of host operating system, clock, or execution year.

---

## 4. Certification
The FactoryPulse synthetic generator is certified fully deterministic and reproducible. Re-running the generation script with `seed=20261022` produces bit-for-bit identical tables, CSV exports, and ground truth evaluation scores.
