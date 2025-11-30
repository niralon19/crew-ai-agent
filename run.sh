#!/bin/bash
#export CREW_LLM=gemini
export GOOGLE_API_KEY=""
#export OPENAI_API_KEY=""

uv run python main.py

#rm -rf .venv
#uv venv
#source .venv/bin/activate
#
#uv venv --python 3.11
#source .venv/bin/activate
#
#uv pip install -r requirements.txt
#uv pip install .
#uv add packege
#uv sync