import React from "react";

interface InfoRowProps {
  label: string;
  value: React.ReactNode;
  className?: string;
}

/**
 * InfoRow component for consistent key-value pair display
 */
const InfoRow: React.FC<InfoRowProps> = ({ label, value, className = "" }) => (
  <div className={`flex justify-between items-baseline gap-2 ${className}`}>
    <span className="text-sm text-slate-500 font-medium">{label}:</span>
    <span className="text-sm text-slate-900">{value}</span>
  </div>
);

export default InfoRow;
