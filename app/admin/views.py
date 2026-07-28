from __future__ import annotations

from fastapi import FastAPI
from sqladmin import Admin, ModelView

from app.admin.auth import AdminAuth
from app.admin.dashboard import DashboardView
from app.core.config import get_settings
from app.database.models.challenge import Challenge
from app.database.models.submission import Submission
from app.database.models.user import User
from app.database.session import async_engine, async_session_factory


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"

    column_list = [
        User.id,
        User.telegram_id,
        User.name,
        User.phone,
        User.status,
        User.created_at,
    ]

    column_searchable_list = [
        User.name,
        User.phone,
        User.status,
    ]

    column_sortable_list = [
        User.id,
        User.telegram_id,
        User.created_at,
    ]

    form_columns = [
        User.telegram_id,
        User.name,
        User.phone,
        User.status,
    ]

    page_size = 50
    page_size_options = [25, 50, 100, 200]


class ChallengeAdmin(ModelView, model=Challenge):
    name = "Challenge"
    name_plural = "Challenges"
    icon = "fa-solid fa-calendar-check"

    column_list = [
        Challenge.id,
        Challenge.day,
        Challenge.title,
        Challenge.send_time,
        Challenge.deadline,
        Challenge.is_active,
        Challenge.sent_at,
        Challenge.created_at,
    ]

    column_searchable_list = [
        Challenge.title,
        Challenge.description,
    ]

    column_sortable_list = [
        Challenge.day,
        Challenge.send_time,
        Challenge.deadline,
        Challenge.created_at,
    ]

    form_columns = [
        Challenge.day,
        Challenge.title,
        Challenge.description,
        Challenge.send_time,
        Challenge.deadline,
        Challenge.is_active,
        Challenge.sent_at,
    ]

    page_size = 50
    page_size_options = [25, 50, 100]


class SubmissionAdmin(ModelView, model=Submission):
    name = "Submission"
    name_plural = "Submissions"
    icon = "fa-solid fa-inbox"

    column_list = [
        Submission.id,
        Submission.user,
        Submission.challenge,
        Submission.answer,
        Submission.submitted_at,
        Submission.is_late,
    ]

    column_searchable_list = [
        Submission.answer,
    ]

    column_sortable_list = [
        Submission.id,
        Submission.submitted_at,
        Submission.is_late,
    ]

    form_columns = [
        Submission.user,
        Submission.challenge,
        Submission.answer,
        Submission.submitted_at,
        Submission.is_late,
    ]

    can_create = True
    can_edit = True
    can_delete = True

    page_size = 50
    page_size_options = [25, 50, 100, 200]


def setup_admin(app: FastAPI) -> Admin:
    settings = get_settings()

    authentication_backend = AdminAuth(
        secret_key=settings.secret_key
    )

    admin = Admin(
        app=app,
        engine=async_engine,
        session_maker=async_session_factory,
        title=f"{settings.app_name} Admin",
        authentication_backend=authentication_backend,
        base_url="/admin",
        statics_dir="/app/.venv/lib/python3.13/site-packages/sqladmin/statics",
    )

    admin.add_view(DashboardView)
    admin.add_view(UserAdmin)
    admin.add_view(ChallengeAdmin)
    admin.add_view(SubmissionAdmin)

    return admin