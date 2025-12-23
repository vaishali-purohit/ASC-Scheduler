export interface Tle {
  tle_id: number;
  line1: string;
  line2: string;
  timestamp: string | null;
}

export interface Satellite {
  norad_id: number;
  name: string;
  description?: string | null;
  tles: Tle[];
  pass_schedules: PassSchedule[];
}

export interface PassSchedule {
  pass_id: number;
  satellite_norad_id: number;
  satellite_name?: string | null;
  ground_station: string;
  start_time: string | null;
  end_time: string | null;
  status: string;
}

export interface GridItem {
  id: string | number;
  content: React.ReactElement;
}

export interface DataState {
  satellites: Satellite[];
  passSchedules: PassSchedule[];
  loading: { satellites: boolean; passSchedules: boolean };
  error: { satellites: string | null; passSchedules: string | null };
  lastUpdated: { satellites: number | null; passSchedules: number | null };
  isStale: { satellites: boolean; passSchedules: boolean };
}

export type DataAction =
  | { type: "FETCH_SATELLITES_START" }
  | { type: "FETCH_SATELLITES_SUCCESS"; payload: Satellite[] }
  | { type: "FETCH_SATELLITES_ERROR"; payload: string }
  | { type: "FETCH_PASS_SCHEDULES_START" }
  | { type: "FETCH_PASS_SCHEDULES_SUCCESS"; payload: PassSchedule[] }
  | { type: "FETCH_PASS_SCHEDULES_ERROR"; payload: string }
  | { type: "MARK_SATELLITES_STALE" }
  | { type: "MARK_PASS_SCHEDULES_STALE" }
  | { type: "SET_SATELLITES_LOADING"; payload: boolean }
  | { type: "SET_PASS_SCHEDULES_LOADING"; payload: boolean };
