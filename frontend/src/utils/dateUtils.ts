/**
 * Formats a date string into a human-readable exact time format
 * @param dateString - ISO date string
 * @returns Formatted date string (e.g., "December 16, 2025 at 5:17 PM")
 */
export const formatExactTime = (dateString: string): string => {
  if (!dateString) return "";

  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
};
