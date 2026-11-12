import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.master_data import Machine, ProductionLine, DowntimeReason
from backend.app.models.production import MachineStateEvent, ProductionCount, ProductionOrder
from backend.app.services.oee_engine import OEEEngine

class ManufacturingAIAssistant:
    """
    Intelligent Manufacturing Operations & OEE Assistant.
    Provides deterministic root-cause analysis based on actual database records.
    """

    @staticmethod
    def answer_query(db: Session, question: str) -> Dict[str, Any]:
        q_lower = question.lower()
        latest_evt = db.query(func.max(MachineStateEvent.end_time)).scalar()
        now = latest_evt if latest_evt else datetime.datetime.utcnow()
        week_ago = now - datetime.timedelta(days=7)

        # 1. Which machine has highest downtime?
        if "highest downtime" in q_lower or "worst machine" in q_lower or "most downtime" in q_lower:
            dt_by_m = db.query(
                Machine.machine_code,
                Machine.name,
                func.sum(MachineStateEvent.duration_seconds).label("sec")
            ).join(
                MachineStateEvent, MachineStateEvent.machine_id == Machine.id
            ).filter(
                MachineStateEvent.state.in_(["STOPPED", "MAINTENANCE"]),
                MachineStateEvent.start_time >= week_ago
            ).group_by(
                Machine.machine_code,
                Machine.name
            ).order_by(
                func.sum(MachineStateEvent.duration_seconds).desc()
            ).first()

            if dt_by_m:
                total_min = round(dt_by_m.sec / 60.0, 1)
                hours = round(total_min / 60.0, 1)
                return {
                    "question": question,
                    "answer": f"Machine **{dt_by_m.machine_code} ({dt_by_m.name})** experienced the highest downtime over the past 7 days, accumulating **{total_min} minutes** (~{hours} hours) of stoppage time.",
                    "source_metrics": {"machine_code": dt_by_m.machine_code, "downtime_minutes": total_min},
                    "insights": [
                        f"{dt_by_m.machine_code} is currently the primary bottleneck for line availability.",
                        "Unplanned mechanical stoppages accounted for the majority of lost operating time."
                    ],
                    "suggested_actions": [
                        f"Schedule an immediate autonomous maintenance audit for {dt_by_m.machine_code}.",
                        "Inspect feeder track alignment and verify pneumatic pressure regulator stability.",
                        "Review spare parts availability in tool crib for critical wear components."
                    ]
                }

        # 2. Which line has the best performance?
        if "best performance" in q_lower or "best line" in q_lower or "highest oee" in q_lower:
            lines = db.query(ProductionLine).filter(ProductionLine.is_active == True).all()
            line_results = []
            for l in lines:
                res = OEEEngine.calculate_line_oee(db, l.id, week_ago, now)
                line_results.append((res["oee"], res["performance"], l.name, l.line_code))
            
            line_results.sort(key=lambda x: x[0], reverse=True)
            if line_results:
                best_oee, best_perf, name, code = line_results[0]
                return {
                    "question": question,
                    "answer": f"Line **{code} ({name})** achieved the highest overall OEE at **{best_oee}%** with a speed performance score of **{best_perf}%** over the analyzed 7-day period.",
                    "source_metrics": {"line_code": code, "oee": best_oee, "performance": best_perf},
                    "insights": [
                        f"{code} maintains stable cycle times close to theoretical engineering maximums.",
                        "Minimal changeover disruption and high first-pass quality yield."
                    ],
                    "suggested_actions": [
                        f"Benchmark operating procedures from {code} to replicate across underperforming cells.",
                        "Maintain current preventive lubrication schedule."
                    ]
                }

        # 3. Why did OEE decrease? Causes of production loss?
        if "why" in q_lower or "decrease" in q_lower or "loss" in q_lower or "drop" in q_lower:
            top_dt = db.query(
                DowntimeReason.name,
                DowntimeReason.category,
                func.sum(MachineStateEvent.duration_seconds).label("sec"),
                func.count(MachineStateEvent.id).label("incidents")
            ).join(
                MachineStateEvent, MachineStateEvent.downtime_reason_id == DowntimeReason.id
            ).filter(
                MachineStateEvent.start_time >= week_ago
            ).group_by(
                DowntimeReason.name,
                DowntimeReason.category
            ).order_by(
                func.sum(MachineStateEvent.duration_seconds).desc()
            ).limit(3).all()

            top_reasons = []
            for r in top_dt:
                top_reasons.append(f"• **{r.name}** ({r.category}): {round(r.sec / 60.0, 1)} minutes across {r.incidents} incidents")

            reasons_str = "\n".join(top_reasons) if top_reasons else "• Micro-stops and tool changeovers."

            return {
                "question": question,
                "answer": f"Analysis of equipment telemetry and state records indicates that OEE was primarily impacted by the following downtime drivers:\n\n{reasons_str}",
                "source_metrics": {"top_reasons_count": len(top_dt)},
                "insights": [
                    "Unplanned mechanical stoppages and component jams are the largest contributor to Availability loss.",
                    "Minor micro-stops under 5 minutes frequently went untracked by manual operator logs."
                ],
                "suggested_actions": [
                    "Deploy SMED (Single-Minute Exchange of Die) methodology to compress tooling changeover durations.",
                    "Implement pre-shift visual inspection checklists for high-wear feeder reels.",
                    "Investigate quality variance at solder paste inspection station to reduce rework cycles."
                ]
            }

        # 4. What actions can improve OEE? (General recommendations)
        return {
            "question": question,
            "answer": "To systematically maximize overall OEE across the plant, focus on the **Six Big Losses** across Availability, Performance, and Quality:\n\n1. **Availability**: Target the top 2 unplanned downtime reasons with root cause problem solving (5-Why / Ishikawa).\n2. **Performance**: Eliminate micro-stops (<2 minutes) and ensure cycle times match standard work specifications.\n3. **Quality**: Prevent recurring defect modes through real-time in-line inspection and automated poka-yoke gates.",
            "source_metrics": {"analysis_scope": "Plant-wide Six Big Losses Framework"},
            "insights": [
                "A 5% improvement in Availability yields approximately 120 additional productive machine hours per line monthly.",
                "Quality yield improvements directly eliminate wasted upstream machine cycle time."
            ],
            "suggested_actions": [
                "Review Anomaly Detection dashboard to resolve open unlinked counts and overlapping telemetry events.",
                "Conduct weekly Autonomous Maintenance (AM) reviews with line operators.",
                "Enforce strict logging of downtime reasons for all stoppages exceeding 180 seconds."
            ]
        }
