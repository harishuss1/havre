import { Skeleton } from "@/components/ui/skeleton";

export default function ListingDetailLoading() {
  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-72 w-full rounded-lg" />
      <div className="space-y-2">
        <Skeleton className="h-9 w-48" />
        <Skeleton className="h-5 w-64" />
      </div>
      <div className="flex gap-2 flex-wrap">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-28 rounded-full" />
        ))}
      </div>
      <Skeleton className="h-px w-full" />
      <div className="space-y-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-4 w-full" />
        ))}
      </div>
    </div>
  );
}
