"use client";

import type { QualitySelectorProps } from "@/components/types";
import { QUALITIES } from "@/constants/options";
import { cn } from "@/lib/utils";

export function QualitySelector({ value, onChange }: QualitySelectorProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {QUALITIES.map(({ value: quality, label }) => (
        <button
          key={quality}
          type="button"
          onClick={() => onChange(quality)}
          className={cn(
            "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
            value === quality
              ? "border-primary bg-primary text-primary-foreground"
              : "border-border text-muted-foreground hover:border-muted-foreground hover:text-foreground",
          )}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
