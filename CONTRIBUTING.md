# Contributing to Tetris Overlay

Thank you for your interest in contributing to Tetris Overlay! This document provides guidelines and instructions for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+ (3.13 recommended)
- Git
- Development tools for your platform

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/-tetris-overlay-test.git
   cd -tetris-overlay-test
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🏗️ Development Workflow

### 1. Code Changes

#### Code Style
We use automated tools to maintain code quality:

```bash
# Format code
black .

# Lint code
ruff check . --fix

# Type checking
mypy .

# Run all quality checks
pre-commit run --all-files
```

#### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Write meaningful commit messages
- Keep functions focused and small

#### Example Code Structure
```python
"""Module description."""

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def example_function(param1: str, param2: Optional[int] = None) -> bool:
    """
    Example function with proper documentation.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If param1 is invalid
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    logger.info("Processing %s", param1)
    return True
```

### 2. Testing

#### Test Requirements
- All new features must include tests
- Maintain 90%+ code coverage
- Tests must pass on all supported platforms

#### Test Structure
```
tests/
├── unit/           # Unit tests for individual modules
├── integration/    # Integration tests for component interaction
├── ui/            # UI tests for Qt components
└── performance/   # Performance benchmarks
```

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tetromino_shapes.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run performance benchmark
python tests/benchmark_frame_time.py --frames 500 --fps 30
```

#### Writing Tests
```python
"""Test example module."""

import pytest
from unittest.mock import Mock, patch
from your_module import example_function

class TestExampleFunction:
    """Test cases for example_function."""
    
    def test_valid_input(self):
        """Test function with valid input."""
        result = example_function("test")
        assert result is True
        
    def test_empty_input(self):
        """Test function with empty input."""
        with pytest.raises(ValueError):
            example_function("")
            
    def test_with_optional_param(self):
        """Test function with optional parameter."""
        result = example_function("test", 42)
        assert result is True
```

### 3. Documentation

#### Documentation Requirements
- Update README.md for user-facing changes
- Add docstrings to all public functions
- Update API docs for new modules
- Create/update wiki pages for complex features

#### Documentation Style
- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Provide troubleshooting information

### 4. Commit Guidelines

#### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

#### Examples
```
feat(overlay): add ghost piece animations

Implement smooth fade animations for ghost pieces when
they approach the landing position.

Closes #123
```

```
fix(settings): resolve ROI validation error

Fix issue where ROI coordinates with decimal values
were incorrectly rejected as invalid.
```

## 🧪 Testing Guidelines

### Unit Tests
- Test individual functions in isolation
- Use mocks for external dependencies
- Cover edge cases and error conditions
- Keep tests fast and focused

### Integration Tests
- Test component interactions
- Use real dependencies when possible
- Test complete user workflows
- Verify database operations

### UI Tests
- Test Qt widget functionality
- Verify user interactions
- Test hotkey handling
- Use pytest-qt for Qt testing

### Performance Tests
- Benchmark critical paths
- Monitor memory usage
- Test frame processing performance
- Verify FPS targets

## 🐛 Bug Reports

### Reporting Bugs
1. Check existing issues first
2. Use the bug report template
3. Provide detailed reproduction steps
4. Include system information
5. Attach relevant logs/screenshots

### Bug Report Template
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## System Information
- OS: Windows 10/11, macOS, Linux
- Python version: 3.13
- Overlay version: 2.0.0

## Additional Context
Logs, screenshots, etc.
```

## ✨ Feature Requests

### Requesting Features
1. Check existing issues and roadmap
2. Use the feature request template
3. Describe the use case clearly
4. Consider implementation complexity

### Feature Request Template
```markdown
## Feature Description
Clear description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this work?

## Alternatives Considered
Other approaches you thought of

## Additional Context
Any other relevant information
```

## 🔧 Development Tools

### IDE Configuration
Recommended VS Code extensions:
- Python
- Pylance
- Black Formatter
- Ruff
- GitLens

### Debugging
```bash
# Enable debug logging
export TETRIS_OVERLAY_LOG_LEVEL=DEBUG

# Run with debugger
python -m pdb run_overlay_core.py

# Profile performance
python -m cProfile -o profile.stats run_overlay_core.py
```

### Code Quality Tools
```bash
# Security scan
bandit -r .

# Dependency check
safety check

# Complexity analysis
radon cc . -a

# Import sorting
isort .
```

## 📦 Release Process

### Version Bumping
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag
4. Automated CI/CD handles the rest

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] Release notes prepared
- [ ] Manual testing completed

## 🤝 Code Review

### Review Guidelines
- Review code quality and style
- Verify test coverage
- Check for security issues
- Ensure documentation is updated
- Test functionality manually

### Review Process
1. Create pull request
2. Request review from maintainers
3. Address feedback
4. Ensure CI passes
5. Merge when approved

### Review Criteria
- **Functionality**: Does it work as intended?
- **Quality**: Is the code well-written?
- **Testing**: Are tests comprehensive?
- **Documentation**: Is it properly documented?
- **Performance**: Does it meet performance standards?

## 🏆 Recognition

### Contributor Recognition
- Contributors listed in README
- Special thanks in release notes
- Contributor badges on GitHub
- Invitation to maintainer team

### Ways to Contribute
- Code contributions
- Bug reports and feature requests
- Documentation improvements
- Community support
- Translation help
- Testing and feedback

## 📞 Getting Help

### Resources
- [GitHub Discussions](https://github.com/gainey666/-tetris-overlay-test/discussions)
- [GitHub Issues](https://github.com/gainey666/-tetris-overlay-test/issues)
- [Wiki](https://github.com/gainey666/-tetris-overlay-test/wiki)
- [Discord Community](https://discord.gg/tetris-overlay)

### Contact
- Email: dev@tetris-overlay.com
- Twitter: @TetrisOverlay
- Mastodon: @tetrisoverlay@techhub.social

## 📄 Legal

### License
By contributing, you agree that your contributions will be licensed under the MIT License.

### DCO
Contributors must sign off their commits using the `-s` flag:

```bash
git commit -s -m "feat: add new feature"
```

This certifies that you have the right to submit the work under the project's license.

---

## 🎉 Thank You!

Thank you for contributing to Tetris Overlay! Your contributions help make this project better for everyone.

Whether you're fixing bugs, adding features, improving documentation, or helping other users, your contributions are valued and appreciated.

Happy coding! 🚀
