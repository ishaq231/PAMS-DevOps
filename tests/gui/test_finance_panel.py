"""

24063400 - Rayyan Tahir

Pytest unit tests for PAMS Finance Manager panel — business logic only.
No Qt, no database, no mocking required.

Run with:
    pytest test_finance_panel.py -v

Covers:
  - InvoiceManagementPanel.isOverdue()
  - InvoiceManagementPanel.calculateLateFee()
  - PaymentManagementPanel.validatePaymentAmount()
  - LatePaymentPanel late fee row calculation
  - FinancialReportsPanel report field calculations
  - TC-FIN-01: addInvoice() calls create_invoice DB function
  - TC-FIN-02: processPayment() calls create_payment after validation passes
  - TC-FIN-03: validatePaymentAmount() rejects overpayment (£1500 > £1200)
  - TC-FIN-04: calculateLateFee(279) == £1395.00
  - TC-FIN-05: _notifyAll() calls _create_notification per overdue tenant
"""


import sys
import pathlib
import importlib.util
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QDialog

def is_overdue(invoice: dict, today: date = None) -> bool:
    """Mirrors InvoiceManagementPanel.isOverdue()"""
    today = today or date.today()
    if invoice.get("status") == "Paid":
        return False
    due_str = invoice.get("due_date", "")
    if not due_str:
        return False
    due = date.fromisoformat(str(due_str))
    return today > due


def calculate_late_fee(days_late: int) -> float:
    """Mirrors InvoiceManagementPanel.calculateLateFee() — £5/day"""
    return days_late * 5.0


def validate_payment_amount(amount: float, invoice_amount: float) -> bool:
    """Mirrors PaymentManagementPanel.validatePaymentAmount()"""
    return amount <= invoice_amount


def compute_report_fields(invoices: list, payments: list,
                          maint_costs: float = 300.0) -> dict:
    """Mirrors FinancialReportsPanel.generateFinancialReport() calculations."""
    total_collected = sum(float(p["amount_paid"]) for p in payments)
    pending         = sum(float(i["amount"]) for i in invoices if i["status"] == "Pending")
    overdue_inv     = [i for i in invoices if i["status"] == "Overdue"]
    overdue_amt     = sum(float(i["amount"]) for i in overdue_inv)
    late_count      = len(overdue_inv)
    total_late_fees = late_count * 50.0
    net_revenue     = total_collected - maint_costs
    return dict(
        total_collected=total_collected,
        pending=pending,
        overdue_amt=overdue_amt,
        late_count=late_count,
        total_late_fees=total_late_fees,
        net_revenue=net_revenue,
    )

TODAY = date.today()
YESTERDAY = (TODAY - timedelta(days=1)).isoformat()
TOMORROW  = (TODAY + timedelta(days=1)).isoformat()
TEN_DAYS_AGO = (TODAY - timedelta(days=10)).isoformat()


@pytest.fixture
def pending_invoice():
    return {"invoiceID": 1, "status": "Pending", "amount": 1200.0, "due_date": TOMORROW}

@pytest.fixture
def overdue_invoice():
    return {"invoiceID": 2, "status": "Overdue", "amount": 950.0, "due_date": YESTERDAY}

@pytest.fixture
def paid_invoice():
    return {"invoiceID": 3, "status": "Paid", "amount": 800.0, "due_date": YESTERDAY}

@pytest.fixture
def sample_payments():
    return [
        {"payment_id": 1, "invoice_id": 1, "amount_paid": 1200.0,
         "payment_method": "Bank Transfer", "transaction_ref": "TXN-001",
         "payment_date": TODAY.isoformat(), "tenant_name": "Alice"},
        {"payment_id": 2, "invoice_id": 2, "amount_paid": 950.0,
         "payment_method": "Cash", "transaction_ref": "TXN-002",
         "payment_date": TODAY.isoformat(), "tenant_name": "Bob"},
    ]

@pytest.fixture
def mixed_invoices(pending_invoice, overdue_invoice, paid_invoice):
    return [pending_invoice, overdue_invoice, paid_invoice]

