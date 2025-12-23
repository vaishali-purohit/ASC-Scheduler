import React, { useCallback } from "react";

interface TabNavigationProps {
  activeTab: "satellites" | "passes";
  onTabChange: (tab: "satellites" | "passes") => void;
  satelliteCount: number;
  passScheduleCount: number;
  satellitesLoading?: boolean;
  passesLoading?: boolean;
}

/**
 * TabNavigation component for switching between satellites and pass schedules
 */
const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
  satelliteCount,
  passScheduleCount,
  satellitesLoading = false,
  passesLoading = false,
}) => {
  // Memoize tab change handler to prevent unnecessary re-renders
  const handleTabChange = useCallback(
    (tab: "satellites" | "passes") => {
      // Debounce rapid tab switching to prevent performance issues
      if (tab !== activeTab) {
        onTabChange(tab);
      }
    },
    [activeTab, onTabChange]
  );

  return (
    <div className="mb-6">
      <div className="bg-white rounded-lg border border-slate-200 p-1 inline-flex shadow-sm">
        <button
          onClick={() => handleTabChange("satellites")}
          className={`px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
            activeTab === "satellites"
              ? "bg-blue-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
          }`}
          disabled={satellitesLoading}
        >
          <span>Satellites ({satelliteCount})</span>
          {satellitesLoading && (
            <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
          )}
        </button>
        <button
          onClick={() => handleTabChange("passes")}
          className={`px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2 ${
            activeTab === "passes"
              ? "bg-blue-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
          }`}
          disabled={passesLoading}
        >
          <span>Pass Schedules ({passScheduleCount})</span>
          {passesLoading && (
            <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
          )}
        </button>
      </div>
    </div>
  );
};

export default TabNavigation;
