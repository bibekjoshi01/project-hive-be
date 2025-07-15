from pydantic import EmailStr, Field

from app.utils.casing import CamelBaseModel


class NewsletterSubscribePayload(CamelBaseModel):
    email: EmailStr


class ContactPayload(CamelBaseModel):
    full_name: str = Field(..., max_length=120)
    email: EmailStr
    phone_no: str | None = Field(None, max_length=20)
    subject: str | None = Field(None, max_length=200)
    message: str = Field(..., max_length=4000)


class StatsOut(CamelBaseModel):
    departments: int
    categories: int
    batches: int
    projects: int
