import React from "react";

interface CardProps {
  title?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  stickyHeader?: boolean;
  subtitle?: string;
}

/**
 * Card component for consistent content containers
 * Supports optional title, action buttons, and sticky headers
 */
const Card: React.FC<CardProps> = ({
  title,
  actions,
  children,
  className = "",
  stickyHeader = false,
  subtitle,
}) => (
  <section
    className={`bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-shadow ${className} ${
      stickyHeader ? "flex flex-col max-h-200" : "p-6"
    }`}
  >
    {(title || actions || subtitle) && (
      <header
        className={`flex items-center justify-between gap-3 ${
          stickyHeader
            ? "sticky top-0 z-10 bg-white border-b border-slate-100 px-6 py-4 shadow-sm"
            : "mb-4 pb-3 border-b border-slate-100"
        }`}
      >
        <div className="flex-1 min-w-0">
          {title && (
            <h2 className="text-xl font-semibold text-slate-900 truncate">
              {title}
            </h2>
          )}
          {subtitle && (
            <p className="text-sm text-slate-600 mt-1">{subtitle}</p>
          )}
        </div>
        {actions && <div className="flex gap-2 shrink-0">{actions}</div>}
      </header>
    )}
    <div className={stickyHeader ? "flex-1 overflow-hidden" : ""}>
      {children}
    </div>
  </section>
);

export default Card;
