import os
import sys
from dotenv import load_dotenv

# השבת telemetry
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

# טען את משתני הסביבה מ-.env
load_dotenv()

# קבע את GOOGLE_API_KEY לפני שמייבאים CrewAI
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set!")
    print("Please run: export GOOGLE_API_KEY='your-key'")
    sys.exit(1)

os.environ["GOOGLE_API_KEY"] = api_key

# ודא שאין OPENAI_API_KEY שיגרום confusion
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]

print("✅ Using Gemini API Key")
print(f"✅ API Key: {api_key[:10]}...")

# ייבוא של CrewAI רכיבים
try:
    from crewai import Crew, Task
    from agents.ip_agent import ip_analysis_agent

    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# הגדר את המשימות
task1 = Task(
    description=(
        "Fetch all Israeli IPv4 prefixes using the fetch_country_prefixes tool "
        "with country code 'IL'. Get a complete list."
    ),
    expected_output="A comprehensive list of Israeli IPv4 prefixes in CIDR notation.",
    agent=ip_analysis_agent,
    name="fetch_israeli_prefixes",
)

task2 = Task(
    description=(
        "Use prefixes_by_isp tool to group Israeli prefixes by ISP. "
        "Input the prefixes as comma-separated values like: 1.2.3.0/24,4.5.6.0/24"
    ),
    expected_output="Mapping of prefixes grouped by ISP/ASN.",
    agent=ip_analysis_agent,
    name="group_prefixes_by_isp",
)


# צור את ה-Crew
try:
    crew = Crew(
        agents=[ip_analysis_agent],
        tasks=[task1, task2],
        verbose=True,
    )
    print("✅ Crew created successfully\n")
except Exception as e:
    print(f"❌ Error creating crew: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# הרץ את ה-Crew
if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting Crew Execution...")
    print("=" * 80 + "\n")

    try:
        result = crew.kickoff()
        print("\n" + "=" * 80)
        print("✅ Crew Execution Completed Successfully!")
        print("=" * 80)
        print("\n📊 RESULTS:\n")
        print(result)
    except Exception as e:
        print(f"\n❌ Crew Execution Failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)