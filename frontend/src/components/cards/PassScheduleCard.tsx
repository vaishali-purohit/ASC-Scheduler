import React, { memo } from "react";
import { formatExactTime } from "../../utils/dateUtils";
import InfoRow from "../ui/InfoRow";
import Badge from "../ui/Badge";
import { useDataContext } from "../../hooks/useDataContext";
import type { PassSchedule } from "../../types";

interface PassScheduleCardProps {
  schedule: PassSchedule;
  showContextInfo?: boolean;
}

/**
 * Custom comparison function for memo to prevent unnecessary re-renders
 */
const areEqual = (
  prevProps: PassScheduleCardProps,
  nextProps: PassScheduleCardProps
) => {
  return (
    prevProps.schedule.pass_id === nextProps.schedule.pass_id &&
    prevProps.schedule.satellite_norad_id ===
      nextProps.schedule.satellite_norad_id &&
    prevProps.schedule.satellite_name === nextProps.schedule.satellite_name &&
    prevProps.schedule.ground_station === nextProps.schedule.ground_station &&
    prevProps.schedule.start_time === nextProps.schedule.start_time &&
    prevProps.schedule.end_time === nextProps.schedule.end_time &&
    prevProps.schedule.status === nextProps.schedule.status &&
    prevProps.showContextInfo === nextProps.showContextInfo
  );
};

/**
 * PassScheduleCard component for displaying pass schedule information with context support
 */
const PassScheduleCard: React.FC<PassScheduleCardProps> = ({
  schedule,
  showContextInfo = false,
}) => {
  const { isStale, getSatelliteById, getTimeSinceLastUpdate } =
    useDataContext();

  const hasStaleData = isStale.passSchedules;
  const satelliteInfo = getSatelliteById(schedule.satellite_norad_id);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex justify-between items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-slate-900 text-base truncate">
              {schedule.satellite_name ||
                `Satellite ${schedule.satellite_norad_id}`}
            </h3>
            {hasStaleData && (
              <div
                className="w-2 h-2 bg-yellow-400 rounded-full"
                title="Data may be stale"
              />
            )}
          </div>
          <Badge variant="info">NORAD {schedule.satellite_norad_id}</Badge>
        </div>
        <Badge variant="success">{schedule.status}</Badge>
      </div>

      <div className="space-y-2 pt-2 border-t border-slate-200">
        <div className="bg-white rounded p-2 border border-slate-100">
          <div className="text-xs text-slate-500 mb-1">Start Time</div>
          <div className="text-sm text-slate-900 font-medium">
            {schedule.start_time ? formatExactTime(schedule.start_time) : "--"}
          </div>
        </div>

        <div className="bg-white rounded p-2 border border-slate-100">
          <div className="text-xs text-slate-500 mb-1">End Time</div>
          <div className="text-sm text-slate-900 font-medium">
            {schedule.end_time ? formatExactTime(schedule.end_time) : "--"}
          </div>
        </div>
      </div>

      <div className="pt-2 border-t border-slate-200">
        <InfoRow label="Ground Station" value={schedule.ground_station} />
      </div>

      {/* Context-aware information */}
      {showContextInfo && (
        <div className="pt-2 border-t border-slate-200">
          <div className="text-xs text-slate-500 space-y-1">
            <div>Updated {getTimeSinceLastUpdate("passSchedules")}</div>
            {satelliteInfo && <div>Satellite: {satelliteInfo.name}</div>}
          </div>
        </div>
      )}
    </div>
  );
};

// Wrap component with memo to prevent unnecessary re-renders
export default memo(PassScheduleCard, areEqual);
