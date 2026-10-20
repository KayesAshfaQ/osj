"""Waitlist domain terms without HTTP or ORM dependencies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WaitlistSignup:
    email: str


class DuplicateEmail(Exception):
    """A normalized email address already exists in the waitlist."""
