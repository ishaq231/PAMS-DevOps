"""
24030388 - Ishaq Modassir Mushtaq

Invoice and payment models for financial management.
Used by finance, tenant, and dashboard GUI panels.
"""

from connection import Database_connection
from base_model import BaseModel


def _notify(recipient_id, message, ntype="Payment"):
    """Fire-and-forget notification helper."""
    try:
        from tenant_models import Tenant
        Tenant.create_notification(recipient_id, message, ntype)
    except Exception as e:
        print(f"[finance_models] notification skipped: {e}")


def _fmt(row, date_keys):
    """Convert date objects to strings for the given keys."""
    for k in date_keys:
        if row.get(k):
            row[k] = str(row[k])


class Invoice(BaseModel):
    """Handles invoice CRUD operations."""

    def __init__(self, invoiceID=None, leaseID=None, amount=None,
                 due_date=None, status=None, issue_date=None,
                 description=None):
        self.invoiceID = invoiceID
        self.leaseID = leaseID
        self.amount = amount
        self.due_date = due_date
        self.status = status
        self.issue_date = issue_date
        self.description = description

    @staticmethod
    def get_all_invoices():
        """Fetch all invoices with tenant and apartment info."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT i.invoiceID, i.leaseID, i.amount, i.due_date, i.status,
                       i.issue_date, i.description,
                       la.tenantID AS tenant_id,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name,
                       a.apartment_number,
                       l.city AS location
                FROM Invoice i
                JOIN lease_agreement la ON i.leaseID = la.leaseID
                JOIN user u ON la.tenantID = u.user_id
                JOIN apartment a ON la.apartmentID = a.apartment_id
                LEFT JOIN location l ON a.location_id = l.location_id
                ORDER BY i.invoiceID
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                _fmt(r, ('due_date', 'issue_date'))
            return [Invoice.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching invoices: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_invoices_for_tenant(user_id):
        """Fetch invoices belonging to a specific tenant."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT i.invoiceID, i.leaseID, i.amount, i.due_date,
                       i.status, i.issue_date, i.description
                FROM Invoice i
                JOIN lease_agreement la ON i.leaseID = la.leaseID
                WHERE la.tenantID = %s
                ORDER BY i.due_date DESC
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            for r in results:
                _fmt(r, ('due_date', 'issue_date'))
            return [Invoice.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching tenant invoices: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def create_invoice(lease_id, amount, due_date, issue_date, description=None):
        """Insert a new invoice and return the new invoiceID (or None)."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO Invoice (leaseID, amount, due_date, status, issue_date, description)
                VALUES (%s, %s, %s, 'Pending', %s, %s)
            """
            cursor.execute(query, (lease_id, amount, due_date, issue_date, description))
            conn.commit()
            inv_id = cursor.lastrowid

            # Notify the tenant
            cursor.execute("SELECT tenantID FROM lease_agreement WHERE leaseID = %s", (lease_id,))
            row = cursor.fetchone()
            if row:
                _notify(row[0],
                        f"New invoice #{inv_id} for £{float(amount):,.2f} due on {due_date}.",
                        "Payment")

            return inv_id
        except Exception as e:
            print(f"Error creating invoice: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_invoice(self, amount=None, due_date=None,
                       description=None, status=None):
        """Update one or more fields of an existing invoice."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            sets, vals = [], []
            if amount is not None:
                sets.append("amount = %s"); vals.append(amount)
            if due_date is not None:
                sets.append("due_date = %s"); vals.append(due_date)
            if description is not None:
                sets.append("description = %s"); vals.append(description)
            if status is not None:
                sets.append("status = %s"); vals.append(status)
            if not sets:
                return False
            vals.append(self.invoiceID)
            query = f"UPDATE Invoice SET {', '.join(sets)} WHERE invoiceID = %s"
            cursor.execute(query, tuple(vals))
            conn.commit()
            ok = cursor.rowcount > 0

            # Notify tenant on status change
            if ok and status:
                cursor.execute("""
                    SELECT la.tenantID FROM Invoice i
                    JOIN lease_agreement la ON i.leaseID = la.leaseID
                    WHERE i.invoiceID = %s
                """, (self.invoiceID,))
                row = cursor.fetchone()
                if row:
                    _notify(row[0],
                            f"Invoice #{self.invoiceID} status updated to '{status}'.",
                            "Payment")
            return ok
        except Exception as e:
            print(f"Error updating invoice: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def mark_invoice_paid(self):
        """Mark an invoice as Paid."""
        return self.update_invoice(status="Paid")


class Payment(BaseModel):
    """Handles payment CRUD operations."""

    def __init__(self, payment_id=None, invoice_id=None, amount_paid=None,
                 payment_date=None, payment_method=None,
                 transaction_ref=None, receipt_number=None):
        self.payment_id = payment_id
        self.invoice_id = invoice_id
        self.amount_paid = amount_paid
        self.payment_date = payment_date
        self.payment_method = payment_method
        self.transaction_ref = transaction_ref
        self.receipt_number = receipt_number

    @staticmethod
    def get_all_payments():
        """Fetch all payments with tenant info (via invoice -> lease -> user)."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.payment_id, p.invoice_id, p.amount_paid,
                       p.payment_date, p.payment_method, p.transaction_ref,
                       p.receipt_number,
                       CONCAT(u.fname, ' ', u.lname) AS tenant_name,
                       l.city AS location
                FROM payment p
                JOIN Invoice i ON p.invoice_id = i.invoiceID
                JOIN lease_agreement la ON i.leaseID = la.leaseID
                JOIN user u ON la.tenantID = u.user_id
                JOIN apartment a ON la.apartmentID = a.apartment_id
                LEFT JOIN location l ON a.location_id = l.location_id
                ORDER BY p.payment_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            for r in results:
                _fmt(r, ('payment_date',))
            return [Payment.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching payments: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def get_payments_for_tenant(user_id):
        """Fetch payments made by a specific tenant."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.payment_id, p.invoice_id, p.amount_paid,
                       p.payment_date, p.payment_method, p.transaction_ref,
                       p.receipt_number
                FROM payment p
                JOIN Invoice i ON p.invoice_id = i.invoiceID
                JOIN lease_agreement la ON i.leaseID = la.leaseID
                WHERE la.tenantID = %s
                ORDER BY p.payment_date DESC
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            for r in results:
                _fmt(r, ('payment_date',))
            return [Payment.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error fetching tenant payments: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    @staticmethod
    def create_payment(invoice_id, amount_paid, payment_date,
                       payment_method, transaction_ref):
        """Insert a new payment, auto-generate receipt number, and update
        the invoice status to 'Paid' if the cumulative amount covers it.
        Returns (payment_id, receipt_number) or (None, None)."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor(dictionary=True)

            # Generate receipt number: max existing + 1 (starting at 1001)
            cursor.execute("SELECT COALESCE(MAX(receipt_number), 1000) AS mx FROM payment")
            receipt = cursor.fetchone()["mx"] + 1

            ins = """
                INSERT INTO payment
                    (invoice_id, amount_paid, payment_date, payment_method,
                     transaction_ref, receipt_number)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(ins, (invoice_id, amount_paid, payment_date,
                                 payment_method, transaction_ref, receipt))
            pid = cursor.lastrowid

            # Check if total paid >= invoice amount → mark Paid
            cursor.execute("""
                SELECT COALESCE(SUM(amount_paid), 0) AS total_paid
                FROM payment WHERE invoice_id = %s
            """, (invoice_id,))
            total_paid = cursor.fetchone()["total_paid"]

            cursor.execute("SELECT amount FROM Invoice WHERE invoiceID = %s",
                           (invoice_id,))
            inv_row = cursor.fetchone()
            if inv_row and total_paid >= inv_row["amount"]:
                cursor.execute("UPDATE Invoice SET status='Paid' WHERE invoiceID=%s",
                               (invoice_id,))

            conn.commit()

            # Notify the tenant about the payment
            cursor.execute("""
                SELECT la.tenantID FROM Invoice i
                JOIN lease_agreement la ON i.leaseID = la.leaseID
                WHERE i.invoiceID = %s
            """, (invoice_id,))
            t_row = cursor.fetchone()
            if t_row:
                _notify(t_row["tenantID"],
                        f"Payment of £{float(amount_paid):,.2f} recorded for invoice #{invoice_id}. Receipt: {receipt}.",
                        "Payment")

            return pid, receipt
        except Exception as e:
            print(f"Error creating payment: {e}")
            if conn:
                conn.rollback()
            return None, None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()

    def update_payment(self, amount_paid=None, payment_method=None,
                       transaction_ref=None, payment_date=None):
        """Update one or more fields of an existing payment."""
        db = Database_connection()
        conn = db.connect()
        try:
            cursor = conn.cursor()
            sets, vals = [], []
            if amount_paid is not None:
                sets.append("amount_paid = %s"); vals.append(amount_paid)
            if payment_method is not None:
                sets.append("payment_method = %s"); vals.append(payment_method)
            if transaction_ref is not None:
                sets.append("transaction_ref = %s"); vals.append(transaction_ref)
            if payment_date is not None:
                sets.append("payment_date = %s"); vals.append(payment_date)
            if not sets:
                return False
            vals.append(self.payment_id)
            query = f"UPDATE payment SET {', '.join(sets)} WHERE payment_id = %s"
            cursor.execute(query, tuple(vals))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating payment: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                db.close()


# Backward-compatible aliases
get_all_invoices = Invoice.get_all_invoices
get_invoices_for_tenant = Invoice.get_invoices_for_tenant
create_invoice = Invoice.create_invoice
get_all_payments = Payment.get_all_payments
get_payments_for_tenant = Payment.get_payments_for_tenant
create_payment = Payment.create_payment


def update_invoice(invoice_id, amount=None, due_date=None, description=None, status=None):
    return Invoice(invoiceID=invoice_id).update_invoice(
        amount=amount, due_date=due_date, description=description, status=status)


def mark_invoice_paid(invoice_id):
    return Invoice(invoiceID=invoice_id).mark_invoice_paid()


def update_payment(payment_id, amount_paid=None, payment_method=None,
                   transaction_ref=None, payment_date=None):
    return Payment(payment_id=payment_id).update_payment(
        amount_paid=amount_paid, payment_method=payment_method,
        transaction_ref=transaction_ref, payment_date=payment_date)
