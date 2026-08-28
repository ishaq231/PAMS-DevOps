/**
 * These mirror what the API actually returns, which is whatever the model
 * classes' to_dict() produces. Field names come from the SQL SELECT aliases in
 * src/database/*_models.py, NOT from the PyQt6 form field labels.
 *
 * Anything marked "verify" hasn't been confirmed against a live response yet.
 */

export type Role =
  | "Administrator"
  | "Manager"
  | "Front Desk Staff"
  | "Finance Manager"
  | "Maintenance Staff"
  | "Tenant";

/** Decoded from the JWT / returned by GET /me. */
export type CurrentUser = {
  user_id: number;
  name: string;
  role: Role;
  location_id: number | null;
  location_name: string | null;
};

/** POST /login response shape. */
export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: CurrentUser;
};

/** GET /tenants — note list_tenants() copies user_id into tenant_id, so both
 *  are present here. GET /tenants/{id} returns a User row and does NOT include
 *  tenant_id, which is why it's optional. */
export type Tenant = {
  user_id: number;
  tenant_id?: number;
  fname: string;
  lname: string;
  email: string;
  phone_number: string;
  date_of_birth: string;
  occupation: string | null;
  ni_number: string | null;
  references: string | null;
};

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
};

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

export type Lease = {
  leaseID: number;
  tenant_id: number;
  apartment_id: number;
  start_date: string;
  end_date: string;
  monthly_rent: number;
  deposit: number;
  term_months: number;
  status: string;
};

export type Invoice = {
  invoiceID: number;
  lease_id: number;
  amount: number;
  due_date: string;
  issue_date: string;
  description: string | null;
  status: string;
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

export type MaintenanceRequest = {
  request_id: number;
  apartment_id: number;
  tenant_id: number;
  description: string;
  priority: string;
  category: string;
  status: string;
  assigned_staff_id: number | null;
  scheduled_date: string | null;
  cost: number | null;
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
