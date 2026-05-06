"use client";

import { useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import type { ListingFilters, Source } from "@/types/api";

interface FilterSidebarProps {
  initialFilters: ListingFilters;
  sources: Source[];
}

export default function FilterSidebar({
  initialFilters,
  sources,
}: FilterSidebarProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  function push(updates: Record<string, string | null>) {
    const params = new URLSearchParams(searchParams.toString());
    // Reset to page 1 on any filter change
    params.delete("page");
    for (const [k, v] of Object.entries(updates)) {
      if (v == null || v === "") {
        params.delete(k);
      } else {
        params.set(k, v);
      }
    }
    router.push(`/listings?${params}`);
  }

  function handleSelect(key: string, value: string) {
    push({ [key]: value === "all" ? null : value });
  }

  function handlePriceInput(key: string, value: string) {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      push({ [key]: value || null });
    }, 600);
  }

  function handleClear() {
    router.push("/listings");
  }

  const hasFilters = Object.values(initialFilters).some(
    (v) => v != null && v !== 1 && v !== 24,
  );

  return (
    <aside className="w-64 shrink-0 space-y-6">
      <div>
        <h2 className="text-sm font-semibold mb-4">Filters</h2>
        <Separator />
      </div>

      {/* Source */}
      <div className="space-y-1.5">
        <Label htmlFor="source">Source</Label>
        <Select
          defaultValue={initialFilters.source ?? "all"}
          onValueChange={(v) => handleSelect("source", v)}
        >
          <SelectTrigger id="source">
            <SelectValue placeholder="All sources" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sources</SelectItem>
            {sources.map((s) => (
              <SelectItem key={s.name} value={s.name}>
                {s.display_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Property type */}
      <div className="space-y-1.5">
        <Label htmlFor="property_type">Property type</Label>
        <Select
          defaultValue={initialFilters.property_type ?? "all"}
          onValueChange={(v) => handleSelect("property_type", v)}
        >
          <SelectTrigger id="property_type">
            <SelectValue placeholder="Any type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any type</SelectItem>
            <SelectItem value="house">House</SelectItem>
            <SelectItem value="condo">Condo</SelectItem>
            <SelectItem value="duplex">Duplex</SelectItem>
            <SelectItem value="land">Land</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Min bedrooms */}
      <div className="space-y-1.5">
        <Label htmlFor="min_bedrooms">Min bedrooms</Label>
        <Select
          defaultValue={
            initialFilters.min_bedrooms != null
              ? String(initialFilters.min_bedrooms)
              : "all"
          }
          onValueChange={(v) => handleSelect("min_bedrooms", v)}
        >
          <SelectTrigger id="min_bedrooms">
            <SelectValue placeholder="Any" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any</SelectItem>
            <SelectItem value="1">1+</SelectItem>
            <SelectItem value="2">2+</SelectItem>
            <SelectItem value="3">3+</SelectItem>
            <SelectItem value="4">4+</SelectItem>
            <SelectItem value="5">5+</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Price range */}
      <div className="space-y-1.5">
        <Label>Price range (CAD)</Label>
        <Input
          type="number"
          placeholder="Min price"
          defaultValue={initialFilters.min_price ?? ""}
          onChange={(e) => handlePriceInput("min_price", e.target.value)}
        />
        <Input
          type="number"
          placeholder="Max price"
          defaultValue={initialFilters.max_price ?? ""}
          onChange={(e) => handlePriceInput("max_price", e.target.value)}
        />
      </div>

      {hasFilters && (
        <>
          <Separator />
          <Button variant="ghost" size="sm" className="w-full" onClick={handleClear}>
            Clear filters
          </Button>
        </>
      )}
    </aside>
  );
}
