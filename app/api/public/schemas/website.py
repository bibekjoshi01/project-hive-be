from pydantic import BaseModel, EmailStr, Field
from typing import Annotated


class NewsletterSubscribePayload(BaseModel):
    email: EmailStr


class ContactPayload(BaseModel):
    full_name: str = Field(..., max_length=120)
    email: EmailStr
    phone_no: str | None = Field(None, max_length=20)
    subject: str | None = Field(None, max_length=200)
    message: str = Field(..., max_length=4000)
