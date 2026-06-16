"use client";

import type { ModeSelectorProps } from "@/components/types";
import { MODES } from "@/constants/modes";
import { cn } from "@/lib/utils";

export function ModeSelector({ value, onChange }: ModeSelectorProps) {
  return (
    <div className="flex gap-1 rounded-lg border border-border bg-muted/40 p-1">
      {MODES.map(({ value: mode, label, icon: Icon }) => (
        <button
          key={mode}
          type="button"
          onClick={() => onChange(mode)}
          className={cn(
            "flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-colors",
            value === mode
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-background hover:text-foreground",
          )}
        >
          <Icon className="size-3.5" />
          <span className="hidden sm:inline">{label}</span>
        </button>
      ))}
    </div>
  );
}
