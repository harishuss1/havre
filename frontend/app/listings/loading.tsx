import FilterSidebarSkeleton from "@/components/listings/FilterSidebarSkeleton";
import ListingCardSkeleton from "@/components/listings/ListingCardSkeleton";
import { Skeleton } from "@/components/ui/skeleton";

export default function ListingsLoading() {
  return (
    <div className="flex gap-8">
      <FilterSidebarSkeleton />
      <div className="flex-1 space-y-4">
        <Skeleton className="h-5 w-32" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <ListingCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
}
