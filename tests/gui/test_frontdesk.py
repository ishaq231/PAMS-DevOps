"""

24063400 - Rayyan Tahir

Unit tests for PAMS Front Desk Staff panels — business logic only.
No database required; DB dependencies are mocked at import time.

Tests cover:
  - MaintenanceRegistrationPanel._PRIORITY_TO_DB / _PRIORITY_FROM_DB
      -> ACTUAL class attributes loaded from frontdesk_panel.py
  - RegisterTenantPanel.registerNewTenant() validation rules
      -> mirrors the inline validation (Qt-coupled, tested via pure-Python mirror)
  - Description build format: "[Category] description"
      -> mirrors registerMaintenanceRequestsAndComplaints() inline logic
  - Description parse: extract category and text from stored string
      -> mirrors MaintenanceRegistrationPanel._refresh_table() inline logic
  - Tenant ID extraction from combo selection text
      -> mirrors split("ID: ") logic in registerMaintenanceRequestsAndComplaints()
  - TenantInfoPanel search/filter logic
      -> mirrors _filter() case-insensitive column search
  - ComplaintsPanel status summary counting
      -> mirrors ComplaintsPanel._refresh_table() status-counting logic

Run with:
    pytest tests/gui/test_frontdesk.py -v
"""

import sys
import pathlib
import importlib.util
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QDialog

for _mod in ["mysql", "mysql.connector", "models"]:
    sys.modules.setdefault(_mod, MagicMock())

GUI_PATH = pathlib.Path("src/gui").resolve()
if str(GUI_PATH) not in sys.path:
    sys.path.insert(0, str(GUI_PATH))


