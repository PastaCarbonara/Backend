from pydantic import BaseModel, Field


class FileUrls(BaseModel):
    small: str = Field(..., description="Public url to retrieve small file from")
    medium: str = Field(..., description="Public url to retrieve medium file from")
    large: str = Field(..., description="Public url to retrieve large file from")
    thumbnail: str = Field(
        ..., description="Public url to retrieve thumbnail file from"
    )


class ImageSchema(BaseModel):
    filename: str = Field(..., description="Filename")
    file_url: str = Field(..., description="Public url to retrieve file from")
    urls: FileUrls = Field(..., description="Public urls to retrieve files from")

    class Config:
        orm_mode = True
