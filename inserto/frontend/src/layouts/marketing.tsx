import { Link, Outlet } from "react-router-dom";
import { Logo } from "@/components/brand/logo";
import { buttonVariants } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

export function MarketingLayout() {
  const { user } = useAuth();
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-transparent bg-bg/80 backdrop-blur supports-[backdrop-filter]:bg-bg/70">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link to="/" aria-label="Inserto home"><Logo /></Link>
          <nav className="hidden items-center gap-7 text-sm text-fg-2 md:flex" aria-label="Marketing">
            <a href="/#features" className="hover:text-fg">Features</a>
            <a href="/#how" className="hover:text-fg">How it works</a>
            <a href="/#method" className="hover:text-fg">Methodology</a>
            <a href="/#faq" className="hover:text-fg">FAQ</a>
          </nav>
          <div className="flex items-center gap-2">
            {user ? (
              <Link to="/app" className={buttonVariants({ size: "sm" })}>Open dashboard</Link>
            ) : (
              <>
                <Link to="/login" className={cn(buttonVariants({ variant: "ghost", size: "sm" }), "hidden sm:inline-flex")}>Sign in</Link>
                <Link to="/register" className={buttonVariants({ size: "sm" })}>Get started</Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1"><Outlet /></main>
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-10 text-sm text-fg-3 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="flex items-center gap-3"><Logo className="text-fg" /><span>Resume intelligence, explained.</span></div>
          <div className="flex items-center gap-5">
            <a href="/#method" className="hover:text-fg">Methodology</a>
            <a href="/#faq" className="hover:text-fg">Privacy</a>
            <a href="/api/docs" className="hover:text-fg">API</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
