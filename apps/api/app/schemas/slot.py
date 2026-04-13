from datetime import datetime

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.user import CamelModel


class SlotResponse(CamelModel):
    id: str
    schedule_id: str
    start_at: datetime
    end_at: datetime
    status: str

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
