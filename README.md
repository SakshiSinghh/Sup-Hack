# ProcurementOS

Procurement teams spend hours doing the same thing over and over: pulling vendor info from scattered sources, checking compliance manually, and building ROI comparisons in spreadsheets. ProcurementOS automates that pipeline with a set of coordinated AI agents so a vendor evaluation that used to take days takes minutes.

## Live Demo
https://sup-hack-mjchp6rvprq3wzgtdqrtqv.streamlit.app/

## How it works

ProcurementOS runs four agents, coordinated by an orchestrator:

- **Zo (Orchestrator)** — routes tasks between agents, keeps context consistent across a full evaluation run, and assembles the final recommendation.
- **Exa (Vendor Intelligence)** — researches vendors in real time using the Exa API: company background, funding, news, and red flags that wouldn't show up in a static database.
- **Workato Execution Agent** — handles the actual workflow automation, pushing approved vendors into downstream systems (e.g. procurement/ERP tools) without manual data entry.
- **Monitoring Agent** — tracks vendors post-onboarding for changes in risk, compliance status, or performance, instead of treating evaluation as a one-time event.

What ties these together is the **Procurement Knowledge Graph** — a structured map of vendors, relationships, risk signals, and past evaluation outcomes that the agents read from and write back to. This is what makes recommendations improve over time instead of starting from zero on every request, and it's the core differentiator versus a plain LLM wrapper.

## Features

- Vendor research pulled live from the web, not a stale database
- Compliance and risk flags surfaced automatically, with sources cited
- ROI scoring that compares vendors side by side on cost, risk, and fit
- One-click handoff into procurement workflows via Workato
- Ongoing monitoring after a vendor is onboarded, not just at evaluation time

## Tech Stack

- Python
- Streamlit
- Exa API
- Workato
- Plotly
- Requests
- python-dotenv

## Installation

```bash
git clone https://github.com/yourusername/procurementos.git
cd procurementos
pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys:

```
EXA_API_KEY=your_exa_key
WORKATO_API_KEY=your_workato_key
```

Then run the app:

```bash
streamlit run app.py
```

## Usage

1. Enter a vendor name or upload a list of candidates.
2. Zo kicks off research (Exa) and compliance checks in parallel.
3. Review the ROI-scored comparison and evidence trail for each vendor.
4. Approve a vendor to trigger the Workato handoff into your procurement workflow.
5. The monitoring agent keeps watching that vendor going forward.

## Status

Hackathon prototype - core agent pipeline and knowledge graph are working; production hardening (auth, error handling, broader integrations) is next.
