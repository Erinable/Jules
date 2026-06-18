"""
Tests for Code Analyzer
"""

from app.agent.analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    """Test suite for Code Analyzer."""

    def setup_method(self):
        """Setup for each test method."""
        self.analyzer = CodeAnalyzer()

    def test_analyze_simple_python_code(self):
        """Test analyzing simple Python code."""
        code = """
def hello():
    return "Hello, World!"
"""
        result = self.analyzer.analyze(code, "python")

        assert "avg_complexity" in result
        assert "maintainability_index" in result
        assert "security_issues" in result
        assert result["avg_complexity"] >= 1.0

    def test_analyze_syntax_error(self):
        """Test analyzing code with syntax error."""
        code = "def hello(:\n    pass"
        result = self.analyzer.analyze(code, "python")

        assert result["avg_complexity"] == 999.0
        assert result["maintainability_index"] == 0.0
        assert result["security_issues"] == 1

    def test_calculate_complexity_simple(self):
        """Test complexity calculation for simple function."""
        code = """
def add(a, b):
    return a + b
"""
        complexity = self.analyzer.calculate_complexity(code)

        assert complexity == 1.0  # No branches

    def test_calculate_complexity_with_if(self):
        """Test complexity calculation with if statement."""
        code = """
def check(x):
    if x > 0:
        return True
    return False
"""
        complexity = self.analyzer.calculate_complexity(code)

        assert complexity == 2.0  # 1 base + 1 if

    def test_calculate_complexity_with_multiple_branches(self):
        """Test complexity with multiple branches."""
        code = """
def process(x):
    if x > 0:
        if x < 10:
            return "small"
        return "large"
    elif x == 0:
        return "zero"
    else:
        return "negative"
"""
        complexity = self.analyzer.calculate_complexity(code)

        assert complexity >= 3.0

    def test_calculate_complexity_with_loops(self):
        """Test complexity with loops."""
        code = """
def sum_list(items):
    total = 0
    for item in items:
        if item > 0:
            total += item
    return total
"""
        complexity = self.analyzer.calculate_complexity(code)

        assert complexity >= 2.0  # for + if

    def test_calculate_maintainability_simple(self):
        """Test maintainability index for simple code."""
        code = """
def add(a, b):
    return a + b
"""
        mi = self.analyzer.calculate_maintainability(code)

        assert 0 <= mi <= 100
        assert mi > 50  # Simple code should have high MI

    def test_calculate_maintainability_complex(self):
        """Test maintainability index for complex code."""
        code = """
def complex_function(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
    return 0
"""
        mi = self.analyzer.calculate_maintainability(code)

        assert 0 <= mi <= 100
        assert mi < 70  # Complex code should have lower MI

    def test_calculate_maintainability_empty_code(self):
        """Test maintainability with empty code."""
        mi = self.analyzer.calculate_maintainability("")

        assert mi == 100.0

    def test_detect_security_issues_eval(self):
        """Test detecting eval() usage."""
        code = """
def dangerous(code):
    return eval(code)
"""
        issues = self.analyzer.detect_security_issues(code)

        assert issues >= 1

    def test_detect_security_issues_exec(self):
        """Test detecting exec() usage."""
        code = """
def dangerous(code):
    exec(code)
"""
        issues = self.analyzer.detect_security_issues(code)

        assert issues >= 1

    def test_detect_security_issues_os_system(self):
        """Test detecting os.system() usage."""
        code = """
import os
def dangerous(cmd):
    os.system(cmd)
"""
        issues = self.analyzer.detect_security_issues(code)

        assert issues >= 1

    def test_detect_security_issues_hardcoded_password(self):
        """Test detecting hardcoded passwords."""
        code = """
password = "secret123"
api_key = "abc123def"
"""
        issues = self.analyzer.detect_security_issues(code)

        assert issues >= 2

    def test_detect_security_issues_pickle(self):
        """Test detecting pickle usage."""
        code = """
import pickle
def load_data(file):
    return pickle.loads(file.read())
"""
        issues = self.analyzer.detect_security_issues(code)

        assert issues >= 1

    def test_detect_security_issues_safe_code(self):
        """Test that safe code has no issues."""
        code = """
def safe_function(a, b):
    result = a + b
    return result
"""
        issues = self.analyzer.detect_security_issues(code)

        assert issues == 0

    def test_analyze_unsupported_language(self):
        """Test analyzing unsupported language."""
        code = "function test() { return 42; }"
        result = self.analyzer.analyze(code, "javascript")

        assert result["avg_complexity"] == 1.0
        assert result["maintainability_index"] == 100.0
        assert result["security_issues"] == 0

    def test_calculate_complexity_no_functions(self):
        """Test complexity with no functions."""
        code = "x = 1 + 2"
        complexity = self.analyzer.calculate_complexity(code)

        assert complexity == 1.0

    def test_calculate_complexity_async_function(self):
        """Test complexity for async function."""
        code = """
async def fetch_data():
    if True:
        return "data"
"""
        complexity = self.analyzer.calculate_complexity(code)

        assert complexity >= 2.0

    def test_detect_security_issues_multiple_patterns(self):
        """Test detecting multiple security issues."""
        code = """
import os
import pickle

def dangerous():
    password = "secret"
    os.system("rm -rf /")
    eval("2 + 2")
    pickle.loads(b"data")
"""
        issues = self.analyzer.detect_security_issues(code)

        assert issues >= 4
