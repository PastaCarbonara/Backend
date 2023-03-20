import os
from hashids import Hashids

from core.exceptions.hashids import IncorrectHashIDException


salt = os.getenv('HASH_SALT')
min_length = os.getenv('HASH_MIN_LEN')

hashids = Hashids(salt=salt, min_length=min_length)


def encode(id):
    return hashids.encode(id)


def decode(hashed_ids):
    try:
        return hashids.decode(hashed_ids)

    except:
        raise IncorrectHashIDException
    
        
def decode_single(hashed_ids):
    real_ids = ()

    real_ids = decode(hashed_ids)
    
    if len(real_ids) < 1:
        raise IncorrectHashIDException
        
    return real_ids[0]


def check_id(hashed_ids, func):
    try:
        real_ids = decode(hashed_ids)
    
    except:
        return False
    
    finally:
        if len(real_ids) < 1:
            return False

        obj = func(real_ids[0])
        if not obj:
            return False
        
        return obj
