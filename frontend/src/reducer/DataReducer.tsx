import type { DataState, DataAction } from "../types";
import { initialState } from "../constants/dataConstants";

export const dataReducer = (
  state: DataState = initialState,
  action: DataAction
): DataState => {
  switch (action.type) {
    case "FETCH_SATELLITES_START":
      return {
        ...state,
        loading: { ...state.loading, satellites: true },
        error: { ...state.error, satellites: null },
      };

    case "FETCH_SATELLITES_SUCCESS":
      return {
        ...state,
        satellites: action.payload,
        loading: { ...state.loading, satellites: false },
        error: { ...state.error, satellites: null },
        lastUpdated: { ...state.lastUpdated, satellites: Date.now() },
        isStale: { ...state.isStale, satellites: false },
      };

    case "FETCH_SATELLITES_ERROR":
      return {
        ...state,
        loading: { ...state.loading, satellites: false },
        error: { ...state.error, satellites: action.payload },
        isStale: { ...state.isStale, satellites: true },
      };

    case "FETCH_PASS_SCHEDULES_START":
      return {
        ...state,
        loading: { ...state.loading, passSchedules: true },
        error: { ...state.error, passSchedules: null },
      };

    case "FETCH_PASS_SCHEDULES_SUCCESS":
      return {
        ...state,
        passSchedules: action.payload,
        loading: { ...state.loading, passSchedules: false },
        error: { ...state.error, passSchedules: null },
        lastUpdated: { ...state.lastUpdated, passSchedules: Date.now() },
        isStale: { ...state.isStale, passSchedules: false },
      };

    case "FETCH_PASS_SCHEDULES_ERROR":
      return {
        ...state,
        loading: { ...state.loading, passSchedules: false },
        error: { ...state.error, passSchedules: action.payload },
        isStale: { ...state.isStale, passSchedules: true },
      };

    case "MARK_SATELLITES_STALE":
      return {
        ...state,
        isStale: { ...state.isStale, satellites: true },
      };

    case "MARK_PASS_SCHEDULES_STALE":
      return {
        ...state,
        isStale: { ...state.isStale, passSchedules: true },
      };

    case "SET_SATELLITES_LOADING":
      return {
        ...state,
        loading: { ...state.loading, satellites: action.payload },
      };

    case "SET_PASS_SCHEDULES_LOADING":
      return {
        ...state,
        loading: { ...state.loading, passSchedules: action.payload },
      };

    default:
      return state;
  }
};
