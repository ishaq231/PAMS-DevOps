"""

24063400 - Rayyan Tahir

Unit tests for PAMS Admin Panel business logic — no live DB required.

DB calls and Qt dialogs are mocked before the module is loaded.



Tests cover:
  - UserManagementPanel.viewAllUserAccounts()   → rows built correctly
  - UserManagementPanel.addUserAccounts()       → validation (missing fields)
  - ExpandBusinessPanel.expandBusinessToOtherCities()
      TC-APT-01: happy path, empty city error, DB failure
  - ApartmentManagementPanel._markUnderMaintenance()
      TC-APT-02: status update called / cancelled
  - ApartmentManagementPanel.assignApartmentToTenant()
      TC-APT-03: available apartment → create_lease() called
      TC-APT-04: occupied apartment → blocked with error

Run with:
    pytest tests/gui/test_admin_panel.py -v
"""


import sys
import pathlib
import importlib.util
import pytest
from unittest.mock import patch, MagicMock

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QDialog,
)

class FakeBasePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._main_layout = QVBoxLayout(self)
        self.setLayout(self._main_layout)


class FakePAMSTableWidget(QTableWidget):
    def __init__(self, headers):
        super().__init__()
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def populate(self, rows):
        self.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.setItem(r, c, QTableWidgetItem(str(value)))


def _make_panel_header(title, subtitle):
    w = QWidget()
    lo = QVBoxLayout(w)
    lo.addWidget(QLabel(title))
    lo.addWidget(QLabel(subtitle))
    return w


def _make_action_button(text, color):  return QPushButton(text)
def _make_outline_button(text, color): return QPushButton(text)


_fake_dialogs = MagicMock()
_fake_dialogs.BasePanel           = FakeBasePanel
_fake_dialogs.PAMSTableWidget     = FakePAMSTableWidget
_fake_dialogs.make_panel_header   = _make_panel_header
_fake_dialogs.make_action_button  = _make_action_button
_fake_dialogs.make_outline_button = _make_outline_button
_fake_dialogs.PAMSFormDialog      = MagicMock()
_fake_dialogs.PAMSDetailDialog    = MagicMock()
_fake_dialogs.confirm_action      = MagicMock()
_fake_dialogs.show_success        = MagicMock()
_fake_dialogs.show_error          = MagicMock()

sys.modules.setdefault("dialogs",             _fake_dialogs)
sys.modules.setdefault("main_window",         MagicMock())
sys.modules.setdefault("mysql",               MagicMock())
sys.modules.setdefault("mysql.connector",     MagicMock())
sys.modules.setdefault("dotenv",              MagicMock())
sys.modules.setdefault("bcrypt",              MagicMock())
sys.modules.setdefault("database",            MagicMock())
sys.modules.setdefault("database.connection", MagicMock())

ROOT             = pathlib.Path(__file__).resolve().parents[2]
ADMIN_PANEL_PATH = ROOT / "src" / "gui" / "admin_panel.py"


