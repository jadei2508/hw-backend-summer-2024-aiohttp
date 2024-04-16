import base64
import json
import typing

from aiohttp.web_exceptions import HTTPUnprocessableEntity, HTTPException, HTTPForbidden
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        return error_json_response(
            http_status=e.status,
            status=HTTP_ERROR_CODES[e.status],
            message=e.reason,
        )
    except Exception as e:
        return error_json_response(
            http_status=500,
            status=HTTP_ERROR_CODES[500],
            message=str(e)
        )


@middleware
async def auth_session_middleware(request: "Request", handler):
    session = await get_session(request)
    request.admin = None
    if not session.empty:
        email = session.get('email', None)
        password = session.get('password', None)
        if not email or not password:
            raise HTTPForbidden
        admin = await request.app.store.admins.get_by_email(email)
        if admin is None:
            raise HTTPForbidden
        if admin.password != password:
            raise HTTPForbidden
        request.admin = admin
    return await handler(request)


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
    print(app.config.session.key)
    print(base64.b64decode(app.config.session.key))
    app.middlewares.append(
        session_middleware(EncryptedCookieStorage(base64.b64decode(app.config.session.key)))
    )
    app.middlewares.append(auth_session_middleware)
