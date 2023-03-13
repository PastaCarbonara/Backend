from pydantic import BaseModel, Field


class JudgementSchema(BaseModel):
    like: bool = Field(..., description="Tag ID")

    class Config:
        orm_mode = True
