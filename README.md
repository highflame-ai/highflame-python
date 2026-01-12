[![Ask DeepWiki](https://deepwiki.com/badge.svg "DeepWiki Documentation")](https://deepwiki.com/getjavelin/javelin-python)

## Highflame: Agent Security Platform SDK

This is the Python SDK package for Highflame.

For more information about Javelin, see https://www.highflame.com

Javelin Documentation: https://docs.highflame.ai

### Development

For local development, Please change `version = "RELEASE_VERSION"` with any semantic version example : `version = "v0.1.10"` in `pyproject.toml`

*Make sure that the file `pyproject.toml` reverted before commit back to main*

### Installation

```python
  pip install highflame
```

### Quick Start Guide

## Development Setup

### Setting up Virtual Environment

#### Windows

```batch
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install
```

#### macOS/Linux

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install poetry
poetry install
```

### Building and Installing the SDK

```bash
# Uninstall any existing version
pip uninstall highflame -y

# Build the package
poetry build

# Install the newly built package
pip install dist/highflame-<version>-py3-none-any.whl
```

