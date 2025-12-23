import { requestManager } from "../utils/requestManager";

const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export type Tle = {
  tle_id: number;
  line1: string;
  line2: string;
  timestamp: string | null;
};

export type PassSchedule = {
  pass_id: number;
  satellite_norad_id: number;
  satellite_name?: string | null;
  ground_station: string;
  start_time: string | null;
  end_time: string | null;
  status: string;
};

export type Satellite = {
  norad_id: number;
  name: string;
  description?: string | null;
  tles: Tle[];
  pass_schedules: PassSchedule[];
};

interface RequestOptions {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  signal?: AbortSignal;
  priority?: "critical" | "normal" | "low";
  method?: string;
  headers?: Record<string, string>;
  body?: string;
}

/**
 * Enhanced request function with caching, debouncing, and timeout handling
 */
const request = async <T>(
  path: string,
  requestOptions?: RequestOptions
): Promise<T> => {
  const cacheKey = `${path}:${JSON.stringify(requestOptions || {})}`;

  try {
    return await requestManager.executeDebounced(
      cacheKey,
      async () => {
        const res = await fetch(`${API_BASE}${path}`, {
          headers: { "Content-Type": "application/json" },
          method: requestOptions?.method || "GET",
          body: requestOptions?.body,
        });
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || res.statusText);
        }
        return res.json();
      },
      {
        timeout: 30000, // 30 seconds (increased from 10s)
        retries: 3,
        retryDelay: 1000,
        priority: requestOptions?.priority || "normal",
      }
    );
  } catch (error) {
    console.error(`API Request failed for ${path}:`, error);
    throw error;
  }
};

export const fetchSatellites = async (): Promise<Satellite[]> =>
  request("/satellites", {
    priority: "critical", // Critical for initial dashboard load
  });

export const fetchPassSchedules = async (): Promise<PassSchedule[]> =>
  request("/pass-schedules", {
    priority: "critical", // Critical for initial dashboard load
  });

export const refreshTle = async (
  group = "active"
): Promise<{
  status: string;
  message: string;
  summary: unknown;
}> =>
  request(`/tle/refresh?group=${encodeURIComponent(group)}`, {
    method: "POST",
    priority: "low", // Background operation
  });

export const generatePassSchedules = async (
  method = "sample",
  days_ahead = 7
): Promise<{
  status: string;
  message: string;
  summary: unknown;
}> =>
  request(
    `/pass-schedules/generate?method=${encodeURIComponent(
      method
    )}&days_ahead=${days_ahead}`,
    {
      method: "POST",
      priority: "normal", // User-initiated operation
    }
  );
