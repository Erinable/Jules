"""Progress calculation utilities (Sprint 3).

Pure functions for calculating progress percentage and ETA.
Based on docs/design/agent-progress-state-machine.md.
"""

from typing import Any

from app.schemas.agent_progress import (
    AgentStep,
    StepState,
    StepStatus,
)

# Step weights (sum = 1.0)
# Based on typical execution time distribution
STEP_WEIGHTS = {
    AgentStep.RESEARCHER: 0.15,
    AgentStep.PLANNER: 0.15,
    AgentStep.CODER: 0.40,
    AgentStep.REVIEWER: 0.15,
    AgentStep.TESTER: 0.15,
}

# Static fallback duration per step when history < 5 (in seconds)
STATIC_FALLBACK_DURATION_SECONDS = 30


class ProgressCalculator:
    """Pure functions for progress calculation (no state, no I/O)."""

    @staticmethod
    def calculate_percentage(steps: list[StepState]) -> float:
        """Calculate overall progress percentage based on step statuses.

        Rules:
        - COMPLETED / SKIPPED: 100% of weight
        - RUNNING / RETRYING: 50% of weight
        - PENDING: 0% of weight
        - FAILED / CANCELLED: 100% of weight, stop counting after

        Args:
            steps: List of step states (must be in order)

        Returns:
            Progress percentage (0.0 - 100.0)
        """
        if not steps:
            return 0.0

        total = 0.0

        for step in steps:
            weight = STEP_WEIGHTS.get(step.name, 0.0)

            if step.status in (StepStatus.COMPLETED, StepStatus.SKIPPED):
                # Full credit
                total += weight * 100
            elif step.status in (StepStatus.RUNNING, StepStatus.RETRYING):
                # Half credit (in progress)
                total += weight * 50
            elif step.status in (StepStatus.FAILED, StepStatus.CANCELLED):
                # Full credit for this step, but stop counting
                total += weight * 100
                break
            # PENDING: no credit, continue

        return round(total, 1)

    @staticmethod
    def estimate_eta(steps: list[StepState], history: list[dict[str, Any]]) -> int | None:
        """Estimate remaining time in seconds.

        Uses P50 median from historical data when ≥ 5 samples available,
        otherwise uses static fallback (30s per step).

        Args:
            steps: List of step states (must be in order)
            history: List of historical step durations
                     [{"step": "researcher", "duration_ms": 10000}, ...]

        Returns:
            Estimated seconds remaining, or None if no active steps,
            or 0 if all steps completed
        """
        # Count remaining steps
        remaining_steps = []
        found_active = False
        has_started = False

        for step in steps:
            if step.status in (StepStatus.COMPLETED, StepStatus.SKIPPED):
                has_started = True
                continue
            elif step.status in (StepStatus.RUNNING, StepStatus.RETRYING):
                # Current step: estimate 50% remaining
                remaining_steps.append((step.name, 0.5))
                found_active = True
                has_started = True
            elif step.status == StepStatus.PENDING:
                # Future step: full duration
                remaining_steps.append((step.name, 1.0))
            else:
                # FAILED / CANCELLED: stop counting
                break

        if not remaining_steps:
            return 0

        if not found_active and not has_started:
            # Not started yet; ETA cannot be estimated from execution state.
            return None

        # Use historical P50 if available (≥ 5 samples)
        if len(history) >= 5:
            durations = [h["duration_ms"] for h in history]
            durations.sort()
            p50_ms = durations[len(durations) // 2]
            p50_seconds = p50_ms / 1000

            eta_seconds = sum(p50_seconds * factor for _, factor in remaining_steps)
            return int(eta_seconds)

        # Use static fallback
        eta_seconds = sum(
            STATIC_FALLBACK_DURATION_SECONDS * factor for _, factor in remaining_steps
        )
        return int(eta_seconds)
