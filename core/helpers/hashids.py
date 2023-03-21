import os
from hashids import Hashids

from core.exceptions.hashids import IncorrectHashIDException


salt = os.getenv('HASH_SALT')
min_length = int(os.getenv('HASH_MIN_LEN'))

hashids = Hashids(salt=salt, min_length=min_length)


def encode(id):
    """Hashids encode function"""
    return hashids.encode(id)


def decode(hashed_ids):
    """Hashids decode function"""
    try:
        return hashids.decode(hashed_ids)

    except Exception:
        raise IncorrectHashIDException
    
        
def decode_single(hashed_ids) -> int:
    """Decode, return single ID"""
    real_ids = ()

    real_ids = decode(hashed_ids)
    
    if len(real_ids) < 1:
        raise IncorrectHashIDException
        
    return real_ids[0]


def check_id(hashed_ids, func):
    """Check if the id returns a value from the provided function"""
    real_id = None
    try:
        real_id = decode_single(hashed_ids)
    
    except IncorrectHashIDException:
        return False
    
    else:
        obj = func(real_id)
        if not obj:
            return False
        
        return obj
