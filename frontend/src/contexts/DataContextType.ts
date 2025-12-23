import { createContext } from "react";
import type { DataState, Satellite, PassSchedule } from "../types";

export interface DataContextType extends DataState {
  fetchSatellitesData: () => Promise<void>;
  fetchPassSchedulesData: () => Promise<void>;
  refreshSatellites: () => Promise<void>;
  refreshPassSchedules: () => Promise<void>;
  markSatellitesStale: () => void;
  markPassSchedulesStale: () => void;
  clearErrors: () => void;
  getSatelliteById: (id: number) => Satellite | undefined;
  getPassSchedulesBySatellite: (satelliteId: number) => PassSchedule[];
  getTimeSinceLastUpdate: (type: "satellites" | "passSchedules") => string;
}

export const DataContext = createContext<DataContextType | undefined>(
  undefined
);
