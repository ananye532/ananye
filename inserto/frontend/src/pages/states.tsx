import { AlertTriangle, Compass, RotateCw } from "lucide-react";
import { Component, type ErrorInfo, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { Logo } from "@/components/brand/logo";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/misc";
import { ApiError } from "@/lib/api";

export function ErrorPanel({ error, onRetry, title = "Couldn’t load this page" }: { error: unknown; onRetry?: () => void; title?: string }) {
  const message = error instanceof ApiError ? error.message : "An unexpected error occurred.";
  return (
    <Card>
      <EmptyState icon={<AlertTriangle />} title={title} description={message}
        action={onRetry && <Button variant="secondary" onClick={onRetry}><RotateCw />Try again</Button>} />
    </Card>
  );
}

export function NotFound({ inApp = false }: { inApp?: boolean }) {
  const body = (
    <EmptyState icon={<Compass />} title="Page not found" description="The page you’re looking for doesn’t exist or was deleted."
      action={<Link to={inApp ? "/app" : "/"} className={buttonVariants()}>{inApp ? "Back to dashboard" : "Go home"}</Link>} />
  );
  if (inApp) return <Card>{body}</Card>;
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <Link to="/" className="mb-10"><Logo /></Link>
      <div className="font-mono text-sm text-fg-3">404</div>
      {body}
    </div>
  );
}

export class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error(error, info.componentStack); }
  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="max-w-md text-center">
          <AlertTriangle className="mx-auto size-8 text-warn" aria-hidden />
          <h1 className="mt-4 text-xl font-semibold">Something went wrong</h1>
          <p className="mt-2 text-sm text-fg-2">An unexpected error interrupted the page. Reloading usually fixes it.</p>
          <Button className="mt-6" onClick={() => location.reload()}><RotateCw />Reload</Button>
        </div>
      </div>
    );
  }
}
