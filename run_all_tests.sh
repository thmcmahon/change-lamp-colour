#!/bin/bash
echo "Running unittest tests..."
python -m unittest discover tests/

echo -e "\n\nRunning pytest tests..."
pytest tests/ -v
