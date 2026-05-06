import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
      <p className="text-4xl font-bold">404</p>
      <p className="text-muted-foreground text-sm">
        This page doesn&apos;t exist.
      </p>
      <Button asChild variant="outline">
        <Link href="/">Go home</Link>
      </Button>
    </div>
  );
}
