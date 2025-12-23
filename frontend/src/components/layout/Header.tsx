import React from "react";

interface HeaderProps {
  onGeneratePasses: () => void;
  onRefreshTLEs: () => void;
}

/**
 * Header component with title, description, and action buttons
 */
const Header: React.FC<HeaderProps> = ({ onGeneratePasses, onRefreshTLEs }) => (
  <header className="mb-8">
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            ASC Scheduler
          </h1>
          <p className="text-slate-600">
            Track satellites, TLEs, and scheduled passes.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={onGeneratePasses}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-sm hover:shadow transition-all duration-200 flex items-center gap-2"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Generate Passes
          </button>
          <button
            onClick={onRefreshTLEs}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white font-medium rounded-lg shadow-sm hover:shadow transition-all duration-200 flex items-center gap-2"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Refresh TLEs
          </button>
        </div>
      </div>
    </div>
  </header>
);

export default Header;
