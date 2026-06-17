"""
Code quality analyzer using static analysis tools.
"""
from typing import Dict
import ast
import re


class CodeAnalyzer:
    """Analyzer for code quality metrics."""

    def analyze(self, code: str, language: str = "python") -> Dict:
        """
        Analyze code quality.

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Dictionary with quality metrics
        """
        if language.lower() == "python":
            return self._analyze_python(code)
        else:
            # Default metrics for unsupported languages
            return {
                "avg_complexity": 1.0,
                "maintainability_index": 100.0,
                "security_issues": 0,
            }

    def _analyze_python(self, code: str) -> Dict:
        """
        Analyze Python code.

        Args:
            code: Python source code

        Returns:
            Dictionary with metrics
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {
                "avg_complexity": 999.0,
                "maintainability_index": 0.0,
                "security_issues": 1,
            }

        complexity = self.calculate_complexity(code)
        maintainability = self.calculate_maintainability(code)
        security_issues = self.detect_security_issues(code)

        return {
            "avg_complexity": complexity,
            "maintainability_index": maintainability,
            "security_issues": security_issues,
        }

    def calculate_complexity(self, code: str) -> float:
        """
        Calculate cyclomatic complexity.

        Args:
            code: Source code

        Returns:
            Average complexity score
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 999.0

        complexities = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_function_complexity(node)
                complexities.append(complexity)

        if not complexities:
            return 1.0

        return sum(complexities) / len(complexities)

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate complexity for a single function.

        Args:
            node: Function AST node

        Returns:
            Complexity score
        """
        complexity = 1

        for child in ast.walk(node):
            # Count decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity

    def calculate_maintainability(self, code: str) -> float:
        """
        Calculate maintainability index.

        Simplified version of Maintainability Index:
        MI = max(0, (171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(L)) * 100 / 171)

        Where:
        - V = Halstead Volume (approximated)
        - G = Cyclomatic Complexity
        - L = Lines of Code

        Args:
            code: Source code

        Returns:
            Maintainability index (0-100)
        """
        import math

        lines = [line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')]
        loc = len(lines)

        if loc == 0:
            return 100.0

        complexity = self.calculate_complexity(code)

        # Simplified Halstead volume approximation
        # Count operators and operands
        operators = len(re.findall(r'[\+\-\*\/\=\<\>\!]', code))
        operands = len(re.findall(r'\b\w+\b', code))
        volume = (operators + operands) * math.log2(operators + operands + 1)

        # Calculate MI
        try:
            mi = max(0, (171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(loc)) * 100 / 171)
        except (ValueError, ZeroDivisionError):
            mi = 50.0  # Default mid-range value

        return min(100.0, max(0.0, mi))

    def detect_security_issues(self, code: str) -> int:
        """
        Detect potential security issues.

        Args:
            code: Source code

        Returns:
            Count of security issues found
        """
        issues = 0

        # Check for dangerous patterns
        dangerous_patterns = [
            r'eval\(',  # eval() usage
            r'exec\(',  # exec() usage
            r'__import__\(',  # dynamic imports
            r'os\.system\(',  # shell command execution
            r'subprocess\.call\(',  # subprocess without shell=False
            r'pickle\.loads?\(',  # pickle deserialization
            r'yaml\.load\(',  # unsafe YAML loading
            r'assert\s',  # assertions in production code
        ]

        for pattern in dangerous_patterns:
            matches = re.findall(pattern, code)
            issues += len(matches)

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\']',
            r'api_key\s*=\s*["\']',
            r'secret\s*=\s*["\']',
            r'token\s*=\s*["\']',
        ]

        for pattern in secret_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            issues += len(matches)

        return issues
