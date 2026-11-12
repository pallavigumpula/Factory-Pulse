import sqlite3

db_path = r'C:\CandidateWorkspace\factorypulse.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check products - especially PROD-ANOM
print('Products with anomaly cycle time:')
rows = cur.execute("SELECT id, product_code, name, ideal_cycle_time_seconds FROM products WHERE ideal_cycle_time_seconds <= 0").fetchall()
for r in rows:
    print(' ', r)

# Check all products
print('\nAll products:')
rows = cur.execute("SELECT id, product_code, name, ideal_cycle_time_seconds FROM products").fetchall()
for r in rows:
    print(' ', r)

# Check if there are overlapping events
print('\nOverlapping events count:')
rows = cur.execute("""
    SELECT COUNT(*) FROM (
        SELECT a.machine_id, a.event_code, a.start_time, a.end_time, b.event_code, b.start_time, b.end_time
        FROM machine_state_events a
        JOIN machine_state_events b ON a.machine_id = b.machine_id AND a.id < b.id
        WHERE b.start_time < a.end_time
    )
""").fetchall()
print(' ', rows[0][0])

# Check negative counts
print('\nNegative counts:')
rows = cur.execute("SELECT id, count_code, quantity, count_type, production_order_id FROM production_counts WHERE quantity < 0").fetchall()
for r in rows:
    print(' ', r)

# Check QC with failed > sample
print('\nQC failed > sample:')
rows = cur.execute("SELECT id, inspection_code, sample_size, failed_count FROM quality_inspections WHERE failed_count > sample_size").fetchall()
for r in rows:
    print(' ', r)

# Check specific ground truth entities
print('\nCheck PO-2026-000001 exists:')
rows = cur.execute("SELECT id, order_code FROM production_orders WHERE order_code = 'PO-2026-000001'").fetchall()
print(' ', rows)

print('\nCheck QC-2026-999903 exists:')
rows = cur.execute("SELECT id, inspection_code FROM quality_inspections WHERE inspection_code = 'QC-2026-999903'").fetchall()
print(' ', rows)

print('\nCheck M-001 machine events overlap:')
rows = cur.execute("""
    SELECT a.event_code, a.start_time, a.end_time
    FROM machine_state_events a
    JOIN machines m ON a.machine_id = m.id
    WHERE m.machine_code = 'M-001'
    ORDER BY a.start_time
    LIMIT 10
""").fetchall()
for r in rows:
    print(' ', r)

# Check downtime/break overlap for machine id=1
print('\nDowntime overlapping BREAK for machine_id=1:')
rows = cur.execute("""
    SELECT a.event_code, a.state, a.start_time, a.end_time, b.event_code, b.state, b.start_time, b.end_time
    FROM machine_state_events a
    JOIN machine_state_events b ON a.machine_id = b.machine_id
    WHERE a.machine_id = 1
      AND a.state IN ('STOPPED', 'MAINTENANCE')
      AND b.state = 'BREAK'
      AND a.start_time < b.end_time
      AND b.start_time < a.end_time
    LIMIT 5
""").fetchall()
for r in rows:
    print(' ', r)

conn.close()
