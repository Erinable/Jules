/**
 * ProgressBar Component (Sprint 3 - Phase 1 MVP)
 *
 * Reusable progress bar component showing percentage and ETA.
 * Based on docs/design/progress-ui-prototype.md
 */

interface ProgressBarProps {
  percentage: number;
  eta: number | null; // in seconds
  className?: string;
}

/**
 * Format seconds to human-readable duration (e.g., "2m 30s", "1h 15m")
 */
function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  if (minutes < 60) {
    return remainingSeconds > 0
      ? `${minutes}m ${remainingSeconds}s`
      : `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

export function ProgressBar({
  percentage,
  eta,
  className = "",
}: ProgressBarProps) {
  // Clamp percentage between 0 and 100
  const clampedPercentage = Math.min(100, Math.max(0, percentage));

  return (
    <div className={`w-full ${className}`}>
      {/* Progress bar track */}
      <div className="relative h-6 bg-gray-200 rounded-full overflow-hidden">
        {/* Progress bar fill */}
        <div
          className="absolute top-0 left-0 h-full bg-blue-500 transition-all duration-300 ease-out"
          style={{ width: `${clampedPercentage}%` }}
          role="progressbar"
          aria-valuenow={clampedPercentage}
          aria-valuemin={0}
          aria-valuemax={100}
        />

        {/* Percentage text overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-medium text-gray-700">
            {clampedPercentage.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* ETA display */}
      {eta !== null && eta > 0 && (
        <div className="mt-2 text-sm text-gray-600 text-right">
          预计剩余: {formatDuration(eta)}
        </div>
      )}
    </div>
  );
}
