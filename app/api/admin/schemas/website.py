from app.utils.casing import CamelBaseModel
from typing import List


class ContactResponse(CamelBaseModel):
    id: int
    full_name: str
    email: str
    phone_no: str
    subject: str
    message: str
    created_at: str


class ContactList(CamelBaseModel):
    count: int
    results: List[ContactResponse]


class ContactSummary(CamelBaseModel):
    total: int
    new: int


class ProjectSummary(CamelBaseModel):
    total: int
    pending: int
    accepted: int
    rejected: int
    success_rate: float


class DashboardSummaryResponse(CamelBaseModel):
    contact_requests: ContactSummary
    projects: ProjectSummary
