import {
  Briefcase, ChevronsUpDown, FileText, GitCompareArrows, History, LayoutDashboard, LogOut, Menu,
  Moon, Plus, Settings, Sparkles, Sun, UserRound, X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Navigate, Outlet, useLocation } from "react-router-dom";
import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/misc";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { cn, initials } from "@/lib/utils";

const NAV = [
  { group: "Workspace", items: [
    { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
    { to: "/app/new", label: "New analysis", icon: Plus },
    { to: "/app/match", label: "Job matcher", icon: Briefcase },
    { to: "/app/resumes", label: "Resumes", icon: FileText },
  ] },
  { group: "Insights", items: [
    { to: "/app/history", label: "History", icon: History },
    { to: "/app/compare", label: "Compare", icon: GitCompareArrows },
    { to: "/app/studio", label: "Improvement studio", icon: Sparkles },
  ] },
];

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4" aria-label="Main">
      {NAV.map((g) => (
        <div key={g.group}>
          <div className="mb-1.5 px-2.5 text-[11px] font-medium uppercase tracking-wider text-fg-3">{g.group}</div>
          <ul className="space-y-0.5">
            {g.items.map((it) => (
              <li key={it.to}>
                <NavLink to={it.to} end={it.end} onClick={onNavigate}
                  className={({ isActive }) => cn(
                    "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors",
                    isActive ? "bg-surface-2 font-medium text-fg" : "text-fg-2 hover:bg-surface-2/60 hover:text-fg",
                  )}>
                  <it.icon className="size-4" aria-hidden />
                  {it.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

function UserMenu() {
  const { user, signOut } = useAuth();
  const { resolved, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const close = (e: MouseEvent) => ref.current && !ref.current.contains(e.target as Node) && setOpen(false);
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);
  if (!user) return null;
  const item = "flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-sm text-fg-2 hover:bg-surface-2 hover:text-fg";
  return (
    <div ref={ref} className="relative border-t border-border p-3">
      {open && (
        <div className="absolute inset-x-3 bottom-[calc(100%-4px)] z-20 animate-fade-up rounded-xl border border-border bg-surface p-1 shadow-pop" role="menu">
          <Link to="/app/profile" className={item} onClick={() => setOpen(false)} role="menuitem"><UserRound className="size-4" />Profile</Link>
          <Link to="/app/settings" className={item} onClick={() => setOpen(false)} role="menuitem"><Settings className="size-4" />Settings</Link>
          <button className={item} onClick={() => setTheme(resolved === "dark" ? "light" : "dark")} role="menuitem">
            {resolved === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            {resolved === "dark" ? "Light mode" : "Dark mode"}
          </button>
          <div className="my-1 h-px bg-border" />
          <button className={item} onClick={signOut} role="menuitem"><LogOut className="size-4" />Sign out</button>
        </div>
      )}
      <button onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-haspopup="menu"
        className="flex w-full items-center gap-2.5 rounded-lg p-1.5 text-left hover:bg-surface-2">
        <span className="grid size-8 shrink-0 place-items-center rounded-full bg-accent-soft text-xs font-semibold text-accent-fg">{initials(user.name)}</span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm font-medium">{user.name}</span>
          <span className="block truncate text-xs text-fg-3">{user.email}</span>
        </span>
        <ChevronsUpDown className="size-4 text-fg-3" aria-hidden />
      </button>
    </div>
  );
}

export function AppShell() {
  const { user, loading } = useAuth();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  useEffect(() => setMobileOpen(false), [location.pathname]);

  if (loading) {
    return (
      <div className="flex min-h-screen">
        <div className="hidden w-64 border-r border-border p-4 lg:block"><Skeleton className="h-7 w-28" /></div>
        <div className="flex-1 p-10"><Skeleton className="h-8 w-64" /><Skeleton className="mt-6 h-48 w-full" /></div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;

  return (
    <div className="min-h-screen lg:flex">
      <div className="hidden w-64 shrink-0 border-r border-border bg-surface lg:block">
        <aside className="sticky top-0 flex h-screen flex-col">
          <div className="flex h-16 items-center px-5"><Link to="/app" aria-label="Inserto home"><Logo /></Link></div>
          <NavItems />
          <UserMenu />
        </aside>
      </div>

      <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-surface/85 px-4 backdrop-blur lg:hidden">
        <Link to="/app" aria-label="Inserto home"><Logo /></Link>
        <Button variant="ghost" size="icon" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Menu /></Button>
      </header>
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setMobileOpen(false)} aria-hidden />
          <aside className="absolute inset-y-0 left-0 flex w-72 animate-fade-up flex-col bg-surface shadow-pop">
            <div className="flex h-14 items-center justify-between px-4">
              <Logo />
              <Button variant="ghost" size="icon" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X /></Button>
            </div>
            <NavItems onNavigate={() => setMobileOpen(false)} />
            <UserMenu />
          </aside>
        </div>
      )}

      <main className="min-w-0 flex-1">
        <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-10 lg:py-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

