from __future__ import annotations

from html import escape

from sqladmin import BaseView, expose
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.core.config import get_settings
from app.database.repositories.challenge_repository import ChallengeRepository
from app.database.repositories.submission_repository import SubmissionRepository
from app.database.repositories.user_repository import UserRepository
from app.database.session import async_session_factory
from app.services.metrics_service import MetricsService


class DashboardView(BaseView):
    name = "Dashboard"
    icon = "fa-solid fa-chart-line"

    @expose("/dashboard", methods=["GET"])
    async def dashboard(self, request: Request) -> HTMLResponse:
        settings = get_settings()
        async with async_session_factory() as session:
            users = UserRepository(session)
            challenges = ChallengeRepository(session)
            submissions = SubmissionRepository(session)
            metrics_service = MetricsService(
                users=users,
                challenges=challenges,
                submissions=submissions,
                max_users=settings.max_users,
                timezone_name=settings.timezone,
            )
            metrics = await metrics_service.get_dashboard_metrics()

        active_day = metrics.active_challenge_day if metrics.active_challenge_day is not None else "Not started"
        html = f"""
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>{escape(settings.app_name)} Admin Dashboard</title>
            <style>
              :root {{
                --bg: #f6f8fb;
                --panel: #ffffff;
                --ink: #0f172a;
                --muted: #64748b;
                --brand: #b99738;
                --brand-dark: #111827;
                --border: #e2e8f0;
                --danger: #dc2626;
              }}
              * {{ box-sizing: border-box; }}
              body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--ink); }}
              .shell {{ min-height: 100vh; padding: 32px; }}
              .hero {{ background: linear-gradient(135deg, #0f172a, #020617); color: white; border-radius: 28px; padding: 32px; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22); }}
              .eyebrow {{ color: #f8e7a0; text-transform: uppercase; letter-spacing: .18em; font-size: 12px; font-weight: 700; }}
              h1 {{ margin: 12px 0 8px; font-size: clamp(32px, 5vw, 56px); line-height: 1; }}
              .subtitle {{ color: #cbd5e1; max-width: 760px; font-size: 17px; line-height: 1.7; }}
              .grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 18px; margin-top: 24px; }}
              .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 22px; padding: 22px; box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08); }}
              .metric-label {{ color: var(--muted); font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }}
              .metric-value {{ margin-top: 10px; font-size: 34px; font-weight: 800; }}
              .metric-value.danger {{ color: var(--danger); }}
              .actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 24px; }}
              .button {{ display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0 18px; border-radius: 999px; color: white; background: var(--brand-dark); text-decoration: none; font-weight: 700; }}
              .button.gold {{ background: linear-gradient(135deg, #d9bd61, #a97914); }}
              @media (max-width: 1100px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
              @media (max-width: 640px) {{ .shell {{ padding: 18px; }} .grid {{ grid-template-columns: 1fr; }} }}
            </style>
          </head>
          <body>
            <main class="shell">
              <section class="hero">
                <div class="eyebrow">Challenge Omid</div>
                <h1>Admin Dashboard</h1>
                <p class="subtitle">Operational overview for registrations, active challenge delivery, submissions, capacity, and late-participant monitoring.</p>
              </section>

              <section class="grid" aria-label="Dashboard metrics">
                <article class="card"><div class="metric-label">Total users</div><div class="metric-value">{metrics.total_users}</div></article>
                <article class="card"><div class="metric-label">Remaining capacity</div><div class="metric-value">{metrics.remaining_capacity}</div></article>
                <article class="card"><div class="metric-label">Active challenge day</div><div class="metric-value">{active_day}</div></article>
                <article class="card"><div class="metric-label">Today's submissions</div><div class="metric-value">{metrics.today_submissions}</div></article>
                <article class="card"><div class="metric-label">Late users count</div><div class="metric-value danger">{metrics.late_users_count}</div></article>
              </section>

              <nav class="actions" aria-label="Admin shortcuts">
                <a class="button gold" href="/admin/challenge/list">Manage challenges</a>
                <a class="button" href="/admin/user/list">Manage users</a>
                <a class="button" href="/admin/submission/list">Review submissions</a>
              </nav>
            </main>
          </body>
        </html>
        """
        return HTMLResponse(html)
