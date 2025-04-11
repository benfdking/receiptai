from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Address(BaseModel):
    country: str
    state: str
    city: str
    postal_code: str
    timezone: str
    coordinates: Coordinates


class Merchant(BaseModel):
    raw_descriptor: str
    mcc: str
    country: str


class OriginalAmount(BaseModel):
    amount: int
    currency: str


class BillingAmount(BaseModel):
    amount: int
    currency: str


class BudgetAmount(BaseModel):
    amount: int
    currency: str


class UsdEquivalentAmount(BaseModel):
    amount: int
    currency: str


class PurchasedAmount(BaseModel):
    amount: int
    currency: str


class PendingReviewer(BaseModel):
    id: str
    first_name: str
    last_name: str


class Reviewer(BaseModel):
    id: str
    first_name: str
    last_name: str


class ApprovalStep(BaseModel):
    pending_reviewers: Optional[List[PendingReviewer]] = None
    status: str
    reviewer: Optional[Reviewer] = None
    resolved_at: Optional[str] = None


class Review(BaseModel):
    compliance_status: str
    approval_steps: Optional[List[ApprovalStep]] = None


class Receipt(BaseModel):
    id: str
    download_uris: Optional[List[str]] = None


class Item(BaseModel):
    id: str
    address: Address
    updated_at: str
    category: str
    merchant_id: str
    merchant: Merchant
    budget_id: str
    expense_type: str
    original_amount: OriginalAmount
    billing_amount: BillingAmount
    budget_amount: BudgetAmount
    usd_equivalent_amount: UsdEquivalentAmount
    purchased_at: str
    status: str
    payment_status: str
    spending_entity_id: str
    vendor_id: str
    payment_posted_at: Optional[str] = None
    purchased_amount: Optional[PurchasedAmount] = None
    billing_entity_id: Optional[str] = None
    integration_spending_entity_id: Optional[str] = None
    integration_billing_entity_id: Optional[str] = None
    review: Optional[Review] = None
    submitted_at: Optional[str] = None
    memo: Optional[str] = None
    receipts: Optional[List[Receipt]] = None
    approved_at: Optional[str] = None


class Model(BaseModel):
    items: Optional[List[Item]] = None
