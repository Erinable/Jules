"""
Tests for LLM Client
"""

from unittest.mock import patch

from app.agent.llm_client import LLMClient


class TestLLMClient:
    """Test suite for LLM Client."""

    def test_init_mock_mode(self):
        """Test client initialization in mock mode."""
        client = LLMClient(use_mock=True)
        assert client.use_mock is True

    def test_generate_mock_web_app(self):
        """Test mock generation for web app."""
        client = LLMClient(use_mock=True)
        prompt = "Create a Flask web application"
        code = client.generate(prompt)

        assert "flask" in code.lower()
        assert "def" in code
        assert "app = Flask" in code

    def test_generate_mock_cli_tool(self):
        """Test mock generation for CLI tool."""
        client = LLMClient(use_mock=True)
        prompt = "Create a CLI command line tool"
        code = client.generate(prompt)

        assert "argparse" in code.lower()
        assert "def main" in code

    def test_generate_mock_generic(self):
        """Test mock generation for generic code."""
        client = LLMClient(use_mock=True)
        prompt = "Create a data processing function"
        code = client.generate(prompt)

        assert "def" in code
        assert "return" in code

    def test_count_tokens(self):
        """Test token counting."""
        client = LLMClient(use_mock=True)
        text = "Hello world, this is a test"
        tokens = client.count_tokens(text)

        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_tokens_empty(self):
        """Test token counting with empty string."""
        client = LLMClient(use_mock=True)
        tokens = client.count_tokens("")

        assert tokens == 0

    def test_calculate_cost_gpt4(self):
        """Test cost calculation for GPT-4."""
        client = LLMClient(use_mock=True)
        cost = client.calculate_cost(1000, "gpt-4")

        assert cost == 3  # $0.03 per 1K tokens = 3 cents

    def test_calculate_cost_gpt35(self):
        """Test cost calculation for GPT-3.5."""
        client = LLMClient(use_mock=True)
        cost = client.calculate_cost(1000, "gpt-3.5-turbo")

        assert cost == 0  # $0.002 per 1K tokens = 0.2 cents, rounded to 0

    def test_calculate_cost_large_tokens(self):
        """Test cost calculation for large token count."""
        client = LLMClient(use_mock=True)
        cost = client.calculate_cost(10000, "gpt-4")

        assert cost == 30  # 10K tokens * $0.03 = 30 cents

    def test_log_call(self):
        """Test call logging."""
        client = LLMClient(use_mock=True)
        log = client.log_call(
            prompt="test prompt",
            response="test response",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=20,
            cost_cents=1,
        )

        assert log["model"] == "gpt-4"
        assert log["prompt_tokens"] == 10
        assert log["completion_tokens"] == 20
        assert log["total_tokens"] == 30
        assert log["cost_cents"] == 1
        assert "timestamp" in log

    @patch("app.agent.llm_client.config")
    def test_init_uses_config(self, mock_config):
        """Test that client uses config values."""
        mock_config.USE_MOCK_LLM = True
        mock_config.OPENAI_API_KEY = ""
        mock_config.DEFAULT_LLM_MODEL = "gpt-4"

        client = LLMClient()

        assert client.use_mock is True
        assert client.default_model == "gpt-4"

    def test_generate_with_custom_model(self):
        """Test generation with custom model."""
        client = LLMClient(use_mock=True)
        code = client.generate("test", model="gpt-3.5-turbo")

        assert isinstance(code, str)
        assert len(code) > 0

    def test_generate_with_max_tokens(self):
        """Test generation with max tokens."""
        client = LLMClient(use_mock=True)
        code = client.generate("test", max_tokens=100)

        assert isinstance(code, str)
        assert len(code) > 0

    def test_count_tokens_fallback_when_tiktoken_unavailable(self):
        """Test token counting fallback when tiktoken not available."""
        client = LLMClient(use_mock=True)

        text = "Hello world this is a test"

        # Mock the import to raise ImportError
        with patch("builtins.__import__", side_effect=ImportError("No module named 'tiktoken'")):
            tokens = client.count_tokens(text)

            # Fallback estimate: ~1.3 tokens per word
            expected = int(len(text.split()) * 1.3)
            assert tokens == expected
