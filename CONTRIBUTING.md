# Contributing to Vibing-Viz

We love your input! We want to make contributing to Vibing-Viz as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the style guidelines
6. Issue that pull request!

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/vibing-viz.git
cd vibing-viz
```

2. Install development environment:
```bash
uv sync --all-extras
```

3. Install pre-commit hooks:
```bash
uv run pre-commit install
```

## Code Style

We use:
- **Black** for code formatting (line length: 88)
- **Ruff** for linting
- **Google-style docstrings** for documentation
- **Type hints** throughout the codebase

Run formatting and linting:
```bash
uv run black .
uv run ruff check --fix .
```

## Testing

Write tests for any new functionality. Run tests with:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest --cov=vibing_viz
```

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the CHANGELOG.md with your changes
3. The PR will be merged once you have the sign-off of at least one maintainer

## Any contributions you make will be under the BSD-3 License

When you submit code changes, your submissions are understood to be under the same [BSD-3 License](LICENSE) that covers the project.

## Report bugs using GitHub's [issue tracker](https://github.com/talmo/vibing-viz/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/talmo/vibing-viz/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License

By contributing, you agree that your contributions will be licensed under its BSD-3 License.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md)