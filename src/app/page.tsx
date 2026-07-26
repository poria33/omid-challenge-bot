import { db } from "@/db";
import { sql } from "drizzle-orm";

export const dynamic = "force-dynamic";

const capabilities = [
  "Telegram onboarding with contact sharing",
  "Capacity-limited challenge registration",
  "APScheduler automatic daily delivery",
  "FastAPI + SQLAdmin professional operations panel",
  "Repository and service based backend architecture",
];

export default async function HomePage() {
  await db.execute(sql`select 1`);

  return (
    <main className="min-h-screen bg-[#050816] px-6 py-12 text-white">
      <section className="mx-auto flex min-h-[calc(100vh-6rem)] w-full max-w-6xl flex-col justify-center">
        <div className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-[0_32px_100px_rgba(0,0,0,0.35)] backdrop-blur md:p-12">
          <p className="text-sm font-semibold uppercase tracking-[0.35em] text-[#f4d77b]">Challenge Omid</p>
          <h1 className="mt-6 max-w-4xl text-4xl font-black leading-[0.95] tracking-tight md:text-7xl">
            Telegram Challenge Management System
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300">
            A production-ready Python backend has been generated in this repository with aiogram 3, FastAPI,
            SQLAdmin, SQLAlchemy 2, Alembic, APScheduler, and environment-based configuration.
          </p>

          <div className="mt-10 grid gap-4 md:grid-cols-5">
            {capabilities.map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-black/20 p-5 text-sm text-slate-200">
                <div className="mb-4 h-1.5 w-12 rounded-full bg-[#f4d77b]" />
                {item}
              </div>
            ))}
          </div>

          <div className="mt-10 flex flex-wrap gap-3 text-sm font-semibold">
            <span className="rounded-full bg-[#f4d77b] px-5 py-3 text-slate-950">FastAPI admin: /admin/dashboard</span>
            <span className="rounded-full border border-white/15 px-5 py-3 text-slate-200">Bot entrypoint: python -m app.bot.runner</span>
          </div>
        </div>
      </section>
    </main>
  );
}
