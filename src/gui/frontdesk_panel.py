"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Front Desk Staff Panels — Register Tenant, Tenant Info, Maintenance, Complaints

Implements all FrontDeskStaff class methods and use-case operations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QLineEdit, QComboBox, QTextEdit, QFrame
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

from models import (
    get_all_tenants, get_all_apartments, get_all_leases,
    get_all_maintenance_requests, create_maintenance_request,
    get_maintenance_for_tenant, get_leases_for_user, get_user_by_id,
    admin_add_user, does_user_exist,
    get_all_complaints, create_complaint, update_complaint_status,
    get_complaint_by_id, get_all_enquiries, create_enquiry,
)


#  REGISTER TENANT PANEL

class RegisterTenantPanel(BasePanel):
    """
    Front Desk Staff → Register Tenant
    Use-case: Register New Tenant (includes Access Tenant Information)
    Methods: registerNewTenant(tenant) → boolean
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Register New Tenant",
            "Register new tenants into the system (Register New Tenant use-case)"
        )
        self._main_layout.addWidget(header)

        # Registration form card
        form_card = SectionCard()
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 20, 24, 20)
        form_layout.setSpacing(14)

        form_title = QLabel("New Tenant Registration Form")
        form_title.setStyleSheet(f"color: {T.TEXT_DARK}; font-size: 16px; font-weight: 600;")
        form_layout.addWidget(form_title)

        input_style = f"""
            QLineEdit, QComboBox {{
                background-color: {T.BG_WHITE};
                border: 1.5px solid {T.BORDER_LIGHT};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: {T.TEXT_DARK};
                min-height: 22px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1.5px solid {T.ACCENT};
            }}
        """
        label_style = f"color: {T.TEXT_DARK}; font-size: 13px; font-weight: 600;"

        # Row 1: Names
        row1 = QHBoxLayout()
        col1 = QVBoxLayout()
        lbl_fname = QLabel("First Name *")
        lbl_fname.setStyleSheet(label_style)
        self._fname = QLineEdit()
        self._fname.setPlaceholderText("Enter first name")
        self._fname.setStyleSheet(input_style)
        self._fname.setFixedHeight(38)
        col1.addWidget(lbl_fname)
        col1.addWidget(self._fname)

        col2 = QVBoxLayout()
        lbl_lname = QLabel("Last Name *")
        lbl_lname.setStyleSheet(label_style)
        self._lname = QLineEdit()
        self._lname.setPlaceholderText("Enter last name")
        self._lname.setStyleSheet(input_style)
        self._lname.setFixedHeight(38)
        col2.addWidget(lbl_lname)
        col2.addWidget(self._lname)

        row1.addLayout(col1)
        row1.addLayout(col2)
        form_layout.addLayout(row1)

        # Row 2: Email, Phone
        row2 = QHBoxLayout()
        col3 = QVBoxLayout()
        lbl_email = QLabel("Email *")
        lbl_email.setStyleSheet(label_style)
        self._email = QLineEdit()
        self._email.setPlaceholderText("e.g. tenant@email.com")
        self._email.setStyleSheet(input_style)
        self._email.setFixedHeight(38)
        col3.addWidget(lbl_email)
        col3.addWidget(self._email)

        col4 = QVBoxLayout()
        lbl_phone = QLabel("Phone Number *")
        lbl_phone.setStyleSheet(label_style)
        self._phone = QLineEdit()
        self._phone.setPlaceholderText("e.g. 07700123456")
        self._phone.setStyleSheet(input_style)
        self._phone.setFixedHeight(38)
        col4.addWidget(lbl_phone)
        col4.addWidget(self._phone)

        row2.addLayout(col3)
        row2.addLayout(col4)
        form_layout.addLayout(row2)

        # Row 3: DoB, Occupation
        row3 = QHBoxLayout()
        col5 = QVBoxLayout()
        lbl_dob = QLabel("Date of Birth *")
        lbl_dob.setStyleSheet(label_style)
        self._dob = QLineEdit()
        self._dob.setPlaceholderText("YYYY-MM-DD")
        self._dob.setStyleSheet(input_style)
        self._dob.setFixedHeight(38)
        col5.addWidget(lbl_dob)
        col5.addWidget(self._dob)

        col6 = QVBoxLayout()
        lbl_occ = QLabel("Occupation")
        lbl_occ.setStyleSheet(label_style)
        self._occupation = QLineEdit()
        self._occupation.setPlaceholderText("e.g. Software Developer")
        self._occupation.setStyleSheet(input_style)
        self._occupation.setFixedHeight(38)
        col6.addWidget(lbl_occ)
        col6.addWidget(self._occupation)

        row3.addLayout(col5)
        row3.addLayout(col6)
        form_layout.addLayout(row3)

        # Row 4: Address
        row4 = QVBoxLayout()
        lbl_addr = QLabel("Address")
        lbl_addr.setStyleSheet(label_style)
        self._address = QLineEdit()
        self._address.setPlaceholderText("Full address")
        self._address.setStyleSheet(input_style)
        self._address.setFixedHeight(38)
        row4.addWidget(lbl_addr)
        row4.addWidget(self._address)
        form_layout.addLayout(row4)

        # Row 5: NI Number, References
        row5 = QHBoxLayout()
        col7 = QVBoxLayout()
        lbl_ni = QLabel("NI Number")
        lbl_ni.setStyleSheet(label_style)
        self._ni = QLineEdit()
        self._ni.setPlaceholderText("e.g. AB123456C")
        self._ni.setStyleSheet(input_style)
        self._ni.setFixedHeight(38)
        col7.addWidget(lbl_ni)
        col7.addWidget(self._ni)

        col8 = QVBoxLayout()
        lbl_ref = QLabel("References")
        lbl_ref.setStyleSheet(label_style)
        self._references = QLineEdit()
        self._references.setPlaceholderText("Employer or previous landlord")
        self._references.setStyleSheet(input_style)
        self._references.setFixedHeight(38)
        col8.addWidget(lbl_ref)
        col8.addWidget(self._references)

        row5.addLayout(col7)
        row5.addLayout(col8)
        form_layout.addLayout(row5)

        # Row 6: Username, Password
        row6 = QHBoxLayout()
        col9 = QVBoxLayout()
        lbl_user = QLabel("Username *")
        lbl_user.setStyleSheet(label_style)
        self._username = QLineEdit()
        self._username.setPlaceholderText("Choose a username")
        self._username.setStyleSheet(input_style)
        self._username.setFixedHeight(38)
        col9.addWidget(lbl_user)
        col9.addWidget(self._username)

        col10 = QVBoxLayout()
        lbl_pw = QLabel("Password *")
        lbl_pw.setStyleSheet(label_style)
        self._password = QLineEdit()
        self._password.setPlaceholderText("Minimum 6 characters")
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setStyleSheet(input_style)
        self._password.setFixedHeight(38)
        col10.addWidget(lbl_pw)
        col10.addWidget(self._password)

        row6.addLayout(col9)
        row6.addLayout(col10)
        form_layout.addLayout(row6)

        # Submit button
        btn_row = QHBoxLayout()
        self._btn_register = make_action_button("Register Tenant", T.ACCENT)
        self._btn_register.clicked.connect(self.registerNewTenant)
        self._btn_clear = make_outline_button("Clear Form", T.TEXT_BODY)
        self._btn_clear.clicked.connect(self._clear_form)
        btn_row.addWidget(self._btn_register)
        btn_row.addWidget(self._btn_clear)
        btn_row.addStretch()
        form_layout.addLayout(btn_row)

        self._main_layout.addWidget(form_card)

        # Recently registered tenants
        recent_row = QHBoxLayout()
        lbl_recent = QLabel("Recently Registered Tenants")
        lbl_recent.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        recent_row.addWidget(lbl_recent)
        recent_row.addStretch()
        self._btn_refresh = make_outline_button("Refresh", T.SUCCESS)
        self._btn_refresh.clicked.connect(self._refresh_table)
        recent_row.addWidget(self._btn_refresh)
        self._main_layout.addLayout(recent_row)

        self._table = PAMSTableWidget([
            "ID", "Name", "Email", "Phone", "DoB", "Occupation"
        ])
        self._refresh_table()
        self._main_layout.addWidget(self._table)

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _refresh_table(self):
        """Load tenants from the database and populate the table."""
        try:
            tenants = self._filter_by_location(get_all_tenants())
            rows = []
            for t in tenants:
                rows.append([
                    str(t["user_id"]),
                    f"{t['fname']} {t['lname']}",
                    t["email"] or "",
                    t["phone_number"] or "",
                    t["date_of_birth"] or "",
                    t["occupation"] or "",
                ])
            self._table.populate(rows)
        except Exception as e:
            show_error(self, f"Failed to load tenants: {e}")

    # FrontDeskStaff.registerNewTenant(tenant) → boolean

    def registerNewTenant(self) -> bool:
        """Validate and register a new tenant into the database."""
        fname = self._fname.text().strip()
        lname = self._lname.text().strip()
        email = self._email.text().strip()
        phone = self._phone.text().strip()
        dob = self._dob.text().strip()
        username = self._username.text().strip()
        password = self._password.text().strip()

        # Validation
        if not all([fname, lname, email, phone, dob, username, password]):
            show_error(self, "Please fill in all required fields (marked with *).")
            return False

        if len(password) < 6:
            show_error(self, "Password must be at least 6 characters.")
            return False

        # Check duplicate username or email in database
        try:
            if does_user_exist(username, email):
                show_error(self, f"Username '{username}' or email '{email}' already exists.")
                return False
        except Exception as e:
            show_error(self, f"Error checking existing users: {e}")
            return False

        # Create new tenant in DB using admin_add_user with role='Tenant'
        try:
            new_id = admin_add_user(
                fname=fname, lname=lname, email=email, phone=phone,
                dob=dob, role='Tenant', username=username, password=password,
                occupation=self._occupation.text().strip() or None,
                ni_number=self._ni.text().strip() or None,
                references=self._references.text().strip() or None,
            )
            if new_id:
                self._refresh_table()
                self._clear_form()
                show_success(self,
                    f"Tenant '{fname} {lname}' registered successfully!\n"
                    f"Username: {username}  |  ID: {new_id}")
                return True
            else:
                show_error(self, "Failed to register tenant. Please try again.")
                return False
        except Exception as e:
            show_error(self, f"Database error: {e}")
            return False

    def _clear_form(self):
        """Clear all form fields."""
        for field in [self._fname, self._lname, self._email, self._phone,
                      self._dob, self._occupation, self._address,
                      self._ni, self._references, self._username, self._password]:
            field.clear()


#  TENANT INFORMATION PANEL

class TenantInfoPanel(BasePanel):
    """
    Front Desk Staff → Tenant Info
    Use-case: Handle Tenant Enquiries (includes Access Tenant Information)
    Methods: handleTenantEnquiries(enquiryDetails) → void,
             accessTenantInformation(tenantID) → Tenant
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Tenant Information & Enquiries",
            "Search, access and manage tenant information (Handle Tenant Enquiries use-case)"
        )
        self._main_layout.addWidget(header)

        # Search bar
        search_row = QHBoxLayout()
        lbl_search = QLabel("Search Tenant:")
        lbl_search.setStyleSheet(f"color: {T.ACCENT}; font-weight: 600; font-size: 13px;")
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search by name, email, phone or username...")
        self._search.setFixedHeight(38)
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
        self._search.textChanged.connect(self._filter)

        search_row.addWidget(lbl_search)
        search_row.addWidget(self._search, 1)
        self._main_layout.addLayout(search_row)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_access = make_action_button("Access Tenant Info", T.ACCENT)
        self._btn_enquiry = make_action_button("Log Enquiry", T.INFO)

        self._btn_access.clicked.connect(self._accessTenantInformation)
        self._btn_enquiry.clicked.connect(self._handleEnquiry)

        toolbar.addWidget(self._btn_access)
        toolbar.addWidget(self._btn_enquiry)
        toolbar.addStretch()
        self._btn_refresh = make_outline_button("Refresh", T.SUCCESS)
        self._btn_refresh.clicked.connect(self._refresh_all)
        toolbar.addWidget(self._btn_refresh)
        self._main_layout.addLayout(toolbar)

        # Tenant table
        self._table = PAMSTableWidget([
            "ID", "Name", "Email", "Phone", "Apartment", "Lease Status"
        ])
        self._load_tenants()
        self._main_layout.addWidget(self._table)

        # Enquiry log
        lbl_log = QLabel("Recent Enquiry Log")
        lbl_log.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        self._main_layout.addWidget(lbl_log)

        self._enquiry_table = PAMSTableWidget([
            "Date", "Tenant", "Enquiry Details", "Handled By"
        ])
        self._load_enquiries()
        self._main_layout.addWidget(self._enquiry_table)

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _load_tenants(self):
        """Load all tenants from the database with lease info."""
        try:
            tenants = self._filter_by_location(get_all_tenants())
            rows = []
            for t in tenants:
                rows.append([
                    str(t["user_id"]),
                    f"{t['fname']} {t['lname']}",
                    t["email"] or "",
                    t["phone_number"] or "",
                    t["apartment_number"] or "—",
                    t["lease_status"] if t["lease_status"] else "No Lease",
                ])
            self._table.populate(rows)
        except Exception as e:
            show_error(self, f"Failed to load tenants: {e}")

    def _load_enquiries(self):
        """Load all enquiries from the database."""
        try:
            enquiries = get_all_enquiries()
            rows = []
            for eq in enquiries:
                rows.append([
                    eq["date_logged"] or "",
                    eq["tenant_name"] or "",
                    (eq["enquiry_details"] or "")[:80],
                    eq["handled_by"] or "",
                ])
            self._enquiry_table.populate(rows)
        except Exception as e:
            show_error(self, f"Failed to load enquiries: {e}")

    # FrontDeskStaff.accessTenantInformation(tenantID) → Tenant

    def _accessTenantInformation(self):
        """Access full information for the selected tenant from the database."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a tenant.")
            return

        tid = int(self._table.item(row, 0).text())

        try:
            tenant = get_user_by_id(tid)
        except Exception as e:
            show_error(self, f"Error loading tenant: {e}")
            return

        if not tenant:
            show_error(self, "Tenant not found.")
            return

        # Load lease info from DB
        try:
            leases = get_leases_for_user(tid)
        except Exception:
            leases = []

        # Load maintenance info from DB
        try:
            maintenance = get_maintenance_for_tenant(tid)
        except Exception:
            maintenance = []

        details = [
            ("Tenant Info", ""),
            ("User ID", str(tenant["user_id"])),
            ("Username", tenant.get("username", "")),
            ("First Name", tenant.get("fname", "")),
            ("Last Name", tenant.get("lname", "")),
            ("Email", tenant.get("email", "")),
            ("Phone", tenant.get("phone_number", "")),
            ("Date of Birth", tenant.get("date_of_birth", "")),
            ("Occupation", tenant.get("occupation", "") or ""),
            ("NI Number", tenant.get("ni_number", "") or ""),
            ("References", tenant.get("references", "") or ""),
        ]
        if leases:
            details.append(("", "─── Lease Information ───"))
            for lease in leases:
                details += [
                    ("Lease ID", str(lease.get("leaseID", ""))),
                    ("Apartment", lease.get("apartment_number", "")),
                    ("Period", f"{lease.get('start_date', '')} → {lease.get('end_date', '')}"),
                    ("Monthly Rent", f"£{lease.get('monthly_rent', 0):.2f}"),
                    ("Status", lease.get("status", "")),
                ]
        if maintenance:
            details.append(("", "─── Maintenance Requests ───"))
            for m in maintenance:
                details.append((
                    f"REQ-{m['request_id']:03d}",
                    f"{m['description']} [{m['status']}]"
                ))

        dlg = PAMSDetailDialog(
            f"Tenant — {tenant.get('fname', '')} {tenant.get('lname', '')}",
            details, self
        )
        dlg.exec()

    def accessTenantInformation(self, tenantID: int):
        """FrontDeskStaff.accessTenantInformation(tenantID) → Tenant"""
        return get_user_by_id(tenantID)

    # FrontDeskStaff.handleTenantEnquiries(enquiryDetails) → void

    def _handleEnquiry(self):
        """Log a new tenant enquiry to the database."""
        row = self._table.currentRow()
        tenant_name = ""
        tenant_id = None
        if row >= 0:
            tenant_name = self._table.item(row, 1).text()
            tenant_id = int(self._table.item(row, 0).text())

        fields = [
            {"key": "tenant", "label": "Tenant", "type": "text", "value": tenant_name},
            {"key": "details", "label": "Enquiry Details", "type": "textarea", "value": ""},
            {"key": "handledBy", "label": "Handled By", "type": "text",
             "value": "Front Desk Staff"},
        ]
        dlg = PAMSFormDialog("Log Tenant Enquiry", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values["details"].strip():
                show_error(self, "Enquiry details are required.")
                return

            try:
                eid = create_enquiry(
                    tenant_name=values["tenant"],
                    enquiry_details=values["details"],
                    handled_by=values["handledBy"],
                    tenant_id=tenant_id,
                )
                if eid:
                    self._load_enquiries()
                    show_success(self, f"Enquiry logged for {values['tenant']}.")
                else:
                    show_error(self, "Failed to log enquiry.")
            except Exception as e:
                show_error(self, f"Database error: {e}")

    def handleTenantEnquiries(self, enquiryDetails: str):
        """FrontDeskStaff.handleTenantEnquiries(enquiryDetails) → void"""
        pass

    def _refresh_all(self):
        """Reload both tenants and enquiries from the database."""
        self._load_tenants()
        self._load_enquiries()

    def _filter(self, text: str):
        """Filter tenant table by search text."""
        text = text.lower()
        for row in range(self._table.rowCount()):
            match = False
            for col in range(self._table.columnCount()):
                item = self._table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self._table.setRowHidden(row, not match)


#  MAINTENANCE REGISTRATION PANEL (Front Desk)

class MaintenanceRegistrationPanel(BasePanel):
    """
    Front Desk Staff → Maintenance
    Use-case: Register Maintenance Requests & Complaints
              (includes Track Maintenance Requests & Complaints,
               includes Access Tenant Information)
    Methods: registerMaintenanceRequestsAndComplaints() → boolean
    """

    # Map between UI priority labels and database ENUM values
    _PRIORITY_TO_DB = {"Urgent": "Emergency", "High": "High", "Medium": "Medium", "Low": "Low"}
    _PRIORITY_FROM_DB = {"Emergency": "Urgent", "High": "High", "Medium": "Medium", "Low": "Low"}

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Maintenance Requests & Complaints",
            "Register and track maintenance requests on behalf of tenants"
        )
        self._main_layout.addWidget(header)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_register = make_action_button("+ Register New Request", T.ACCENT)
        self._btn_track = make_outline_button("Track Status", T.INFO)

        self._btn_register.clicked.connect(self.registerMaintenanceRequestsAndComplaints)
        self._btn_track.clicked.connect(self._trackRequest)

        toolbar.addWidget(self._btn_register)
        toolbar.addWidget(self._btn_track)
        toolbar.addStretch()
        self._btn_refresh = make_outline_button("Refresh", T.SUCCESS)
        self._btn_refresh.clicked.connect(self._refresh_table)
        toolbar.addWidget(self._btn_refresh)
        self._main_layout.addLayout(toolbar)

        # Requests table (Track Maintenance Requests & Complaints)
        self._table = PAMSTableWidget([
            "ID", "Description", "Category", "Tenant", "Apartment",
            "Status", "Priority", "Reported Date"
        ])
        self._refresh_table()
        self._main_layout.addWidget(self._table)

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _refresh_table(self):
        """Load maintenance requests from the database."""
        try:
            requests = self._filter_by_location(get_all_maintenance_requests())
            rows = []
            for r in requests:
                desc = r.get("description", "")
                # Extract category if stored as "[Category] description"
                category = "General"
                if desc.startswith("[") and "]" in desc:
                    category = desc[1:desc.index("]")]
                    desc = desc[desc.index("]") + 2:]  # text after "] "

                priority = self._PRIORITY_FROM_DB.get(r.get("priority", ""), r.get("priority", ""))

                rows.append([
                    str(r["request_id"]),
                    desc[:40],
                    category,
                    r.get("tenant_name", ""),
                    r.get("apartment_number", ""),
                    r.get("status", ""),
                    priority,
                    r.get("report_date", ""),
                ])
            self._table.populate(rows)
        except Exception as e:
            show_error(self, f"Failed to load maintenance requests: {e}")

    # FrontDeskStaff.registerMaintenanceRequestsAndComplaints()

    def registerMaintenanceRequestsAndComplaints(self) -> bool:
        """Register a new maintenance request on behalf of a tenant.
        Includes: Access Tenant Information."""
        try:
            tenants = get_all_tenants()
            apartments = get_all_apartments()
        except Exception as e:
            show_error(self, f"Failed to load data: {e}")
            return False

        tenant_options = [f"{t['fname']} {t['lname']} (ID: {t['user_id']})" for t in tenants]
        # Build apartment options with apartment_id stored for later lookup
        apt_options = [a["apartment_number"] for a in apartments]
        # Store apartment lookup: apartment_number → apartment_id
        self._apt_lookup = {a["apartment_number"]: a["apartment_id"] for a in apartments}

        if not tenant_options:
            show_error(self, "No tenants found. Please register a tenant first.")
            return False
        if not apt_options:
            show_error(self, "No apartments found in the system.")
            return False

        fields = [
            {"key": "tenant", "label": "Tenant", "type": "combo",
             "options": tenant_options, "value": tenant_options[0]},
            {"key": "apartment", "label": "Apartment", "type": "combo",
             "options": apt_options, "value": apt_options[0]},
            {"key": "category", "label": "Category", "type": "combo",
             "options": ["Plumbing", "Electrical", "Heating", "Security",
                         "Structural", "Appliance", "General", "Other"],
             "value": "General"},
            {"key": "priority", "label": "Priority", "type": "combo",
             "options": ["Urgent", "High", "Medium", "Low"],
             "value": "Medium"},
            {"key": "description", "label": "Description", "type": "textarea",
             "value": ""},
            {"key": "formData", "label": "Detailed Form Data", "type": "textarea",
             "value": ""},
        ]
        dlg = PAMSFormDialog("Register Maintenance Request / Complaint", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values["description"].strip():
                show_error(self, "Description is required.")
                return False

            # Extract tenant_id
            try:
                tenant_id = int(values["tenant"].split("ID: ")[1].rstrip(")"))
            except (IndexError, ValueError):
                show_error(self, "Invalid tenant selection.")
                return False

            # Resolve apartment_id
            apartment_number = values["apartment"]
            apartment_id = self._apt_lookup.get(apartment_number)
            if not apartment_id:
                show_error(self, f"Apartment '{apartment_number}' not found.")
                return False

            # Build description with category prefix: "[Category] description"
            category = values["category"]
            full_desc = f"[{category}] {values['description']}"
            if values.get("formData", "").strip():
                full_desc += f"\n\nForm Data:\n{values['formData']}"

            # Map UI priority to DB enum
            db_priority = self._PRIORITY_TO_DB.get(values["priority"], values["priority"])

            try:
                new_id = create_maintenance_request(
                    apartment_id=apartment_id,
                    tenant_id=tenant_id,
                    description=full_desc,
                    priority=db_priority,
                    category=category,
                )
                if new_id:
                    tenant_name = values["tenant"].split(" (")[0]
                    self._refresh_table()
                    show_success(self,
                        f"Maintenance request #{new_id} registered for {tenant_name}.\n"
                        f"Category: {category}  |  Priority: {values['priority']}")
                    return True
                else:
                    show_error(self, "Failed to create maintenance request.")
                    return False
            except Exception as e:
                show_error(self, f"Database error: {e}")
                return False
        return False

    # Track Maintenance Requests & Complaints

    def _trackRequest(self):
        """View tracking status of the selected request from the database."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a request to track.")
            return

        rid = int(self._table.item(row, 0).text())

        try:
            requests = get_all_maintenance_requests()
            req = next((r for r in requests if r["request_id"] == rid), None)
        except Exception as e:
            show_error(self, f"Error loading request: {e}")
            return

        if not req:
            show_error(self, "Request not found.")
            return

        desc = req.get("description", "")
        category = "General"
        if desc.startswith("[") and "]" in desc:
            category = desc[1:desc.index("]")]
            desc = desc[desc.index("]") + 2:]

        priority = self._PRIORITY_FROM_DB.get(req.get("priority", ""), req.get("priority", ""))

        details = [
            ("Request ID", str(req["request_id"])),
            ("Description", desc),
            ("Category", category),
            ("Status", req.get("status", "")),
            ("Priority", priority),
            ("Tenant", req.get("tenant_name", "")),
            ("Apartment", req.get("apartment_number", "")),
            ("Reported Date", req.get("report_date", "")),
            ("Resolved Date", req.get("resolved_date") or "Not yet resolved"),
            ("Assigned Staff", req.get("staff_name") or "Not yet assigned"),
            ("Cost", f"£{req.get('cost', 0):.2f}" if req.get("cost") else "N/A"),
        ]
        dlg = PAMSDetailDialog(f"Track Request #{req['request_id']}", details, self)
        dlg.exec()


