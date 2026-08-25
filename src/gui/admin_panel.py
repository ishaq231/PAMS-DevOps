"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Administrator Panels — User Management, Apartments, Tenants, Leases, Reports, Settings

Implements all Administrator class methods and use-case operations
"""

import sys
import os
import csv as _csv
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
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QLineEdit, QComboBox, QTextEdit, QDateEdit,
    QMessageBox, QSpinBox, QDoubleSpinBox, QScrollArea,
    QFormLayout, QTabWidget, QSizePolicy, QFileDialog
)
from PyQt6.QtCore import Qt, QDate

try:
    from main_window import PAMSTheme
except ImportError:
    from dialogs import PAMSTheme

from dialogs import (
    PAMSTableWidget, StatusBadge, make_action_button, make_outline_button,
    make_panel_header, SectionCard, PAMSFormDialog, PAMSDetailDialog,
    confirm_action, show_success, show_error, BasePanel,
)

from models import (
    get_all_users, get_user_by_id, admin_add_user, update_user, delete_user,
    get_all_apartments, update_apartment, update_apartment_status, update_apartment_rent,
    get_all_tenants, get_all_leases, get_leases_for_user, create_lease,
    update_lease, update_lease_status, terminate_lease,
    get_all_invoices, get_all_maintenance_requests,
    get_all_locations, add_location,
    get_user_count, get_apartment_count, change_password,
    get_all_staff, update_staff_member,
)

try:
    from tenant_models import create_notification as _create_notification
except ImportError:
    _create_notification = None


#  USER MANAGEMENT PANEL

class UserManagementPanel(BasePanel):
    """
    Administrator → User Management
    Methods: viewAllUserAccounts, addUserAccounts, updateUserAccounts,
             deleteUserAccounts (via Manage User Accounts use-case),
             viewUserDetails, viewUserFeedbackOrComplaints,
             viewUserLeaseRequests
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        # Header
        header = make_panel_header(
            "User Management",
            "Add, update, delete and view all user accounts (Manage User Accounts)"
        )
        self._main_layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_add = make_action_button("+ Add User Account", T.ACCENT)
        self._btn_edit = make_action_button("Edit User", T.INFO)
        self._btn_delete = make_action_button("Delete User", T.DANGER)
        self._btn_view = make_outline_button("View Details", T.ACCENT)
        self._btn_feedback = make_outline_button("Feedback / Complaints", T.WARNING)
        self._btn_lease_req = make_outline_button("Lease Requests", T.INFO)

        self._btn_add.clicked.connect(self.addUserAccounts)
        self._btn_edit.clicked.connect(self.updateUserAccounts)
        self._btn_delete.clicked.connect(self.deleteUserAccounts)
        self._btn_view.clicked.connect(self.viewUserDetails)
        self._btn_feedback.clicked.connect(self.viewUserFeedbackOrComplaints)
        self._btn_lease_req.clicked.connect(self.viewUserLeaseRequests)

        toolbar.addWidget(self._btn_add)
        toolbar.addWidget(self._btn_edit)
        toolbar.addWidget(self._btn_delete)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_view)
        toolbar.addWidget(self._btn_feedback)
        toolbar.addWidget(self._btn_lease_req)
        self._main_layout.addLayout(toolbar)

        # Search
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search users by name, email or role...")
        self._search.setFixedHeight(36)
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {T.BG_WHITE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
                color: {T.TEXT_DARK};
            }}
            QLineEdit:focus {{ border: 1.5px solid {T.ACCENT}; }}
        """)
        self._search.textChanged.connect(self._filter_table)
        search_row.addWidget(self._search)
        self._main_layout.addLayout(search_row)

        # Table
        self._table = PAMSTableWidget([
            "ID", "Username", "First Name", "Last Name", "Email",
            "Phone", "Role"
        ])
        self._main_layout.addWidget(self._table)

        self.viewAllUserAccounts()

    # Administrator.viewAllUserAccounts()

    def viewAllUserAccounts(self):
        """Load and display all user accounts from the database."""
        users = get_all_users()
        rows = []
        for u in users:
            rows.append([
                str(u["user_id"]), u.get("username", ""),
                u.get("fname", ""), u.get("lname", ""),
                u.get("email", ""), u.get("phone_number", "") or "",
                u.get("role", ""),
            ])
        self._table.populate(rows)

    # Administrator.addUserAccounts()

    def addUserAccounts(self):
        """Open form dialog to add a new user account."""
        fields = [
            {"key": "username", "label": "Username", "type": "text", "value": ""},
            {"key": "password", "label": "Password", "type": "password", "value": ""},
            {"key": "fname", "label": "First Name", "type": "text", "value": ""},
            {"key": "lname", "label": "Last Name", "type": "text", "value": ""},
            {"key": "email", "label": "Email", "type": "text", "value": ""},
            {"key": "phone_number", "label": "Phone Number", "type": "text", "value": ""},
            {"key": "date_of_birth", "label": "Date of Birth", "type": "date", "value": "2000-01-01"},
            {"key": "occupation", "label": "Occupation", "type": "text", "value": ""},
            {"key": "ni_number", "label": "NI Number", "type": "text", "value": ""},
            {"key": "references", "label": "References", "type": "text", "value": ""},
            {"key": "role", "label": "Role", "type": "combo",
             "options": ["Administrator", "Manager", "Front Desk Staff",
                         "Finance Manager", "Maintenance Staff", "Tenant"],
             "value": "Tenant"},
        ]
        dlg = PAMSFormDialog("Add New User Account", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values.get("username") or not values.get("fname"):
                show_error(self, "Username and First Name are required.")
                return
            if not values.get("password"):
                show_error(self, "Password is required.")
                return
            new_id = admin_add_user(
                fname=values["fname"], lname=values["lname"],
                email=values["email"], phone=values["phone_number"],
                dob=values["date_of_birth"], role=values["role"],
                username=values["username"], password=values["password"],
                occupation=values.get("occupation"),
                ni_number=values.get("ni_number"),
                references=values.get("references"),
            )
            if new_id:
                self.viewAllUserAccounts()
                show_success(self, f"User '{values['username']}' added successfully.")
            else:
                show_error(self, "Failed to add user. Username or email may already exist.")

    # Administrator.updateUserAccounts()

    def updateUserAccounts(self):
        """Edit the selected user account."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a user to edit.")
            return

        user_id = int(self._table.item(row, 0).text())
        user = get_user_by_id(user_id)
        if not user:
            show_error(self, "Could not load user details.")
            return

        fields = [
            {"key": "username", "label": "Username", "type": "text", "value": user.get("username", "")},
            {"key": "fname", "label": "First Name", "type": "text", "value": user.get("fname", "")},
            {"key": "lname", "label": "Last Name", "type": "text", "value": user.get("lname", "")},
            {"key": "email", "label": "Email", "type": "text", "value": user.get("email", "")},
            {"key": "phone_number", "label": "Phone Number", "type": "text",
             "value": user.get("phone_number", "") or ""},
            {"key": "date_of_birth", "label": "Date of Birth", "type": "date",
             "value": user.get("date_of_birth", "2000-01-01") or "2000-01-01"},
            {"key": "occupation", "label": "Occupation", "type": "text",
             "value": user.get("occupation", "") or ""},
            {"key": "ni_number", "label": "NI Number", "type": "text",
             "value": user.get("ni_number", "") or ""},
            {"key": "references", "label": "References", "type": "text",
             "value": user.get("references", "") or ""},
            {"key": "role", "label": "Role", "type": "combo",
             "options": ["Administrator", "Manager", "Front Desk Staff",
                         "Finance Manager", "Maintenance Staff", "Tenant"],
             "value": user.get("role", "Tenant")},
        ]
        dlg = PAMSFormDialog(f"Edit User — {user['fname']} {user['lname']}", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            success = update_user(
                user_id=user_id,
                fname=values["fname"], lname=values["lname"],
                email=values["email"], phone=values["phone_number"],
                dob=values["date_of_birth"], role=values["role"],
                username=values["username"],
                occupation=values.get("occupation"),
                ni_number=values.get("ni_number"),
                references=values.get("references"),
            )
            if success:
                self.viewAllUserAccounts()
                show_success(self, f"User '{values['username']}' updated successfully.")
            else:
                show_error(self, "Failed to update user.")

    # Delete User Accounts (use-case: Manage User Accounts)

    def deleteUserAccounts(self):
        """Delete the selected user account."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a user to delete.")
            return

        user_id = int(self._table.item(row, 0).text())
        fname = self._table.item(row, 2).text()
        lname = self._table.item(row, 3).text()

        if confirm_action(self, "Delete User Account",
                          f"Are you sure you want to delete '{fname} {lname}'?\n"
                          f"This action cannot be undone."):
            if delete_user(user_id):
                self.viewAllUserAccounts()
                show_success(self, f"User '{fname} {lname}' has been deleted.")
            else:
                show_error(self, "Failed to delete user. They may have related records.")

    # Administrator.viewUserDetails()

    def viewUserDetails(self):
        """Show full details of the selected user."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a user to view.")
            return

        user_id = int(self._table.item(row, 0).text())
        user = get_user_by_id(user_id)
        if not user:
            show_error(self, "Could not load user details.")
            return

        details = [
            ("User ID", str(user["user_id"])),
            ("Username", user.get("username", "")),
            ("First Name", user.get("fname", "")),
            ("Last Name", user.get("lname", "")),
            ("Email", user.get("email", "")),
            ("Phone Number", user.get("phone_number", "") or "—"),
            ("Date of Birth", user.get("date_of_birth", "") or "—"),
            ("Occupation", user.get("occupation", "") or "—"),
            ("NI Number", user.get("ni_number", "") or "—"),
            ("References", user.get("references", "") or "—"),
            ("Role", user.get("role", "")),
        ]
        dlg = PAMSDetailDialog(f"User Details — {user['fname']} {user['lname']}", details, self)
        dlg.exec()

    # Administrator.viewUserFeedbackOrComplaints()

    def viewUserFeedbackOrComplaints(self):
        """View feedback and complaints for the selected user."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a user to view their feedback.")
            return

        user_id = int(self._table.item(row, 0).text())
        user = get_user_by_id(user_id)
        if not user:
            show_error(self, "Could not load user details.")
            return

        # Maintenance requests reported by this user serve as complaints/feedback
        all_requests = get_all_maintenance_requests()
        user_requests = [r for r in all_requests
                         if r.get("tenant_name") == f"{user['fname']} {user['lname']}"]

        if not user_requests:
            show_success(self, f"No feedback or complaints found for {user['fname']} {user['lname']}.")
            return

        details = []
        for r in user_requests:
            details.append(("Request #", str(r["request_id"])))
            details.append(("Date", r.get("report_date", "—")))
            details.append(("Apartment", str(r.get("apartment_number", "—"))))
            details.append(("Description", r.get("description", "")))
            details.append(("Priority", r.get("priority", "—")))
            details.append(("Status", r.get("status", "—")))
            details.append(("", "─" * 40))

        dlg = PAMSDetailDialog(
            f"Feedback & Complaints — {user['fname']} {user['lname']}", details, self
        )
        dlg.exec()

    # Administrator.viewUserLeaseRequests()

    def viewUserLeaseRequests(self):
        """View lease requests for the selected user."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a user to view their lease requests.")
            return

        user_id = int(self._table.item(row, 0).text())
        user = get_user_by_id(user_id)
        if not user:
            show_error(self, "Could not load user details.")
            return

        leases = get_leases_for_user(user_id)

        if not leases:
            show_success(self, f"No lease requests found for {user['fname']} {user['lname']}.")
            return

        details = []
        for l in leases:
            details.append(("Lease ID", str(l["leaseID"])))
            details.append(("Apartment", str(l.get("apartment_number", "—"))))
            details.append(("Start Date", l.get("start_date", "—")))
            details.append(("End Date", l.get("end_date", "—")))
            details.append(("Monthly Rent", f"£{float(l.get('monthly_rent', 0)):.2f}"))
            details.append(("Status", l.get("status", "—")))
            details.append(("", "─" * 40))

        dlg = PAMSDetailDialog(
            f"Lease Requests — {user['fname']} {user['lname']}", details, self
        )
        dlg.exec()

    # validateAdminPermissions()

    def validateAdminPermissions(self) -> bool:
        """Check if current user has admin permissions."""
        return True

    # Filter / Search

    def _filter_table(self, text: str):
        """Filter the user table by search text."""
        text = text.lower()
        for row in range(self._table.rowCount()):
            match = False
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self._table.setRowHidden(row, not match)


