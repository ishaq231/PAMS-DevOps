"""
24030388 - Ishaq Modassir Mushtaq

Location model for location management and login selection.
"""

from connection import Database_connection
from base_model import BaseModel


class Location(BaseModel):
    """Handles location database operations."""

    def __init__(self, location_id=None, city=None, manager=None):
        self.location_id = location_id
        self.city = city
        self.manager = manager

    @staticmethod
    def get_all_locations():
        """Fetch all locations."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT location_id, city, manager FROM location ORDER BY location_id")
            return [Location.from_dict(r) for r in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching locations: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def add_location(city, manager):
        """Add a new location and return the new location_id."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO location (city, manager) VALUES (%s, %s)",
                           (city, manager))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding location: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()


# Backward-compatible aliases
get_all_locations = Location.get_all_locations
add_location = Location.add_location
