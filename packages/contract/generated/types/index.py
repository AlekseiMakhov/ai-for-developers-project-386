# Generated from TypeSpec — do not edit manually
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TimeRange(BaseModel):
    start: str
    end: str


class WeeklyAvailability(BaseModel):
    monday: Optional[list[TimeRange]] = None
    tuesday: Optional[list[TimeRange]] = None
    wednesday: Optional[list[TimeRange]] = None
    thursday: Optional[list[TimeRange]] = None
    friday: Optional[list[TimeRange]] = None
    saturday: Optional[list[TimeRange]] = None
    sunday: Optional[list[TimeRange]] = None


class SlotStatus(str, Enum):
    available = "available"
    booked = "booked"
    blocked = "blocked"


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class User(BaseModel):
    id: UUID
    email: str
    name: str
    timezone: str
    slug: str
    created_at: datetime


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    timezone: str
    slug: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class Schedule(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str] = None
    duration: int
    buffer_before: int
    buffer_after: int
    availability: WeeklyAvailability
    timezone: str
    is_active: bool
    color: Optional[str] = None
    slug: str


class ScheduleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int
    buffer_before: int = 0
    buffer_after: int = 0
    availability: WeeklyAvailability
    timezone: str
    is_active: bool = True
    color: Optional[str] = None
    slug: str


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    buffer_before: Optional[int] = None
    buffer_after: Optional[int] = None
    availability: Optional[WeeklyAvailability] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    color: Optional[str] = None
    slug: Optional[str] = None


class Slot(BaseModel):
    id: UUID
    schedule_id: UUID
    start_at: datetime
    end_at: datetime
    status: SlotStatus


class Booking(BaseModel):
    id: UUID
    schedule_id: UUID
    slot_id: UUID
    guest_name: str
    guest_email: str
    guest_note: Optional[str] = None
    status: BookingStatus
    confirmation_token: str
    cancel_token: str
    created_at: datetime


class BookingCreate(BaseModel):
    slot_id: UUID
    guest_name: str
    guest_email: str
    guest_note: Optional[str] = None


class PublicProfile(BaseModel):
    user: User
    schedules: list[Schedule]