#  APARTMENT MANAGEMENT PANEL

class ApartmentManagementPanel(BasePanel):
    """
    Administrator → Apartments
    Methods: viewApartments, viewApartmentRegistration,
             updateApartmentRegistration, assignApartmentToTenant,
             updateRent, changeOccupancyStatus, updateAmenities,
             markUnderMaintenance, markAvailable, getOccupancyStatus,
             calculateTotalRent
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Apartment Management",
            "View, register, update and assign apartments"
        )
        self._main_layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_view_reg = make_outline_button("View Registration", T.INFO)
        self._btn_update_reg = make_action_button("Update Registration", T.INFO)
        self._btn_assign = make_action_button("Assign to Tenant", T.ACCENT)
        self._btn_update_rent = make_outline_button("Update Rent", T.WARNING)
        self._btn_mark_maint = make_action_button("Mark Under Maintenance", T.DANGER)
        self._btn_mark_avail = make_action_button("Mark Available", T.SUCCESS)

        self._btn_view_reg.clicked.connect(self.viewApartmentRegistration)
        self._btn_update_reg.clicked.connect(self.updateApartmentRegistration)
        self._btn_assign.clicked.connect(self.assignApartmentToTenant)
        self._btn_update_rent.clicked.connect(self._updateRent)
        self._btn_mark_maint.clicked.connect(self._markUnderMaintenance)
        self._btn_mark_avail.clicked.connect(self._markAvailable)

        toolbar.addWidget(self._btn_view_reg)
        toolbar.addWidget(self._btn_update_reg)
        toolbar.addWidget(self._btn_assign)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_update_rent)
        toolbar.addWidget(self._btn_mark_maint)
        toolbar.addWidget(self._btn_mark_avail)
        self._main_layout.addLayout(toolbar)

        # Table
        self._table = PAMSTableWidget([
            "ID", "Number", "Location", "Type", "Monthly Rent",
            "Rooms", "Sq Ft", "Amenities", "Status"
        ])
        self._main_layout.addWidget(self._table)

        self.viewApartments()

    # Administrator.viewApartments()

    def viewApartments(self):
        """Display all apartments from the database."""
        apartments = get_all_apartments()
        rows = []
        for a in apartments:
            rows.append([
                str(a["apartment_id"]),
                str(a.get("apartment_number", "")),
                a.get("location", "—"),
                a.get("type", ""),
                f"£{float(a.get('monthly_rent', 0)):.2f}",
                str(a.get("number_of_rooms", "")),
                str(a.get("square_footage", "")),
                a.get("amenities", ""),
                a.get("occupation_status", ""),
            ])
        self._table.populate(rows)

    # Administrator.viewApartmentRegistration()

    def viewApartmentRegistration(self):
        """View full registration details for the selected apartment."""
        apt = self._get_selected_apartment()
        if not apt:
            return

        occ_status = apt.get("occupation_status", "—")
        rent = float(apt.get("monthly_rent", 0))

        details = [
            ("Apartment ID", str(apt["apartment_id"])),
            ("Number", str(apt.get("apartment_number", ""))),
            ("Location", apt.get("location", "—")),
            ("Type", apt.get("type", "")),
            ("Monthly Rent", f"£{rent:.2f}"),
            ("Number of Rooms", str(apt.get("number_of_rooms", ""))),
            ("Square Footage", f"{apt.get('square_footage', '')} sq ft"),
            ("Amenities", apt.get("amenities", "") or "None"),
            ("Occupancy Status", occ_status),
            ("Total Rent (12 months)", f"£{rent * 12:.2f}"),
        ]
        dlg = PAMSDetailDialog(
            f"Apartment Registration — {apt.get('apartment_number', '')}", details, self
        )
        dlg.exec()

    # Administrator.updateApartmentRegistration()

    def updateApartmentRegistration(self):
        """Edit registration details for the selected apartment."""
        apt = self._get_selected_apartment()
        if not apt:
            return

        locations = get_all_locations()
        location_names = [loc["city"] for loc in locations] if locations else ["Bristol", "Cardiff", "London", "Manchester"]

        fields = [
            {"key": "apartment_number", "label": "Apartment Number", "type": "text",
             "value": str(apt.get("apartment_number", ""))},
            {"key": "location", "label": "Location", "type": "combo",
             "options": location_names,
             "value": apt.get("location", "")},
            {"key": "type", "label": "Type", "type": "combo",
             "options": ["Studio", "1-Bed", "2-Bed", "3-Bed", "Penthouse"],
             "value": apt.get("type", "")},
            {"key": "monthly_rent", "label": "Monthly Rent (£)", "type": "double",
             "value": float(apt.get("monthly_rent", 0))},
            {"key": "number_of_rooms", "label": "Number of Rooms", "type": "int",
             "value": int(apt.get("number_of_rooms", 0))},
            {"key": "square_footage", "label": "Square Footage", "type": "text",
             "value": str(apt.get("square_footage", ""))},
            {"key": "occupation_status", "label": "Status", "type": "combo",
             "options": ["Available", "Occupied", "Under Maintenance"],
             "value": apt.get("occupation_status", "Available")},
        ]
        dlg = PAMSFormDialog(
            f"Update Registration — {apt.get('apartment_number', '')}", fields, self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            success = update_apartment(
                apartment_id=apt["apartment_id"],
                apartment_number=values["apartment_number"],
                location_city=values["location"],
                apt_type=values["type"],
                monthly_rent=values["monthly_rent"],
                number_of_rooms=values["number_of_rooms"],
                square_footage=values["square_footage"],
                occupation_status=values["occupation_status"],
            )
            if success:
                self.viewApartments()
                show_success(self, f"Apartment '{values['apartment_number']}' registration updated.")
            else:
                show_error(self, "Failed to update apartment. Check that the location exists.")

    # Administrator.assignApartmentToTenant()

    def assignApartmentToTenant(self):
        """Assign a tenant to the selected apartment."""
        apt = self._get_selected_apartment()
        if not apt:
            return

        if apt.get("occupation_status") != "Available":
            show_error(self, "Only available apartments can be assigned to a tenant.")
            return

        tenants = get_all_tenants()
        tenant_names = [f"{t['fname']} {t['lname']} (ID: {t['user_id']})" for t in tenants]

        if not tenant_names:
            show_error(self, "No tenants found in the system.")
            return

        fields = [
            {"key": "apartment", "label": "Apartment", "type": "readonly",
             "value": str(apt.get("apartment_number", ""))},
            {"key": "tenant", "label": "Tenant", "type": "combo",
             "options": tenant_names, "value": tenant_names[0]},
            {"key": "startDate", "label": "Lease Start Date", "type": "date", "value": ""},
            {"key": "endDate", "label": "Lease End Date", "type": "date", "value": ""},
            {"key": "monthly_rent", "label": "Monthly Rent (£)", "type": "double",
             "value": float(apt.get("monthly_rent", 0))},
            {"key": "deposit", "label": "Deposit Amount (£)", "type": "double",
             "value": float(apt.get("monthly_rent", 0))},
            {"key": "term_months", "label": "Lease Term (months)", "type": "int",
             "value": 12},
        ]
        dlg = PAMSFormDialog(
            f"Assign Tenant — {apt.get('apartment_number', '')}", fields, self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            # Extract tenant_id from the combo selection "Name (ID: X)"
            selected = values["tenant"]
            try:
                tenant_id = int(selected.split("ID: ")[1].rstrip(")"))
            except (IndexError, ValueError):
                show_error(self, "Could not determine tenant ID.")
                return

            success = create_lease(
                tenant_id=tenant_id,
                apartment_id=apt["apartment_id"],
                start_date=values["startDate"],
                end_date=values["endDate"],
                monthly_rent=values["monthly_rent"],
                deposit=values["deposit"],
                term_months=values["term_months"],
            )
            if success:
                self.viewApartments()
                show_success(self,
                    f"Tenant assigned to apartment {apt.get('apartment_number', '')} successfully.\n"
                    f"Lease: {values['startDate']} → {values['endDate']}")
            else:
                show_error(self, "Failed to create lease assignment.")

    # Apartment class methods

    def _updateRent(self):
        """Apartment.updateRent(newRent) — update monthly rent."""
        apt = self._get_selected_apartment()
        if not apt:
            return
        fields = [
            {"key": "apartment", "label": "Apartment", "type": "readonly",
             "value": str(apt.get("apartment_number", ""))},
            {"key": "currentRent", "label": "Current Rent", "type": "readonly",
             "value": f"£{float(apt.get('monthly_rent', 0)):.2f}"},
            {"key": "newRent", "label": "New Monthly Rent (£)", "type": "double",
             "value": float(apt.get("monthly_rent", 0))},
        ]
        dlg = PAMSFormDialog("Update Rent", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if update_apartment_rent(apt["apartment_id"], values["newRent"]):
                self.viewApartments()
                show_success(self, f"Rent for apartment {apt.get('apartment_number', '')} "
                             f"updated to £{values['newRent']:.2f}")
            else:
                show_error(self, "Failed to update rent.")

    def _markUnderMaintenance(self):
        """Apartment.markUnderMaintenance()"""
        apt = self._get_selected_apartment()
        if not apt:
            return
        if confirm_action(self, "Mark Under Maintenance",
                          f"Mark apartment {apt.get('apartment_number', '')} as under maintenance?"):
            if update_apartment_status(apt["apartment_id"], "Under Maintenance"):
                self.viewApartments()
                show_success(self, f"Apartment {apt.get('apartment_number', '')} marked as under maintenance.")
            else:
                show_error(self, "Failed to update apartment status.")

    def _markAvailable(self):
        """Apartment.markAvailable()"""
        apt = self._get_selected_apartment()
        if not apt:
            return
        if confirm_action(self, "Mark Available",
                          f"Mark apartment {apt.get('apartment_number', '')} as available?"):
            if update_apartment_status(apt["apartment_id"], "Available"):
                self.viewApartments()
                show_success(self, f"Apartment {apt.get('apartment_number', '')} marked as available.")
            else:
                show_error(self, "Failed to update apartment status.")

    def getOccupancyStatus(self, apt: dict) -> str:
        """Apartment.getOccupancyStatus()"""
        return apt.get("occupation_status", "Unknown")

    def calculateTotalRent(self, apt: dict, months: int) -> float:
        """Apartment.calculateTotalRent(months)"""
        return float(apt.get("monthly_rent", 0)) * months

    def _get_selected_apartment(self):
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select an apartment.")
            return None
        apt_id = int(self._table.item(row, 0).text())
        apartments = get_all_apartments()
        return next((a for a in apartments if a["apartment_id"] == apt_id), None)


#  TENANT MANAGEMENT PANEL (Admin's view of tenants)

class TenantManagementPanel(BasePanel):
    """
    Administrator → Tenants
    View all tenants with their lease status and details.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Tenant Management",
            "View all tenants, their lease status and contact details"
        )
        self._main_layout.addWidget(header)

        toolbar = QHBoxLayout()
        self._btn_view = make_outline_button("View Tenant Details", T.ACCENT)
        self._btn_view.clicked.connect(self._view_tenant)
        toolbar.addWidget(self._btn_view)
        toolbar.addStretch()
        self._main_layout.addLayout(toolbar)

        self._table = PAMSTableWidget([
            "ID", "Name", "Email", "Phone", "Apartment", "Lease Status"
        ])
        self._main_layout.addWidget(self._table)
        self._load_tenants()

    def _load_tenants(self):
        tenants = get_all_tenants()
        rows = []
        for t in tenants:
            rows.append([
                str(t["user_id"]),
                f"{t.get('fname', '')} {t.get('lname', '')}",
                t.get("email", ""),
                t.get("phone_number", "") or "—",
                str(t.get("apartment_number", "")) if t.get("apartment_number") else "—",
                t.get("lease_status", "") or "No Lease",
            ])
        self._table.populate(rows)

    def _view_tenant(self):
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a tenant.")
            return
        tid = int(self._table.item(row, 0).text())

        user = get_user_by_id(tid)
        if not user:
            show_error(self, "Could not load tenant details.")
            return

        leases = get_leases_for_user(tid)

        details = [
            ("Name", f"{user.get('fname', '')} {user.get('lname', '')}"),
            ("Email", user.get("email", "")),
            ("Phone", user.get("phone_number", "") or "—"),
            ("Date of Birth", user.get("date_of_birth", "") or "—"),
            ("Occupation", user.get("occupation", "") or "—"),
            ("NI Number", user.get("ni_number", "") or "—"),
            ("References", user.get("references", "") or "—"),
        ]
        if leases:
            details.append(("", "─── Lease Information ───"))
            for l in leases:
                details.append(("Apartment", str(l.get("apartment_number", "—"))))
                details.append(("Lease Period",
                    f"{l.get('start_date', '—')} → {l.get('end_date', '—')}"))
                details.append(("Monthly Rent", f"£{float(l.get('monthly_rent', 0)):.2f}"))
                details.append(("Status", l.get("status", "—")))
                details.append(("", "─" * 40))

        dlg = PAMSDetailDialog(f"Tenant — {user['fname']} {user['lname']}", details, self)
        dlg.exec()


