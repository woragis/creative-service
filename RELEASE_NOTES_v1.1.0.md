# Creative Service v1.1.0

## Release Date
December 27, 2025

## Overview
This release focuses on CI/CD improvements, test coverage enhancements, and workflow automation. The service now includes comprehensive GitHub Actions workflows for continuous integration and deployment.

## What's New

### CI/CD Workflows
- **GitHub Actions CI Workflow**: Automated testing on push and pull requests
  - Unit tests with coverage reporting
  - Integration tests with external API providers (Replicate, OpenAI)
  - Docker image building and validation
  - Markdown test reports in GitHub Actions
- **GitHub Actions CD Workflow**: Automated deployment on version tags
  - Docker image building and pushing to Docker Hub
  - Multi-tag support (vX.Y.Z, X.Y.Z, latest)
- **Pip Caching**: Optimized dependency installation with pip cache

### Test Improvements
- **Test Coverage**: Improved unit and integration test coverage
- **Test Reports**: Markdown-formatted test summaries in CI
- **Pytest Configuration**: Fixed `pytest-asyncio` deprecation warnings
- **Diagram Generation Tests**: Improved Mermaid diagram generation tests with API mocking
- **Integration Test Fixes**: Enhanced resilience for diagram generation failures

### Docker Improvements
- **Docker Build**: Enhanced Dockerfile with better caching
- **Image Testing**: Automated Docker image validation in CI
- **Graphviz Support**: Included graphviz installation for diagram generation

## Technical Details

### Dependencies
- No breaking changes to dependencies
- Updated pytest configuration for better async test handling

### Configuration
- No configuration changes required
- Note: `REPLICATE_API_KEY` environment variable is required for integration tests

## Migration Guide
No migration required. This is a non-breaking release.

## Full Changelog

### Added
- GitHub Actions CI workflow (`.github/workflows/ci.yml`)
- GitHub Actions CD workflow (`.github/workflows/cd.yml`)
- Markdown test reports in CI
- Pip caching in CI workflows
- Docker image validation in CI
- Graphviz installation in CI for diagram generation

### Changed
- Updated `pytest.ini` to fix asyncio deprecation warnings
- Improved Mermaid diagram generation tests with API mocking
- Enhanced integration test resilience for rendering failures

### Fixed
- Fixed `pytest-asyncio` deprecation warning
- Fixed Mermaid diagram generation tests to use API mocking instead of local CLI
- Improved test result parsing in CI

## Contributors
- Automated CI/CD implementation
- Test coverage improvements