def _load_admin_panel(models_mock):
    """Load admin_panel.py with a specific models mock bound at import time."""
    with patch.dict("sys.modules", {"models": models_mock}):
        spec   = importlib.util.spec_from_file_location("admin_panel", ADMIN_PANEL_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module

AVAILABLE_APT = {
    "apartment_id": 10, "apartment_number": "A101",
    "occupation_status": "Available", "monthly_rent": 900.0, "location": "Bristol",
}

OCCUPIED_APT = {
    "apartment_id": 11, "apartment_number": "B202",
    "occupation_status": "Occupied", "monthly_rent": 1100.0, "location": "London",
}

@pytest.fixture
def user_panel(qtbot):
    models = MagicMock(get_all_users=lambda: [])
    module = _load_admin_panel(models)
    panel  = module.UserManagementPanel()
    qtbot.addWidget(panel)
    return panel, module


@pytest.fixture
def expand_panel(qtbot):
    models = MagicMock(get_all_locations=lambda: [])
    module = _load_admin_panel(models)
    panel  = module.ExpandBusinessPanel()
    qtbot.addWidget(panel)
    return panel, module


@pytest.fixture
def apt_panel(qtbot):
    models = MagicMock(get_all_apartments=lambda: [], get_all_tenants=lambda: [])
    module = _load_admin_panel(models)
    panel  = module.ApartmentManagementPanel()
    qtbot.addWidget(panel)
    return panel, module

class TestViewAllUserAccounts:

    def test_rows_formatted_correctly(self, qtbot, user_panel):
        """viewAllUserAccounts() builds one row per user with the correct columns."""
        panel, module = user_panel
        fake_users = [{
            "user_id": 1, "username": "admin", "fname": "John", "lname": "Doe",
            "email": "john@example.com", "phone_number": "123", "role": "Administrator",
        }]
        expected = [["1", "admin", "John", "Doe", "john@example.com", "123", "Administrator"]]

        with patch.object(module, "get_all_users", return_value=fake_users), \
             patch.object(panel._table, "populate") as mock_pop:
            panel.viewAllUserAccounts()

        mock_pop.assert_called_once_with(expected)

    def test_empty_user_list_populates_empty(self, qtbot, user_panel):
        """viewAllUserAccounts() with no users passes an empty list to populate()."""
        panel, module = user_panel

        with patch.object(module, "get_all_users", return_value=[]), \
             patch.object(panel._table, "populate") as mock_pop:
            panel.viewAllUserAccounts()

        mock_pop.assert_called_once_with([])

class TestAddUserAccountsValidation:

    def _accepted_dialog(self, values):
        dlg = MagicMock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.get_values.return_value = values
        return dlg

    def _base(self):
        return {
            "username": "", "password": "", "fname": "", "lname": "",
            "email": "", "phone_number": "", "date_of_birth": "2000-01-01",
            "occupation": "", "ni_number": "", "references": "", "role": "Tenant",
        }

    def test_missing_username_shows_error(self, qtbot, user_panel):
        panel, module = user_panel
        vals = {**self._base(), "fname": "John", "password": "pass123"}
        with patch.object(module, "PAMSFormDialog", return_value=self._accepted_dialog(vals)), \
             patch.object(module, "show_error") as mock_err:
            panel.addUserAccounts()
        mock_err.assert_called_once_with(panel, "Username and First Name are required.")

    def test_missing_first_name_shows_error(self, qtbot, user_panel):
        panel, module = user_panel
        vals = {**self._base(), "username": "johnny", "password": "pass123"}
        with patch.object(module, "PAMSFormDialog", return_value=self._accepted_dialog(vals)), \
             patch.object(module, "show_error") as mock_err:
            panel.addUserAccounts()
        mock_err.assert_called_once_with(panel, "Username and First Name are required.")

    def test_missing_password_shows_error(self, qtbot, user_panel):
        panel, module = user_panel
        vals = {**self._base(), "username": "johnny", "fname": "John"}
        with patch.object(module, "PAMSFormDialog", return_value=self._accepted_dialog(vals)), \
             patch.object(module, "show_error") as mock_err:
            panel.addUserAccounts()
        mock_err.assert_called_once_with(panel, "Password is required.")

class TestAddNewLocation:

    def test_empty_city_shows_error(self, qtbot, expand_panel):
        """TC-APT-01 (edge): Empty city name → validation error, DB not called."""
        panel, module = expand_panel
        dlg = MagicMock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.get_values.return_value = {"city": "", "manager": "Alice"}

        with patch.object(module, "PAMSFormDialog", return_value=dlg), \
             patch.object(module, "show_error") as mock_err, \
             patch.object(module, "add_location") as mock_add:
            panel.expandBusinessToOtherCities()

        mock_err.assert_called_once_with(panel, "City name is required.")
        mock_add.assert_not_called()

    def test_valid_city_calls_add_location(self, qtbot, expand_panel):
        """TC-APT-01 (happy path): 'Leeds' + manager → add_location() called, success shown."""
        panel, module = expand_panel
        dlg = MagicMock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.get_values.return_value = {"city": "Leeds", "manager": "Bob"}

        with patch.object(module, "PAMSFormDialog", return_value=dlg), \
             patch.object(module, "add_location", return_value=5) as mock_add, \
             patch.object(module, "show_success") as mock_ok, \
             patch.object(module, "get_all_locations", return_value=[]):
            panel.expandBusinessToOtherCities()

        mock_add.assert_called_once_with("Leeds", "Bob")
        mock_ok.assert_called_once()
        assert "Leeds" in mock_ok.call_args[0][1]

    def test_db_failure_shows_error(self, qtbot, expand_panel):
        """TC-APT-01 (edge): add_location() returns None → error message shown."""
        panel, module = expand_panel
        dlg = MagicMock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.get_values.return_value = {"city": "Leeds", "manager": "Bob"}

        with patch.object(module, "PAMSFormDialog", return_value=dlg), \
             patch.object(module, "add_location", return_value=None), \
             patch.object(module, "show_error") as mock_err:
            panel.expandBusinessToOtherCities()

        mock_err.assert_called_once_with(panel, "Failed to add location.")

class TestMarkUnderMaintenance:

    def test_confirmed_calls_update_status(self, qtbot, apt_panel):
        """TC-APT-02: Confirming calls update_apartment_status with 'Under Maintenance'."""
        panel, module = apt_panel

        with patch.object(panel, "_get_selected_apartment", return_value=AVAILABLE_APT), \
             patch.object(module, "confirm_action", return_value=True), \
             patch.object(module, "update_apartment_status", return_value=True) as mock_upd, \
             patch.object(module, "show_success") as mock_ok, \
             patch.object(panel, "viewApartments"):
            panel._markUnderMaintenance()

        mock_upd.assert_called_once_with(10, "Under Maintenance")
        mock_ok.assert_called_once()

    def test_cancelled_makes_no_db_call(self, qtbot, apt_panel):
        """TC-APT-02 (edge): Cancelling the confirmation dialog makes no DB call."""
        panel, module = apt_panel

        with patch.object(panel, "_get_selected_apartment", return_value=AVAILABLE_APT), \
             patch.object(module, "confirm_action", return_value=False), \
             patch.object(module, "update_apartment_status") as mock_upd:
            panel._markUnderMaintenance()

        mock_upd.assert_not_called()

class TestAssignApartmentToTenant:

    def test_available_apartment_creates_lease(self, qtbot, apt_panel):
        """TC-APT-03: Available apartment + valid form → create_lease() called."""
        panel, module = apt_panel
        dlg = MagicMock()
        dlg.exec.return_value = QDialog.DialogCode.Accepted
        dlg.get_values.return_value = {
            "apartment": "A101", "tenant": "Alice Smith (ID: 7)",
            "startDate": "2026-04-01", "endDate": "2027-03-31",
            "monthly_rent": 900.0, "deposit": 900.0, "term_months": 12,
        }

        with patch.object(panel, "_get_selected_apartment", return_value=AVAILABLE_APT), \
             patch.object(module, "get_all_tenants",
                          return_value=[{"fname": "Alice", "lname": "Smith", "user_id": 7}]), \
             patch.object(module, "PAMSFormDialog", return_value=dlg), \
             patch.object(module, "create_lease", return_value=True) as mock_lease, \
             patch.object(module, "show_success") as mock_ok, \
             patch.object(panel, "viewApartments"):
            panel.assignApartmentToTenant()

        mock_lease.assert_called_once_with(
            tenant_id=7, apartment_id=10,
            start_date="2026-04-01", end_date="2027-03-31",
            monthly_rent=900.0, deposit=900.0, term_months=12,
        )
        mock_ok.assert_called_once()

    def test_occupied_apartment_is_blocked(self, qtbot, apt_panel):
        """TC-APT-04: Occupied apartment → error shown, create_lease() never called."""
        panel, module = apt_panel

        with patch.object(panel, "_get_selected_apartment", return_value=OCCUPIED_APT), \
             patch.object(module, "show_error") as mock_err, \
             patch.object(module, "create_lease") as mock_lease:
            panel.assignApartmentToTenant()

        mock_err.assert_called_once_with(
            panel, "Only available apartments can be assigned to a tenant."
        )
        mock_lease.assert_not_called()

    def test_no_tenants_in_system_shows_error(self, qtbot, apt_panel):
        """TC-APT-03 (edge): No tenants registered → error shown, create_lease() not called."""
        panel, module = apt_panel

        with patch.object(panel, "_get_selected_apartment", return_value=AVAILABLE_APT), \
             patch.object(module, "get_all_tenants", return_value=[]), \
             patch.object(module, "show_error") as mock_err, \
             patch.object(module, "create_lease") as mock_lease:
            panel.assignApartmentToTenant()

        mock_err.assert_called_once_with(panel, "No tenants found in the system.")
        mock_lease.assert_not_called()
