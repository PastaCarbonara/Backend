import json
from fastapi import Request

from core.helpers.hashids import decode_single


class HashIdDependency:
    def __init__(self, body_params: list[str], query_params: list[str]) -> None:
        self.body_params = body_params
        self.query_params = query_params

    async def __call__(self, request: Request):
        body = request.json()
        query = request.path_params

        for param in self.body_params:
            if param not in body:
                continue
            
            body[param] = self.decode(body[param])

        for param in self.query_params:
            if param not in query:
                continue
            
            query[param] = self.decode(query[param])

        body = json.dumps(body, indent=2).encode("utf-8")

        request.body = body
        request.path_params = query

    def decode(value):
        return decode_single(value)
