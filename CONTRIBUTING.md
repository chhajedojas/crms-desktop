# Contributing to CRMS

Thank you for your interest in contributing to CRMS (Company Records Management System)! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We value respectful, constructive, and collaborative interactions.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or derogatory language
- Personal attacks or insults
- Public or private harassment
- Publishing others' private information
- Other unethical or unprofessional conduct

### Reporting

If you witness unacceptable behavior, please contact the project maintainers privately.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Tesseract OCR (system package)

### Setup Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/crms-ai-document-intelligence.git
   cd crms-ai-document-intelligence
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/chhajedojas/crms-ai-document-intelligence.git
   ```

4. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements.txt[dev]
   python scripts/init_db.py
   pre-commit install
   ```

5. **Frontend setup**:
   ```bash
   cd ../frontend
   npm install
   ```

### Create a Branch

```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

## Development Workflow

### 1. Understand the System

Before making changes:
- Read [ARCHITECTURE.md](ARCHITECTURE.md)
- Read [DECISIONS.md](DECISIONS.md)
- Read [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md)
- Understand the engineering rules in README.md

### 2. Choose a Task

Check [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) for pending tasks, or:
- Look for issues labeled "good first issue"
- Propose a new feature by creating an issue first
- Start with small tasks to get familiar with the codebase

### 3. Write Tests First

Follow TDD (Test-Driven Development):
1. Write a failing test for the feature
2. Run the test to confirm it fails
3. Implement the feature
4. Run the test to confirm it passes
5. Add more tests for edge cases

### 4. Implement the Feature

- Follow the existing code style
- Add docstrings to all public functions
- Update relevant documentation
- Ensure type annotations are correct

### 5. Run Quality Checks

```bash
# Backend
cd backend
black .
isort .
flake8 .
mypy core/ --ignore-missing-imports
pytest tests/ -v --cov

# Frontend
cd frontend
npm run lint
npm run format
npm test
```

### 6. Commit Your Changes

Follow conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for test changes
- `chore:` for maintenance tasks

Example:
```bash
git add .
git commit -m "feat(scanner): implement document scanner with change detection"
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference related issues
- Link to relevant ADRs if architectural changes
- Screenshots if UI changes

## Coding Standards

### Python

#### Style
- Use Black for formatting (automatic)
- Use isort for import sorting (automatic)
- Follow PEP 8 guidelines
- Maximum line length: 100 characters

#### Type Safety
- All public functions must have type hints
- Pass mypy type checking
- Use `Optional[T]` for nullable types
- Avoid `Any` type when possible

#### Documentation
- All public functions must have docstrings
- Use Google style docstrings
- Include Args, Returns, Raises sections
- Add examples for complex functions

#### Error Handling
- Never silently catch exceptions
- Log errors with context
- Use custom exceptions from `core.exceptions`
- Handle expected errors gracefully

#### Naming Conventions
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`
- Modules: `lowercase_with_underscores`

### TypeScript

#### Style
- Use Prettier for formatting (automatic)
- Follow ESLint rules
- Maximum line length: 100 characters

#### Type Safety
- Enable strict mode
- Avoid `any` type when possible
- Use interfaces for object shapes
- Use type guards for runtime checks

#### Documentation
- Add JSDoc comments for public APIs
- Include parameter and return types
- Add examples for complex functions

#### Naming Conventions
- Classes and interfaces: `PascalCase`
- Functions and variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `leading_underscore`
- Modules: `lowercase-with-hyphens`

### Engineering Rules

Never violate these core principles (from README.md):
- Never modify original documents
- All reorganization must be undoable
- Every feature must have tests
- Every module must compile independently
- Never use hard-coded paths
- Use dependency injection
- Every database migration must be reversible
- Long-running operations must show progress
- All file operations must be atomic
- Never log sensitive data

## Testing Guidelines

### Python Tests

#### Test Structure
- Unit tests in `tests/test_*.py`
- Integration tests in `tests/integration/`
- End-to-end tests in `tests/e2e/`
- Use pytest fixtures for setup

#### Test Coverage
- Aim for >80% coverage on new code
- Critical paths must have 100% coverage
- Placeholder modules can have lower coverage

#### Test Naming
- Test functions: `test_<feature>_<scenario>`
- Test classes: `Test<ClassName>`
- Use descriptive names that explain what is tested

#### Test Organization
```python
def test_document_scanner_detects_new_files():
    """Test that scanner detects new files in directory."""
    # Arrange
    # Act
    # Assert
```

### TypeScript Tests

#### Test Structure
- Component tests in `src/components/__tests__/`
- Hook tests in `src/hooks/__tests__/`
- Service tests in `src/services/__tests__/`
- Use Vitest framework

#### Test Coverage
- Aim for >80% coverage on new code
- UI components must have snapshot tests
- Critical services must have 100% coverage

## Pull Request Process

### Before Submitting

1. **Self-review your changes**
   - Run all quality checks
   - Update documentation
   - Add tests for new features
   - Check for TODO comments

2. **Update documentation**
   - Update README.md if user-facing changes
   - Update ARCHITECTURE.md if architectural changes
   - Add ADR if architectural decision
   - Update CHANGELOG.md
   - Update DEVELOPMENT_STATUS.md

3. **Ensure tests pass**
   - All tests must pass locally
   - No linting errors
   - No type checking errors

### Pull Request Description

Include:
- **Summary**: Brief description of changes
- **Motivation**: Why this change is needed
- **Changes**: Detailed list of changes
- **Testing**: How you tested the changes
- **Screenshots**: If UI changes
- **Related issues**: Links to related GitHub issues
- **Breaking changes**: If any, explain migration path

### Review Process

1. **Automated checks**: CI will run tests and linting
2. **Code review**: Maintainers will review code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, maintainers will merge

### After Merge

1. **Delete your branch**:
   ```bash
   git branch -d feature/your-feature-name
   ```

2. **Update your fork**:
   ```bash
   git checkout main
   git pull upstream main
   ```

## Reporting Issues

### Bug Reports

When reporting bugs, include:
- **Description**: Clear description of the bug
- **Steps to reproduce**: Exact steps to reproduce
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, Node version
- **Screenshots**: If applicable
- **Logs**: Relevant log output

### Feature Requests

When requesting features, include:
- **Problem**: What problem this solves
- **Proposed solution**: How you envision the solution
- **Alternatives considered**: Other approaches you thought of
- **Use case**: How this would be used
- **Priority**: How important this is to you

### Security Issues

For security vulnerabilities:
- Do NOT report publicly
- Email: security@example.com (to be configured)
- Include "Security" in subject line
- Provide details and reproduction steps

## Getting Help

### Documentation
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DECISIONS.md](DECISIONS.md) - Architectural decisions
- [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) - Current status
- [ROADMAP.md](ROADMAP.md) - Development timeline

### Questions
- Create a GitHub issue with "question" label
- Be specific and provide context
- Include what you've already tried

### Discussions
- Use GitHub Discussions for broader topics
- Propose ideas and get community feedback
- Share your use cases and experiences

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to CRMS! 🎉
