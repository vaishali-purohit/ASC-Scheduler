import { type PassSchedule } from "../api/schedulerApi";

type Props = {
  data: PassSchedule[];
  loading?: boolean;
  error?: string | null;
};

const PassScheduleTable = ({ data, loading, error }: Props) => {
  if (loading) return <div>Loading pass schedules…</div>;
  if (error) return <div className="text-red-700">{error}</div>;
  if (!data.length) return <div>No pass schedules found.</div>;

  return (
    <div className="overflow-auto max-h-96">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="p-3 text-left bg-slate-50 font-bold border-b border-slate-200 sticky top-0 z-10 shadow-sm">
              Satellite
            </th>
            <th className="p-3 text-left bg-slate-50 font-bold border-b border-slate-200 sticky top-0 z-10 shadow-sm">
              Ground Station
            </th>
            <th className="p-3 text-left bg-slate-50 font-bold border-b border-slate-200 sticky top-0 z-10 shadow-sm">
              Start
            </th>
            <th className="p-3 text-left bg-slate-50 font-bold border-b border-slate-200 sticky top-0 z-10 shadow-sm">
              End
            </th>
            <th className="p-3 text-left bg-slate-50 font-bold border-b border-slate-200 sticky top-0 z-10 shadow-sm">
              Status
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((p) => (
            <tr key={p.pass_id} className="hover:bg-slate-50">
              <td className="p-3 border-b border-slate-200 text-left">
                {p.satellite_name || p.satellite_norad_id} (
                {p.satellite_norad_id})
              </td>
              <td className="p-3 border-b border-slate-200 text-left">
                {p.ground_station}
              </td>
              <td className="p-3 border-b border-slate-200 text-left">
                {p.start_time ? new Date(p.start_time).toLocaleString() : "—"}
              </td>
              <td className="p-3 border-b border-slate-200 text-left">
                {p.end_time ? new Date(p.end_time).toLocaleString() : "—"}
              </td>
              <td className="p-3 border-b border-slate-200 text-left">
                {p.status}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PassScheduleTable;
