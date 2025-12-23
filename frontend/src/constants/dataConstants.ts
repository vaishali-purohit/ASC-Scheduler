import type { DataState } from "../types";

export const initialState: DataState = {
  satellites: [],
  passSchedules: [],
  loading: {
    satellites: false,
    passSchedules: false,
  },
  error: {
    satellites: null,
    passSchedules: null,
  },
  lastUpdated: {
    satellites: null,
    passSchedules: null,
  },
  isStale: {
    satellites: true,
    passSchedules: true,
  },
};
