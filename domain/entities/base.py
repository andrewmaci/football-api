from pydantic import BaseModel, ConfigDict
from datetime import date

class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    last_changed_date: date
