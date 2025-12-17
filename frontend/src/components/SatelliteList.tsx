import { type Satellite } from "../api/schedulerApi";

type Props = {
  satellites: Satellite[];
  loading?: boolean;
  error?: string | null;
};

const SatelliteList = ({ satellites, loading, error }: Props) => {
  if (loading) return <div>Loading satellites…</div>;
  if (error) return <div className="text-red-700">{error}</div>;
  if (!satellites.length) return <div>No satellites found.</div>;

  return (
    <div className="overflow-auto max-h-96">
      <ul className="flex flex-col gap-2 list-none p-0 m-0">
        {satellites.map((s) => (
          <li
            key={s.norad_id}
            className="p-3 border border-slate-200 rounded-lg bg-slate-50 flex flex-col gap-2"
          >
            <div className="flex justify-between items-baseline">
              <strong className="text-slate-900">{s.name}</strong>
              <span className="text-slate-600 text-sm">NORAD {s.norad_id}</span>
            </div>
            <div className="text-slate-600">
              {s.description || "No description"}
            </div>
            <div className="flex gap-3 text-sm text-slate-600">
              <span>TLEs: {s.tles.length}</span>
              <span>Passes: {s.pass_schedules.length}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SatelliteList;
