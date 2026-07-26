import type { Metadata } from "next";
import type { ReactNode } from "react";
import "../src/app/globals.css";

export const metadata: Metadata = {
  title: "Challenge Omid",
  description: "Telegram challenge management system with FastAPI, aiogram, SQLAdmin, and APScheduler.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-white antialiased">{children}</body>
    </html>
  );
}
