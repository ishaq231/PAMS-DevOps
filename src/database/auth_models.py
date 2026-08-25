"""
24030388 - Ishaq Modassir Mushtaq

Authentication model used by login and signup windows.
"""

from connection import Database_connection
from base_model import BaseModel
from datetime import date
import bcrypt

STAFF_ROLES = {'Administrator', 'Manager', 'Front Desk Staff', 'Finance Manager', 'Maintenance Staff'}


class User(BaseModel):
    """Handles authentication-related database operations."""

    STAFF_ROLES = STAFF_ROLES

    def __init__(self, user_id=None, fname=None, lname=None, email=None,
                 phone_number=None, date_of_birth=None, role=None,
                 username=None, password=None):
        self.user_id = user_id
        self.fname = fname
        self.lname = lname
        self.email = email
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.role = role
        self.username = username
        self.password = password

    @staticmethod
    def signup(fname, lname, email, phone_number, DoB, role, username, password):
        """Register a new user and insert them into their role-specific table."""
        db = Database_connection()
        conn = db.connect()
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor = conn.cursor()

            query = ("INSERT INTO user (fname, lname, email, phone_number, date_of_birth, "
                     "role, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
            values = (fname, lname, email, phone_number, DoB, role, username, hashed_password)
            cursor.execute(query, values)
            new_user_id = cursor.lastrowid

            if role == 'Tenant':
                cursor.execute(
                    "INSERT INTO tenant (tenant_id) VALUES (%s)",
                    (new_user_id,)
                )
            elif role in STAFF_ROLES:
                cursor.execute(
                    "INSERT INTO staff_member (employee_id, role, start_date) VALUES (%s, %s, %s)",
                    (new_user_id, role, date.today())
                )

            conn.commit()
            print("User signed up successfully!")
            return True

        except Exception as e:
            print(f"Failed to sign up user: {e}")
            return False

        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def login(username, password):
        """Authenticate a user and return {user_id, name, role, location_id, location_name} or False."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            query = "SELECT user_id, fname, lname, password, role FROM user WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            if result:
                user_id, fname, lname, stored_password, role = result
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    print("Login successful!")

                    location_id = None
                    location_name = None

                    if role in STAFF_ROLES and role not in ('Administrator', 'Manager'):
                        cursor.execute(
                            "SELECT sm.location_id, l.city "
                            "FROM staff_member sm "
                            "LEFT JOIN location l ON sm.location_id = l.location_id "
                            "WHERE sm.employee_id = %s",
                            (user_id,)
                        )
                        loc_row = cursor.fetchone()
                        if loc_row:
                            location_id = loc_row[0]
                            location_name = loc_row[1]

                    elif role == 'Tenant':
                        cursor.execute(
                            "SELECT l.location_id, l.city "
                            "FROM lease_agreement la "
                            "JOIN apartment a ON la.apartmentID = a.apartment_id "
                            "JOIN location l ON a.location_id = l.location_id "
                            "WHERE la.tenantID = %s AND la.status = 'ACTIVE' "
                            "ORDER BY la.start_date DESC LIMIT 1",
                            (user_id,)
                        )
                        loc_row = cursor.fetchone()
                        if loc_row:
                            location_id = loc_row[0]
                            location_name = loc_row[1]

                    return {
                        "user_id": user_id,
                        "name": f"{fname} {lname}",
                        "role": role,
                        "location_id": location_id,
                        "location_name": location_name,
                    }
                else:
                    print("Incorrect password.")
                    return False
            else:
                print("User not found.")
                return False
        except Exception as e:
            print(f"Error during login: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_role_by_code(signup_code):
        """Return the role_name matching a staff signup code, or None if invalid."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT role_name FROM staff_role WHERE signup_code = %s", (signup_code,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error validating staff code: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def does_user_exist(username, email):
        """Return True if a user with the given username or email already exists."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE username = %s OR email = %s",
                           (username, email))
            result = cursor.fetchone()
            if result is not None:
                print("User or email already exists.")
                return True
            print("User does not exist.")
            return False
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()


# Backward-compatible aliases
signup = User.signup
login = User.login
get_role_by_code = User.get_role_by_code
does_user_exist = User.does_user_exist
