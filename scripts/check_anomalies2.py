import sqlite3

db_path = r'C:\CandidateWorkspace\factorypulse.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check M-001 specifically for overlapping events (not just contiguous)
row = cur.execute("SELECT id FROM machines WHERE machine_code = 'M-001'").fetchone()
print('M-001 machine_id:', row)
mid = row[0]

# Look for ANY overlap in M-001 events (b.start_time < a.end_time means overlap)
rows = cur.execute('''
    SELECT a.id, a.event_code, a.start_time, a.end_time, b.id, b.event_code, b.start_time, b.end_time
    FROM machine_state_events a
    JOIN machine_state_events b ON a.machine_id = b.machine_id AND a.id < b.id
    WHERE a.machine_id = ? AND b.start_time < a.end_time
    LIMIT 10
''', (mid,)).fetchall()
print('\nOverlapping events for M-001:')
for r in rows:
    print(' ', r)

# Check negative count for PO-2026-000001 that is GOOD/SCRAP/REWORK type
print('\nGOOD/SCRAP/REWORK type negative count:')
rows = cur.execute('''
    SELECT id, count_code, quantity, count_type, production_order_id
    FROM production_counts
    WHERE quantity < 0 AND count_type IN ('GOOD', 'SCRAP', 'REWORK')
''').fetchall()
for r in rows:
    print(' ', r)

# What order code is production_order_id=1?
row = cur.execute("SELECT id, order_code FROM production_orders WHERE id = 1").fetchone()
print('\nProduction order id=1:', row)

conn.close()
