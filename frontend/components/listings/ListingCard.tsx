import Link from "next/link";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  formatPrice,
  formatRelativeTime,
  formatSource,
  formatPropertyType,
} from "@/lib/utils";
import type { Listing } from "@/types/api";

interface ListingCardProps {
  listing: Listing;
}

export default function ListingCard({ listing: l }: ListingCardProps) {
  const image = l.images?.[0] ?? null;

  return (
    <Link href={`/listings/${l.id}`}>
      <Card className="overflow-hidden h-full hover:shadow-md transition-shadow">
        <div className="relative h-48 bg-muted">
          {image ? (
            <Image
              src={image}
              alt={l.address || l.city || "Listing"}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground text-xs">
              No image
            </div>
          )}
        </div>
        <CardContent className="pt-4 space-y-1">
          <p className="font-bold text-lg tabular-nums">{formatPrice(l.price)}</p>
          <p className="text-sm text-foreground truncate">
            {l.address || l.city || "Address unavailable"}
          </p>
          {l.city && l.address && (
            <p className="text-xs text-muted-foreground">{l.city}</p>
          )}
          <div className="flex flex-wrap gap-1.5 pt-1">
            <Badge variant="secondary">{formatSource(l.source)}</Badge>
            <Badge variant="outline">{formatPropertyType(l.property_type)}</Badge>
            {l.bedrooms != null && (
              <Badge variant="outline">{l.bedrooms} bd</Badge>
            )}
            {l.bathrooms != null && (
              <Badge variant="outline">{l.bathrooms} ba</Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground pt-0.5">
            {formatRelativeTime(l.first_seen_at)}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
