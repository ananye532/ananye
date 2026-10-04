import { Sparkles } from "lucide-react";
import { Link, Navigate } from "react-router-dom";
import { buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState, PageHeader, Skeleton } from "@/components/ui/misc";
import { useAnalyses } from "@/lib/queries";

/** The studio works on an analysis; open the most recent one. */
export default function StudioEntry() {
  const { data, isLoading } = useAnalyses({ limit: 1 });
  if (isLoading) return <Skeleton className="h-64 rounded-2xl" />;
  if (data?.[0]) return <Navigate to={`/app/analyses/${data[0].id}/studio`} replace />;
  return (
    <>
      <PageHeader title="Improvement studio" description="Rewrite weak bullets into outcome-driven ones." />
      <Card><EmptyState icon={<Sparkles />} title="Analyze a resume to start" description="The studio picks your weakest bullets from an analysis and suggests stronger versions."
        action={<Link to="/app/new" className={buttonVariants()}>New analysis</Link>} /></Card>
    </>
  );
}