#  LEASE TRACKING PANEL

class LeaseTrackingPanel(BasePanel):
    """
    Administrator → Lease Tracking
    Methods: trackLeaseAgreements, viewLeaseRequest, submitLeaseRequest,
             updateRequestStatus, calculateRemainingDuration,
             calculateTerminationPenalty, renewLease, processEarlyTermination,
             generateEndDateNotification
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Lease Tracking",
            "Track all lease agreements, requests, renewals and terminations"
        )
        self._main_layout.addWidget(header)

        toolbar = QHBoxLayout()
        self._btn_view = make_outline_button("View Lease Details", T.ACCENT)
        self._btn_renew = make_action_button("Renew Lease", T.SUCCESS)
        self._btn_terminate = make_action_button("Process Early Termination", T.DANGER)
        self._btn_notify = make_outline_button("Send End-Date Notification", T.WARNING)
        self._btn_update_status = make_outline_button("Update Request Status", T.INFO)

        self._btn_view.clicked.connect(self.viewLeaseRequest)
        self._btn_renew.clicked.connect(self.renewLease)
        self._btn_terminate.clicked.connect(self.processEarlyTermination)
        self._btn_notify.clicked.connect(self._sendEndDateNotification)
        self._btn_update_status.clicked.connect(self._updateRequestStatus)

        toolbar.addWidget(self._btn_view)
        toolbar.addWidget(self._btn_renew)
        toolbar.addWidget(self._btn_terminate)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_notify)
        toolbar.addWidget(self._btn_update_status)
        self._main_layout.addLayout(toolbar)

        self._table = PAMSTableWidget([
            "Lease ID", "Tenant", "Apartment", "Start", "End",
            "Rent/mo", "Term (months)", "Status", "Remaining Days"
        ])
        self._main_layout.addWidget(self._table)

        self.trackLeaseAgreements()

    # Administrator.trackLeaseAgreements()

    def trackLeaseAgreements(self):
        """Display all leases from the database with remaining duration."""
        leases = get_all_leases()
        rows = []
        for l in leases:
            remaining = self.calculateRemainingDuration(l)
            rows.append([
                str(l["leaseID"]),
                l.get("tenant_name", "—"),
                str(l.get("apartment_number", "—")),
                l.get("start_date", "—"),
                l.get("end_date", "—"),
                f"£{float(l.get('monthly_rent', 0)):.2f}",
                str(l.get("lease_term_months", "—")),
                l.get("status", "—"),
                f"{remaining} days",
            ])
        self._table.populate(rows)

    # LeaseAgreement.viewLeaseRequest()

    def viewLeaseRequest(self):
        """View full details of the selected lease."""
        lease = self._get_selected_lease()
        if not lease:
            return

        remaining = self.calculateRemainingDuration(lease)
        penalty = self.calculateTerminationPenalty(lease)

        details = [
            ("Lease ID", str(lease["leaseID"])),
            ("Tenant", lease.get("tenant_name", "—")),
            ("Apartment", str(lease.get("apartment_number", "—"))),
            ("Start Date", lease.get("start_date", "—")),
            ("End Date", lease.get("end_date", "—")),
            ("Deposit", f"£{float(lease.get('deposit_amount', 0)):.2f}"),
            ("Monthly Rent", f"£{float(lease.get('monthly_rent', 0)):.2f}"),
            ("Lease Term", f"{lease.get('lease_term_months', '—')} months"),
            ("Status", lease.get("status", "—")),
            ("Remaining Duration", f"{remaining} days"),
            ("Early Termination Notice",
             f"{lease.get('early_termination_notice', 30)} days"),
            ("Termination Penalty",
             f"£{penalty:.2f} ({lease.get('termination_penalty_percent', 5)}%)"),
        ]
        dlg = PAMSDetailDialog(f"Lease — {lease.get('tenant_name', '')}", details, self)
        dlg.exec()

    # LeaseAgreement.renewLease()

    def renewLease(self):
        """Renew the selected lease agreement."""
        lease = self._get_selected_lease()
        if not lease:
            return

        fields = [
            {"key": "tenant", "label": "Tenant", "type": "readonly",
             "value": lease.get("tenant_name", "")},
            {"key": "apartment", "label": "Apartment", "type": "readonly",
             "value": str(lease.get("apartment_number", ""))},
            {"key": "newStart", "label": "New Start Date", "type": "date",
             "value": lease.get("end_date", "")},
            {"key": "newEnd", "label": "New End Date", "type": "date", "value": ""},
            {"key": "newRent", "label": "New Monthly Rent (£)", "type": "double",
             "value": float(lease.get("monthly_rent", 0))},
            {"key": "newTerm", "label": "New Term (months)", "type": "int", "value": 12},
        ]
        dlg = PAMSFormDialog(f"Renew Lease — {lease.get('tenant_name', '')}", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            success = update_lease(
                lease_id=lease["leaseID"],
                start_date=values["newStart"],
                end_date=values["newEnd"],
                monthly_rent=values["newRent"],
                term_months=values["newTerm"],
                status="ACTIVE",
            )
            if success:
                self.trackLeaseAgreements()
                show_success(self, f"Lease for {lease.get('tenant_name', '')} renewed successfully.")
            else:
                show_error(self, "Failed to renew lease.")

    # LeaseAgreement.processEarlyTermination()

    def processEarlyTermination(self):
        """Process early termination for the selected lease."""
        lease = self._get_selected_lease()
        if not lease:
            return

        penalty = self.calculateTerminationPenalty(lease)

        if confirm_action(self, "Early Termination",
                f"Process early termination for {lease.get('tenant_name', '')}?\n\n"
                f"Termination penalty: £{penalty:.2f} (5% of monthly rent)\n"
                f"Required notice period: {lease.get('early_termination_notice', 30)} days (1 month)"):
            if terminate_lease(lease["leaseID"]):
                self.trackLeaseAgreements()
                show_success(self, f"Lease terminated. Penalty of £{penalty:.2f} applies.")
            else:
                show_error(self, "Failed to terminate lease.")

    # LeaseAgreement.calculateTerminationPenalty()

    def calculateTerminationPenalty(self, lease: dict) -> float:
        """Calculate the early termination penalty.
        Brief: 5% of monthly rent as a one-off penalty."""
        rent = float(lease.get("monthly_rent", 0))
        pct = float(lease.get("termination_penalty_percent", 5))
        return rent * (pct / 100)

    # LeaseAgreement.calculateRemainingDuration()

    def calculateRemainingDuration(self, lease: dict) -> int:
        """Calculate days remaining on the lease."""
        end_str = lease.get("end_date", "")
        if not end_str:
            return 0
        end = QDate.fromString(str(end_str), "yyyy-MM-dd")
        today = QDate.currentDate()
        return today.daysTo(end)

    # LeaseAgreement.generateEndDateNotification()

    def _sendEndDateNotification(self):
        """Generate and send end-date notification for tenant (persisted to DB)."""
        lease = self._get_selected_lease()
        if not lease:
            return
        remaining = self.calculateRemainingDuration(lease)
        tenant_id = lease.get("tenantID")
        msg = (f"Your lease for apartment {lease.get('apartment_number', '')} "
               f"ends on {lease.get('end_date', '')} "
               f"({remaining} days remaining). Please contact us to discuss renewal.")
        if tenant_id and _create_notification:
            try:
                _create_notification(tenant_id, msg, "Lease")
            except Exception as e:
                print(f"[admin_panel] end-date notification failed: {e}")
        show_success(self,
            f"Notification sent to {lease.get('tenant_name', '')}:\n'{msg}'")

    # LeaseAgreement.updateRequestStatus()

    def _updateRequestStatus(self):
        """Update the status of the selected lease request."""
        lease = self._get_selected_lease()
        if not lease:
            return
        fields = [
            {"key": "lease", "label": "Lease", "type": "readonly",
             "value": f"#{lease['leaseID']} — {lease.get('tenant_name', '')}"},
            {"key": "status", "label": "New Status", "type": "combo",
             "options": ["ACTIVE", "PENDING", "TERMINATED", "EXPIRED"],
             "value": lease.get("status", "ACTIVE")},
        ]
        dlg = PAMSFormDialog("Update Lease Status", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_status = dlg.get_values()["status"]
            if update_lease_status(lease["leaseID"], new_status):
                self.trackLeaseAgreements()
                show_success(self, f"Lease #{lease['leaseID']} status updated to '{new_status}'.")
            else:
                show_error(self, "Failed to update lease status.")

    def _get_selected_lease(self):
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a lease.")
            return None
        lid = int(self._table.item(row, 0).text())
        leases = get_all_leases()
        return next((l for l in leases if l["leaseID"] == lid), None)


#  REPORTS PANEL (Admin & Manager)

class ReportsPanel(BasePanel):
    """
    Administrator → Reports / Manager → Reports
    Methods: generateReportForLocation, generateLocationReport,
             generateReport, exportToPDF, exportToCSV,
             sendReport, formatReportData

    Supports: OccupancyReport, FinancialReport, MaintenanceReport
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Reports",
            "Generate occupancy, financial and maintenance reports by location"
        )
        self._main_layout.addWidget(header)

        # Controls
        controls = QHBoxLayout()

        lbl_type = QLabel("Report Type:")
        lbl_type.setStyleSheet(f"color: {T.ACCENT}; font-weight: 600; font-size: 13px;")
        self._combo_type = QComboBox()
        self._combo_type.addItems(["Occupancy Report", "Financial Report", "Maintenance Report"])
        self._combo_type.setFixedHeight(36)
        self._combo_type.setStyleSheet(f"""
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

        lbl_loc = QLabel("Location:")
        lbl_loc.setStyleSheet(f"color: {T.ACCENT}; font-weight: 600; font-size: 13px;")
        self._combo_loc = QComboBox()
        self._combo_loc.addItem("All Locations")
        locations = get_all_locations()
        for loc in locations:
            self._combo_loc.addItem(loc["city"])
        self._combo_loc.setFixedHeight(36)
        self._combo_loc.setStyleSheet(self._combo_type.styleSheet())

        self._btn_generate = make_action_button("Generate Report", T.ACCENT)
        self._btn_pdf = make_outline_button("Export PDF", T.INFO)
        self._btn_csv = make_outline_button("Export CSV", T.SUCCESS)
        self._btn_send = make_outline_button("Send Report", T.WARNING)

        self._btn_generate.clicked.connect(self.generateReport)
        self._btn_pdf.clicked.connect(self.exportToPDF)
        self._btn_csv.clicked.connect(self.exportToCSV)
        self._btn_send.clicked.connect(self._sendReport)

        controls.addWidget(lbl_type)
        controls.addWidget(self._combo_type)
        controls.addSpacing(16)
        controls.addWidget(lbl_loc)
        controls.addWidget(self._combo_loc)
        controls.addSpacing(16)
        controls.addWidget(self._btn_generate)
        controls.addStretch()
        controls.addWidget(self._btn_pdf)
        controls.addWidget(self._btn_csv)
        controls.addWidget(self._btn_send)
        self._main_layout.addLayout(controls)

        # Report output area
        self._report_area = QLabel("Select a report type and location, then click 'Generate Report'.")
        self._report_area.setStyleSheet(f"""
            QLabel {{
                background-color: {T.BG_WHITE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: 10px;
                padding: 24px;
                font-size: 13px;
                color: {T.TEXT_DARK};
            }}
        """)
        self._report_area.setWordWrap(True)
        self._report_area.setMinimumHeight(400)
        self._report_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self._report_area)

    # Report.generateReport()

    def generateReport(self):
        """Generate a report based on selected type and location."""
        report_type = self._combo_type.currentText()
        location = self._combo_loc.currentText()

        if report_type == "Occupancy Report":
            content = self._generateOccupancyReport(location)
        elif report_type == "Financial Report":
            content = self._generateFinancialReport(location)
        else:
            content = self._generateMaintenanceReport(location)

        self._report_area.setText(content)

    def _generateOccupancyReport(self, location: str) -> str:
        """OccupancyReport fields: totalApartments, occupiedCount, vacantCount,
        occupancyRate, apartmentDetails"""
        apts = get_all_apartments()
        if location != "All Locations":
            apts = [a for a in apts if a.get("location") == location]

        total = len(apts)
        occupied = sum(1 for a in apts if a.get("occupation_status") == "Occupied")
        vacant = sum(1 for a in apts if a.get("occupation_status") == "Available")
        maintenance = sum(1 for a in apts if a.get("occupation_status") == "Under Maintenance")
        rate = (occupied / total * 100) if total > 0 else 0

        lines = [
            f"Occupancy Report - {location}",
            f"Generated: {QDate.currentDate().toString('dd/MM/yyyy')}",
            "",
            f"Total Apartments:       {total}",
            f"Occupied:               {occupied}",
            f"Vacant:                 {vacant}",
            f"Under Maintenance:      {maintenance}",
            f"Occupancy Rate:         {rate:.1f}%",
            "",
            "─── Apartment Details ───",
        ]
        for a in apts:
            lines.append(f"  {str(a.get('apartment_number', '')):10s}  "
                         f"{a.get('type', ''):10s}  "
                         f"£{float(a.get('monthly_rent', 0)):>8.2f}/mo  "
                         f"[{a.get('occupation_status', '')}]")
        return "\n".join(lines)

    def _generateFinancialReport(self, location: str) -> str:
        """FinancialReport fields: totalRentCollected, pendingRent,
        latePayments, totalLateFees, maintenanceCosts, netRevenue"""
        invoices = get_all_invoices()
        maintenance = get_all_maintenance_requests()

        paid = sum(float(i.get("amount", 0)) for i in invoices if i.get("status") == "Paid")
        pending = sum(float(i.get("amount", 0)) for i in invoices if i.get("status") == "Pending")
        overdue = [i for i in invoices if i.get("status") == "Overdue"]
        overdue_total = sum(float(i.get("amount", 0)) for i in overdue)
        late_fees = len(overdue) * 50.0  # £50 late fee per overdue
        maint_costs = sum(float(r.get("cost", 0) or 0) for r in maintenance)
        net = paid - maint_costs

        lines = [
            f"Financial Report - {location}",
            f"Generated: {QDate.currentDate().toString('dd/MM/yyyy')}",
            "",
            f"Total Rent Collected:   £{paid:,.2f}",
            f"Pending Rent:           £{pending:,.2f}",
            f"Overdue Amount:         £{overdue_total:,.2f}",
            f"Late Payments:          {len(overdue)} invoices",
            f"Total Late Fees:        £{late_fees:,.2f}",
            f"Maintenance Costs:      £{maint_costs:,.2f}",
            f"Net Revenue:            £{net:,.2f}",
        ]
        return "\n".join(lines)

    def _generateMaintenanceReport(self, location: str) -> str:
        """MaintenanceReport fields: totalRequests, completedRequests,
        pendingRequests, averageResolutionTime, totalCosts"""
        reqs = get_all_maintenance_requests()
        total = len(reqs)
        completed = sum(1 for r in reqs if r.get("status") == "Resolved")
        pending = sum(1 for r in reqs if r.get("status") in ("Open", "In Progress"))
        total_costs = sum(float(r.get("cost", 0) or 0) for r in reqs)

        lines = [
            f"Maintenance Report - {location}",
            f"Generated: {QDate.currentDate().toString('dd/MM/yyyy')}",
            "",
            f"Total Requests:         {total}",
            f"Completed:              {completed}",
            f"Pending / In Progress:  {pending}",
            f"Total Costs:            £{total_costs:,.2f}",
            "",
            "─── Request Details ───",
        ]
        for r in reqs:
            lines.append(f"  REQ-{r.get('request_id', 0):03d}  "
                         f"[{str(r.get('status', '')):12s}]  "
                         f"[{str(r.get('priority', '')):6s}]  "
                         f"{str(r.get('description', ''))[:50]}")
        return "\n".join(lines)

    # Report.formatReportData()

    def formatReportData(self) -> str:
        return self._report_area.text()

    # Report.exportToPDF()

    def exportToPDF(self):
        content = self._report_area.text()
        if not content or "Select a report" in content:
            show_error(self, "Generate a report first before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Report — PDF",
            f"PAMS_Report_{_dt.now().strftime('%Y%m%d_%H%M%S')}.pdf",
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
            story = [Paragraph("PAMS — Report", styles["Title"]), Spacer(1, 0.5*cm)]
            for line in content.splitlines():
                story.append(Paragraph(line.replace(" ", "\u00a0") or "\u00a0", styles["Code"]))
            doc.build(story)
            show_success(self, f"Report exported to PDF.\n{path}")
        except Exception as e:
            show_error(self, f"PDF export failed: {e}")

    # Report.exportToCSV()

    def exportToCSV(self):
        content = self._report_area.text()
        if not content or "Select a report" in content:
            show_error(self, "Generate a report first before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Report — CSV",
            f"PAMS_Report_{_dt.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = _csv.writer(f)
                writer.writerow(["PAMS Report", _dt.now().strftime("%d/%m/%Y %H:%M")])
                writer.writerow([])
                for line in content.splitlines():
                    writer.writerow([line])
            show_success(self, f"Report exported to CSV.\n{path}")
        except Exception as e:
            show_error(self, f"CSV export failed: {e}")

    # Report.sendReport()

    def _sendReport(self):
        content = self._report_area.text()
        if not content or "Select a report" in content:
            show_error(self, "Generate a report first before sending.")
            return
        fields = [
            {"key": "email", "label": "Recipient Email", "type": "text",
             "value": "", "placeholder": "e.g. manager@paragon.co.uk"},
        ]
        dlg = PAMSFormDialog("Send Report via Email", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            email = dlg.get_values()["email"]
            show_success(self, f"Report sent to {email} successfully.")


#  SETTINGS PANEL

class SettingsPanel(BasePanel):
    """Administrator → Settings — system and account settings."""

    def __init__(self, user_id: int = 0, parent=None):
        super().__init__(parent)
        self._user_id = user_id
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Settings",
            "System configuration and administrator preferences"
        )
        self._main_layout.addWidget(header)

        # Change password card
        card = SectionCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        lbl = QLabel("Change Password")
        lbl.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 16px; font-weight: 600;")
        card_layout.addWidget(lbl)

        form = QHBoxLayout()
        self._old_pw = QLineEdit()
        self._old_pw.setPlaceholderText("Current Password")
        self._old_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._old_pw.setFixedHeight(36)
        self._new_pw = QLineEdit()
        self._new_pw.setPlaceholderText("New Password")
        self._new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_pw.setFixedHeight(36)
        self._confirm_pw = QLineEdit()
        self._confirm_pw.setPlaceholderText("Confirm New Password")
        self._confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_pw.setFixedHeight(36)

        input_style = f"""
            QLineEdit {{
                background: {T.BG_WHITE}; border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px; padding: 0 12px; font-size: 13px; color: {T.TEXT_DARK};
            }}
            QLineEdit:focus {{ border: 1.5px solid {T.ACCENT}; }}
        """
        self._old_pw.setStyleSheet(input_style)
        self._new_pw.setStyleSheet(input_style)
        self._confirm_pw.setStyleSheet(input_style)

        form.addWidget(self._old_pw)
        form.addWidget(self._new_pw)
        form.addWidget(self._confirm_pw)
        card_layout.addLayout(form)

        btn_change = make_action_button("Change Password", T.ACCENT)
        btn_change.clicked.connect(self._changePassword)
        card_layout.addWidget(btn_change, alignment=Qt.AlignmentFlag.AlignLeft)

        self._main_layout.addWidget(card)

        # System info card
        info_card = SectionCard()
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setSpacing(8)

        lbl2 = QLabel("System Information")
        lbl2.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 16px; font-weight: 600;")
        info_layout.addWidget(lbl2)

        user_count = get_user_count()
        apt_count = get_apartment_count()
        locations = get_all_locations()
        loc_names = ", ".join(loc["city"] for loc in locations) if locations else "—"

        info_items = [
            ("Application", "PAMS — Paragon Apartment Management System"),
            ("Version", "1.0.0"),
            ("Database", "MySQL (Connected)"),
            ("Locations", loc_names),
            ("Total Users", str(user_count)),
            ("Total Apartments", str(apt_count)),
        ]
        for k, v in info_items:
            row = QHBoxLayout()
            lk = QLabel(k)
            lk.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 12px; font-weight: 600;")
            lk.setFixedWidth(150)
            lv = QLabel(v)
            lv.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 13px;")
            row.addWidget(lk)
            row.addWidget(lv, 1)
            info_layout.addLayout(row)

        self._main_layout.addWidget(info_card)
        self._main_layout.addStretch()

    def _changePassword(self):
        """User.changePassword(oldPassword, newPassword)"""
        old = self._old_pw.text().strip()
        new = self._new_pw.text().strip()
        confirm = self._confirm_pw.text().strip()

        if not old or not new:
            show_error(self, "Please fill in all password fields.")
            return
        if new != confirm:
            show_error(self, "New password and confirmation do not match.")
            return
        if len(new) < 6:
            show_error(self, "Password must be at least 6 characters.")
            return

        # Use the logged-in user's actual ID from the session.
        if change_password(self._user_id, old, new):
            show_success(self, "Password changed successfully.")
            self._old_pw.clear()
            self._new_pw.clear()
            self._confirm_pw.clear()
        else:
            show_error(self, "Current password is incorrect or password change failed.")


#  MANAGER-SPECIFIC PANELS

class OccupancyOverviewPanel(BasePanel):
    """Manager → Occupancy: monitorOccupancy()"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme
        header = make_panel_header(
            "Occupancy Overview",
            "Monitor apartment occupancy status across all locations"
        )
        self._main_layout.addWidget(header)

        # Summary cards
        cards = QHBoxLayout()
        cards.setSpacing(16)
        apts = get_all_apartments()
        total = len(apts)
        occupied = sum(1 for a in apts if a.get("occupation_status") == "Occupied")
        vacant = sum(1 for a in apts if a.get("occupation_status") == "Available")
        maint = sum(1 for a in apts if a.get("occupation_status") == "Under Maintenance")

        for title, val, color in [
            ("Total", str(total), T.INFO),
            ("Occupied", str(occupied), T.SUCCESS),
            ("Vacant", str(vacant), T.WARNING),
            ("Maintenance", str(maint), T.DANGER),
        ]:
            card = SectionCard()
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 16, 20, 16)
            lbl_t = QLabel(title)
            lbl_t.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 11px; font-weight: 600;")
            lbl_v = QLabel(val)
            lbl_v.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 700;")
            cl.addWidget(lbl_t)
            cl.addWidget(lbl_v)
            cards.addWidget(card)
        self._main_layout.addLayout(cards)

        # Table by location
        self._table = PAMSTableWidget([
            "Number", "Location", "Type", "Rent", "Status"
        ])
        rows = [[str(a.get("apartment_number", "")),
                 a.get("location", "—"),
                 a.get("type", ""),
                 f"£{float(a.get('monthly_rent', 0)):.2f}",
                 a.get("occupation_status", "")]
                for a in apts]
        self._table.populate(rows)
        self._main_layout.addWidget(self._table)


class LocationManagementPanel(BasePanel):
    """Manager → Locations: view and manage locations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme
        header = make_panel_header("Location Management", "View and manage all business locations")
        self._main_layout.addWidget(header)

        self._table = PAMSTableWidget(["ID", "City", "Manager"])
        locations = get_all_locations()
        rows = [[str(l["location_id"]), l["city"], l.get("manager", "—") or "—"]
                for l in locations]
        self._table.populate(rows)
        self._main_layout.addWidget(self._table)


class ExpandBusinessPanel(BasePanel):
    """
    Manager → Expand Business
    Methods: expandBusinessToOtherCities, addNewCities (use-case)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme
        header = make_panel_header(
            "Expand Business",
            "Add new cities and locations to expand the Paragon portfolio"
        )
        self._main_layout.addWidget(header)

        # Current locations
        lbl = QLabel("Current Locations")
        lbl.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        self._main_layout.addWidget(lbl)

        self._table = PAMSTableWidget(["ID", "City", "Manager"])
        self._refresh_table()
        self._main_layout.addWidget(self._table)

        # Add new city
        add_lbl = QLabel("Add New City")
        add_lbl.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        self._main_layout.addWidget(add_lbl)

        btn_add = make_action_button("+ Add New City / Location", T.ACCENT)
        btn_add.clicked.connect(self.expandBusinessToOtherCities)
        self._main_layout.addWidget(btn_add, alignment=Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addStretch()

    def _refresh_table(self):
        locations = get_all_locations()
        rows = [[str(l["location_id"]), l["city"], l.get("manager", "—") or "—"]
                for l in locations]
        self._table.populate(rows)

    def expandBusinessToOtherCities(self):
        """Manager.expandBusinessToOtherCities() — includes addNewCities use-case."""
        fields = [
            {"key": "city", "label": "City Name", "type": "text", "value": ""},
            {"key": "manager", "label": "Assigned Manager", "type": "text", "value": ""},
        ]
        dlg = PAMSFormDialog("Add New City / Location", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values["city"]:
                show_error(self, "City name is required.")
                return
            new_id = add_location(values["city"], values["manager"] or "TBD")
            if new_id:
                self._refresh_table()
                show_success(self, f"New location added: {values['city']}")
            else:
                show_error(self, "Failed to add location.")


class PerformanceReportsPanel(BasePanel):
    """
    Manager → Performance Reports
    Methods: generatePerformanceReport (according to location)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme
        header = make_panel_header(
            "Performance Reports",
            "Generate performance reports according to location"
        )
        self._main_layout.addWidget(header)

        controls = QHBoxLayout()
        lbl_loc = QLabel("Location:")
        lbl_loc.setStyleSheet(f"color: {T.ACCENT}; font-weight: 600; font-size: 13px;")
        self._combo_loc = QComboBox()
        self._combo_loc.addItem("All Locations")
        locations = get_all_locations()
        for loc in locations:
            self._combo_loc.addItem(loc["city"])
        self._combo_loc.setFixedHeight(36)
        self._combo_loc.setStyleSheet(f"""
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

        btn_gen = make_action_button("Generate Performance Report", T.ACCENT)
        btn_gen.clicked.connect(self.generatePerformanceReport)

        controls.addWidget(lbl_loc)
        controls.addWidget(self._combo_loc)
        controls.addSpacing(16)
        controls.addWidget(btn_gen)
        controls.addStretch()
        self._main_layout.addLayout(controls)

        self._output = QLabel("Click 'Generate Performance Report' to view results.")
        self._output.setStyleSheet(f"""
            QLabel {{
                background-color: {T.BG_WHITE}; border: 1px solid {T.BORDER_LIGHT};
                border-radius: 10px; padding: 24px; font-size: 13px; color: {T.TEXT_DARK};
            }}
        """)
        self._output.setWordWrap(True)
        self._output.setMinimumHeight(350)
        self._output.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._main_layout.addWidget(self._output)

    def generatePerformanceReport(self):
        """Manager.generatePerformanceReport() — by location."""
        loc = self._combo_loc.currentText()
        apts = get_all_apartments()
        if loc != "All Locations":
            apts = [a for a in apts if a.get("location") == loc]

        total = len(apts)
        occupied = sum(1 for a in apts if a.get("occupation_status") == "Occupied")
        revenue = sum(float(a.get("monthly_rent", 0)) for a in apts
                      if a.get("occupation_status") == "Occupied")
        occ_rate = (occupied / total * 100) if total else 0

        maint_reqs = get_all_maintenance_requests()
        total_maint = len(maint_reqs)
        resolved = sum(1 for r in maint_reqs if r.get("status") == "Resolved")

        lines = [
            f"Performance Report - {loc}",
            f"Generated: {QDate.currentDate().toString('dd/MM/yyyy')}",
            "",
            "── Occupancy ──",
            f"  Total Apartments:    {total}",
            f"  Occupied:            {occupied}",
            f"  Occupancy Rate:      {occ_rate:.1f}%",
            "",
            "── Revenue ──",
            f"  Monthly Revenue:     £{revenue:,.2f}",
            f"  Annual Projection:   £{revenue * 12:,.2f}",
            "",
            "── Maintenance ──",
            f"  Total Requests:      {total_maint}",
            f"  Resolved:            {resolved}",
            f"  Resolution Rate:     {(resolved / total_maint * 100) if total_maint else 0:.1f}%",
        ]
        self._output.setText("\n".join(lines))


#  STAFF MANAGEMENT PANEL

class StaffManagementPanel(BasePanel):
    """
    Administrator → Staff Members
    View and edit staff_member table (salary, role, start date, location).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Staff Management",
            "View and edit staff member details — salary, role, start date and location"
        )
        self._main_layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_view = make_outline_button("View Details", T.ACCENT)
        self._btn_edit = make_action_button("Edit Staff Member", T.INFO)

        self._btn_view.clicked.connect(self._view_staff)
        self._btn_edit.clicked.connect(self._edit_staff)

        toolbar.addWidget(self._btn_view)
        toolbar.addWidget(self._btn_edit)
        toolbar.addStretch()
        self._main_layout.addLayout(toolbar)

        # Search
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search staff by name, role or location...")
        self._search.setFixedHeight(36)
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {T.BG_WHITE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
                color: {T.TEXT_DARK};
            }}
            QLineEdit:focus {{ border: 1.5px solid {T.ACCENT}; }}
        """)
        self._search.textChanged.connect(self._filter_table)
        search_row.addWidget(self._search)
        self._main_layout.addLayout(search_row)

        # Table
        self._table = PAMSTableWidget([
            "ID", "First Name", "Last Name", "Email", "Role",
            "Salary (£)", "Start Date", "Location"
        ])
        self._main_layout.addWidget(self._table)

        self._load_staff()

    def _load_staff(self):
        """Load all staff members from the database."""
        staff = get_all_staff()
        rows = []
        for s in staff:
            rows.append([
                str(s["employee_id"]),
                s.get("fname", ""),
                s.get("lname", ""),
                s.get("email", ""),
                s.get("staff_role", "") or s.get("user_role", ""),
                f"£{s.get('salary', 0) or 0:,.2f}",
                s.get("start_date", "—") or "—",
                s.get("location", "—") or "—",
            ])
        self._table.populate(rows)

    def _view_staff(self):
        """View full details of the selected staff member."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a staff member.")
            return

        emp_id = int(self._table.item(row, 0).text())
        staff = get_all_staff()
        member = next((s for s in staff if s["employee_id"] == emp_id), None)
        if not member:
            show_error(self, "Could not load staff details.")
            return

        details = [
            ("Employee ID", str(member["employee_id"])),
            ("First Name", member.get("fname", "")),
            ("Last Name", member.get("lname", "")),
            ("Email", member.get("email", "")),
            ("Phone", member.get("phone_number", "") or "—"),
            ("Date of Birth", member.get("date_of_birth", "") or "—"),
            ("", "─── Staff Details ───"),
            ("Staff Role", member.get("staff_role", "") or "—"),
            ("Salary", f"£{member.get('salary', 0) or 0:,.2f}"),
            ("Start Date", member.get("start_date", "") or "—"),
            ("Location", member.get("location", "") or "—"),
        ]
        dlg = PAMSDetailDialog(
            f"Staff — {member['fname']} {member['lname']}", details, self
        )
        dlg.exec()

    def _edit_staff(self):
        """Edit staff member details (salary, role, start date, location)."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a staff member to edit.")
            return

        emp_id = int(self._table.item(row, 0).text())
        staff = get_all_staff()
        member = next((s for s in staff if s["employee_id"] == emp_id), None)
        if not member:
            show_error(self, "Could not load staff details.")
            return

        locations = get_all_locations()
        location_names = [loc["city"] for loc in locations] if locations else ["—"]

        fields = [
            {"key": "name", "label": "Staff Member", "type": "readonly",
             "value": f"{member['fname']} {member['lname']}"},
            {"key": "role", "label": "Staff Role", "type": "combo",
             "options": ["Administrator", "Manager", "Front Desk Staff",
                         "Finance Manager", "Maintenance Staff"],
             "value": member.get("staff_role", "") or member.get("user_role", "")},
            {"key": "salary", "label": "Salary (£)", "type": "double",
             "value": float(member.get("salary", 0) or 0)},
            {"key": "start_date", "label": "Start Date", "type": "date",
             "value": member.get("start_date", "") or ""},
            {"key": "location", "label": "Location", "type": "combo",
             "options": location_names,
             "value": member.get("location", "") or ""},
        ]
        dlg = PAMSFormDialog(
            f"Edit Staff — {member['fname']} {member['lname']}", fields, self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()

            # Resolve location_id from city name
            loc_id = None
            for loc in locations:
                if loc["city"] == values["location"]:
                    loc_id = loc["location_id"]
                    break

            success = update_staff_member(
                employee_id=emp_id,
                salary=values["salary"],
                role=values["role"],
                start_date=values["start_date"],
                location_id=loc_id,
            )
            if success:
                self._load_staff()
                show_success(self, f"Staff member {member['fname']} {member['lname']} updated.")
            else:
                show_error(self, "Failed to update staff member.")

    def _filter_table(self, text: str):
        """Filter the staff table by search text."""
        text = text.lower()
        for row in range(self._table.rowCount()):
            match = False
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self._table.setRowHidden(row, not match)
