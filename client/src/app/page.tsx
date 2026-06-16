"use client";

import { JobList } from "@/components/JobList";
import LineWaves from "@/components/LineWaves";
import SplitText from "@/components/SplitText";
import { UrlPanel } from "@/components/UrlPanel";
import { useJobManager } from "@/hooks/useJobManager";
import { useJobReconcile } from "@/hooks/useJobReconcile";

export default function Home() {
  const { jobs, addJob, patchJob, applySSEEvent, removeJob } = useJobManager();
  useJobReconcile(jobs, patchJob);

  return (
    <div className="relative min-h-[100dvh] overflow-hidden">
      {/* Cinematic backdrop — ember-tinted flowing silk, kept dim and faded
          toward the content so it sets mood without competing with the UI. */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 z-0 opacity-[0.55] [mask-image:radial-gradient(120%_85%_at_50%_0%,black,transparent_75%)]"
      >
        <LineWaves
          color1="#FF7A2F"
          color2="#C2476A"
          color3="#5B3FA8"
          speed={0.18}
          brightness={0.32}
          warpIntensity={1.8}
          edgeFadeWidth={0.5}
          colorCycleSpeed={0.25}
        />
      </div>

      <main className="relative z-10 mx-auto flex min-h-[100dvh] w-full max-w-xl flex-col px-5 pt-20 pb-28 sm:pt-28">
        <header className="mb-12 flex flex-col items-center gap-5 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/40 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.18em] text-muted-foreground backdrop-blur-sm">
            <span className="size-1.5 rounded-full bg-primary shadow-[0_0_8px_2px] shadow-primary/60" />
            self-hosted · ad-free
          </div>
          <SplitText
            text="Tensa"
            tag="h1"
            className="font-display text-7xl font-bold leading-[0.9] tracking-[-0.04em] text-foreground sm:text-8xl"
            splitType="chars"
            delay={45}
            duration={0.9}
            ease="power3.out"
            from={{ opacity: 0, y: 40 }}
            to={{ opacity: 1, y: 0 }}
          />
          <p className="font-mono text-sm text-muted-foreground">
            paste a link. get the file.
          </p>
        </header>

        <UrlPanel onJobAdded={addJob} />

        <JobList jobs={jobs} onEvent={applySSEEvent} onRemove={removeJob} />
      </main>
    </div>
  );
}
