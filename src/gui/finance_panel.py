"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Finance Manager Panels — Invoices, Payments, Late Payments, Financial Reports

Implements all FinanceManager class methods and use-case operations
"""

import sys, os, csv as _csv
from datetime import datetime as _dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    _RL = True
except ImportError:
    _RL = False

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QLineEdit, QComboBox, QTextEdit, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, QDate

try:
    from main_window import PAMSTheme
except ImportError:
    from dialogs import PAMSTheme

from dialogs import (
    PAMSTableWidget, make_action_button, make_outline_button,
    make_panel_header, SectionCard, PAMSFormDialog, PAMSDetailDialog,
    confirm_action, show_success, show_error, BasePanel,
)

from finance_models import (
    get_all_invoices, get_invoices_for_tenant,
    create_invoice, update_invoice, mark_invoice_paid,
    get_all_payments, get_payments_for_tenant,
    create_payment, update_payment,
)

try:
    from tenant_models import create_notification as _create_notification
except ImportError:
    _create_notification = None
from lease_models import get_all_leases
from tenant_models import get_all_tenants


#  INVOICE MANAGEMENT PANEL

class InvoiceManagementPanel(BasePanel):
    """
    Finance Manager → Invoices
    Use-case: Add Invoices
    Methods: updateInvoice, markAsPaid, sendNotification, calculateLateFee,
             isOverdue, generateReceipt
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._invoices = []
        self._build_ui()
        self._load_from_db()

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _load_from_db(self):
        """Load invoices from the database and refresh UI."""
        try:
            self._invoices = self._filter_by_location(get_all_invoices())
        except Exception as e:
            show_error(self, f"Failed to load invoices: {e}")
            self._invoices = []
        self._rebuild_summary()
        self._refresh_table()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Invoice Management",
            "Create, update, and manage tenant invoices"
        )
        self._main_layout.addWidget(header)

        # Summary — populated later by _rebuild_summary
        self._summary_layout = QHBoxLayout()
        self._summary_layout.setSpacing(12)
        self._summary_cards = {}
        for title, color in [
            ("Total Invoices", T.INFO), ("Paid", T.SUCCESS),
            ("Pending", T.WARNING), ("Overdue", T.DANGER),
        ]:
            card = SectionCard()
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            lt = QLabel(title)
            lt.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 11px; font-weight: 600;")
            lv = QLabel("0")
            lv.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
            cl.addWidget(lt)
            cl.addWidget(lv)
            card.setFixedHeight(80)
            self._summary_layout.addWidget(card)
            self._summary_cards[title] = lv
        self._main_layout.addLayout(self._summary_layout)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_add = make_action_button("+ Add Invoice", T.ACCENT)
        self._btn_edit = make_action_button("Update Invoice", T.INFO)
        self._btn_paid = make_action_button("Mark as Paid", T.SUCCESS)
        self._btn_receipt = make_outline_button("Generate Receipt", T.ACCENT)
        self._btn_notify = make_outline_button("Send Notification", T.WARNING)
        self._btn_late_fee = make_outline_button("Calculate Late Fee", T.DANGER)

        self._btn_add.clicked.connect(self.addInvoice)
        self._btn_edit.clicked.connect(self.updateInvoice)
        self._btn_paid.clicked.connect(self.markAsPaid)
        self._btn_receipt.clicked.connect(self._generateReceipt)
        self._btn_notify.clicked.connect(self._sendNotification)
        self._btn_late_fee.clicked.connect(self._calculateLateFee)

        toolbar.addWidget(self._btn_add)
        toolbar.addWidget(self._btn_edit)
        toolbar.addWidget(self._btn_paid)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_receipt)
        toolbar.addWidget(self._btn_notify)
        toolbar.addWidget(self._btn_late_fee)
        self._main_layout.addLayout(toolbar)

        # Table
        self._table = PAMSTableWidget([
            "ID", "Tenant", "Apartment", "Amount", "Status",
            "Due Date", "Issue Date", "Description", "Overdue?"
        ])
        self._main_layout.addWidget(self._table)

    def _rebuild_summary(self):
        total = len(self._invoices)
        paid = sum(1 for i in self._invoices if i["status"] == "Paid")
        pending = sum(1 for i in self._invoices if i["status"] == "Pending")
        overdue = sum(1 for i in self._invoices if i["status"] == "Overdue")
        self._summary_cards["Total Invoices"].setText(str(total))
        self._summary_cards["Paid"].setText(str(paid))
        self._summary_cards["Pending"].setText(str(pending))
        self._summary_cards["Overdue"].setText(str(overdue))

    def _refresh_table(self):
        rows = []
        for inv in self._invoices:
            overdue = "Yes" if self.isOverdue(inv) else "No"
            rows.append([
                str(inv["invoiceID"]),
                inv.get("tenant_name", ""),
                inv.get("apartment_number", ""),
                f"£{inv['amount']:.2f}",
                inv["status"],
                inv.get("due_date", ""),
                inv.get("issue_date", ""),
                (inv.get("description") or "")[:35],
                overdue,
            ])
        self._table.populate(rows)

    def _get_selected_invoice(self):
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select an invoice.")
            return None
        iid = int(self._table.item(row, 0).text())
        return next((i for i in self._invoices if i["invoiceID"] == iid), None)

    # Add Invoices (use-case)

    def addInvoice(self):
        """Create a new invoice for a tenant (backed by database)."""
        try:
            leases = get_all_leases()
        except Exception as e:
            show_error(self, f"Failed to load leases: {e}")
            return

        if not leases:
            show_error(self, "No leases found. A lease must exist to create an invoice.")
            return

        lease_options = [
            f"Lease #{l['leaseID']} — {l['tenant_name']} — {l['apartment_number']}"
            for l in leases
        ]
        self._lease_lookup = {l['leaseID']: l for l in leases}

        fields = [
            {"key": "lease", "label": "Lease Agreement", "type": "combo",
             "options": lease_options, "value": lease_options[0]},
            {"key": "amount", "label": "Amount (£)", "type": "double", "value": 0.0},
            {"key": "dueDate", "label": "Due Date", "type": "date", "value": ""},
            {"key": "issueDate", "label": "Issue Date", "type": "date", "value": ""},
            {"key": "description", "label": "Description", "type": "text",
             "value": "", "placeholder": "e.g. Monthly rent — April 2026"},
        ]
        dlg = PAMSFormDialog("Add New Invoice", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            try:
                lease_id = int(values["lease"].split("#")[1].split(" ")[0])
            except (IndexError, ValueError):
                show_error(self, "Invalid lease selection.")
                return

            try:
                new_id = create_invoice(
                    lease_id=lease_id,
                    amount=values["amount"],
                    due_date=values["dueDate"],
                    issue_date=values["issueDate"],
                    description=values["description"] or None,
                )
                if new_id:
                    self._load_from_db()
                    lease = self._lease_lookup.get(lease_id, {})
                    show_success(self,
                        f"Invoice #{new_id} created for "
                        f"{lease.get('tenant_name', 'tenant')} — £{values['amount']:.2f}")
                else:
                    show_error(self, "Failed to create invoice.")
            except Exception as e:
                show_error(self, f"Database error: {e}")

    # Invoice.updateInvoice(newAmount, newDueDate)

    def updateInvoice(self):
        """Update amount and due date of the selected invoice."""
        inv = self._get_selected_invoice()
        if not inv:
            return

        fields = [
            {"key": "invoice", "label": "Invoice", "type": "readonly",
             "value": f"INV-{inv['invoiceID']:03d} — {inv.get('tenant_name', '')}"},
            {"key": "amount", "label": "New Amount (£)", "type": "double",
             "value": float(inv["amount"])},
            {"key": "dueDate", "label": "New Due Date", "type": "date",
             "value": inv.get("due_date", "")},
            {"key": "description", "label": "Description", "type": "text",
             "value": inv.get("description") or ""},
            {"key": "status", "label": "Status", "type": "combo",
             "options": ["Pending", "Paid", "Overdue", "Partial"],
             "value": inv["status"]},
        ]
        dlg = PAMSFormDialog(f"Update Invoice #{inv['invoiceID']}", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            try:
                ok = update_invoice(
                    inv["invoiceID"],
                    amount=values["amount"],
                    due_date=values["dueDate"],
                    description=values["description"],
                    status=values["status"],
                )
                if ok:
                    self._load_from_db()
                    show_success(self, f"Invoice #{inv['invoiceID']} updated.")
                else:
                    show_error(self, "Failed to update invoice.")
            except Exception as e:
                show_error(self, f"Database error: {e}")

    # Invoice.markAsPaid()

    def markAsPaid(self):
        """Mark the selected invoice as paid."""
        inv = self._get_selected_invoice()
        if not inv:
            return

        if inv["status"] == "Paid":
            show_error(self, "This invoice is already marked as paid.")
            return

        if confirm_action(self, "Mark as Paid",
                f"Mark Invoice #{inv['invoiceID']} (£{inv['amount']:.2f}) as paid?"):
            try:
                ok = mark_invoice_paid(inv["invoiceID"])
                if ok:
                    self._load_from_db()
                    show_success(self,
                        f"Invoice #{inv['invoiceID']} marked as paid.")
                else:
                    show_error(self, "Failed to mark invoice as paid.")
            except Exception as e:
                show_error(self, f"Database error: {e}")

    # Invoice.isOverdue()

    def isOverdue(self, inv: dict) -> bool:
        """Check if an invoice is overdue."""
        if inv["status"] == "Paid":
            return False
        due_str = inv.get("due_date", "")
        if not due_str:
            return False
        due = QDate.fromString(str(due_str), "yyyy-MM-dd")
        return QDate.currentDate() > due

    # Invoice.calculateLateFee(daysLate)

    def _calculateLateFee(self):
        """Calculate late fee for the selected overdue invoice."""
        inv = self._get_selected_invoice()
        if not inv:
            return

        if not self.isOverdue(inv):
            show_error(self, "This invoice is not overdue. No late fee applicable.")
            return

        due = QDate.fromString(str(inv.get("due_date", "")), "yyyy-MM-dd")
        days_late = due.daysTo(QDate.currentDate())
        fee = self.calculateLateFee(days_late)

        show_success(self,
            f"Late Fee Calculation for Invoice #{inv['invoiceID']}:\n\n"
            f"Original Amount: £{inv['amount']:.2f}\n"
            f"Days Late: {days_late}\n"
            f"Late Fee (£5/day): £{fee:.2f}\n"
            f"Total Due: £{float(inv['amount']) + fee:.2f}")

    def calculateLateFee(self, days_late: int) -> float:
        """Invoice.calculateLateFee(daysLate) — £5 per day late."""
        return days_late * 5.0

    # Invoice.generateReceipt()

    def _generateReceipt(self):
        """Generate a receipt for the selected paid invoice."""
        inv = self._get_selected_invoice()
        if not inv:
            return

        if inv["status"] != "Paid":
            show_error(self, "Receipts can only be generated for paid invoices.")
            return

        receipt_id = 1000 + inv["invoiceID"]
        details = [
            ("Receipt ID", f"REC-{receipt_id}"),
            ("Invoice ID", f"INV-{inv['invoiceID']:03d}"),
            ("Tenant", inv.get("tenant_name", "")),
            ("Apartment", inv.get("apartment_number", "")),
            ("Amount Paid", f"£{inv['amount']:.2f}"),
            ("Payment Date", inv.get("due_date", "")),
            ("Description", inv.get("description") or ""),
            ("Remaining Balance", "£0.00"),
            ("Generated", QDate.currentDate().toString("dd/MM/yyyy")),
        ]
        dlg = PAMSDetailDialog(f"Receipt — REC-{receipt_id}", details, self)
        dlg.exec()

    # Invoice.sendNotification()

    def _sendNotification(self):
        """Send a notification to the tenant about their invoice."""
        inv = self._get_selected_invoice()
        if not inv:
            return

        tenant = inv.get("tenant_name", "Tenant")
        fields = [
            {"key": "tenant", "label": "Tenant", "type": "readonly", "value": tenant},
            {"key": "invoice", "label": "Invoice", "type": "readonly",
             "value": f"INV-{inv['invoiceID']:03d} — £{inv['amount']:.2f}"},
            {"key": "message", "label": "Message", "type": "textarea",
             "value": f"Dear {tenant},\n\n"
                      f"This is a reminder regarding Invoice #{inv['invoiceID']} "
                      f"for £{inv['amount']:.2f} (Due: {inv.get('due_date', '')}).\n"
                      f"Current status: {inv['status']}.\n\n"
                      f"Please ensure timely payment.\n\nParagon Management"},
        ]
        dlg = PAMSFormDialog("Send Invoice Notification", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            message = dlg.get_values().get("message", "")
            tenant_id = inv.get("tenant_id")
            if tenant_id and _create_notification:
                try:
                    _create_notification(tenant_id, message, "Payment")
                except Exception as e:
                    print(f"[finance_panel] notification save failed: {e}")
            show_success(self, f"Notification sent to {tenant}.")


#  PAYMENT MANAGEMENT PANEL

class PaymentManagementPanel(BasePanel):
    """
    Finance Manager → Payments
    Use-case: Manage Payments
    Methods: processPayment, generateReceipt, verifyPayment,
             updatePaymentDetails, validatePaymentAmount, sendNotification
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._payments = []
        self._invoices = []
        self._build_ui()
        self._load_from_db()

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _load_from_db(self):
        """Load payments and invoices from the database and refresh UI."""
        try:
            self._payments = self._filter_by_location(get_all_payments())
        except Exception as e:
            show_error(self, f"Failed to load payments: {e}")
            self._payments = []
        try:
            self._invoices = self._filter_by_location(get_all_invoices())
        except Exception:
            self._invoices = []
        self._rebuild_summary()
        self._refresh_table()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Payment Management",
            "Process, verify and manage all tenant payments"
        )
        self._main_layout.addWidget(header)

        # Summary — populated later by _rebuild_summary
        self._summary_layout = QHBoxLayout()
        self._summary_layout.setSpacing(12)
        self._summary_cards = {}
        for title, color in [
            ("Total Payments", T.INFO),
            ("Total Collected", T.SUCCESS),
        ]:
            card = SectionCard()
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            lt = QLabel(title)
            lt.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 11px; font-weight: 600;")
            lv = QLabel("0")
            lv.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
            cl.addWidget(lt)
            cl.addWidget(lv)
            card.setFixedHeight(80)
            self._summary_layout.addWidget(card)
            self._summary_cards[title] = lv
        self._summary_layout.addStretch()
        self._main_layout.addLayout(self._summary_layout)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_process = make_action_button("+ Process Payment", T.ACCENT)
        self._btn_verify = make_action_button("Verify Payment", T.INFO)
        self._btn_update = make_outline_button("Update Details", T.WARNING)
        self._btn_receipt = make_outline_button("Generate Receipt", T.SUCCESS)
        self._btn_notify = make_outline_button("Send Notification", T.ACCENT)

        self._btn_process.clicked.connect(self.processPayment)
        self._btn_verify.clicked.connect(self._verifyPayment)
        self._btn_update.clicked.connect(self._updatePaymentDetails)
        self._btn_receipt.clicked.connect(self._generateReceipt)
        self._btn_notify.clicked.connect(self._sendNotification)

        toolbar.addWidget(self._btn_process)
        toolbar.addWidget(self._btn_verify)
        toolbar.addWidget(self._btn_update)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_receipt)
        toolbar.addWidget(self._btn_notify)
        self._main_layout.addLayout(toolbar)

        # Table
        self._table = PAMSTableWidget([
            "ID", "Tenant", "Invoice", "Amount Paid", "Date",
            "Method", "Transaction Ref", "Receipt"
        ])
        self._main_layout.addWidget(self._table)

    def _rebuild_summary(self):
        count = len(self._payments)
        total = sum(float(p["amount_paid"]) for p in self._payments)
        self._summary_cards["Total Payments"].setText(str(count))
        self._summary_cards["Total Collected"].setText(f"£{total:,.2f}")

    def _refresh_table(self):
        rows = []
        for p in self._payments:
            rows.append([
                str(p["payment_id"]),
                p.get("tenant_name", ""),
                f"INV-{p['invoice_id']:03d}",
                f"£{p['amount_paid']:.2f}",
                p.get("payment_date", ""),
                p.get("payment_method", ""),
                p.get("transaction_ref", ""),
                f"REC-{p['receipt_number']}" if p.get("receipt_number") else "",
            ])
        self._table.populate(rows)

    def _get_selected_payment(self):
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a payment.")
            return None
        pid = int(self._table.item(row, 0).text())
        return next((p for p in self._payments if p["payment_id"] == pid), None)

    # Payment.processPayment() / FinanceManager.processPayment()

    def processPayment(self):
        """Process a new payment against a pending invoice."""
        unpaid = [i for i in self._invoices if i["status"] != "Paid"]
        if not unpaid:
            show_error(self, "No unpaid invoices to process payment against.")
            return

        inv_options = [
            f"INV-{i['invoiceID']:03d} — {i.get('tenant_name', '')} — "
            f"£{i['amount']:.2f} [{i['status']}]"
            for i in unpaid
        ]

        fields = [
            {"key": "invoice", "label": "Invoice", "type": "combo",
             "options": inv_options, "value": inv_options[0]},
            {"key": "amount", "label": "Amount (£)", "type": "double", "value": 0.0},
            {"key": "method", "label": "Payment Method", "type": "combo",
             "options": ["Bank Transfer", "Debit Card", "Credit Card", "Cash", "Cheque"],
             "value": "Bank Transfer"},
            {"key": "transactionref", "label": "Transaction Reference", "type": "text",
             "value": "", "placeholder": "e.g. TXN-2026-0004"},
            {"key": "date", "label": "Payment Date", "type": "date", "value": ""},
        ]
        dlg = PAMSFormDialog("Process Payment", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()

            # Parse invoice ID from selection
            try:
                inv_id = int(values["invoice"].split("INV-")[1].split(" ")[0])
            except (IndexError, ValueError):
                show_error(self, "Invalid invoice selection.")
                return

            invoice = next((i for i in self._invoices if i["invoiceID"] == inv_id), None)

            # validatePaymentAmount
            if invoice and not self.validatePaymentAmount(
                    values["amount"], float(invoice["amount"])):
                show_error(self,
                    f"Payment amount £{values['amount']:.2f} exceeds "
                    f"invoice amount £{invoice['amount']:.2f}.")
                return

            try:
                pid, receipt = create_payment(
                    invoice_id=inv_id,
                    amount_paid=values["amount"],
                    payment_date=values["date"],
                    payment_method=values["method"],
                    transaction_ref=values["transactionref"],
                )
                if pid:
                    self._load_from_db()
                    show_success(self,
                        f"Payment #{pid} processed: £{values['amount']:.2f}\n"
                        f"Receipt: REC-{receipt}")
                else:
                    show_error(self, "Failed to process payment.")
            except Exception as e:
                show_error(self, f"Database error: {e}")

    # Payment.validatePaymentAmount(amount)

    def validatePaymentAmount(self, amount: float, invoice_amount: float) -> bool:
        """Validate that payment amount doesn't exceed invoice amount."""
        return amount <= invoice_amount

    # Payment.verifyPayment()

    def _verifyPayment(self):
        """Verify the selected payment is valid."""
        pay = self._get_selected_payment()
        if not pay:
            return

        invoice = next((i for i in self._invoices
                        if i["invoiceID"] == pay["invoice_id"]), None)
        verified = bool(
            pay.get("transaction_ref") and
            float(pay["amount_paid"]) > 0 and
            invoice is not None
        )

        details = [
            ("Payment ID", str(pay["payment_id"])),
            ("Tenant", pay.get("tenant_name", "")),
            ("Invoice", f"INV-{pay['invoice_id']:03d}"),
            ("Amount", f"£{pay['amount_paid']:.2f}"),
            ("Method", pay.get("payment_method", "")),
            ("Transaction Ref", pay.get("transaction_ref", "")),
            ("Date", pay.get("payment_date", "")),
            ("", "─" * 40),
            ("Verification Status", "VERIFIED ✓" if verified else "FAILED ✗"),
            ("Transaction Ref Valid", "Yes" if pay.get("transaction_ref") else "No"),
            ("Amount Valid", "Yes" if float(pay["amount_paid"]) > 0 else "No"),
            ("Invoice Found", "Yes" if invoice else "No"),
        ]
        dlg = PAMSDetailDialog(
            f"Payment Verification — #{pay['payment_id']}", details, self)
        dlg.exec()

    # Payment.updatePaymentDetails(payment)

    def _updatePaymentDetails(self):
        """Update details of an existing payment."""
        pay = self._get_selected_payment()
        if not pay:
            return

        fields = [
            {"key": "payment", "label": "Payment", "type": "readonly",
             "value": f"PAY-{pay['payment_id']:03d}"},
            {"key": "amount", "label": "Amount (£)", "type": "double",
             "value": float(pay["amount_paid"])},
            {"key": "method", "label": "Payment Method", "type": "combo",
             "options": ["Bank Transfer", "Debit Card", "Credit Card", "Cash", "Cheque"],
             "value": pay.get("payment_method", "Bank Transfer")},
            {"key": "transactionref", "label": "Transaction Reference", "type": "text",
             "value": pay.get("transaction_ref", "")},
            {"key": "date", "label": "Payment Date", "type": "date",
             "value": pay.get("payment_date", "")},
        ]
        dlg = PAMSFormDialog(f"Update Payment #{pay['payment_id']}", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            try:
                ok = update_payment(
                    pay["payment_id"],
                    amount_paid=values["amount"],
                    payment_method=values["method"],
                    transaction_ref=values["transactionref"],
                    payment_date=values["date"],
                )
                if ok:
                    self._load_from_db()
                    show_success(self, f"Payment #{pay['payment_id']} updated.")
                else:
                    show_error(self, "Failed to update payment.")
            except Exception as e:
                show_error(self, f"Database error: {e}")

    # Payment.generateReceipt() / Receipt.printReceipt()

    def _generateReceipt(self):
        """Generate and display a receipt for the selected payment."""
        pay = self._get_selected_payment()
        if not pay:
            return

        invoice = next((i for i in self._invoices
                        if i["invoiceID"] == pay["invoice_id"]), None)
        remaining = (float(invoice["amount"]) - float(pay["amount_paid"])) if invoice else 0
        if remaining < 0:
            remaining = 0

        details = [
            ("Receipt", ""),
            ("Receipt ID", f"REC-{pay.get('receipt_number', '')}"),
            ("Payment ID", f"PAY-{pay['payment_id']:03d}"),
            ("Date", pay.get("payment_date", "")),
            ("", "─" * 40),
            ("Tenant", pay.get("tenant_name", "")),
            ("Invoice", f"INV-{pay['invoice_id']:03d}"),
            ("Amount Paid", f"£{pay['amount_paid']:.2f}"),
            ("Payment Method", pay.get("payment_method", "")),
            ("Transaction Ref", pay.get("transaction_ref", "")),
            ("", "─" * 40),
            ("Total Amount Due",
             f"£{invoice['amount']:.2f}" if invoice else "N/A"),
            ("Amount Paid", f"£{pay['amount_paid']:.2f}"),
            ("Remaining Balance", f"£{remaining:.2f}"),
            ("", "─" * 40),
            ("Generated", QDate.currentDate().toString("dd/MM/yyyy")),
        ]
        dlg = PAMSDetailDialog(
            f"Receipt — REC-{pay.get('receipt_number', '')}", details, self)
        dlg.exec()

    # Payment.sendNotification(tenantID, message)

    def _sendNotification(self):
        """Send payment confirmation notification to tenant."""
        pay = self._get_selected_payment()
        if not pay:
            return

        tenant = pay.get("tenant_name", "Tenant")
        fields = [
            {"key": "tenant", "label": "Tenant", "type": "readonly", "value": tenant},
            {"key": "message", "label": "Message", "type": "textarea",
             "value": f"Dear {tenant},\n\n"
                      f"Your payment of £{pay['amount_paid']:.2f} "
                      f"(Ref: {pay.get('transaction_ref', '')}) has been received.\n"
                      f"Receipt: REC-{pay.get('receipt_number', '')}\n\n"
                      f"Thank you.\nParagon Management"},
        ]
        dlg = PAMSFormDialog("Send Payment Notification", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            message = dlg.get_values().get("message", "")
            # Resolve tenant_id via the invoice
            inv_id = pay.get("invoice_id")
            tenant_id = None
            if inv_id:
                inv = next((i for i in self._invoices if i.get("invoiceID") == inv_id), None)
                if inv:
                    tenant_id = inv.get("tenant_id")
            if tenant_id and _create_notification:
                try:
                    _create_notification(tenant_id, message, "Payment")
                except Exception as e:
                    print(f"[finance_panel] notification save failed: {e}")
            show_success(self, f"Payment notification sent to {tenant}.")


#  LATE PAYMENT PANEL

class LatePaymentPanel(BasePanel):
    """
    Finance Manager → Late Payments
    Use-case: Notify Tenants for Late Payments (extends Manage Payments)
    Methods: trackLatePayments, sendNotification
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._invoices = []
        self._build_ui()
        self._load_from_db()

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _load_from_db(self):
        """Load invoices from the database and refresh UI."""
        try:
            self._invoices = self._filter_by_location(get_all_invoices())
        except Exception as e:
            show_error(self, f"Failed to load invoices: {e}")
            self._invoices = []
        self._rebuild_summary()
        self._refresh_table()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Late Payment Alerts",
            "Track overdue invoices and notify tenants (Notify Tenants for Late Payments)"
        )
        self._main_layout.addWidget(header)

        # Summary — populated by _rebuild_summary
        self._summary_card = SectionCard()
        self._sc_layout = QHBoxLayout(self._summary_card)
        self._sc_layout.setContentsMargins(20, 16, 20, 16)
        self._late_labels = {}
        for title, color in [
            ("Overdue Invoices", T.DANGER),
            ("Total Overdue", T.DANGER),
            ("Avg Days Late", T.WARNING),
        ]:
            col = QVBoxLayout()
            lt = QLabel(title)
            lt.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 11px; font-weight: 600;")
            lv = QLabel("0")
            lv.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 700;")
            col.addWidget(lt)
            col.addWidget(lv)
            self._sc_layout.addLayout(col)
            self._late_labels[title] = lv
        self._main_layout.addWidget(self._summary_card)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_notify_one = make_action_button("Notify Selected Tenant", T.WARNING)
        self._btn_notify_all = make_action_button("Notify All Late Tenants", T.DANGER)
        self._btn_calc_fee = make_outline_button("Calculate Late Fee", T.DANGER)

        self._btn_notify_one.clicked.connect(self._notifyOne)
        self._btn_notify_all.clicked.connect(self._notifyAll)
        self._btn_calc_fee.clicked.connect(self._calcFee)

        toolbar.addWidget(self._btn_notify_one)
        toolbar.addWidget(self._btn_notify_all)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_calc_fee)
        self._main_layout.addLayout(toolbar)

        # Overdue invoices table
        self._table = PAMSTableWidget([
            "ID", "Tenant", "Apartment", "Amount", "Due Date",
            "Days Late", "Late Fee", "Total Due"
        ])
        self._main_layout.addWidget(self._table)

    def _rebuild_summary(self):
        overdue = [i for i in self._invoices if i["status"] == "Overdue"]
        total_overdue = sum(float(i["amount"]) for i in overdue)
        if overdue:
            days_list = []
            for inv in overdue:
                due = QDate.fromString(str(inv.get("due_date", "")), "yyyy-MM-dd")
                if due.isValid():
                    days_list.append(due.daysTo(QDate.currentDate()))
            avg_days = int(sum(days_list) / len(days_list)) if days_list else 0
        else:
            avg_days = 0
        self._late_labels["Overdue Invoices"].setText(str(len(overdue)))
        self._late_labels["Total Overdue"].setText(f"£{total_overdue:,.2f}")
        self._late_labels["Avg Days Late"].setText(str(avg_days))

    def _refresh_table(self):
        """FinanceManager.trackLatePayments() — display all overdue invoices."""
        rows = []
        for inv in self._invoices:
            if inv["status"] == "Overdue":
                due = QDate.fromString(str(inv.get("due_date", "")), "yyyy-MM-dd")
                days_late = due.daysTo(QDate.currentDate()) if due.isValid() else 0
                late_fee = days_late * 5.0
                total = float(inv["amount"]) + late_fee
                rows.append([
                    str(inv["invoiceID"]),
                    inv.get("tenant_name", ""),
                    inv.get("apartment_number", ""),
                    f"£{inv['amount']:.2f}",
                    inv.get("due_date", ""),
                    str(days_late),
                    f"£{late_fee:.2f}",
                    f"£{total:.2f}",
                ])
        self._table.populate(rows)

    def _notifyOne(self):
        """Notify selected tenant about their late payment."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select an overdue invoice.")
            return
        tenant = self._table.item(row, 1).text()
        amount = self._table.item(row, 3).text()
        days = self._table.item(row, 5).text()
        total = self._table.item(row, 7).text()

        msg = (f"Your payment of {amount} is {days} days overdue.\n"
               f"Total now due (including late fees): {total}.\n"
               f"Please settle immediately to avoid further charges.")

        # Find the invoice to get tenant_id
        inv_id_text = self._table.item(row, 0).text()
        try:
            inv_id = int(inv_id_text)
            inv = next((i for i in self._invoices if i.get("invoiceID") == inv_id), None)
            tenant_id = inv.get("tenant_id") if inv else None
            if tenant_id and _create_notification:
                _create_notification(tenant_id, msg, "Payment")
        except Exception as e:
            print(f"[finance_panel] late notify failed: {e}")

        show_success(self,
            f"Late payment notification sent to {tenant}:\n\n'{msg}'")

    def _notifyAll(self):
        """Notify all tenants with overdue payments."""
        overdue = [i for i in self._invoices if i["status"] == "Overdue"]
        if not overdue:
            show_success(self, "No overdue invoices — no notifications to send.")
            return

        tenants = set(i.get("tenant_name", "") for i in overdue)
        if confirm_action(self, "Notify All",
                f"Send late payment notifications to {len(tenants)} tenant(s)?"):
            sent = 0
            for inv in overdue:
                tid = inv.get("tenant_id")
                if tid and _create_notification:
                    try:
                        amt = float(inv.get("amount", 0))
                        _create_notification(
                            tid,
                            f"Your invoice #{inv['invoiceID']} for £{amt:,.2f} "
                            f"(due {inv.get('due_date', '')}) is overdue. "
                            f"Please pay immediately to avoid further charges.",
                            "Payment"
                        )
                        sent += 1
                    except Exception as e:
                        print(f"[finance_panel] late notify all failed for {tid}: {e}")
            show_success(self,
                f"Late payment notifications sent to {len(tenants)} tenants "
                f"({sent} notification(s) created):\n" +
                "\n".join(f"  • {t}" for t in tenants))

    def _calcFee(self):
        """Calculate late fee for selected row."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select an overdue invoice.")
            return
        days = int(self._table.item(row, 5).text())
        fee = days * 5.0
        show_success(self, f"Late fee: {days} days × £5.00/day = £{fee:.2f}")


#  FINANCIAL REPORTS PANEL

class FinancialReportsPanel(BasePanel):
    """
    Finance Manager → Financial Reports
    Use-case: View Financial Reports
    Methods: generateFinancialReport → Report, exportToPDF, exportToCSV
    FinancialReport fields: totalRentCollected, pendingRent, latePayments,
                            totalLateFees, maintenanceCosts, netRevenue
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Financial Reports",
            "Generate comprehensive financial reports and summaries"
        )
        self._main_layout.addWidget(header)

        # Controls
        controls = QHBoxLayout()
        lbl_period = QLabel("Period:")
        lbl_period.setStyleSheet(f"color: {T.ACCENT}; font-weight: 600; font-size: 13px;")
        self._combo_period = QComboBox()
        self._combo_period.addItems([
            "This Month", "Last Month", "This Quarter", "This Year", "Custom"
        ])
        self._combo_period.setFixedHeight(36)
        self._combo_period.setStyleSheet(f"""
            QComboBox {{
                background: {T.BG_WHITE}; border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px; padding: 0 12px; font-size: 13px; color: {T.TEXT_DARK};
            }}
            QComboBox::drop-down {{ border: none; width: 32px; }}
            QComboBox::down-arrow {{
                image: none; border-left: 5px solid transparent;
                border-right: 5px solid transparent; border-top: 6px solid {T.TEXT_MUTED};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {T.BG_WHITE}; border: 1px solid {T.BORDER_LIGHT};
                border-radius: 6px; padding: 4px; color: {T.TEXT_DARK};
                selection-background-color: {T.ACCENT_GLOW}; selection-color: {T.TEXT_DARK};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{ padding: 8px 12px; min-height: 32px; }}
        """)

        btn_gen = make_action_button("Generate Financial Report", T.ACCENT)
        btn_gen.clicked.connect(self.generateFinancialReport)
        btn_pdf = make_outline_button("Export PDF", T.INFO)
        btn_pdf.clicked.connect(self._exportPDF)
        btn_csv = make_outline_button("Export CSV", T.SUCCESS)
        btn_csv.clicked.connect(self._exportCSV)

        controls.addWidget(lbl_period)
        controls.addWidget(self._combo_period)
        controls.addSpacing(16)
        controls.addWidget(btn_gen)
        controls.addStretch()
        controls.addWidget(btn_pdf)
        controls.addWidget(btn_csv)
        self._main_layout.addLayout(controls)

        # Summary cards
        self._cards_layout = QHBoxLayout()
        self._cards_layout.setSpacing(12)
        self._main_layout.addLayout(self._cards_layout)

        # Report output
        self._output = QLabel("Click 'Generate Financial Report' to view results.")
        self._output.setStyleSheet(f"""
            QLabel {{
                background-color: {T.BG_WHITE}; border: 1px solid {T.BORDER_LIGHT};
                border-radius: 10px; padding: 24px; font-size: 13px; color: {T.TEXT_DARK};
                font-family: "Consolas", "Courier New", monospace;
            }}
        """)
        self._output.setWordWrap(True)
        self._output.setMinimumHeight(350)
        self._output.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self._output)

    # FinanceManager.generateFinancialReport() → Report

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def generateFinancialReport(self):
        """Generate a comprehensive financial report from live DB data."""
        period = self._combo_period.currentText()

        try:
            invoices = self._filter_by_location(get_all_invoices())
            payments = self._filter_by_location(get_all_payments())
        except Exception as e:
            show_error(self, f"Failed to load data: {e}")
            return

        total_collected = sum(float(p["amount_paid"]) for p in payments)
        pending = sum(float(i["amount"]) for i in invoices if i["status"] == "Pending")
        overdue_inv = [i for i in invoices if i["status"] == "Overdue"]
        overdue_amt = sum(float(i["amount"]) for i in overdue_inv)
        late_count = len(overdue_inv)
        total_late_fees = late_count * 50.0
        maint_costs = 300.0
        net_revenue = total_collected - maint_costs

        # Update summary cards
        T = PAMSTheme
        # Clear existing cards
        while self._cards_layout.count():
            child = self._cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for title, val, color in [
            ("Collected", f"£{total_collected:,.2f}", T.SUCCESS),
            ("Pending", f"£{pending:,.2f}", T.WARNING),
            ("Overdue", f"£{overdue_amt:,.2f}", T.DANGER),
            ("Net Revenue", f"£{net_revenue:,.2f}", T.ACCENT),
        ]:
            card = SectionCard()
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            lt = QLabel(title)
            lt.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 11px; font-weight: 600;")
            lv = QLabel(val)
            lv.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 700;")
            cl.addWidget(lt)
            cl.addWidget(lv)
            card.setFixedHeight(72)
            self._cards_layout.addWidget(card)

        lines = [
            f"Financial Report - {period}",
            f"Generated: {QDate.currentDate().toString('dd/MM/yyyy')}",
            "",
            "── Revenue Summary ──",
            f"  Total Rent Collected:    £{total_collected:>10,.2f}",
            f"  Pending Rent:            £{pending:>10,.2f}",
            f"  Overdue Amount:          £{overdue_amt:>10,.2f}",
            "",
            "── Late Payments ──",
            f"  Late Invoices:           {late_count}",
            f"  Total Late Fees:         £{total_late_fees:>10,.2f}",
            "",
            "── Costs ──",
            f"  Maintenance Costs:       £{maint_costs:>10,.2f}",
            "",
            "── Net ──",
            f"  Net Revenue:             £{net_revenue:>10,.2f}",
            "",
            "── Payment Breakdown ──",
        ]
        for p in payments:
            lines.append(
                f"  PAY-{p['payment_id']:03d}  {p.get('tenant_name', ''):18s}  "
                f"£{p['amount_paid']:>8,.2f}  {p.get('payment_method', ''):16s}  "
                f"{p.get('payment_date', '')}"
            )

        lines += [
            "",
            "── Invoice Breakdown ──",
        ]
        for i in invoices:
            lines.append(
                f"  INV-{i['invoiceID']:03d}  {i.get('tenant_name', ''):18s}  "
                f"£{i['amount']:>8,.2f}  [{i['status']:8s}]  "
                f"Due: {i.get('due_date', '')}"
            )

        self._output.setText("\n".join(lines))

    def _exportPDF(self):
        """Report.exportToPDF() — write the financial report to a real PDF file."""
        content = self._output.text()
        if "Generate Financial" in content:
            show_error(self, "Generate a report first before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Financial Report — PDF",
            f"PAMS_Financial_Report_{_dt.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf);;All Files (*)",
        )
        if not path:
            return
        if not _RL:
            show_error(self, "reportlab is not installed.\nRun: pip install reportlab")
            return
        try:
            doc = SimpleDocTemplate(
                path, pagesize=A4,
                leftMargin=2*cm, rightMargin=2*cm,
                topMargin=2*cm, bottomMargin=2*cm,
            )
            styles = getSampleStyleSheet()
            story = [Paragraph("PAMS — Financial Report", styles["Title"]),
                     Spacer(1, 0.5*cm)]
            for line in content.splitlines():
                story.append(Paragraph(
                    line.replace(" ", "\u00a0") or "\u00a0", styles["Code"]))
            doc.build(story)
            show_success(self, f"Financial report exported to PDF.\n{path}")
        except Exception as e:
            show_error(self, f"PDF export failed: {e}")

    def _exportCSV(self):
        """Report.exportToCSV() — write the financial report to a real CSV file."""
        content = self._output.text()
        if "Generate Financial" in content:
            show_error(self, "Generate a report first before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Financial Report — CSV",
            f"PAMS_Financial_Report_{_dt.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = _csv.writer(f)
                writer.writerow(["PAMS Financial Report",
                                 _dt.now().strftime("%d/%m/%Y %H:%M")])
                writer.writerow([])
                for line in content.splitlines():
                    writer.writerow([line])
            show_success(self, f"Financial report exported to CSV.\n{path}")
        except Exception as e:
            show_error(self, f"CSV export failed: {e}")
