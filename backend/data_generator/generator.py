import os
import json
import csv
import random
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from backend.app.database import engine, Base, SessionLocal
from backend.app.models.user import User
from backend.app.models.master_data import (
    Plant,
    ProductionLine,
    Machine,
    Shift,
    ShiftInstance,
    Product,
    DowntimeReason,
)
from backend.app.models.production import (
    ProductionOrder,
    MachineStateEvent,
    ProductionCount,
    QualityInspection,
)
from backend.app.utils.security import hash_password
from backend.app.utils.identifiers import (
    generate_po_code,
    generate_event_code,
    generate_count_code,
    generate_qc_code,
    generate_anomaly_code,
)

DEFAULT_SEED = 20261022


class ManufacturingDataGenerator:

    def __init__(
        self,
        seed: int = DEFAULT_SEED,
        mode: str = "starter",
        clean: bool = True,
    ):
        self.seed = seed
        self.mode = mode.lower()
        self.clean = clean
        self.rng = random.Random(self.seed)
        self.ground_truth_anomalies: List[Dict[str, Any]] = []

    def run(
        self,
        db: Optional[Session] = None,
        export_dir: Optional[str] = None,
    ):
        self.rng = random.Random(self.seed)
        self.ground_truth_anomalies = []

        close_session = False

        if db is None:
            db = SessionLocal()
            close_session = True

        try:
            print(
                f"[{datetime.datetime.now()}] Starting data generation "
                f"in '{self.mode}' mode with seed {self.seed}..."
            )

            target_bind = db.get_bind() if db else engine

            if self.clean:
                Base.metadata.drop_all(bind=target_bind)

            Base.metadata.create_all(bind=target_bind)

            # 1. Master Data
            plants = self._create_plants(db)
            lines = self._create_lines(db, plants)
            machines = self._create_machines(db, lines)
            shifts = self._create_shifts(db, plants)
            products = self._create_products(db)
            downtime_reasons = self._create_downtime_reasons(db)
            users = self._create_users(db)

            db.commit()

            # 2. Production Orders
            days = 5 if self.mode == "starter" else 90
            start_date = datetime.date(2026, 1, 1)

            # Create dated shift instances
            self._create_shift_instances(
                db,
                shifts,
                start_date,
                days,
            )
            db.commit()

            orders = self._create_production_orders(
                db,
                lines,
                products,
                start_date,
                days,
            )
            db.commit()

            # 3. Machine State Events, Counts, Inspections
            self._create_operations_data(
                db,
                machines,
                shifts,
                products,
                orders,
                downtime_reasons,
                users,
                start_date,
                days,
            )
            db.commit()

            # 4. Inject anomalies
            self._inject_anomalies(
                db,
                machines,
                orders,
                products,
            )
            db.commit()

            # 5. Export Ground Truth and CSV files
            self._export_ground_truth(export_dir)

            mode_dir = (
                Path(export_dir if export_dir else "data")
                / self.mode
            )

            self._export_csv_tables(db, mode_dir)

            print(
                f"[{datetime.datetime.now()}] "
                "Generation finished successfully!"
            )

        finally:
            if close_session:
                db.close()

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------

    def _create_users(self, db: Session) -> List[User]:

        user_specs = [
            (
                "admin",
                "admin@factorypulse.internal",
                "System Administrator",
                "ADMIN",
                "admin123",
            ),
            (
                "operator1",
                "operator1@factorypulse.internal",
                "John Vance (Operator)",
                "OPERATOR",
                "operator123",
            ),
            (
                "maint1",
                "maint1@factorypulse.internal",
                "Sarah Connor (Maintenance)",
                "MAINTENANCE",
                "maint123",
            ),
            (
                "qc1",
                "qc1@factorypulse.internal",
                "Alex Chen (Quality)",
                "QUALITY",
                "qc123",
            ),
            (
                "planner1",
                "planner1@factorypulse.internal",
                "Elena Rostova (Planner)",
                "PLANNER",
                "planner123",
            ),
        ]

        created = []

        for username, email, full_name, role, pwd in user_specs:

            user = (
                db.query(User)
                .filter(User.username == username)
                .first()
            )

            if not user:
                user = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    role=role,
                    is_active=True,
                    password_hash=hash_password(pwd),
                )

                db.add(user)
                db.flush()

            created.append(user)

        return created

    # ---------------------------------------------------------
    # PLANTS
    # ---------------------------------------------------------

    def _create_plants(self, db: Session) -> List[Plant]:

        plant_specs = [
            (
                "PLANT-01",
                "Austin Advanced Electronics Plant",
                "Austin, TX, USA",
                "America/Chicago",
            ),
            (
                "PLANT-02",
                "Detroit Precision Machining Works",
                "Detroit, MI, USA",
                "America/Detroit",
            ),
        ]

        created = []

        for code, name, location, timezone in plant_specs:

            plant = (
                db.query(Plant)
                .filter(Plant.plant_code == code)
                .first()
            )

            if not plant:
                plant = Plant(
                    plant_code=code,
                    name=name,
                    location=location,
                    timezone=timezone,
                    is_active=True,
                )

                db.add(plant)
                db.flush()

            created.append(plant)

        return created

    # ---------------------------------------------------------
    # PRODUCTION LINES
    # ---------------------------------------------------------

    def _create_lines(
        self,
        db: Session,
        plants: List[Plant],
    ) -> List[ProductionLine]:

        line_specs = [
            (
                plants[0].id,
                "LINE-01",
                "SMT High-Speed Surface Mount Line 1",
                88.0,
            ),
            (
                plants[0].id,
                "LINE-02",
                "Through-Hole Wave Soldering Line 2",
                85.0,
            ),
            (
                plants[0].id,
                "LINE-03",
                "Final Assembly & Packaging Line 3",
                90.0,
            ),
            (
                plants[1].id,
                "LINE-04",
                "5-Axis CNC Precision Milling Cell",
                82.0,
            ),
            (
                plants[1].id,
                "LINE-05",
                "High-Tonnage Progressive Stamping Line",
                86.0,
            ),
        ]

        created = []

        for plant_id, code, name, oee in line_specs:

            line = (
                db.query(ProductionLine)
                .filter(ProductionLine.line_code == code)
                .first()
            )

            if not line:
                line = ProductionLine(
                    plant_id=plant_id,
                    line_code=code,
                    name=name,
                    target_oee=oee,
                    is_active=True,
                )

                db.add(line)
                db.flush()

            created.append(line)

        return created

    # ---------------------------------------------------------
    # MACHINES
    # ---------------------------------------------------------

    def _create_machines(
        self,
        db: Session,
        lines: List[ProductionLine],
    ) -> List[Machine]:

        created = []
        machine_idx = 1

        for line in lines:

            for j in range(1, 7):

                code = f"M-{machine_idx:03d}"
                name = f"{line.line_code} Station {j}"

                machine = (
                    db.query(Machine)
                    .filter(Machine.machine_code == code)
                    .first()
                )

                if not machine:
                    machine = Machine(
                        line_id=line.id,
                        machine_code=code,
                        name=name,
                        model=f"Model-{line.line_code}-S{j}",
                        current_status="RUNNING",
                        is_active=True,
                    )

                    db.add(machine)
                    db.flush()

                created.append(machine)
                machine_idx += 1

        return created

    # ---------------------------------------------------------
    # SHIFTS
    # ---------------------------------------------------------

    def _create_shifts(
        self,
        db: Session,
        plants: List[Plant],
    ) -> List[Shift]:

        created = []

        shift_specs = [
            (
                "SHIFT-A",
                "Morning Shift (06:00 - 14:00)",
                datetime.time(6, 0),
                datetime.time(14, 0),
                60,
            ),
            (
                "SHIFT-B",
                "Afternoon Shift (14:00 - 22:00)",
                datetime.time(14, 0),
                datetime.time(22, 0),
                60,
            ),
            (
                "SHIFT-C",
                "Night Shift (22:00 - 06:00)",
                datetime.time(22, 0),
                datetime.time(6, 0),
                60,
            ),
        ]

        for plant in plants:

            for code, name, start, end, break_minutes in shift_specs:

                shift = (
                    db.query(Shift)
                    .filter(
                        Shift.plant_id == plant.id,
                        Shift.shift_code == code,
                    )
                    .first()
                )

                if not shift:
                    shift = Shift(
                        plant_id=plant.id,
                        shift_code=code,
                        name=name,
                        start_time=start,
                        end_time=end,
                        planned_break_minutes=break_minutes,
                        is_active=True,
                    )

                    db.add(shift)
                    db.flush()

                created.append(shift)

        return created

    # ---------------------------------------------------------
    # SHIFT INSTANCES
    # ---------------------------------------------------------

    def _create_shift_instances(
        self,
        db: Session,
        shifts: List[Shift],
        start_date: datetime.date,
        days: int,
    ) -> List[ShiftInstance]:

        created: List[ShiftInstance] = []

        for day in range(days):

            current_day = start_date + datetime.timedelta(days=day)

            for shift in shifts:

                shift_start = datetime.datetime.combine(
                    current_day,
                    shift.start_time,
                )

                end_date = current_day

                if shift.end_time <= shift.start_time:
                    end_date += datetime.timedelta(days=1)

                shift_end = datetime.datetime.combine(
                    end_date,
                    shift.end_time,
                )

                plant = shift.plant

                instance_code = (
                    f"{plant.plant_code}-"
                    f"{current_day.isoformat()}-"
                    f"{shift.shift_code}"
                )

                instance = (
                    db.query(ShiftInstance)
                    .filter(
                        ShiftInstance.instance_code == instance_code
                    )
                    .first()
                )

                if instance is None:

                    instance = ShiftInstance(
                        instance_code=instance_code,
                        shift_template_id=shift.id,
                        plant_id=shift.plant_id,
                        shift_date=current_day,
                        start_time=shift_start,
                        end_time=shift_end,
                        planned_break_minutes=(
                            shift.planned_break_minutes
                        ),
                    )

                    db.add(instance)
                    db.flush()

                created.append(instance)

        return created

    # ---------------------------------------------------------
    # PRODUCTS
    # ---------------------------------------------------------

    def _create_products(self, db: Session) -> List[Product]:

        prod_specs = [
            ("PROD-001", "Automotive ECU Control Unit v3", "Electronics", 18.5),
            ("PROD-002", "Industrial IoT Gateway Module", "Electronics", 14.2),
            ("PROD-003", "High-Torque BLDC Motor Driver Board", "Power Electronics", 22.0),
            ("PROD-004", "Medical Sensor Signal Conditioner", "Medical", 28.0),
            ("PROD-005", "EV Battery Management Slave Board", "Automotive", 16.0),
            ("PROD-006", "Precision Servo Actuator Housing", "Mechanical", 35.0),
            ("PROD-007", "Titanium Orthopedic Screw Implant", "Medical", 45.0),
            ("PROD-008", "Hydraulic Valve Spool Sleeve", "Hydraulics", 30.0),
            ("PROD-009", "Aerospace Bracket Alloy 7075-T6", "Aerospace", 55.0),
            ("PROD-010", "High-Pressure Fuel Injection Nozzle", "Automotive", 40.0),
            ("PROD-011", "Multi-Layer Copper Heat Sink Plate", "Thermal", 12.5),
            ("PROD-012", "Stainless Steel Stamped Sensor Shield", "Stamping", 6.5),
            ("PROD-013", "High-Speed Optical Transceiver Cage", "Telecom", 8.0),
            ("PROD-014", "Micro-Inverter Filter Choke Assembly", "Renewable", 19.5),
            ("PROD-015", "Radar Transceiver Front-End Board", "Aerospace", 32.0),
            ("PROD-016", "Pneumatic Manifold Block 4-Station", "Pneumatics", 48.0),
            ("PROD-017", "EMI Shielding Can Enclosure", "Stamping", 5.0),
            ("PROD-018", "Rugged Display Touch Controller PCB", "Electronics", 17.5),
            ("PROD-019", "Turbine Impeller Blade Segment", "Aerospace", 65.0),
            ("PROD-020", "Precision Ground Spur Gear Ring", "Transmission", 38.0),
        ]

        created = []

        for code, name, category, cycle_time in prod_specs:

            product = (
                db.query(Product)
                .filter(Product.product_code == code)
                .first()
            )

            if not product:
                product = Product(
                    product_code=code,
                    name=name,
                    category=category,
                    ideal_cycle_time_seconds=cycle_time,
                    is_active=True,
                )

                db.add(product)
                db.flush()

            created.append(product)

        return created

    # ---------------------------------------------------------
    # DOWNTIME REASONS
    # ---------------------------------------------------------

    def _create_downtime_reasons(
        self,
        db: Session,
    ) -> List[DowntimeReason]:

        dt_specs = [
            ("DTR-BRK-01", "BREAK", "Scheduled Meal / Shift Break", True),
            ("DTR-CHG-01", "CHANGEOVER", "Product Tooling & Feeder Changeover", True),
            ("DTR-MNT-01", "MAINTENANCE", "Preventive Scheduled Maintenance", True),
            ("DTR-MNT-02", "MAINTENANCE", "Autonomous Maintenance & Cleaning", True),
            ("DTR-JAM-01", "UNPLANNED_DOWNTIME", "Component Feeder Jam", False),
            ("DTR-MEC-01", "UNPLANNED_DOWNTIME", "Mechanical Drive / Spindle Failure", False),
            ("DTR-ELE-01", "UNPLANNED_DOWNTIME", "Sensor / Vision System Fault", False),
            ("DTR-MAT-01", "UNPLANNED_DOWNTIME", "Raw Material Starvation", False),
            ("DTR-TMP-01", "UNPLANNED_DOWNTIME", "Process Temperature Out-of-Spec", False),
            ("DTR-ENV-01", "UNPLANNED_DOWNTIME", "Facility Power Surge / Utility Interruption", False),
        ]

        created = []

        for code, category, name, planned in dt_specs:

            reason = (
                db.query(DowntimeReason)
                .filter(DowntimeReason.reason_code == code)
                .first()
            )

            if not reason:
                reason = DowntimeReason(
                    reason_code=code,
                    category=category,
                    name=name,
                    is_planned=planned,
                    is_active=True,
                )

                db.add(reason)
                db.flush()

            created.append(reason)

        return created

    # ---------------------------------------------------------
    # PRODUCTION ORDERS
    # ---------------------------------------------------------

    def _create_production_orders(
        self,
        db: Session,
        lines: List[ProductionLine],
        products: List[Product],
        start_date: datetime.date,
        days: int,
    ) -> List[ProductionOrder]:

        orders = []
        order_idx = 1

        for day in range(days):

            current_day = start_date + datetime.timedelta(days=day)

            for line in lines:

                num_orders = (
                    1
                    if self.mode == "starter"
                    else self.rng.choice([1, 2])
                )

                for o in range(num_orders):

                    product = self.rng.choice(products)
                    target = self.rng.randint(400, 1500)

                    start_dt = (
                        datetime.datetime.combine(
                            current_day,
                            datetime.time(6, 0),
                        )
                        + datetime.timedelta(hours=o * 8)
                    )

                    end_dt = start_dt + datetime.timedelta(
                        hours=7,
                        minutes=30,
                    )

                    po_code = generate_po_code(
                        order_idx,
                        current_day.year,
                    )

                    existing = (
                        db.query(ProductionOrder)
                        .filter(
                            ProductionOrder.order_code == po_code
                        )
                        .first()
                    )

                    if not existing:

                        po = ProductionOrder(
                            order_code=po_code,
                            line_id=line.id,
                            product_id=product.id,
                            target_quantity=target,
                            produced_quantity=0,
                            status=(
                                "COMPLETED"
                                if day < days - 1
                                else "IN_PROGRESS"
                            ),
                            start_time=start_dt,
                            end_time=end_dt,
                        )

                        db.add(po)
                        db.flush()
                        orders.append(po)

                    else:
                        orders.append(existing)

                    order_idx += 1

        return orders

    # ---------------------------------------------------------
    # OPERATIONS DATA
    # ---------------------------------------------------------

    def _create_operations_data(
        self,
        db: Session,
        machines: List[Machine],
        shifts: List[Shift],
        products: List[Product],
        orders: List[ProductionOrder],
        reasons: List[DowntimeReason],
        users: List[User],
        start_date: datetime.date,
        days: int,
    ):

        event_counter = 1
        count_counter = 1
        qc_counter = 1

        unplanned_reasons = [
            reason for reason in reasons
            if not reason.is_planned
        ]

        break_reason = [
            reason for reason in reasons
            if reason.category == "BREAK"
        ][0]

        shift_schedule = [
            (6, 14, 11.5),
            (14, 22, 17.5),
            (22, 6, 1.5),
        ]

        for day in range(days):

            current_day = start_date + datetime.timedelta(days=day)

            for s_idx, (
                start_h,
                end_h,
                break_start_h,
            ) in enumerate(shift_schedule):

                active_shift = shifts[s_idx % len(shifts)]

                if start_h < end_h:

                    shift_start = datetime.datetime.combine(
                        current_day,
                        datetime.time(start_h, 0),
                    )

                    shift_end = datetime.datetime.combine(
                        current_day,
                        datetime.time(end_h, 0),
                    )

                else:

                    shift_start = datetime.datetime.combine(
                        current_day,
                        datetime.time(start_h, 0),
                    )

                    shift_end = datetime.datetime.combine(
                        current_day + datetime.timedelta(days=1),
                        datetime.time(end_h, 0),
                    )

                target_machines = (
                    machines
                    if self.mode == "full"
                    else machines[:10]
                )

                for machine in target_machines:

                    po = next(
                        (
                            order for order in orders
                            if order.line_id == machine.line_id
                        ),
                        orders[0],
                    )

                    product = po.product or products[0]

                    break_start = (
                        shift_start
                        + datetime.timedelta(
                            hours=(
                                break_start_h - start_h
                                if break_start_h > start_h
                                else break_start_h + 24 - start_h
                            )
                        )
                    )

                    break_end = break_start + datetime.timedelta(
                        minutes=60
                    )

                    # RUNNING 1
                    seg1_end = break_start

                    e1 = MachineStateEvent(
                        event_code=generate_event_code(
                            machine.machine_code,
                            event_counter,
                        ),
                        machine_id=machine.id,
                        production_order_id=po.id,
                        shift_id=active_shift.id,
                        state="RUNNING",
                        start_time=shift_start,
                        end_time=seg1_end,
                        duration_seconds=int(
                            (seg1_end - shift_start).total_seconds()
                        ),
                    )

                    db.add(e1)
                    event_counter += 1

                    # BREAK
                    e_brk = MachineStateEvent(
                        event_code=generate_event_code(
                            machine.machine_code,
                            event_counter,
                        ),
                        machine_id=machine.id,
                        production_order_id=po.id,
                        shift_id=active_shift.id,
                        state="BREAK",
                        start_time=break_start,
                        end_time=break_end,
                        duration_seconds=3600,
                        downtime_reason_id=break_reason.id,
                    )

                    db.add(e_brk)
                    event_counter += 1

                    # UNPLANNED STOPPAGE
                    dt_minutes = (
                        self.rng.randint(5, 20)
                        if self.rng.random() < 0.75
                        else 0
                    )

                    dt_start = break_end + datetime.timedelta(
                        minutes=30
                    )

                    dt_end = min(
                        shift_end - datetime.timedelta(minutes=10),
                        dt_start + datetime.timedelta(
                            minutes=dt_minutes
                        ),
                    )

                    if dt_minutes > 0 and dt_end > dt_start:

                        e2 = MachineStateEvent(
                            event_code=generate_event_code(
                                machine.machine_code,
                                event_counter,
                            ),
                            machine_id=machine.id,
                            production_order_id=po.id,
                            shift_id=active_shift.id,
                            state="RUNNING",
                            start_time=break_end,
                            end_time=dt_start,
                            duration_seconds=int(
                                (dt_start - break_end).total_seconds()
                            ),
                        )

                        db.add(e2)
                        event_counter += 1

                        reason = self.rng.choice(unplanned_reasons)

                        e_dt = MachineStateEvent(
                            event_code=generate_event_code(
                                machine.machine_code,
                                event_counter,
                            ),
                            machine_id=machine.id,
                            production_order_id=po.id,
                            shift_id=active_shift.id,
                            state="STOPPED",
                            start_time=dt_start,
                            end_time=dt_end,
                            duration_seconds=int(
                                (dt_end - dt_start).total_seconds()
                            ),
                            downtime_reason_id=reason.id,
                        )

                        db.add(e_dt)
                        event_counter += 1

                        if shift_end > dt_end:

                            e3 = MachineStateEvent(
                                event_code=generate_event_code(
                                    machine.machine_code,
                                    event_counter,
                                ),
                                machine_id=machine.id,
                                production_order_id=po.id,
                                shift_id=active_shift.id,
                                state="RUNNING",
                                start_time=dt_end,
                                end_time=shift_end,
                                duration_seconds=int(
                                    (shift_end - dt_end).total_seconds()
                                ),
                            )

                            db.add(e3)
                            event_counter += 1

                    else:

                        e2 = MachineStateEvent(
                            event_code=generate_event_code(
                                machine.machine_code,
                                event_counter,
                            ),
                            machine_id=machine.id,
                            production_order_id=po.id,
                            shift_id=active_shift.id,
                            state="RUNNING",
                            start_time=break_end,
                            end_time=shift_end,
                            duration_seconds=int(
                                (shift_end - break_end).total_seconds()
                            ),
                        )

                        db.add(e2)
                        event_counter += 1

                    # PRODUCTION COUNTS
                    cycle_time = float(
                        product.ideal_cycle_time_seconds
                    )

                    total_operating_sec = (
                        7 * 3600
                    ) - (dt_minutes * 60)

                    expected_units = int(
                        total_operating_sec / cycle_time
                        * self.rng.uniform(0.85, 0.98)
                    )

                    good_units = int(expected_units * 0.95)
                    scrap_units = int(expected_units * 0.035)

                    rework_units = max(
                        0,
                        expected_units - good_units - scrap_units,
                    )

                    count_time = shift_start + datetime.timedelta(
                        hours=3
                    )

                    good_count = ProductionCount(
                        count_code=generate_count_code(
                            po.order_code,
                            count_counter,
                        ),
                        production_order_id=po.id,
                        machine_id=machine.id,
                        shift_id=active_shift.id,
                        product_id=product.id,
                        count_type="GOOD",
                        quantity=good_units,
                        timestamp=count_time,
                        operator_id=users[1].id,
                    )

                    db.add(good_count)
                    count_counter += 1

                    scrap_count = ProductionCount(
                        count_code=generate_count_code(
                            po.order_code,
                            count_counter,
                        ),
                        production_order_id=po.id,
                        machine_id=machine.id,
                        shift_id=active_shift.id,
                        product_id=product.id,
                        count_type="SCRAP",
                        quantity=scrap_units,
                        timestamp=count_time + datetime.timedelta(
                            minutes=10
                        ),
                        operator_id=users[1].id,
                    )

                    db.add(scrap_count)
                    count_counter += 1

                    if rework_units > 0:

                        rework_count = ProductionCount(
                            count_code=generate_count_code(
                                po.order_code,
                                count_counter,
                            ),
                            production_order_id=po.id,
                            machine_id=machine.id,
                            shift_id=active_shift.id,
                            product_id=product.id,
                            count_type="REWORK",
                            quantity=rework_units,
                            timestamp=count_time + datetime.timedelta(
                                minutes=20
                            ),
                            operator_id=users[1].id,
                        )

                        db.add(rework_count)
                        count_counter += 1

                    po.produced_quantity = (
                        (po.produced_quantity or 0) + good_units
                    )

                    # QUALITY INSPECTION
                    sample_size = self.rng.randint(25, 50)
                    failed = self.rng.randint(0, 2)
                    passed = sample_size - failed

                    qc = QualityInspection(
                        inspection_code=generate_qc_code(
                            qc_counter,
                            current_day.year,
                        ),
                        production_order_id=po.id,
                        machine_id=machine.id,
                        shift_id=active_shift.id,
                        sample_size=sample_size,
                        passed_count=passed,
                        failed_count=failed,
                        defect_type=(
                            "Solder Bridge" if failed > 0 else None
                        ),
                        inspector_id=users[3].id,
                        timestamp=shift_start + datetime.timedelta(
                            hours=5
                        ),
                        status=(
                            "PASSED" if failed == 0
                            else "CONDITIONAL"
                        ),
                    )

                    db.add(qc)
                    qc_counter += 1

    # ---------------------------------------------------------
    # ANOMALY INJECTION
    # ---------------------------------------------------------

    def _inject_anomalies(
        self,
        db: Session,
        machines: List[Machine],
        orders: List[ProductionOrder],
        products: List[Product],
    ):

        anom_idx = 1
        target_machine = machines[0]

        now = datetime.datetime(2026, 1, 2, 10, 0, 0)

        # Anomaly 1: Overlapping machine-state event
        overlap_event = MachineStateEvent(
            event_code=generate_event_code(
                target_machine.machine_code,
                999901,
            ),
            machine_id=target_machine.id,
            production_order_id=orders[0].id,
            state="STOPPED",
            start_time=now,
            end_time=now + datetime.timedelta(minutes=30),
            duration_seconds=1800,
            notes="Injected anomaly: Overlapping event",
        )

        db.add(overlap_event)

        self.ground_truth_anomalies.append({
            "anomaly_id": f"GT-{anom_idx:04d}",
            "anomaly_type": "OVERLAPPING_MACHINE_EVENT",
            "entity_id": target_machine.machine_code,
            "timestamp": now.isoformat(),
            "severity": "HIGH",
            "description": (
                f"Machine {target_machine.machine_code} "
                "has overlapping state intervals."
            ),
            "expected_value": "Non-overlapping intervals",
            "actual_value": "Overlap detected at 10:00",
        })

        anom_idx += 1

        # Anomaly 2: Negative production count
        po_target = orders[0]

        bad_count = ProductionCount(
            count_code=generate_count_code(
                po_target.order_code,
                999902,
            ),
            production_order_id=po_target.id,
            machine_id=target_machine.id,
            product_id=products[0].id,
            count_type="GOOD",
            quantity=-45,
            timestamp=datetime.datetime(2026, 1, 2, 12, 0, 0),
            reason="Injected anomaly: Negative count under GOOD",
        )

        db.add(bad_count)

        self.ground_truth_anomalies.append({
            "anomaly_id": f"GT-{anom_idx:04d}",
            "anomaly_type": "NEGATIVE_COUNT_WITHOUT_CORRECTION",
            "entity_id": po_target.order_code,
            "timestamp": datetime.datetime(
                2026, 1, 2, 12, 0, 0
            ).isoformat(),
            "severity": "CRITICAL",
            "description": (
                f"Production order {po_target.order_code} "
                "has negative count under non-correction type."
            ),
            "expected_value": "quantity >= 0",
            "actual_value": "-45",
        })

        anom_idx += 1

        # Anomaly 3: Failed count exceeds sample size
        bad_qc = QualityInspection(
            inspection_code=generate_qc_code(999903, 2026),
            production_order_id=po_target.id,
            machine_id=target_machine.id,
            sample_size=30,
            passed_count=0,
            failed_count=42,
            defect_type="Severe Warpage",
            timestamp=datetime.datetime(2026, 1, 2, 14, 0, 0),
            status="FAILED",
            notes="Injected anomaly: Failed count exceeds sample size",
        )

        db.add(bad_qc)

        self.ground_truth_anomalies.append({
            "anomaly_id": f"GT-{anom_idx:04d}",
            "anomaly_type": "SCRAP_EXCEEDS_TOTAL_PRODUCTION",
            "entity_id": bad_qc.inspection_code,
            "timestamp": datetime.datetime(
                2026, 1, 2, 14, 0, 0
            ).isoformat(),
            "severity": "CRITICAL",
            "description": (
                f"Quality inspection {bad_qc.inspection_code} "
                "has failed count exceeding sample size."
            ),
            "expected_value": "failed_count <= sample_size (30)",
            "actual_value": "42",
        })

        anom_idx += 1

        # Anomaly 4: Invalid ideal cycle time
        anom_product = (
            db.query(Product)
            .filter(Product.product_code == "PROD-ANOM")
            .first()
        )

        if not anom_product:

            anom_product = Product(
                product_code="PROD-ANOM",
                name="Anomalous Prototype Bracket",
                category="Prototype",
                ideal_cycle_time_seconds=-5.0,
                is_active=True,
            )

            db.add(anom_product)
            db.flush()

        self.ground_truth_anomalies.append({
            "anomaly_id": f"GT-{anom_idx:04d}",
            "anomaly_type": "INCORRECT_IDEAL_CYCLE_TIME",
            "entity_id": anom_product.product_code,
            "timestamp": anom_product.created_at.isoformat(),
            "severity": "HIGH",
            "description": "Product has invalid negative ideal cycle time.",
            "expected_value": "ideal_cycle_time_seconds > 0",
            "actual_value": "-5.0",
        })

        anom_idx += 1

        # Anomaly 5: Downtime overlapping planned break
        downtime_event = MachineStateEvent(
            event_code=generate_event_code(
                target_machine.machine_code,
                999905,
            ),
            machine_id=target_machine.id,
            production_order_id=po_target.id,
            state="STOPPED",
            start_time=datetime.datetime(2026, 1, 1, 11, 45, 0),
            end_time=datetime.datetime(2026, 1, 1, 12, 15, 0),
            duration_seconds=1800,
            notes=(
                "Injected anomaly: Breakdown overlapping "
                "statutory break"
            ),
        )

        db.add(downtime_event)

        self.ground_truth_anomalies.append({
            "anomaly_id": f"GT-{anom_idx:04d}",
            "anomaly_type": "DOWNTIME_OVERLAPPING_PLANNED_BREAK",
            "entity_id": str(target_machine.id),
            "timestamp": datetime.datetime(
                2026, 1, 1, 11, 45, 0
            ).isoformat(),
            "severity": "MEDIUM",
            "description": (
                "Equipment breakdown reported concurrently "
                "with statutory lunch break."
            ),
            "expected_value": (
                "No overlapping unplanned downtime during BREAK"
            ),
            "actual_value": "STOPPED state inside BREAK window",
        })

    # ---------------------------------------------------------
    # EXPORT GROUND TRUTH
    # ---------------------------------------------------------

    def _export_ground_truth(
        self,
        export_dir: Optional[str] = None,
    ):

        target_dir = (
            Path(export_dir) if export_dir else Path("data")
        )

        target_dir.mkdir(parents=True, exist_ok=True)

        json_path = target_dir / "ground_truth.json"
        csv_path = target_dir / "ground_truth.csv"

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(
                self.ground_truth_anomalies,
                file,
                indent=2,
            )

        if self.ground_truth_anomalies:

            with open(
                csv_path,
                "w",
                newline="",
                encoding="utf-8",
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=list(
                        self.ground_truth_anomalies[0].keys()
                    ),
                )

                writer.writeheader()
                writer.writerows(self.ground_truth_anomalies)

        print(
            f"Ground truth exported to {json_path} and "
            f"{csv_path} with "
            f"{len(self.ground_truth_anomalies)} labeled anomalies."
        )

    # ---------------------------------------------------------
    # EXPORT CSV TABLES
    # ---------------------------------------------------------

    def _export_csv_tables(
        self,
        db: Session,
        target_dir: Path,
    ):

        target_dir.mkdir(parents=True, exist_ok=True)

        models = [
            ("plants.csv", Plant),
            ("production_lines.csv", ProductionLine),
            ("machines.csv", Machine),
            ("shifts.csv", Shift),
            ("shift_instances.csv", ShiftInstance),
            ("products.csv", Product),
            ("downtime_reasons.csv", DowntimeReason),
            ("production_orders.csv", ProductionOrder),
            ("machine_state_events.csv", MachineStateEvent),
            ("production_counts.csv", ProductionCount),
            ("quality_inspections.csv", QualityInspection),
            ("users.csv", User),
        ]

        for filename, model in models:

            records = db.query(model).all()

            if records:

                columns = [
                    column.name
                    for column in model.__table__.columns
                ]

                output_path = target_dir / filename

                with open(
                    output_path,
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as file:

                    writer = csv.writer(file)
                    writer.writerow(columns)

                    for record in records:
                        writer.writerow([
                            getattr(record, column)
                            for column in columns
                        ])

        print(f"Table datasets exported to {target_dir}")