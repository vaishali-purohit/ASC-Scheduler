import React from "react";
import type { GridItem } from "../../types";

interface TwoColumnGridProps {
  items: GridItem[];
  loading?: boolean;
  error?: string | null;
  emptyMessage?: string;
  className?: string;
  stickyHeader?: React.ReactNode;
  maxHeight?: string;
  showScrollbar?: boolean;
}

/**
 * TwoColumnGrid component for displaying items in a responsive 2-column layout
 * Handles loading, error, and empty states with scrollable container and sticky headers
 */
const TwoColumnGrid: React.FC<TwoColumnGridProps> = ({
  items,
  loading,
  error,
  emptyMessage = "No items found.",
  className = "",
  stickyHeader,
  maxHeight = "max-h-[600px]",
  showScrollbar = true,
}) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-slate-600">Loading data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8 px-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md">
          <div className="flex gap-3">
            <svg
              className="w-5 h-5 text-red-600 shrink-0 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h3 className="font-medium text-red-900 mb-1">Error</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!items.length) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-slate-400 mb-3"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <p className="text-slate-600 text-sm">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className} relative`}>
      {/* Sticky Header */}
      {stickyHeader && (
        <div className="sticky top-0 z-10 bg-white border-b border-slate-200 px-4 py-3 shadow-sm">
          {stickyHeader}
        </div>
      )}

      {/* Scrollable Content Container */}
      <div
        className={`${maxHeight} ${
          showScrollbar
            ? "overflow-y-auto overflow-x-hidden"
            : "overflow-y-hidden"
        }`}
        style={{
          scrollbarWidth: "thin",
          scrollbarColor: "rgb(148 163 184) rgb(248 250 252)",
        }}
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="group bg-slate-50 border border-slate-200 rounded-lg p-4 hover:bg-white hover:border-slate-300 hover:shadow-sm transition-all duration-200"
            >
              {item.content}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TwoColumnGrid;
