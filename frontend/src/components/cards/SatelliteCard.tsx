import React, { memo } from "react";
import InfoRow from "../ui/InfoRow";
import Badge from "../ui/Badge";
import { useDataContext } from "../../hooks/useDataContext";
import type { Satellite } from "../../types";

interface SatelliteCardProps {
  satellite: Satellite;
  showPassCount?: boolean;
}

/**
 * Custom comparison function for memo to prevent unnecessary re-renders
 */
const areEqual = (
  prevProps: SatelliteCardProps,
  nextProps: SatelliteCardProps
) => {
  return (
    prevProps.satellite.norad_id === nextProps.satellite.norad_id &&
    prevProps.satellite.name === nextProps.satellite.name &&
    prevProps.satellite.description === nextProps.satellite.description &&
    prevProps.satellite.tles.length === nextProps.satellite.tles.length &&
    prevProps.satellite.pass_schedules.length ===
      nextProps.satellite.pass_schedules.length &&
    prevProps.showPassCount === nextProps.showPassCount
  );
};

/**
 * SatelliteCard component for displaying satellite information with context support
 */
const SatelliteCard: React.FC<SatelliteCardProps> = ({
  satellite,
  showPassCount = true,
}) => {
  const { getPassSchedulesBySatellite, isStale } = useDataContext();

  // Get pass schedules from context for this satellite
  const contextPassSchedules = getPassSchedulesBySatellite(satellite.norad_id);
  const passCount = showPassCount
    ? contextPassSchedules.length
    : satellite.pass_schedules.length;
  const hasStaleData = isStale.satellites;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex justify-between items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-slate-900 text-base truncate">
              {satellite.name}
            </h3>
            {hasStaleData && (
              <div
                className="w-2 h-2 bg-yellow-400 rounded-full"
                title="Data may be stale"
              />
            )}
          </div>
          <Badge variant="info">NORAD {satellite.norad_id}</Badge>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-200">
        <InfoRow label="TLEs" value={satellite.tles.length} />
        <InfoRow label="Passes" value={passCount} />
      </div>

      {satellite.description && (
        <p className="text-sm text-slate-600 pt-2 border-t border-slate-200 line-clamp-2">
          {satellite.description}
        </p>
      )}
    </div>
  );
};

// Wrap component with memo to prevent unnecessary re-renders
export default memo(SatelliteCard, areEqual);
