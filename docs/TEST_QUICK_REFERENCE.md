# Solid CLI - Test Quick Reference

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd C:\Users\hobo\Desktop\githubchallenge
uv pip install -e .
uv pip install pytest pytest-asyncio respx
```

### 2. Run All Tests
```bash
pytest tests/ -v
```

### 3. Run Specific Module
```bash
pytest tests/test_auth.py -v
pytest tests/test_client.py -v
pytest tests/test_sync.py -v
pytest tests/test_acl.py -v
pytest tests/test_cli.py -v
```

## 📋 Test Command Reference

| Command | Purpose |
|---------|---------|
| `pytest tests/` | Run all tests |
| `pytest tests/test_auth.py` | Run auth tests only |
| `pytest tests/ -v` | Verbose output |
| `pytest tests/ -q` | Quiet output |
| `pytest tests/ -k "sync"` | Run tests matching "sync" |
| `pytest tests/test_auth.py::TestProxyAuthProvider` | Run specific test class |
| `pytest tests/test_auth.py::TestProxyAuthProvider::test_get_headers_returns_dict` | Run specific test |
| `pytest tests/ -m asyncio` | Run only async tests |
| `pytest tests/ --lf` | Run last failed tests |
| `pytest tests/ --ff` | Run failed first, then others |

## 📊 Coverage Reports

```bash
# Install coverage plugin
pip install pytest-cov

# Generate HTML report
pytest tests/ --cov=solid_cli --cov-report=html
# Opens: htmlcov/index.html in browser

# Terminal report
pytest tests/ --cov=solid_cli --cov-report=term-missing
```

## 🔍 Debugging Tests

```bash
# Verbose output with print statements
pytest tests/ -v -s

# Show local variables on failure
pytest tests/ -l

# Stop on first failure
pytest tests/ -x

# Show test execution time
pytest tests/ --durations=10

# Debug with pdb (stops on failure)
pytest tests/ --pdb

# Show all test names (don't run them)
pytest tests/ --collect-only
```

## 📈 Pytest Plugins

```bash
# Install pytest-watch (auto-rerun on file changes)
pip install pytest-watch
ptw tests/

# Install pytest-xdist (parallel execution)
pip install pytest-xdist
pytest tests/ -n auto

# Install pytest-timeout (timeout per test)
pip install pytest-timeout
pytest tests/ --timeout=10
```

## 🎯 Test Categories

### Unit Tests
```bash
pytest tests/test_auth.py -v          # Auth provider tests (11)
pytest tests/test_client.py -v        # HTTP client tests (10)
```

### Integration Tests
```bash
pytest tests/test_sync.py -v          # Directory sync tests (8)
pytest tests/test_acl.py -v           # ACL management tests (10)
pytest tests/test_cli.py -v           # CLI command tests (20)
```

### By Test Type
```bash
pytest tests/ -m asyncio              # Only async tests (28)
pytest tests/test_cli.py              # Only CLI tests (20)
```

## 📝 Test File Quick Reference

### tests/conftest.py
**Fixtures**: 4 shared fixtures used across all tests
- `mock_pod` - HTTP mocking backend
- `mock_fs` - Temporary file structure  
- `sample_acl_turtle` - Sample ACL content
- `sample_resource_turtle` - Sample RDF resource

### tests/test_auth.py
**Tests**: 11 tests for authentication
- ProxyAuthProvider (3 tests)
- OIDCAuthProvider (4 tests)
- Integration (2 tests)

### tests/test_client.py
**Tests**: 10 tests for HTTP operations
- Initialization (3 tests)
- Header injection (2 tests)
- HTTP methods (4 tests)
- Context manager (1 test)

### tests/test_sync.py
**Tests**: 8 tests for directory sync
- Directory validation (1 test)
- Upload scenarios (2 tests)
- Progress tracking (1 test)
- File handling (2 tests)
- Error handling (2 tests)

### tests/test_acl.py
**Tests**: 10 tests for ACL management
- ACL creation/modification (2 tests)
- Modes (1 test)
- RDF validation (3 tests)
- Error handling (3 tests)

### tests/test_cli.py
**Tests**: 20 tests for CLI commands
- Help text (5 tests)
- Sync command (3 tests)
- Share command (3 tests)
- Monitor command (2 tests)
- Tmux command (2 tests)
- Error handling (5 tests)

## 🐛 Troubleshooting

### Tests fail with "module not found"
```bash
# Reinstall package in editable mode
uv pip install -e .
```

### Async tests not running
```bash
# Verify pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

### httpx mocking not working
```bash
# Verify respx is installed
pip install respx

# Check @respx.mock decorator is on test function
```

### RDF parsing errors
```bash
# Verify rdflib is installed
pip install rdflib

# Check Turtle format is valid
```

## 📚 Example Test Commands

### Run auth tests with output
```bash
pytest tests/test_auth.py -v -s
```

### Run sync tests with timing
```bash
pytest tests/test_sync.py -v --durations=5
```

### Run ACL tests with coverage
```bash
pytest tests/test_acl.py -v --cov=solid_cli.acl
```

### Run CLI tests with pdb on failure
```bash
pytest tests/test_cli.py -v --pdb
```

### Run async tests in parallel
```bash
pytest tests/ -m asyncio -n auto
```

## 🎯 Common Patterns

### Run specific test class
```bash
pytest tests/test_auth.py::TestOIDCAuthProvider -v
```

### Run tests matching pattern
```bash
pytest tests/ -k "acl" -v
pytest tests/ -k "not cli" -v
```

### Run with different Python versions
```bash
tox  # requires tox to be installed
```

### Generate JUnit XML (CI/CD)
```bash
pytest tests/ --junit-xml=results.xml
```

## ⚡ Performance Tips

- Use `-n auto` with pytest-xdist for parallel execution
- Use `--lf` to run only last failed tests during debugging
- Use `-x` to stop on first failure for faster feedback
- Use `--tb=short` for shorter tracebacks

## 📖 Documentation

- See `TEST_SUITE.md` for comprehensive test guide
- See `TEST_IMPLEMENTATION.md` for implementation details
- See individual test files for detailed docstrings

---

**Last Updated**: February 14, 2026
**Test Count**: 59 tests
**Status**: ✅ Production Ready
