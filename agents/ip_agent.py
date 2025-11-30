import os
import sys
from crewai import Agent

# ודא שאין OPENAI_API_KEY
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]
    print("✅ Removed OPENAI_API_KEY from environment")

# ייבוא הכלים ישירות
try:
    from tools.ripe_tools import (
        fetch_country_prefixes,
        prefixes_by_isp
    )
    print("✅ Tools imported successfully")
except ImportError as e:
    print(f"❌ Error importing tools: {e}")
    sys.exit(1)

# קבע את GOOGLE_API_KEY
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set!")
    print("Please run: export GOOGLE_API_KEY='your-key'")
    sys.exit(1)

os.environ["GOOGLE_API_KEY"] = api_key
print(f"✅ Using Gemini API Key: {api_key[:10]}...")

# צור את ה-Agent עם Gemini - שימוש בפורמט CrewAI
try:
    ip_analysis_agent = Agent(
        name="Israeli-IP-Analyst",
        role="Network Intelligence Agent",
        goal=(
            "Analyze Israeli IPv4 space using RIPE APIs. "
            "Group prefixes by ISP, check overlaps, run geolocation on example IPs."
        ),
        backstory=(
            "You are a senior RIPE intelligence specialist with extensive experience "
            "in analyzing IP address space, ASN mappings, and network geolocation."
        ),
        tools=[
            fetch_country_prefixes,
            prefixes_by_isp
        ],
        llm="gemini/gemini-2.0-flash",  # פורמט ישיר
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )
    print("✅ Agent created successfully with Gemini")
except Exception as e:
    print(f"❌ Error creating agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)