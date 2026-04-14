# Import all models here so Alembic can detect them
from app.models.schedule import Schedule
from app.models.slot import Slot
from app.models.user import User

__all__ = ["User", "Schedule", "Slot"]
