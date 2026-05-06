export const dynamic = "force-dynamic";

import { notFound } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import ListingHero from "@/components/listing-detail/ListingHero";
import ListingMeta from "@/components/listing-detail/ListingMeta";
import ListingDescription from "@/components/listing-detail/ListingDescription";
import { getListing } from "@/lib/api";
import { ApiError } from "@/lib/api";

interface PageProps {
  params: { id: string };
}

export default async function ListingDetailPage({ params }: PageProps) {
  let listing;
  try {
    listing = await getListing(params.id);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      notFound();
    }
    throw err;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link
        href="/listings"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ChevronLeft className="h-4 w-4" />
        Back to listings
      </Link>

      <ListingHero listing={listing} />
      <ListingMeta listing={listing} />
      <ListingDescription
        description={listing.description ?? ""}
        listingUrl={listing.listing_url}
        source={listing.source}
      />
    </div>
  );
}
