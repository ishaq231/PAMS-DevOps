"""

23010646 - Hasaan Ahmad 
220367921 - Royden Dias

PAMS - Paragon Apartment Management System
Maintenance Staff Panels — Requests, Log Resolution, Schedule

Implements all MaintenanceStaff class methods and use-case operations:
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QLineEdit, QComboBox, QTextEdit, QFrame, QTabWidget
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

from maintenance_models import (
    get_all_maintenance_requests,
    get_request_by_id,
    update_maintenance_status,
    update_maintenance_priority,
    assign_staff_to_request,
    update_scheduled_date,
    update_maintenance_cost,
    get_staff_availability,
    get_all_staff,
    get_all_maintenance_logs,
    get_logs_for_request,
    create_maintenance_log,
    get_maintenance_stats,
)

try:
    from tenant_models import create_notification as _create_notification
except ImportError:
    _create_notification = None


#  MAINTENANCE REQUESTS PANEL

class MaintenanceRequestsPanel(BasePanel):
    """
    Maintenance Staff → My Requests
    View, investigate, prioritise, assign, update and resolve maintenance
    requests and complaints.
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._requests = []
        self._observers: list = []  # Observer pattern: attach/detach
        self._build_ui()
        self._load_from_db()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Maintenance Requests & Complaints",
            "View, investigate, prioritise and resolve all maintenance requests"
        )
        self._main_layout.addWidget(header)

        # Summary counts row — populated after data load
        self._summary_layout = QHBoxLayout()
        self._summary_layout.setSpacing(12)
        self._main_layout.addLayout(self._summary_layout)

        # Toolbar
        toolbar = QHBoxLayout()
        self._btn_details = make_outline_button("View Details", T.ACCENT)
        self._btn_status = make_action_button("Update Status", T.INFO)
        self._btn_assign = make_action_button("Assign Staff", T.ACCENT)
        self._btn_priority = make_action_button("Set Priority", T.WARNING)
        self._btn_notify = make_outline_button("Notify Tenant", T.SUCCESS)
        self._btn_schedule = make_outline_button("Communicate Dates", T.INFO)

        self._btn_details.clicked.connect(self.getRequestDetails)
        self._btn_status.clicked.connect(self._updateStatus)
        self._btn_assign.clicked.connect(self._assignStaff)
        self._btn_priority.clicked.connect(self._setPriority)
        self._btn_notify.clicked.connect(self._notifyTenant)
        self._btn_schedule.clicked.connect(self._communicateDates)

        toolbar.addWidget(self._btn_details)
        toolbar.addWidget(self._btn_status)
        toolbar.addWidget(self._btn_assign)
        toolbar.addWidget(self._btn_priority)
        toolbar.addStretch()
        toolbar.addWidget(self._btn_notify)
        toolbar.addWidget(self._btn_schedule)
        self._btn_refresh = make_outline_button("Refresh", T.SUCCESS)
        self._btn_refresh.clicked.connect(self._load_from_db)
        toolbar.addWidget(self._btn_refresh)
        self._main_layout.addLayout(toolbar)

        # Table
        self._table = PAMSTableWidget([
            "ID", "Description", "Category", "Status", "Priority",
            "Tenant", "Apartment", "Reported", "Scheduled", "Assigned To"
        ])
        self._main_layout.addWidget(self._table)

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _load_from_db(self):
        """Reload requests from the database and refresh the table."""
        self._requests = self._filter_by_location(get_all_maintenance_requests())
        self._rebuild_summary()
        self._load_table()

    def _rebuild_summary(self):
        T = PAMSTheme
        while self._summary_layout.count():
            item = self._summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total  = len(self._requests)
        open_c = sum(1 for r in self._requests if r["status"] == "Open")
        prog_c = sum(1 for r in self._requests if r["status"] == "In Progress")
        done_c = sum(1 for r in self._requests if r["status"] == "Resolved")

        for title, val, color in [
            ("Total",       str(total),  T.INFO),
            ("Open",        str(open_c), T.WARNING),
            ("In Progress", str(prog_c), T.ACCENT),
            ("Resolved",    str(done_c), T.SUCCESS),
        ]:
            card = SectionCard()
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            lt = QLabel(title)
            lt.setStyleSheet(f"color: {T.TEXT_BODY}; font-size: 11px; font-weight: 600;")
            lv = QLabel(val)
            lv.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
            cl.addWidget(lt)
            cl.addWidget(lv)
            card.setFixedHeight(80)
            self._summary_layout.addWidget(card)

    def _load_table(self):
        rows = []
        for r in self._requests:
            rows.append([
                str(r["request_id"]),
                (r.get("description") or "")[:40],
                r.get("category") or "General",
                r["status"],
                r["priority"],
                r.get("tenant_name") or "—",
                r.get("apartment_number") or "—",
                r.get("report_date") or "—",
                r.get("scheduled_date") or "—",
                r.get("staff_name") or "Unassigned",
            ])
        self._table.populate(rows)

    def _get_selected_request(self):
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a maintenance request.")
            return None
        rid = int(self._table.item(row, 0).text())
        return next((r for r in self._requests if r["request_id"] == rid), None)

    # Maintenance.getRequestDetails()

    def getRequestDetails(self):
        """View full details of the selected maintenance request.
        Also serves as: Investigate Maintenance Requests & Complaints."""
        req = self._get_selected_request()
        if not req:
            return

        tracking = self.getTrackingStatus(req)
        details = [
            ("Request ID",     str(req["request_id"])),
            ("Description",    req.get("description") or ""),
            ("Category",       req.get("category") or "General"),
            ("Status",         req["status"]),
            ("Priority",       req["priority"]),
            ("Tenant",         req.get("tenant_name") or "—"),
            ("Apartment",      req.get("apartment_number") or "—"),
            ("Reported Date",  req.get("report_date") or "—"),
            ("Scheduled Date", req.get("scheduled_date") or "Not scheduled"),
            ("Resolved Date",  req.get("resolved_date") or "Not resolved"),
            ("Assigned Staff", req.get("staff_name") or "Unassigned"),
            ("Tracking Status", tracking),
            ("Data Valid",     "Yes" if self.validateRequestData(req) else "No"),
        ]
        dlg = PAMSDetailDialog(
            f"Request #{req['request_id']} — Details", details, self)
        dlg.exec()

    # Maintenance.getTrackingStatus()

    def getTrackingStatus(self, req: dict) -> str:
        if req["status"] == "Resolved":
            return f"Resolved on {req.get('resolved_date', '—')}"
        elif req["status"] == "In Progress":
            return f"In progress — scheduled {req.get('scheduled_date') or 'TBD'}"
        elif req["status"] == "Open":
            return "Awaiting assignment and scheduling"
        return req["status"]

    # Maintenance.validateRequestData()

    def validateRequestData(self, req: dict) -> bool:
        return bool(req.get("description") and
                    req.get("tenant_name") and
                    req.get("apartment_number"))

    # Maintenance.updateStatus(newStatus)

    def _updateStatus(self):
        req = self._get_selected_request()
        if not req:
            return

        fields = [
            {"key": "request", "label": "Request", "type": "readonly",
             "value": f"REQ-{req['request_id']:03d} — {(req.get('description') or '')[:40]}"},
            {"key": "status", "label": "New Status", "type": "combo",
             "options": ["Open", "In Progress", "Resolved", "Closed"],
             "value": req["status"]},
        ]
        dlg = PAMSFormDialog("Update Request Status", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_status = dlg.get_values()["status"]
            if update_maintenance_status(req["request_id"], new_status):
                self._load_from_db()
                self.notifyObservers(req)
                show_success(self,
                    f"Request #{req['request_id']} status updated to '{new_status}'.")
            else:
                show_error(self, "Failed to update status. Please try again.")

    # Maintenance.assignToStaff(staffID) — includes: Check Worker Availability

    def _assignStaff(self):
        req = self._get_selected_request()
        if not req:
            return

        available = [s for s in get_staff_availability() if s["available"]]
        if not available:
            show_error(self, "No maintenance staff currently available.")
            return

        staff_options = [
            f"{s['name']} (Jobs: {s['current_jobs']}/{s['max_jobs']}) [ID:{s['user_id']}]"
            for s in available
        ]

        fields = [
            {"key": "request", "label": "Request", "type": "readonly",
             "value": f"REQ-{req['request_id']:03d} — {(req.get('description') or '')[:40]}"},
            {"key": "staff", "label": "Assign To", "type": "combo",
             "options": staff_options, "value": staff_options[0]},
        ]
        dlg = PAMSFormDialog("Assign Staff — Check Availability", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            staff_str = dlg.get_values()["staff"]
            staff_id = int(staff_str.split("[ID:")[1].rstrip("]"))
            staff_name = staff_str.split(" (")[0]
            if assign_staff_to_request(req["request_id"], staff_id):
                self._load_from_db()
                show_success(self,
                    f"Request #{req['request_id']} assigned to {staff_name}.")
            else:
                show_error(self, "Failed to assign staff. Please try again.")

    # Maintenance.setPriority(priority) — Prioritises Maintenance Requests

    def _setPriority(self):
        req = self._get_selected_request()
        if not req:
            return

        fields = [
            {"key": "request", "label": "Request", "type": "readonly",
             "value": f"REQ-{req['request_id']:03d} — {(req.get('description') or '')[:40]}"},
            {"key": "current", "label": "Current Priority", "type": "readonly",
             "value": req["priority"]},
            {"key": "priority", "label": "New Priority", "type": "combo",
             "options": ["Emergency", "High", "Medium", "Low"],
             "value": req["priority"]},
        ]
        dlg = PAMSFormDialog("Prioritise Request", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_priority = dlg.get_values()["priority"]
            if update_maintenance_priority(req["request_id"], new_priority):
                self._load_from_db()
                show_success(self,
                    f"Request #{req['request_id']} priority set to '{new_priority}'.")
            else:
                show_error(self, "Failed to update priority. Please try again.")

    # Maintenance.notifyTenant() → Notification

    def _notifyTenant(self):
        req = self._get_selected_request()
        if not req:
            return

        tenant = req.get("tenant_name") or "Tenant"
        fields = [
            {"key": "tenant",  "label": "Tenant",  "type": "readonly", "value": tenant},
            {"key": "request", "label": "Request", "type": "readonly",
             "value": f"REQ-{req['request_id']:03d}"},
            {"key": "message", "label": "Notification Message", "type": "textarea",
             "value": (
                 f"Dear {tenant},\n\nYour maintenance request "
                 f"(REQ-{req['request_id']:03d}: {req.get('description') or ''}) "
                 f"is currently '{req['status']}'.\n\n"
                 + (f"Scheduled for: {req['scheduled_date']}"
                    if req.get("scheduled_date")
                    else "We will schedule this shortly.")
                 + "\n\nParagon Management"
             )},
        ]
        dlg = PAMSFormDialog("Notify Tenant", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # Persist notification to DB
            message = dlg.get_values().get("message", "")
            tenant_id = req.get("reportedByTenant_id") or req.get("tenant_id")
            if tenant_id and _create_notification:
                try:
                    _create_notification(tenant_id, message, "Maintenance")
                except Exception as e:
                    print(f"[maintenance_panel] notification save failed: {e}")
            show_success(self,
                f"Notification sent to {tenant} for REQ-{req['request_id']:03d}.")

    # Communicate Maintenance Dates & Times to Tenants

    def _communicateDates(self):
        req = self._get_selected_request()
        if not req:
            return

        fields = [
            {"key": "tenant", "label": "Tenant", "type": "readonly",
             "value": req.get("tenant_name") or "—"},
            {"key": "request", "label": "Request", "type": "readonly",
             "value": f"REQ-{req['request_id']:03d}"},
            {"key": "date", "label": "Scheduled Date", "type": "date",
             "value": req.get("scheduled_date") or ""},
            {"key": "time", "label": "Scheduled Time", "type": "combo",
             "options": ["08:00–10:00", "10:00–12:00", "12:00–14:00",
                         "14:00–16:00", "16:00–18:00"],
             "value": "10:00–12:00"},
            {"key": "notes", "label": "Additional Notes", "type": "textarea", "value": ""},
        ]
        dlg = PAMSFormDialog("Communicate Dates to Tenant", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            if update_scheduled_date(req["request_id"], values["date"]):
                self._load_from_db()

                # Persist notification to DB
                tenant_id = req.get("reportedByTenant_id") or req.get("tenant_id")
                if tenant_id and _create_notification:
                    try:
                        note_msg = (
                            f"Maintenance request #{req['request_id']} has been scheduled "
                            f"for {values['date']} ({values['time']})."
                        )
                        if values.get("notes"):
                            note_msg += f" Notes: {values['notes']}"
                        _create_notification(tenant_id, note_msg, "Maintenance")
                    except Exception as e:
                        print(f"[maintenance_panel] schedule notification failed: {e}")

                show_success(self,
                    f"Maintenance date communicated to {req.get('tenant_name') or 'tenant'}:\n"
                    f"Date: {values['date']}, Time: {values['time']}")
            else:
                show_error(self, "Failed to save scheduled date.")

    # Observer pattern: attach / detach / notifyObservers

    def attach(self, observer):
        """Maintenance.attach(o: Observer) — subscribe to updates."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """Maintenance.detach(o: Observer) — unsubscribe from updates."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notifyObservers(self, req: dict):
        """Maintenance.notifyObservers() — notify all observers of status change."""
        message = (f"Maintenance Request #{req['request_id']} "
                   f"status changed to '{req['status']}'")
        for obs in self._observers:
            if hasattr(obs, 'update'):
                obs.update(message)


#  LOG RESOLUTION PANEL

class LogResolutionPanel(BasePanel):
    """
    Maintenance Staff → Log Resolution
    Methods: logResolutionDetails(details), MaintenanceLog.create_log(),
    Resolves Issues (use-case)
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._logs = []
        self._requests = []
        self._build_ui()
        self._load_from_db()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Log Resolution / Maintenance Data",
            "Log resolution details once maintenance issues are resolved"
        )
        self._main_layout.addWidget(header)

        toolbar = QHBoxLayout()
        self._btn_new_log = make_action_button("+ Create New Log", T.ACCENT)
        self._btn_view_log = make_outline_button("View Log Details", T.INFO)

        self._btn_new_log.clicked.connect(self.create_log)
        self._btn_view_log.clicked.connect(self._view_log)

        toolbar.addWidget(self._btn_new_log)
        toolbar.addWidget(self._btn_view_log)
        toolbar.addStretch()
        self._btn_refresh = make_outline_button("Refresh", T.SUCCESS)
        self._btn_refresh.clicked.connect(self._load_from_db)
        toolbar.addWidget(self._btn_refresh)
        self._main_layout.addLayout(toolbar)

        lbl = QLabel("Maintenance Logs")
        lbl.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        self._main_layout.addWidget(lbl)

        self._table = PAMSTableWidget([
            "Log ID", "Request ID", "Start Time", "End Time",
            "Description", "Parts Used", "Cost"
        ])
        self._main_layout.addWidget(self._table)

        lbl2 = QLabel("Resolved Requests Awaiting Log")
        lbl2.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        self._main_layout.addWidget(lbl2)

        self._resolved_table = PAMSTableWidget([
            "ID", "Description", "Tenant", "Apartment", "Resolved Date"
        ])
        self._main_layout.addWidget(self._resolved_table)

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _load_from_db(self):
        self._logs = get_all_maintenance_logs()
        self._requests = self._filter_by_location(get_all_maintenance_requests())
        self._refresh_logs_table()
        self._refresh_resolved_table()

    def _refresh_logs_table(self):
        rows = [
            [str(l["log_id"]), str(l["request_id"]),
             l.get("start_time") or "—", l.get("end_time") or "—",
             (l.get("description") or "")[:40],
             (l.get("parts_used") or "")[:30],
             l.get("cost_breakdown") or "—"]
            for l in self._logs
        ]
        self._table.populate(rows)

    def _refresh_resolved_table(self):
        logged_ids = {l["request_id"] for l in self._logs}
        unlogged = [
            r for r in self._requests
            if r["status"] == "Resolved" and r["request_id"] not in logged_ids
        ]
        rows = [
            [str(r["request_id"]), (r.get("description") or "")[:40],
             r.get("tenant_name") or "—",
             r.get("apartment_number") or "—",
             r.get("resolved_date") or "—"]
            for r in unlogged
        ]
        self._resolved_table.populate(rows)

    # MaintenanceLog.create_log()

    def create_log(self):
        """Create a new maintenance log entry (writes to DB).
        Includes: logResolutionDetails, Log Maintenance Data once resolved."""
        resolved = [r for r in self._requests if r["status"] == "Resolved"]
        if not resolved:
            show_error(self, "No resolved requests to log.")
            return

        request_options = [
            f"REQ-{r['request_id']:03d} — {(r.get('description') or '')[:40]}"
            for r in resolved
        ]

        fields = [
            {"key": "request", "label": "Request", "type": "combo",
             "options": request_options, "value": request_options[0]},
            {"key": "startTime", "label": "Start Time", "type": "text",
             "value": "", "placeholder": "e.g. 2026-03-01 09:00"},
            {"key": "endTime", "label": "End Time", "type": "text",
             "value": "", "placeholder": "e.g. 2026-03-01 15:00"},
            {"key": "description", "label": "Resolution Description",
             "type": "textarea", "value": ""},
            {"key": "partsUsed", "label": "Parts Used", "type": "text", "value": ""},
            {"key": "costBreakdown", "label": "Cost Breakdown", "type": "text",
             "value": "", "placeholder": "e.g. Parts: £50, Labour: £100"},
            {"key": "technicianNotes", "label": "Technician Notes",
             "type": "textarea", "value": ""},
        ]
        dlg = PAMSFormDialog("Create Maintenance Log", fields, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            values = dlg.get_values()
            req_id = int(values["request"].split("REQ-")[1].split(" ")[0])
            new_id = create_maintenance_log(
                request_id=req_id,
                start_time=values["startTime"] or None,
                end_time=values["endTime"] or None,
                description=values["description"],
                parts_used=values["partsUsed"],
                cost_breakdown=values["costBreakdown"],
                technician_notes=values["technicianNotes"],
            )
            if new_id:
                self._load_from_db()
                show_success(self,
                    f"Maintenance log #{new_id} created for REQ-{req_id:03d}.")
            else:
                show_error(self, "Failed to save maintenance log. Please try again.")

    def logResolutionDetails(self, details: str):
        """Maintenance.logResolutionDetails(details) — programmatic hook."""
        pass

    def _view_log(self):
        row = self._table.currentRow()
        if row < 0:
            show_error(self, "Please select a log entry.")
            return
        log_id = int(self._table.item(row, 0).text())
        log = next((l for l in self._logs if l["log_id"] == log_id), None)
        if not log:
            return

        details = [
            ("Log ID",           str(log["log_id"])),
            ("Request ID",       str(log["request_id"])),
            ("Start Time",       log.get("start_time") or "—"),
            ("End Time",         log.get("end_time") or "—"),
            ("Description",      log.get("description") or "—"),
            ("Parts Used",       log.get("parts_used") or "—"),
            ("Cost Breakdown",   log.get("cost_breakdown") or "—"),
            ("Technician Notes", log.get("technician_notes") or "—"),
        ]
        dlg = PAMSDetailDialog(f"Maintenance Log #{log['log_id']}", details, self)
        dlg.exec()


#  SCHEDULE & AVAILABILITY PANEL

class SchedulePanel(BasePanel):
    """
    Maintenance Staff → Schedule
    Methods: Check Worker Availability, Communicate Maintenance Dates
    """

    def __init__(self, location_name=None, parent=None):
        super().__init__(parent)
        self._location_name = location_name
        self._build_ui()
        self._load_from_db()

    def _build_ui(self):
        T = PAMSTheme

        header = make_panel_header(
            "Schedule & Worker Availability",
            "Check worker availability and manage maintenance schedules"
        )
        self._main_layout.addWidget(header)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        self._btn_refresh = make_outline_button("Refresh", T.SUCCESS)
        self._btn_refresh.clicked.connect(self._load_from_db)
        toolbar.addWidget(self._btn_refresh)
        self._main_layout.addLayout(toolbar)

        lbl = QLabel("Worker Availability")
        lbl.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        self._main_layout.addWidget(lbl)

        self._staff_table = PAMSTableWidget([
            "Staff ID", "Name", "Role", "Available", "Current Jobs", "Max Jobs"
        ])
        self._main_layout.addWidget(self._staff_table)

        lbl2 = QLabel("Scheduled Maintenance")
        lbl2.setStyleSheet(f"color: {T.ACCENT}; font-size: 16px; font-weight: 600;")
        self._main_layout.addWidget(lbl2)

        self._sched_table = PAMSTableWidget([
            "ID", "Description", "Tenant", "Apartment", "Scheduled Date", "Assigned To"
        ])
        self._main_layout.addWidget(self._sched_table)

    def _filter_by_location(self, items):
        if self._location_name is None:
            return items
        return [i for i in items if i.get('location') == self._location_name]

    def _load_from_db(self):
        staff = get_staff_availability()
        self._staff_table.populate([
            [str(s["user_id"]), s["name"], s.get("role") or "—",
             "Yes" if s["available"] else "No",
             str(s["current_jobs"]), str(s["max_jobs"])]
            for s in staff
        ])

        requests = self._filter_by_location(get_all_maintenance_requests())
        scheduled = [r for r in requests if r.get("scheduled_date")]
        self._sched_table.populate([
            [str(r["request_id"]), (r.get("description") or "")[:40],
             r.get("tenant_name") or "—",
             r.get("apartment_number") or "—",
             r.get("scheduled_date") or "—",
             r.get("staff_name") or "Unassigned"]
            for r in scheduled
        ])

    def checkWorkerAvailability(self) -> list:
        """Return list of available maintenance workers (DB-backed)."""
        return [s for s in get_staff_availability() if s["available"]]

