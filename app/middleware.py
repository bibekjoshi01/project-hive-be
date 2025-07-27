import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


def snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(word.title() for word in parts[1:])


def keys_to_camel(obj):
    if isinstance(obj, list):
        return [keys_to_camel(i) for i in obj]
    elif isinstance(obj, dict):
        return {snake_to_camel(k): keys_to_camel(v) for k, v in obj.items()}
    else:
        return obj


class CamelCaseResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if "application/json" not in response.headers.get("content-type", ""):
            return response  # Only process JSON responses

        # Read and join the response body parts
        response_body = [section async for section in response.body_iterator]
        body = b"".join(response_body).decode()

        if not body:
            return response

        # Parse JSON, convert keys, and re-encode
        data = json.loads(body)
        new_data = keys_to_camel(data)
        new_body = json.dumps(new_data).encode("utf-8")

        headers = dict(response.headers)
        headers.pop("content-length", None)  # Remove old content-length header

        return Response(
            content=new_body,
            status_code=response.status_code,
            headers=headers,
            media_type="application/json",
        )
