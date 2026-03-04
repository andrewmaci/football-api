from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BaseEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    last_changed_date: datetime
