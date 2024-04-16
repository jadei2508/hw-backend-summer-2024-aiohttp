from aiohttp.web_exceptions import HTTPUnauthorized

from app.web.app import Request


class AuthRequiredMixin:
    def __init__(self, request: Request) -> None:
        super().__init__(request)
        if request.admin is None:
            raise HTTPUnauthorized
