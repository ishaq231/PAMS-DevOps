"""
24030388 - Ishaq Modassir Mushtaq

PAMS seed data script for populating database tables with demo data.

Run from root:
    python src/database/seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import bcrypt
from connection import Database_connection

# Helpers
def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def run_seed():
    db = Database_connection()
    conn = db.connect()
    cursor = conn.cursor()

    

    print("Clearing existing data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in [
        "notification", "enquiry", "complaint",
        "maintenance_request", "payment", "Invoice", "lease_agreement",
        "apartment_amenity", "apartment", "tenant", "staff_member",
        "user", "amenity", "location", "staff_role",
    ]:
        cursor.execute(f"DELETE FROM `{table}`")
        # Reset AUTO_INCREMENT where applicable
        try:
            cursor.execute(f"ALTER TABLE `{table}` AUTO_INCREMENT = 1")
        except Exception:
            pass
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("Tables cleared.")

    # 1. locations
    print("Seeding locations...")
    locations = [
        (1, "Bristol",    "Sarah Chen"),
        (2, "Cardiff",    "David Okafor"),
        (3, "London",     "Priya Sharma"),
        (4, "Manchester", "Tom Briggs"),
    ]
    cursor.executemany(
        "INSERT INTO location (location_id, city, manager) VALUES (%s, %s, %s)",
        locations
    )
    conn.commit()

    # 2. amenities
    print("Seeding amenities...")
    amenities = [
        (1, "Gym",             "On-site fitness centre with modern equipment"),
        (2, "Parking",         "Secure underground parking space included"),
        (3, "WiFi",            "High-speed fibre broadband included"),
        (4, "Balcony",         "Private balcony with city or garden views"),
        (5, "Dishwasher",      "Built-in dishwasher in kitchen"),
        (6, "Air Conditioning","Multi-zone air conditioning system"),
        (7, "Concierge",       "24/7 concierge and security service"),
        (8, "Rooftop Terrace", "Shared rooftop terrace with panoramic views"),
        (9, "Pet Friendly",    "Pets welcome with prior approval"),
        (10,"Storage Unit",    "Private locked storage unit in basement"),
    ]
    cursor.executemany(
        "INSERT INTO amenity (amenity_id, name, description) VALUES (%s, %s, %s)",
        amenities
    )
    conn.commit()

    # 3. staff_role
    print("Seeding staff roles...")
    staff_roles = [
        (1, "Administrator",     "ADMIN2026"),
        (2, "Manager",           "MGR2026"),
        (3, "Front Desk Staff",  "FRONT2026"),
        (4, "Finance Manager",   "FIN2026"),
        (5, "Maintenance Staff", "MAINT2026"),
    ]
    try:
        cursor.executemany(
            "INSERT INTO staff_role (role_id, role_name, signup_code) VALUES (%s, %s, %s)",
            staff_roles
        )
        conn.commit()
    except Exception as e:
        print(f"  staff_role skipped (table may not exist yet): {e}")
        conn.rollback()

    # 4. users
    # Roles: Administrator, Manager, Front Desk Staff,
    #        Finance Manager, Maintenance Staff, Tenant
    print("Seeding users (hashing passwords — may take a moment)...")
    users = [
        # (fname, lname, email, phone, dob, role, username, password_plain)
        # Staff
        ("Haso",    "Admin",    "haso@paragon.co.uk",          "07700100001", "1985-03-15",
         "Administrator",    "haso_admin",    "Admin1234!"),
        ("Sarah",   "Chen",     "sarah.chen@paragon.co.uk",    "07700100002", "1980-07-22",
         "Manager",           "sarah_mgr",     "Manager123!"),
        ("James",   "Wilson",   "james.w@paragon.co.uk",       "07700100003", "1992-11-08",
         "Front Desk Staff",  "james_fd",      "FrontDesk1!"),
        ("Nina",    "Patel",    "nina.p@paragon.co.uk",        "07700100004", "1990-04-30",
         "Finance Manager",   "nina_fin",      "Finance123!"),
        ("Marcus",  "Brown",    "marcus.b@paragon.co.uk",      "07700100005", "1988-09-12",
         "Maintenance Staff", "marcus_maint",  "Maint1234!"),
        ("Aisha",   "Osei",     "aisha.o@paragon.co.uk",       "07700100006", "1994-02-18",
         "Maintenance Staff", "aisha_maint",   "Maint5678!"),
        # Tenants
        ("Oliver",  "Thompson", "oliver.t@gmail.com",          "07800200001", "1995-06-14",
         "Tenant",             "oliver_t",      "Tenant123!"),
        ("Emma",    "Clarke",   "emma.c@gmail.com",            "07800200002", "1998-01-25",
         "Tenant",             "emma_c",        "Tenant123!"),
        ("Liam",    "Murphy",   "liam.m@gmail.com",            "07800200003", "1993-08-03",
         "Tenant",             "liam_m",        "Tenant123!"),
        ("Sophie",  "Williams", "sophie.w@gmail.com",          "07800200004", "1997-12-11",
         "Tenant",             "sophie_w",      "Tenant123!"),
        ("Daniel",  "Khan",     "daniel.k@gmail.com",          "07800200005", "1990-05-20",
         "Tenant",             "daniel_k",      "Tenant123!"),
        ("Zoe",     "Henderson","zoe.h@gmail.com",             "07800200006", "1996-09-07",
         "Tenant",             "zoe_h",         "Tenant123!"),
    ]

    user_insert = (
        "INSERT INTO user (fname, lname, email, phone_number, date_of_birth, "
        "role, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    for u in users:
        hashed = hash_pw(u[7])
        cursor.execute(user_insert, (u[0], u[1], u[2], u[3], u[4], u[5], u[6], hashed))
    conn.commit()
    print("  Users inserted.")

    # Get auto-assigned IDs
    cursor.execute("SELECT user_id, username FROM user ORDER BY user_id")
    user_rows = cursor.fetchall()
    user_ids = {row[1]: row[0] for row in user_rows}

    # 5. staff_member
    print("Seeding staff members...")
    staff_data = [
        # (username,            salary,    role,                start_date, location_id)
        ("haso_admin",    52000.00, "Administrator",     "2020-01-10", 1),
        ("sarah_mgr",     48000.00, "Manager",           "2019-03-15", 1),
        ("james_fd",      28000.00, "Front Desk Staff",  "2021-06-01", 2),
        ("nina_fin",      42000.00, "Finance Manager",   "2020-09-20", 3),
        ("marcus_maint",  31000.00, "Maintenance Staff", "2022-02-14", 1),
        ("aisha_maint",   30500.00, "Maintenance Staff", "2023-05-08", 4),
    ]
    for s in staff_data:
        emp_id = user_ids[s[0]]
        cursor.execute(
            "INSERT INTO staff_member (employee_id, salary, role, start_date, location_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (emp_id, s[1], s[2], s[3], s[4])
        )
    conn.commit()

    # 6. tenants
    print("Seeding tenants...")
    tenant_data = [
        # (username,     occupation,            ni_number,    references)
        ("oliver_t",  "Software Engineer",    "AB123456C",  "John Doe, +447700900001"),
        ("emma_c",    "Graphic Designer",     "CD234567D",  "Jane Smith, +447700900002"),
        ("liam_m",    "Teacher",              "EF345678E",  "Paul Brown, +447700900003"),
        ("sophie_w",  "Marketing Manager",   "GH456789F",  "Lisa Green, +447700900004"),
        ("daniel_k",  "Accountant",           "IJ567890G",  "Mike White, +447700900005"),
        ("zoe_h",     "Nurse",                "KL678901H",  "Sandra Black, +447700900006"),
    ]
    for t in tenant_data:
        tid = user_ids[t[0]]
        cursor.execute(
            "INSERT INTO tenant (tenant_id, occupation, ni_number, `references`) "
            "VALUES (%s, %s, %s, %s)",
            (tid, t[1], t[2], t[3])
        )
    conn.commit()

    # 7. apartments
    print("Seeding apartments...")
    apartments = [
        # (apt_number, monthly_rent, location_id, type,        sq_ft, status,       rooms)
        (101, 1200.00, 1, "1-Bed",    "550",  "Occupied",    2),
        (102, 1500.00, 1, "2-Bed",    "750",  "Vacant",      3),
        (103, 900.00,  1, "Studio",   "380",  "Vacant",      1),
        (201, 1800.00, 2, "2-Bed",    "800",  "Occupied",    3),
        (202, 2200.00, 2, "3-Bed",    "1100", "Vacant",      4),
        (203, 950.00,  2, "Studio",   "400",  "Maintenance", 1),
        (301, 2500.00, 3, "Penthouse","1800", "Occupied",    5),
        (302, 1900.00, 3, "2-Bed",    "850",  "Occupied",    3),
        (303, 1100.00, 3, "1-Bed",    "520",  "Vacant",      2),
        (401, 1400.00, 4, "1-Bed",    "600",  "Occupied",    2),
        (402, 1700.00, 4, "2-Bed",    "780",  "Occupied",    3),
        (403, 2100.00, 4, "3-Bed",    "1050", "Vacant",      4),
    ]
    apt_insert = (
        "INSERT INTO apartment (apartment_number, monthly_rent, location_id, type, "
        "square_footage, occupation_status, number_of_rooms) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    for a in apartments:
        cursor.execute(apt_insert, a)
    conn.commit()

    # Get apartment IDs
    cursor.execute("SELECT apartment_id, apartment_number FROM apartment ORDER BY apartment_id")
    apt_rows = cursor.fetchall()
    apt_ids = {row[1]: row[0] for row in apt_rows}  # apt_number -> apt_id

    # 8. apartment_amenity
    print("Seeding apartment amenities...")
    apt_amenity_links = [
        # (apt_number, amenity_id)
        (101, 2), (101, 3), (101, 9),               # Parking, WiFi, Pet Friendly
        (102, 1), (102, 2), (102, 3), (102, 5),     # Gym, Parking, WiFi, Dishwasher
        (103, 3),                                    # WiFi
        (201, 2), (201, 3), (201, 4), (201, 6),     # Parking, WiFi, Balcony, AC
        (202, 1), (202, 2), (202, 3), (202, 4), (202, 6),
        (203, 3),                                    # WiFi only (under maintenance)
        (301, 1), (301, 2), (301, 3), (301, 4),
        (301, 6), (301, 7), (301, 8), (301, 10),    # Full penthouse amenities
        (302, 2), (302, 3), (302, 5), (302, 6),
        (303, 3), (303, 9),                          # WiFi, Pet Friendly
        (401, 2), (401, 3), (401, 5),
        (402, 1), (402, 2), (402, 3), (402, 4),
        (403, 1), (403, 2), (403, 3), (403, 4), (403, 6), (403, 10),
    ]
    for apt_num, am_id in apt_amenity_links:
        aId = apt_ids.get(apt_num)
        if aId:
            cursor.execute(
                "INSERT IGNORE INTO apartment_amenity (apartmentID, amenityID) VALUES (%s, %s)",
                (aId, am_id)
            )
    conn.commit()

    # 9. lease_agreements
    print("Seeding lease agreements...")
    leases = [
        # (tenant_username, apt_number, start,        end,          rent,    deposit, months, status)
        ("oliver_t",  101, "2025-01-01", "2026-01-01", 1200.00, 1200.00, 12, "ACTIVE"),
        ("emma_c",    201, "2025-03-01", "2026-03-01", 1800.00, 1800.00, 12, "ACTIVE"),
        ("liam_m",    301, "2024-06-01", "2025-06-01", 2500.00, 2500.00, 12, "EXPIRED"),
        ("sophie_w",  302, "2025-07-01", "2026-07-01", 1900.00, 1900.00, 12, "ACTIVE"),
        ("daniel_k",  401, "2025-02-15", "2026-02-15", 1400.00, 1400.00, 12, "ACTIVE"),
        ("zoe_h",     402, "2025-09-01", "2026-09-01", 1700.00, 1700.00, 12, "ACTIVE"),
    ]
    lease_ids = []
    lease_insert = (
        "INSERT INTO lease_agreement "
        "(tenantID, apartmentID, start_date, end_date, monthly_rent, deposit_amount, "
        "lease_term_months, status, early_termination_notice, termination_penalty_percent) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 30, 5.00)"
    )
    for l in leases:
        tid = user_ids[l[0]]
        aid = apt_ids[l[1]]
        cursor.execute(lease_insert, (tid, aid, l[2], l[3], l[4], l[5], l[6], l[7]))
        lease_ids.append(cursor.lastrowid)
    conn.commit()

    # 10. invoices
    print("Seeding invoices...")
    # 3 invoices per active lease (Jan–Mar 2026)
    invoice_data = []
    month_labels = ["January 2026", "February 2026", "March 2026"]
    for i, (lease_id, lease) in enumerate(zip(lease_ids, leases)):
        months = [
            ("2026-01-01", "2026-01-31", "Paid"),
            ("2026-02-01", "2026-02-28", "Paid"),
            ("2026-03-01", "2026-03-31", "Pending"),
        ]
        rent = lease[4]
        for j, (issue, due, status) in enumerate(months):
            desc = f"Monthly rent — {month_labels[j]}"
            invoice_data.append((lease_id, rent, due, status, issue, desc))

    cursor.executemany(
        "INSERT INTO Invoice (leaseID, amount, due_date, status, issue_date, description) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        invoice_data
    )
    conn.commit()

    # Add one overdue invoice for variety
    cursor.execute(
        "INSERT INTO Invoice (leaseID, amount, due_date, status, issue_date, description) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (lease_ids[2], 2500.00, "2025-05-31", "Overdue", "2025-05-01", "Monthly rent — May 2025")
    )
    conn.commit()

    # 10b. payments
    print("Seeding payments...")
    # Fetch all Paid invoice IDs grouped by lease so we can match tenants
    cursor.execute("""
        SELECT i.invoiceID, i.leaseID, i.amount, i.due_date,
               CONCAT(u.fname, ' ', u.lname) AS tenant_name
        FROM Invoice i
        JOIN lease_agreement la ON i.leaseID = la.leaseID
        JOIN user u ON la.tenantID = u.user_id
        WHERE i.status = 'Paid'
        ORDER BY i.invoiceID
    """)
    paid_invoices = cursor.fetchall()
    # (invoiceID, leaseID, amount, due_date, tenant_name)

    # Payment methods and refs cycling through tenants for variety
    methods = [
        "Bank Transfer", "Debit Card", "Bank Transfer",
        "Credit Card",  "Bank Transfer", "Debit Card",
    ]
    # Map lease_id → method index (fixed per tenant)
    lease_method = {lid: methods[i % len(methods)] for i, lid in enumerate(lease_ids)}

    payment_rows = []
    for idx, (inv_id, lease_id, amount, due_date, tenant_name) in enumerate(paid_invoices):
        method = lease_method.get(lease_id, "Bank Transfer")
        # Payment date = due_date (paid on time)
        pay_date = str(due_date)
        txn_ref  = f"TXN-2026-{1000 + idx + 1:04d}"
        receipt  = 1001 + idx
        payment_rows.append((inv_id, amount, pay_date, method, txn_ref, receipt))

    cursor.executemany(
        "INSERT INTO payment "
        "(invoice_id, amount_paid, payment_date, payment_method, transaction_ref, receipt_number) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        payment_rows
    )
    conn.commit()
    print(f"  {len(payment_rows)} payment records inserted.")

    # 11. maintenance_requests
    print("Seeding maintenance requests...")
    maint_staff_id = user_ids["marcus_maint"]
    aisha_id       = user_ids["aisha_maint"]

    maint_requests = [
        # (apt_number, tenant_username, assigned_username, description,
        #  priority, status, report_date, resolved_date, cost)
        (101, "oliver_t",  "marcus_maint",
         "Boiler not producing hot water",
         "High",   "Resolved",    "2025-11-15 09:00:00", "2025-11-16 14:00:00", 180.00),
        (201, "emma_c",    "aisha_maint",
         "Bathroom tap dripping constantly",
         "Medium", "Resolved",    "2025-12-01 10:30:00", "2025-12-02 11:00:00", 45.00),
        (302, "sophie_w",  "marcus_maint",
         "Kitchen extractor fan making loud noise",
         "Medium", "In Progress", "2026-01-10 08:00:00", None, 0.00),
        (401, "daniel_k",  "aisha_maint",
         "Window latch broken on bedroom window",
         "Low",    "Open",        "2026-02-05 13:00:00", None, 0.00),
        (402, "zoe_h",     "marcus_maint",
         "Damp patch appearing on living room ceiling",
         "High",   "In Progress", "2026-02-20 09:30:00", None, 0.00),
        (203, "liam_m",    "aisha_maint",
         "Front door lock jammed — cannot enter apartment",
         "Emergency", "Resolved", "2025-10-08 18:00:00", "2025-10-08 20:30:00", 220.00),
        (101, "oliver_t",  None,
         "Light fixture in hallway flickering",
         "Low",    "Open",        "2026-03-01 11:00:00", None, 0.00),
        (302, "sophie_w",  "aisha_maint",
         "Oven heating element not working",
         "Medium", "Open",        "2026-03-03 14:00:00", None, 0.00),
    ]
    maint_insert = (
        "INSERT INTO maintenance_request "
        "(apartment_id, reportedByTenant_id, assignedStaff_id, description, "
        "priority, status, report_date, resolved_date, cost) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )
    for m in maint_requests:
        apt_id    = apt_ids[m[0]]
        tenant_id = user_ids[m[1]]
        staff_id  = user_ids[m[2]] if m[2] else None
        cursor.execute(maint_insert,
            (apt_id, tenant_id, staff_id, m[3], m[4], m[5], m[6], m[7], m[8])
        )
    conn.commit()

    # 12. complaints
    print("Seeding complaints...")
    # status choices: Open | Under Review | Resolved | Closed
    complaints = [
        # (tenant_username, date_filed,    subject,                                   description,                                                                                    status)
        ("oliver_t",  "2025-11-20",
         "Noise from neighbouring unit late at night",
         "There is persistent loud music and noise coming from apartment 102 after midnight on weekdays. It has disrupted my sleep on multiple occasions.",
         "Resolved"),
        ("emma_c",    "2025-12-10",
         "Heating system not working properly",
         "The central heating in apartment 201 has been intermittent since early December. The radiators in the bedroom do not heat up at all.",
         "Resolved"),
        ("sophie_w",  "2026-01-15",
         "Lift out of service — no notice given",
         "The main lift has been out of service for three days with no advance notice or estimated repair time communicated to residents. I carry heavy equipment for work.",
         "Under Review"),
        ("daniel_k",  "2026-01-28",
         "Communal bin area not being cleaned regularly",
         "The bin area on the ground floor is consistently overflowing and has not been cleared for over a week. It is creating an unpleasant smell in the entrance hallway.",
         "Under Review"),
        ("zoe_h",     "2026-02-03",
         "Parking space occupied by unauthorised vehicle",
         "My assigned parking space (bay 12) has been used by an unknown vehicle on three separate occasions this month. I have had to park elsewhere.",
         "Open"),
        ("liam_m",    "2026-02-14",
         "Post and parcels going missing from communal area",
         "Multiple packages addressed to me have not been received over the past month. I believe they are being left unattended in the communal entrance and may have been taken.",
         "Open"),
        ("oliver_t",  "2026-02-25",
         "Water pressure in shower very low",
         "The shower in the main bathroom has had noticeably low water pressure since the start of February. The maintenance request raised was closed without the issue being fully resolved.",
         "Open"),
        ("emma_c",    "2026-03-01",
         "Rude conduct by a member of staff",
         "During my visit to the front desk on 28 February I felt I was spoken to dismissively when raising a concern about my lease renewal. I would like this to be formally noted.",
         "Open"),
    ]
    complaint_insert = (
        "INSERT INTO complaint (tenant_id, date_filed, subject, description, status) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    for c in complaints:
        tid = user_ids[c[0]]
        cursor.execute(complaint_insert, (tid, c[1], c[2], c[3], c[4]))
    conn.commit()

    # 13. enquiries
    print("Seeding enquiries...")
    james_id = user_ids["james_fd"]
    enquiries = [
        # (tenant_username, tenant_name_display, enquiry_details,                             handled_by,    date_logged)
        ("oliver_t",  "Oliver Thompson",
         "Asked about the process for renewing his lease which expires in January 2026. Advised on renewal timelines and directed to the manager.",
         "James Wilson", "2025-11-05"),
        ("emma_c",    "Emma Clarke",
         "Enquired whether she can sublet a room in apartment 201. Informed that subletting is not permitted under the standard lease agreement.",
         "James Wilson", "2025-11-18"),
        ("liam_m",    "Liam Murphy",
         "Asked about the status of his expired lease and options for signing a new agreement. Advised to schedule a meeting with the manager.",
         "James Wilson", "2025-12-03"),
        ("sophie_w",  "Sophie Williams",
         "Enquired about obtaining a second parking permit for a visiting family member. Informed that visitor permits are issued at the front desk on request.",
         "James Wilson", "2026-01-09"),
        ("daniel_k",  "Daniel Khan",
         "Asked when the January invoice would be generated and how to access payment history. Directed to the tenant portal and explained the billing cycle.",
         "James Wilson", "2026-01-20"),
        ("zoe_h",     "Zoe Henderson",
         "Enquired about adding a cat to the apartment. Confirmed apartment 402 is pet-friendly and advised her to submit a written request for management approval.",
         "James Wilson", "2026-02-06"),
        ("oliver_t",  "Oliver Thompson",
         "Requested a letter confirming his tenancy for a mortgage application. Letter prepared and emailed within the same day.",
         "James Wilson", "2026-02-19"),
        ("emma_c",    "Emma Clarke",
         "Asked about early termination of her lease. Explained the 30-day notice requirement and 5% early termination penalty as per the lease agreement.",
         "James Wilson", "2026-03-02"),
    ]
    enquiry_insert = (
        "INSERT INTO enquiry (tenant_id, tenant_name, enquiry_details, handled_by, date_logged) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    for e in enquiries:
        tid = user_ids[e[0]]
        cursor.execute(enquiry_insert, (tid, e[1], e[2], e[3], e[4]))
    conn.commit()

    # 14. notifications
    print("Seeding notifications...")
    notifications = [
        # (tenant_username, message, date, is_read, type)
        # Oliver Thompson (user 7)
        ("oliver_t", "Your invoice #1 for £1,200.00 has been marked as Paid.",
         "2026-01-31", 1, "Payment"),
        ("oliver_t", "Your invoice #2 for £1,200.00 has been marked as Paid.",
         "2026-02-28", 1, "Payment"),
        ("oliver_t", "New invoice #3 for £1,200.00 due on 2026-03-31.",
         "2026-03-01", 0, "Payment"),
        ("oliver_t", "Maintenance request #1 (Boiler not producing hot water) has been resolved.",
         "2025-11-16", 1, "Maintenance"),
        ("oliver_t", "Maintenance request #7 submitted (Low priority). We will review it shortly.",
         "2026-03-01", 0, "Maintenance"),
        ("oliver_t", "Your complaint 'Noise from neighbouring unit late at night' status has been updated to 'Resolved'.",
         "2025-12-05", 1, "General"),
        ("oliver_t", "Your complaint 'Water pressure in shower very low' (#7) has been filed and is now Open.",
         "2026-02-25", 0, "General"),

        # Emma Clarke (user 8)
        ("emma_c", "Your invoice #4 for £1,800.00 has been marked as Paid.",
         "2026-01-31", 1, "Payment"),
        ("emma_c", "Your invoice #5 for £1,800.00 has been marked as Paid.",
         "2026-02-28", 1, "Payment"),
        ("emma_c", "New invoice #6 for £1,800.00 due on 2026-03-31.",
         "2026-03-01", 0, "Payment"),
        ("emma_c", "Maintenance request #2 (Bathroom tap dripping) has been resolved.",
         "2025-12-02", 1, "Maintenance"),
        ("emma_c", "Your complaint 'Heating system not working properly' status has been updated to 'Resolved'.",
         "2025-12-20", 1, "General"),
        ("emma_c", "Your complaint 'Rude conduct by a member of staff' (#8) has been filed and is now Open.",
         "2026-03-01", 0, "General"),
        ("emma_c", "Your lease has been created. Start: 2025-03-01, End: 2026-03-01.",
         "2025-03-01", 1, "Lease"),

        # Liam Murphy (user 9)
        ("liam_m", "Maintenance request #6 (Front door lock jammed) has been resolved.",
         "2025-10-08", 1, "Maintenance"),
        ("liam_m", "Your complaint 'Post and parcels going missing' (#6) has been filed and is now Open.",
         "2026-02-14", 0, "General"),
        ("liam_m", "Invoice #19 for £2,500.00 is overdue (due 2025-05-31). Please pay immediately.",
         "2025-06-01", 0, "Payment"),
        ("liam_m", "Your lease (2024-06-01 to 2025-06-01) has expired.",
         "2025-06-01", 1, "Lease"),

        # Sophie Williams (user 10)
        ("sophie_w", "Your invoice #10 for £1,900.00 has been marked as Paid.",
         "2026-01-31", 1, "Payment"),
        ("sophie_w", "Your invoice #11 for £1,900.00 has been marked as Paid.",
         "2026-02-28", 1, "Payment"),
        ("sophie_w", "New invoice #12 for £1,900.00 due on 2026-03-31.",
         "2026-03-01", 0, "Payment"),
        ("sophie_w", "Maintenance request #3 status updated to 'In Progress'.",
         "2026-01-12", 0, "Maintenance"),
        ("sophie_w", "Maintenance request #8 submitted (Medium priority). We will review it shortly.",
         "2026-03-03", 0, "Maintenance"),
        ("sophie_w", "Your complaint 'Lift out of service — no notice given' status has been updated to 'Under Review'.",
         "2026-01-20", 0, "General"),
        ("sophie_w", "Your lease has been created. Start: 2025-07-01, End: 2026-07-01.",
         "2025-07-01", 1, "Lease"),

        # Daniel Khan (user 11)
        ("daniel_k", "Your invoice #13 for £1,400.00 has been marked as Paid.",
         "2026-01-31", 1, "Payment"),
        ("daniel_k", "New invoice #15 for £1,400.00 due on 2026-03-31.",
         "2026-03-01", 0, "Payment"),
        ("daniel_k", "Maintenance request #4 submitted (Low priority). We will review it shortly.",
         "2026-02-05", 0, "Maintenance"),
        ("daniel_k", "Your complaint 'Communal bin area not being cleaned' status has been updated to 'Under Review'.",
         "2026-02-05", 0, "General"),
        ("daniel_k", "Your lease has been created. Start: 2025-02-15, End: 2026-02-15.",
         "2025-02-15", 1, "Lease"),

        # Zoe Henderson (user 12)
        ("zoe_h", "Your invoice #16 for £1,700.00 has been marked as Paid.",
         "2026-01-31", 1, "Payment"),
        ("zoe_h", "New invoice #18 for £1,700.00 due on 2026-03-31.",
         "2026-03-01", 0, "Payment"),
        ("zoe_h", "Maintenance request #5 status updated to 'In Progress'.",
         "2026-02-22", 0, "Maintenance"),
        ("zoe_h", "Your complaint 'Parking space occupied by unauthorised vehicle' (#5) has been filed and is now Open.",
         "2026-02-03", 0, "General"),
        ("zoe_h", "Your lease has been created. Start: 2025-09-01, End: 2026-09-01.",
         "2025-09-01", 1, "Lease"),
    ]
    notif_insert = (
        "INSERT INTO notification "
        "(recipient_id, message, notification_date, is_read, notification_type) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    for n in notifications:
        tid = user_ids[n[0]]
        cursor.execute(notif_insert, (tid, n[1], n[2], n[3], n[4]))
    conn.commit()
    print(f"  {len(notifications)} notification records inserted.")

    cursor.close()
    db.close()

    print("\n✓ Seed data inserted successfully!")
    print("\nDemo login credentials:")
    print("  Administrator  →  username: haso_admin      password: Admin1234!")
    print("  Manager        →  username: sarah_mgr       password: Manager123!")
    print("  Front Desk     →  username: james_fd        password: FrontDesk1!")
    print("  Finance Mgr    →  username: nina_fin        password: Finance123!")
    print("  Maintenance    →  username: marcus_maint    password: Maint1234!")
    print("  Tenant         →  username: oliver_t        password: Tenant123!")


if __name__ == "__main__":
    run_seed()
