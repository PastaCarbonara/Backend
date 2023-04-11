from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, validator, HttpUrl, PostgresDsn


def decode(value): return f"{value}hash"


class HashId(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, int):
            raise TypeError('integer required')
        
        return f"{v} hash"

class Response(BaseModel):
    id: int | HashId
    name: str


class Request:
    id: int


group = Response(
    id=1,
    name="harry"
)
# print("frick")
print(group)
print(group.id)