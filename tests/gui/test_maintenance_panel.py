"""

24063400 - Rayyan Tahir

Unit tests for PAMS Maintenance Panel business logic — no live DB required.
"""
import sys
import pathlib
import importlib.util
import pytest
from unittest.mock import patch, MagicMock

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel,
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


def _make_action_button(text, color=None):  return QPushButton(text)
def _make_outline_button(text, color=None): return QPushButton(text)


_fake_dialogs = MagicMock()
_fake_dialogs.BasePanel           = FakeBasePanel
_fake_dialogs.PAMSTableWidget     = FakePAMSTableWidget
_fake_dialogs.make_panel_header   = _make_panel_header
_fake_dialogs.make_action_button  = _make_action_button
_fake_dialogs.make_outline_button = _make_outline_button
_fake_dialogs.SectionCard         = QWidget
_fake_dialogs.PAMSFormDialog      = MagicMock()
_fake_dialogs.PAMSDetailDialog    = MagicMock()
_fake_dialogs.confirm_action      = MagicMock(return_value=False)
_fake_dialogs.show_success        = MagicMock()
_fake_dialogs.show_error          = MagicMock()

_fake_main_window = MagicMock()
_fake_main_window.PAMSTheme       = MagicMock()

_fake_maintenance_models = MagicMock()
_fake_maintenance_models.get_all_maintenance_requests.return_value = []
_fake_maintenance_models.get_request_by_id.return_value = None
_fake_maintenance_models.update_maintenance_status.return_value = True
_fake_maintenance_models.update_maintenance_priority.return_value = True
_fake_maintenance_models.assign_staff_to_request.return_value = True
_fake_maintenance_models.update_scheduled_date.return_value = True
_fake_maintenance_models.update_maintenance_cost.return_value = True
_fake_maintenance_models.get_staff_availability.return_value = []
_fake_maintenance_models.get_all_staff.return_value = []
_fake_maintenance_models.get_all_maintenance_logs.return_value = []
_fake_maintenance_models.get_logs_for_request.return_value = []
_fake_maintenance_models.create_maintenance_log.return_value = 1
_fake_maintenance_models.get_maintenance_stats.return_value = {}

_MAINT_MOCKS = {
    "main_window":        _fake_main_window,
    "dialogs":            _fake_dialogs,
    "maintenance_models": _fake_maintenance_models,
    "tenant_models":      MagicMock(),
    "models":             MagicMock(),
    "mysql":              MagicMock(),
    "mysql.connector":    MagicMock(),
}

for _k, _v in _MAINT_MOCKS.items():
    sys.modules.setdefault(_k, _v)

ROOT               = pathlib.Path(__file__).resolve().parents[2]
MAINT_PANEL_PATH   = ROOT / "src" / "gui" / "maintenance_panel.py"


def load_maintenance_module():
    with patch.dict("sys.modules", _MAINT_MOCKS):
        spec   = importlib.util.spec_from_file_location("maintenance_panel", MAINT_PANEL_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module

class TestValidateRequestData:
    """TC-MNT-01: Maintenance request data validation logic."""

    @pytest.fixture(autouse=True)
    def panel(self):
        module = load_maintenance_module()
        p = module.MaintenanceRequestsPanel.__new__(module.MaintenanceRequestsPanel)
        p._observers = []
        p._requests  = []
        self._panel  = p

    def test_valid_request_passes_validation(self):
        """Complete request with description, tenant and apartment → True."""
        req = {
            "description":      "Leaking pipe in bathroom",
            "tenant_name":      "Alice Johnson",
            "apartment_number": "A101",
            "status":           "Open",
        }
        assert self._panel.validateRequestData(req) is True

    def test_missing_description_fails_validation(self):
        """Request without description → False."""
        req = {
            "description":      "",
            "tenant_name":      "Alice Johnson",
            "apartment_number": "A101",
        }
        assert self._panel.validateRequestData(req) is False

    def test_open_status_request_is_valid(self):
        """New request defaulting to status 'Open' passes validation."""
        req = {
            "description":      "Broken boiler",
            "tenant_name":      "Bob Smith",
            "apartment_number": "B202",
            "status":           "Open",
        }
        assert self._panel.validateRequestData(req) is True
        assert req["status"] == "Open"
