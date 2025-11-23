#!/bin/bash
# Format code with ruff and black

set -e

echo "Formatting code with ruff..."
ruff format src/

echo "Formatting code with black..."
black src/

echo "Checking formatting..."
ruff format --check src/
black --check src/

echo "Running linter..."
ruff check src/

echo "✅ All formatting checks passed!"

