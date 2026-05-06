import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { PropertyType } from "@/types/api";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const formatPrice = (p: number) =>
  new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
    maximumFractionDigits: 0,
  }).format(p);

export const formatDate = (iso: string) =>
  new Intl.DateTimeFormat("en-CA", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(iso));

export function formatRelativeTime(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return days === 1 ? "Yesterday" : `${days} days ago`;
}

export const formatPropertyType = (t: PropertyType): string =>
  ({ house: "House", condo: "Condo", duplex: "Duplex", land: "Land", other: "Other" }[t] ?? t);

export const formatSource = (s: string): string =>
  ({ centris: "Centris", duproprio: "DuProprio", kijiji: "Kijiji" }[s] ?? s);

export const formatSqft = (n: number | null) =>
  n ? `${n.toLocaleString("en-CA")} sq ft` : null;
