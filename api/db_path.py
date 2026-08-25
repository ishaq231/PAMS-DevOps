import os
import sys

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "database"))
if DB_PATH not in sys.path:
    sys.path.insert(0, DB_PATH)