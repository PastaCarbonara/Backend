import json
from fastapi import Request

from core.helpers.hashid import decode_single


async def decode_path_id(hashed_id: int):
    return decode_single(hashed_id)


