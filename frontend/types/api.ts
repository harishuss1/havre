export type PropertyType = "house" | "condo" | "duplex" | "land" | "other";

export interface Listing {
  id: string;
  source: string;
  external_id: string;
  title: string;
  address: string;
  city: string;
  region: string;
  postal_code: string;
  price: number;
  bedrooms: number | null;
  bathrooms: number | null;
  size_sqft: number | null;
  property_type: PropertyType;
  listing_url: string;
  images: string[];
  description: string;
  content_hash: string;
  first_seen_at: string;
  last_seen_at: string;
}

export interface PaginatedListings {
  total: number;
  page: number;
  per_page: number;
  results: Listing[];
}

export interface Stats {
  total_listings: number;
  new_today: number;
  sources_active: number;
  sources_total: number;
}

export interface Source {
  id: string;
  name: string;
  display_name: string;
  is_enabled: boolean;
  scrape_interval_minutes: number;
  last_scraped_at: string | null;
  total_listings_found: number;
}

export interface SearchProfile {
  id: string;
  name: string;
  min_price: number | null;
  max_price: number | null;
  min_bedrooms: number | null;
  cities: string[];
  property_types: PropertyType[];
  sources: string[];
  is_active: boolean;
  created_at: string;
}

export interface ListingFilters {
  page?: number;
  per_page?: number;
  source?: string;
  city?: string;
  min_price?: number;
  max_price?: number;
  min_bedrooms?: number;
  property_type?: PropertyType;
}
