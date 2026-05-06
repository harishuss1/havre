import ListingCard from "@/components/listings/ListingCard";
import type { Listing } from "@/types/api";

interface ListingGridProps {
  listings: Listing[];
}

export default function ListingGrid({ listings }: ListingGridProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {listings.map((l) => (
        <ListingCard key={l.id} listing={l} />
      ))}
    </div>
  );
}
