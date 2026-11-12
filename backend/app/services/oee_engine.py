import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from backend.app.models.master_data import Machine, ProductionLine, Shift, Product, Plant, DowntimeReason
from backend.app.models.production import MachineStateEvent, ProductionCount, ProductionOrder, OEEAggregate

def merge_time_intervals(intervals: List[Tuple[datetime.datetime, datetime.datetime]]) -> List[Tuple[datetime.datetime, datetime.datetime]]:
    """
    Merges overlapping or contiguous time intervals to prevent double-counting duration.
    """
    if not intervals:
        return []
    # Filter valid intervals
    valid = sorted([ (s, e) for s, e in intervals if e > s ], key=lambda x: x[0])
    if not valid:
        return []
    
    merged = [valid[0]]
    for current_start, current_end in valid[1:]:
        prev_start, prev_end = merged[-1]
        if current_start <= prev_end:
            # Overlap or adjacent: extend previous end if current_end is later
            merged[-1] = (prev_start, max(prev_end, current_end))
        else:
            merged.append((current_start, current_end))
    return merged

def calculate_merged_seconds(intervals: List[Tuple[datetime.datetime, datetime.datetime]]) -> float:
    """Calculates total duration in seconds from non-overlapping intervals."""
    merged = merge_time_intervals(intervals)
    return sum((end - start).total_seconds() for start, end in merged)

