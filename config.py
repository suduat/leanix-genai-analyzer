import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-5"
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))

LIFECYCLE_STAGES = ["Plan", "Phase In", "Active", "Phase Out", "End of Life"]

REQUIRED_COLUMNS = [
    "app_name", "business_capability", "lifecycle_stage",
    "tech_debt_score", "business_value_score", "annual_cost_usd",
    "hosting_type", "last_updated_year", "owner_team"
]