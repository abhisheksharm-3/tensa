"use client";

import { JobCard } from "@/components/JobCard";
import type { JobListProps } from "@/components/types";

export function JobList({ jobs, onEvent, onRemove }: JobListProps) {
  if (jobs.length === 0) return null;

  return (
    <div className="mt-4 space-y-3">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} onEvent={onEvent} onRemove={onRemove} />
      ))}
    </div>
  );
}
