"""
LLM Client for code generation.
Supports both real OpenAI API and Mock mode for testing.
"""
from typing import Optional
from datetime import datetime

from app.agent.config import config


class LLMClient:
    """Client for LLM code generation with OpenAI API."""

    def __init__(self, use_mock: bool = config.USE_MOCK_LLM):
        """
        Initialize LLM client.

        Args:
            use_mock: If True, use mock responses instead of real API
        """
        self.use_mock = use_mock
        self.api_key = config.OPENAI_API_KEY
        self.default_model = config.DEFAULT_LLM_MODEL

        if not use_mock:
            try:
                import openai
                openai.api_key = self.api_key
                self.openai = openai
            except ImportError:
                raise ImportError("openai package required for real API mode")

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate code using LLM.

        Args:
            prompt: The prompt for code generation
            model: Model to use (default: gpt-4)
            max_tokens: Max tokens in response

        Returns:
            Generated code as string
        """
        model = model or self.default_model
        max_tokens = max_tokens or config.MAX_TOKENS_PER_REQUEST

        if self.use_mock:
            return self._generate_mock(prompt)

        # Real OpenAI API call
        response = self.openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert Python programmer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def _generate_mock(self, prompt: str) -> str:
        """
        Generate mock code for testing.

        Args:
            prompt: The prompt (used to determine response type)

        Returns:
            Mock generated code
        """
        # Simple mock: return a basic Python function
        if "web" in prompt.lower() or "flask" in prompt.lower():
            return '''
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
'''
        elif "cli" in prompt.lower() or "command" in prompt.lower():
            return '''
import argparse

def main():
    parser = argparse.ArgumentParser(description='CLI Tool')
    parser.add_argument('--input', help='Input file')
    args = parser.parse_args()
    print(f"Processing: {args.input}")

if __name__ == '__main__':
    main()
'''
        else:
            return '''
def process_data(data):
    """Process input data."""
    result = []
    for item in data:
        result.append(item * 2)
    return result
'''

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for
            model: Model to use for tokenization

        Returns:
            Number of tokens
        """
        model = model or self.default_model

        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(model)
        except ImportError:
            # Fallback: rough estimate (1 token ~= 0.75 words)
            return int(len(text.split()) * 1.3)
        except KeyError:
            try:
                import tiktoken
                encoding = tiktoken.get_encoding("cl100k_base")
            except ImportError:
                return int(len(text.split()) * 1.3)

        return len(encoding.encode(text))

    def calculate_cost(self, tokens: int, model: Optional[str] = None) -> int:
        """
        Calculate cost in cents for token usage.

        Args:
            tokens: Number of tokens
            model: Model used

        Returns:
            Cost in cents (integer)
        """
        model = model or self.default_model

        # Pricing per 1K tokens (in cents)
        pricing = {
            "gpt-4": 3,  # $0.03 per 1K tokens
            "gpt-4-32k": 6,
            "gpt-3.5-turbo": 0.2,  # $0.002 per 1K tokens
        }

        cost_per_1k = pricing.get(model, 3)  # Default to gpt-4 pricing
        return int((tokens / 1000) * cost_per_1k)

    def log_call(
        self,
        prompt: str,
        response: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_cents: int,
    ) -> dict:
        """
        Create log entry for LLM call.

        Args:
            prompt: The prompt used
            response: The response received
            model: Model used
            prompt_tokens: Tokens in prompt
            completion_tokens: Tokens in completion
            cost_cents: Cost in cents

        Returns:
            Dictionary with call metadata
        """
        return {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_cents": cost_cents,
            "timestamp": datetime.utcnow().isoformat(),
        }
