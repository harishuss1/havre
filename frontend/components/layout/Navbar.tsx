import Link from "next/link";

export default function Navbar() {
  return (
    <header className="border-b bg-background">
      <div className="container flex h-14 items-center gap-6">
        <Link href="/" className="font-semibold text-lg tracking-tight">
          Havre
        </Link>
        <nav className="flex items-center gap-4 text-sm text-muted-foreground">
          <Link
            href="/"
            className="hover:text-foreground transition-colors"
          >
            Dashboard
          </Link>
          <Link
            href="/listings"
            className="hover:text-foreground transition-colors"
          >
            Listings
          </Link>
        </nav>
      </div>
    </header>
  );
}
