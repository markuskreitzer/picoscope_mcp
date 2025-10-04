# Contributing to PicoScope MCP Server

Thank you for your interest in contributing to the PicoScope MCP Server! This document provides guidelines and information for contributors.

## Project Goals

- Provide a robust MCP interface for PicoScope oscilloscopes
- Enable natural language control via AI assistants like Claude
- Support multiple PicoScope series with a unified API
- Maintain high code quality and comprehensive documentation

## Getting Started

### Development Environment

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/picoscope_mcp.git
   cd picoscope_mcp
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Install PicoSDK C libraries** (for testing with hardware):
   - See [README.md](README.md) for platform-specific instructions

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Test your changes**:
   ```bash
   uv run pytest
   ```

4. **Commit your changes**:
   ```bash
   git commit -m "Add: brief description of changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

## Code Style Guidelines

### Python Code

- Follow **PEP 8** conventions
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep functions focused and concise
- Use descriptive variable names

### Example Function

```python
def configure_channel(
    channel: str,
    voltage_range: float,
    coupling: ChannelCoupling,
) -> bool:
    """Configure a PicoScope channel.

    Args:
        channel: Channel identifier (A, B, C, or D).
        voltage_range: Voltage range in volts.
        coupling: AC or DC coupling.

    Returns:
        True if configuration successful, False otherwise.
    """
    # Implementation here
    pass
```

### MCP Tools

- Include clear **descriptions** explaining what the tool does
- Specify **parameter units** in docstrings (mV, ns, Hz, etc.)
- Return **structured dictionaries** with status and data
- Handle **errors gracefully** with informative messages
- Return results in formats useful for LLM interpretation

### Error Handling

```python
try:
    # Your code here
    return {
        "status": "success",
        "data": result,
    }
except Exception as e:
    return {
        "status": "error",
        "error": str(e),
    }
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=picoscope_mcp

# Run specific test file
uv run pytest tests/test_tools.py
```

### Writing Tests

- Add tests for all new functionality
- Test both success and failure cases
- Mock hardware interactions when appropriate
- Use descriptive test names

## Project Structure

```
picoscope_mcp/
├── src/picoscope_mcp/
│   ├── server.py           # FastMCP server setup
│   ├── device_manager.py   # Device abstraction layer
│   ├── models.py           # Data structures
│   ├── utils.py            # Helper functions
│   └── tools/              # MCP tool implementations
│       ├── discovery.py    # Device discovery/connection
│       ├── configuration.py # Channel configuration
│       ├── acquisition.py  # Data capture
│       ├── analysis.py     # Measurements
│       └── advanced.py     # Advanced features
└── tests/
    └── test_*.py           # Test files
```

## Areas for Contribution

### High Priority

- [ ] **Streaming mode implementation** - Complete the streaming data acquisition
- [ ] **PS2000/3000/4000/6000 support** - Add support for other PicoScope series
- [ ] **Advanced triggers** - Pulse width, window, and logic triggers
- [ ] **Test coverage** - Expand test suite

### Medium Priority

- [ ] **Real-time measurements** - Store and analyze captured data
- [ ] **Signal characterization** - Automated signal analysis
- [ ] **Data export formats** - CSV, JSON, NumPy array support
- [ ] **Documentation** - Usage examples and tutorials

### Low Priority

- [ ] **Web visualization** - Optional web dashboard
- [ ] **Multi-device support** - Simultaneous control of multiple scopes
- [ ] **Configuration presets** - Save/load common configurations

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (README, docstrings)
- [ ] Commit messages are clear and descriptive

### PR Description

Please include:

1. **Summary** - What does this PR do?
2. **Motivation** - Why is this change needed?
3. **Testing** - How was this tested?
4. **Breaking Changes** - Any API changes?
5. **Related Issues** - Links to relevant issues

### Example PR Template

```markdown
## Summary
Adds support for PS3000A series oscilloscopes

## Motivation
Enables the server to work with PS3000A devices, expanding hardware compatibility

## Testing
- Tested with PS3425A device
- All existing tests pass
- Added PS3000A-specific tests

## Breaking Changes
None

## Related Issues
Closes #42
```

## Bug Reports

### Creating an Issue

Include:

1. **Description** - Clear description of the bug
2. **Steps to Reproduce** - Minimal reproducible example
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Environment**:
   - OS and version
   - Python version
   - PicoScope model
   - PicoSDK version

### Example Bug Report

```markdown
## Bug: Channel configuration fails on PS5244D

**Description**
Configuring channel C with 1V range fails with error

**Steps to Reproduce**
1. Connect PS5244D
2. Call `configure_channel(channel="C", voltage_range=1.0)`
3. Error occurs

**Expected**
Channel C configured successfully

**Actual**
Returns error: "Invalid channel configuration"

**Environment**
- macOS 14.0
- Python 3.11.5
- PS5244D (4-channel, 200MHz)
- PicoSDK 10.7.24
```

## Feature Requests

When proposing new features:

1. **Use Case** - Describe the problem this solves
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Other approaches considered?
4. **Additional Context** - Screenshots, examples, etc.

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update PROJECT_PLAN.md for architectural changes
- Add docstrings for all new code
- Include usage examples where helpful

### Documentation Style

- Use clear, concise language
- Include code examples
- Specify units for all measurements
- Link to relevant PicoScope documentation

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks
- Trolling or insulting comments
- Publishing others' private information

## Questions?

- **General questions**: Open a [GitHub Discussion](https://github.com/markuskreitzer/picoscope_mcp/discussions)
- **Bug reports**: Open an [Issue](https://github.com/markuskreitzer/picoscope_mcp/issues)
- **Security issues**: Email directly (see repository security policy)

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.

---

Thank you for contributing to PicoScope MCP Server!
