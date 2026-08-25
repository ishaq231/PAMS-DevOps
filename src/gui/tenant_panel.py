"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Tenant Panels — My Lease, Payments, Maintenance, Profile, Notifications.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QLineEdit, QComboBox, QTextEdit, QDateEdit,
    QTabWidget, QFormLayout, QSpinBox, QDoubleSpinBox,
    QGraphicsDropShadowEffect, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QFont, QColor, QCursor

try:
    from main_window import PAMSTheme
except ImportError:
    try:
        from dialogs import PAMSTheme
    except ImportError:
        class PAMSTheme:
            BG_DARKEST = "#0F1923"; BG_DARK = "#15202E"; BG_SIDEBAR = "#1A2736"
            BG_CARD = "#1E2D3D"; BG_HOVER = "#253647"; BG_SURFACE = "#F0F4F8"
            BG_WHITE = "#FFFFFF"; ACCENT = "#00D4AA"; ACCENT_HOVER = "#00E8BB"
            ACCENT_DIM = "#00B894"; ACCENT_GLOW = "rgba(0, 212, 170, 0.15)"
            SUCCESS = "#2ECC71"; WARNING = "#F39C12"; DANGER = "#E74C3C"
            INFO = "#3498DB"; TEXT_PRIMARY = "#FFFFFF"; TEXT_SECONDARY = "#8899AA"
            TEXT_MUTED = "#7E92A5"; TEXT_DARK = "#1A2736"; TEXT_BODY = "#4A5568"
            BORDER_SUBTLE = "rgba(255, 255, 255, 0.06)"; BORDER_LIGHT = "#E2E8F0"
            SHADOW = "rgba(0, 0, 0, 0.25)"; FONT_FAMILY = "Segoe UI"
            CARD_RADIUS = 14; BTN_RADIUS = 10

from dialogs import (
    BasePanel, PAMSTableWidget, PAMSFormDialog, PAMSDetailDialog,
    SectionCard, StatusBadge, make_action_button, make_outline_button,
    make_panel_header, confirm_action, show_success, show_error,
)

try:
    from tenant_models import (
        get_tenant_profile, update_tenant_contact, update_tenant_personal,
        get_active_lease_for_tenant, request_early_termination,
        change_tenant_password, get_notifications_for_tenant,
        create_notification, mark_notification_read, mark_all_notifications_read,
    )
    from finance_models import (
        get_invoices_for_tenant, get_payments_for_tenant,
        create_payment, mark_invoice_paid,
    )
    from maintenance_models import (
        get_maintenance_for_tenant, create_maintenance_request,
    )
    from frontdesk_models import (
        get_complaints_for_tenant, create_complaint,
    )
    _DB_OK = True
except Exception as _e:
    print(f"[tenant_panel] DB import warning: {_e}")
    _DB_OK = False

T = PAMSTheme


# Panel 1: MyLeasePanel
# Class diagram: Tenant.viewLeaseStatus(), Tenant.requestEarlyLeaseTermination(reason),
# LeaseAgreement.calculateRemainingDuration(), LeaseAgreement.calculateTerminationPenalty()

