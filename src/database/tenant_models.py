"""
24030388 - Ishaq Modassir Mushtaq

Tenant and notification models for tenant management operations.
"""

from connection import Database_connection
from base_model import BaseModel
from datetime import date as _date, datetime as _datetime


class Tenant(BaseModel):
    """Handles tenant-specific database operations."""

    def __init__(self, tenant_id=None, lease_status=None, occupation=None,
                 ni_number=None, references=None):
        self.tenant_id = tenant_id
        self.lease_status = lease_status
        self.occupation = occupation
        self.ni_number = ni_number
        self.references = references

    @staticmethod
    def get_all_tenants():
        """Fetch all tenants with user info and active lease details."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT u.user_id, u.fname, u.lname, u.email, u.phone_number,
                       u.date_of_birth, t.occupation, t.ni_number, t.`references`,
                       a.apartment_number, la.status AS lease_status,
                       l.city AS location
                FROM user u
                JOIN tenant t ON u.user_id = t.tenant_id
                LEFT JOIN lease_agreement la ON u.user_id = la.tenantID AND la.status = 'ACTIVE'
                LEFT JOIN apartment a ON la.apartmentID = a.apartment_id
                LEFT JOIN location l ON a.location_id = l.location_id
                ORDER BY u.user_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                if r.get('date_of_birth'):
                    r['date_of_birth'] = str(r['date_of_birth'])
            return [Tenant.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching tenants: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    def get_tenant_profile(self):
        """Fetch full profile for a tenant: user + tenant-specific data.
        Delegates to User.get_user_by_id() in user_models to avoid duplicate SQL."""
        from user_models import User
        return User.get_user_by_id(self.tenant_id)

    def update_tenant_contact(self, email=None, phone=None):
        """Update email and/or phone number for a user."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            sets, vals = [], []
            if email:
                sets.append("email = %s"); vals.append(email)
            if phone:
                sets.append("phone_number = %s"); vals.append(phone)
            if not sets:
                return True
            vals.append(self.tenant_id)
            cursor.execute(f"UPDATE user SET {', '.join(sets)} WHERE user_id = %s", tuple(vals))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating contact info: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def update_tenant_personal(self, fname=None, lname=None):
        """Update first name and/or last name for a user."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            sets, vals = [], []
            if fname:
                sets.append("fname = %s"); vals.append(fname)
            if lname:
                sets.append("lname = %s"); vals.append(lname)
            if not sets:
                return True
            vals.append(self.tenant_id)
            cursor.execute(f"UPDATE user SET {', '.join(sets)} WHERE user_id = %s", tuple(vals))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating personal info: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def get_active_lease_for_tenant(self):
        """Get the most recent active or pending lease for a tenant with full details."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT la.leaseID, la.tenantID, la.apartmentID,
                       a.apartment_number,
                       la.start_date, la.end_date, la.monthly_rent,
                       la.deposit_amount, la.lease_term_months, la.status,
                       la.termination_date, la.early_termination_notice,
                       la.termination_penalty_percent
                FROM lease_agreement la
                JOIN apartment a ON la.apartmentID = a.apartment_id
                WHERE la.tenantID = %s
                AND la.status IN ('ACTIVE', 'PENDING')
                ORDER BY la.start_date DESC
                LIMIT 1
            """
            cursor.execute(query, (self.tenant_id,))
            result = cursor.fetchone()
            if result:
                for key in ('start_date', 'end_date', 'termination_date'):
                    if result.get(key):
                        result[key] = str(result[key])
                for key in ('monthly_rent', 'deposit_amount', 'termination_penalty_percent'):
                    if result.get(key) is not None:
                        result[key] = float(result[key])
            return result
        except Exception as e:
            print(f"Error fetching active lease: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()

    def request_early_termination(self, lease_id, reason=""):
        """Submit early termination — terminates the lease and logs a complaint."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE lease_agreement SET status='TERMINATED', termination_date=CURDATE() "
                "WHERE leaseID = %s",
                (lease_id,)
            )
            # Log complaint with the reason if provided
            if reason and self.tenant_id:
                cursor.execute(
                    "INSERT INTO complaint (tenant_id, date_filed, subject, description, status) "
                    "VALUES (%s, %s, %s, %s, 'Open')",
                    (self.tenant_id, _date.today(),
                     "Early Lease Termination Request", reason)
                )
            conn.commit()

            # Notify the tenant
            Tenant.create_notification(
                self.tenant_id,
                f"Your early termination request for lease #{lease_id} has been processed. "
                f"The lease is now terminated.",
                "Lease"
            )

            return True
        except Exception as e:
            print(f"Error processing early termination: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def change_tenant_password(self, old_password, new_password):
        """Change a tenant's password after verifying the current one.
        Delegates to User.change_password() in user_models to avoid duplication."""
        from user_models import User
        return User(user_id=self.tenant_id).change_password(old_password, new_password)

    def get_notifications_for_tenant(self):
        """Fetch all notifications for a tenant from the notification table.
        Returns a list of notification dicts compatible with NotificationsPanel."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT notification_id, recipient_id, message,
                       notification_date, is_read, notification_type
                FROM notification
                WHERE recipient_id = %s
                ORDER BY notification_date DESC, notification_id DESC
            """, (self.tenant_id,))
            results = cursor.fetchall()
            notifications = []
            for r in results:
                notifications.append({
                    "notificationID": r["notification_id"],
                    "message": r["message"],
                    "notificationDate": str(r["notification_date"]) if r.get("notification_date") else "",
                    "isRead": bool(r["is_read"]),
                    "notificationType": r["notification_type"] or "General",
                })
            return notifications
        except Exception as e:
            print(f"Error fetching notifications: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def create_notification(recipient_id, message, notification_type="General"):
        """Insert a new notification into the notification table.
        Returns the new notification_id, or None on failure."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notification (recipient_id, message, notification_date, "
                "is_read, notification_type) VALUES (%s, %s, %s, 0, %s)",
                (recipient_id, message, _date.today(), notification_type)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating notification: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def mark_notification_read(notification_id):
        """Mark a single notification as read. Returns True on success."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notification SET is_read = 1 WHERE notification_id = %s",
                (notification_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error marking notification read: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def mark_all_notifications_read(self):
        """Mark all notifications as read for a given user. Returns True on success."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notification SET is_read = 1 WHERE recipient_id = %s AND is_read = 0",
                (self.tenant_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking all notifications read: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()


# Backward-compatible aliases
get_all_tenants = Tenant.get_all_tenants
create_notification = Tenant.create_notification
mark_notification_read = Tenant.mark_notification_read


def get_tenant_profile(user_id):
    return Tenant(tenant_id=user_id).get_tenant_profile()


def update_tenant_contact(user_id, email=None, phone=None):
    return Tenant(tenant_id=user_id).update_tenant_contact(email=email, phone=phone)


def update_tenant_personal(user_id, fname=None, lname=None):
    return Tenant(tenant_id=user_id).update_tenant_personal(fname=fname, lname=lname)


def get_active_lease_for_tenant(user_id):
    return Tenant(tenant_id=user_id).get_active_lease_for_tenant()


def request_early_termination(lease_id, tenant_id, reason=""):
    return Tenant(tenant_id=tenant_id).request_early_termination(lease_id, reason=reason)


def change_tenant_password(user_id, old_password, new_password):
    return Tenant(tenant_id=user_id).change_tenant_password(old_password, new_password)


def get_notifications_for_tenant(user_id):
    return Tenant(tenant_id=user_id).get_notifications_for_tenant()


def mark_all_notifications_read(user_id):
    return Tenant(tenant_id=user_id).mark_all_notifications_read()


# Helper resolvers used internally.

def _resolve_tenant_for_invoice(cursor, invoice_id):
    """Helper: resolve tenant user_id from an invoice_id."""
    cursor.execute("""
        SELECT la.tenantID FROM Invoice i
        JOIN lease_agreement la ON i.leaseID = la.leaseID
        WHERE i.invoiceID = %s
    """, (invoice_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def _resolve_tenant_for_lease(cursor, lease_id):
    """Helper: resolve tenant user_id from a lease_id."""
    cursor.execute(
        "SELECT tenantID FROM lease_agreement WHERE leaseID = %s", (lease_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def _resolve_tenant_for_request(cursor, request_id):
    """Helper: resolve tenant user_id from a maintenance request_id."""
    cursor.execute(
        "SELECT reportedByTenant_id FROM maintenance_request WHERE request_id = %s",
        (request_id,))
    row = cursor.fetchone()
    return row[0] if row else None


def _resolve_tenant_for_complaint(cursor, complaint_id):
    """Helper: resolve tenant user_id from a complaint_id."""
    cursor.execute(
        "SELECT tenant_id FROM complaint WHERE complaint_id = %s", (complaint_id,))
    row = cursor.fetchone()
    return row[0] if row else None
