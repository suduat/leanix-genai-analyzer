import anthropic
import streamlit as st
import json
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS

# This module handles the analysis of the application portfolio using the Anthropic API and generates rationalization recommendations.
def run_analysis(df, summary: dict) -> dict | None:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) # Initialize the Anthropic API client with the provided API key from the configuration. This client will be used to send requests for analysis and receive recommendations based on the application portfolio data.

    portfolio_text = _build_portfolio_text(df, summary) # Build a textual representation of the application portfolio, including an overview and detailed information about each application. This text will be included in the prompt sent to the Anthropic API for analysis and recommendation generation.
    system_prompt = _build_system_prompt() # Build the system prompt that defines the role and instructions for the Anthropic API. This prompt instructs the API to act as a senior Enterprise Architect with experience in application portfolio management and to produce clear, actionable rationalization recommendations in a specific JSON format.
    user_prompt = _build_user_prompt(portfolio_text) # Build the user prompt that includes the portfolio text and specific instructions for the analysis. This prompt guides the Anthropic API to focus on identifying applications for retirement, modernization, capability overlaps, high-risk items, quick wins, and capability gaps based on the provided portfolio data.

    try:
        with st.spinner("Claude is analyzing your portfolio..."): # Display a loading spinner in the Streamlit app while waiting for the response from the Anthropic API, indicating that the analysis is in progress.
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

        raw = response.content[0].text
        return _parse_response(raw)

    except anthropic.AuthenticationError:
        st.error("Invalid API key. Check your .env file.")
        return None
    except anthropic.RateLimitError:
        st.error("Rate limit hit. Wait 60 seconds and retry.")
        return None
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return None

# Helper functions to build prompts and parse responses for the Anthropic API analysis of the application portfolio.
def _build_system_prompt() -> str:
    return """You are a senior Enterprise Architect with 5+ years of experience in 
application portfolio management using LeanIX. You analyze portfolios and produce 
clear, actionable rationalization recommendations.

Always respond in valid JSON only. No markdown, no explanation outside the JSON.

Your JSON must follow this exact structure:
{
  "executive_summary": "2-3 sentence summary for a CTO audience",
  "total_potential_saving_usd": <integer>,
  "retire": [
    {
      "app_name": "...",
      "reason": "...",
      "estimated_saving_usd": <integer>,
      "urgency": "immediate|6-months|12-months"
    }
  ],
  "modernize": [
    {
      "app_name": "...",
      "reason": "...",
      "recommended_approach": "...",
      "priority": "high|medium|low"
    }
  ],
  "key_risks": [
    {
      "risk": "...",
      "affected_apps": ["..."],
      "mitigation": "..."
    }
  ],
  "quick_wins": ["...", "..."],
  "capability_gaps": ["...", "..."]
}"""

# Build a textual representation of the application portfolio, including an overview and detailed information about each application. This text will be included in the prompt sent to the Anthropic API for analysis and recommendation generation.
def _build_portfolio_text(df, summary: dict) -> str:
    lines = []
    lines.append(f"PORTFOLIO OVERVIEW")
    lines.append(f"Total applications: {summary['total_apps']}")
    lines.append(f"Total annual cost: ${summary['total_cost']:,}")
    lines.append(f"High tech debt (>=7): {summary['high_debt_count']} apps")
    lines.append(f"Lifecycle breakdown: {summary['lifecycle_counts']}")
    lines.append(f"Rationalization quadrants: {summary['quadrant_counts']}")
    lines.append(f"Cost by hosting: {summary['hosting_cost']}")
    lines.append(f"\nAVERAGE TECH DEBT BY CAPABILITY:")
    for cap, score in summary['capability_debt'].items():
        lines.append(f"  {cap}: {score}/10")

    lines.append(f"\nFULL APPLICATION LIST:") # Add a detailed list of all applications in the portfolio, including key attributes such as name, business capability, lifecycle stage, tech debt score, business value score, annual cost, hosting type, age, rationalization quadrant, and risk score. This detailed information will provide the Anthropic API with the necessary context to generate specific recommendations for each application based on its characteristics and performance within the portfolio.
    cols = [
        "app_name", "business_capability", "lifecycle_stage",
        "tech_debt_score", "business_value_score", "annual_cost_usd",
        "hosting_type", "age_years", "rationalization_quadrant", "risk_score"
    ]
    for _, row in df[cols].iterrows(): # Iterate through each application in the DataFrame and append its details to the portfolio text. This includes key attributes such as the application name, business capability, lifecycle stage, tech debt score, business value score, annual cost, hosting type, age in years, rationalization quadrant, and calculated risk score. This detailed information will be used by the Anthropic API to analyze each application and generate specific recommendations based on its characteristics and performance within the portfolio.
        lines.append(
            f"  {row['app_name']} | {row['business_capability']} | "
            f"{row['lifecycle_stage']} | TD:{row['tech_debt_score']} "
            f"BV:{row['business_value_score']} | "
            f"${int(row['annual_cost_usd']):,}/yr | "
            f"{row['hosting_type']} | Age:{row['age_years']}yrs | "
            f"Quadrant:{row['rationalization_quadrant']} | "
            f"Risk:{row['risk_score']}"
        )

    return "\n".join(lines)

# Build the user prompt that includes the portfolio text and specific instructions for the analysis. This prompt guides the Anthropic API to focus on identifying applications for retirement, modernization, capability overlaps, high-risk items, quick wins, and capability gaps based on the provided portfolio data.
def _build_user_prompt(portfolio_text: str) -> str:
    return f"""Analyze this enterprise application portfolio and produce a 
rationalization report in the exact JSON format specified.

Focus on:
1. Applications that should be retired (low value, high debt, end of life)
2. Applications that need modernization (high value but high debt — cannot retire)
3. Capability overlaps where multiple apps serve the same function
4. The highest risk items requiring immediate attention
5. Quick wins (low effort, high impact actions)

{portfolio_text}

Return only valid JSON. No other text."""

# Parse the raw response from the Anthropic API, which is expected to be in JSON format, and convert it into a Python dictionary. 
# If the response is not valid JSON, return a default dictionary with empty recommendations and an executive summary containing the first 500 characters of the raw response for context. 
# This function ensures that the application can handle cases where the API response may not be properly formatted and still provide some level of feedback to the user based on the content of the response.
def _parse_response(raw: str) -> dict:
    import re
    try:
        cleaned = raw.strip()
        # Strip markdown code fences if present
        cleaned = re.sub(r'^```json\s*', '', cleaned)
        cleaned = re.sub(r'^```\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON object with regex as last resort
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        # Fallback — return raw text in summary field
        return {
            "executive_summary": raw,
            "retire": [],
            "modernize": [],
            "key_risks": [],
            "quick_wins": [],
            "capability_gaps": [],
            "total_potential_saving_usd": 0
        }