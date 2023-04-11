from core.helpers.hashid import decode, encode


class HashId(int):
    """Pydantic type for hashing integer"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, int):
            raise TypeError('integer required')
        
        return encode(v)
    

class DehashId(str):
    """Pydantic type for dehashing hash"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, int):
            raise TypeError('integer required')
        
        return decode(v)
        