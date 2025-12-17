import { useEffect, useState } from "react";

import {
  fetchPassSchedules,
  fetchSatellites,
  refreshTle,
  generatePassSchedules,
  type Satellite,
  type PassSchedule,
} from "../api/schedulerApi";
import PassScheduleTable from "../components/PassScheduleTable";
import Card from "../components/Card";
import Layout from "../components/Layout";
import SatelliteList from "../components/SatelliteList";

const Dashboard = () => {
  const [satellites, setSatellites] = useState<Satellite[]>([]);
  const [passes, setPasses] = useState<PassSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        setError(null);
        const [satData, passData] = await Promise.all([
          fetchSatellites(),
          fetchPassSchedules(),
        ]);
        setSatellites(satData);
        setPasses(passData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await refreshTle();
      const [satData, passData] = await Promise.all([
        fetchSatellites(),
        fetchPassSchedules(),
      ]);
      setSatellites(satData);
      setPasses(passData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  const handleGeneratePasses = async () => {
    try {
      setGenerating(true);
      await generatePassSchedules("sample", 7);
      const passData = await fetchPassSchedules();
      setPasses(passData);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate pass schedules"
      );
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Layout>
      <div className="flex justify-end gap-2">
        <button
          onClick={handleGeneratePasses}
          disabled={generating}
          className="px-3 py-2 bg-blue-600 text-slate-50 rounded-lg border border-slate-300 font-semibold hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
        >
          {generating ? "Generating…" : "Generate Passes"}
        </button>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-3 py-2 bg-slate-900 text-slate-50 rounded-lg border border-slate-300 font-semibold hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
        >
          {refreshing ? "Refreshing…" : "Refresh TLEs"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card title={`Satellites (${satellites.length})`}>
          <SatelliteList
            satellites={satellites}
            loading={loading}
            error={error}
          />
        </Card>

        <Card title="Pass Schedules">
          <PassScheduleTable data={passes} loading={loading} error={error} />
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;
