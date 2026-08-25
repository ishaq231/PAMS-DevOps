"""
24063400 - Rayyan Tahir

PAMS - Paragon Apartment Management System
Tenant panel GUI tests.
"""
import importlib.util
import pathlib
import sys
from unittest.mock import patch
from unittest.mock import MagicMock

sys.modules["tenant_models"] = MagicMock()
sys.modules["mysql"] = MagicMock()
sys.modules["mysql.connector"] = MagicMock()
GUI_PATH = pathlib.Path("src/gui").resolve()
if str(GUI_PATH) not in sys.path:
    sys.path.insert(0, str(GUI_PATH))


def load_tenant_module():
    file_path = pathlib.Path("src/gui/tenant_panel.py").resolve()
    spec = importlib.util.spec_from_file_location("tenant_panel", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def test_calculate_termination_penalty():
    module = load_tenant_module()
    panel = module.MyLeasePanel.__new__(module.MyLeasePanel)

    fake_lease = {
        "monthly_rent": 2000,
        "termination_penalty_percent": 5.0,
    }

    penalty = panel.calculateTerminationPenalty(fake_lease)

    assert penalty == 100.0
def test_verify_payment():
    module = load_tenant_module()
    panel = module.MyPaymentsPanel.__new__(module.MyPaymentsPanel)

    assert panel.verifyPayment(100.00, 100.00) is True
    assert panel.verifyPayment(100.00, 99.99) is False
    assert panel.verifyPayment(50.00, 50.001) is True  # difference is 0.001 < 0.01
def test_generate_receipt():
    module = load_tenant_module()

    panel = module.MyPaymentsPanel.__new__(module.MyPaymentsPanel)

    fake_payment = {
        "receipt_number": 123,
        "payment_id": 10,
        "amount_paid": 500,
        "payment_date": "2024-01-01",
        "payment_method": "Debit Card",
        "transaction_ref": "TXN-2024-99999",
    }

    receipt = panel.generateReceipt(fake_payment)

    assert receipt["receiptID"] == 123
    assert receipt["paymentID"] == 10
    assert receipt["amount"] == 500
    assert receipt["date"] == "2024-01-01"
    assert receipt["method"] == "Debit Card"
    assert receipt["transactionRef"] == "TXN-2024-99999"
def test_fill_out_maintenance_form():
    module = load_tenant_module()
    panel = module.MyMaintenancePanel.__new__(module.MyMaintenancePanel)
    panel.submitMaintenanceRequest = lambda data: True
    assert panel.fillOutMaintenanceForm({"description": ""}) is False
    assert panel.fillOutMaintenanceForm({"description": "Broken sink"}) is True
def test_track_status_found():
    """Real method: searches self._maintenance and returns the status string."""
    module = load_tenant_module()
    panel = module.MyMaintenancePanel.__new__(module.MyMaintenancePanel)
    panel._maintenance = [
        {"request_id": 1, "status": "Open",        "description": "Leaking pipe",
         "category": "Plumbing", "priority": "High",
         "report_date": "2026-03-01", "resolved_date": None},
        {"request_id": 2, "status": "In Progress",  "description": "Broken window",
         "category": "General",  "priority": "Medium",
         "report_date": "2026-03-05", "resolved_date": None},
        {"request_id": 3, "status": "Resolved",     "description": "Door lock",
         "category": "Security", "priority": "Low",
         "report_date": "2026-02-20", "resolved_date": "2026-02-25"},
    ]
    with patch.object(module, 'PAMSDetailDialog') as mock_dlg:
        mock_dlg.return_value.exec.return_value = None
        assert panel.trackMaintenanceRequestStatus(1) == "Open"
        assert panel.trackMaintenanceRequestStatus(2) == "In Progress"
        assert panel.trackMaintenanceRequestStatus(3) == "Resolved"


def test_track_status_not_found():
    """Real method: returns empty string when request_id does not exist."""
    module = load_tenant_module()
    panel = module.MyMaintenancePanel.__new__(module.MyMaintenancePanel)
    panel._maintenance = []

    with patch.object(module, 'show_error'):
        result = panel.trackMaintenanceRequestStatus(999)

    assert result == ""
def test_fill_out_maintenance_form_submit_fails():
    """fillOutMaintenanceForm returns False when submitMaintenanceRequest returns None."""
    module = load_tenant_module()
    panel = module.MyMaintenancePanel.__new__(module.MyMaintenancePanel)
    panel.submitMaintenanceRequest = lambda data: None

    assert panel.fillOutMaintenanceForm({"description": "Leaking pipe"}) is False
def test_calculate_termination_penalty_zero_rent():
    """Penalty is 0 when monthly_rent is 0."""
    module = load_tenant_module()
    panel = module.MyLeasePanel.__new__(module.MyLeasePanel)
    assert panel.calculateTerminationPenalty({"monthly_rent": 0}) == 0.0


def test_calculate_termination_penalty_custom_percent():
    """Penalty uses the termination_penalty_percent field from the lease."""
    module = load_tenant_module()
    panel = module.MyLeasePanel.__new__(module.MyLeasePanel)
    lease = {"monthly_rent": 1000, "termination_penalty_percent": 10.0}
    assert panel.calculateTerminationPenalty(lease) == 100.0


def test_calculate_termination_penalty_missing_percent_defaults_to_5():
    """When termination_penalty_percent is absent, defaults to 5%."""
    module = load_tenant_module()
    panel = module.MyLeasePanel.__new__(module.MyLeasePanel)
    lease = {"monthly_rent": 2000}  # no termination_penalty_percent key
    assert panel.calculateTerminationPenalty(lease) == 100.0
def test_verify_payment_exact_boundary():
    """A difference of exactly 0.01 is NOT < 0.01, so should return False."""
    module = load_tenant_module()
    panel = module.MyPaymentsPanel.__new__(module.MyPaymentsPanel)
    assert panel.verifyPayment(100.00, 100.01) is False
    assert panel.verifyPayment(0.00, 0.00) is True
def test_generate_receipt_fallback_keys():
    """generateReceipt falls back to alternate key names when primary keys are absent."""
    module = load_tenant_module()
    panel = module.MyPaymentsPanel.__new__(module.MyPaymentsPanel)

    fake_payment = {
        "receipt": "R-456",          # fallback for receipt_number
        "paymentID": 20,             # fallback for payment_id
        "amountPaid": 300,           # fallback for amount_paid
        "paymentDate": "2024-02-01", # fallback for payment_date
        "paymentMethod": "Credit Card",  # fallback for payment_method
        "transactionref": "TXN-ALT-123", # fallback for transaction_ref
    }

    receipt = panel.generateReceipt(fake_payment)
    assert receipt["receiptID"] == "R-456"
    assert receipt["paymentID"] == 20
    assert receipt["amount"] == 300
    assert receipt["date"] == "2024-02-01"
    assert receipt["method"] == "Credit Card"
    assert receipt["transactionRef"] == "TXN-ALT-123"
def test_change_password_empty_old_password():
    """changePassword returns False immediately if old password is empty."""
    module = load_tenant_module()
    panel = module.MyProfilePanel.__new__(module.MyProfilePanel)
    panel._user_id = 1

    with patch.object(module, 'show_error'):
        result = panel.changePassword("", "newpass123", "newpass123")

    assert result is False


def test_change_password_mismatch():
    """changePassword returns False when new password and confirmation don't match."""
    module = load_tenant_module()
    panel = module.MyProfilePanel.__new__(module.MyProfilePanel)
    panel._user_id = 1

    with patch.object(module, 'show_error'):
        result = panel.changePassword("oldpass", "newpass1", "newpass2")

    assert result is False


def test_change_password_too_short():
    """changePassword returns False when new password is shorter than 6 characters."""
    module = load_tenant_module()
    panel = module.MyProfilePanel.__new__(module.MyProfilePanel)
    panel._user_id = 1

    with patch.object(module, 'show_error'):
        result = panel.changePassword("oldpass", "abc", "abc")

    assert result is False
class TestViewActiveLeaseStatus:
    """TC-TEN-01: Tenant's active lease shows 'Active' status and remaining duration."""

    def test_calculate_remaining_duration_future_date(self):
        """calculateRemainingDuration returns a positive number for a future end date."""
        module = load_tenant_module()
        panel = module.MyLeasePanel.__new__(module.MyLeasePanel)
        remaining = panel.calculateRemainingDuration({"end_date": "2099-12-31"})
        assert remaining > 0

    def test_calculate_remaining_duration_past_date(self):
        """calculateRemainingDuration returns a non-positive number for a past end date."""
        module = load_tenant_module()
        panel = module.MyLeasePanel.__new__(module.MyLeasePanel)
        remaining = panel.calculateRemainingDuration({"end_date": "2000-01-01"})
        assert remaining <= 0

    def test_calculate_remaining_duration_missing_end_date(self):
        """calculateRemainingDuration returns 0 when end_date is absent."""
        module = load_tenant_module()
        panel = module.MyLeasePanel.__new__(module.MyLeasePanel)
        assert panel.calculateRemainingDuration({}) == 0

    def _active_lease_panel(self):
        """Helper: panel with mocked layout widgets and a future ACTIVE lease."""
        module = load_tenant_module()
        panel = module.MyLeasePanel.__new__(module.MyLeasePanel)
        panel._user_id = 1
        panel._lease = None
        panel._card_layout = MagicMock()
        panel._card_layout.count.return_value = 0
        panel._remaining_label = MagicMock()
        panel._btn_terminate = MagicMock()
        panel._get_tenant_lease = MagicMock(return_value={
            "leaseID": 1, "apartment_number": "A101",
            "start_date": "2025-01-01", "end_date": "2099-12-31",
            "lease_term_months": 12, "monthly_rent": 1200.00,
            "deposit_amount": 1200.00, "status": "ACTIVE",
        })
        return panel, module
    _widget  = staticmethod(lambda *a, **k: MagicMock())
    _layout  = staticmethod(lambda *a, **k: MagicMock())

    def test_active_db_status_mapped_to_display_active(self):
        """ACTIVE lease status is shown as 'Active' via StatusBadge."""
        panel, module = self._active_lease_panel()
        badge_calls = []
        with patch.object(module, 'QHBoxLayout', self._layout), \
             patch.object(module, 'QLabel', self._widget), \
             patch.object(module, 'StatusBadge',
                          side_effect=lambda t: badge_calls.append(t) or MagicMock()):
            panel.viewLeaseStatus()
        assert "Active" in badge_calls

    def test_active_lease_enables_terminate_button(self):
        """viewLeaseStatus enables the terminate button for ACTIVE leases."""
        panel, module = self._active_lease_panel()
        with patch.object(module, 'QHBoxLayout', self._layout), \
             patch.object(module, 'QLabel', self._widget), \
             patch.object(module, 'StatusBadge', self._widget):
            panel.viewLeaseStatus()
        panel._btn_terminate.setEnabled.assert_called_with(True)

    def test_remaining_duration_label_populated(self):
        """viewLeaseStatus writes 'Remaining Duration: N days' into the label."""
        panel, module = self._active_lease_panel()
        with patch.object(module, 'QHBoxLayout', self._layout), \
             patch.object(module, 'QLabel', self._widget), \
             patch.object(module, 'StatusBadge', self._widget):
            panel.viewLeaseStatus()
        call_text = panel._remaining_label.setText.call_args[0][0]
        assert call_text.startswith("Remaining Duration:")
        assert "days" in call_text
class TestUpdateContactInfo:
    """TC-TEN-03: Update Contact Info — email & phone changes are saved to DB."""

    def test_email_update_calls_db_with_correct_args(self):
        """updateContactInfo calls update_tenant_contact with the new email."""
        module = load_tenant_module()
        module._DB_OK = True           # DB failed to connect at import; force it
        panel = module.MyProfilePanel.__new__(module.MyProfilePanel)
        panel._user_id = 5
        mock_update = MagicMock(return_value=True)
        with patch.object(module, 'update_tenant_contact', mock_update):
            result = panel.updateContactInfo("new@example.com", "")
        assert result is True
        mock_update.assert_called_once_with(5, email="new@example.com", phone=None)

    def test_email_and_phone_both_forwarded_to_db(self):
        """updateContactInfo passes both email and phone to update_tenant_contact."""
        module = load_tenant_module()
        module._DB_OK = True
        panel = module.MyProfilePanel.__new__(module.MyProfilePanel)
        panel._user_id = 7
        mock_update = MagicMock(return_value=True)
        with patch.object(module, 'update_tenant_contact', mock_update):
            panel.updateContactInfo("test@example.com", "07700999999")
        mock_update.assert_called_once_with(7, email="test@example.com", phone="07700999999")

    def test_empty_email_normalised_to_none(self):
        """An empty email string is normalised to None before the DB call."""
        module = load_tenant_module()
        module._DB_OK = True
        panel = module.MyProfilePanel.__new__(module.MyProfilePanel)
        panel._user_id = 3
        mock_update = MagicMock(return_value=True)
        with patch.object(module, 'update_tenant_contact', mock_update):
            panel.updateContactInfo("", "07700111222")
        _, kwargs = mock_update.call_args
        assert kwargs["email"] is None

    def test_no_user_id_returns_false_without_db_call(self):
        """updateContactInfo returns False immediately when user_id is 0."""
        module = load_tenant_module()
        module._DB_OK = True
        panel = module.MyProfilePanel.__new__(module.MyProfilePanel)
        panel._user_id = 0
        mock_update = MagicMock()
        with patch.object(module, 'update_tenant_contact', mock_update):
            result = panel.updateContactInfo("new@example.com", "")
        assert result is False
        mock_update.assert_not_called()



