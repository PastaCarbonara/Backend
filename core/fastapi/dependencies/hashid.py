import json
from fastapi import Path, Request

from core.helpers.hashid import decode_single


async def decode_path_id(hashed_id: str):
    return decode_single(hashed_id)

async def get_group_id(group_id: str = Path(...)):
    return decode_single(group_id)

async def get_session_id(session_id: str = Path(...)):
    return decode_single(session_id)
