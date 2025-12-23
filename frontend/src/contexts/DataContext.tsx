import React, { useReducer, useCallback, useEffect, useMemo } from "react";
import type { ReactNode } from "react";
import { fetchSatellites, fetchPassSchedules } from "../api/schedulerApi";
import { dataReducer } from "../reducer/DataReducer";
import { initialState } from "../constants/dataConstants";
import { DataContext } from "./DataContextType";
import type { DataContextType } from "./DataContextType";

export const DataProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(dataReducer, initialState);

  const fetchSatellitesData = useCallback(async () => {
    // Logic check inside the action to prevent redundant network calls
    dispatch({ type: "FETCH_SATELLITES_START" });
    try {
      const data = await fetchSatellites();
      dispatch({ type: "FETCH_SATELLITES_SUCCESS", payload: data });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to fetch satellites";
      dispatch({ type: "FETCH_SATELLITES_ERROR", payload: errorMessage });
    }
  }, []);

  const fetchPassSchedulesData = useCallback(async () => {
    dispatch({ type: "FETCH_PASS_SCHEDULES_START" });
    try {
      const data = await fetchPassSchedules();
      dispatch({ type: "FETCH_PASS_SCHEDULES_SUCCESS", payload: data });
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Failed to fetch pass schedules";
      dispatch({ type: "FETCH_PASS_SCHEDULES_ERROR", payload: errorMessage });
    }
  }, []);

  const refreshSatellites = useCallback(async () => {
    dispatch({ type: "MARK_SATELLITES_STALE" });
    await fetchSatellitesData();
  }, [fetchSatellitesData]);

  const refreshPassSchedules = useCallback(async () => {
    dispatch({ type: "MARK_PASS_SCHEDULES_STALE" });
    await fetchPassSchedulesData();
  }, [fetchPassSchedulesData]);

  const markSatellitesStale = useCallback(() => {
    dispatch({ type: "MARK_SATELLITES_STALE" });
  }, []);

  const markPassSchedulesStale = useCallback(() => {
    dispatch({ type: "MARK_PASS_SCHEDULES_STALE" });
  }, []);

  const clearErrors = useCallback(() => {
    dispatch({ type: "FETCH_SATELLITES_ERROR", payload: "" });
    dispatch({ type: "FETCH_PASS_SCHEDULES_ERROR", payload: "" });
  }, []);

  // Utility Functions
  const getSatelliteById = useCallback(
    (id: number) => state.satellites.find((sat) => sat.norad_id === id),
    [state.satellites]
  );

  const getPassSchedulesBySatellite = useCallback(
    (satelliteId: number) =>
      state.passSchedules.filter((s) => s.satellite_norad_id === satelliteId),
    [state.passSchedules]
  );

  const getTimeSinceLastUpdate = useCallback(
    (type: "satellites" | "passSchedules") => {
      const lastUpdate = state.lastUpdated[type];
      if (!lastUpdate) return "Never";

      const diff = Date.now() - lastUpdate;
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(minutes / 60);

      if (hours > 0) return `${hours}h ago`;
      if (minutes > 0) return `${minutes}m ago`;
      return "Just now";
    },
    [state.lastUpdated]
  );

  useEffect(() => {
    if (state.isStale.satellites) fetchSatellitesData();
  }, [state.isStale.satellites, fetchSatellitesData]);

  useEffect(() => {
    if (state.isStale.passSchedules) fetchPassSchedulesData();
  }, [state.isStale.passSchedules, fetchPassSchedulesData]);

  const contextValue: DataContextType = useMemo(
    () => ({
      ...state,
      fetchSatellitesData,
      fetchPassSchedulesData,
      refreshSatellites,
      refreshPassSchedules,
      markSatellitesStale,
      markPassSchedulesStale,
      clearErrors,
      getSatelliteById,
      getPassSchedulesBySatellite,
      getTimeSinceLastUpdate,
    }),
    [
      state,
      fetchSatellitesData,
      fetchPassSchedulesData,
      refreshSatellites,
      refreshPassSchedules,
      getSatelliteById,
      getPassSchedulesBySatellite,
      getTimeSinceLastUpdate,
      markSatellitesStale,
      markPassSchedulesStale,
      clearErrors,
    ]
  );

  return (
    <DataContext.Provider value={contextValue}>{children}</DataContext.Provider>
  );
};
