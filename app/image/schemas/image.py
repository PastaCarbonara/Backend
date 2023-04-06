from pydantic import BaseModel, Field


class ImageSchema(BaseModel):
    filename: str = Field(..., description="Filename")
    file_url: str = Field(..., description="Public url to retrieve file from")

    class Config:
        orm_mode = True
