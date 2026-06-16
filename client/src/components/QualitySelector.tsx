"use client";

import type { QualitySelectorProps } from "@/components/types";
import { QUALITIES } from "@/constants/options";
import { cn } from "@/lib/utils";

export function QualitySelector({ value, onChange }: QualitySelectorProps) {
  return (
    <div className="flex flex-wrap gap-1.5 px-1">
      {QUALITIES.map(({ value: quality, label }) => {
        const active = value === quality;
        return (
          <button
            key={quality}
            type="button"
            onClick={() => onChange(quality)}
            aria-pressed={active}
            className={cn(
              "rounded-lg px-3 py-1.5 font-mono text-xs transition-colors",
              active
                ? "bg-primary/15 text-primary ring-1 ring-inset ring-primary/40"
                : "text-muted-foreground hover:bg-muted/60 hover:text-foreground",
            )}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}
