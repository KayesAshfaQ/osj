"""Waitlist HTTP request/response contract."""

from pydantic import BaseModel, EmailStr


class WaitlistRequest(BaseModel):
    email: EmailStr


class WaitlistResponse(BaseModel):
    message: str
    email: str