#  COMPLAINTS & FEEDBACK PANEL

class ComplaintsPanel(BasePanel):
    """
    Front Desk Staff → Complaints & Feedback
    Methods: logComplaint() → void
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._build_ui()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Complaints & Feedback",
            "View and log tenant complaints and feedback"
        )
        self._main_layout.addWidget(header)

        # Summary cards - will be populated by _refresh_summary()
        self._summary_layout = QHBoxLayout()
        self._summary_layout.setSpacing(12)
        self._summary_cards = {}
        for title, color in [
            ("Total", T.INFO), ("Open", T.WARNING),
            ("Under Review", T.ACCENT), ("Resolved", T.SUCCESS),
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
        self._btn_log = make_action_button("+ Log New Complaint", T.ACCENT)
        self._btn_view = make_outline_button("View Details", T.INFO)
        self._btn_update = make_outline_button("Update Status", T.WARNING)

        self._btn_log.clicked.connect(self.logComplaint)
        self._btn_view.clicked.connect(self._viewComplaint)
        self._btn_update.clicked.connect(self._updateStatus)

        toolbar.addWidget(self._btn_log)
        toolbar.addWidget(self._btn_view)
        toolbar.addWidget(self._btn_update)
        toolbar.addStretch()
        self._btn_refresh = make_outline_button("Refresh", T.SUCCESS)
        self._btn_refresh.clicked.connect(self._refresh_table)
        toolbar.addWidget(self._btn_refresh)
        self._main_layout.addLayout(toolbar)

        # Complaints table
        self._table = PAMSTableWidget([
            "ID", "Tenant", "Date", "Subject", "Status"
        ])
        self._refresh_table()
        self._main_layout.addWidget(self._table)

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _refresh_table(self):
        """Load complaints from the database and update summary cards."""
        try:
            complaints = self._filter_by_location(get_all_complaints())
            rows = []
            total = len(complaints)
            open_c = 0
            review_c = 0
            resolved_c = 0
            for c in complaints:
                status = c.get("status", "")
                if status == "Open":
                    open_c += 1
                elif status == "Under Review":
                    review_c += 1
                elif status == "Resolved":
                    resolved_c += 1
                rows.append([
                    str(c["complaint_id"]),
                    c.get("tenant_name", ""),
                    c.get("date_filed", ""),
                    c.get("subject", ""),
                    status,
                ])
            self._table.populate(rows)

            # Update summary cards
            self._summary_cards["Total"].setText(str(total))
            self._summary_cards["Open"].setText(str(open_c))
            self._summary_cards["Under Review"].setText(str(review_c))
            self._summary_cards["Resolved"].setText(str(resolved_c))
        except Exception as e:
            show_error(self, f"Failed to load complaints: {e}")

    # FrontDeskStaff.logComplaint() → void

    def logComplaint(self):
        """Log a new complaint or feedback from a tenant."""
        try:
            tenants = get_all_tenants()
        except Exception as e:
            show_error(self, f"Failed to load tenants: {e}")
            return

        tenant_options = [f"{t['fname']} {t['lname']} (ID: {t['user_id']})" for t in tenants]
        if not tenant_options:
            show_error(self, "No tenants found. Please register a tenant first.")
            return

        fields = [
            {"key": "tenant", "label": "Tenant", "type": "combo",
             "options": tenant_options, "value": tenant_options[0]},
            {"key": "subject", "label": "Subject", "type": "text",
             "value": "", "placeholder": "Brief summary of the complaint"},
            {"key": "description", "label": "Full Description", "type": "textarea",
             "value": ""},
        ]
        dlg = PAMSFormDialog("Log New Complaint / Feedback", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if not values["subject"].strip() or not values["description"].strip():
                show_error(self, "Subject and description are required.")
                return

            try:
                tenant_id = int(values["tenant"].split("ID: ")[1].rstrip(")"))
            except (IndexError, ValueError):
                show_error(self, "Invalid tenant selection.")
                return

            try:
                new_id = create_complaint(
                    tenant_id=tenant_id,
                    subject=values["subject"],
                    description=values["description"],
                )
                if new_id:
                    tenant_name = values["tenant"].split(" (")[0]
                    self._refresh_table()
                    show_success(self, f"Complaint #{new_id} logged for {tenant_name}.")
                else:
                    show_error(self, "Failed to log complaint.")
            except Exception as e:
                show_error(self, f"Database error: {e}")

    def _viewComplaint(self):
        """View details of the selected complaint from the database."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a complaint.")
            return

        cid = int(self._table.item(row, 0).text())

        try:
            complaint = get_complaint_by_id(cid)
        except Exception as e:
            show_error(self, f"Error loading complaint: {e}")
            return

        if not complaint:
            show_error(self, "Complaint not found.")
            return

        details = [
            ("Complaint ID", str(complaint["complaint_id"])),
            ("Tenant", complaint.get("tenant_name", "")),
            ("Date", complaint.get("date_filed", "")),
            ("Subject", complaint.get("subject", "")),
            ("Description", complaint.get("description", "")),
            ("Status", complaint.get("status", "")),
        ]
        dlg = PAMSDetailDialog(f"Complaint #{complaint['complaint_id']}", details, self)
        dlg.exec()

    def _updateStatus(self):
        """Update the status of the selected complaint in the database."""
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a complaint.")
            return

        cid = int(self._table.item(row, 0).text())
        current_subject = self._table.item(row, 3).text()
        current_status = self._table.item(row, 4).text()

        fields = [
            {"key": "complaint", "label": "Complaint", "type": "readonly",
             "value": f"#{cid} — {current_subject}"},
            {"key": "status", "label": "New Status", "type": "combo",
             "options": ["Open", "Under Review", "Resolved", "Closed"],
             "value": current_status},
        ]
        dlg = PAMSFormDialog("Update Complaint Status", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_status = dlg.get_values()["status"]
            try:
                success = update_complaint_status(cid, new_status)
                if success:
                    self._refresh_table()
                    show_success(self, f"Complaint #{cid} status updated to '{new_status}'.")
                else:
                    show_error(self, "Failed to update complaint status.")
            except Exception as e:
                show_error(self, f"Database error: {e}")
