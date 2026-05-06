export const dynamic = "force-dynamic";

import { Suspense } from "react";
import FilterSidebar from "@/components/listings/FilterSidebar";
import FilterSidebarSkeleton from "@/components/listings/FilterSidebarSkeleton";
import ListingGrid from "@/components/listings/ListingGrid";
import Pagination from "@/components/listings/Pagination";
import EmptyState from "@/components/listings/EmptyState";
import { getListings, getSources } from "@/lib/api";
import type { ListingFilters, PropertyType } from "@/types/api";

interface PageProps {
  searchParams: {
    page?: string;
    source?: string;
    city?: string;
    min_price?: string;
    max_price?: string;
    min_bedrooms?: string;
    property_type?: string;
  };
}

export default async function ListingsPage({ searchParams }: PageProps) {
  const page = Number(searchParams.page ?? 1);
  const perPage = 24;

  const filters: ListingFilters = {
    page,
    per_page: perPage,
    ...(searchParams.source && { source: searchParams.source }),
    ...(searchParams.city && { city: searchParams.city }),
    ...(searchParams.min_price && { min_price: Number(searchParams.min_price) }),
    ...(searchParams.max_price && { max_price: Number(searchParams.max_price) }),
    ...(searchParams.min_bedrooms && {
      min_bedrooms: Number(searchParams.min_bedrooms),
    }),
    ...(searchParams.property_type && {
      property_type: searchParams.property_type as PropertyType,
    }),
  };

  const [data, sources] = await Promise.all([
    getListings(filters),
    getSources(),
  ]);

  return (
    <div className="flex gap-8">
      <Suspense fallback={<FilterSidebarSkeleton />}>
        <FilterSidebar initialFilters={filters} sources={sources} />
      </Suspense>

      <div className="flex-1 min-w-0">
        <p className="text-sm text-muted-foreground mb-4">
          {data.total.toLocaleString("en-CA")} listing
          {data.total !== 1 ? "s" : ""}
        </p>

        {data.results.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            <ListingGrid listings={data.results} />
            <Suspense>
              <Pagination page={page} total={data.total} perPage={perPage} />
            </Suspense>
          </>
        )}
      </div>
    </div>
  );
}
