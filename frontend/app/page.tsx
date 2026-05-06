export const dynamic = "force-dynamic";

import { Building2, TrendingUp, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import StatCard from "@/components/dashboard/StatCard";
import RecentListings from "@/components/dashboard/RecentListings";
import { getStats, getListings } from "@/lib/api";

export default async function DashboardPage() {
  const [stats, recent] = await Promise.all([
    getStats(),
    getListings({ per_page: 5 }),
  ]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Montreal real estate — all sources in one place.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Total listings"
          value={stats.total_listings.toLocaleString("en-CA")}
          Icon={Building2}
        />
        <StatCard
          label="New today"
          value={stats.new_today.toLocaleString("en-CA")}
          Icon={TrendingUp}
        />
        <StatCard
          label={`Active sources (${stats.sources_total} total)`}
          value={stats.sources_active}
          Icon={Zap}
        />
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Most recent listings</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentListings listings={recent.results} />
        </CardContent>
      </Card>
    </div>
  );
}
