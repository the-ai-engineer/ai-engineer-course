"use client";

import { useState } from "react";
import { ChevronDown, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Source } from "@/lib/api";

interface SourcesProps {
  sources: Source[];
}

function normalizeScore(score: number): number {
  // RRF scores with k=60 max out around 0.033 (rank 1 in both searches)
  // Normalize to 0-100 range for display
  const maxRrfScore = 0.033;
  return Math.min(100, Math.round((score / maxRrfScore) * 100));
}

export default function Sources({ sources }: SourcesProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-border/50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        <FileText className="h-3.5 w-3.5" />
        <span>
          {sources.length} source{sources.length !== 1 ? "s" : ""}
        </span>
        <ChevronDown
          className={cn(
            "h-3.5 w-3.5 transition-transform",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {isOpen && (
        <div className="mt-2 space-y-2">
          {sources.map((source, idx) => (
            <div
              key={idx}
              className="p-2.5 bg-background/50 rounded-md border border-border/50 text-xs"
            >
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium">{source.source}</span>
                <span className="text-muted-foreground">
                  {normalizeScore(source.score)}% relevance
                </span>
              </div>
              <p className="text-muted-foreground line-clamp-2">
                {source.content}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