class MyLeasePanel(BasePanel):
    """Tenant view of their active lease agreement."""

    def __init__(self, user_id: int = 0, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self._lease = None
        self._build_ui()
        self.viewLeaseStatus()

    def _build_ui(self):
        header = make_panel_header(
            "My Lease Agreement",
            "View your current lease details and request changes"
        )
        self._main_layout.addWidget(header)

        # Lease details card
        self._card = SectionCard()
        self._card_layout = QVBoxLayout(self._card)
        self._card_layout.setContentsMargins(24, 20, 24, 20)
        self._card_layout.setSpacing(12)
        self._main_layout.addWidget(self._card)

        # Remaining duration display
        self._remaining_label = QLabel()
        self._remaining_label.setStyleSheet(f"""
            color: {T.ACCENT}; font-size: 15px; font-weight: 600;
            background: transparent; padding: 8px 0;
        """)
        self._main_layout.addWidget(self._remaining_label)

        # Action buttons
        btn_row = QHBoxLayout()
        self._btn_terminate = make_action_button("Request Early Termination", T.DANGER)
        self._btn_terminate.clicked.connect(self.requestEarlyLeaseTermination)
        btn_row.addWidget(self._btn_terminate)
        btn_row.addStretch()
        self._main_layout.addLayout(btn_row)

        self._main_layout.addStretch()

    def viewLeaseStatus(self):
        """Tenant.viewLeaseStatus() - Display the tenant's active lease details."""
        # Clear existing detail rows
        while self._card_layout.count():
            item = self._card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        self._lease = self._get_tenant_lease()
        lease = self._lease
        if not lease:
            no_lease = QLabel("No active lease found.")
            no_lease.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 14px;")
            self._card_layout.addWidget(no_lease)
            self._remaining_label.setText("")
            self._btn_terminate.setEnabled(False)
            return

        # Map DB status keys to display-friendly labels
        status_display = {
            'ACTIVE': 'Active', 'PENDING': 'Pending',
            'TERMINATED': 'Terminated', 'EXPIRED': 'Expired',
        }.get(lease.get('status', ''), lease.get('status', '—'))

        details = [
            ("Lease ID", str(lease["leaseID"])),
            ("Apartment", lease.get("apartment_number", "—")),
            ("Start Date", lease.get("start_date", "—")),
            ("End Date", lease.get("end_date", "—")),
            ("Lease Term", f"{lease.get('lease_term_months', '—')} months"),
            ("Monthly Rent", f"£{lease.get('monthly_rent', 0):,.2f}"),
            ("Deposit Amount", f"£{lease.get('deposit_amount', 0):,.2f}"),
            ("Status", status_display),
        ]

        for label_text, value_text in details:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 13px; font-weight: 600;")
            lbl.setFixedWidth(160)
            if label_text == "Status":
                val = StatusBadge(value_text)
            else:
                val = QLabel(str(value_text))
                val.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 13px;")
            row.addWidget(lbl)
            row.addWidget(val, 1)
            self._card_layout.addLayout(row)

        remaining = self.calculateRemainingDuration(lease)
        self._remaining_label.setText(
            f"Remaining Duration: {remaining} days"
            if remaining > 0 else "Lease has expired or ends today"
        )

        self._btn_terminate.setEnabled(lease.get("status") == "ACTIVE")

    def _get_tenant_lease(self) -> dict | None:
        """Fetch the tenant's active lease from the database."""
        if not _DB_OK or not self._user_id:
            return None
        try:
            return get_active_lease_for_tenant(self._user_id)
        except Exception as e:
            print(f"Error loading lease: {e}")
            return None

    def requestEarlyLeaseTermination(self, reason: str = ""):
        """Tenant.requestEarlyLeaseTermination(reason) - Request to terminate lease early."""
        if self._lease is None:
            self._lease = self._get_tenant_lease()
        lease = self._lease
        if not lease:
            show_error(self, "No active lease found.")
            return

        penalty = self.calculateTerminationPenalty(lease)
        notice = lease.get('early_termination_notice', 30)

        fields = [
            {"key": "apartment", "label": "Apartment", "type": "readonly",
             "value": lease.get("apartment_number", "—")},
            {"key": "penalty", "label": "Termination Penalty", "type": "readonly",
             "value": f"£{penalty:.2f} (5% of monthly rent)"},
            {"key": "notice", "label": "Notice Period", "type": "readonly",
             "value": f"{notice} days (1 month)"},
            {"key": "reason", "label": "Reason for Termination", "type": "textarea",
             "value": ""},
        ]

        dlg = PAMSFormDialog("Request Early Termination", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values.get("reason"):
                show_error(self, "Please provide a reason for termination.")
                return
            if _DB_OK:
                ok = request_early_termination(
                    lease["leaseID"], self._user_id, values["reason"]
                )
                if not ok:
                    show_error(self, "Failed to submit termination request. Please try again.")
                    return
            self.viewLeaseStatus()
            show_success(self,
                f"Early termination request submitted.\n"
                f"Penalty: £{penalty:.2f}\n"
                f"Notice period: {notice} days."
            )

    def calculateRemainingDuration(self, lease: dict) -> int:
        """LeaseAgreement.calculateRemainingDuration() - Days remaining on the lease."""
        end_str = lease.get("end_date", "")
        if not end_str:
            return 0
        end = QDate.fromString(str(end_str), "yyyy-MM-dd")
        today = QDate.currentDate()
        return today.daysTo(end)

    def calculateTerminationPenalty(self, lease: dict) -> float:
        """LeaseAgreement.calculateTerminationPenalty() - 5% of monthly rent."""
        rent = float(lease.get("monthly_rent", 0))
        pct = float(lease.get("termination_penalty_percent", 5.0))
        return rent * (pct / 100)


# Panel 2: MyPaymentsPanel
# Class diagram: Tenant.makePayment(), Tenant.viewInvoices(), Tenant.viewPayments(),
# Tenant.viewPaymentHistoryReceipts(), Payment.processPayment(),
# Payment.generateReceipt(), Payment.verifyPayment(), Receipt.printReceipt()

class MyPaymentsPanel(BasePanel):
    """Tenant view of invoices, payments and receipts."""

    def __init__(self, user_id: int = 0, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self._invoices = []
        self._payments = []
        self._build_ui()

    def _build_ui(self):
        header = make_panel_header(
            "My Payments",
            "View invoices, make payments, and access receipts"
        )
        self._main_layout.addWidget(header)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                background-color: {T.BG_WHITE};
            }}
            QTabBar::tab {{
                background-color: {T.BG_SURFACE};
                color: {T.TEXT_BODY};
                padding: 10px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: {T.BG_WHITE};
                color: {T.ACCENT};
                border-bottom: 2px solid {T.ACCENT};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: #E2E8F0;
            }}
        """)

        # Tab 1: Invoices
        self._invoices_tab = QWidget()
        self._build_invoices_tab()
        self._tabs.addTab(self._invoices_tab, "Invoices")

        # Tab 2: Payment History
        self._history_tab = QWidget()
        self._build_history_tab()
        self._tabs.addTab(self._history_tab, "Payment History")

        # Tab 3: Receipts
        self._receipts_tab = QWidget()
        self._build_receipts_tab()
        self._tabs.addTab(self._receipts_tab, "Receipts")

        self._main_layout.addWidget(self._tabs)
        self._main_layout.addStretch()

    # Invoices tab

    def _build_invoices_tab(self):
        layout = QVBoxLayout(self._invoices_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        self._btn_pay = make_action_button("Pay Now", T.ACCENT)
        self._btn_pay.clicked.connect(self.makePayment)
        btn_row.addWidget(self._btn_pay)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._invoice_table = PAMSTableWidget([
            "Invoice ID", "Description", "Amount", "Due Date", "Status"
        ])
        layout.addWidget(self._invoice_table)
        self.viewInvoices()

    def viewInvoices(self):
        """Tenant.viewInvoices() - Display invoices for this tenant from the database."""
        if _DB_OK and self._user_id:
            try:
                self._invoices = get_invoices_for_tenant(self._user_id)
            except Exception as e:
                print(f"Error loading invoices: {e}")
                self._invoices = []
        self._invoice_table.setRowCount(len(self._invoices))
        for row, inv in enumerate(self._invoices):
            self._invoice_table.setItem(row, 0, QTableWidgetItem(str(inv["invoiceID"])))
            self._invoice_table.setItem(row, 1, QTableWidgetItem(inv.get("description") or ""))
            self._invoice_table.setItem(row, 2, QTableWidgetItem(f"£{float(inv['amount']):,.2f}"))
            self._invoice_table.setItem(row, 3, QTableWidgetItem(inv.get("due_date", "") or ""))
            badge = StatusBadge(inv.get("status", "") or "")
            self._invoice_table.setCellWidget(row, 4, badge)

    def _get_selected_invoice(self) -> dict | None:
        row = self._invoice_table.currentRow()
        if row < 0:
            show_error(self, "Please select an invoice first.")
            return None
        inv_id = int(self._invoice_table.item(row, 0).text())
        for inv in self._invoices:
            if inv["invoiceID"] == inv_id:
                return inv
        return None

    def makePayment(self):
        """Tenant.makePayment() - Open payment form for the selected invoice."""
        invoice = self._get_selected_invoice()
        if not invoice:
            return
        if invoice.get("status") == "Paid":
            show_error(self, "This invoice has already been paid.")
            return

        fields = [
            {"key": "invoice", "label": "Invoice", "type": "readonly",
             "value": f"#{invoice['invoiceID']} - {invoice.get('description', '')}"},
            {"key": "amount", "label": "Amount (£)", "type": "double",
             "value": float(invoice["amount"])},
            {"key": "method", "label": "Payment Method", "type": "combo",
             "options": ["Bank Transfer", "Debit Card", "Credit Card"]},
        ]

        dlg = PAMSFormDialog("Make Payment", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not self.verifyPayment(values["amount"], float(invoice["amount"])):
                show_error(self, "Payment amount must match the invoice amount.")
                return
            self.processPayment(invoice, values)

    def processPayment(self, invoice: dict, values: dict) -> bool:
        """Payment.processPayment() - Process the payment and persist to the database."""
        if not _DB_OK:
            show_error(self, "Database not available.")
            return False
        from datetime import date as _d
        pay_date = _d.today().strftime("%Y-%m-%d")
        import random
        txn_ref = f"TXN-{_d.today().year}-{random.randint(10000, 99999)}"
        pid, receipt_num = create_payment(
            invoice_id=invoice["invoiceID"],
            amount_paid=values["amount"],
            payment_date=pay_date,
            payment_method=values["method"],
            transaction_ref=txn_ref,
        )
        if pid is None:
            show_error(self, "Payment failed. Please try again.")
            return False

        # Refresh tables from DB
        self.viewInvoices()
        self.viewPayments()
        self._refresh_receipts_table()

        receipt = {
            "receiptID": receipt_num,
            "paymentID": pid,
            "amount": values["amount"],
            "date": pay_date,
            "method": values["method"],
            "transactionRef": txn_ref,
        }
        show_success(self,
            f"Payment of £{values['amount']:,.2f} processed successfully.\n"
            f"Transaction Ref: {txn_ref}\n"
            f"Receipt #{receipt_num} generated."
        )
        return True

    def verifyPayment(self, paid: float, expected: float) -> bool:
        """Payment.verifyPayment() - Verify the payment amount matches."""
        return abs(paid - expected) < 0.01

    def generateReceipt(self, payment: dict) -> dict:
        """Payment.generateReceipt() - Generate a receipt dict for the payment."""
        return {
            "receiptID": payment.get("receipt_number") or payment.get("receipt", "N/A"),
            "paymentID": payment.get("payment_id") or payment.get("paymentID", "N/A"),
            "amount": payment.get("amount_paid") or payment.get("amountPaid", 0),
            "date": payment.get("payment_date") or payment.get("paymentDate", ""),
            "method": payment.get("payment_method") or payment.get("paymentMethod", ""),
            "transactionRef": payment.get("transaction_ref") or payment.get("transactionref", ""),
        }

    # Payment History tab

    def _build_history_tab(self):
        layout = QVBoxLayout(self._history_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._history_table = PAMSTableWidget([
            "Payment ID", "Invoice", "Amount Paid", "Date", "Method", "Transaction Ref"
        ])
        layout.addWidget(self._history_table)
        self.viewPayments()

    def viewPayments(self):
        """Tenant.viewPayments() / Tenant.viewPaymentHistoryReceipts() - Display payment history."""
        if _DB_OK and self._user_id:
            try:
                self._payments = get_payments_for_tenant(self._user_id)
            except Exception as e:
                print(f"Error loading payments: {e}")
                self._payments = []
        self._history_table.setRowCount(len(self._payments))
        for row, pay in enumerate(self._payments):
            self._history_table.setItem(row, 0, QTableWidgetItem(str(pay.get("payment_id", ""))))
            self._history_table.setItem(row, 1, QTableWidgetItem(f"INV-{pay.get('invoice_id', '')}"))
            self._history_table.setItem(row, 2, QTableWidgetItem(f"£{float(pay.get('amount_paid', 0)):,.2f}"))
            self._history_table.setItem(row, 3, QTableWidgetItem(str(pay.get("payment_date", ""))))
            self._history_table.setItem(row, 4, QTableWidgetItem(pay.get("payment_method", "") or ""))
            self._history_table.setItem(row, 5, QTableWidgetItem(pay.get("transaction_ref", "") or ""))

    # Receipts tab

    def _build_receipts_tab(self):
        layout = QVBoxLayout(self._receipts_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        btn_row = QHBoxLayout()
        self._btn_receipt = make_action_button("View Receipt", T.INFO)
        self._btn_receipt.clicked.connect(self._view_receipt)
        btn_row.addWidget(self._btn_receipt)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._receipts_table = PAMSTableWidget([
            "Receipt #", "Payment ID", "Amount", "Date", "Method"
        ])
        layout.addWidget(self._receipts_table)
        self._refresh_receipts_table()

    def _refresh_receipts_table(self):
        if _DB_OK and self._user_id:
            try:
                self._payments = get_payments_for_tenant(self._user_id)
            except Exception:
                pass
        self._receipts_table.setRowCount(len(self._payments))
        for row, pay in enumerate(self._payments):
            self._receipts_table.setItem(row, 0, QTableWidgetItem(str(pay.get("receipt_number", "N/A"))))
            self._receipts_table.setItem(row, 1, QTableWidgetItem(str(pay.get("payment_id", ""))))
            self._receipts_table.setItem(row, 2, QTableWidgetItem(f"£{float(pay.get('amount_paid', 0)):,.2f}"))
            self._receipts_table.setItem(row, 3, QTableWidgetItem(str(pay.get("payment_date", ""))))
            self._receipts_table.setItem(row, 4, QTableWidgetItem(pay.get("payment_method", "") or ""))

    def _view_receipt(self):
        """Receipt.printReceipt() - Display receipt details for a selected payment."""
        row = self._receipts_table.currentRow()
        if row < 0:
            show_error(self, "Please select a payment to view its receipt.")
            return

        pay_id_item = self._receipts_table.item(row, 1)
        if pay_id_item is None:
            return
        pay_id_str = pay_id_item.text()
        try:
            pay_id = int(pay_id_str)
        except ValueError:
            return
        payment = None
        for p in self._payments:
            if p.get("payment_id") == pay_id:
                payment = p
                break
        if not payment:
            return

        receipt = self.generateReceipt(payment)
        self.printReceipt(receipt)

    def printReceipt(self, receipt: dict):
        """Receipt.printReceipt() - Show receipt in a detail dialog."""
        details = [
            ("Receipt Number", str(receipt.get("receiptID", "N/A"))),
            ("Payment ID", str(receipt.get("paymentID", "N/A"))),
            ("Amount Paid", f"£{float(receipt.get('amount', 0)):,.2f}"),
            ("Payment Date", str(receipt.get("date", ""))),
            ("Payment Method", str(receipt.get("method", ""))),
            ("Transaction Ref", str(receipt.get("transactionRef", ""))),
            ("", ""),
            ("Paragon Apartment Management", "Thank you for your payment."),
        ]
        dlg = PAMSDetailDialog("Payment Receipt", details, self)
        dlg.exec()


# Panel 3: MyMaintenancePanel
# Class diagram: Tenant.submitMaintenanceRequest(description),
# Tenant.fillOutMaintenanceForm(formData), Tenant.trackMaintenanceRequestStatus(requestID),
# Tenant.submitFeedbackOrComplaint(feedback)

class MyMaintenancePanel(BasePanel):
    """Tenant view for maintenance requests and complaints."""

    def __init__(self, user_id: int = 0, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self._maintenance = []
        self._build_ui()

    def _build_ui(self):
        header = make_panel_header(
            "My Maintenance Requests",
            "Submit requests, track status, and submit feedback"
        )
        self._main_layout.addWidget(header)

        # Submit new request button
        top_row = QHBoxLayout()
        self._btn_submit = make_action_button("Submit New Request", T.ACCENT)
        self._btn_submit.clicked.connect(self._open_request_form)
        top_row.addWidget(self._btn_submit)

        self._btn_track = make_outline_button("Track Status", T.INFO)
        self._btn_track.clicked.connect(self._track_status)
        top_row.addWidget(self._btn_track)

        top_row.addStretch()
        self._main_layout.addLayout(top_row)

        # Maintenance requests table
        self._table = PAMSTableWidget([
            "ID", "Description", "Category", "Priority", "Status",
            "Reported Date", "Scheduled Date"
        ])
        self._main_layout.addWidget(self._table)
        self._refresh_table()

        # Feedback / complaint section
        complaint_row = QHBoxLayout()
        self._btn_complaint = make_outline_button("Submit Feedback / Complaint", T.WARNING)
        self._btn_complaint.clicked.connect(self._submit_complaint)
        complaint_row.addWidget(self._btn_complaint)
        complaint_row.addStretch()
        self._main_layout.addLayout(complaint_row)

        self._main_layout.addStretch()

    def _refresh_table(self):
        """Reload the maintenance request table for this tenant from the database."""
        if _DB_OK and self._user_id:
            try:
                self._maintenance = get_maintenance_for_tenant(self._user_id)
            except Exception as e:
                print(f"Error loading maintenance: {e}")
                self._maintenance = []
        self._table.setRowCount(len(self._maintenance))
        for row, req in enumerate(self._maintenance):
            self._table.setItem(row, 0, QTableWidgetItem(str(req.get("request_id", ""))))
            self._table.setItem(row, 1, QTableWidgetItem(req.get("description", "") or ""))
            self._table.setItem(row, 2, QTableWidgetItem(req.get("category", "") or ""))
            self._table.setItem(row, 3, QTableWidgetItem(req.get("priority", "") or ""))
            badge = StatusBadge(req.get("status", "") or "")
            self._table.setCellWidget(row, 4, badge)
            self._table.setItem(row, 5, QTableWidgetItem(str(req.get("report_date", "") or "")))
            scheduled = req.get("scheduled_date") or "Not scheduled"
            self._table.setItem(row, 6, QTableWidgetItem(str(scheduled)))

    def _open_request_form(self):
        """Open the maintenance request submission form."""
        fields = [
            {"key": "category", "label": "Category", "type": "combo",
             "options": ["Plumbing", "Electrical", "Heating", "Security", "General"]},
            {"key": "description", "label": "Description", "type": "textarea", "value": ""},
            {"key": "urgency", "label": "Urgency", "type": "combo",
             "options": ["Low", "Medium", "High", "Urgent"]},
        ]
        dlg = PAMSFormDialog("Submit Maintenance Request", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values.get("description"):
                show_error(self, "Please provide a description of the issue.")
                return
            self.submitMaintenanceRequest(values)

    def submitMaintenanceRequest(self, form_data: dict):
        """Tenant.submitMaintenanceRequest(description) - Create a new maintenance request in DB."""
        if not _DB_OK or not self._user_id:
            show_error(self, "Database not available.")
            return None
        # Get the tenant's apartment_id from their active lease
        try:
            lease = get_active_lease_for_tenant(self._user_id)
        except Exception:
            lease = None
        if not lease:
            show_error(self, "You must have an active lease to submit a maintenance request.")
            return None
        apartment_id = lease["apartmentID"]
        try:
            new_id = create_maintenance_request(
                apartment_id=apartment_id,
                tenant_id=self._user_id,
                description=form_data["description"],
                priority=form_data.get("urgency", "Low"),
                category=form_data.get("category", "General"),
            )
        except Exception as e:
            show_error(self, f"Failed to submit request: {e}")
            return None
        if new_id:
            self._refresh_table()
            show_success(self, f"Maintenance request #{new_id} submitted successfully.")
        else:
            show_error(self, "Failed to submit maintenance request.")
        return new_id

    def fillOutMaintenanceForm(self, form_data: dict) -> bool:
        """Tenant.fillOutMaintenanceForm(formData) - Validate and submit form data."""
        if not form_data.get("description"):
            return False
        result = self.submitMaintenanceRequest(form_data)
        return result is not None

    def _track_status(self):
        """Open a detail dialog for the selected maintenance request."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a request to track.")
            return
        req_id_item = self._table.item(row, 0)
        if req_id_item is None:
            return
        try:
            req_id = int(req_id_item.text())
        except ValueError:
            return
        self.trackMaintenanceRequestStatus(req_id)

    def trackMaintenanceRequestStatus(self, request_id: int) -> str:
        """Tenant.trackMaintenanceRequestStatus(requestID) - Show full request details."""
        request = None
        for r in self._maintenance:
            if r.get("request_id") == request_id:
                request = r
                break
        if not request:
            show_error(self, f"Request #{request_id} not found.")
            return ""

        details = [
            ("Request ID", str(request.get("request_id", ""))),
            ("Description", request.get("description", "") or ""),
            ("Category", request.get("category") or "N/A"),
            ("Priority", request.get("priority") or "N/A"),
            ("Status", request.get("status", "") or ""),
            ("Apartment", request.get("apartment_number") or "N/A"),
            ("Reported Date", str(request.get("report_date") or "N/A")),
            ("Assigned Staff", request.get("staff_name") or "Not yet assigned"),
            ("Scheduled Date", str(request.get("scheduled_date") or "Not scheduled")),
            ("Resolved Date", str(request.get("resolved_date") or "Pending")),
        ]
        dlg = PAMSDetailDialog("Maintenance Request Status", details, self)
        dlg.exec()
        return request.get("status", "")

    def _submit_complaint(self):
        """Open form to submit feedback or complaint."""
        fields = [
            {"key": "subject", "label": "Subject", "type": "text", "value": ""},
            {"key": "description", "label": "Description", "type": "textarea", "value": ""},
        ]
        dlg = PAMSFormDialog("Submit Feedback / Complaint", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values.get("subject") or not values.get("description"):
                show_error(self, "Please fill in both subject and description.")
                return
            self.submitFeedbackOrComplaint(values)

    def submitFeedbackOrComplaint(self, feedback: dict) -> int:
        """Tenant.submitFeedbackOrComplaint(feedback) - Add a complaint to the database."""
        if not _DB_OK or not self._user_id:
            show_error(self, "Database not available.")
            return 0
        try:
            complaint_id = create_complaint(
                tenant_id=self._user_id,
                subject=feedback["subject"],
                description=feedback["description"],
            )
        except Exception as e:
            show_error(self, f"Failed to submit complaint: {e}")
            return 0
        if complaint_id:
            show_success(self, f"Complaint #{complaint_id} submitted successfully.")
            return complaint_id
        else:
            show_error(self, "Failed to submit complaint.")
            return 0


# Panel 4: MyProfilePanel
# Class diagram: User.viewPersonalProfile(), Tenant.updateContactInfo(email, phone),
# Tenant.updatePersonalInfo(fname, lname, address), User.changePassword(oldPassword, newPassword)

class MyProfilePanel(BasePanel):
    """Tenant view of their personal profile and settings."""

    def __init__(self, user_id: int = 0, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self._user = self._get_current_user()
        self._build_ui()

    def _get_current_user(self) -> dict:
        """Load the current tenant's profile from the database."""
        if not _DB_OK or not self._user_id:
            return {}
        try:
            result = get_tenant_profile(self._user_id)
            return result or {}
        except Exception as e:
            print(f"Error loading profile: {e}")
            return {}

    def _build_ui(self):
        header = make_panel_header(
            "My Profile",
            "View and update your personal information"
        )
        self._main_layout.addWidget(header)

        # Profile card
        self._profile_card = SectionCard()
        self._profile_layout = QVBoxLayout(self._profile_card)
        self._profile_layout.setContentsMargins(24, 20, 24, 20)
        self._profile_layout.setSpacing(10)
        self._main_layout.addWidget(self._profile_card)

        self.viewPersonalProfile()

        # Edit button
        btn_row = QHBoxLayout()
        self._btn_edit = make_action_button("Edit Contact Info", T.ACCENT)
        self._btn_edit.clicked.connect(self._edit_contact_info)
        btn_row.addWidget(self._btn_edit)

        self._btn_edit_personal = make_outline_button("Edit Personal Info", T.INFO)
        self._btn_edit_personal.clicked.connect(self._edit_personal_info)
        btn_row.addWidget(self._btn_edit_personal)
        btn_row.addStretch()
        self._main_layout.addLayout(btn_row)

        # Change password section
        pwd_header = QLabel("Change Password")
        pwd_header.setStyleSheet(f"""
            color: {T.ACCENT}; font-size: 16px; font-weight: 700;
            background: transparent; padding-top: 12px;
        """)
        self._main_layout.addWidget(pwd_header)

        pwd_card = SectionCard()
        pwd_layout = QFormLayout(pwd_card)
        pwd_layout.setContentsMargins(24, 20, 24, 20)
        pwd_layout.setSpacing(12)

        input_style = f"""
            QLineEdit {{
                background-color: {T.BG_WHITE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {T.TEXT_DARK};
                min-height: 22px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {T.ACCENT};
            }}
        """
        label_style = f"color: {T.TEXT_DARK}; font-size: 13px; font-weight: 600;"

        lbl_old = QLabel("Current Password")
        lbl_old.setStyleSheet(label_style)
        self._old_pwd = QLineEdit()
        self._old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._old_pwd.setStyleSheet(input_style)

        lbl_new = QLabel("New Password")
        lbl_new.setStyleSheet(label_style)
        self._new_pwd = QLineEdit()
        self._new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_pwd.setStyleSheet(input_style)

        lbl_conf = QLabel("Confirm New Password")
        lbl_conf.setStyleSheet(label_style)
        self._confirm_pwd = QLineEdit()
        self._confirm_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_pwd.setStyleSheet(input_style)

        pwd_layout.addRow(lbl_old, self._old_pwd)
        pwd_layout.addRow(lbl_new, self._new_pwd)
        pwd_layout.addRow(lbl_conf, self._confirm_pwd)

        self._main_layout.addWidget(pwd_card)

        pwd_btn_row = QHBoxLayout()
        self._btn_change_pwd = make_action_button("Change Password", T.WARNING)
        self._btn_change_pwd.clicked.connect(self._change_password_clicked)
        pwd_btn_row.addWidget(self._btn_change_pwd)
        pwd_btn_row.addStretch()
        self._main_layout.addLayout(pwd_btn_row)

        self._main_layout.addStretch()

    def viewPersonalProfile(self):
        """User.viewPersonalProfile() - Display all profile details from the database."""
        # Clear existing
        while self._profile_layout.count():
            item = self._profile_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

        if not self._user:
            lbl = QLabel("User not found.")
            lbl.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 14px;")
            self._profile_layout.addWidget(lbl)
            return

        fname = self._user.get('fname', '')
        lname = self._user.get('lname', '')
        details = [
            ("Full Name", f"{fname} {lname}".strip()),
            ("Username", self._user.get("username", "")),
            ("Email", self._user.get("email", "")),
            ("Phone", self._user.get("phone_number", "")),
            ("Date of Birth", self._user.get("date_of_birth", "")),
            ("Occupation", self._user.get("occupation") or "—"),
            ("NI Number", self._user.get("ni_number") or "—"),
            ("References", self._user.get("references") or "—"),
            ("Role", self._user.get("role", "")),
        ]

        for label_text, value_text in details:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 13px; font-weight: 600;")
            lbl.setFixedWidth(160)
            val = QLabel(str(value_text))
            val.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 13px;")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, 1)
            self._profile_layout.addLayout(row)

    def _edit_contact_info(self):
        """Open form to edit contact information."""
        fields = [
            {"key": "email", "label": "Email", "type": "text",
             "value": self._user.get("email", "")},
            {"key": "phone", "label": "Phone Number", "type": "text",
             "value": self._user.get("phone_number", "")},
        ]
        dlg = PAMSFormDialog("Edit Contact Information", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            ok = self.updateContactInfo(values.get("email", ""), values.get("phone", ""))
            if ok:
                # Reload from DB to get fresh data
                self._user = self._get_current_user()
                self.viewPersonalProfile()
                show_success(self, "Contact information updated successfully.")
            else:
                show_error(self, "Failed to update contact information.")

    def updateContactInfo(self, email: str, phone: str) -> bool:
        """Tenant.updateContactInfo(email, phone) - Update email and phone in DB."""
        if not _DB_OK or not self._user_id:
            return False
        try:
            return update_tenant_contact(self._user_id, email=email or None, phone=phone or None)
        except Exception as e:
            print(f"Error updating contact: {e}")
            return False

    def _edit_personal_info(self):
        """Open form to edit personal information."""
        fields = [
            {"key": "fname", "label": "First Name", "type": "text",
             "value": self._user.get("fname", "")},
            {"key": "lname", "label": "Last Name", "type": "text",
             "value": self._user.get("lname", "")},
        ]
        dlg = PAMSFormDialog("Edit Personal Information", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            ok = self.updatePersonalInfo(
                values.get("fname", ""), values.get("lname", "")
            )
            if ok:
                self._user = self._get_current_user()
                self.viewPersonalProfile()
                show_success(self, "Personal information updated successfully.")
            else:
                show_error(self, "Failed to update personal information.")

    def updatePersonalInfo(self, fname: str, lname: str) -> bool:
        """Tenant.updatePersonalInfo(fname, lname) - Update name in DB."""
        if not _DB_OK or not self._user_id:
            return False
        try:
            return update_tenant_personal(self._user_id, fname=fname or None, lname=lname or None)
        except Exception as e:
            print(f"Error updating personal info: {e}")
            return False

    def _change_password_clicked(self):
        """Handle the Change Password button click."""
        old_pwd = self._old_pwd.text()
        new_pwd = self._new_pwd.text()
        confirm_pwd = self._confirm_pwd.text()

        if not old_pwd or not new_pwd or not confirm_pwd:
            show_error(self, "Please fill in all password fields.")
            return

        result = self.changePassword(old_pwd, new_pwd, confirm_pwd)
        if result:
            self._old_pwd.clear()
            self._new_pwd.clear()
            self._confirm_pwd.clear()

    def changePassword(self, old_password: str, new_password: str,
                       confirm_password: str = "") -> bool:
        """User.changePassword(oldPassword, newPassword) - Validate and change password in DB."""
        if not old_password:
            show_error(self, "Please enter your current password.")
            return False
        if new_password != confirm_password:
            show_error(self, "New password and confirmation do not match.")
            return False
        if len(new_password) < 6:
            show_error(self, "New password must be at least 6 characters long.")
            return False
        if not _DB_OK or not self._user_id:
            show_error(self, "Database not available.")
            return False
        try:
            ok = change_tenant_password(self._user_id, old_password, new_password)
        except Exception as e:
            show_error(self, f"Error changing password: {e}")
            return False
        if ok:
            show_success(self, "Password changed successfully.")
        else:
            show_error(self, "Current password is incorrect.")
        return ok


# Panel 5: NotificationsPanel
# Class diagram: Tenant.receiveNotificationsAndAlerts(), Notification.markAsRead(),
# Notification.resend()

class NotificationsPanel(BasePanel):
    """Tenant view of notifications and alerts."""

    def __init__(self, user_id: int = 0, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self._notifications = []
        self._build_ui()

    def _build_ui(self):
        header = make_panel_header(
            "Notifications",
            "View your alerts and notifications"
        )
        self._main_layout.addWidget(header)

        # Controls row
        controls = QHBoxLayout()

        # Filter combo
        lbl_filter = QLabel("Filter:")
        lbl_filter.setStyleSheet(f"color: {T.ACCENT}; font-weight: 600; font-size: 13px;")
        self._combo_filter = QComboBox()
        self._combo_filter.addItems(["All", "Payment", "Maintenance", "Lease"])
        self._combo_filter.setFixedHeight(36)
        self._combo_filter.setStyleSheet(f"""
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
        self._combo_filter.currentTextChanged.connect(self._on_filter_changed)

        # Unread count
        self._unread_label = QLabel()
        self._unread_label.setStyleSheet(f"""
            color: {T.DANGER}; font-size: 13px; font-weight: 600;
            background: transparent;
        """)

        controls.addWidget(lbl_filter)
        controls.addWidget(self._combo_filter)
        controls.addSpacing(20)
        controls.addWidget(self._unread_label)
        controls.addStretch()

        # Action buttons
        self._btn_mark_read = make_action_button("Mark as Read", T.ACCENT)
        self._btn_mark_read.clicked.connect(self._mark_read)
        controls.addWidget(self._btn_mark_read)

        self._btn_mark_all = make_outline_button("Mark All Read", T.INFO)
        self._btn_mark_all.clicked.connect(self._mark_all_read)
        controls.addWidget(self._btn_mark_all)

        self._main_layout.addLayout(controls)

        # Notifications table
        self._table = PAMSTableWidget([
            "ID", "Type", "Message", "Date", "Read"
        ])
        self._main_layout.addWidget(self._table)

        self._main_layout.addStretch()
        self.receiveNotificationsAndAlerts()

    def _on_filter_changed(self):
        self.receiveNotificationsAndAlerts()

    def receiveNotificationsAndAlerts(self):
        """Tenant.receiveNotificationsAndAlerts() - Load and display filtered notifications."""
        if _DB_OK and self._user_id:
            try:
                self._notifications = get_notifications_for_tenant(self._user_id)
            except Exception as e:
                print(f"Error loading notifications: {e}")
                self._notifications = []

        filter_type = self._combo_filter.currentText()
        notifications = list(self._notifications)
        if filter_type != "All":
            notifications = [n for n in notifications if n.get("notificationType") == filter_type]

        unread = sum(1 for n in self._notifications if not n.get("isRead", True))
        self._unread_label.setText(f"{unread} unread" if unread else "All read")

        self._table.setRowCount(len(notifications))
        for row, notif in enumerate(notifications):
            self._table.setItem(row, 0, QTableWidgetItem(str(notif.get("notificationID", ""))))
            self._table.setItem(row, 1, QTableWidgetItem(notif.get("notificationType", "") or ""))

            msg_item = QTableWidgetItem(notif.get("message", "") or "")
            if not notif.get("isRead", True):
                font = msg_item.font()
                font.setBold(True)
                msg_item.setFont(font)
            self._table.setItem(row, 2, msg_item)

            self._table.setItem(row, 3, QTableWidgetItem(str(notif.get("notificationDate", "") or "")))

            read_text = "Yes" if notif.get("isRead", False) else "No"
            badge = StatusBadge(read_text)
            self._table.setCellWidget(row, 4, badge)

    def _get_selected_notification(self) -> dict | None:
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a notification.")
            return None
        item = self._table.item(row, 0)
        if item is None:
            return None
        try:
            notif_id = int(item.text())
        except ValueError:
            return None
        for n in self._notifications:
            if n.get("notificationID") == notif_id:
                return n
        return None

    def _mark_read(self):
        """Mark the selected notification as read."""
        notif = self._get_selected_notification()
        if notif:
            self.markAsRead(notif)

    def markAsRead(self, notification: dict):
        """Notification.markAsRead() - Mark a notification as read in the DB."""
        if _DB_OK:
            try:
                mark_notification_read(notification["notificationID"])
            except Exception as e:
                print(f"Error marking notification read: {e}")
        notification["isRead"] = True
        self.receiveNotificationsAndAlerts()

    def _mark_all_read(self):
        """Mark all notifications as read (persisted to DB)."""
        if _DB_OK and self._user_id:
            try:
                mark_all_notifications_read(self._user_id)
            except Exception as e:
                print(f"Error marking all notifications read: {e}")
        for n in self._notifications:
            n["isRead"] = True
        self.receiveNotificationsAndAlerts()
        show_success(self, "All notifications marked as read.")

    def resend(self, notification: dict):
        """Notification.resend() - Re-send a notification (placeholder)."""
        show_success(self, f"Notification #{notification['notificationID']} has been resent.")
