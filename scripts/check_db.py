import sqlite3
import os

db_path = r'C:\CandidateWorkspace\factorypulse.db'
print(f"DB exists: {os.path.exists(db_path)}, size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0} bytes")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("\nTables:", [t[0] for t in tables])

for table_name in [t[0] for t in tables]:
    count = cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  {table_name}: {count} rows")

# Check date range of key tables
print("\n--- Date ranges ---")
for table, col in [("machine_state_events", "start_time"), ("production_counts", "count_time"), ("quality_inspections", "inspection_time"), ("detected_anomalies", "detected_at")]:
    try:
        row = cur.execute(f"SELECT MIN({col}), MAX({col}) FROM {table}").fetchone()
        print(f"  {table}.{col}: {row[0]} to {row[1]}")
    except Exception as e:
        print(f"  {table}: ERROR {e}")

print("\n--- detected_anomalies sample ---")
try:
    rows = cur.execute("SELECT * FROM detected_anomalies LIMIT 5").fetchall()
    for r in rows:
        print(" ", r)
except Exception as e:
    print("  ERROR:", e)

conn.close()
