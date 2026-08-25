"""
24030388 - Ishaq Modassir Mushtaq

Complaint and enquiry models for front desk operations.
"""

from connection import Database_connection
from base_model import BaseModel
from datetime import date


def _notify(recipient_id, message, ntype="General"):
    """Fire-and-forget notification helper."""
    try:
        from tenant_models import Tenant
        Tenant.create_notification(recipient_id, message, ntype)
    except Exception as e:
        print(f"[frontdesk_models] notification skipped: {e}")


class Complaint(BaseModel):
    """Handles complaint CRUD operations."""

    def __init__(self, complaint_id=None, tenant_id=None, date_filed=None,
                 subject=None, description=None, status=None):
        self.complaint_id = complaint_id
        self.tenant_id = tenant_id
        self.date_filed = date_filed
        self.subject = subject
        self.description = description
        self.status = status

    @staticmethod
    def get_all_complaints():
        """Fetch all complaints with tenant name."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT c.complaint_id, c.tenant_id, c.date_filed, c.subject,
                       c.description, c.status,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name,
                       l.city AS location
                FROM complaint c
                JOIN user u ON c.tenant_id = u.user_id
                LEFT JOIN lease_agreement la ON c.tenant_id = la.tenantID AND la.status = 'ACTIVE'
                LEFT JOIN apartment a ON la.apartmentID = a.apartment_id
                LEFT JOIN location l ON a.location_id = l.location_id
                ORDER BY c.complaint_id DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                if r.get('date_filed'):
                    r['date_filed'] = str(r['date_filed'])
            return [Complaint.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching complaints: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_complaint_by_id(complaint_id):
        """Fetch a single complaint by ID."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT c.complaint_id, c.tenant_id, c.date_filed, c.subject,
                       c.description, c.status,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name
                FROM complaint c
                JOIN user u ON c.tenant_id = u.user_id
                WHERE c.complaint_id = %s
            """
            cursor.execute(query, (complaint_id,))
            result = cursor.fetchone()
            if result and result.get('date_filed'):
                result['date_filed'] = str(result['date_filed'])
            return Complaint.from_dict(result) if result else None
        except Exception as e:
            print(f"Error fetching complaint: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_complaints_for_tenant(tenant_id):
        """Fetch complaints filed by a specific tenant."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT complaint_id, tenant_id, date_filed, subject,
                       description, status
                FROM complaint
                WHERE tenant_id = %s
                ORDER BY complaint_id DESC
            """, (tenant_id,))
            results = cursor.fetchall()
            for r in results:
                if r.get('date_filed'):
                    r['date_filed'] = str(r['date_filed'])
            return [Complaint.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching complaints for tenant {tenant_id}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_complaint_stats():
        """Return summary statistics for complaints."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(status = 'Open') AS open_count,
                    SUM(status = 'Under Review') AS under_review_count,
                    SUM(status = 'Resolved') AS resolved_count,
                    SUM(status = 'Closed') AS closed_count
                FROM complaint
            """)
            row = cursor.fetchone()
            return {k: int(v or 0) for k, v in row.items()} if row else {}
        except Exception as e:
            print(f"Error fetching complaint stats: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def create_complaint(tenant_id, subject, description):
        """Insert a new complaint and return the new complaint_id, or None on failure."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO complaint (tenant_id, date_filed, subject, description, status)
                VALUES (%s, %s, %s, %s, 'Open')
            """
            cursor.execute(query, (tenant_id, date.today(), subject, description))
            conn.commit()
            cid = cursor.lastrowid

            _notify(tenant_id,
                    f"Your complaint '{subject}' (#{cid}) has been filed and is now Open.",
                    "General")

            return cid
        except Exception as e:
            print(f"Error creating complaint: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()

    def update_complaint_status(self, status):
        """Update the status of a complaint.
        Valid statuses: Open, Under Review, Resolved, Closed.
        Returns True on success."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE complaint SET status=%s WHERE complaint_id=%s",
                           (status, self.complaint_id))
            conn.commit()
            ok = cursor.rowcount > 0

            # Notify the tenant
            if ok:
                cursor.execute(
                    "SELECT tenant_id FROM complaint WHERE complaint_id=%s",
                    (self.complaint_id,))
                row = cursor.fetchone()
                if row:
                    _notify(row[0],
                            f"Your complaint #{self.complaint_id} status has been updated to '{status}'.",
                            "General")
            return ok
        except Exception as e:
            print(f"Error updating complaint status: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def delete_complaint(self):
        """Delete a complaint by ID. Returns True on success."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM complaint WHERE complaint_id=%s", (self.complaint_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting complaint: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()


class Enquiry(BaseModel):
    """Handles enquiry CRUD operations."""

    def __init__(self, enquiry_id=None, tenant_id=None, tenant_name=None,
                 enquiry_details=None, handled_by=None, date_logged=None):
        self.enquiry_id = enquiry_id
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.enquiry_details = enquiry_details
        self.handled_by = handled_by
        self.date_logged = date_logged

    @staticmethod
    def get_all_enquiries():
        """Fetch all enquiries ordered by most recent first."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT enquiry_id, tenant_id, tenant_name, enquiry_details,
                       handled_by, date_logged
                FROM enquiry
                ORDER BY enquiry_id DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                if r.get('date_logged'):
                    r['date_logged'] = str(r['date_logged'])
            return [Enquiry.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching enquiries: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_enquiries_for_tenant(tenant_id):
        """Fetch enquiries related to a specific tenant."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT enquiry_id, tenant_id, tenant_name, enquiry_details,
                       handled_by, date_logged
                FROM enquiry
                WHERE tenant_id = %s
                ORDER BY enquiry_id DESC
            """, (tenant_id,))
            results = cursor.fetchall()
            for r in results:
                if r.get('date_logged'):
                    r['date_logged'] = str(r['date_logged'])
            return [Enquiry.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching enquiries for tenant {tenant_id}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def create_enquiry(tenant_name, enquiry_details, handled_by, tenant_id=None):
        """Log a new enquiry and return the new enquiry_id, or None on failure."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO enquiry (tenant_id, tenant_name, enquiry_details, handled_by, date_logged)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (tenant_id, tenant_name, enquiry_details, handled_by, date.today()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating enquiry: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()


# Backward-compatible aliases
get_all_complaints = Complaint.get_all_complaints
get_complaint_by_id = Complaint.get_complaint_by_id
get_complaints_for_tenant = Complaint.get_complaints_for_tenant
get_complaint_stats = Complaint.get_complaint_stats
create_complaint = Complaint.create_complaint
get_all_enquiries = Enquiry.get_all_enquiries
get_enquiries_for_tenant = Enquiry.get_enquiries_for_tenant
create_enquiry = Enquiry.create_enquiry


def update_complaint_status(complaint_id, status):
    return Complaint(complaint_id=complaint_id).update_complaint_status(status)


def delete_complaint(complaint_id):
    return Complaint(complaint_id=complaint_id).delete_complaint()
