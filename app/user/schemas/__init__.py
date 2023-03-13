from .user import *


class ExceptionResponseSchema(BaseModel):
    error_code: str
    message: str
