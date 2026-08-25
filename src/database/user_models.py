"""
24030388 - Ishaq Modassir Mushtaq

User and staff member models for account management operations.
"""

from connection import Database_connection
from base_model import BaseModel
from datetime import date
import bcrypt

STAFF_ROLES = {'Administrator', 'Manager', 'Front Desk Staff', 'Finance Manager', 'Maintenance Staff'}


class User(BaseModel):
    """Handles user CRUD and password operations."""

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
    def get_all_users():
        """Fetch all users with optional tenant extra fields."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT u.user_id, u.username, u.fname, u.lname, u.email,
                       u.phone_number, u.date_of_birth, u.role,
                       t.occupation, t.ni_number, t.`references`
                FROM user u
                LEFT JOIN tenant t ON u.user_id = t.tenant_id
                ORDER BY u.user_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                if r.get('date_of_birth'):
                    r['date_of_birth'] = str(r['date_of_birth'])
            return [User.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_user_by_id(user_id):
        """Fetch a single user by ID with tenant details."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT u.user_id, u.username, u.fname, u.lname, u.email,
                       u.phone_number, u.date_of_birth, u.role,
                       t.occupation, t.ni_number, t.`references`
                FROM user u
                LEFT JOIN tenant t ON u.user_id = t.tenant_id
                WHERE u.user_id = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result and result.get('date_of_birth'):
                result['date_of_birth'] = str(result['date_of_birth'])
            return User.from_dict(result)
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def admin_add_user(fname, lname, email, phone, dob, role, username, password,
                       occupation=None, ni_number=None, references=None):
        """Admin adds a new user with a hashed password and inserts into the role-specific table."""
        db = Database_connection()
        conn = db.connect()
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor = conn.cursor()
            query = ("INSERT INTO user (fname, lname, email, phone_number, date_of_birth, "
                     "role, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
            cursor.execute(query, (fname, lname, email, phone, dob, role, username, hashed_password))
            new_id = cursor.lastrowid

            if role == 'Tenant':
                cursor.execute(
                    "INSERT INTO tenant (tenant_id, occupation, ni_number, `references`) "
                    "VALUES (%s, %s, %s, %s)",
                    (new_id, occupation, ni_number, references)
                )
            elif role in STAFF_ROLES:
                cursor.execute(
                    "INSERT INTO staff_member (employee_id, role, start_date) VALUES (%s, %s, %s)",
                    (new_id, role, date.today())
                )

            conn.commit()
            return new_id
        except Exception as e:
            print(f"Error adding user: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_user(self, fname, lname, email, phone, dob, role, username,
                    occupation=None, ni_number=None, references=None):
        """Update user details and tenant-specific fields if applicable."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            query = ("UPDATE user SET fname=%s, lname=%s, email=%s, phone_number=%s, "
                     "date_of_birth=%s, role=%s, username=%s WHERE user_id=%s")
            cursor.execute(query, (fname, lname, email, phone, dob, role, username, self.user_id))

            if role == 'Tenant':
                cursor.execute("SELECT tenant_id FROM tenant WHERE tenant_id = %s", (self.user_id,))
                if cursor.fetchone():
                    cursor.execute(
                        "UPDATE tenant SET occupation=%s, ni_number=%s, `references`=%s "
                        "WHERE tenant_id=%s",
                        (occupation, ni_number, references, self.user_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO tenant (tenant_id, occupation, ni_number, `references`) "
                        "VALUES (%s, %s, %s, %s)",
                        (self.user_id, occupation, ni_number, references)
                    )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def delete_user(self):
        """Delete a user (cascades to tenant/staff_member via FK)."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user WHERE user_id = %s", (self.user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_user_count():
        """Return total number of users."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user")
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def change_password(self, old_password, new_password):
        """Change a user's password after verifying the current one."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM user WHERE user_id = %s", (self.user_id,))
            result = cursor.fetchone()
            if not result:
                return False
            stored = result[0]
            if isinstance(stored, str):
                stored = stored.encode('utf-8')
            if not bcrypt.checkpw(old_password.encode('utf-8'), stored):
                return False
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE user SET password=%s WHERE user_id=%s", (new_hash, self.user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()


class StaffMember(BaseModel):
    """Handles staff member database operations."""

    def __init__(self, employee_id=None, salary=None, role=None,
                 start_date=None, location_id=None):
        self.employee_id = employee_id
        self.salary = salary
        self.role = role
        self.start_date = start_date
        self.location_id = location_id

    @staticmethod
    def get_all_staff():
        """Fetch all staff members with user info and location."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT u.user_id, u.fname, u.lname, u.email, u.phone_number,
                       u.date_of_birth, u.role AS user_role,
                       sm.employee_id, sm.salary, sm.role AS staff_role,
                       sm.start_date, sm.location_id,
                       l.city AS location
                FROM user u
                JOIN staff_member sm ON u.user_id = sm.employee_id
                LEFT JOIN location l ON sm.location_id = l.location_id
                ORDER BY u.user_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                if r.get('date_of_birth'):
                    r['date_of_birth'] = str(r['date_of_birth'])
                if r.get('start_date'):
                    r['start_date'] = str(r['start_date'])
                if r.get('salary'):
                    r['salary'] = float(r['salary'])
            return [StaffMember.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching staff: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_staff_member(self, salary=None, role=None, start_date=None, location_id=None):
        """Update staff_member table fields."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            sets, vals = [], []
            if salary is not None:
                sets.append("salary=%s"); vals.append(salary)
            if role is not None:
                sets.append("role=%s"); vals.append(role)
            if start_date is not None:
                sets.append("start_date=%s"); vals.append(start_date)
            if location_id is not None:
                sets.append("location_id=%s"); vals.append(location_id)
            if not sets:
                return True
            vals.append(self.employee_id)
            cursor.execute(f"UPDATE staff_member SET {', '.join(sets)} WHERE employee_id=%s",
                           tuple(vals))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating staff member: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()


# Backward-compatible aliases
# So existing `from user_models import get_all_users` still works
get_all_users = User.get_all_users
get_user_by_id = User.get_user_by_id
admin_add_user = User.admin_add_user
get_user_count = User.get_user_count
get_all_staff = StaffMember.get_all_staff


def update_user(user_id, fname, lname, email, phone, dob, role, username,
                occupation=None, ni_number=None, references=None):
    return User(user_id=user_id).update_user(
        fname, lname, email, phone, dob, role, username,
        occupation=occupation, ni_number=ni_number, references=references)


def delete_user(user_id):
    return User(user_id=user_id).delete_user()


def change_password(user_id, old_password, new_password):
    return User(user_id=user_id).change_password(old_password, new_password)


def update_staff_member(employee_id, salary=None, role=None, start_date=None, location_id=None):
    return StaffMember(employee_id=employee_id).update_staff_member(
        salary=salary, role=role, start_date=start_date, location_id=location_id)
