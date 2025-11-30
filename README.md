# CrewAI Israeli IP Intelligence (Gemini-ready)

## What's included
- tools/ripe_tools.py — RIPE-based tools: fetch prefixes, group by ISP, overlaps, geolocation.
- agents/ip_agent.py — Agent configured to use Gemini (preferred) or OpenAI as fallback.
- tasks/ip_tasks.py — Tasks describing the workflow.
- main.py — Small runner that creates the Crew and runs tasks.
- requirements.txt — pip requirements.
- run.sh — convenience run script (make executable).

## Quickstart
1. Create virtualenv:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set environment variables for LLM provider, for example:
   ```bash
   export CREW_LLM=gemini
   export GEMINI_API_KEY=...   # provider-specific
   # OR for OpenAI:
   export CREW_LLM=openai
   export OPENAI_API_KEY=...
   ```
3. Run:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## Notes
- The code assumes your CrewAI distribution exposes `crewai.llms.Gemini` or `crewai.llms.OpenAI`. Adjust imports to your environment if necessary.
- For high-volume IP geolocation, respect rate limits (ip-api or other services).
