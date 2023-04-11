"""Tag schemas
"""

from pydantic import BaseModel, Field


class TagSchema(BaseModel):
    """
    A Pydantic model representing a tag with an ID and a name.

    Parameters
    ----------
    id : int
        The ID of the tag.
    name : str
        The name of the tag.

    Attributes
    ----------
    id : int
        The ID of the tag.
    name : str
        The name of the tag.

    Config
    ------
    orm_mode : bool
        If True, this Pydantic model can be used to extract data directly from the ORM.
    """

    id: int = Field(..., description="ID")
    name: str = Field(..., description="tag name")

    class Config:
        orm_mode = True


class CreateTagSchema(BaseModel):
    """
    A Pydantic model representing the data needed to create a tag.

    Parameters
    ----------
    name : str
        The name of the tag.

    Attributes
    ----------
    name : str
        The name of the tag.
    """

    name: str
