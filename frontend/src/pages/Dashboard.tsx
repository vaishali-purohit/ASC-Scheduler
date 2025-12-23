import { useState, useMemo, useCallback } from "react";

import { refreshTle, generatePassSchedules } from "../api/schedulerApi";
import { useDataContext } from "../hooks/useDataContext";
import TabNavigation from "../components/layout/TabNavigation";
import Header from "../components/layout/Header";
import TwoColumnGrid from "../components/ui/TwoColumnGrid";
import SatelliteCard from "../components/cards/SatelliteCard";
import PassScheduleCard from "../components/cards/PassScheduleCard";
import Card from "../components/ui/Card";

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState<"satellites" | "passes">(
    "satellites"
  );

  // Use the data context instead of local state
  const {
    satellites,
    passSchedules,
    loading,
    error,
    isStale,
    refreshSatellites,
    refreshPassSchedules,
    getTimeSinceLastUpdate,
  } = useDataContext();

  const handleGeneratePasses = useCallback(async () => {
    try {
      await generatePassSchedules();
      alert("Pass generation started successfully!");
      // Mark pass schedules as stale so they refresh automatically
      await refreshPassSchedules();
    } catch (err) {
      alert("Failed to generate passes. Please try again.");
      console.error(err);
    }
  }, [refreshPassSchedules]);

  const handleRefreshTLEs = useCallback(async () => {
    try {
      await refreshTle();
      alert("TLE refresh started successfully!");
      // Mark satellites as stale so they refresh automatically
      await refreshSatellites();
    } catch (err) {
      alert("Failed to refresh TLEs. Please try again.");
      console.error(err);
    }
  }, [refreshSatellites]);

  // Manual refresh handlers for each tab
  const handleRefreshSatellites = useCallback(async () => {
    try {
      await refreshSatellites();
    } catch (err) {
      console.error("Failed to refresh satellites:", err);
    }
  }, [refreshSatellites]);

  const handleRefreshPassSchedules = useCallback(async () => {
    try {
      await refreshPassSchedules();
    } catch (err) {
      console.error("Failed to refresh pass schedules:", err);
    }
  }, [refreshPassSchedules]);

  // Memoize satellite items to prevent unnecessary recalculations
  const satelliteItems = useMemo(
    () =>
      satellites.map((sat) => ({
        id: sat.norad_id,
        content: <SatelliteCard satellite={sat} />,
      })),
    [satellites]
  );

  // Memoize pass schedule items to prevent unnecessary recalculations
  const passScheduleItems = useMemo(
    () =>
      passSchedules.map((schedule, idx) => ({
        id: `${schedule.satellite_norad_id}-${idx}`,
        content: <PassScheduleCard schedule={schedule} />,
      })),
    [passSchedules]
  );

  // Create sticky header content for satellites
  const satelliteStickyHeader = useMemo(
    () => (
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-600">
            {satellites.length} satellites
          </span>
          {isStale.satellites && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Stale
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">
            Updated {getTimeSinceLastUpdate("satellites")}
          </span>
          <button
            onClick={handleRefreshSatellites}
            disabled={loading.satellites}
            className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading.satellites ? (
              <>
                <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin mr-1" />
                Refreshing
              </>
            ) : (
              "Refresh"
            )}
          </button>
        </div>
      </div>
    ),
    [
      satellites.length,
      isStale.satellites,
      loading.satellites,
      getTimeSinceLastUpdate,
      handleRefreshSatellites,
    ]
  );

  // Create sticky header content for pass schedules
  const passSchedulesStickyHeader = useMemo(
    () => (
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-600">
            {passSchedules.length} pass schedules
          </span>
          {isStale.passSchedules && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              Stale
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">
            Updated {getTimeSinceLastUpdate("passSchedules")}
          </span>
          <button
            onClick={handleRefreshPassSchedules}
            disabled={loading.passSchedules}
            className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading.passSchedules ? (
              <>
                <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin mr-1" />
                Refreshing
              </>
            ) : (
              "Refresh"
            )}
          </button>
        </div>
      </div>
    ),
    [
      passSchedules.length,
      isStale.passSchedules,
      loading.passSchedules,
      getTimeSinceLastUpdate,
      handleRefreshPassSchedules,
    ]
  );

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Header
          onGeneratePasses={handleGeneratePasses}
          onRefreshTLEs={handleRefreshTLEs}
        />

        <TabNavigation
          activeTab={activeTab}
          onTabChange={setActiveTab}
          satelliteCount={satellites.length}
          passScheduleCount={passSchedules.length}
          satellitesLoading={loading.satellites}
          passesLoading={loading.passSchedules}
        />

        <main>
          {activeTab === "satellites" ? (
            <Card
              title="Satellites"
              subtitle={`Total: ${satellites.length} satellites`}
              stickyHeader={true}
            >
              <TwoColumnGrid
                items={satelliteItems}
                loading={loading.satellites}
                error={error.satellites}
                emptyMessage="No satellites found."
                stickyHeader={satelliteStickyHeader}
                maxHeight="max-h-[600px]"
              />
            </Card>
          ) : (
            <Card
              title="Pass Schedules"
              subtitle={`Total: ${passSchedules.length} schedules`}
              stickyHeader={true}
            >
              <TwoColumnGrid
                items={passScheduleItems}
                loading={loading.passSchedules}
                error={error.passSchedules}
                emptyMessage="No pass schedules found."
                stickyHeader={passSchedulesStickyHeader}
                maxHeight="max-h-[600px]"
              />
            </Card>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
