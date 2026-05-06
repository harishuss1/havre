"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ExternalLink } from "lucide-react";
import { formatSource } from "@/lib/utils";

interface ListingDescriptionProps {
  description: string;
  listingUrl: string;
  source: string;
}

export default function ListingDescription({
  description,
  listingUrl,
  source,
}: ListingDescriptionProps) {
  const [expanded, setExpanded] = useState(false);
  const lines = description.split("\n");
  const isLong = lines.length > 10;
  const visible = expanded ? description : lines.slice(0, 10).join("\n");

  return (
    <div className="space-y-4">
      <Separator />

      {description ? (
        <div>
          <p className="text-sm leading-relaxed whitespace-pre-line">{visible}</p>
          {isLong && (
            <Button
              variant="ghost"
              size="sm"
              className="mt-2 -ml-2 text-muted-foreground"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? "Show less" : "Show more"}
            </Button>
          )}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">No description provided.</p>
      )}

      <a
        href={listingUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 text-sm font-medium underline underline-offset-4 hover:text-muted-foreground transition-colors"
      >
        View on {formatSource(source)}
        <ExternalLink className="h-3.5 w-3.5" />
      </a>
    </div>
  );
}
