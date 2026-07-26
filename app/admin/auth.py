from __future__ import annotations

import hmac

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import get_settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))
        settings = get_settings()

        username_matches = hmac.compare_digest(username, settings.admin_username)
        password_matches = hmac.compare_digest(password, settings.admin_password)
        if username_matches and password_matches:
            request.session.update({"authenticated": True, "admin_username": username})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("authenticated"))
