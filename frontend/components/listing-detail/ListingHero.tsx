import Image from "next/image";
import { Badge } from "@/components/ui/badge";
import { formatPrice, formatSource } from "@/lib/utils";
import type { Listing } from "@/types/api";

interface ListingHeroProps {
  listing: Listing;
}

export default function ListingHero({ listing: l }: ListingHeroProps) {
  const image = l.images?.[0] ?? null;

  return (
    <div className="space-y-4">
      <div className="relative h-72 rounded-lg overflow-hidden bg-muted">
        {image ? (
          <Image
            src={image}
            alt={l.address || l.city || "Listing photo"}
            fill
            priority
            className="object-cover"
            sizes="(max-width: 896px) 100vw, 896px"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
            No photo available
          </div>
        )}
      </div>

      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <p className="text-3xl font-bold tabular-nums">
            {formatPrice(l.price)}
          </p>
          <p className="text-muted-foreground mt-1">
            {l.address || l.city || "Address unavailable"}
          </p>
          {l.city && l.address && (
            <p className="text-sm text-muted-foreground">{l.city}</p>
          )}
        </div>
        <Badge variant="secondary" className="text-sm px-3 py-1">
          {formatSource(l.source)}
        </Badge>
      </div>
    </div>
  );
}
