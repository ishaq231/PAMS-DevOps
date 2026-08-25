"""

24063400 - Rayyan Tahir

Unit tests for PAMS Main Window business logic (no Qt required).



Tests cover:
  - Helper functions: _safe_float, _days_between
  - Role-based navigation key configuration
  - Role-based quick actions mapping
  - Stats aggregation logic (apartments, invoices, maintenance)
  - Finance stats aggregation
  - Bell click routing logic
  - Page title resolution

Run with:
    pytest tests/gui/test_main_window.py -v
"""

import pytest
import sys

def _safe_float(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _days_between(d1_str, d2_str):
    try:
        from datetime import datetime as _dt
        fmt = "%Y-%m-%d"
        return (_dt.strptime(d2_str[:10], fmt) - _dt.strptime(d1_str[:10], fmt)).days
    except Exception:
        return None


def compute_base_stats(apartments, invoices, requests):
    def _sf(v): return _safe_float(v)
    total_apts  = len(apartments)
    occupied    = sum(1 for a in apartments if a.get("occupation_status") == "Occupied")
    locations   = len({a.get("location", "") for a in apartments if a.get("location")})
    occ_pct     = round(occupied / total_apts * 100) if total_apts else 0
    pending_amt = sum(_sf(i.get("amount")) for i in invoices
                      if i.get("status") in ("Pending", "Overdue"))
    overdue_cnt = sum(1 for i in invoices if i.get("status") == "Overdue")
    paid_amt    = sum(_sf(i.get("amount")) for i in invoices if i.get("status") == "Paid")
    open_reqs   = sum(1 for r in requests if r.get("status") in ("Open", "In Progress"))
    high_pri    = sum(1 for r in requests
                      if r.get("status") in ("Open", "In Progress")
                      and r.get("priority") == "High")
    maint_costs = sum(_sf(r.get("cost")) for r in requests)
    return dict(total_apts=total_apts, occupied=occupied, locations=locations,
                occ_pct=occ_pct, pending_amt=pending_amt, overdue_cnt=overdue_cnt,
                paid_amt=paid_amt, open_reqs=open_reqs, high_pri=high_pri,
                maint_costs=maint_costs)


def compute_finance_stats(invoices, requests):
    s = compute_base_stats([], invoices, requests)
    return dict(
        collected=s["paid_amt"],
        outstanding=s["pending_amt"],
        overdue_cnt=s["overdue_cnt"],
        net_revenue=s["paid_amt"] - s["maint_costs"],
    )


def bell_nav_target(role: str, pages: dict) -> str:
    if role == "Tenant" and "notifications" in pages:
        return "notifications"
    return "dashboard"

ROLE_NAV_KEYS = {
    "Administrator":    ["dashboard", "users", "apartments", "tenants", "staff",
                         "leases", "reports", "settings"],
    "Manager":          ["dashboard", "occupancy", "expand", "locations", "users",
                         "apartments", "tenants", "leases", "settings", "register",
                         "maintenance", "complaints", "invoices", "payments", "late",
                         "fin_reports", "requests", "log", "schedule", "reports"],
    "Front Desk Staff": ["dashboard", "register", "tenants", "maintenance", "complaints"],
    "Finance Manager":  ["dashboard", "invoices", "payments", "late", "fin_reports"],
    "Maintenance Staff":["dashboard", "requests", "log", "schedule"],
    "Tenant":           ["dashboard", "my_lease", "my_payments", "my_maint",
                         "my_profile", "notifications"],
}

ROLE_ACTIONS = {
    "Administrator":    ["Register Apartment", "Manage Users", "Track Leases",
                         "Generate Report", "Assign Apartment", "View Complaints"],
    "Manager":          ["Performance Reports", "Expand Business", "Occupancy Overview",
                         "Manage Users", "View Invoices", "Maintenance Requests"],
    "Front Desk Staff": ["Register Tenant", "Handle Enquiry", "Log Complaint"],
    "Finance Manager":  ["Generate Invoice", "Record Payment",
                         "Late Payment Alerts", "Financial Summary"],
    "Maintenance Staff":["View My Requests", "Log Resolution", "Update Priority"],
    "Tenant":           ["Submit Request", "View Invoices", "Lease Details",
                         "Early Termination"],
}

ROLE_ACTION_NAVS = {
    "Administrator":    ["apartments", "users", "leases", "reports",
                         "apartments", "complaints"],
    "Front Desk Staff": ["register", "tenants", "complaints"],
    "Finance Manager":  ["invoices", "payments", "late", "fin_reports"],
    "Tenant":           ["my_maint", "my_payments", "my_lease", "my_lease"],
}

PAGE_TITLES = {
    "dashboard":     "Dashboard",
    "users":         "User Management",
    "apartments":    "Apartment Management",
    "tenants":       "Tenant Management",
    "leases":        "Lease Tracking",
    "staff":         "Staff Management",
    "reports":       "Reports",
    "settings":      "Settings",
    "occupancy":     "Occupancy Overview",
    "locations":     "Location Management",
    "expand":        "Expand Business",
    "register":      "Register Tenant",
    "maintenance":   "Maintenance Requests",
    "complaints":    "Complaints & Feedback",
    "invoices":      "Invoice Management",
    "payments":      "Payment Management",
    "late":          "Late Payment Alerts",
    "fin_reports":   "Financial Reports",
    "requests":      "My Maintenance Requests",
    "log":           "Log Resolution",
    "schedule":      "Schedule & Availability",
    "my_lease":      "My Lease Agreement",
    "my_payments":   "My Payments",
    "my_maint":      "My Maintenance Requests",
    "my_profile":    "My Profile",
    "notifications": "Notifications",
}

@pytest.fixture
def sample_apartments():
    return [
        {"apartment_id": 1, "apartment_number": "A101",
         "occupation_status": "Occupied", "location": "Bristol"},
        {"apartment_id": 2, "apartment_number": "A102",
         "occupation_status": "Vacant",   "location": "Bristol"},
        {"apartment_id": 3, "apartment_number": "B201",
         "occupation_status": "Occupied", "location": "London"},
    ]


@pytest.fixture
def sample_invoices():
    return [
        {"invoiceID": 1, "amount": 1200.0, "status": "Paid",    "due_date": "2026-03-15"},
        {"invoiceID": 2, "amount":  950.0, "status": "Pending", "due_date": "2026-03-20"},
        {"invoiceID": 3, "amount":  800.0, "status": "Overdue", "due_date": "2026-02-28"},
        {"invoiceID": 4, "amount":  600.0, "status": "Paid",    "due_date": "2026-02-10"},
    ]


@pytest.fixture
def sample_maintenance_requests():
    return [
        {"request_id": 1, "status": "Open",        "priority": "High",
         "cost": 150.0, "description": "Leaking pipe",
         "report_date": "2026-03-01", "resolved_date": None},
        {"request_id": 2, "status": "In Progress", "priority": "Medium",
         "cost":   0.0, "description": "Broken window",
         "report_date": "2026-03-05", "resolved_date": None},
        {"request_id": 3, "status": "Resolved",    "priority": "Low",
         "cost":  75.0, "description": "Door lock repair",
         "report_date": "2026-02-20", "resolved_date": "2026-02-25"},
    ]


@pytest.fixture
def all_pages():
    return {k: i for i, k in enumerate(PAGE_TITLES.keys())}

class TestSafeFloat:

    def test_int_value(self):          assert _safe_float(42)     == 42.0
    def test_float_string(self):       assert _safe_float("3.14") == 3.14
    def test_none_returns_zero(self):  assert _safe_float(None)   == 0.0
    def test_empty_string(self):       assert _safe_float("")     == 0.0
    def test_non_numeric(self):        assert _safe_float("abc")  == 0.0
    def test_zero_string(self):        assert _safe_float("0")    == 0.0
    def test_negative(self):           assert _safe_float(-5.5)   == -5.5
    def test_returns_float(self):      assert isinstance(_safe_float(10), float)

class TestDaysBetween:

    def test_same_date(self):           assert _days_between("2026-03-08", "2026-03-08") == 0
    def test_one_day(self):             assert _days_between("2026-03-08", "2026-03-09") == 1
    def test_negative(self):            assert _days_between("2026-03-10", "2026-03-08") == -2
    def test_across_months(self):       assert _days_between("2026-01-31", "2026-03-02") == 30
    def test_leap_year(self):           assert _days_between("2024-01-01", "2025-01-01") == 366
    def test_invalid_returns_none(self):assert _days_between("not-a-date", "2026-03-08") is None
    def test_empty_returns_none(self):  assert _days_between("", "2026-03-08") is None
    def test_truncates_datetime(self):  assert _days_between("2026-03-08T00:00:00", "2026-03-09T00:00:00") == 1

    @pytest.mark.parametrize("d1,d2,expected", [
        ("2026-06-01", "2026-06-08",  7),
        ("2026-01-01", "2026-04-01", 90),
        ("2024-02-28", "2024-03-01",  2),
    ])
    def test_parametrized(self, d1, d2, expected):
        assert _days_between(d1, d2) == expected

class TestRoleNavItems:

    def test_all_roles_have_dashboard(self):
        for role, keys in ROLE_NAV_KEYS.items():
            assert "dashboard" in keys, f"{role} missing dashboard"

    def test_administrator_keys(self):
        keys = ROLE_NAV_KEYS["Administrator"]
        for k in ["users", "apartments", "settings"]:
            assert k in keys

    def test_finance_manager_keys(self):
        for k in ["invoices", "payments", "late", "fin_reports"]:
            assert k in ROLE_NAV_KEYS["Finance Manager"]

    def test_front_desk_keys(self):
        for k in ["register", "tenants", "maintenance", "complaints"]:
            assert k in ROLE_NAV_KEYS["Front Desk Staff"]

    def test_tenant_personal_keys(self):
        for k in ["my_lease", "my_payments", "my_maint", "notifications"]:
            assert k in ROLE_NAV_KEYS["Tenant"]

    def test_tenant_no_admin_keys(self):
        tenant_keys = ROLE_NAV_KEYS["Tenant"]
        for k in ["users", "apartments", "leases", "staff"]:
            assert k not in tenant_keys

    def test_maintenance_staff_keys(self):
        for k in ["requests", "log", "schedule"]:
            assert k in ROLE_NAV_KEYS["Maintenance Staff"]

    def test_manager_inherits_keys(self):
        for k in ["register", "invoices", "requests", "users", "apartments"]:
            assert k in ROLE_NAV_KEYS["Manager"]

    @pytest.mark.parametrize("role", list(ROLE_NAV_KEYS.keys()))
    def test_no_duplicate_keys(self, role):
        keys = ROLE_NAV_KEYS[role]
        assert len(keys) == len(set(keys)), f"{role} has duplicate keys"

class TestRoleActions:

    def test_all_roles_have_actions(self):
        for role, actions in ROLE_ACTIONS.items():
            assert len(actions) > 0

    def test_administrator_six_actions(self):
        assert len(ROLE_ACTIONS["Administrator"]) == 6

    def test_front_desk_three_actions(self):
        assert len(ROLE_ACTIONS["Front Desk Staff"]) == 3

    def test_finance_manager_four_actions(self):
        assert len(ROLE_ACTIONS["Finance Manager"]) == 4

    def test_tenant_submit_request(self):
        assert "Submit Request" in ROLE_ACTIONS["Tenant"]

    def test_tenant_lease_details(self):
        assert "Lease Details" in ROLE_ACTIONS["Tenant"]

    def test_finance_generate_invoice(self):
        assert "Generate Invoice" in ROLE_ACTIONS["Finance Manager"]

    def test_admin_navs_valid(self):
        for nav in ROLE_ACTION_NAVS["Administrator"]:
            assert nav in PAGE_TITLES

    def test_front_desk_navs_valid(self):
        for nav in ROLE_ACTION_NAVS["Front Desk Staff"]:
            assert nav in PAGE_TITLES

    def test_finance_navs_valid(self):
        for nav in ROLE_ACTION_NAVS["Finance Manager"]:
            assert nav in PAGE_TITLES

    def test_tenant_navs_valid(self):
        for nav in ROLE_ACTION_NAVS["Tenant"]:
            assert nav in PAGE_TITLES

class TestPageTitles:

    def test_dashboard_title(self):
        assert PAGE_TITLES["dashboard"] == "Dashboard"

    def test_invoices_title(self):
        assert PAGE_TITLES["invoices"] == "Invoice Management"

    def test_all_titles_non_empty(self):
        for key, title in PAGE_TITLES.items():
            assert title.strip(), f"Title for '{key}' is empty"

    def test_all_role_nav_keys_have_titles(self):
        for role, keys in ROLE_NAV_KEYS.items():
            for key in keys:
                assert key in PAGE_TITLES, \
                    f"{role} nav key '{key}' has no page title"

    @pytest.mark.parametrize("key,expected", [
        ("register",   "Register Tenant"),
        ("complaints", "Complaints & Feedback"),
        ("late",       "Late Payment Alerts"),
        ("my_lease",   "My Lease Agreement"),
        ("schedule",   "Schedule & Availability"),
    ])
    def test_specific_titles(self, key, expected):
        assert PAGE_TITLES[key] == expected

class TestBaseStatsAggregation:

    def test_total_apartments(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["total_apts"] == 3

    def test_occupied_count(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["occupied"] == 2

    def test_location_count(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["locations"] == 2

    def test_occupancy_percentage(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["occ_pct"] == 67  # round(2/3 * 100)

    def test_pending_amount_includes_overdue(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["pending_amt"] == 1750.0  # 950 + 800

    def test_overdue_count(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["overdue_cnt"] == 1

    def test_paid_amount(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["paid_amt"] == 1800.0  # 1200 + 600

    def test_open_requests(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["open_reqs"] == 2  # Open + In Progress

    def test_high_priority_count(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["high_pri"] == 1

    def test_maintenance_costs(self, sample_apartments, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats(sample_apartments, sample_invoices, sample_maintenance_requests)
        assert s["maint_costs"] == 225.0  # 150 + 0 + 75

    def test_zero_apartments_zero_occ_pct(self, sample_invoices, sample_maintenance_requests):
        s = compute_base_stats([], sample_invoices, sample_maintenance_requests)
        assert s["occ_pct"] == 0
        assert s["total_apts"] == 0

    def test_all_vacant(self, sample_invoices, sample_maintenance_requests):
        apts = [{"occupation_status": "Vacant", "location": "Bristol"} for _ in range(3)]
        s = compute_base_stats(apts, sample_invoices, sample_maintenance_requests)
        assert s["occ_pct"] == 0
        assert s["occupied"] == 0

class TestFinanceStats:

    def test_collected(self, sample_invoices, sample_maintenance_requests):
        s = compute_finance_stats(sample_invoices, sample_maintenance_requests)
        assert s["collected"] == 1800.0

    def test_outstanding(self, sample_invoices, sample_maintenance_requests):
        s = compute_finance_stats(sample_invoices, sample_maintenance_requests)
        assert s["outstanding"] == 1750.0

    def test_overdue_count(self, sample_invoices, sample_maintenance_requests):
        s = compute_finance_stats(sample_invoices, sample_maintenance_requests)
        assert s["overdue_cnt"] == 1

    def test_net_revenue(self, sample_invoices, sample_maintenance_requests):
        s = compute_finance_stats(sample_invoices, sample_maintenance_requests)
        assert s["net_revenue"] == 1575.0

    def test_net_revenue_no_costs(self, sample_invoices):
        s = compute_finance_stats(sample_invoices, [])
        assert s["net_revenue"] == 1800.0

    def test_no_invoices_zero_collected(self, sample_maintenance_requests):
        s = compute_finance_stats([], sample_maintenance_requests)
        assert s["collected"] == 0.0
        assert s["outstanding"] == 0.0

class TestBellClickRouting:

    def test_tenant_routes_to_notifications(self, all_pages):
        assert bell_nav_target("Tenant", all_pages) == "notifications"

    def test_admin_routes_to_dashboard(self, all_pages):
        assert bell_nav_target("Administrator", all_pages) == "dashboard"

    def test_finance_manager_routes_to_dashboard(self, all_pages):
        assert bell_nav_target("Finance Manager", all_pages) == "dashboard"

    def test_front_desk_routes_to_dashboard(self, all_pages):
        assert bell_nav_target("Front Desk Staff", all_pages) == "dashboard"

    def test_maintenance_staff_routes_to_dashboard(self, all_pages):
        assert bell_nav_target("Maintenance Staff", all_pages) == "dashboard"

    def test_tenant_without_notifications_falls_back(self):
        pages = {k: i for i, k in enumerate(PAGE_TITLES.keys()) if k != "notifications"}
        assert bell_nav_target("Tenant", pages) == "dashboard"

    @pytest.mark.parametrize("role", [
        "Administrator", "Manager", "Finance Manager",
        "Maintenance Staff", "Front Desk Staff",
    ])
    def test_non_tenant_always_dashboard(self, role, all_pages):
        assert bell_nav_target(role, all_pages) == "dashboard"
