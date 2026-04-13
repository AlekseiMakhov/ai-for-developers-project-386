from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.user import CamelModel


class TimeRange(CamelModel):
    start: str  # "09:00"
    end: str    # "17:00"


class WeeklyAvailability(CamelModel):
    monday: list[TimeRange] = []
    tuesday: list[TimeRange] = []
    wednesday: list[TimeRange] = []
    thursday: list[TimeRange] = []
    friday: list[TimeRange] = []
    saturday: list[TimeRange] = []
    sunday: list[TimeRange] = []


class ScheduleCreate(CamelModel):
    name: str
    description: str | None = None
    duration: int
    buffer_before: int = 0
    buffer_after: int = 0
    availability: WeeklyAvailability
    timezone: str = "UTC"
    is_active: bool = True
    color: str | None = None
    slug: str


class ScheduleUpdate(CamelModel):
    name: str | None = None
    description: str | None = None
    duration: int | None = None
    buffer_before: int | None = None
    buffer_after: int | None = None
    availability: WeeklyAvailability | None = None
    timezone: str | None = None
    is_active: bool | None = None
    color: str | None = None
    slug: str | None = None


class ScheduleResponse(CamelModel):
    id: str
    user_id: str
    name: str
    description: str | None = None
    duration: int
    buffer_before: int
    buffer_after: int
    availability: WeeklyAvailability
    timezone: str
    is_active: bool
    color: str | None = None
    slug: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
