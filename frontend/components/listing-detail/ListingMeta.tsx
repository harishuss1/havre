import { Bed, Bath, Maximize2, Home, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  formatPropertyType,
  formatDate,
  formatSqft,
} from "@/lib/utils";
import type { Listing } from "@/types/api";

interface ListingMetaProps {
  listing: Listing;
}

export default function ListingMeta({ listing: l }: ListingMetaProps) {
  const sqft = formatSqft(l.size_sqft);

  return (
    <div className="flex flex-wrap gap-2">
      {l.bedrooms != null && (
        <Badge variant="outline" className="gap-1.5 px-3 py-1.5 text-sm">
          <Bed className="h-3.5 w-3.5" />
          {l.bedrooms} {l.bedrooms === 1 ? "bedroom" : "bedrooms"}
        </Badge>
      )}
      {l.bathrooms != null && (
        <Badge variant="outline" className="gap-1.5 px-3 py-1.5 text-sm">
          <Bath className="h-3.5 w-3.5" />
          {l.bathrooms} {l.bathrooms === 1 ? "bathroom" : "bathrooms"}
        </Badge>
      )}
      {sqft && (
        <Badge variant="outline" className="gap-1.5 px-3 py-1.5 text-sm">
          <Maximize2 className="h-3.5 w-3.5" />
          {sqft}
        </Badge>
      )}
      <Badge variant="outline" className="gap-1.5 px-3 py-1.5 text-sm">
        <Home className="h-3.5 w-3.5" />
        {formatPropertyType(l.property_type)}
      </Badge>
      <Badge variant="outline" className="gap-1.5 px-3 py-1.5 text-sm">
        <Calendar className="h-3.5 w-3.5" />
        Listed {formatDate(l.first_seen_at)}
      </Badge>
    </div>
  );
}
