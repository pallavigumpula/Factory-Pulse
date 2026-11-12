# FactoryPulse — OEE Calculation Methodology & Formulas

## 1. Executive Summary

Overall Equipment Effectiveness (OEE) is the gold standard for measuring manufacturing productivity. **FactoryPulse** calculates OEE strictly from empirical machine state events, discrete production counts, shift definitions, and quality inspection records stored in MySQL.

---

## 2. Core Mathematical Formulas

### 2.1 Availability (\(A\))
Availability measures the proportion of planned operating time that the equipment is actually running without stoppages.

$$\text{Availability} = \frac{\text{Operating Time}}{\text{Planned Production Time}} \times 100\%$$

Where:
- **Shift Duration**: Standard 8 hours (480 minutes).
- **Planned Breaks**: Statutory meal and rest intervals (60 minutes per shift).
- **Planned Production Time (PPT)**:
  $$\text{PPT} = \text{Shift Duration} - \text{Planned Breaks}$$
  For a standard 8-hour shift with 60 min break, \(\text{PPT} = 420 \text{ minutes}\).
- **Operating Time**:
  $$\text{Operating Time} = \sum_{\text{state}=\text{RUNNING}} \text{Duration}(\text{event})$$
  Excludes all Unplanned Downtime (equipment breakdown, feeder jam, sensor fault) and Planned Loss (tooling changeovers, preventive maintenance).

---

### 2.2 Performance (\(P\))
Performance measures the operating speed of the machine against its theoretical maximum design speed.

$$\text{Performance} = \frac{\text{Ideal Cycle Time} \times \text{Total Production Count}}{\text{Operating Time}} \times 100\%$$

Where:
- **Ideal Cycle Time (\(T_{\text{ideal}}\))**: Theoretical minimum time (in seconds) required to produce one unit under optimal conditions.
- **Total Production Count (\(N_{\text{total}}\))**: Net sum of all pieces produced during the interval:
  $$N_{\text{total}} = N_{\text{good}} + N_{\text{scrap}} + N_{\text{rework}} + \Delta N_{\text{corrections}}$$
- **Operating Time in Seconds**: \(\text{Operating Time (minutes)} \times 60\).
- **Over-Performance Flagging**: If \(P > 100.0\%\), the record is explicitly flagged as `performance_flagged = TRUE` to alert planners that the ideal cycle time is either configured too conservatively or counts are misattributed.

---

### 2.3 Quality (\(Q\))
Quality evaluates the proportion of manufactured parts that meet customer engineering specifications on first pass.

$$\text{Quality} = \frac{\text{Good Production Count}}{\text{Total Production Count}} \times 100\%$$

Where:
- **Good Production Count (\(N_{\text{good}}\))**: First-pass conforming units.
- **Scrap (\(N_{\text{scrap}}\))**: Non-conforming units rejected and discarded.
- **Rework (\(N_{\text{rework}}\))**: Items needing secondary processing.

---

### 2.4 Overall Equipment Effectiveness (OEE)
OEE is the composite multiplicative metric of the three underlying dimensions.

$$\text{OEE} = \left(\frac{\text{Availability}}{100}\right) \times \left(\frac{\text{Performance}}{100}\right) \times \left(\frac{\text{Quality}}{100}\right) \times 100\%$$

*Note: The calculation engine computes decimal ratios internally to prevent compounding roundoff errors before expressing the final result as a percentage.*

---

## 3. Calculation Assumptions & Edge Case Handling

1. **Division by Zero Protection**:
   - If \(\text{PPT} \le 0\), Availability is set to `0.0%`.
   - If \(\text{Operating Time} \le 0\), Performance is set to `0.0%`.
   - If \(N_{\text{total}} \le 0\), Quality is set to `100.0%` (if machine did not run) or `0.0%` if reported scrap exists, preventing NaN errors.
2. **Planned Downtime vs. Unplanned Downtime**:
   - **Planned Breaks**: Statutory 60-minute shift breaks are subtracted from total shift time to yield Planned Production Time.
   - **Planned Maintenance & Changeovers**: Included in PPT but reduce Operating Time, directly impacting Availability unless specifically excluded via non-scheduled status.
   - **Unplanned Stoppages**: Direct losses against Availability.
3. **Overlapping State Events Elimination**:
   - In industrial telemetry, sensor glitches or conflicting operator logs can produce overlapping intervals. The FactoryPulse OEE Engine parses intervals chronologically and merges overlaps to prevent double-counting machine time.
4. **Hierarchical Rollups**:
   - Machine \(\rightarrow\) Production Line \(\rightarrow\) Shift \(\rightarrow\) Product \(\rightarrow\) Plant.
   - Aggregations are calculated from the bottom-up sum of actual operating seconds and counts, rather than an unweighted average of individual percentage figures.
