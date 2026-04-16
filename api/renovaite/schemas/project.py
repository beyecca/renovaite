from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreateIn(BaseModel):
    name: str
    project_type: str
    description: str
    budget: float | None = None
    target_date: date | None = None


class ProjectUpdateIn(BaseModel):
    name: str | None = None
    project_type: str | None = None
    description: str | None = None
    budget: float | None = None
    target_date: date | None = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    project_type: str
    description: str
    budget: float | None
    target_date: date | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
