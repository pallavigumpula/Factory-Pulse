import datetime
import uuid

def generate_po_code(index: int, year: int = None) -> str:
    y = year or datetime.datetime.now().year
    return f"PO-{y}-{index:06d}"

def generate_shift_instance_code(date_str: str, shift_suffix: str) -> str:
    return f"SHIFT-{date_str}-{shift_suffix}"

def generate_event_code(machine_code: str, index: int) -> str:
    clean_m = machine_code.replace("-", "").upper()
    return f"EVT-{clean_m}-{index:06d}"

def generate_count_code(po_code: str, index: int) -> str:
    clean_po = po_code.replace("-", "").upper()
    return f"CNT-{clean_po}-{index:06d}"

def generate_qc_code(index: int, year: int = None) -> str:
    y = year or datetime.datetime.now().year
    return f"QC-{y}-{index:06d}"

def generate_anomaly_code(index: int, year: int = None) -> str:
    y = year or datetime.datetime.now().year
    return f"ANOM-{y}-{index:06d}"
