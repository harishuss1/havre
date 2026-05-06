import type {
  Listing,
  ListingFilters,
  PaginatedListings,
  Source,
  Stats,
  SearchProfile,
} from "@/types/api";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    next: { revalidate: 60 },
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": KEY,
      ...options.headers,
    },
  });
  if (!res.ok) throw new ApiError(res.status, `API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export async function getListings(
  filters: ListingFilters = {},
): Promise<PaginatedListings> {
  const p = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v != null) p.set(k, String(v));
  });
  return apiFetch<PaginatedListings>(`/listings${p.size ? `?${p}` : ""}`);
}

export async function getListing(id: string): Promise<Listing> {
  return apiFetch<Listing>(`/listings/${id}`);
}

export const getStats = () => apiFetch<Stats>("/stats");
export const getSources = () => apiFetch<Source[]>("/sources");
export const getProfiles = () => apiFetch<SearchProfile[]>("/profiles");

export const triggerScrape = (name: string) =>
  apiFetch<{ message: string }>(`/sources/${name}/trigger`, {
    method: "POST",
    cache: "no-store",
  });
