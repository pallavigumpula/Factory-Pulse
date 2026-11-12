import os
import sys
from pathlib import Path

# Ensure root workspace is on python path
workspace_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, workspace_root)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_factorypulse.db"

import pytest

if __name__ == "__main__":
    print(f"Running FactoryPulse test suite from: {workspace_root}")
    # Remove old test db if present
    test_db = Path("test_factorypulse.db")
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass

    exit_code = pytest.main(["-v", "backend/tests"])
    sys.exit(exit_code)
