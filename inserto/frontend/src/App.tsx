import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import { Skeleton } from "./components/ui/misc";
import { AppShell } from "./layouts/app-shell";
import { MarketingLayout } from "./layouts/marketing";
import Landing from "./pages/landing";
import { NotFound } from "./pages/states";

const AnalysisLayout = lazy(() => import("./pages/analysis/layout"));
const AtsTab = lazy(() => import("./pages/analysis/ats"));
const ContentTab = lazy(() => import("./pages/analysis/content"));
const MatchTab = lazy(() => import("./pages/analysis/match"));
const Overview = lazy(() => import("./pages/analysis/overview"));
const ParsedResume = lazy(() => import("./pages/analysis/parsed"));
const SkillsTab = lazy(() => import("./pages/analysis/skills"));
const StudioTab = lazy(() => import("./pages/analysis/studio"));
const Login = lazy(() => import("./pages/auth").then((m) => ({ default: m.Login })));
const Register = lazy(() => import("./pages/auth").then((m) => ({ default: m.Register })));
const ComparePage = lazy(() => import("./pages/compare"));
const DashboardPage = lazy(() => import("./pages/dashboard"));
const HistoryPage = lazy(() => import("./pages/history"));
const JobMatcher = lazy(() => import("./pages/match"));
const NewAnalysis = lazy(() => import("./pages/new-analysis"));
const ProfilePage = lazy(() => import("./pages/profile"));
const ResumeDetailPage = lazy(() => import("./pages/resumes").then((m) => ({ default: m.ResumeDetailPage })));
const ResumesPage = lazy(() => import("./pages/resumes").then((m) => ({ default: m.ResumesPage })));
const SettingsPage = lazy(() => import("./pages/settings"));
const StudioEntry = lazy(() => import("./pages/studio-entry"));

export default function App() {
  return (
    <Suspense fallback={<div className="mx-auto max-w-6xl p-10"><Skeleton className="h-8 w-64" /><Skeleton className="mt-6 h-64 w-full rounded-2xl" /></div>}>
      <Routes>
        <Route element={<MarketingLayout />}><Route index element={<Landing />} /></Route>
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="app" element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="new" element={<NewAnalysis />} />
          <Route path="match" element={<JobMatcher />} />
          <Route path="resumes" element={<ResumesPage />} />
          <Route path="resumes/:id" element={<ResumeDetailPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="compare" element={<ComparePage />} />
          <Route path="studio" element={<StudioEntry />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="analyses/:id" element={<AnalysisLayout />}>
            <Route index element={<Overview />} />
            <Route path="resume" element={<ParsedResume />} />
            <Route path="ats" element={<AtsTab />} />
            <Route path="skills" element={<SkillsTab />} />
            <Route path="content" element={<ContentTab />} />
            <Route path="match" element={<MatchTab />} />
            <Route path="studio" element={<StudioTab />} />
          </Route>
          <Route path="*" element={<NotFound inApp />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
}
