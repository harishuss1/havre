import { SearchX } from "lucide-react";

export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
      <SearchX className="h-10 w-10 text-muted-foreground" />
      <p className="text-sm text-muted-foreground">
        No listings match your filters.
      </p>
    </div>
  );
}
