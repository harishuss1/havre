"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function ListingsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center gap-4 py-20 text-center">
      <p className="text-sm text-muted-foreground">{error.message}</p>
      <Button onClick={reset} variant="outline" size="sm">
        Retry
      </Button>
    </div>
  );
}
