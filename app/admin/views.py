from hashlib import sha256

from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session
from aiohttp.web_exceptions import HTTPForbidden

from app.admin.schemes import AdminLoginSchema, AdminResponseSchema, AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["admin"], summary="create admin")
    @request_schema(AdminLoginSchema)
    @response_schema(AdminResponseSchema, 200)
    async def post(self):
        email = self.data['email']
        password = sha256(self.data['password'].encode()).hexdigest()
        admin = await self.store.admins.get_by_email(email)
        if admin is None:
            raise HTTPForbidden
        if admin.password != password:
            raise HTTPForbidden
        session = await new_session(request=self.request)
        session['email'] = email
        session['password'] = password
        return json_response(AdminSchema().dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["admin"], summary="current admin")
    @response_schema(AdminResponseSchema, 200)
    async def get(self):
        return json_response(AdminResponseSchema().dump(self.request.admin))
