import { Skeleton } from "@/components/ui/skeleton";

export default function FilterSidebarSkeleton() {
  return (
    <aside className="w-64 shrink-0 space-y-6">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-9 w-full" />
        </div>
      ))}
    </aside>
  );
}
