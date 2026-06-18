"""
ProgressRepository (Sprint 3).

Data access layer for progress tracking tables:
- execution_progress
- execution_transitions
- execution_logs

Based on docs/design/progress-tracking-api.md and 003_progress_tables.py migration.
"""

from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.progress import ExecutionLog, ExecutionProgress, ExecutionTransition


class ProgressRepository:
    """Repository for execution progress, transitions, and logs."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── execution_progress ──────────────────────────────────────────

    def create_progress(
        self,
        run_id: str,
        user_id: str,
        status: str,
        steps_json: list[dict],
        current_step: str | None = None,
        overall_percentage: float = 0.0,
        eta_seconds: int | None = None,
    ) -> ExecutionProgress:
        now = datetime.utcnow()
        progress = ExecutionProgress(
            run_id=run_id,
            user_id=user_id,
            status=status,
            current_step=current_step,
            overall_percentage=overall_percentage,
            eta_seconds=eta_seconds,
            steps_json=steps_json,
            started_at=now,
            updated_at=now,
        )
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_progress(self, run_id: str) -> ExecutionProgress | None:
        return self.db.query(ExecutionProgress).filter(ExecutionProgress.run_id == run_id).first()

    def update_progress(self, run_id: str, **fields) -> bool:
        fields["updated_at"] = datetime.utcnow()
        result = (
            self.db.query(ExecutionProgress)
            .filter(ExecutionProgress.run_id == run_id)
            .update(fields)
        )
        self.db.commit()
        return result > 0

    def list_progress_by_user(
        self,
        user_id: str,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ExecutionProgress], int]:
        q = self.db.query(ExecutionProgress).filter(ExecutionProgress.user_id == user_id)
        if status:
            q = q.filter(ExecutionProgress.status == status)
        total = q.count()
        items = q.order_by(desc(ExecutionProgress.started_at)).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def list_all_progress(
        self,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ExecutionProgress], int]:
        q = self.db.query(ExecutionProgress)
        if status:
            q = q.filter(ExecutionProgress.status == status)
        total = q.count()
        items = q.order_by(desc(ExecutionProgress.started_at)).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def delete_progress(self, run_id: str) -> bool:
        result = self.db.query(ExecutionProgress).filter(ExecutionProgress.run_id == run_id).delete()
        self.db.commit()
        return result > 0

    # ── execution_transitions ───────────────────────────────────────

    def add_transition(
        self,
        run_id: str,
        to_status: str,
        from_status: str | None = None,
        step: str | None = None,
        metadata: dict | None = None,
    ) -> ExecutionTransition:
        transition = ExecutionTransition(
            run_id=run_id,
            from_status=from_status,
            to_status=to_status,
            step=step,
            timestamp=datetime.utcnow(),
            metadata_json=metadata,
        )
        self.db.add(transition)
        self.db.commit()
        self.db.refresh(transition)
        return transition

    def get_transitions(
        self,
        run_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[ExecutionTransition]:
        q = self.db.query(ExecutionTransition).filter(ExecutionTransition.run_id == run_id)
        if start_time:
            q = q.filter(ExecutionTransition.timestamp >= start_time)
        if end_time:
            q = q.filter(ExecutionTransition.timestamp <= end_time)
        return q.order_by(ExecutionTransition.timestamp).all()

    # ── execution_logs ──────────────────────────────────────────────

    def add_log(
        self,
        run_id: str,
        step: str,
        level: str,
        message: str,
        metadata: dict | None = None,
    ) -> ExecutionLog:
        max_seq = (
            self.db.query(func.max(ExecutionLog.sequence_num))
            .filter(ExecutionLog.run_id == run_id)
            .scalar()
        )
        next_seq = (max_seq or 0) + 1
        log = ExecutionLog(
            run_id=run_id,
            step=step,
            level=level,
            message=message,
            sequence_num=next_seq,
            timestamp=datetime.utcnow(),
            metadata_json=metadata,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_logs(
        self,
        run_id: str,
        step: str | None = None,
        level: str | None = None,
        page: int = 1,
        limit: int = 50,
        order: str = "asc",
    ) -> tuple[list[ExecutionLog], int]:
        q = self.db.query(ExecutionLog).filter(ExecutionLog.run_id == run_id)
        if step:
            q = q.filter(ExecutionLog.step == step)
        if level:
            q = q.filter(ExecutionLog.level == level)
        total = q.count()
        order_col = ExecutionLog.sequence_num if order == "asc" else desc(ExecutionLog.sequence_num)
        items = q.order_by(order_col).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def get_log_count(self, run_id: str) -> int:
        return (
            self.db.query(func.count(ExecutionLog.id))
            .filter(ExecutionLog.run_id == run_id)
            .scalar()
        ) or 0
