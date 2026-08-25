"""
24030388 - Ishaq Modassir Mushtaq

Maintenance and maintenance log models for request management.
Used by maintenance, tenant, front desk, and dashboard panels.
"""

from connection import Database_connection
from base_model import BaseModel

_DATE_FIELDS = ('report_date', 'resolved_date', 'scheduled_date')


def _notify(recipient_id, message, ntype="Maintenance"):
    """Fire-and-forget notification helper."""
    try:
        from tenant_models import Tenant
        Tenant.create_notification(recipient_id, message, ntype)
    except Exception as e:
        print(f"[maintenance_models] notification skipped: {e}")


def _fmt_dates(row: dict) -> dict:
    """Convert date objects to strings in-place."""
    for key in _DATE_FIELDS:
        if row.get(key):
            row[key] = str(row[key])
    return row


class Maintenance(BaseModel):
    """Handles maintenance request CRUD operations."""

    def __init__(self, request_id=None, apartment_id=None,
                 reportedByTenant_id=None, assignedStaff_id=None,
                 description=None, priority=None, status=None,
                 report_date=None, resolved_date=None, cost=None,
                 scheduled_date=None, category=None):
        self.request_id = request_id
        self.apartment_id = apartment_id
        self.reportedByTenant_id = reportedByTenant_id
        self.assignedStaff_id = assignedStaff_id
        self.description = description
        self.priority = priority
        self.status = status
        self.report_date = report_date
        self.resolved_date = resolved_date
        self.cost = cost
        self.scheduled_date = scheduled_date
        self.category = category

    @staticmethod
    def get_all_maintenance_requests():
        """Fetch all maintenance requests with related tenant, apartment, and staff info."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT mr.request_id, mr.description, mr.priority, mr.status,
                       mr.category, mr.report_date, mr.scheduled_date,
                       mr.resolved_date, mr.cost,
                       a.apartment_number, a.apartment_id,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name,
                       u.user_id AS tenant_id,
                       mr.assignedStaff_id,
                       CONCAT(s.fname, ' ', s.lname) AS staff_name,
                       l.city AS location
                FROM maintenance_request mr
                JOIN apartment a ON mr.apartment_id = a.apartment_id
                JOIN user u ON mr.reportedByTenant_id = u.user_id
                LEFT JOIN user s ON mr.assignedStaff_id = s.user_id
                LEFT JOIN location l ON a.location_id = l.location_id
                ORDER BY mr.request_id
            """
            cursor.execute(query)
            return [Maintenance.from_dict(_fmt_dates(r)) for r in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching maintenance requests: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_maintenance_for_tenant(user_id):
        """Fetch maintenance requests reported by a specific tenant."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT mr.request_id, mr.description, mr.priority, mr.status,
                       mr.category, mr.report_date, mr.scheduled_date,
                       mr.resolved_date, mr.cost,
                       a.apartment_number,
                       CONCAT(s.fname, ' ', s.lname) AS staff_name
                FROM maintenance_request mr
                JOIN apartment a ON mr.apartment_id = a.apartment_id
                LEFT JOIN user s ON mr.assignedStaff_id = s.user_id
                WHERE mr.reportedByTenant_id = %s
                ORDER BY mr.request_id DESC
            """
            cursor.execute(query, (user_id,))
            return [Maintenance.from_dict(_fmt_dates(r)) for r in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching tenant maintenance: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_maintenance_for_staff(user_id):
        """Fetch maintenance requests assigned to a specific staff member."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT mr.request_id, mr.description, mr.priority, mr.status,
                       mr.category, mr.report_date, mr.scheduled_date,
                       mr.resolved_date, mr.cost,
                       a.apartment_number,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name
                FROM maintenance_request mr
                JOIN apartment a ON mr.apartment_id = a.apartment_id
                JOIN user u ON mr.reportedByTenant_id = u.user_id
                WHERE mr.assignedStaff_id = %s
                ORDER BY mr.request_id DESC
            """
            cursor.execute(query, (user_id,))
            return [Maintenance.from_dict(_fmt_dates(r)) for r in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching staff maintenance: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_request_by_id(request_id):
        """Fetch a single maintenance request by ID."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT mr.request_id, mr.description, mr.priority, mr.status,
                       mr.category, mr.report_date, mr.scheduled_date,
                       mr.resolved_date, mr.cost,
                       a.apartment_number, a.apartment_id,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name,
                       u.user_id AS tenant_id,
                       mr.assignedStaff_id,
                       CONCAT(s.fname, ' ', s.lname) AS staff_name
                FROM maintenance_request mr
                JOIN apartment a ON mr.apartment_id = a.apartment_id
                JOIN user u ON mr.reportedByTenant_id = u.user_id
                LEFT JOIN user s ON mr.assignedStaff_id = s.user_id
                WHERE mr.request_id = %s
            """, (request_id,))
            row = cursor.fetchone()
            return Maintenance.from_dict(_fmt_dates(row)) if row else None
        except Exception as e:
            print(f"Error fetching request {request_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_staff_availability():
        """Return maintenance staff with current job counts and availability.
        Only returns staff whose role is 'Maintenance Staff'.
        Returns list of dicts: user_id, name, role, current_jobs, max_jobs, available."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT sm.employee_id AS user_id,
                       CONCAT(u.fname, ' ', u.lname) AS name,
                       COALESCE(sm.role, u.role) AS role,
                       COUNT(mr.request_id) AS current_jobs,
                       5 AS max_jobs
                FROM staff_member sm
                JOIN user u ON sm.employee_id = u.user_id
                LEFT JOIN maintenance_request mr
                    ON mr.assignedStaff_id = sm.employee_id
                    AND mr.status NOT IN ('Resolved', 'Closed')
                WHERE sm.role = 'Maintenance Staff' OR u.role = 'Maintenance Staff'
                GROUP BY sm.employee_id, u.fname, u.lname, sm.role, u.role
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                r['available'] = r['current_jobs'] < r['max_jobs']
            return results
        except Exception as e:
            print(f"Error fetching staff availability: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_all_staff():
        """Return all staff members (for assignment to any request)."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT sm.employee_id AS user_id,
                       CONCAT(u.fname, ' ', u.lname) AS name,
                       COALESCE(sm.role, u.role) AS role
                FROM staff_member sm
                JOIN user u ON sm.employee_id = u.user_id
                ORDER BY u.fname
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching all staff: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_maintenance_stats():
        """Return summary statistics for maintenance requests (for dashboard)."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(status = 'Open') AS open_count,
                    SUM(status = 'In Progress') AS in_progress_count,
                    SUM(status = 'Resolved') AS resolved_count,
                    SUM(status = 'Closed') AS closed_count,
                    SUM(priority = 'Emergency') AS emergency_count,
                    SUM(priority = 'High') AS high_count
                FROM maintenance_request
            """)
            row = cursor.fetchone()
            # Convert Decimal/None to int
            return {k: int(v or 0) for k, v in row.items()} if row else {}
        except Exception as e:
            print(f"Error fetching maintenance stats: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def create_maintenance_request(apartment_id, tenant_id, description,
                                   priority="Low", category="General"):
        """Create a new maintenance request. Returns new request_id or None."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO maintenance_request
                    (apartment_id, reportedByTenant_id, description, priority,
                     category, status, report_date, cost)
                VALUES (%s, %s, %s, %s, %s, 'Open', NOW(), 0.00)
            """, (apartment_id, tenant_id, description, priority, category))
            conn.commit()
            req_id = cursor.lastrowid

            _notify(tenant_id,
                    f"Maintenance request #{req_id} submitted ({priority} priority). We will review it shortly.",
                    "Maintenance")

            return req_id
        except Exception as e:
            print(f"Error creating maintenance request: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()

    def update_maintenance_status(self, new_status):
        """Update the status of a maintenance request.
        Valid statuses: Open, In Progress, Resolved, Closed.
        Sets resolved_date automatically when Resolved."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            if new_status == "Resolved":
                cursor.execute("""
                    UPDATE maintenance_request
                    SET status = %s, resolved_date = CURDATE()
                    WHERE request_id = %s
                """, (new_status, self.request_id))
            else:
                cursor.execute("""
                    UPDATE maintenance_request SET status = %s WHERE request_id = %s
                """, (new_status, self.request_id))
            conn.commit()
            ok = cursor.rowcount > 0

            # Notify the tenant
            if ok:
                cursor.execute(
                    "SELECT reportedByTenant_id FROM maintenance_request WHERE request_id = %s",
                    (self.request_id,))
                row = cursor.fetchone()
                if row:
                    _notify(row[0],
                            f"Maintenance request #{self.request_id} status updated to '{new_status}'.",
                            "Maintenance")
            return ok
        except Exception as e:
            print(f"Error updating maintenance status: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def update_maintenance_priority(self, priority):
        """Update the priority of a maintenance request.
        Valid priorities: Low, Medium, High, Emergency."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE maintenance_request SET priority = %s WHERE request_id = %s
            """, (priority, self.request_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating maintenance priority: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def assign_staff_to_request(self, staff_id):
        """Assign a staff member to a request, setting status to In Progress if Open."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE maintenance_request
                SET assignedStaff_id = %s,
                    status = CASE WHEN status = 'Open' THEN 'In Progress' ELSE status END
                WHERE request_id = %s
            """, (staff_id, self.request_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error assigning staff: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def update_scheduled_date(self, scheduled_date):
        """Set the scheduled_date for a maintenance request."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE maintenance_request SET scheduled_date = %s WHERE request_id = %s
            """, (scheduled_date or None, self.request_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating scheduled date: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()

    def update_maintenance_cost(self, cost):
        """Update the cost of a maintenance request."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE maintenance_request SET cost = %s WHERE request_id = %s
            """, (cost, self.request_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating maintenance cost: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            db.close()


class MaintenanceLog(BaseModel):
    """Handles maintenance log CRUD operations."""

    def __init__(self, log_id=None, request_id=None, start_time=None,
                 end_time=None, description=None, parts_used=None,
                 cost_breakdown=None, technician_notes=None):
        self.log_id = log_id
        self.request_id = request_id
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.parts_used = parts_used
        self.cost_breakdown = cost_breakdown
        self.technician_notes = technician_notes

    @staticmethod
    def get_all_maintenance_logs():
        """Fetch all maintenance log entries."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT log_id, request_id, start_time, end_time,
                       description, parts_used, cost_breakdown, technician_notes
                FROM maintenance_log
                ORDER BY log_id
            """)
            results = cursor.fetchall()
            for r in results:
                for key in ('start_time', 'end_time'):
                    if r.get(key):
                        r[key] = str(r[key])
            return [MaintenanceLog.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching maintenance logs: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def get_logs_for_request(request_id):
        """Fetch maintenance logs for a specific request."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT log_id, request_id, start_time, end_time,
                       description, parts_used, cost_breakdown, technician_notes
                FROM maintenance_log
                WHERE request_id = %s
                ORDER BY log_id
            """, (request_id,))
            results = cursor.fetchall()
            for r in results:
                for key in ('start_time', 'end_time'):
                    if r.get(key):
                        r[key] = str(r[key])
            return [MaintenanceLog.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching logs for request {request_id}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            db.close()

    @staticmethod
    def create_maintenance_log(request_id, start_time, end_time,
                               description, parts_used, cost_breakdown,
                               technician_notes):
        """Create a new maintenance log entry. Returns new log_id or None."""
        db = Database_connection()
        conn = db.connect()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO maintenance_log
                    (request_id, start_time, end_time, description,
                     parts_used, cost_breakdown, technician_notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (request_id,
                  start_time or None, end_time or None,
                  description, parts_used, cost_breakdown, technician_notes))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating maintenance log: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            db.close()


# Backward-compatible aliases
get_all_maintenance_requests = Maintenance.get_all_maintenance_requests
get_maintenance_for_tenant = Maintenance.get_maintenance_for_tenant
get_maintenance_for_staff = Maintenance.get_maintenance_for_staff
get_request_by_id = Maintenance.get_request_by_id
get_staff_availability = Maintenance.get_staff_availability
get_all_staff = Maintenance.get_all_staff
get_maintenance_stats = Maintenance.get_maintenance_stats
create_maintenance_request = Maintenance.create_maintenance_request
get_all_maintenance_logs = MaintenanceLog.get_all_maintenance_logs
get_logs_for_request = MaintenanceLog.get_logs_for_request
create_maintenance_log = MaintenanceLog.create_maintenance_log


def update_maintenance_status(request_id, new_status):
    return Maintenance(request_id=request_id).update_maintenance_status(new_status)


def update_maintenance_priority(request_id, priority):
    return Maintenance(request_id=request_id).update_maintenance_priority(priority)


def assign_staff_to_request(request_id, staff_id):
    return Maintenance(request_id=request_id).assign_staff_to_request(staff_id)


def update_scheduled_date(request_id, scheduled_date):
    return Maintenance(request_id=request_id).update_scheduled_date(scheduled_date)


def update_maintenance_cost(request_id, cost):
    return Maintenance(request_id=request_id).update_maintenance_cost(cost)
