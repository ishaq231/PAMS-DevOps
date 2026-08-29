from . import db_path  # noqa: F401

from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from .auth import require_roles, require_staff_or_self
from pydantic import BaseModel as PydanticModel

from finance_models import Invoice
from finance_models import Payment 

router = APIRouter()


@router.get("/invoices")
def list_invoices(user: dict = Depends(require_roles("Administrator", "Manager", "Finance Manager"))):
    invoices = Invoice.get_all_invoices()
    return [i.to_dict() for i in invoices]


@router.get("/tenants/{tenant_id}/invoices")
def list_invoices_for_tenant(tenant_id: int, user: dict = Depends(require_staff_or_self("Administrator", "Manager", "Finance Manager"))):
    invoices = Invoice.get_invoices_for_tenant(tenant_id)
    return [i.to_dict() for i in invoices]


class InvoiceCreateRequest(PydanticModel):
    lease_id: int
    amount: float
    due_date: str
    issue_date: str
    description: Optional[str] = None


@router.post("/invoices", status_code=201)
def create_invoice(payload: InvoiceCreateRequest, user: dict = Depends(require_roles("Administrator", "Finance Manager"))):
    invoice_id = Invoice.create_invoice(
        lease_id=payload.lease_id,
        amount=payload.amount,
        due_date=payload.due_date,
        issue_date=payload.issue_date,
        description=payload.description,
    )
    if invoice_id is None:
        raise HTTPException(status_code=400, detail="Could not create invoice")
    return {"invoice_id": invoice_id}


class InvoiceUpdateRequest(PydanticModel):
    amount: Optional[float] = None
    due_date: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


@router.patch("/invoices/{invoice_id}")
def update_invoice(invoice_id: int, payload: InvoiceUpdateRequest, user: dict = Depends(require_roles("Administrator", "Finance Manager"))):
    updated = Invoice(invoiceID=invoice_id).update_invoice(
        amount=payload.amount,
        due_date=payload.due_date,
        description=payload.description,
        status=payload.status,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Nothing updated, check the ID and that at least one field was sent")
    return {"invoiceID": invoice_id, "updated": True}


@router.post("/invoices/{invoice_id}/mark-paid")
def mark_invoice_paid(invoice_id: int, user: dict = Depends(require_roles("Administrator", "Finance Manager"))):
    updated = Invoice(invoiceID=invoice_id).mark_invoice_paid()
    if not updated:
        raise HTTPException(status_code=400, detail="Could not mark invoice as paid")
    return {"invoiceID": invoice_id, "status": "Paid"}


@router.get("/payments")
def list_payments(user: dict = Depends(require_roles("Administrator", "Manager", "Finance Manager"))):
    payments = Payment.get_all_payments()
    return [p.to_dict() for p in payments]


@router.get("/tenants/{tenant_id}/payments")
def list_payments_for_tenant(tenant_id: int, user: dict = Depends(require_staff_or_self("Administrator", "Manager", "Finance Manager"))):
    payments = Payment.get_payments_for_tenant(tenant_id)
    return [p.to_dict() for p in payments]


class PaymentCreateRequest(PydanticModel):
    invoice_id: int
    amount_paid: float
    payment_date: str
    payment_method: str
    transaction_ref: str


@router.post("/payments", status_code=201)
def create_payment(payload: PaymentCreateRequest, user: dict = Depends(require_roles("Administrator", "Finance Manager"))):
    payment_id, receipt = Payment.create_payment(
        invoice_id=payload.invoice_id,
        amount_paid=payload.amount_paid,
        payment_date=payload.payment_date,
        payment_method=payload.payment_method,
        transaction_ref=payload.transaction_ref,
    )
    if payment_id is None:
        raise HTTPException(status_code=400, detail="Could not create payment")
    return {"payment_id": payment_id, "receipt_number": receipt}


class PaymentUpdateRequest(PydanticModel):
    amount_paid: Optional[float] = None
    payment_method: Optional[str] = None
    transaction_ref: Optional[str] = None
    payment_date: Optional[str] = None


@router.patch("/payments/{payment_id}")
def update_payment(payment_id: int, payload: PaymentUpdateRequest, user: dict = Depends(require_roles("Administrator", "Finance Manager"))):
    updated = Payment(payment_id=payment_id).update_payment(
        amount_paid=payload.amount_paid,
        payment_method=payload.payment_method,
        transaction_ref=payload.transaction_ref,
        payment_date=payload.payment_date,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Nothing updated, check the ID and that at least one field was sent")
    return {"payment_id": payment_id, "updated": True}