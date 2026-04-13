from datetime import datetime

from pydantic import ConfigDict, EmailStr
from pydantic.alias_generators import to_camel

from app.schemas.user import CamelModel


class BookingCreate(CamelModel):
    slot_id: str
    guest_name: str
    guest_email: EmailStr
    guest_note: str | None = None


class BookingResponse(CamelModel):
    id: str
    schedule_id: str
    slot_id: str
    guest_name: str
    guest_email: str
    guest_note: str | None = None
    status: str
    confirmation_token: str
    cancel_token: str
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