def load_frontdesk_module():
    """Load frontdesk_panel.py with DB mocked out."""
    file_path = pathlib.Path("src/gui/frontdesk_panel.py").resolve()
    spec = importlib.util.spec_from_file_location("frontdesk_panel", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

REQUIRED_FIELDS = ["fname", "lname", "email", "phone", "dob", "username", "password"]


def validate_registration(data: dict) -> tuple[bool, str]:
    """
    Mirrors RegisterTenantPanel.registerNewTenant():
        if not all([fname, lname, email, phone, dob, username, password]):
            return False, "Please fill in all required fields (marked with *)."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
    """
    for field in REQUIRED_FIELDS:
        if not data.get(field, "").strip():
            return False, "Please fill in all required fields (marked with *)."
    if len(data["password"].strip()) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


def build_description(category: str, description: str, form_data: str = "") -> str:
    """
    Mirrors registerMaintenanceRequestsAndComplaints():
        full_desc = f"[{category}] {values['description']}"
        if values.get("formData", "").strip():
            full_desc += f"\n\nForm Data:\n{values['formData']}"
    """
    full = f"[{category}] {description}"
    if form_data.strip():
        full += f"\n\nForm Data:\n{form_data}"
    return full


def parse_description(raw: str) -> tuple[str, str]:
    """
    Mirrors MaintenanceRegistrationPanel._refresh_table():
        if desc.startswith("[") and "]" in desc:
            category = desc[1:desc.index("]")]
            desc = desc[desc.index("]") + 2:]
        else:
            category = "General"
    """
    if raw.startswith("[") and "]" in raw:
        category = raw[1:raw.index("]")]
        description = raw[raw.index("]") + 2:]
        return category, description
    return "General", raw


def extract_tenant_id(combo_text: str) -> int:
    """
    Mirrors tenant ID extraction in registerMaintenanceRequestsAndComplaints()
    and logComplaint():
        tenant_id = int(values["tenant"].split("ID: ")[1].rstrip(")"))
    """
    return int(combo_text.split("ID: ")[1].rstrip(")"))
def filter_tenants(tenants: list, search: str) -> list:
    """
    Mirrors TenantInfoPanel._filter():
        text = search.lower()
        visible = [t for t in all_tenants if any(text in str(v).lower() for v in t.values())]
    """
    text = search.lower()
    if not text:
        return tenants
    return [
        t for t in tenants
        if any(text in str(v).lower() for v in t.values())
    ]
def compute_complaint_summary(complaints: list) -> dict:
    """
    Mirrors ComplaintsPanel._refresh_table() status-counting:
        if status == "Open": open_c += 1
        elif status == "Under Review": review_c += 1
        elif status == "Resolved": resolved_c += 1
    """
    return {
        "total": len(complaints),
        "open": sum(1 for c in complaints if c["status"] == "Open"),
        "under_review": sum(1 for c in complaints if c["status"] == "Under Review"),
        "resolved": sum(1 for c in complaints if c["status"] == "Resolved"),
    }

@pytest.fixture(scope="module")
def fd_module():
    return load_frontdesk_module()


@pytest.fixture
def valid_tenant_data():
    return {
        "fname": "Alice", "lname": "Smith", "email": "alice@test.com",
        "phone": "07700123456", "dob": "1990-05-15",
        "username": "alicesmith", "password": "securepass",
    }


@pytest.fixture
def sample_tenants():
    return [
        {"user_id": 1, "fname": "Alice", "lname": "Smith",
         "email": "alice@test.com", "phone": "07700111111",
         "apartment_number": "A101", "lease_status": "Active"},
        {"user_id": 2, "fname": "Bob", "lname": "Jones",
         "email": "bob@test.com", "phone": "07700222222",
         "apartment_number": "B202", "lease_status": "Expired"},
        {"user_id": 3, "fname": "Carol", "lname": "White",
         "email": "carol@test.com", "phone": "07700333333",
         "apartment_number": "—", "lease_status": None},
    ]


@pytest.fixture
def sample_complaints():
    return [
        {"complaint_id": 1, "status": "Open",         "subject": "Noise"},
        {"complaint_id": 2, "status": "Under Review", "subject": "Leak"},
        {"complaint_id": 3, "status": "Resolved",     "subject": "Heating"},
        {"complaint_id": 4, "status": "Open",         "subject": "Pest"},
        {"complaint_id": 5, "status": "Resolved",     "subject": "Door"},
    ]

class TestPriorityMapping:

    @pytest.mark.parametrize("ui,db", [
        ("Urgent", "Emergency"),
        ("High",   "High"),
        ("Medium", "Medium"),
        ("Low",    "Low"),
    ])
    def test_ui_to_db_mapping(self, fd_module, ui, db):
        assert fd_module.MaintenanceRegistrationPanel._PRIORITY_TO_DB[ui] == db

    @pytest.mark.parametrize("db,ui", [
        ("Emergency", "Urgent"),
        ("High",      "High"),
        ("Medium",    "Medium"),
        ("Low",       "Low"),
    ])
    def test_db_to_ui_mapping(self, fd_module, db, ui):
        assert fd_module.MaintenanceRegistrationPanel._PRIORITY_FROM_DB[db] == ui

    def test_roundtrip_all_priorities(self, fd_module):
        to_db   = fd_module.MaintenanceRegistrationPanel._PRIORITY_TO_DB
        from_db = fd_module.MaintenanceRegistrationPanel._PRIORITY_FROM_DB
        for ui_label, db_val in to_db.items():
            assert from_db[db_val] == ui_label

class TestRegisterTenantValidation:

    def test_valid_data_passes(self, valid_tenant_data):
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is True
        assert msg == ""

    def test_missing_fname_fails(self, valid_tenant_data):
        valid_tenant_data["fname"] = ""
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is False
        assert "required" in msg.lower()

    def test_missing_email_fails(self, valid_tenant_data):
        valid_tenant_data["email"] = ""
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is False

    def test_missing_password_fails(self, valid_tenant_data):
        valid_tenant_data["password"] = ""
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is False

    def test_password_too_short_fails(self, valid_tenant_data):
        valid_tenant_data["password"] = "abc"
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is False
        assert "6 characters" in msg

    def test_password_exactly_6_passes(self, valid_tenant_data):
        valid_tenant_data["password"] = "abcdef"
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is True

    def test_password_longer_than_6_passes(self, valid_tenant_data):
        valid_tenant_data["password"] = "supersecurepassword"
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is True

    def test_whitespace_only_field_fails(self, valid_tenant_data):
        valid_tenant_data["fname"] = "   "
        ok, msg = validate_registration(valid_tenant_data)
        assert ok is False

    @pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
    def test_each_required_field_enforced(self, valid_tenant_data, missing_field):
        valid_tenant_data[missing_field] = ""
        ok, _ = validate_registration(valid_tenant_data)
        assert ok is False

class TestDescriptionBuilding:

    def test_basic_description(self):
        result = build_description("Plumbing", "Leaking tap")
        assert result == "[Plumbing] Leaking tap"

    def test_description_with_form_data(self):
        result = build_description("Electrical", "No power", "Room: Kitchen")
        assert "[Electrical] No power" in result
        assert "Form Data:" in result
        assert "Room: Kitchen" in result

    def test_empty_form_data_omitted(self):
        result = build_description("Heating", "Boiler broken", "")
        assert "Form Data:" not in result

    def test_whitespace_form_data_omitted(self):
        result = build_description("General", "Issue", "   ")
        assert "Form Data:" not in result

    @pytest.mark.parametrize("category", [
        "Plumbing", "Electrical", "Heating", "Security",
        "Structural", "Appliance", "General", "Other"
    ])
    def test_all_categories_format_correctly(self, category):
        result = build_description(category, "some issue")
        assert result.startswith(f"[{category}]")


class TestDescriptionParsing:

    def test_parses_category_and_description(self):
        category, desc = parse_description("[Plumbing] Leaking tap in bathroom")
        assert category == "Plumbing"
        assert desc == "Leaking tap in bathroom"

    def test_no_bracket_defaults_to_general(self):
        category, desc = parse_description("Random text with no category")
        assert category == "General"
        assert desc == "Random text with no category"

    def test_roundtrip_build_then_parse(self):
        original_cat = "Electrical"
        original_desc = "Fuse box tripped"
        built = build_description(original_cat, original_desc)
        parsed_cat, parsed_desc = parse_description(built)
        assert parsed_cat == original_cat
        assert parsed_desc == original_desc

    def test_empty_string_defaults_to_general(self):
        category, desc = parse_description("")
        assert category == "General"

    def test_bracket_only_no_crash(self):
        category, desc = parse_description("[NoClose")
        assert category == "General"

class TestTenantIdExtraction:

    def test_standard_format(self):
        assert extract_tenant_id("Alice Smith (ID: 42)") == 42

    def test_single_digit_id(self):
        assert extract_tenant_id("Bob Jones (ID: 7)") == 7

    def test_large_id(self):
        assert extract_tenant_id("Carol White (ID: 1234)") == 1234

    def test_invalid_format_raises(self):
        with pytest.raises((IndexError, ValueError)):
            extract_tenant_id("No ID here")

class TestTenantFilter:

    def test_empty_search_returns_all(self, sample_tenants):
        result = filter_tenants(sample_tenants, "")
        assert len(result) == 3

    def test_filter_by_first_name(self, sample_tenants):
        result = filter_tenants(sample_tenants, "alice")
        assert len(result) == 1
        assert result[0]["fname"] == "Alice"

    def test_filter_by_email(self, sample_tenants):
        result = filter_tenants(sample_tenants, "bob@test.com")
        assert len(result) == 1

    def test_filter_by_apartment(self, sample_tenants):
        result = filter_tenants(sample_tenants, "B202")
        assert len(result) == 1
        assert result[0]["fname"] == "Bob"

    def test_filter_case_insensitive(self, sample_tenants):
        result = filter_tenants(sample_tenants, "ALICE")
        assert len(result) == 1

    def test_filter_no_match_returns_empty(self, sample_tenants):
        result = filter_tenants(sample_tenants, "zzznomatch")
        assert len(result) == 0

    def test_filter_partial_match(self, sample_tenants):
        result = filter_tenants(sample_tenants, "07700")
        assert len(result) == 3  # all phone numbers start with 07700

    def test_filter_by_lease_status(self, sample_tenants):
        result = filter_tenants(sample_tenants, "expired")
        assert len(result) == 1
        assert result[0]["fname"] == "Bob"

class TestComplaintSummary:

    def test_total_count(self, sample_complaints):
        s = compute_complaint_summary(sample_complaints)
        assert s["total"] == 5

    def test_open_count(self, sample_complaints):
        s = compute_complaint_summary(sample_complaints)
        assert s["open"] == 2

    def test_under_review_count(self, sample_complaints):
        s = compute_complaint_summary(sample_complaints)
        assert s["under_review"] == 1

    def test_resolved_count(self, sample_complaints):
        s = compute_complaint_summary(sample_complaints)
        assert s["resolved"] == 2

    def test_empty_complaints(self):
        s = compute_complaint_summary([])
        assert s == {"total": 0, "open": 0, "under_review": 0, "resolved": 0}

    def test_all_open(self):
        complaints = [{"status": "Open"} for _ in range(4)]
        s = compute_complaint_summary(complaints)
        assert s["open"] == 4
        assert s["resolved"] == 0

    def test_counts_sum_to_known_statuses(self, sample_complaints):
        s = compute_complaint_summary(sample_complaints)
        accounted = s["open"] + s["under_review"] + s["resolved"]
        assert accounted <= s["total"]

    @pytest.mark.parametrize("status,key", [
        ("Open", "open"),
        ("Under Review", "under_review"),
        ("Resolved", "resolved"),
    ])
    def test_single_complaint_per_status(self, status, key):
        s = compute_complaint_summary([{"status": status}])
        assert s[key] == 1
        assert s["total"] == 1

class TestLogTenantEnquiry:
    """TC-TEN-05: Log Tenant Enquiry — saves to DB and refreshes Recent Enquiry Log."""
    def _make_panel(self, fd_module):
        """Return a TenantInfoPanel stub with the minimal attributes needed."""
        panel = fd_module.TenantInfoPanel.__new__(fd_module.TenantInfoPanel)
        panel._table = MagicMock()
        panel._table.currentRow.return_value = -1   # no row pre-selected
        panel._load_enquiries = MagicMock()
        return panel

    def _accepted_dialog(self, tenant, details, handled_by="Front Desk Staff"):
        """Return a mock PAMSFormDialog that immediately accepts with given values."""
        mock_dlg = MagicMock()
        mock_dlg.exec.return_value = QDialog.DialogCode.Accepted
        mock_dlg.get_values.return_value = {
            "tenant": tenant,
            "details": details,
            "handledBy": handled_by,
        }
        return mock_dlg

    def test_create_enquiry_called_with_correct_args(self, fd_module):
        """_handleEnquiry calls create_enquiry with the submitted tenant and details."""
        panel = self._make_panel(fd_module)
        mock_dlg = self._accepted_dialog("Alice Smith", "Lost apartment keys")
        mock_create = MagicMock(return_value=42)

        with patch.object(fd_module, 'PAMSFormDialog', return_value=mock_dlg), \
             patch.object(fd_module, 'create_enquiry', mock_create), \
             patch.object(fd_module, 'show_success'):
            panel._handleEnquiry()

        mock_create.assert_called_once_with(
            tenant_name="Alice Smith",
            enquiry_details="Lost apartment keys",
            handled_by="Front Desk Staff",
            tenant_id=None,
        )

    def test_enquiry_log_refreshed_after_successful_save(self, fd_module):
        """_handleEnquiry calls _load_enquiries to refresh the log after saving."""
        panel = self._make_panel(fd_module)
        mock_dlg = self._accepted_dialog("Bob Jones", "Noise complaint from above")

        with patch.object(fd_module, 'PAMSFormDialog', return_value=mock_dlg), \
             patch.object(fd_module, 'create_enquiry', return_value=1), \
             patch.object(fd_module, 'show_success'):
            panel._handleEnquiry()

        panel._load_enquiries.assert_called_once()

    def test_empty_details_aborts_without_db_call(self, fd_module):
        """_handleEnquiry rejects whitespace-only details and never calls create_enquiry."""
        panel = self._make_panel(fd_module)
        mock_dlg = self._accepted_dialog("Alice Smith", "   ")  # whitespace only
        mock_create = MagicMock()

        with patch.object(fd_module, 'PAMSFormDialog', return_value=mock_dlg), \
             patch.object(fd_module, 'create_enquiry', mock_create), \
             patch.object(fd_module, 'show_error'):
            panel._handleEnquiry()

        mock_create.assert_not_called()