class TestIsOverdue:

    def test_overdue_status_past_due_date(self, overdue_invoice):
        assert is_overdue(overdue_invoice) is True

    def test_paid_invoice_never_overdue(self, paid_invoice):
        assert is_overdue(paid_invoice) is False

    def test_pending_future_due_date_not_overdue(self, pending_invoice):
        assert is_overdue(pending_invoice) is False

    def test_pending_past_due_date_is_overdue(self):
        inv = {"status": "Pending", "amount": 500.0, "due_date": YESTERDAY}
        assert is_overdue(inv) is True

    def test_missing_due_date_not_overdue(self):
        inv = {"status": "Overdue", "amount": 500.0, "due_date": ""}
        assert is_overdue(inv) is False

    def test_due_today_not_overdue(self):
        inv = {"status": "Pending", "amount": 500.0, "due_date": TODAY.isoformat()}
        assert is_overdue(inv) is False

    def test_overdue_10_days_ago(self):
        inv = {"status": "Overdue", "amount": 500.0, "due_date": TEN_DAYS_AGO}
        assert is_overdue(inv) is True

    def test_custom_today_param(self):
        inv = {"status": "Pending", "amount": 500.0, "due_date": "2025-01-01"}
        assert is_overdue(inv, today=date(2025, 1, 2)) is True
        assert is_overdue(inv, today=date(2024, 12, 31)) is False

class TestCalculateLateFee:

    def test_zero_days(self):
        assert calculate_late_fee(0) == 0.0

    def test_one_day(self):
        assert calculate_late_fee(1) == 5.0

    def test_ten_days(self):
        assert calculate_late_fee(10) == 50.0

    def test_thirty_days(self):
        assert calculate_late_fee(30) == 150.0

    def test_returns_float(self):
        assert isinstance(calculate_late_fee(7), float)

    def test_large_value(self):
        assert calculate_late_fee(365) == 1825.0

    @pytest.mark.parametrize("days,expected", [
        (1, 5.0),
        (5, 25.0),
        (14, 70.0),
        (100, 500.0),
    ])
    def test_parametrized(self, days, expected):
        assert calculate_late_fee(days) == expected

class TestValidatePaymentAmount:

    def test_exact_amount_valid(self):
        assert validate_payment_amount(1200.0, 1200.0) is True

    def test_partial_payment_valid(self):
        assert validate_payment_amount(600.0, 1200.0) is True

    def test_overpayment_invalid(self):
        assert validate_payment_amount(1500.0, 1200.0) is False

    def test_zero_payment_valid(self):
        assert validate_payment_amount(0.0, 1200.0) is True

    def test_penny_over_invalid(self):
        assert validate_payment_amount(1200.01, 1200.00) is False

    @pytest.mark.parametrize("paid,invoice,expected", [
        (100.0, 200.0, True),
        (200.0, 200.0, True),
        (200.01, 200.0, False),
        (0.0, 500.0, True),
    ])
    def test_parametrized(self, paid, invoice, expected):
        assert validate_payment_amount(paid, invoice) == expected

class TestComputeReportFields:

    def test_total_collected(self, mixed_invoices, sample_payments):
        r = compute_report_fields(mixed_invoices, sample_payments)
        assert r["total_collected"] == 2150.0

    def test_pending_amount(self, mixed_invoices, sample_payments):
        r = compute_report_fields(mixed_invoices, sample_payments)
        assert r["pending"] == 1200.0

    def test_overdue_amount(self, mixed_invoices, sample_payments):
        r = compute_report_fields(mixed_invoices, sample_payments)
        assert r["overdue_amt"] == 950.0

    def test_late_count(self, mixed_invoices, sample_payments):
        r = compute_report_fields(mixed_invoices, sample_payments)
        assert r["late_count"] == 1

    def test_total_late_fees(self, mixed_invoices, sample_payments):
        r = compute_report_fields(mixed_invoices, sample_payments)
        assert r["total_late_fees"] == 50.0

    def test_net_revenue(self, mixed_invoices, sample_payments):
        r = compute_report_fields(mixed_invoices, sample_payments)
        assert r["net_revenue"] == 1850.0

    def test_no_payments_zero_collected(self, mixed_invoices):
        r = compute_report_fields(mixed_invoices, [])
        assert r["total_collected"] == 0.0
        assert r["net_revenue"] == -300.0

    def test_no_invoices_no_overdue(self, sample_payments):
        r = compute_report_fields([], sample_payments)
        assert r["overdue_amt"] == 0.0
        assert r["late_count"] == 0
        assert r["total_late_fees"] == 0.0

    def test_custom_maintenance_cost(self, mixed_invoices, sample_payments):
        r = compute_report_fields(mixed_invoices, sample_payments, maint_costs=500.0)
        assert r["net_revenue"] == 1650.0

    def test_multiple_overdue_invoices(self, sample_payments):
        invoices = [
            {"invoiceID": 1, "status": "Overdue", "amount": 400.0, "due_date": YESTERDAY},
            {"invoiceID": 2, "status": "Overdue", "amount": 600.0, "due_date": YESTERDAY},
            {"invoiceID": 3, "status": "Paid",    "amount": 800.0, "due_date": YESTERDAY},
        ]
        r = compute_report_fields(invoices, sample_payments)
        assert r["late_count"] == 2
        assert r["overdue_amt"] == 1000.0
        assert r["total_late_fees"] == 100.0

