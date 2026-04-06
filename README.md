# LeanIX GenAI Portfolio Analyzer

> Reduce 3-week application portfolio rationalization to few minutes using GenAI + LeanIX data.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Claude](https://img.shields.io/badge/Powered%20by-Claude%20Sonnet-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What this does

Enterprise architects spend 3–6 weeks manually analyzing application portfolios —
running workshops, building spreadsheets, and producing rationalization recommendations.

This tool does it in few minutes:

1. Upload a LeanIX-style portfolio CSV (or use the included sample with 30 apps)
2. Claude analyzes tech debt, business value, cost, and lifecycle data
3. Get an AI-generated rationalization report: what to retire, modernize, invest in, or monitor
4. Download a professional PDF report or JSON export

---

## Sample output

A real AI-generated rationalization report from the included 30-app sample portfolio:

📄 **[View sample PDF report](docs/screenshots/portfolio_rationalization_report.pdf)**

The report includes:
- Executive summary for CTO audience
- Retire recommendations with estimated savings
- Modernize priorities with recommended approaches      
- Key risks and mitigations
- Quick wins
- Portfolio charts: quadrant scatter, lifecycle breakdown, cost by hosting, capability heatmap

---

## Architecture
```
LeanIX CSV export
      │
      ▼
data_loader.py ──► validate + enrich + score
      │
      ▼
analyzer.py ──────► Claude Sonnet API
      │                    │
      │              system prompt:
      │              "You are a senior EA
      │               with 20yrs LeanIX APM
      │               experience..."
      │
      ▼
structured JSON response
      │
      ├──► visualizer.py ──► Plotly charts
      │
      ├──► app.py ──────────► Streamlit UI
      │
      └──► exporter.py ─────► PDF + JSON
```

---

## Quickstart
```bash
# 1. Clone
git clone https://github.com/suduat/leanix-genai-analyzer.git
cd leanix-genai-analyzer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API key
cp .env.example .env
# Edit .env and add your Anthropic API key
# Get one at: https://console.anthropic.com

# 5. Run
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Sample data

The repo includes `data/sample_portfolio.csv` — 30 realistic enterprise applications
spanning Finance, HR, Integration, Analytics, and more. Use it to test the tool
without needing a real LeanIX export.

See `data/schema.md` for the full column reference and how to export from LeanIX.

---

## Key files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI — 3 tabs: Upload, Dashboard, AI Report |
| `utils/data_loader.py` | CSV parsing, validation, derived column generation |
| `utils/analyzer.py` | Prompt engineering + Claude API integration |
| `utils/visualizer.py` | Plotly charts: quadrant scatter, lifecycle bar, cost donut, capability heatmap |
| `utils/exporter.py` | PDF report (with embedded charts) + JSON export |
| `config.py` | Model name, token limits, column definitions |
| `data/sample_portfolio.csv` | 30-app sample dataset |
| `data/schema.md` | Column definitions + LeanIX export mapping |

---

## What I learned building this

**Prompt engineering for structured output**
Getting Claude to return consistent, parseable JSON required careful system prompt
design — specifying the exact schema, handling edge cases, and building a
fallback parser for partial responses.

**LeanIX + AI = rare combination**
Almost nobody combines LeanIX APM expertise with GenAI implementation.
The tool demonstrates that EA practitioners can apply emerging AI to solve
real portfolio management problems — not just talk about it.

**Token economics matter**
A 30-app portfolio analysis costs ~$0.03 per run with Claude Sonnet.
Prompt design (summarising the CSV rather than dumping raw rows) keeps
token usage low while preserving analytical quality.

**Where AI judgment breaks down**
Claude occasionally over-recommends retirement for apps with high cost but
legitimate strategic value. The quadrant chart provides a human sanity-check
layer — the AI is a first draft, not the final word.

---

## Estimated API cost

| Usage | Cost |
|---|---|
| Single analysis (30 apps) | ~$0.03 |
| 10 analyses/day | ~$0.30/day |
| Monthly (active development) | ~$5–10/month |

---

## Roadmap

- [ ] LeanIX MCP server integration (live data, no CSV export needed)
- [ ] Multi-portfolio comparison
- [ ] Agentic mode: Claude autonomously queries LeanIX and generates report
- [ ] AWS Well-Architected alignment scoring

---

## About

I build enterprise architecture practices as well as cloud architecture solutions— translating complex business problems into scalable, governed, and deliverable technology solutions. 

Certifications: AWS SAP-Pro · LeanIX EAM Associate · TOGAF

[LinkedIn](https://www.linkedin.com/in/sudeshna-sarkar-76aa7612/) ·
[GitHub](https://github.com/suduat)

---

## License

MIT — free to use, adapt, and build on.