"use client";

import { JobCard } from "@/components/JobCard";
import type { JobListProps } from "@/components/types";

export function JobList({ jobs, onEvent, onRemove }: JobListProps) {
  if (jobs.length === 0) return null;

  return (
    <section className="mt-8">
      <h2 className="mb-3 px-1 font-mono text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
        Queue · {jobs.length}
      </h2>
      <div className="space-y-2.5">
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onEvent={onEvent}
            onRemove={onRemove}
          />
        ))}
      </div>
    </section>
  );
}