class TestLatePaymentRowCalc:
    """Tests the per-invoice late fee logic used when building table rows."""

    def _row_totals(self, invoice: dict, today: date = None) -> dict:
        """Replicates the row-building logic in LatePaymentPanel._refresh_table()"""
        today = today or date.today()
        due = date.fromisoformat(str(invoice["due_date"]))
        days_late = (today - due).days
        late_fee = days_late * 5.0
        total = float(invoice["amount"]) + late_fee
        return {"days_late": days_late, "late_fee": late_fee, "total": total}

    def test_days_late_correct(self):
        inv = {"amount": 500.0, "due_date": TEN_DAYS_AGO}
        r = self._row_totals(inv)
        assert r["days_late"] == 10

    def test_late_fee_correct(self):
        inv = {"amount": 500.0, "due_date": TEN_DAYS_AGO}
        r = self._row_totals(inv)
        assert r["late_fee"] == 50.0

    def test_total_due_correct(self):
        inv = {"amount": 500.0, "due_date": TEN_DAYS_AGO}
        r = self._row_totals(inv)
        assert r["total"] == 550.0

    def test_one_day_late(self):
        inv = {"amount": 1000.0, "due_date": YESTERDAY}
        r = self._row_totals(inv)
        assert r["days_late"] == 1
        assert r["late_fee"] == 5.0
        assert r["total"] == 1005.0

GUI_PATH = pathlib.Path("src/gui").resolve()
if str(GUI_PATH) not in sys.path:
    sys.path.insert(0, str(GUI_PATH))


def _make_finance_mocks():
    """Return a dict of sys.modules patches that satisfy finance_panel imports."""
    fm = MagicMock()
    fm.get_all_invoices.return_value = []
    fm.create_invoice.return_value = 99
    fm.create_payment.return_value = (5, 1005)
    fm.get_all_payments.return_value = []
    fm.get_all_leases.return_value = []
    lm = MagicMock()
    lm.get_all_leases.return_value = []
    tm = MagicMock()
    tm.create_notification.return_value = None
    tm.get_all_tenants.return_value = []
    return {
        "finance_models": fm,
        "lease_models":   lm,
        "tenant_models":  tm,
        "models":         MagicMock(),
        "mysql":          MagicMock(),
        "mysql.connector": MagicMock(),
    }


