import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { formatPrice, formatRelativeTime, formatSource } from "@/lib/utils";
import type { Listing } from "@/types/api";

interface RecentListingsProps {
  listings: Listing[];
}

export default function RecentListings({ listings }: RecentListingsProps) {
  if (listings.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-4">No listings yet.</p>
    );
  }

  return (
    <ul className="divide-y">
      {listings.map((l) => (
        <li key={l.id}>
          <Link
            href={`/listings/${l.id}`}
            className="flex items-center justify-between py-3 hover:bg-muted/50 -mx-2 px-2 rounded transition-colors"
          >
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">
                {l.address || l.city || "—"}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatRelativeTime(l.first_seen_at)}
              </p>
            </div>
            <div className="ml-4 flex items-center gap-2 shrink-0">
              <Badge variant="secondary">{formatSource(l.source)}</Badge>
              <span className="text-sm font-semibold tabular-nums">
                {formatPrice(l.price)}
              </span>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}
