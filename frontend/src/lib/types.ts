/**
 * These mirror what the API actually returns: whatever to_dict() produces,
 * which is the SELECT aliases from src/database/*_models.py.
 *
 * Verified against the SQL directly — several of these are NOT the snake_case
 * you'd expect (leaseID, tenantID, assignedStaff_id), because the original
 * schema mixes conventions. Don't "tidy" them or the fields render blank.
 *
 * Note also that list endpoints return extra JOINed display fields
 * (tenant_name, apartment_number, location) that the single-record endpoints
 * don't, which is why those are optional.
 */

export type Role =
  | "Administrator"
  | "Manager"
  | "Front Desk Staff"
  | "Finance Manager"
  | "Maintenance Staff"
  | "Tenant";

export type CurrentUser = {
  user_id: number;
  name: string;
  role: Role;
  location_id: number | null;
  location_name: string | null;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: CurrentUser;
};

/** GET /tenants — list_tenants() copies user_id into tenant_id.
 *  GET /tenants/{id} returns a User row, which has no tenant_id. */
export type Tenant = {
  user_id: number;
  tenant_id?: number;
  username?: string;
  fname: string;
  lname: string;
  email: string;
  phone_number: string;
  date_of_birth: string;
  occupation: string | null;
  ni_number: string | null;
  references: string | null;
};

/** GET /users. `password` appears as null because User.__init__ defines it and
 *  to_dict() returns everything on the instance — the hash is never selected. */
export type User = {
  user_id: number;
  username: string;
  fname: string;
  lname: string;
  email: string;
  phone_number: string;
  date_of_birth: string;
  role: Role;
  occupation: string | null;
  ni_number: string | null;
  references: string | null;
  password?: null;
};

/** GET /staff — note user_role (the account role) and staff_role (the job
 *  title) are two different columns aliased apart in the SQL. */
export type StaffMember = {
  user_id: number;
  employee_id: number;
  fname: string;
  lname: string;
  email: string;
  phone_number: string;
  date_of_birth: string;
  user_role: Role;
  staff_role: string;
  salary: number | null;
  start_date: string | null;
  location_id: number | null;
  location: string | null;
};

export type Apartment = {
  apartment_id: number;
  apartment_number: string;
  location_id: number;
  type: string;
  monthly_rent: number;
  number_of_rooms: number;
  square_footage: number;
  occupation_status: string;
};

export type Location = {
  location_id: number;
  city: string;
  manager: string;
};

/** GET /leases uses camel-ish IDs from the original schema. */
export type Lease = {
  leaseID: number;
  tenantID?: number;
  apartmentID?: number;
  start_date: string;
  end_date: string;
  monthly_rent: number;
  status: string;
  deposit_amount?: number;
  lease_term_months?: number;
  termination_date?: string | null;
  early_termination_notice?: string | null;
  termination_penalty_percent?: number | null;
  // JOINed display fields, present on the full list only
  tenant_name?: string;
  apartment_number?: string;
  location?: string;
};

/** GET /invoices — the FK is leaseID, not lease_id. */
export type Invoice = {
  invoiceID: number;
  leaseID: number;
  amount: number;
  due_date: string;
  issue_date: string;
  description: string | null;
  status: string;
  tenant_id?: number;
  tenant_name?: string;
  apartment_number?: string;
  location?: string;
};

export type Payment = {
  payment_id: number;
  invoice_id: number;
  amount_paid: number;
  payment_date: string;
  payment_method: string;
  transaction_ref: string;
  receipt_number: string | null;
};

export type Complaint = {
  complaint_id: number;
  tenant_id: number;
  subject: string;
  description: string;
  status: string;
  date_filed: string;
  tenant_name?: string;
  location?: string;
};

export type ComplaintStats = Record<string, number>;

export type Enquiry = {
  enquiry_id: number;
  tenant_id: number | null;
  tenant_name: string;
  enquiry_details: string;
  handled_by: string;
  date_logged: string;
};

/** GET /maintenance — assignedStaff_id keeps the original schema's casing.
 *  The list query aliases the reporting tenant as tenant_id. */
export type MaintenanceRequest = {
  request_id: number;
  apartment_id: number;
  description: string;
  priority: string;
  category: string;
  status: string;
  report_date: string | null;
  scheduled_date: string | null;
  resolved_date: string | null;
  cost: number | null;
  assignedStaff_id: number | null;
  tenant_id?: number;
  reportedByTenant_id?: number;
  tenant_name?: string;
  staff_name?: string;
  apartment_number?: string;
  location?: string;
};

export type MaintenanceLog = {
  log_id: number;
  request_id: number;
  description: string;
  start_time: string | null;
  end_time: string | null;
  parts_used: string | null;
  cost_breakdown: string | null;
  technician_notes: string | null;
};

/** GET /maintenance/staff returns a trimmed shape, not full StaffMember. */
export type MaintenanceStaff = {
  user_id: number;
  fname?: string;
  lname?: string;
  name?: string;
  role?: string;
};
