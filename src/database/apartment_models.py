"""
24030388 - Ishaq Modassir Mushtaq

Apartment model for apartment management operations.
Used by admin and dashboard GUI panels.
"""

from connection import Database_connection
from base_model import BaseModel


class Apartment(BaseModel):
    """Handles apartment CRUD operations."""

    def __init__(self, apartment_id=None, apartment_number=None, monthly_rent=None,
                 location_id=None, type=None, square_footage=None,
                 occupation_status=None, number_of_rooms=None):
        self.apartment_id = apartment_id
        self.apartment_number = apartment_number
        self.monthly_rent = monthly_rent
        self.location_id = location_id
        self.type = type
        self.square_footage = square_footage
        self.occupation_status = occupation_status
        self.number_of_rooms = number_of_rooms

    @staticmethod
    def get_all_apartments():
        """Fetch all apartments with location city and amenities."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT a.apartment_id, a.apartment_number, a.monthly_rent,
                       l.city AS location, a.type, a.square_footage,
                       a.occupation_status, a.number_of_rooms,
                       GROUP_CONCAT(am.name SEPARATOR ', ') AS amenities
                FROM apartment a
                LEFT JOIN location l ON a.location_id = l.location_id
                LEFT JOIN apartment_amenity aa ON a.apartment_id = aa.apartmentID
                LEFT JOIN amenity am ON aa.amenityID = am.amenity_id
                GROUP BY a.apartment_id
                ORDER BY a.apartment_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                status = r.get('occupation_status', '')
                if status == 'Vacant':
                    r['occupation_status'] = 'Available'
                elif status == 'Maintenance':
                    r['occupation_status'] = 'Under Maintenance'
                r['amenities'] = r.get('amenities') or ''
            return [Apartment.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching apartments: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_apartment_count():
        """Return total number of apartments."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM apartment")
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_apartment(self, apartment_number, location_city, apt_type,
                         monthly_rent, number_of_rooms, square_footage, occupation_status):
        """Update apartment details."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT location_id FROM location WHERE city = %s", (location_city,))
            loc_result = cursor.fetchone()
            if not loc_result:
                return False
            location_id = loc_result[0]

            db_status = occupation_status
            if occupation_status == 'Available':
                db_status = 'Vacant'
            elif occupation_status == 'Under Maintenance':
                db_status = 'Maintenance'

            query = ("UPDATE apartment SET apartment_number=%s, location_id=%s, type=%s, "
                     "monthly_rent=%s, number_of_rooms=%s, square_footage=%s, "
                     "occupation_status=%s WHERE apartment_id=%s")
            cursor.execute(query, (apartment_number, location_id, apt_type, monthly_rent,
                                   number_of_rooms, square_footage, db_status, self.apartment_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating apartment: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_apartment_status(self, status):
        """Change apartment occupancy status."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            db_status = status
            if status == 'Available':
                db_status = 'Vacant'
            elif status == 'Under Maintenance':
                db_status = 'Maintenance'
            cursor.execute("UPDATE apartment SET occupation_status=%s WHERE apartment_id=%s",
                           (db_status, self.apartment_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating apartment status: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_apartment_rent(self, new_rent):
        """Update monthly rent for an apartment."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE apartment SET monthly_rent=%s WHERE apartment_id=%s",
                           (new_rent, self.apartment_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating rent: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()


# Backward-compatible aliases
get_all_apartments = Apartment.get_all_apartments
get_apartment_count = Apartment.get_apartment_count


def update_apartment(apartment_id, apartment_number, location_city, apt_type,
                     monthly_rent, number_of_rooms, square_footage, occupation_status):
    return Apartment(apartment_id=apartment_id).update_apartment(
        apartment_number, location_city, apt_type, monthly_rent,
        number_of_rooms, square_footage, occupation_status)


def update_apartment_status(apartment_id, status):
    return Apartment(apartment_id=apartment_id).update_apartment_status(status)


def update_apartment_rent(apartment_id, new_rent):
    return Apartment(apartment_id=apartment_id).update_apartment_rent(new_rent)
