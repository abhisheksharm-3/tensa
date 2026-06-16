"use client";

import { JobList } from "@/components/JobList";
import { UrlPanel } from "@/components/UrlPanel";
import { useJobManager } from "@/hooks/useJobManager";

export default function Home() {
  const { jobs, addJob, applySSEEvent, removeJob } = useJobManager();

  return (
    <main className="flex min-h-[100dvh] flex-col items-center px-4 pt-16 pb-24">
      <div className="w-full max-w-lg">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Tensa
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Paste any link. Get the file.
          </p>
        </div>

        <div className="rounded-xl border border-border bg-card/50 p-4 shadow-xl">
          <UrlPanel onJobAdded={addJob} />
        </div>

        <JobList jobs={jobs} onEvent={applySSEEvent} onRemove={removeJob} />
      </div>
    </main>
  );
}
