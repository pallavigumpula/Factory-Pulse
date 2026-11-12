import pytest
from fastapi import HTTPException
from backend.app.schemas.master_data import (
    PlantCreate, LineCreate, MachineCreate, ProductCreate
)
from backend.app.routers.plants import list_plants, create_plant, delete_plant
from backend.app.routers.lines import list_lines
from backend.app.routers.machines import list_machines
from backend.app.routers.products import list_products, create_product
from backend.app.routers.shifts import list_shifts
from backend.app.routers.downtime import list_downtime_reasons

def test_list_plants(db, admin_user):
    plants = list_plants(skip=0, limit=10, db=db, current_user=admin_user)
    assert len(plants) >= 2

def test_create_and_delete_plant(db, admin_user):
    p_in = PlantCreate(
        plant_code="PLANT-TEST-88",
        name="Dallas Assembly Plant",
        location="Dallas, TX",
        timezone="America/Chicago"
    )
    created = create_plant(p_in, db=db, admin=admin_user)
    assert created.plant_code == "PLANT-TEST-88"

    # Delete
    del_res = delete_plant(created.id, db=db, admin=admin_user)
    assert "deleted" in del_res["message"].lower()

def test_list_lines_and_machines(db, admin_user):
    lines = list_lines(db=db, current_user=admin_user)
    assert len(lines) == 5

    machines = list_machines(db=db, current_user=admin_user)
    assert len(machines) == 30

def test_product_ideal_cycle_time_validation(db, admin_user):
    # Non-positive cycle time must raise 400
    prod_in = ProductCreate(
        product_code="PROD-INVALID-99",
        name="Invalid Product Test",
        ideal_cycle_time_seconds=-10.0
    )
    with pytest.raises(HTTPException) as excinfo:
        create_product(prod_in, db=db, admin=admin_user)
    assert excinfo.value.status_code == 400

def test_list_shifts_and_downtime_reasons(db, admin_user):
    shifts = list_shifts(db=db, current_user=admin_user)
    assert len(shifts) >= 3

    reasons = list_downtime_reasons(db=db, current_user=admin_user)
    assert len(reasons) >= 10
