"""
Agent configuration settings.
"""

import os


class AgentConfig:
    """Configuration for Agent system."""

    # Concurrency settings
    MAX_CONCURRENT_AGENTS: int = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))

    # Retry settings
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_SECONDS: list[int] = [1, 5, 15]

    # LLM settings
    DEFAULT_LLM_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    MAX_TOKENS_PER_REQUEST: int = 4000
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Use mock mode if no API key provided
    USE_MOCK_LLM: bool = not bool(OPENAI_API_KEY)

    # Task settings
    TASK_TIMEOUT_SECONDS: int = 300  # 5 minutes

    # Queue settings
    QUEUE_POLL_INTERVAL_SECONDS: int = 5


# Global config instance
config = AgentConfig()
