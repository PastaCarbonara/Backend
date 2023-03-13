from pydantic import BaseModel, Field


class InstructionItemSchema(BaseModel):
    title: str | None = Field(None, description="Title of instruction, optional")
    description: str = Field(None, description="The full instruction")
    time: int | None = Field(None, description="Time needed in minutes, optional")

    class Config:
        orm_mode = True
