# Testing Guide - FastAPI Activity Management System

## Overview

This directory contains comprehensive tests for the Mergington High School Activity Management System API. Tests are organized by feature and use the AAA (Arrange-Act-Assert) pattern for clarity and consistency.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── routes/                  # Endpoint tests
│   ├── test_root.py        # GET / redirect endpoint
│   ├── test_activities.py  # GET /activities endpoint
│   ├── test_signup.py      # POST /activities/{activity_name}/signup endpoint
│   └── test_unregister.py  # POST /activities/{activity_name}/unregister endpoint
├── models/                  # Data validation tests
│   └── test_validation.py  # Input validation and data structure tests
└── integration/             # Multi-step workflow tests
    └── test_activity_workflow.py  # Complete workflow scenarios
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/routes/test_signup.py
```

### Run specific test
```bash
pytest tests/routes/test_signup.py::test_signup_success
```

### Run tests by marker (unit or integration)
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
```

### Run with coverage report
```bash
pytest --cov=src --cov-report=term-missing
```

### Run with coverage and generate HTML report
```bash
pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in browser
```

### Run tests in watch mode (requires pytest-watch)
```bash
ptw  # Auto-reruns tests on file changes
```

## Test Organization

### Unit Tests (`tests/routes/` and `tests/models/`)

Unit tests focus on individual endpoints and validations:

- **test_root.py**: Route redirect behavior (2 tests)
- **test_activities.py**: Activity list retrieval and structure (4 tests)
- **test_signup.py**: Signup functionality, errors, and validation (5 tests)
- **test_unregister.py**: Unregister functionality and edge cases (6 tests)
- **test_validation.py**: Data validation, field requirements, consistency (6 tests)

**Total Unit Tests**: ~23 tests

### Integration Tests (`tests/integration/`)

Integration tests verify multi-step workflows and realistic user scenarios:

- **test_activity_workflow.py**: Complete signup-view-unregister workflows (4 tests)

**Total Integration Tests**: ~4 tests

## Test Patterns

### AAA (Arrange-Act-Assert) Pattern

Every test follows this structure for clarity:

```python
@pytest.mark.unit
def test_example(client, sample_activity_name):
    """Description of what is being tested."""
    
    # ARRANGE: Setup test data and fixtures
    activity_name = sample_activity_name
    email = "test@example.com"
    
    # ACT: Perform the action being tested
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # ASSERT: Verify the results
    assert response.status_code == 200
    assert email in response.json()["message"]
```

### Test Naming Convention

Test names follow the pattern: `test_<action>_<scenario>`

- `test_signup_success` - Happy path
- `test_signup_duplicate_email` - Error case
- `test_signup_activity_not_found` - Edge case

## Fixtures

All fixtures are defined in `conftest.py`:

| Fixture | Purpose |
|---------|---------|
| `client` | TestClient for FastAPI app |
| `reset_activities` | Auto-resets activities between tests (ensures isolation) |
| `sample_activity_name` | Pre-existing activity: "Chess Club" |
| `sample_email` | Sample email for testing: "test.student@mergington.edu" |
| `existing_activity_with_participants` | Details of activity with participants |
| `all_sample_emails` | List of 4 unique test emails |

**Example usage:**
```python
def test_something(client, sample_activity_name, sample_email):
    # client, sample_activity_name, and sample_email are automatically injected
    pass
```

## Test Coverage

Current test coverage target: **90%+**

To view coverage details:
```bash
pytest --cov=src --cov-report=term-missing
```

Coverage includes:
- ✅ All 4 endpoints (GET /, GET /activities, POST /signup, POST /unregister)
- ✅ Success paths (happy paths)
- ✅ Error cases (404, 400 status codes)
- ✅ Edge cases (duplicate signups, unregistering non-participants)
- ✅ Data structure validation
- ✅ Multi-step workflows

## Adding New Tests

### 1. Decide where the test belongs

- Endpoint behavior → `tests/routes/test_<endpoint_name>.py`
- Data validation → `tests/models/test_validation.py`
- Multi-step workflow → `tests/integration/test_activity_workflow.py`

### 2. Use AAA pattern with clear comments

```python
@pytest.mark.unit  # or @pytest.mark.integration
def test_descriptive_name(client, relevant_fixtures):
    """Clear description of what is being tested."""
    
    # ARRANGE: Setup
    # ... setup code ...
    
    # ACT: Perform action
    # ... action code ...
    
    # ASSERT: Verify results
    # ... assertions ...
```

### 3. Use existing fixtures when possible

```python
# ✅ Good: Reuses fixtures
def test_signup_flow(client, sample_activity_name, sample_email):
    pass

# ❌ Avoid: Hardcoding values
def test_signup_flow(client):
    activity_name = "Chess Club"  # Hardcoded instead of fixture
    email = "test@example.com"     # Hardcoded instead of fixture
    pass
```

### 4. Add pytest marker for categorization

```python
@pytest.mark.unit         # For endpoint/validation tests
@pytest.mark.integration  # For workflow tests
```

## Common Assertions

### Status codes
```python
assert response.status_code == 200      # Success
assert response.status_code == 400      # Bad request
assert response.status_code == 404      # Not found
assert response.status_code == 422      # Validation error
```

### Response structure
```python
data = response.json()
assert "message" in data
assert email in data["message"]
assert "participants" in activity
```

### Participant operations
```python
participants = activities[activity_name]["participants"]
assert email in participants          # After signup
assert email not in participants      # After unregister
```

## Debugging Tests

### Run with print statements visible
```bash
pytest -s  # Shows print() output
```

### Run single test with verbose output
```bash
pytest -vv tests/routes/test_signup.py::test_signup_success
```

### Drop into debugger on failure
```bash
pytest --pdb  # Opens debugger on exception
```

### Show local variables in exception
```bash
pytest -l  # 'l' shows locals on failure
```

## Known Limitations

The test suite documents current app behavior and notes areas for future enhancement:

1. **No email format validation** - App accepts any string as email. Tests document this with TODO comments.
2. **max_participants not enforced** - Activities allow unlimited participants. Tests check current behavior.
3. **No concurrent request handling** - In-memory state, no locking mechanism.

These limitations are noted in tests with comments like:
```python
# TODO: Add email format validation once implemented
# TODO: Enforce max_participants constraint
```

## Continuous Integration

To run tests in CI/CD pipeline:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage
pytest --cov=src --cov-report=term-missing --cov-report=json

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=90
```

## Troubleshooting

### Tests fail with import errors
- Ensure `pythonpath = .` is set in `pytest.ini`
- Run from project root: `pytest` (not `pytest tests/`)

### Tests pass individually but fail when run together
- Check if `reset_activities` fixture is applied (`autouse=True`)
- Verify tests aren't sharing state inappropriately

### Asyncio warnings
- Ensure `asyncio_mode = auto` is set in `pytest.ini`
- Update pytest-asyncio if warnings persist: `pip install --upgrade pytest-asyncio`

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [AAA Pattern Guide](https://www.boykis.com/blog/arrange-act-assert/)