def load_finance_module():
    mocks = _make_finance_mocks()
    for k, v in mocks.items():
        sys.modules.setdefault(k, v)
    file_path = pathlib.Path("src/gui/finance_panel.py").resolve()
    spec = importlib.util.spec_from_file_location("finance_panel", file_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict("sys.modules", mocks):
        spec.loader.exec_module(module)
    return module

class TestCalculateLateFeeExactScenario:
    """TC-FIN-04: 279 days overdue at £5/day = £1395.00."""

    def test_279_days_late_equals_1395(self):
        assert calculate_late_fee(279) == 1395.00

    def test_279_days_late_on_panel_instance(self):
        module = load_finance_module()
        panel = module.InvoiceManagementPanel.__new__(
            module.InvoiceManagementPanel)
        assert panel.calculateLateFee(279) == 1395.00

class TestAddInvoice:
    """TC-FIN-01: addInvoice() calls create_invoice and refreshes on success."""

    def _panel_with_lease(self, module):
        """InvoiceManagementPanel stub with one available lease."""
        panel = module.InvoiceManagementPanel.__new__(
            module.InvoiceManagementPanel)
        panel._invoices = []
        panel._lease_lookup = {}
        panel._load_from_db = MagicMock()
        return panel

    def _accepted_dialog(self, values):
        dlg = MagicMock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.get_values.return_value = values
        return dlg

    def test_create_invoice_called_with_correct_args(self):
        module = load_finance_module()
        panel = self._panel_with_lease(module)

        lease = {"leaseID": 3, "tenant_name": "Alice", "apartment_number": "A101"}
        mock_create = MagicMock(return_value=42)
        mock_leases = MagicMock(return_value=[lease])

        dialog_values = {
            "lease": "Lease #3 — Alice — A101",
            "amount": 1200.0,
            "dueDate": "2026-04-01",
            "issueDate": "2026-03-01",
            "description": "Monthly rent",
        }

        with patch.object(module, 'get_all_leases', mock_leases), \
             patch.object(module, 'create_invoice', mock_create), \
             patch.object(module, 'PAMSFormDialog',
                          return_value=self._accepted_dialog(dialog_values)), \
             patch.object(module, 'show_success'):
            panel.addInvoice()

        mock_create.assert_called_once_with(
            lease_id=3,
            amount=1200.0,
            due_date="2026-04-01",
            issue_date="2026-03-01",
            description="Monthly rent",
        )

    def test_db_refresh_called_after_successful_create(self):
        module = load_finance_module()
        panel = self._panel_with_lease(module)

        lease = {"leaseID": 1, "tenant_name": "Bob", "apartment_number": "B202"}
        dialog_values = {
            "lease": "Lease #1 — Bob — B202",
            "amount": 900.0, "dueDate": "2026-04-01",
            "issueDate": "2026-03-01", "description": "",
        }

        with patch.object(module, 'get_all_leases', return_value=[lease]), \
             patch.object(module, 'create_invoice', return_value=7), \
             patch.object(module, 'PAMSFormDialog',
                          return_value=self._accepted_dialog(dialog_values)), \
             patch.object(module, 'show_success'):
            panel.addInvoice()

        panel._load_from_db.assert_called_once()

    def test_no_leases_shows_error_without_db_call(self):
        module = load_finance_module()
        panel = self._panel_with_lease(module)
        mock_create = MagicMock()

        with patch.object(module, 'get_all_leases', return_value=[]), \
             patch.object(module, 'create_invoice', mock_create), \
             patch.object(module, 'show_error'):
            panel.addInvoice()

        mock_create.assert_not_called()

class TestProcessPayment:
    """TC-FIN-02: processPayment() validates amount then calls create_payment."""

    def _panel_with_invoice(self, module, amount=1200.0):
        panel = module.PaymentManagementPanel.__new__(
            module.PaymentManagementPanel)
        panel._invoices = [
            {"invoiceID": 1, "tenant_name": "Alice", "amount": amount,
             "status": "Pending", "tenant_id": 10}
        ]
        panel._payments = []
        panel._load_from_db = MagicMock()
        return panel

    def _accepted_dialog(self, values):
        dlg = MagicMock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.get_values.return_value = values
        return dlg

    def test_create_payment_called_with_correct_args(self):
        module = load_finance_module()
        panel = self._panel_with_invoice(module)
        mock_create = MagicMock(return_value=(5, 1005))

        dialog_values = {
            "invoice": "INV-001 — Alice — £1200.00 [Pending]",
            "amount": 1200.0,
            "method": "Bank Transfer",
            "transactionref": "TXN-2026-001",
            "date": "2026-03-08",
        }

        with patch.object(module, 'PAMSFormDialog',
                          return_value=self._accepted_dialog(dialog_values)), \
             patch.object(module, 'create_payment', mock_create), \
             patch.object(module, 'show_success'):
            panel.processPayment()

        mock_create.assert_called_once_with(
            invoice_id=1,
            amount_paid=1200.0,
            payment_date="2026-03-08",
            payment_method="Bank Transfer",
            transaction_ref="TXN-2026-001",
        )

    def test_overpayment_aborts_without_db_call(self):
        """TC-FIN-03 via processPayment: £1500 against £1200 invoice is rejected."""
        module = load_finance_module()
        panel = self._panel_with_invoice(module, amount=1200.0)
        mock_create = MagicMock()

        dialog_values = {
            "invoice": "INV-001 — Alice — £1200.00 [Pending]",
            "amount": 1500.0,
            "method": "Bank Transfer",
            "transactionref": "TXN-OVER",
            "date": "2026-03-08",
        }

        with patch.object(module, 'PAMSFormDialog',
                          return_value=self._accepted_dialog(dialog_values)), \
             patch.object(module, 'create_payment', mock_create), \
             patch.object(module, 'show_error'):
            panel.processPayment()

        mock_create.assert_not_called()

    def test_db_refresh_called_after_successful_payment(self):
        module = load_finance_module()
        panel = self._panel_with_invoice(module)

        dialog_values = {
            "invoice": "INV-001 — Alice — £1200.00 [Pending]",
            "amount": 1200.0, "method": "Cash",
            "transactionref": "TXN-X", "date": "2026-03-08",
        }

        with patch.object(module, 'PAMSFormDialog',
                          return_value=self._accepted_dialog(dialog_values)), \
             patch.object(module, 'create_payment', return_value=(3, 1003)), \
             patch.object(module, 'show_success'):
            panel.processPayment()

        panel._load_from_db.assert_called_once()

class TestNotifyAllLateTenants:
    """TC-FIN-05: _notifyAll() calls _create_notification for every overdue tenant."""

    def _panel_with_overdue(self, module, invoices):
        panel = module.LatePaymentPanel.__new__(module.LatePaymentPanel)
        panel._invoices = invoices
        panel._table = MagicMock()
        return panel

    def test_notification_sent_for_each_overdue_invoice(self):
        module = load_finance_module()
        overdue = [
            {"invoiceID": 1, "status": "Overdue", "tenant_id": 10,
             "tenant_name": "Alice", "amount": 1200.0, "due_date": "2026-01-01"},
            {"invoiceID": 2, "status": "Overdue", "tenant_id": 20,
             "tenant_name": "Bob",   "amount": 950.0,  "due_date": "2026-01-15"},
        ]
        panel = self._panel_with_overdue(module, overdue)
        mock_notify = MagicMock()

        with patch.object(module, '_create_notification', mock_notify), \
             patch.object(module, 'confirm_action', return_value=True), \
             patch.object(module, 'show_success'):
            panel._notifyAll()

        assert mock_notify.call_count == 2
        called_ids = {call.args[0] for call in mock_notify.call_args_list}
        assert called_ids == {10, 20}

    def test_no_overdue_invoices_sends_no_notifications(self):
        module = load_finance_module()
        panel = self._panel_with_overdue(module, [
            {"invoiceID": 3, "status": "Paid", "tenant_id": 30,
             "tenant_name": "Carol", "amount": 800.0, "due_date": "2026-01-01"},
        ])
        mock_notify = MagicMock()

        with patch.object(module, '_create_notification', mock_notify), \
             patch.object(module, 'show_success'):
            panel._notifyAll()

        mock_notify.assert_not_called()

    def test_notification_type_is_payment(self):
        module = load_finance_module()
        overdue = [
            {"invoiceID": 4, "status": "Overdue", "tenant_id": 40,
             "tenant_name": "Dave", "amount": 600.0, "due_date": "2026-02-01"},
        ]
        panel = self._panel_with_overdue(module, overdue)
        mock_notify = MagicMock()

        with patch.object(module, '_create_notification', mock_notify), \
             patch.object(module, 'confirm_action', return_value=True), \
             patch.object(module, 'show_success'):
            panel._notifyAll()

        _, ntype = mock_notify.call_args.args[0], mock_notify.call_args.args[2]
        assert ntype == "Payment"