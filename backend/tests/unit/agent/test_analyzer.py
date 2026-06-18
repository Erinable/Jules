"""Unit tests for CodeAnalyzer."""
from app.agent.analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    """Test suite for CodeAnalyzer."""

    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = CodeAnalyzer()

    def test_analyze_valid_python_code(self):
        """Test analyzing valid Python code."""
        code = """
def hello():
    return "world"
"""
        result = self.analyzer.analyze(code, "python")

        assert "avg_complexity" in result
        assert "maintainability_index" in result
        assert "security_issues" in result
        assert result["avg_complexity"] >= 1.0
        assert 0 <= result["maintainability_index"] <= 100

    def test_analyze_invalid_python_syntax(self):
        """Test analyzing Python code with syntax errors."""
        code = "def broken("
        result = self.analyzer.analyze(code, "python")

        assert result["avg_complexity"] == 999.0
        assert result["maintainability_index"] == 0.0
        assert result["security_issues"] == 1

    def test_analyze_unsupported_language(self):
        """Test analyzing unsupported language."""
        code = "console.log('test');"
        result = self.analyzer.analyze(code, "javascript")

        assert result["avg_complexity"] == 1.0
        assert result["maintainability_index"] == 100.0
        assert result["security_issues"] == 0

    def test_calculate_complexity_simple_function(self):
        """Test complexity calculation for simple function."""
        code = """
def simple():
    return True
"""
        complexity = self.analyzer.calculate_complexity(code)
        assert complexity == 1.0

    def test_calculate_complexity_with_conditionals(self):
        """Test complexity calculation with conditionals."""
        code = """
def complex_func(x):
    if x > 0:
        if x > 10:
            return "high"
        return "low"
    return "zero"
"""
        complexity = self.analyzer.calculate_complexity(code)
        assert complexity > 1.0

    def test_calculate_complexity_empty_code(self):
        """Test complexity calculation for empty code."""
        code = ""
        complexity = self.analyzer.calculate_complexity(code)
        assert complexity == 1.0

    def test_calculate_complexity_syntax_error(self):
        """Test complexity calculation with syntax error."""
        code = "def broken("
        complexity = self.analyzer.calculate_complexity(code)
        assert complexity == 999.0

    def test_calculate_maintainability_simple_code(self):
        """Test maintainability calculation for simple code."""
        code = "x = 1"
        maintainability = self.analyzer.calculate_maintainability(code)
        assert 0 <= maintainability <= 100

    def test_calculate_maintainability_empty_code(self):
        """Test maintainability calculation for empty code."""
        code = ""
        maintainability = self.analyzer.calculate_maintainability(code)
        assert maintainability == 100.0

    def test_calculate_maintainability_complex_code(self):
        """Test maintainability calculation for complex code."""
        code = """
def complex_function(a, b, c):
    if a > 0:
        for i in range(10):
            if b > i:
                while c > 0:
                    c -= 1
    return c
"""
        maintainability = self.analyzer.calculate_maintainability(code)
        assert 0 <= maintainability <= 100

    def test_detect_security_issues_eval(self):
        """Test detection of eval() usage."""
        code = 'result = eval("1 + 1")'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_detect_security_issues_exec(self):
        """Test detection of exec() usage."""
        code = 'exec("print(1)")'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_detect_security_issues_os_system(self):
        """Test detection of os.system() usage."""
        code = 'import os\nos.system("ls")'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_detect_security_issues_hardcoded_password(self):
        """Test detection of hardcoded password."""
        code = 'password = "secret123"'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_detect_security_issues_api_key(self):
        """Test detection of hardcoded API key."""
        code = 'api_key = "12345"'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_detect_security_issues_clean_code(self):
        """Test detection on clean code without issues."""
        code = """
def calculate(x, y):
    return x + y
"""
        issues = self.analyzer.detect_security_issues(code)
        assert issues == 0

    def test_detect_security_issues_pickle(self):
        """Test detection of pickle usage."""
        code = 'import pickle\ndata = pickle.loads(bytes)'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_detect_security_issues_yaml_load(self):
        """Test detection of unsafe YAML loading."""
        code = 'import yaml\ndata = yaml.load(file)'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_detect_security_issues_assert(self):
        """Test detection of assert statements."""
        code = 'assert user.is_admin'
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 1

    def test_function_complexity_with_loops(self):
        """Test complexity calculation for function with loops."""
        code = """
def loop_func():
    for i in range(10):
        if i > 5:
            break
"""
        tree = __import__('ast').parse(code)
        func_node = tree.body[0]
        complexity = self.analyzer._calculate_function_complexity(func_node)
        assert complexity >= 2

    def test_function_complexity_with_exception_handling(self):
        """Test complexity calculation for function with try/except."""
        code = """
def error_handler():
    try:
        risky_operation()
    except ValueError:
        handle_error()
"""
        tree = __import__('ast').parse(code)
        func_node = tree.body[0]
        complexity = self.analyzer._calculate_function_complexity(func_node)
        assert complexity >= 2

    def test_function_complexity_with_logical_operators(self):
        """Test complexity calculation for function with and/or."""
        code = """
def logic_func(a, b, c):
    if a and b or c:
        return True
"""
        tree = __import__('ast').parse(code)
        func_node = tree.body[0]
        complexity = self.analyzer._calculate_function_complexity(func_node)
        assert complexity >= 2

    def test_maintainability_with_comments(self):
        """Test maintainability ignores comments."""
        code = """
# This is a comment
def func():
    # Another comment
    return True
"""
        maintainability = self.analyzer.calculate_maintainability(code)
        assert 0 <= maintainability <= 100

    def test_analyze_multiple_security_issues(self):
        """Test detection of multiple security issues."""
        code = """
import os
password = "secret"
api_key = "12345"
eval("dangerous")
os.system("rm -rf /")
"""
        issues = self.analyzer.detect_security_issues(code)
        assert issues >= 4
