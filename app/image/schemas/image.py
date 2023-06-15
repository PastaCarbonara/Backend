from pydantic import BaseModel, Field


class FileUrls(BaseModel):
    """Public urls to retrieve files from"""

    xs: str = Field(..., description="Public url to retrieve xs file from")
    sm: str = Field(..., description="Public url to retrieve sm file from")
    md: str = Field(..., description="Public url to retrieve md file from")
    lg: str = Field(..., description="Public url to retrieve lg file from")
    thumbnail: str = Field(
        ..., description="Public url to retrieve thumbnail file from"
    )


class ImageSchema(BaseModel):
    filename: str = Field(..., description="Filename")
    urls: FileUrls = Field(..., description="Public urls to retrieve files from")

    class Config:
        orm_mode = True
