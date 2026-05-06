import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function StatCardSkeleton() {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center gap-3">
          <Skeleton className="h-9 w-9 rounded-md" />
          <div className="space-y-1.5">
            <Skeleton className="h-7 w-16" />
            <Skeleton className="h-4 w-28" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
