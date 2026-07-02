"use client";

import type { ModeSelectorProps } from "@/components/types";
import { MODES } from "@/constants/modes";
import { cn } from "@/lib/utils";

export function ModeSelector({ value, onChange }: ModeSelectorProps) {
  return (
    <div className="flex gap-0.5 rounded-xl bg-background/40 p-1">
      {MODES.map(({ value: mode, label, icon: Icon }) => {
        const active = value === mode;
        return (
          <button
            key={mode}
            type="button"
            onClick={() => onChange(mode)}
            aria-label={label}
            aria-pressed={active}
            className={cn(
              "flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-xs font-medium transition-colors",
              active
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            <Icon
              className={cn("size-4", active && "text-primary")}
              strokeWidth={active ? 2.25 : 2}
            />
            <span className="hidden sm:inline">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
