"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function ListingDetailError({
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
    <div className="max-w-3xl mx-auto flex flex-col items-center gap-4 py-20 text-center">
      <p className="text-sm text-muted-foreground">{error.message}</p>
      <div className="flex gap-2">
        <Button onClick={reset} variant="outline" size="sm">
          Retry
        </Button>
        <Button asChild variant="ghost" size="sm">
          <Link href="/listings">Back to listings</Link>
        </Button>
      </div>
    </div>
  );
}
