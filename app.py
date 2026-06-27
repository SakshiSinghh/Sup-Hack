import streamlit as st
import os, time, requests, json, pathlib
import plotly.graph_objects as pgo
from datetime import datetime, timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
EXA_API_KEY         = os.getenv("EXA_API_KEY", "")
WORKATO_WEBHOOK_URL = os.getenv("WORKATO_WEBHOOK_URL", "")
ZO_API_KEY          = os.getenv("ZO_API_KEY", "")
LOG_FILE            = pathlib.Path("monitoring_log.json")

st.set_page_config(page_title="ProcurementOS", page_icon="📋", layout="wide", initial_sidebar_state="expanded")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, html, body, [class*="css"] { font-family:'Inter', sans-serif !important; box-sizing:border-box; }
.main .block-container, [data-testid="stMainBlockContainer"], div[data-testid="stMainBlockContainer"] { max-width:1040px !important; width:1040px !important; margin-left:auto !important; margin-right:auto !important; padding:1.25rem 1.5rem 2rem !important; }
@media (max-width:1120px) { .main .block-container, [data-testid="stMainBlockContainer"], div[data-testid="stMainBlockContainer"] { width:calc(100vw - 2rem) !important; max-width:calc(100vw - 2rem) !important; padding-left:1rem !important; padding-right:1rem !important; } }
.block-container > div { padding-top:0 !important; }
header[data-testid="stHeader"] { display:none; }
section[data-testid="stSidebar"] { background:#fff; border-right:1px solid #E5E7EB; width:220px !important; }
section[data-testid="stSidebar"] > div { padding:0; }
section[data-testid="stSidebar"] .stButton > button { background:transparent !important; border:none !important; border-radius:6px !important; color:#6B7280 !important; font-size:.84rem !important; font-weight:500 !important; text-align:left !important; justify-content:flex-start !important; padding:.45rem .85rem !important; width:100% !important; box-shadow:none !important; }
section[data-testid="stSidebar"] .stButton > button:hover { background:#EFF6FF !important; color:#2563EB !important; }
.stButton > button { border-radius:8px !important; font-weight:600 !important; min-height:2.35rem !important; }
.stButton > button[kind="primary"] { background:#2563EB !important; border:none !important; color:#fff !important; box-shadow:0 1px 3px rgba(37,99,235,.18) !important; }
.stButton > button[kind="primary"]:hover { background:#1D4ED8 !important; }
.stButton > button[kind="secondary"] { background:#fff !important; border:1px solid #E5E7EB !important; color:#374151 !important; }
.stButton > button[kind="secondary"]:hover { border-color:#93C5FD !important; color:#1D4ED8 !important; }
.stTextArea > div > div, .stSelectbox > div > div, .stNumberInput > div > div, .stTextInput > div > div, .stMultiSelect > div > div { border-radius:8px !important; border-color:#E5E7EB !important; background:#fff !important; font-size:.86rem !important; }
label { font-size:.8rem !important; font-weight:700 !important; color:#374151 !important; }
.stTabs [data-baseweb="tab-list"] { background:#F8FAFC; border:1px solid #E5E7EB; border-radius:10px; padding:4px; gap:3px; max-width:100%; }
.stTabs [data-baseweb="tab"] { border-radius:8px; color:#64748B; font-size:.82rem; font-weight:650; padding:.45rem .9rem; }
.stTabs [aria-selected="true"] { background:#fff !important; color:#0F172A !important; box-shadow:0 1px 3px rgba(15,23,42,.08) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:1rem; }
.card, .card-sm, .metric-card, .rec-vendor-card, .source-card, .risk-card, .log-shell { background:#fff; border:1px solid #E5E7EB; box-shadow:0 1px 2px rgba(15,23,42,.04); }
.card { border-radius:10px; padding:1rem 1.1rem; margin-bottom:.75rem; }
.card-sm { border-radius:8px; padding:.75rem .85rem; }
.metric-card { border-radius:10px; padding:.9rem 1rem; }
.rec-vendor-card { border-radius:12px; padding:1.2rem 1.35rem; border-color:#BFDBFE; box-shadow:0 8px 28px rgba(37,99,235,.08); max-width:100%; }
.source-card { border-radius:10px; padding:.95rem; height:100%; }
.risk-card { border-radius:10px; padding:.9rem 1rem; height:100%; }
.log-shell { border-radius:12px; padding:1rem; }
.card:empty, .card-sm:empty, .wizard-card:empty, .rec-vendor-card:empty { display:none !important; }
.badge, .chip { display:inline-flex; align-items:center; gap:5px; padding:2px 9px; border-radius:999px; font-size:.71rem; font-weight:700; white-space:nowrap; }
.bg-green { background:#ECFDF5; color:#047857; border:1px solid #A7F3D0; }
.bg-amber { background:#FFFBEB; color:#B45309; border:1px solid #FDE68A; }
.bg-red { background:#FEF2F2; color:#B91C1C; border:1px solid #FECACA; }
.bg-blue { background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; }
.bg-gray { background:#F8FAFC; color:#64748B; border:1px solid #E2E8F0; }
.bg-purple { background:#EEF2FF; color:#4338CA; border:1px solid #C7D2FE; }
.section-label { font-size:.68rem; font-weight:800; color:#94A3B8; text-transform:uppercase; letter-spacing:.08em; margin-bottom:.45rem; }
.q-label { font-size:.68rem; font-weight:800; color:#2563EB; text-transform:uppercase; letter-spacing:.09em; margin-bottom:3px; }
.q-title { font-size:1.25rem; font-weight:800; color:#111827; line-height:1.2; margin-bottom:3px; }
.q-sub { font-size:.8rem; color:#64748B; margin-bottom:.8rem; }
.metric-val { font-size:1.55rem; font-weight:800; color:#111827; line-height:1; }
.metric-lbl { font-size:.72rem; color:#64748B; margin-top:4px; font-weight:600; }
.table-wrap { border:1px solid #E5E7EB; border-radius:10px; overflow:hidden; background:#fff; }
.data-table { width:100%; border-collapse:collapse; }
.data-table th { background:#F8FAFC; font-size:.69rem; font-weight:800; color:#64748B; text-transform:uppercase; letter-spacing:.06em; padding:9px 11px; border-bottom:1px solid #E5E7EB; text-align:left; }
.data-table td { padding:10px 11px; border-bottom:1px solid #F1F5F9; font-size:.82rem; color:#334155; vertical-align:middle; }
.data-table tr:last-child td { border-bottom:none; }
.data-table tr:hover td { background:#F8FAFC; }
.callout { background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:.65rem .85rem; font-size:.82rem; color:#1E40AF; margin-bottom:.8rem; }
.callout-green { background:#ECFDF5; border-color:#A7F3D0; color:#065F46; }
.callout-amber { background:#FFFBEB; border-color:#FDE68A; color:#92400E; }
.cert-chip { display:inline-flex; align-items:center; gap:6px; border-radius:999px; padding:5px 10px; font-size:.73rem; font-weight:700; white-space:nowrap; }
.cert-chip.verified { background:#ECFDF5; border:1px solid #A7F3D0; color:#047857; }
.cert-chip.pending { background:#FFFBEB; border:1px solid #FDE68A; color:#B45309; }
.cert-chip.missing { background:#F8FAFC; border:1px solid #E2E8F0; color:#94A3B8; }
.help-dot { display:inline-flex; align-items:center; justify-content:center; width:16px; height:16px; border-radius:50%; background:#F1F5F9; color:#64748B; font-size:.68rem; font-weight:800; cursor:help; }
.progress-bg { background:#EEF2F7; border-radius:999px; height:8px; width:100%; overflow:hidden; }
.progress-fill { height:8px; border-radius:999px; }
.sidebar-divider { border:none; border-top:1px solid #F3F4F6; margin:1rem 0; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
BUDGET_MAP   = {"< $5k/yr":"low","$5k–$20k/yr":"mid","$20k–$50k/yr":"mid-high","$50k+/yr":"high"}
TIER_ORDER   = {"low":1,"mid":2,"mid-high":3,"high":4}
COMP_POS     = ["soc2","soc 2","iso 27001","iso27001","gdpr","certified","certification","audit","hipaa","pci","compliant","encryption"]
COMP_NEG     = ["breach","lawsuit","fine","outage","vulnerability","hack","leaked","incident","violated","penalty"]
CATEGORIES   = ["Meeting Transcription","CRM","Project Management","HR","Data & Analytics","Other"]

VENDORS = {
    "Meeting Transcription":[
        {"name":"Fireflies.ai","description":"AI meeting recorder with search, summaries and CRM sync.","url":"https://fireflies.ai","pricing_tier":"mid","annual_cost":"$10k–$18k","setup":"1 week","uptime":"99.9%","data_residency":"US / EU","features":["transcription","summary","crm","search","integrations","ai"]},
        {"name":"Otter.ai","description":"Real-time transcription with live collaboration and notes.","url":"https://otter.ai","pricing_tier":"low","annual_cost":"$4k–$10k","setup":"1 day","uptime":"99.5%","data_residency":"US","features":["transcription","collaboration","search","zoom","teams"]},
        {"name":"Fathom","description":"Free AI notetaker for Zoom with highlights and action items.","url":"https://fathom.video","pricing_tier":"low","annual_cost":"Free–$5k","setup":"< 1 day","uptime":"99.7%","data_residency":"US","features":["transcription","zoom","highlights","action items","free"]},
        {"name":"Granola","description":"AI notepad that enhances your own notes with meeting context.","url":"https://granola.ai","pricing_tier":"mid","annual_cost":"$8k–$15k","setup":"2 days","uptime":"99.5%","data_residency":"US","features":["notes","ai","summarization","mac"]},
    ],
    "CRM":[
        {"name":"HubSpot","description":"All-in-one CRM with marketing, sales and service hubs.","url":"https://hubspot.com","pricing_tier":"mid","annual_cost":"$15k–$40k","setup":"2–4 weeks","uptime":"99.99%","data_residency":"US / EU","features":["crm","email","pipeline","automation","reporting","integrations"]},
        {"name":"Salesforce","description":"Enterprise CRM with deep customisation and AI capabilities.","url":"https://salesforce.com","pricing_tier":"high","annual_cost":"$50k+","setup":"4–12 weeks","uptime":"99.9%","data_residency":"US / EU / APAC","features":["crm","enterprise","custom","ai","analytics","pipeline"]},
        {"name":"Pipedrive","description":"Sales-focused CRM built around deal pipeline management.","url":"https://pipedrive.com","pricing_tier":"low","annual_cost":"$5k–$15k","setup":"3 days","uptime":"99.9%","data_residency":"US / EU","features":["pipeline","sales","email","mobile","reporting"]},
        {"name":"Attio","description":"Modern CRM with real-time enrichment and flexible views.","url":"https://attio.com","pricing_tier":"mid","annual_cost":"$12k–$25k","setup":"1 week","uptime":"99.9%","data_residency":"US / EU","features":["crm","enrichment","collaboration","views","integrations"]},
    ],
    "Project Management":[
        {"name":"Linear","description":"Fast, opinionated project management for engineering teams.","url":"https://linear.app","pricing_tier":"mid","annual_cost":"$8k–$20k","setup":"1 day","uptime":"99.9%","data_residency":"US / EU","features":["issues","sprints","roadmap","github","fast","integrations"]},
        {"name":"Notion","description":"All-in-one workspace combining docs, wikis and projects.","url":"https://notion.so","pricing_tier":"low","annual_cost":"$4k–$12k","setup":"1 week","uptime":"99.9%","data_residency":"US / EU","features":["docs","database","kanban","wiki","collaboration"]},
        {"name":"Jira","description":"Enterprise issue tracking and agile project management.","url":"https://atlassian.com/jira","pricing_tier":"mid","annual_cost":"$10k–$30k","setup":"2–4 weeks","uptime":"99.9%","data_residency":"US / EU / APAC","features":["agile","sprint","reporting","enterprise","integrations"]},
        {"name":"Asana","description":"Work management platform for cross-functional teams.","url":"https://asana.com","pricing_tier":"mid","annual_cost":"$12k–$30k","setup":"1–2 weeks","uptime":"99.9%","data_residency":"US / EU","features":["tasks","goals","timeline","portfolio","automation"]},
    ],
    "HR":[
        {"name":"Rippling","description":"Unified HR, IT and Finance platform for modern teams.","url":"https://rippling.com","pricing_tier":"mid","annual_cost":"$15k–$35k","setup":"2–4 weeks","uptime":"99.9%","data_residency":"US / EU","features":["payroll","benefits","it","onboarding","compliance","integrations"]},
        {"name":"Workday","description":"Enterprise HR and financial management cloud platform.","url":"https://workday.com","pricing_tier":"high","annual_cost":"$50k+","setup":"3–6 months","uptime":"99.7%","data_residency":"US / EU","features":["hris","payroll","talent","analytics","enterprise"]},
        {"name":"BambooHR","description":"HR software for small and mid-sized businesses.","url":"https://bamboohr.com","pricing_tier":"low","annual_cost":"$6k–$18k","setup":"1–2 weeks","uptime":"99.9%","data_residency":"US","features":["ats","onboarding","performance","payroll","reporting"]},
        {"name":"Lattice","description":"People management for performance reviews and OKRs.","url":"https://lattice.com","pricing_tier":"mid","annual_cost":"$10k–$25k","setup":"1–2 weeks","uptime":"99.9%","data_residency":"US / EU","features":["performance","okrs","engagement","grow","analytics"]},
    ],
    "Data & Analytics":[
        {"name":"Snowflake","description":"Cloud data platform for data warehousing and sharing.","url":"https://snowflake.com","pricing_tier":"high","annual_cost":"$30k+","setup":"2–4 weeks","uptime":"99.9%","data_residency":"US / EU / APAC","features":["data warehouse","sql","sharing","ml","governance"]},
        {"name":"Databricks","description":"Unified analytics platform for data engineering and ML.","url":"https://databricks.com","pricing_tier":"high","annual_cost":"$40k+","setup":"4–8 weeks","uptime":"99.9%","data_residency":"US / EU","features":["ml","data engineering","notebooks","delta lake","governance"]},
        {"name":"Looker","description":"Business intelligence and data exploration platform.","url":"https://looker.com","pricing_tier":"mid","annual_cost":"$20k–$50k","setup":"2–4 weeks","uptime":"99.9%","data_residency":"US / EU","features":["bi","dashboards","sql","explore","embedding"]},
        {"name":"Metabase","description":"Open-source BI tool with a simple, no-code interface.","url":"https://metabase.com","pricing_tier":"low","annual_cost":"$5k–$20k","setup":"3 days","uptime":"99.5%","data_residency":"Self-hosted","features":["bi","dashboards","sql","open-source","embedding"]},
    ],
    "Other":[
        {"name":"Vendor A","description":"Leading solution in this category with strong reviews.","url":"#","pricing_tier":"mid","annual_cost":"TBD","setup":"TBD","uptime":"99.9%","data_residency":"US","features":[]},
        {"name":"Vendor B","description":"Popular alternative with a strong integration ecosystem.","url":"#","pricing_tier":"low","annual_cost":"TBD","setup":"TBD","uptime":"99.5%","data_residency":"US","features":[]},
        {"name":"Vendor C","description":"Enterprise-grade option with advanced compliance features.","url":"#","pricing_tier":"high","annual_cost":"TBD","setup":"TBD","uptime":"99.9%","data_residency":"US / EU","features":[]},
    ],
}

# ── Monitoring log ─────────────────────────────────────────────────────────────
def load_log():
    if LOG_FILE.exists():
        try: return json.loads(LOG_FILE.read_text())
        except: return []
    return []

def append_log(entry):
    log = load_log(); log.append(entry)
    LOG_FILE.write_text(json.dumps(log, indent=2))

# ── Exa ────────────────────────────────────────────────────────────────────────
def exa_search(query, n=5):
    if not EXA_API_KEY: return []
    try:
        from exa_py import Exa
        exa = Exa(api_key=EXA_API_KEY)
        res = exa.search_and_contents(query, num_results=n, text={"max_characters":600})
        return [{"title":r.title or "","url":r.url or "","text":r.text or ""} for r in res.results]
    except: return []

# ── Agents ─────────────────────────────────────────────────────────────────────
def agent_vendor_research(category, description):
    results  = exa_search(f"best {category} software vendors pricing comparison 2024", n=8)
    results += exa_search(f"{category} software reviews G2 Reddit alternatives", n=5)
    fallbacks = VENDORS.get(category, VENDORS["Other"])
    seen, enriched = set(), []
    for r in results:
        for v in fallbacks:
            if v["name"].lower() in r.get("title","").lower() and v["name"] not in seen:
                e = dict(v); e["exa_snippet"] = r["text"][:260]; enriched.append(e); seen.add(v["name"])
    for v in fallbacks:
        if v["name"] not in seen: enriched.append(dict(v))
    return enriched[:4]

def agent_risk_compliance(vendors):
    out = {}
    for v in vendors[:4]:
        name = v["name"]
        res  = exa_search(f"{name} SOC2 GDPR ISO27001 security compliance certification", n=4)
        res += exa_search(f"{name} data breach security incident", n=3)
        txt  = " ".join(r.get("text","") + r.get("title","") for r in res).lower()
        pos  = list(dict.fromkeys([k.upper() for k in COMP_POS if k in txt]))[:6]
        neg  = list(dict.fromkeys([k.upper() for k in COMP_NEG if k in txt]))[:3]
        risk = "High" if (len(neg)>=2 or (neg and not pos)) else ("Low" if len(pos)>=3 and not neg else "Medium")
        certs = {
            "SOC2":     "verified" if any("soc" in p.lower() for p in pos) else "missing",
            "GDPR":     "verified" if any("gdpr" in p.lower() for p in pos) else "missing",
            "ISO27001": "verified" if any("iso" in p.lower() for p in pos) else "missing",
            "HIPAA":    "verified" if any("hipaa" in p.lower() for p in pos) else "pending",
            "PCI":      "verified" if any("pci" in p.lower() for p in pos) else "missing",
        }
        parts = []
        if pos: parts.append(f"Verified compliance signals: {', '.join(pos)}.")
        if neg: parts.append(f"Risk signals: {', '.join(neg)}.")
        if not parts: parts.append("No strong compliance signals found in public sources.")
        out[name] = {"risk_level":risk,"positive_signals":pos,"negative_signals":neg,"certs":certs,
                     "summary":" ".join(parts),"sources":[r["url"] for r in res[:3] if r.get("url")]}
    return out

def agent_roi(vendors, compliance, budget, description, team_size):
    bt = BUDGET_MAP.get(budget,"mid"); dw = set(description.lower().split())
    out = []
    for v in vendors:
        vn = TIER_ORDER.get(v.get("pricing_tier","mid"),2)
        bn = TIER_ORDER.get(bt,2)
        cost   = max(0, 30 - abs(bn-vn)*10)
        feat   = min(30, len(dw & set(f.lower() for f in v.get("features",[]))) * 6)
        risk   = compliance.get(v["name"],{}).get("risk_level","Medium")
        comp_s = {"Low":25,"Medium":15,"High":5}.get(risk,15)
        adopt  = 15 if (v.get("pricing_tier")=="low" and team_size<=50) else (5 if v.get("pricing_tier")=="high" and team_size<=20 else 10)
        total  = cost + feat + comp_s + adopt
        strength = "strongest overall fit" if total>=80 else ("solid choice" if total>=65 else "viable option")
        rn = {"Low":"with minimal compliance risk","Medium":"with an acceptable risk profile","High":"— carries elevated compliance risk"}.get(risk,"")
        out.append({**v,"score":total,"risk_level":risk,
                    "compliance_summary":compliance.get(v["name"],{}).get("summary",""),
                    "rationale":f"{v['name']} is the {strength} {rn} for a {team_size}-person team.",
                    "breakdown":{"Cost Fit":cost,"Feature Match":feat,"Compliance":comp_s,"Adoption":adopt},
                    "breakdown_max":{"Cost Fit":30,"Feature Match":30,"Compliance":25,"Adoption":15}})
    out.sort(key=lambda x:x["score"], reverse=True)
    if out: out[0]["recommended"] = True
    return out

def agent_monitoring(vendor_name, category):
    news  = exa_search(f"{vendor_name} news funding product update 2024 2025", n=4)
    risks = exa_search(f"{vendor_name} outage downtime complaint 2024 2025", n=3)
    comps = exa_search(f"best {category} software alternative to {vendor_name} 2025", n=3)
    ns = [r["text"][:220] for r in news  if r.get("text")]
    rs = [r["text"][:220] for r in risks if r.get("text")]
    cs = [r["text"][:220] for r in comps if r.get("text")]
    nc = " ".join(ns).lower(); rc = " ".join(rs).lower()
    pos = any(kw in nc for kw in ["funding","raised","launch","growth","partnership","award"])
    neg = any(kw in rc for kw in ["outage","down","complaint","issue","slow","broken"])
    if pos and not neg:  h,hn = "Healthy",f"{vendor_name} showing positive growth signals."
    elif neg:            h,hn = "Watch",  f"{vendor_name} has reported issues — monitor closely."
    else:                h,hn = "Stable", f"{vendor_name} appears stable. No critical signals detected."
    alerts = []
    if "outage" in rc or "downtime" in rc: alerts.append({"type":"amber","msg":f"Outage/downtime reported for {vendor_name}. Check status page."})
    if "complaint" in rc:                  alerts.append({"type":"amber","msg":"User complaints detected. Consider a vendor review call."})
    if pos:                                alerts.append({"type":"green","msg":f"{vendor_name} growing — strong long-term stability signal."})
    if cs:                                 alerts.append({"type":"amber","msg":f"Potential better alternatives detected in the {category} market."})
    if not alerts:                         alerts.append({"type":"green","msg":"All clear. No critical signals. Next review in 30 days."})
    return {"health":h,"health_note":hn,"alerts":alerts,
            "news_snippets":ns[:2],"risk_snippets":rs[:2],"competitor_snippets":cs[:2],
            "competitor_found":bool(cs),"timestamp":datetime.utcnow().isoformat()+"Z"}

def trigger_workato(payload):
    if not WORKATO_WEBHOOK_URL: return False, "No webhook URL configured"
    try:
        r = requests.post(WORKATO_WEBHOOK_URL, json=payload, timeout=10)
        return r.status_code < 400, f"HTTP {r.status_code}"
    except Exception as e: return False, str(e)

def _zo_fallback(vendor, category, team_size, risk):
    return f"""**1. Onboarding steps for your {team_size}-person team**
- Week 1: Set up accounts, configure SSO and admin permissions
- Week 2: Pilot with 5 power users, gather early feedback
- Week 3–4: Full team rollout with a structured training session
- Month 2: Monitor adoption weekly, address drop-off early

**2. Common pitfalls with {category} tools**
- Low adoption if the team isn't trained before go-live
- Integration delays with existing tools — plan extra time
- Data migration taking 2x longer than expected

**3. Measuring ROI at 90 days**
- Track weekly active users vs total licences purchased
- Survey the team at Day 30 and Day 90 on time saved
- Compare output quality before and after implementation

**4. Risk mitigation — {risk} compliance profile**
- Request {vendor}'s latest security audit report before go-live
- Ensure a Data Processing Agreement (DPA) is signed
- Assign an internal data owner for quarterly access reviews"""


def ask_zo(prompt: str, vendor: str = "", category: str = "", team_size: int = 0, risk: str = "Medium") -> str:
    if not ZO_API_KEY:
        return _zo_fallback(vendor, category, team_size, risk)
    try:
        resp = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={"Authorization": f"Bearer {ZO_API_KEY}", "Content-Type": "application/json"},
            json={"input": prompt},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("output", str(data))
        return _zo_fallback(vendor, category, team_size, risk)
    except Exception:
        return _zo_fallback(vendor, category, team_size, risk)


def agent_execution(top, req):
    payload = {
        "event":"procurement_approved","timestamp":datetime.utcnow().isoformat()+"Z",
        "category":req["category"],"description":req["description"],"budget":req["budget"],
        "team_size":req["team_size"],"timeline":req["timeline"],
        "recommended_vendor":top["name"],"score":top["score"],"risk_level":top["risk_level"],
        "rationale":top["rationale"],"vendor_url":top.get("url",""),
        "annual_cost":top.get("annual_cost",""),"setup_time":top.get("setup",""),
    }
    ok, msg = trigger_workato(payload)
    return {"success":ok,"msg":msg,"payload":payload}

# ── UI helpers ─────────────────────────────────────────────────────────────────
def sc(s): return "#059669" if s>=80 else ("#D97706" if s>=60 else "#DC2626")

def badge(level):
    c = {"Low":"bg-green","Medium":"bg-amber","High":"bg-red"}.get(level,"bg-gray")
    return f'<span class="badge {c}">● {level}</span>'

def cert_chip(label, status):
    icon = {"verified":"✓","pending":"~","missing":"—"}.get(status,"—")
    return f'<span class="cert-chip {status}">{icon} {label}</span>'

def radar(breakdown, max_vals, name):
    cats = list(breakdown.keys()); vals = [breakdown[c]/max_vals[c]*100 for c in cats]
    fig = pgo.Figure()
    fig.add_trace(pgo.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]], fill='toself',
        fillcolor='rgba(108,99,255,.08)', line=dict(color='#6C63FF', width=2)))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True,range=[0,100],tickfont=dict(size=8,color="#9CA3AF"),gridcolor="#F3F4F6",linecolor="#F3F4F6"),
            angularaxis=dict(tickfont=dict(size=10,color="#374151")),
            bgcolor="white"),
        showlegend=False, margin=dict(l=45,r=45,t=25,b=25), paper_bgcolor="white", height=240)
    return fig

def wizard_bar(step):
    steps = ["What","Requirements","Budget","Review"]
    h = '<div style="display:flex;align-items:center;gap:0;margin-bottom:2rem">'
    for i, lbl in enumerate(steps):
        n = i+1; done=n<step; active=n==step
        bg = "#6C63FF" if (done or active) else "#F3F4F6"
        fg = "#fff" if (done or active) else "#9CA3AF"
        bd = "none" if (done or active) else "1px solid #E5E7EB"
        txt = "✓" if done else str(n)
        lc  = "#6C63FF" if (done or active) else "#9CA3AF"
        lf  = "600" if active else "500"
        circ = f'<div style="width:26px;height:26px;border-radius:50%;background:{bg};border:{bd};color:{fg};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0">{txt}</div>'
        h += f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px">{circ}<span style="font-size:.65rem;font-weight:{lf};color:{lc};white-space:nowrap">{lbl}</span></div>'
        if i < len(steps)-1:
            lnc = "#6C63FF" if done else "#E5E7EB"
            h += f'<div style="flex:1;height:2px;background:{lnc};margin:0 6px;margin-bottom:18px"></div>'
    h += '</div>'
    st.markdown(h, unsafe_allow_html=True)

def agent_block(title, state="running"):
    dot_color    = "#059669" if state=="done" else "#6C63FF"
    anim         = "" if state=="done" else "animation:pulse 1s infinite;"
    status_label = "Complete" if state=="done" else "Running"
    status_bg    = "#ECFDF5" if state=="done" else "#F5F3FF"
    status_color = "#059669" if state=="done" else "#6C63FF"
    check        = "&#10003; " if state=="done" else ""
    st.markdown(f"""
<div style="border:1px solid #E5E7EB;border-radius:10px;padding:.85rem 1.1rem;margin-bottom:.5rem;background:#fff">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:8px;height:8px;border-radius:50%;background:{dot_color};flex-shrink:0;{anim}"></div>
    <div style="font-size:.845rem;font-weight:600;color:#111827;flex:1">{title}</div>
    <span style="font-size:.7rem;font-weight:600;background:{status_bg};color:{status_color};border-radius:6px;padding:2px 8px">{check}{status_label}</span>
  </div>
</div>""", unsafe_allow_html=True)

def log_line(text, color="#374151", bold=False):
    w = "font-weight:600;" if bold else ""
    st.markdown(f'<div style="display:flex;align-items:center;gap:8px;padding:3px 0 3px 1.1rem;font-size:.8rem;color:{color};{w}"><div style="width:4px;height:4px;border-radius:50%;background:#D1D5DB;flex-shrink:0"></div>{text}</div>', unsafe_allow_html=True)

def esc(value):
    return str(value).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def help_dot(text):
    return f'<span class="help-dot" title="{esc(text)}">?</span>'

def source_title(url):
    try:
        parsed = urlparse(url)
        host = parsed.netloc.replace("www.","") or "Source"
        path = parsed.path.strip("/").replace("-"," ").replace("_"," ")
        label = path.split("/")[-1][:58] if path else host
        return label.title() if label else host
    except Exception:
        return "Source"

def source_type(url):
    host = urlparse(url).netloc.lower() if url else ""
    if any(x in host for x in ["g2", "capterra", "reddit"]): return "Review"
    if any(x in host for x in ["status", "trust", "security", "compliance"]): return "Trust"
    if any(x in host for x in ["news", "techcrunch", "forbes", "businesswire"]): return "News"
    return "Web"

def severity_chip(level):
    palette = {
        "Success": "bg-green", "Info": "bg-blue", "Warning": "bg-amber", "Critical": "bg-red",
        "Low": "bg-green", "Medium": "bg-amber", "High": "bg-red",
    }
    return f'<span class="chip {palette.get(level,"bg-gray")}">{level}</span>'

def progress_row(label, value, max_value, color, tip):
    pct = int(value / max_value * 100) if max_value else 0
    return f'''<div style="margin-bottom:13px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px">
        <span style="font-size:.82rem;font-weight:700;color:#334155">{label} {help_dot(tip)}</span>
        <span style="font-size:.8rem;font-weight:800;color:{color}">{value}/{max_value}</span>
      </div>
      <div class="progress-bg"><div class="progress-fill" style="width:{pct}%;background:{color}"></div></div>
    </div>'''

# ── Session init ───────────────────────────────────────────────────────────────
DEFS = {"page":"home","wizard_step":1,"w_category":"Meeting Transcription","w_description":"",
        "w_budget":"$5k–$20k/yr","w_team_size":20,"w_timeline":"Within 1 month",
        "request":None,"vendors":None,"compliance":None,"scores":None,
        "execution_result":None,"monitoring_result":None,"zo_response":None,"zo_vendor":None}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k] = v

def go(p): st.session_state.page=p; st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="padding:1.3rem 1.1rem .9rem;border-bottom:1px solid #F3F4F6">
  <div style="display:flex;align-items:center;gap:9px">
    <div style="width:28px;height:28px;background:#6C63FF;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:800">P</div>
    <div>
      <div style="font-weight:800;font-size:.9rem;color:#111827;line-height:1">ProcurementOS</div>
      <div style="font-size:.62rem;color:#9CA3AF;margin-top:1px">AI Procurement Department</div>
    </div>
  </div>
</div>
<div style="padding:.7rem .5rem 0">
""", unsafe_allow_html=True)

    p = st.session_state.page
    def nav(label, pid):
        prefix = "●  " if p==pid else "    "
        if st.button(f"{prefix}{label}", key=f"nav_{pid}", use_container_width=True): go(pid)

    nav("Home",        "home")
    nav("New Mission", "wizard")
    nav("Monitoring",  "monitoring")
    nav("Reports",     "reports")
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    nav("Settings",    "settings")

    if st.session_state.scores:
        top = st.session_state.scores[0]; req = st.session_state.request or {}
        color = sc(top["score"])
        st.markdown(f"""
<div style="margin:1rem .4rem 0;background:#F5F3FF;border:1px solid #DDD6FE;border-radius:10px;padding:.8rem">
  <div style="font-size:.63rem;font-weight:700;color:#7C3AED;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px">Active Mission</div>
  <div style="font-size:.83rem;font-weight:600;color:#1F1F3A">{req.get('category','')}</div>
  <div style="font-size:.75rem;color:#6B7280;margin-top:2px">{top['name']} · <span style="color:{color};font-weight:600">{top['score']}/100</span></div>
</div>""", unsafe_allow_html=True)

# ── Pages ──────────────────────────────────────────────────────────────────────

def page_home():
    st.markdown("""
<div style="padding:2.5rem 0 1.5rem">
  <div style="font-size:.72rem;font-weight:700;color:#6C63FF;text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px">AI Procurement Consultant</div>
  <h1 style="font-size:2.5rem;font-weight:800;color:#111827;line-height:1.15;margin:0 0 .9rem">I evaluate vendors the way<br>your exec team actually decides.</h1>
  <p style="font-size:1rem;color:#6B7280;max-width:500px;line-height:1.65;margin-bottom:1.6rem">Tell me what you're buying. I'll score the market, surface the risks Legal and Security need to see, and back every claim with evidence — structured around five questions.</p>
</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([1,3])
    with c1:
        if st.button("Start a new request", type="primary", use_container_width=True): go("wizard")

    st.markdown('<div style="margin:2.5rem 0 .5rem"><div class="section-label">Every recommendation answers</div></div>', unsafe_allow_html=True)
    qs = [
        ("1","What should I buy?","A clear pick, the price, and the one-paragraph why."),
        ("2","Why should I trust this?","The scoring model and compliance posture, transparent."),
        ("3","How does it compare?","Side-by-side against the alternatives you shortlisted."),
        ("4","What are the risks?","Flagged for Legal and Security, each with an owner."),
        ("5","What evidence supports this?","Every claim traces to a source document."),
    ]
    col_a, col_b = st.columns(2)
    for i, (n, title, desc) in enumerate(qs):
        with (col_a if i%2==0 else col_b):
            st.markdown(f"""
<div class="card" style="margin-bottom:.7rem">
  <div style="display:flex;align-items:flex-start;gap:12px">
    <div style="width:26px;height:26px;background:#F5F3FF;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:.78rem;font-weight:800;color:#6C63FF;flex-shrink:0">{n}</div>
    <div>
      <div style="font-weight:700;font-size:.88rem;color:#111827;margin-bottom:3px">{title}</div>
      <div style="font-size:.78rem;color:#6B7280;line-height:1.55">{desc}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:2rem"><div class="section-label">How it works</div></div>', unsafe_allow_html=True)
    agents = [
        ("Vendor Research","Searches Exa for live vendor data, pricing, reviews and news","Exa API"),
        ("Risk & Compliance","Checks SOC2, GDPR, ISO27001 and breach history per vendor","Exa API"),
        ("ROI & Scoring","Weighted score across cost, features, compliance, adoption","Rule-based"),
        ("Execution","Fires Workato workflows on approval — Jira, Slack, Calendar","Workato"),
        ("Monitoring","30-day cycles — vendor health, competitor watch, alerts","Exa + Workato"),
    ]
    cols = st.columns(5)
    for col, (title, desc, tag) in zip(cols, agents):
        with col:
            st.markdown(f"""
<div class="card-sm" style="height:100%">
  <div style="font-weight:700;font-size:.82rem;color:#111827;margin-bottom:4px">{title}</div>
  <div style="font-size:.74rem;color:#6B7280;line-height:1.5;margin-bottom:8px">{desc}</div>
  <span class="badge bg-purple">{tag}</span>
</div>""", unsafe_allow_html=True)


def page_wizard():
    step = st.session_state.wizard_step
    st.markdown('<h2 style="font-size:1.35rem;font-weight:800;color:#111827;margin-bottom:.15rem">New Procurement Request</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B;font-size:.84rem;margin-bottom:1rem">A short brief is enough. The agents handle research, risk, scoring, and execution.</p>', unsafe_allow_html=True)

    left, center, right = st.columns([1, 5, 1])
    with center:
        wizard_bar(step)
        if step == 1:
            st.markdown(f'<div class="q-label">Step 1 of 4</div><div class="q-title">Category {help_dot("This tells the research agent which vendor market to scan.")}</div><div class="q-sub">Pick the closest buying area.</div>', unsafe_allow_html=True)
            cur = st.session_state.w_category
            cols = st.columns(3)
            for i, cat in enumerate(CATEGORIES):
                with cols[i % 3]:
                    if st.button(cat, key=f"cat_{cat}", use_container_width=True, help=f"Use {cat} vendor benchmarks"):
                        st.session_state.w_category = cat; st.rerun()
            st.markdown(f'<div style="margin-top:10px">{severity_chip("Info")} <span style="font-size:.8rem;color:#475569;font-weight:700;margin-left:6px">Selected: {esc(cur)}</span></div>', unsafe_allow_html=True)

        elif step == 2:
            st.markdown(f'<div class="q-label">Step 2 of 4</div><div class="q-title">Requirements {help_dot("Used for feature-match scoring. Mention integrations, must-haves, and constraints.")}</div><div class="q-sub">Short bullets work best.</div>', unsafe_allow_html=True)
            st.session_state.w_description = st.text_area("Requirements", value=st.session_state.w_description, placeholder="Example: Transcribe sales calls, AI summaries, HubSpot sync, searchable by speaker, SOC2 preferred", height=120, label_visibility="collapsed", help="Used by the ROI agent to score feature match.")
            n = len(st.session_state.w_description)
            chip = "Success" if n > 80 else "Info"
            st.markdown(f'<div style="display:flex;justify-content:flex-end;gap:8px;align-items:center;font-size:.74rem;color:#64748B">{severity_chip(chip)} <span>{n} characters</span></div>', unsafe_allow_html=True)

        elif step == 3:
            st.markdown(f'<div class="q-label">Step 3 of 4</div><div class="q-title">Budget and timing {help_dot("Budget affects cost-fit scoring. Team size affects adoption risk.")}</div><div class="q-sub">These become scoring inputs, not hard filters.</div>', unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            with c1:
                bs = list(BUDGET_MAP.keys())
                st.session_state.w_budget = st.selectbox("Annual Budget", bs, index=bs.index(st.session_state.w_budget) if st.session_state.w_budget in bs else 1, help="Used for the Cost Fit score.")
            with c2:
                st.session_state.w_team_size = st.number_input("Team Size", min_value=1, max_value=10000, value=st.session_state.w_team_size, help="Used to estimate rollout and adoption effort.")
            with c3:
                ts = ["ASAP","Within 1 month","Within 1 quarter"]
                st.session_state.w_timeline = st.selectbox("Timeline", ts, index=ts.index(st.session_state.w_timeline) if st.session_state.w_timeline in ts else 1, help="Used for execution planning after approval.")

        elif step == 4:
            st.markdown(f'<div class="q-label">Step 4 of 4</div><div class="q-title">Review and launch {help_dot("Launch runs vendor research, compliance checks, ROI scoring, and recommendation.")}</div><div class="q-sub">Confirm the brief before the agents start.</div>', unsafe_allow_html=True)
            rows = [("Category",st.session_state.w_category),("Requirements",st.session_state.w_description or "-"),("Budget",st.session_state.w_budget),("Team",str(st.session_state.w_team_size)),("Timeline",st.session_state.w_timeline)]
            for lbl,val in rows:
                st.markdown(f'<div style="display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #F1F5F9"><div style="font-size:.76rem;font-weight:800;color:#64748B;width:95px;flex-shrink:0">{lbl}</div><div style="font-size:.84rem;color:#111827">{esc(val)}</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="callout" style="margin-top:1rem">Agents: Research -> Risk -> ROI scoring -> Recommendation -> Workato-ready execution.</div>', unsafe_allow_html=True)

        bc1,_,bc3 = st.columns([1,3,1])
        with bc1:
            if step>1 and st.button("Back", use_container_width=True, help="Return to the previous step"):
                st.session_state.wizard_step -= 1; st.rerun()
        with bc3:
            if step < 4:
                if st.button("Continue", type="primary", use_container_width=True, help="Save this step and continue"):
                    if step==2 and not st.session_state.w_description.strip(): st.error("Please describe your requirements.")
                    else: st.session_state.wizard_step += 1; st.rerun()
            else:
                if st.button("Launch", type="primary", use_container_width=True, help="Run the procurement agents"):
                    st.session_state.request = {"category":st.session_state.w_category,"description":st.session_state.w_description,
                        "budget":st.session_state.w_budget,"team_size":int(st.session_state.w_team_size),"timeline":st.session_state.w_timeline}
                    for k in ["vendors","compliance","scores","execution_result","monitoring_result"]: st.session_state[k]=None
                    st.session_state.wizard_step = 1; go("running")

def page_running():
    req = st.session_state.request
    st.markdown(f'<h2 style="font-size:1.3rem;font-weight:800;color:#111827;margin-bottom:.25rem">Procurement Mission Running</h2><div style="font-size:.81rem;color:#6B7280;margin-bottom:1.5rem">{req["category"]} · {req["budget"]} · Team of {req["team_size"]}</div>', unsafe_allow_html=True)

    agent_block("Vendor Research Agent — Searching Exa for live vendor data...")
    log_line(f'Query: best {req["category"]} software vendors pricing comparison 2024')
    vendors = agent_vendor_research(req["category"], req["description"])
    log_line(f'Query: {req["category"]} software reviews G2 Reddit alternatives')
    log_line(f'Found {len(vendors)} vendors: {", ".join(v["name"] for v in vendors)}', color="#059669", bold=True)
    st.session_state.vendors = vendors
    agent_block(f"Vendor Research Agent — {len(vendors)} vendors identified", state="done")

    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

    agent_block("Risk & Compliance Agent — Checking certifications and incidents...")
    for v in vendors[:4]:
        log_line(f'Checking {v["name"]}: SOC2 · GDPR · ISO27001 · breach history')
    compliance = agent_risk_compliance(vendors)
    risk_colors = {"Low":"#059669","Medium":"#D97706","High":"#DC2626"}
    for name, data in compliance.items():
        rl = data["risk_level"]
        log_line(f'{name}: {rl} risk', color=risk_colors.get(rl,"#374151"))
    st.session_state.compliance = compliance
    agent_block("Risk & Compliance Agent — Analysis complete", state="done")

    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

    agent_block("ROI & Recommendation Agent — Scoring vendors...")
    log_line("Applying weights: Cost Fit 30% · Feature Match 30% · Compliance 25% · Adoption 15%")
    scores = agent_roi(vendors, compliance, req["budget"], req["description"], req["team_size"])
    for v in scores:
        prefix = "* " if v.get("recommended") else "  "
        log_line(f'{prefix}{v["name"]}  {v["score"]}/100  ·  {v["risk_level"]} risk',
                 color=sc(v["score"]) if v.get("recommended") else "#374151",
                 bold=v.get("recommended",False))
    st.session_state.scores = scores
    agent_block("ROI & Recommendation Agent — Ranking complete", state="done")

    time.sleep(0.3); go("results")


def page_results():
    req = st.session_state.request; scores = st.session_state.scores
    compliance = st.session_state.compliance; top = scores[0]
    color = sc(top["score"]); bd = top.get("breakdown",{}); bm = top.get("breakdown_max",{})

    h1,h2,h3 = st.columns([4,1,1])
    with h1:
        st.markdown(f'<h2 style="font-size:1.28rem;font-weight:800;color:#111827;margin:0">{esc(req["category"])} Vendor Analysis</h2><div style="font-size:.8rem;color:#64748B;margin-top:3px">{len(scores)} vendors evaluated | {esc(req["budget"])} | Team of {req["team_size"]}</div>', unsafe_allow_html=True)
    with h2:
        if st.button("Approve", type="primary", use_container_width=True, help="Approve the recommended vendor and trigger execution workflow"):
            go("execution")
    with h3:
        if st.button("Reject", use_container_width=True, help="Discard this analysis and start a new request"):
            for k in ["vendors","compliance","scores","execution_result","monitoring_result","request"]: st.session_state[k]=None
            st.session_state.wizard_step=1; go("wizard")

    st.markdown('<div style="margin-bottom:1rem"></div>', unsafe_allow_html=True)
    tab_rec, tab_score, tab_compare, tab_risks, tab_evidence = st.tabs(["Recommendation", "Scoring", "Compare Vendors", "Risks", "Evidence"])

    with tab_rec:
        meta = [("Score", f'{top["score"]}/100'), ("Risk", top["risk_level"]), ("Cost", top.get("annual_cost","-")), ("Setup", top.get("setup","-")), ("Uptime", top.get("uptime","-")), ("Residency", top.get("data_residency","-"))]
        chips = ''.join(f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:9px;padding:7px 11px;min-width:92px"><div style="font-size:.66rem;color:#94A3B8;font-weight:800;text-transform:uppercase">{k}</div><div style="font-size:.86rem;font-weight:800;color:#111827;margin-top:2px">{esc(v)}</div></div>' for k,v in meta)
        st.markdown(f'''
<div class="rec-vendor-card">
  <div style="display:flex;align-items:flex-start;gap:1.25rem">
    <div style="width:76px;height:76px;border-radius:18px;background:#EFF6FF;border:1px solid #BFDBFE;display:flex;align-items:center;justify-content:center;flex-direction:column;flex-shrink:0">
      <div style="font-size:1.45rem;font-weight:900;color:{color};line-height:1">{top["score"]}</div><div style="font-size:.62rem;color:#64748B;font-weight:800">SCORE</div>
    </div>
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px"><div style="font-size:1.45rem;font-weight:900;color:#111827">{esc(top["name"])}</div>{badge(top["risk_level"])}</div>
      <div style="font-size:.84rem;color:#64748B;margin-bottom:12px;max-width:760px">{esc(top.get("description",""))}</div>
      <div style="display:flex;gap:9px;flex-wrap:wrap">{chips}</div>
    </div>
  </div>
  <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #E2E8F0;font-size:.84rem;color:#334155;line-height:1.55"><strong style="color:#111827">Decision:</strong> {esc(top["rationale"])}</div>
</div>''', unsafe_allow_html=True)

    with tab_score:
        comp = compliance.get(top["name"],{}); certs = comp.get("certs",{})
        tips = {"Cost Fit":"30% weight. Compares vendor pricing tier against your stated budget.", "Feature Match":"30% weight. Measures overlap between requirements and vendor capabilities.", "Compliance":"25% weight. Rewards strong compliance signals and penalizes public risk signals.", "Adoption":"15% weight. Estimates rollout fit based on team size and vendor complexity."}
        rows = ''.join(progress_row(k, val, bm.get(k,30), sc(int(val / bm.get(k,30) * 100)), tips.get(k,"Scoring input.")) for k,val in bd.items())
        c1,c2 = st.columns([3,2])
        with c1:
            st.markdown(f'<div class="card"><div class="section-label">Weighted score bars</div>{rows}</div>', unsafe_allow_html=True)
            cert_html = ''.join(cert_chip(k, certs.get(k,"missing")) for k in ["SOC2","GDPR","ISO27001","HIPAA","PCI"])
            st.markdown(f'<div class="card"><div style="display:flex;align-items:center;gap:6px;font-weight:800;color:#111827;font-size:.88rem;margin-bottom:9px">Compliance signals {help_dot("Certification chips come from public compliance and security source checks.")}</div><div style="display:flex;flex-wrap:wrap;gap:8px">{cert_html}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-label">Score shape</div>', unsafe_allow_html=True)
            st.plotly_chart(radar(bd, bm, top["name"]), use_container_width=True, config={"displayModeBar":False})

    with tab_compare:
        hdr = '<tr><th>Vendor</th><th>Score</th><th>Risk</th><th>Cost</th><th>Setup</th><th>Uptime</th><th>Data</th></tr>'
        body = ''
        for v in scores[:4]:
            pick = ' <span class="chip bg-blue">Pick</span>' if v.get("recommended") else ''
            body += f'<tr><td><strong>{esc(v["name"])}</strong>{pick}<div style="font-size:.72rem;color:#64748B;margin-top:2px">{esc(v.get("description","")[:70])}</div></td><td><strong style="color:{sc(v["score"])}">{v["score"]}</strong></td><td>{badge(v["risk_level"])}</td><td>{esc(v.get("annual_cost","-"))}</td><td>{esc(v.get("setup","-"))}</td><td>{esc(v.get("uptime","-"))}</td><td>{esc(v.get("data_residency","-"))}</td></tr>'
        st.markdown(f'<div class="table-wrap"><table class="data-table"><thead>{hdr}</thead><tbody>{body}</tbody></table></div>', unsafe_allow_html=True)

    with tab_risks:
        owners = {"Security":[], "Legal":[], "Procurement":[]}
        for v in scores[:4]:
            comp2 = compliance.get(v["name"],{}); risk = comp2.get("risk_level","Medium"); neg = comp2.get("negative_signals",[])
            if neg:
                for n in neg:
                    owner = "Legal" if any(kw in n.lower() for kw in ["gdpr","privacy","fine","lawsuit","violated","penalty"]) else "Security"
                    owners[owner].append((v["name"], n.title(), risk))
            else:
                owners["Procurement"].append((v["name"], "No major public risk signal found. Confirm pricing, SLA, and renewal terms.", risk))
        if not owners["Legal"]:
            owners["Legal"] = [
                (top["name"], "Review DPA, privacy policy, subprocessors, and data retention terms before signature.", "Medium"),
                (top["name"], f"Confirm data residency matches requirement: {top.get('data_residency','TBD')}.", "Medium"),
                (top["name"], "Check renewal, termination, liability cap, and security notification clauses.", "Low"),
            ]
        cols = st.columns(3)
        owner_help = {
            "Security":"Security validates controls, certifications, breach history, SSO, and incident response.",
            "Legal":"Legal reviews contract terms, privacy, DPA, subprocessors, data residency, and liability clauses.",
            "Procurement":"Procurement owns commercial fit, pricing, renewal terms, rollout owner, and vendor follow-up.",
        }
        for col, owner in zip(cols, ["Security", "Legal", "Procurement"]):
            with col:
                items = owners[owner] or [(top["name"], "No open item for this owner.", "Low")]
                rows = ''.join(f'<div style="border-top:1px solid #F1F5F9;padding:.65rem 0"><div style="display:flex;justify-content:space-between;gap:8px;align-items:center"><strong style="font-size:.82rem;color:#111827">{esc(vendor)}</strong>{severity_chip(risk)}</div><div style="font-size:.78rem;color:#475569;margin-top:5px;line-height:1.45">{esc(msg)}</div></div>' for vendor,msg,risk in items[:4])
                st.markdown(f'<div class="risk-card"><div style="display:flex;align-items:center;gap:6px;font-size:.92rem;font-weight:900;color:#111827;margin-bottom:4px">{owner} {help_dot(owner_help[owner])}</div><div style="font-size:.72rem;color:#64748B;margin-bottom:4px">Owner queue</div>{rows}</div>', unsafe_allow_html=True)

    with tab_evidence:
        st.markdown(f'<div class="section-label">Source-backed checks {help_dot("Each vendor is grouped once. Open the source rows for the evidence behind each claim.")}</div>', unsafe_allow_html=True)
        for v in scores[:4]:
            comp3 = compliance.get(v["name"],{}); sources = comp3.get("sources",[])
            claim = comp3.get("summary", "Compliance and market signals checked.")
            confidence = "High" if len(sources) >= 3 else ("Medium" if sources else "Low")
            conf_class = {"High":"bg-green","Medium":"bg-amber","Low":"bg-gray"}.get(confidence,"bg-gray")
            source_count = len(sources)
            risk = v.get("risk_level", "Medium")
            header_meta = f'<span class="chip {conf_class}">{confidence}</span><span class="chip bg-blue">{source_count} sources</span>{badge(risk)}'
            source_rows = ""
            if sources:
                for idx, url in enumerate(sources[:4], start=1):
                    title = source_title(url)
                    stype = source_type(url)
                    host = urlparse(url).netloc.replace("www.","") if url else "Source"
                    source_rows += f'<div style="display:grid;grid-template-columns:34px 1fr auto;gap:10px;align-items:center;padding:.7rem 0;border-top:1px solid #F1F5F9"><div style="width:26px;height:26px;border-radius:8px;background:#EFF6FF;color:#1D4ED8;display:flex;align-items:center;justify-content:center;font-size:.74rem;font-weight:900">{idx}</div><div><div style="display:flex;gap:6px;align-items:center;margin-bottom:3px"><span class="chip bg-blue">{stype}</span><span style="font-size:.72rem;color:#94A3B8">{esc(host)}</span></div><div style="font-size:.84rem;font-weight:850;color:#111827;line-height:1.35">{esc(title)}</div></div><a href="{esc(url)}" target="_blank" style="font-size:.76rem;font-weight:850;color:#1D4ED8;text-decoration:none;white-space:nowrap">Open</a></div>'
            else:
                source_rows = '<div style="padding:.75rem 0;border-top:1px solid #F1F5F9;font-size:.8rem;color:#94A3B8">No external sources retrieved for this scan.</div>'

            st.markdown(f'''
<div class="source-card" style="height:auto;margin-bottom:.85rem;padding:1rem 1.1rem">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:.75rem">
    <div>
      <div style="font-size:1rem;font-weight:900;color:#111827">{esc(v["name"])}</div>
      <div style="font-size:.74rem;color:#64748B;margin-top:3px">Evidence summary</div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end">{header_meta}</div>
  </div>
  <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:9px;padding:.75rem .85rem;margin-bottom:.55rem">
    <div style="font-size:.68rem;color:#64748B;font-weight:900;text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px">Claim checked</div>
    <div style="font-size:.82rem;color:#334155;line-height:1.45">{esc(claim)}</div>
  </div>
  {source_rows}
</div>''', unsafe_allow_html=True)

def page_execution():
    req = st.session_state.request; scores = st.session_state.scores; top = scores[0]
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem"><div><h2 style="font-size:1.3rem;font-weight:800;color:#111827;margin:0">Procurement Approved</h2><div style="font-size:.81rem;color:#6B7280;margin-top:3px">{top["name"]} · {req["category"]} · {req["budget"]}</div></div><span class="badge bg-green" style="margin-left:auto">● Approved</span></div>', unsafe_allow_html=True)

    if st.session_state.execution_result is None:
        agent_block("Execution Agent — Triggering Workato...")
        log_line("Building procurement payload")
        result = agent_execution(top, req); st.session_state.execution_result = result
        if result["success"]:
            log_line("Workato webhook triggered successfully", color="#059669", bold=True)
        else:
            log_line(f"Webhook response: {result['msg']}", color="#D97706")
        agent_block("Execution Agent — All workflows triggered", state="done")

    result = st.session_state.execution_result
    st.markdown(f'<div class="callout callout-green" style="margin-top:1rem">Approved: <strong>{top["name"]}</strong> for {req["category"]} · Score {top["score"]}/100 · {top["risk_level"]} Risk · {req["budget"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top:1.5rem">Automated workflow status</div>', unsafe_allow_html=True)
    wf = [("Approval payload sent to Workato","Procurement data delivered"),
          ("Jira ticket created","Implementation tracker opened"),
          ("Slack #procurement notified","Team alerted with vendor summary"),
          ("Notion vendor database updated","Vendor record added"),
          ("Calendar kickoff scheduled","30-min review booked"),
          ("Approval email drafted","Stakeholders notified")]
    for title, desc in wf:
        st.markdown(f'<div style="display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1px solid #F9FAFB"><div style="width:18px;height:18px;border-radius:50%;background:#ECFDF5;border:1.5px solid #A7F3D0;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px;font-size:9px;font-weight:800;color:#059669">&#10003;</div><div><div style="font-size:.855rem;font-weight:600;color:#111827">{title}</div><div style="font-size:.775rem;color:#6B7280;margin-top:2px">{desc}</div></div></div>', unsafe_allow_html=True)

    show_payload = st.toggle("View Workato payload", value=False)
    if show_payload and result:
        st.json(result["payload"])

    # ── Zo AI Advisor ─────────────────────────────────────────────────────────
    st.markdown('<div style="margin-top:2rem"></div>', unsafe_allow_html=True)

    zo_prompt = f"We just approved {top['name']} for {req['category']} for a {req['team_size']}-person team with a {req['budget']} budget. Risk level is {top['risk_level']}. Please advise on: 1) Key onboarding steps, 2) Common pitfalls with {req['category']} tools, 3) How to measure ROI at 90 days, 4) Risks to mitigate given {top['risk_level']} compliance risk."

    st.markdown(f"""
<div style="background:#fff;border:1px solid #E5E7EB;border-radius:12px;padding:1.2rem 1.4rem;box-shadow:0 1px 3px rgba(0,0,0,.04)">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
    <div>
      <div style="font-size:.68rem;font-weight:800;color:#94A3B8;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px">Zo AI Advisor</div>
      <div style="font-weight:700;font-size:.9rem;color:#111827">Live onboarding guidance for {top['name']}</div>
      <div style="font-size:.77rem;color:#6B7280;margin-top:2px">Zo is consulting on your procurement decision in real time</div>
    </div>
    <a href="https://sakshizz.zo.computer/?chat=con_T1GmqBg1SI6MGkNj" target="_blank" style="background:#111827;color:#fff;border-radius:8px;padding:6px 14px;font-size:.78rem;font-weight:600;text-decoration:none;white-space:nowrap;flex-shrink:0;margin-left:1rem">Open Zo</a>
  </div>
</div>""", unsafe_allow_html=True)

    if "zo_response" not in st.session_state or st.session_state.get("zo_vendor") != top["name"]:
        with st.spinner("Zo is thinking..."):
            zo_resp = ask_zo(zo_prompt, vendor=top["name"], category=req["category"], team_size=req["team_size"], risk=top["risk_level"])
            st.session_state.zo_response = zo_resp
            st.session_state.zo_vendor = top["name"]
    else:
        zo_resp = st.session_state.zo_response

    st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E5E7EB;border-radius:10px;padding:1.1rem 1.2rem;font-size:.84rem;color:#1E293B;line-height:1.75;white-space:pre-wrap">{zo_resp}</div>""", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:1.5rem"></div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        if st.button("Launch Monitoring Agent", type="primary", use_container_width=True):
            st.session_state.monitoring_result = None; go("monitoring")
    with c2:
        if st.button("New Mission", use_container_width=True):
            for k in ["vendors","compliance","scores","execution_result","monitoring_result","request"]: st.session_state[k]=None
            st.session_state.wizard_step=1; go("wizard")


def page_monitoring():
    scores = st.session_state.scores; req = st.session_state.get("request") or {}
    if not scores:
        st.markdown('<h2 style="font-size:1.3rem;font-weight:800;color:#111827;margin-bottom:.5rem">Monitoring Dashboard</h2>', unsafe_allow_html=True)
        st.info("No active missions yet. Complete a procurement to start monitoring.")
        if st.button("Start a Mission", type="primary", help="Create a procurement mission first"):
            go("wizard")
        return

    top = scores[0]
    if "monitor_vendor" not in st.session_state:
        st.session_state.monitor_vendor = top["name"]

    if st.session_state.monitoring_result is None:
        with st.spinner(f"Scanning {top['name']} for health, news, outages, and competitor signals..."):
            mon = agent_monitoring(top["name"], req.get("category",""))
            if mon["competitor_found"]:
                ok,_ = trigger_workato({"event":"competitor_alert","timestamp":mon["timestamp"],"current_vendor":top["name"],"category":req.get("category",""),"alert":f"Better alternative to {top['name']} detected.","market_signal":mon["competitor_snippets"][0][:300] if mon["competitor_snippets"] else "","budget":req.get("budget",""),"team_size":req.get("team_size",""),"next_review":"30 days"})
                mon["workato_fired"] = ok
            st.session_state.monitoring_result = mon
            append_log({"timestamp":mon["timestamp"],"vendor":top["name"],"category":req.get("category",""),"health":mon["health"],"alerts":[a["msg"] for a in mon["alerts"]],"competitor_found":mon["competitor_found"],"workato_fired":mon.get("workato_fired",False)})
        st.rerun()

    mon = st.session_state.monitoring_result
    hcolor = "#059669" if mon["health"] in ["Healthy","Stable"] else "#D97706"
    open_alerts = len([a for a in mon["alerts"] if a["type"]=="amber"])
    st.markdown(f'<h2 style="font-size:1.28rem;font-weight:800;color:#111827;margin-bottom:.2rem">Monitoring Dashboard</h2><div style="font-size:.8rem;color:#64748B;margin-bottom:1rem">Current vendor: <strong>{esc(top["name"])}</strong> | {esc(req.get("category",""))} | 30-day review cycle</div>', unsafe_allow_html=True)

    st.markdown(f'''
<div class="card" style="padding:1rem 1.1rem;margin-bottom:1rem">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:14px">
    <div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px"><span style="width:10px;height:10px;border-radius:50%;background:{hcolor};display:inline-block"></span><div style="font-size:1rem;font-weight:900;color:#111827">{esc(top["name"])} is {esc(mon["health"])}</div>{help_dot("Health is based on recent news, outage, complaint, and competitor signals.")}</div>
      <div style="font-size:.82rem;color:#64748B;line-height:1.5">{esc(mon["health_note"])}</div>
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end">
      <span class="chip bg-blue">Score {top["score"]}/100</span>
      {badge(top["risk_level"])}
      <span class="chip {'bg-amber' if open_alerts else 'bg-green'}">{open_alerts} open alerts</span>
    </div>
  </div>
</div>''', unsafe_allow_html=True)

    kdata = [(str(top["score"]), "Approval score", "baseline", sc(top["score"])), (top["risk_level"], "Risk", "contract/compliance", {"Low":"#059669","Medium":"#D97706","High":"#DC2626"}.get(top["risk_level"],"#64748B")), (mon["health"], "Health", "latest scan", hcolor), (str(open_alerts), "Open alerts", "needs review", "#D97706" if open_alerts else "#059669")]
    cols = st.columns(4)
    for col, (val, lbl, sub, c) in zip(cols, kdata):
        with col:
            fs = "1.35rem" if len(val)>5 else "1.5rem"
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:{c};font-size:{fs}">{esc(val)}</div><div class="metric-lbl">{lbl}</div><div style="font-size:.68rem;color:#94A3B8;margin-top:3px">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
    tab_overview, tab_alerts, tab_market, tab_log = st.tabs(["Overview", "Alerts", "Market Intel", "Log History"])

    with tab_overview:
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown('<div class="section-label">Lifecycle</div>', unsafe_allow_html=True)
            stages = [("Done","Approved","Day 0","#059669","#ECFDF5"),("Now","Contract","Day 3","#2563EB","#EFF6FF"),("Next","Onboarding","Day 14","#64748B","#F8FAFC"),("Next","Live","Day 30","#64748B","#F8FAFC"),("Later","ROI Review","Day 90","#64748B","#F8FAFC")]
            for icon,lbl,day,c,bg in stages:
                st.markdown(f'<div style="display:grid;grid-template-columns:58px 1fr auto;gap:10px;align-items:center;background:{bg};border:1px solid {c}33;border-radius:9px;padding:.65rem .75rem;margin-bottom:.45rem"><span style="font-size:.68rem;color:{c};font-weight:900;text-transform:uppercase">{icon}</span><strong style="font-size:.82rem;color:#111827">{lbl}</strong><span style="font-size:.72rem;color:#94A3B8">{day}</span></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="section-label">What users should do</div>', unsafe_allow_html=True)
            next_items = ["Review open alerts before renewal or rollout.", "Check Legal/Security owner queues from the Risks tab.", "Use Log History to compare scans over time."]
            rows = ''.join(f'<div style="display:flex;gap:8px;padding:.55rem 0;border-top:1px solid #F1F5F9"><span class="chip bg-blue">{i}</span><span style="font-size:.8rem;color:#475569;line-height:1.4">{esc(item)}</span></div>' for i,item in enumerate(next_items, start=1))
            st.markdown(f'<div class="card-sm"><strong style="font-size:.86rem;color:#111827">Monitoring guide</strong>{rows}</div>', unsafe_allow_html=True)

    with tab_alerts:
        st.markdown(f'<div class="section-label">Alert queue {help_dot("Amber items need review. Green items are positive or all-clear signals.")}</div>', unsafe_allow_html=True)
        for a in mon["alerts"]:
            if a["type"]=="amber": st.warning(a["msg"])
            else: st.success(a["msg"])
        if mon.get("workato_fired"):
            st.markdown('<div class="callout callout-green">Workato competitor alert sent. Procurement has been notified.</div>', unsafe_allow_html=True)
        if mon["competitor_found"]:
            st.markdown('<div class="callout callout-amber">Better alternatives detected. Re-evaluation recommended.</div>', unsafe_allow_html=True)
            if st.button("Re-evaluate Vendors", type="primary", help="Run the original mission again with fresh market data"):
                for k in ["vendors","compliance","scores","execution_result","monitoring_result"]: st.session_state[k]=None
                go("running")

    with tab_market:
        st.markdown('<div class="section-label">Real-time intelligence via Exa</div>', unsafe_allow_html=True)
        groups = [("Recent news", mon["news_snippets"], "bg-blue"), ("Incident signals", mon["risk_snippets"], "bg-amber"), ("Competitor landscape", mon["competitor_snippets"], "bg-purple")]
        for title, snippets, chip in groups:
            if snippets:
                st.markdown(f'<div style="font-size:.8rem;font-weight:900;color:#111827;margin:.7rem 0 .45rem">{title}</div>', unsafe_allow_html=True)
                for s in snippets:
                    st.markdown(f'<div class="card-sm" style="font-size:.79rem;color:#475569;line-height:1.55;margin-bottom:.5rem"><span class="chip {chip}" style="margin-bottom:6px">Signal</span><br>{esc(s)}</div>', unsafe_allow_html=True)
        if not any([mon["news_snippets"],mon["risk_snippets"],mon["competitor_snippets"]]):
            st.info("No live signals found. Market appears stable.")

    with tab_log:
        log = load_log(); total = len(log)
        st.markdown(f'<div class="section-label">Monitoring log {help_dot("Filter first, then select a vendor to inspect detailed events. Designed for large log histories.")}</div>', unsafe_allow_html=True)

        entries = []
        for entry in log:
            health = entry.get("health","Stable")
            alerts = entry.get("alerts",[]) or []
            sev = "Warning" if health == "Watch" else ("Success" if health in ["Healthy","Stable"] else "Info")
            if entry.get("competitor_found") and health == "Watch": sev = "Critical"
            source = "Workato" if entry.get("workato_fired") else "Exa"
            msg = alerts[0] if alerts else f"Health scan: {health}"
            action = "Review" if sev in ["Warning","Critical"] else "Monitor"
            entries.append({"time":entry.get("timestamp",""),"source":source,"vendor":entry.get("vendor","-"),"severity":sev,"message":msg,"action":action,"category":entry.get("category",""),"health":health,"alert_count":len(alerts),"alerts":alerts,"workato":entry.get("workato_fired",False),"competitor":entry.get("competitor_found",False)})

        if not entries:
            st.markdown('<div style="text-align:center;padding:2.6rem;background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:10px;color:#64748B;font-size:.84rem">No monitoring scans yet.</div>', unsafe_allow_html=True)
        else:
            now = datetime.utcnow()
            time_windows = {"Last 15m": timedelta(minutes=15), "1h": timedelta(hours=1), "24h": timedelta(hours=24), "All": None}
            fc1, fc2, fc3, fc4 = st.columns([1.15, 1.15, 1.25, 2.2])
            with fc1:
                time_range = st.selectbox("Time Range", list(time_windows.keys()), index=3, help="Limit logs to a recent time window.")
            with fc2:
                severity_filter = st.multiselect("Severity", ["Critical","Warning","Info","Success"], default=["Critical","Warning","Info","Success"], help="Color-coded log levels.")
            with fc3:
                components = sorted(set(e["category"] or e["source"] for e in entries))
                component_filter = st.selectbox("Component / Service", ["All"] + components, help="Filter by vendor category or signal source.")
            with fc4:
                search = st.text_input("Search", placeholder="Search vendor, source, severity, message, action...", label_visibility="collapsed", help="Searches all visible log metadata and messages.")

            query = search.lower().strip()
            cutoff = now - time_windows[time_range] if time_windows[time_range] else None
            filtered = []
            for e in entries:
                if e["severity"] not in severity_filter: continue
                if component_filter != "All" and e["category"] != component_filter and e["source"] != component_filter: continue
                if cutoff:
                    try:
                        ts = datetime.fromisoformat(e["time"].replace("Z", ""))
                        if ts < cutoff: continue
                    except Exception:
                        pass
                haystack = " ".join(str(x).lower() for x in e.values())
                if query and query not in haystack: continue
                filtered.append(e)

            counts = {level: len([e for e in filtered if e["severity"] == level]) for level in ["Critical","Warning","Info","Success"]}
            st.markdown(f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin:.25rem 0 .9rem"><span class="chip bg-red">Critical {counts["Critical"]}</span><span class="chip bg-amber">Warning {counts["Warning"]}</span><span class="chip bg-blue">Info {counts["Info"]}</span><span class="chip bg-green">Success {counts["Success"]}</span><span class="chip bg-gray">Showing {len(filtered)} of {total}</span></div>', unsafe_allow_html=True)

            vendor_names = sorted(set(e["vendor"] for e in filtered))
            if st.session_state.monitor_vendor not in vendor_names and vendor_names:
                st.session_state.monitor_vendor = vendor_names[0]

            summary = {}
            sev_rank = {"Success":0,"Info":1,"Warning":2,"Critical":3}
            for e in filtered:
                vendor = e["vendor"]
                cur = summary.setdefault(vendor, {"count":0,"alerts":0,"latest":"","severity":"Success","category":e["category"]})
                cur["count"] += 1
                cur["alerts"] += e["alert_count"]
                if sev_rank[e["severity"]] > sev_rank[cur["severity"]]: cur["severity"] = e["severity"]
                if e["time"] > cur["latest"]:
                    cur["latest"] = e["time"]; cur["category"] = e["category"]

            left, right = st.columns([1.05, 2.45])
            with left:
                st.markdown(f'<div class="card-sm"><div style="font-size:.86rem;font-weight:900;color:#111827;margin-bottom:.3rem">Vendors</div><div style="font-size:.74rem;color:#64748B;margin-bottom:.65rem">Select a vendor to inspect</div>', unsafe_allow_html=True)
                if not vendor_names:
                    st.markdown('<div style="font-size:.8rem;color:#94A3B8;padding:.7rem 0">No vendors match filters.</div>', unsafe_allow_html=True)
                for vendor in vendor_names:
                    data = summary[vendor]
                    selected = vendor == st.session_state.monitor_vendor
                    label = f'{vendor} ({data["count"]})'
                    if st.button(label, key=f"monitor_vendor_{vendor}", use_container_width=True, type="primary" if selected else "secondary", help=f"View logs for {vendor}"):
                        st.session_state.monitor_vendor = vendor; st.rerun()
                    latest = data["latest"][:10] if data["latest"] else "-"
                    st.markdown(f'<div style="display:flex;justify-content:space-between;gap:6px;margin:-.25rem 0 .5rem;padding:0 .15rem .45rem;border-bottom:1px solid #F1F5F9"><span style="font-size:.7rem;color:#94A3B8">{esc(data["category"])} | {esc(latest)}</span>{severity_chip(data["severity"])}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with right:
                selected_vendor = st.session_state.monitor_vendor
                vendor_entries = [e for e in reversed(filtered) if e["vendor"] == selected_vendor]
                st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.65rem"><div><div style="font-size:.96rem;font-weight:900;color:#111827">{esc(selected_vendor)}</div><div style="font-size:.74rem;color:#64748B">{len(vendor_entries)} events | newest first</div></div><span class="chip bg-blue">Expandable rows</span></div>', unsafe_allow_html=True)
                if not vendor_entries:
                    st.markdown('<div style="text-align:center;padding:2rem;background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:10px;color:#64748B;font-size:.84rem">No events for this vendor under current filters.</div>', unsafe_allow_html=True)
                else:
                    rows = ''
                    for i, e in enumerate(vendor_entries[:40], start=1):
                        ts = (e["time"][:19].replace("T"," ") + "Z") if e["time"] else "-"
                        payload = json.dumps({"vendor":e["vendor"],"category":e["category"],"health":e["health"],"alerts":e["alerts"],"competitor_found":e["competitor"],"workato_fired":e["workato"]}, indent=2)
                        details = f'<details><summary style="cursor:pointer;color:#1D4ED8;font-weight:850">Details</summary><pre style="white-space:pre-wrap;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:.7rem;margin:.55rem 0 0;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.72rem;color:#334155;line-height:1.45">{esc(payload)}</pre></details>'
                        rows += f'<tr><td style="white-space:nowrap;font-family:Inter,sans-serif;font-size:.73rem;color:#64748B">{esc(ts)}</td><td>{severity_chip(e["severity"])}</td><td>{severity_chip(e["source"])}</td><td style="font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.76rem;color:#334155;line-height:1.45">{esc(e["message"][:150])}</td><td><span class="chip bg-gray">{esc(e["action"])}</span></td><td>{details}</td></tr>'
                    st.markdown(f'<div class="table-wrap"><table class="data-table"><thead><tr><th>Time</th><th>Severity</th><th>Service</th><th>Message</th><th>Action</th><th>Payload</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)
                    st.download_button("Download log as JSON", data=json.dumps(log, indent=2), file_name="monitoring_log.json", mime="application/json", help="Export the full raw monitoring log.")

    st.markdown('<div style="margin-top:1.2rem"></div>', unsafe_allow_html=True)
    if st.button("New Procurement Mission", use_container_width=True, help="Clear the active mission and start again"):
        for k in ["vendors","compliance","scores","execution_result","monitoring_result","request"]: st.session_state[k]=None
        st.session_state.wizard_step=1; go("wizard")

def page_placeholder(title, desc):
    st.markdown(f'<h2 style="font-size:1.3rem;font-weight:800;color:#111827;margin-bottom:.3rem">{title}</h2><p style="color:#6B7280;font-size:.875rem">{desc}</p>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top:3rem;text-align:center;padding:3rem;background:#fff;border:1px dashed #E5E7EB;border-radius:14px"><div style="font-weight:600;color:#374151;margin-bottom:6px">Coming soon</div><div style="font-size:.82rem;color:#9CA3AF">Part of the full ProcurementOS roadmap.</div></div>', unsafe_allow_html=True)

# ── Router ─────────────────────────────────────────────────────────────────────
p = st.session_state.page
if   p=="home":       page_home()
elif p=="wizard":     page_wizard()
elif p=="running":    page_running()
elif p=="results":    page_results()
elif p=="execution":  page_execution()
elif p=="monitoring": page_monitoring()
elif p=="reports":    page_placeholder("Reports","Procurement analytics and spend history.")
elif p=="settings":   page_placeholder("Settings","Configure agents, integrations, and team preferences.")
else:                 page_home()
