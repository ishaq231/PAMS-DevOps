"""
24030388 - Ishaq Modassir Mushtaq

Lease agreement model for lease tracking and tenant lease views.
"""

from connection import Database_connection
from base_model import BaseModel


def _notify(recipient_id, message, ntype="Lease"):
    """Fire-and-forget notification helper."""
    try:
        from tenant_models import Tenant
        Tenant.create_notification(recipient_id, message, ntype)
    except Exception as e:
        print(f"[lease_models] notification skipped: {e}")


class LeaseAgreement(BaseModel):
    """Handles lease agreement CRUD operations."""

    def __init__(self, leaseID=None, tenantID=None, apartmentID=None,
                 start_date=None, end_date=None, monthly_rent=None,
                 deposit_amount=None, lease_term_months=None, status=None,
                 termination_date=None, early_termination_notice=None,
                 termination_penalty_percent=None):
        self.leaseID = leaseID
        self.tenantID = tenantID
        self.apartmentID = apartmentID
        self.start_date = start_date
        self.end_date = end_date
        self.monthly_rent = monthly_rent
        self.deposit_amount = deposit_amount
        self.lease_term_months = lease_term_months
        self.status = status
        self.termination_date = termination_date
        self.early_termination_notice = early_termination_notice
        self.termination_penalty_percent = termination_penalty_percent

    @staticmethod
    def get_all_leases():
        """Fetch all lease agreements with tenant and apartment info."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT la.leaseID, la.tenantID, la.apartmentID,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name,
                       a.apartment_number,
                       la.start_date, la.end_date, la.monthly_rent,
                       la.deposit_amount, la.lease_term_months, la.status,
                       la.termination_date, la.early_termination_notice,
                       la.termination_penalty_percent,
                       l.city AS location
                FROM lease_agreement la
                JOIN user u ON la.tenantID = u.user_id
                JOIN apartment a ON la.apartmentID = a.apartment_id
                LEFT JOIN location l ON a.location_id = l.location_id
                ORDER BY la.leaseID
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                for key in ('start_date', 'end_date', 'termination_date'):
                    if r.get(key):
                        r[key] = str(r[key])
            return [LeaseAgreement.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching leases: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_leases_for_user(user_id):
        """Fetch leases for a specific tenant user."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT la.leaseID, a.apartment_number,
                       la.start_date, la.end_date, la.monthly_rent, la.status
                FROM lease_agreement la
                JOIN apartment a ON la.apartmentID = a.apartment_id
                WHERE la.tenantID = %s
                ORDER BY la.start_date DESC
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            for r in results:
                for key in ('start_date', 'end_date'):
                    if r.get(key):
                        r[key] = str(r[key])
            return [LeaseAgreement.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching user leases: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def create_lease(tenant_id, apartment_id, start_date, end_date, monthly_rent,
                     deposit, term_months):
        """Create a new lease agreement and mark the apartment as Occupied."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            query = ("INSERT INTO lease_agreement "
                     "(tenantID, apartmentID, start_date, end_date, monthly_rent, "
                     "deposit_amount, lease_term_months, status, "
                     "early_termination_notice, termination_penalty_percent) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE', 30, 5.00)")
            cursor.execute(query, (tenant_id, apartment_id, start_date, end_date,
                                   monthly_rent, deposit, term_months))
            cursor.execute("UPDATE apartment SET occupation_status='Occupied' "
                           "WHERE apartment_id=%s", (apartment_id,))
            conn.commit()

            _notify(tenant_id,
                    f"Your new lease has been created. Start: {start_date}, End: {end_date}, "
                    f"Monthly rent: \u00a3{float(monthly_rent):,.2f}.",
                    "Lease")

            return True
        except Exception as e:
            print(f"Error creating lease: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_lease(self, start_date, end_date, monthly_rent, term_months, status):
        """Update lease agreement details."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            query = ("UPDATE lease_agreement SET start_date=%s, end_date=%s, monthly_rent=%s, "
                     "lease_term_months=%s, status=%s WHERE leaseID=%s")
            cursor.execute(query, (start_date, end_date, monthly_rent, term_months, status, self.leaseID))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating lease: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_lease_status(self, status):
        """Update only the status field of a lease."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE lease_agreement SET status=%s WHERE leaseID=%s",
                           (status, self.leaseID))
            conn.commit()

            # Notify the tenant
            cursor.execute("SELECT tenantID FROM lease_agreement WHERE leaseID=%s", (self.leaseID,))
            row = cursor.fetchone()
            if row:
                _notify(row[0],
                        f"Your lease (#{self.leaseID}) status has been updated to '{status}'.",
                        "Lease")

            return True
        except Exception as e:
            print(f"Error updating lease status: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def terminate_lease(self):
        """Terminate a lease and set termination date to today."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE lease_agreement SET status='TERMINATED', termination_date=CURDATE() "
                "WHERE leaseID=%s", (self.leaseID,))
            conn.commit()

            # Notify the tenant
            cursor.execute("SELECT tenantID FROM lease_agreement WHERE leaseID=%s", (self.leaseID,))
            row = cursor.fetchone()
            if row:
                _notify(row[0],
                        f"Your lease (#{self.leaseID}) has been terminated.",
                        "Lease")

            return True
        except Exception as e:
            print(f"Error terminating lease: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()


# Backward-compatible aliases
get_all_leases = LeaseAgreement.get_all_leases
get_leases_for_user = LeaseAgreement.get_leases_for_user
create_lease = LeaseAgreement.create_lease


def update_lease(lease_id, start_date, end_date, monthly_rent, term_months, status):
    return LeaseAgreement(leaseID=lease_id).update_lease(
        start_date, end_date, monthly_rent, term_months, status)


def update_lease_status(lease_id, status):
    return LeaseAgreement(leaseID=lease_id).update_lease_status(status)


def terminate_lease(lease_id):
    return LeaseAgreement(leaseID=lease_id).terminate_lease()
