"""
24030388 - Ishaq Modassir Mushtaq

Compatibility re-export hub for database models and helper functions.
Existing imports from this module continue to work.
"""

# Class re-exports
from auth_models import User as AuthUser
from user_models import User, StaffMember
from apartment_models import Apartment
from tenant_models import Tenant
from lease_models import LeaseAgreement
from finance_models import Invoice, Payment
from maintenance_models import Maintenance, MaintenanceLog
from location_models import Location
from frontdesk_models import Complaint, Enquiry

# Auth (login / signup windows)
from auth_models import (
    signup,
    login,
    get_role_by_code,
    does_user_exist,
    STAFF_ROLES,
)

# User & Staff (admin panel)
from user_models import (
    get_all_users,
    get_user_by_id,
    admin_add_user,
    update_user,
    delete_user,
    get_user_count,
    change_password,
    get_all_staff,
    update_staff_member,
)

# Apartments (admin panel, dashboard)
from apartment_models import (
    get_all_apartments,
    get_apartment_count,
    update_apartment,
    update_apartment_status,
    update_apartment_rent,
)

# Tenants (admin panel, front desk panel, tenant panel)
from tenant_models import (
    get_all_tenants,
    get_tenant_profile,
    update_tenant_contact,
    update_tenant_personal,
    get_active_lease_for_tenant,
    request_early_termination,
    change_tenant_password,
    get_notifications_for_tenant,
    create_notification,
    mark_notification_read,
    mark_all_notifications_read,
)

# Leases (admin panel, tenant panel)
from lease_models import (
    get_all_leases,
    get_leases_for_user,
    create_lease,
    update_lease,
    update_lease_status,
    terminate_lease,
)

# Finance / Invoices / Payments (finance panel, tenant panel)
from finance_models import (
    get_all_invoices,
    get_invoices_for_tenant,
    create_invoice,
    update_invoice,
    mark_invoice_paid,
    get_all_payments,
    get_payments_for_tenant,
    create_payment,
    update_payment,
)

# Maintenance (maintenance panel, tenant panel, front desk panel)
from maintenance_models import (
    get_all_maintenance_requests,
    get_request_by_id,
    get_maintenance_for_tenant,
    get_maintenance_for_staff,
    create_maintenance_request,
    update_maintenance_status,
    update_maintenance_priority,
    assign_staff_to_request,
    update_scheduled_date,
    update_maintenance_cost,
    get_staff_availability,
    get_all_staff as get_all_maintenance_staff,
    get_maintenance_stats,
    get_all_maintenance_logs,
    get_logs_for_request,
    create_maintenance_log,
)

# Locations (admin panel, login window)
from location_models import (
    get_all_locations,
    add_location,
)

# Front desk (complaints, enquiries)
from frontdesk_models import (
    get_all_complaints,
    get_complaint_by_id,
    get_complaints_for_tenant,
    get_complaint_stats,
    create_complaint,
    update_complaint_status,
    delete_complaint,
    get_all_enquiries,
    get_enquiries_for_tenant,
    create_enquiry,
)
