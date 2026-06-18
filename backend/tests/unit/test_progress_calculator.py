"""Unit tests for ProgressCalculator (Sprint 3).

Tests progress percentage calculation and ETA estimation.
Based on docs/design/agent-progress-state-machine.md.

Run: pytest tests/unit/test_progress_calculator.py -v
"""

from datetime import UTC, datetime

import pytest
from app.core.progress_calculator import ProgressCalculator
from app.schemas.agent_progress import (
    AgentStep,
    StepState,
    StepStatus,
)

pytestmark = pytest.mark.asyncio


class TestProgressPercentage:
    """Test progress percentage calculation with step weights."""

    def test_all_pending_returns_zero(self):
        """Test: 所有步骤 pending 返回 0%"""
        steps = [StepState(name=step, status=StepStatus.PENDING) for step in AgentStep.ordered()]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 0.0

    def test_all_completed_returns_hundred(self):
        """Test: 所有步骤 completed 返回 100%"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=step,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=1000,
            )
            for step in AgentStep.ordered()
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 100.0

    def test_first_step_completed_returns_15_percent(self):
        """Test: Researcher 完成返回 15%"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(name=AgentStep.PLANNER, status=StepStatus.PENDING),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 15.0

    def test_coder_completed_returns_70_percent(self):
        """Test: Researcher + Planner + Coder 完成返回 70%"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(
                name=AgentStep.PLANNER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(
                name=AgentStep.CODER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=30000,
            ),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 70.0  # 0.15 + 0.15 + 0.40

    def test_step_weights_sum_to_one(self):
        """Test: 步骤权重总和为 1.0"""
        from app.core.progress_calculator import STEP_WEIGHTS

        assert sum(STEP_WEIGHTS.values()) == 1.0

    def test_running_step_counts_as_partial(self):
        """Test: RUNNING 状态算作 50% 完成"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(
                name=AgentStep.PLANNER,
                status=StepStatus.RUNNING,
                started_at=now,
            ),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 22.5  # 15 + (15 * 0.5)

    def test_skipped_step_counts_as_completed(self):
        """Test: SKIPPED 状态算作 100% 完成"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(
                name=AgentStep.PLANNER,
                status=StepStatus.SKIPPED,
                started_at=now,
                completed_at=now,
            ),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 30.0  # 15 + 15


class TestETAEstimation:
    """Test ETA estimation with historical data."""

    def test_eta_with_sufficient_history_uses_p50(self):
        """Test: 历史数据 ≥ 5 次时使用 P50 中位数"""
        history = [
            {"step": "researcher", "duration_ms": 10000},
            {"step": "researcher", "duration_ms": 12000},
            {"step": "researcher", "duration_ms": 11000},
            {"step": "researcher", "duration_ms": 13000},
            {"step": "researcher", "duration_ms": 11500},
        ]
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.RUNNING,
                started_at=now,
            ),
            StepState(name=AgentStep.PLANNER, status=StepStatus.PENDING),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        eta = ProgressCalculator.estimate_eta(steps, history)
        # P50 = 11500ms = 11.5s
        # researcher running (50%): 11.5 * 0.5 = 5.75
        # + 4 pending steps: 11.5 * 4 = 46
        # Total: 51.75s ≈ 51s (int)
        assert eta == 51

    def test_eta_with_insufficient_history_uses_static_fallback(self):
        """Test: 历史数据 < 5 次时使用静态 fallback（30s/step）"""
        history = [
            {"step": "researcher", "duration_ms": 10000},
            {"step": "researcher", "duration_ms": 12000},
        ]  # < 5 samples
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(name=AgentStep.PLANNER, status=StepStatus.PENDING),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        eta = ProgressCalculator.estimate_eta(steps, history)
        # 4 remaining steps * 30s = 120s
        assert eta == 120

    def test_eta_all_completed_returns_zero(self):
        """Test: 所有步骤完成返回 ETA = 0"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=step,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            )
            for step in AgentStep.ordered()
        ]
        eta = ProgressCalculator.estimate_eta(steps, [])
        assert eta == 0

    def test_eta_no_active_steps_returns_none(self):
        """Test: 无活跃步骤返回 None"""
        steps = [StepState(name=step, status=StepStatus.PENDING) for step in AgentStep.ordered()]
        eta = ProgressCalculator.estimate_eta(steps, [])
        assert eta is None


class TestBoundaryConditions:
    """Test edge cases and boundary conditions."""

    def test_empty_steps_list_returns_zero(self):
        """Test: 空步骤列表返回 0%"""
        percentage = ProgressCalculator.calculate_percentage([])
        assert percentage == 0.0

    def test_failed_step_stops_counting(self):
        """Test: FAILED 步骤后不计算后续步骤"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(
                name=AgentStep.PLANNER,
                status=StepStatus.FAILED,
                started_at=now,
                completed_at=now,
                error_message="Planning failed",
            ),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        # Only count up to failed step
        assert percentage == 30.0  # 15 + 15

    def test_retrying_step_counts_as_running(self):
        """Test: RETRYING 状态等同于 RUNNING"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(
                name=AgentStep.PLANNER,
                status=StepStatus.RETRYING,
                started_at=now,
                retry_count=1,
            ),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 22.5  # 15 + (15 * 0.5)

    def test_cancelled_step_stops_counting(self):
        """Test: CANCELLED 步骤后不计算后续步骤"""
        now = datetime.now(UTC)
        steps = [
            StepState(
                name=AgentStep.RESEARCHER,
                status=StepStatus.COMPLETED,
                started_at=now,
                completed_at=now,
                duration_ms=10000,
            ),
            StepState(
                name=AgentStep.PLANNER,
                status=StepStatus.CANCELLED,
                started_at=now,
                completed_at=now,
            ),
            StepState(name=AgentStep.CODER, status=StepStatus.PENDING),
            StepState(name=AgentStep.REVIEWER, status=StepStatus.PENDING),
            StepState(name=AgentStep.TESTER, status=StepStatus.PENDING),
        ]
        percentage = ProgressCalculator.calculate_percentage(steps)
        assert percentage == 30.0  # 15 + 15