class OEEEngine:
    """
    Deterministic OEE Calculation Engine.
    Executes calculations directly against database records with edge-case protections.
    """

    @staticmethod
    def calculate_machine_oee(
        db: Session,
        machine_id: int,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        planned_production_time_minutes: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates OEE for an individual machine across a time window.
        """
        machine = db.query(Machine).filter(Machine.id == machine_id).first()
        if not machine:
            raise ValueError(f"Machine with id {machine_id} does not exist")

        # 1. State events within the window
        events = db.query(MachineStateEvent).filter(
            MachineStateEvent.machine_id == machine_id,
            MachineStateEvent.start_time < end_time,
            MachineStateEvent.end_time > start_time
        ).all()

        running_intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []
        unplanned_intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []
        planned_dt_intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []
        break_intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []

        for evt in events:
            # Clip event boundaries to the analysis window
            act_start = max(evt.start_time, start_time)
            act_end = min(evt.end_time, end_time)
            if act_end <= act_start:
                continue

            span = (act_start, act_end)
            if evt.state == "RUNNING":
                running_intervals.append(span)
            elif evt.state in ("STOPPED", "IDLE"):
                unplanned_intervals.append(span)
            elif evt.state in ("CHANGEOVER", "MAINTENANCE"):
                planned_dt_intervals.append(span)
            elif evt.state == "BREAK":
                break_intervals.append(span)

        operating_seconds = calculate_merged_seconds(running_intervals)
        unplanned_dt_seconds = calculate_merged_seconds(unplanned_intervals)
        planned_dt_seconds = calculate_merged_seconds(planned_dt_intervals)
        break_seconds = calculate_merged_seconds(break_intervals)

        total_window_seconds = (end_time - start_time).total_seconds()

        # If planned production time is not explicitly passed, define PPT = total_window_seconds - break_seconds
        if planned_production_time_minutes is not None:
            ppt_seconds = max(0.0, planned_production_time_minutes * 60.0)
        else:
            ppt_seconds = max(0.0, total_window_seconds - break_seconds)

        # 2. Production counts within the window
        counts = db.query(ProductionCount).filter(
            ProductionCount.machine_id == machine_id,
            ProductionCount.timestamp >= start_time,
            ProductionCount.timestamp <= end_time
        ).all()

        good_count = 0
        scrap_count = 0
        rework_count = 0
        correction_delta = 0
        products_weight: Dict[int, int] = {}

        for c in counts:
            if c.count_type == "GOOD":
                good_count += c.quantity
                products_weight[c.product_id] = products_weight.get(c.product_id, 0) + c.quantity
            elif c.count_type == "SCRAP":
                scrap_count += c.quantity
                products_weight[c.product_id] = products_weight.get(c.product_id, 0) + c.quantity
            elif c.count_type == "REWORK":
                rework_count += c.quantity
                products_weight[c.product_id] = products_weight.get(c.product_id, 0) + c.quantity
            elif c.count_type == "CORRECTION":
                correction_delta += c.quantity
                # Adjust good count by correction
                good_count += c.quantity

        good_count = max(0, good_count)
        total_count = max(0, good_count + scrap_count + rework_count)

        # 3. Determine ideal cycle time (seconds)
        # Weighted by production volume per product
        ideal_cycle_time_seconds = 20.0 # fallback default
        if products_weight:
            total_weighted_sec = 0.0
            sum_qty = 0
            for prod_id, qty in products_weight.items():
                p = db.query(Product).filter(Product.id == prod_id).first()
                if p:
                    cyc = float(p.ideal_cycle_time_seconds)
                    total_weighted_sec += cyc * qty
                    sum_qty += qty
            if sum_qty > 0:
                ideal_cycle_time_seconds = total_weighted_sec / sum_qty
        else:
            # Check latest PO for machine
            latest_po = db.query(ProductionOrder).filter(
                ProductionOrder.line_id == machine.line_id
            ).order_by(ProductionOrder.id.desc()).first()
            if latest_po and latest_po.product:
                ideal_cycle_time_seconds = float(latest_po.product.ideal_cycle_time_seconds)

        # 4. Availability = Operating Time / Planned Production Time * 100
        if ppt_seconds > 0:
            availability_ratio = min(1.0, operating_seconds / ppt_seconds)
        else:
            availability_ratio = 0.0

        # 5. Performance = (Ideal Cycle Time * Total Count) / Operating Time * 100
        performance_flagged = False
        if operating_seconds > 0:
            performance_ratio = (ideal_cycle_time_seconds * total_count) / operating_seconds
            if performance_ratio > 1.0:
                performance_flagged = True
        else:
            performance_ratio = 0.0

        # 6. Quality = Good Count / Total Count * 100
        if total_count > 0:
            quality_ratio = good_count / total_count
        else:
            quality_ratio = 1.0 if operating_seconds == 0 else 0.0

        # 7. OEE = Availability * Performance * Quality (decimal multiplication)
        # We cap performance in composite OEE at 1.0 to keep OEE mathematically bounded between 0 and 100%
        bounded_perf = min(1.0, performance_ratio)
        oee_ratio = availability_ratio * bounded_perf * quality_ratio

        return {
            "machine_id": machine.id,
            "machine_code": machine.machine_code,
            "machine_name": machine.name,
            "planned_production_time_minutes": round(ppt_seconds / 60.0, 2),
            "operating_time_minutes": round(operating_seconds / 60.0, 2),
            "planned_downtime_minutes": round(planned_dt_seconds / 60.0, 2),
            "unplanned_downtime_minutes": round(unplanned_dt_seconds / 60.0, 2),
            "ideal_cycle_time_seconds": round(ideal_cycle_time_seconds, 4),
            "total_count": total_count,
            "good_count": good_count,
            "scrap_count": scrap_count,
            "rework_count": rework_count,
            "availability": round(availability_ratio * 100.0, 2),
            "performance": round(performance_ratio * 100.0, 2),
            "quality": round(quality_ratio * 100.0, 2),
            "oee": round(oee_ratio * 100.0, 2),
            "performance_flagged": performance_flagged,
            "assumptions": [
                "Planned breaks are deducted from total window time to yield Planned Production Time.",
                "Overlapping state intervals are merged to avoid duplicate time accounting.",
                "Performance values > 100% are flagged for review and bounded to 100% in composite OEE.",
                "Calculated directly from discrete database records."
            ]
        }

    @staticmethod
    def calculate_line_oee(
        db: Session,
        line_id: int,
        start_time: datetime.datetime,
        end_time: datetime.datetime
    ) -> Dict[str, Any]:
        """Calculates line level aggregation from constituent machines."""
        line = db.query(ProductionLine).filter(ProductionLine.id == line_id).first()
        if not line:
            raise ValueError(f"Line {line_id} not found")
        machines = db.query(Machine).filter(Machine.line_id == line_id, Machine.is_active == True).all()
        if not machines:
            return {
                "line_id": line.id,
                "line_code": line.line_code,
                "name": line.name,
                "oee": 0.0,
                "availability": 0.0,
                "performance": 0.0,
                "quality": 0.0
            }

        machine_results = [
            OEEEngine.calculate_machine_oee(db, m.id, start_time, end_time)
            for m in machines
        ]

        total_ppt = sum(r["planned_production_time_minutes"] for r in machine_results)
        total_opt = sum(r["operating_time_minutes"] for r in machine_results)
        total_p_dt = sum(r["planned_downtime_minutes"] for r in machine_results)
        total_u_dt = sum(r["unplanned_downtime_minutes"] for r in machine_results)
        total_cnt = sum(r["total_count"] for r in machine_results)
        total_good = sum(r["good_count"] for r in machine_results)
        total_scrap = sum(r["scrap_count"] for r in machine_results)
        total_rework = sum(r["rework_count"] for r in machine_results)

        # Weighted availability
        avail = (total_opt / total_ppt * 100.0) if total_ppt > 0 else 0.0
        # Weighted quality
        qual = (total_good / total_cnt * 100.0) if total_cnt > 0 else 100.0
        # Average performance
        perf = sum(r["performance"] for r in machine_results) / len(machine_results) if machine_results else 0.0

        oee = (avail / 100.0) * (min(100.0, perf) / 100.0) * (qual / 100.0) * 100.0

        return {
            "line_id": line.id,
            "line_code": line.line_code,
            "name": line.name,
            "target_oee": float(line.target_oee),
            "planned_production_time_minutes": round(total_ppt, 2),
            "operating_time_minutes": round(total_opt, 2),
            "planned_downtime_minutes": round(total_p_dt, 2),
            "unplanned_downtime_minutes": round(total_u_dt, 2),
            "total_count": total_cnt,
            "good_count": total_good,
            "scrap_count": total_scrap,
            "rework_count": total_rework,
            "availability": round(avail, 2),
            "performance": round(perf, 2),
            "quality": round(qual, 2),
            "oee": round(oee, 2),
            "machines_count": len(machines),
            "machines": machine_results
        }
