"""
main.py — AdPilot AI Dashboard (Streamlit).

Run with:
    streamlit run main.py
"""

import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data import (
    get_campaigns,
    get_platform_budgets,
    get_data_sources,
    get_forecast_actions,
    get_trend_data,
    generate_sparkline,
    PLATFORM_COLORS,
)
from engine import (
    analyze_campaigns,
    get_winner,
    score_campaign,
    compute_forecast_impact,
    IMPACT_COLORS,
    IMPACT_ICONS,
)

# ══════════════════════════════════════════════
#  Page Config & Theme
# ══════════════════════════════════════════════

st.set_page_config(
    page_title="AdPilot AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (dark-theme matching the HTML prototype) ──

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg: #080b12; --surface: #0e1219; --surface2: #141923; --surface3: #1a2130;
    --border: #1f2a3a; --border2: #263245;
    --accent: #7c6fea; --accent-light: #9d93f0; --accent-dark: #5b50c8;
    --accent-glow: rgba(124,111,234,.18);
    --teal: #26d9b0; --teal-dim: rgba(38,217,176,.12);
    --orange: #f59e0b; --orange-dim: rgba(245,158,11,.12);
    --red: #f43f5e; --red-dim: rgba(244,63,94,.12);
    --gold: #fbbf24; --gold-dim: rgba(251,191,36,.12);
    --text: #f1f4f9; --text2: #c8d0df; --muted: #6b7a95;
    --green: #26d9b0;
}

/* -- global overrides -- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text2) !important; }
[data-testid="stHeader"] { background: transparent !important; }
h1, h2, h3, h4, h5, h6, .stMarkdown p, span, label, div { color: var(--text) !important; }

/* -- KPI card -- */
.kpi-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; position: relative;
    overflow: hidden; transition: all .25s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,.35); }
.kpi-label { font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .7px; }
.kpi-value { font-size: 30px; font-weight: 800; line-height: 1; letter-spacing: -1px; margin: 10px 0 8px; }
.kpi-change { font-size: 11px; font-weight: 700; padding: 3px 7px; border-radius: 20px; display: inline-block; }
.kpi-change.up { color: var(--teal); background: var(--teal-dim); }
.kpi-change.down { color: var(--red); background: var(--red-dim); }
.kpi-period { font-size: 11px; color: var(--muted); margin-left: 6px; }

/* -- stat card -- */
.stat-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; transition: all .2s;
}
.stat-card:hover { border-color: var(--border2); box-shadow: 0 4px 24px rgba(0,0,0,.35); }

/* -- data source card -- */
.ds-item {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 11px; padding: 14px; transition: all .2s;
}
.ds-item:hover { border-color: var(--border2); background: var(--surface3); }

/* -- recommendation card -- */
.rec-card {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 13px; padding: 18px; transition: all .2s;
}
.rec-card:hover { border-color: var(--border2); background: var(--surface3);
    transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,.35); }

/* -- winner card -- */
.winner-card {
    background: linear-gradient(145deg, rgba(251,191,36,.06), rgba(124,111,234,.05));
    border: 1px solid rgba(251,191,36,.2); border-radius: 13px; padding: 22px;
}

/* -- forecast row -- */
.forecast-row {
    display: grid; grid-template-columns: 1fr 140px 100px;
    padding: 12px 16px; border-bottom: 1px solid var(--border); align-items: center;
}
.forecast-row:last-child { border-bottom: none; }

/* -- general helpers -- */
.badge { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px;
    padding: 3px 9px; border-radius: 20px; display: inline-block; }
.badge-high { background: var(--red-dim); color: var(--red); }
.badge-medium { background: var(--orange-dim); color: var(--orange); }
.badge-opportunity { background: var(--teal-dim); color: var(--teal); }
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--teal);
    display: inline-block; animation: pulse 1.5s infinite; margin-right: 4px; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.8)} }

/* -- progress bar -- */
.prog-track { height: 5px; background: var(--surface3); border-radius: 99px; overflow: hidden; margin-top: 4px; }
.prog-fill { height: 100%; border-radius: 99px; }

/* -- budget legend row -- */
.plat-leg-row {
    display: flex; align-items: center; gap: 14px;
    padding: 11px 14px; border-radius: 12px;
    border: 1px solid var(--border); background: var(--surface2);
    margin-bottom: 8px; transition: .2s;
}
.plat-leg-row:hover { border-color: var(--border2); }

/* -- Streamlit widget overrides -- */
[data-testid="stMetricValue"] { color: var(--text) !important; }
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 14px !important; }
button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-dark), var(--accent)) !important;
    border: none !important; color: #ffffff !important; font-weight: 700 !important;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--accent), var(--accent-light)) !important;
    color: #ffffff !important;
}
button[kind="secondary"], button[kind="tertiary"],
div[data-testid="stDownloadButton"] button,
button:not([kind]) {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    color: #ffffff !important; font-weight: 600 !important;
}
button[kind="secondary"]:hover, button[kind="tertiary"]:hover,
div[data-testid="stDownloadButton"] button:hover,
button:not([kind]):hover {
    background: var(--surface3) !important;
    border-color: var(--accent) !important; color: #ffffff !important;
}
/* Ensure all button text is white regardless of Streamlit state */
button p, button span, button div,
[data-testid="stBaseButton-secondary"] p,
[data-testid="stBaseButton-primary"] p,
[data-testid="baseButton-secondary"] p,
[data-testid="baseButton-primary"] p {
    color: #ffffff !important;
}
div[data-testid="stForm"] {
    background: var(--surface) !important; border: 1px solid var(--border2) !important;
    border-radius: 14px !important; padding: 20px !important;
}

/* ─── Responsive: ≤ 768px ─── */
@media (max-width: 768px) {

    /* ── Sidebar: fixed overlay, off-screen by default ── */
    [data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        height: 100vh !important;
        z-index: 9999 !important;
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 4px 0 30px rgba(0,0,0,.6) !important;
        transition: transform 0.3s cubic-bezier(.4,0,.2,1) !important;
    }

    /* When sidebar is expanded → slide in + show backdrop */
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
    }
    [data-testid="stSidebar"][aria-expanded="true"] ~ .stMain::before {
        content: "" !important;
        position: fixed !important;
        inset: 0 !important;
        background: rgba(0,0,0,.55) !important;
        z-index: 9998 !important;
        pointer-events: auto !important;
    }

    /* When sidebar is collapsed → slide off-screen */
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"]:not([aria-expanded="true"]) {
        transform: translateX(-100%) !important;
    }

    /* ── Collapse toggle arrow: always visible, styled ── */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 10000 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        background: var(--surface2) !important;
        border: 1px solid var(--border2) !important;
        border-radius: 8px !important;
        color: var(--accent-light) !important;
        padding: 8px !important;
        cursor: pointer !important;
        box-shadow: 0 2px 12px rgba(0,0,0,.4) !important;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover {
        background: var(--accent-glow) !important;
        border-color: var(--accent) !important;
    }

    /* ── Main content: full width, ignore sidebar offset ── */
    .stMain,
    [data-testid="stAppViewContainer"] > .stMain {
        margin-left: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* ── Columns: stack vertically ── */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* KPI cards: 2-per-row (override the full-width stacking) */
    [data-testid="stHorizontalBlock"]:has(.kpi-card) {
        flex-wrap: wrap !important;
    }
    [data-testid="stHorizontalBlock"]:has(.kpi-card) > [data-testid="stColumn"] {
        width: 48% !important;
        min-width: 48% !important;
        flex: 1 1 48% !important;
    }

    /* ── Component sizing ── */
    .kpi-card {
        padding: 14px !important;
    }
    .kpi-value {
        font-size: 22px !important;
        letter-spacing: -0.5px !important;
    }
    .kpi-label {
        font-size: 10px !important;
    }
    .kpi-change, .kpi-period {
        font-size: 10px !important;
    }
    .stat-card {
        padding: 16px !important;
        margin-bottom: 8px !important;
    }
    .winner-card {
        padding: 16px !important;
    }
    .rec-card {
        padding: 14px !important;
    }
    .ds-item {
        padding: 10px !important;
        margin-bottom: 6px !important;
    }
    .forecast-row {
        grid-template-columns: 1fr !important;
        gap: 6px !important;
        padding: 10px !important;
    }
    .stDataFrame {
        overflow-x: auto !important;
    }
    [data-testid="stHorizontalBlock"] button {
        font-size: 12px !important;
        padding: 6px 10px !important;
    }
    h1 { font-size: 22px !important; }
    h4 { font-size: 14px !important; }
    .plat-leg-row {
        padding: 8px 10px !important;
        gap: 8px !important;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  Session State Init
# ══════════════════════════════════════════════

if "campaigns" not in st.session_state:
    st.session_state.campaigns = get_campaigns()
if "budget_spends" not in st.session_state:
    budgets = get_platform_budgets()
    st.session_state.budget_spends = {b["name"]: b["spend"] for b in budgets}
if "ai_results" not in st.session_state:
    st.session_state.ai_results = None
if "applied_recs" not in st.session_state:
    st.session_state.applied_recs = set()
if "next_id" not in st.session_state:
    st.session_state.next_id = 9

campaigns_df: pd.DataFrame = st.session_state.campaigns

# ══════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════

PLOTLY_LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#c8d0df", size=12),
    margin=dict(l=0, r=0, t=0, b=0),
    hovermode="x unified",
)


def _hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    """Convert '#7c6fea' to 'rgba(124,111,234,0.12)'."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _sparkline_fig(data: list[float], color: str) -> go.Figure:
    """Tiny area chart for KPI cards."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data, mode="lines", fill="tozeroy",
        line=dict(color=color, width=2),
        fillcolor=_hex_to_rgba(color, 0.12),
        hoverinfo="skip",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        height=50, xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def _fmt_spend(val: float) -> str:
    """$18400 → '$18.4K'."""
    return f"${val / 1000:.1f}K"


# ══════════════════════════════════════════════
#  Sidebar
# ══════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        "<div style='display:flex;align-items:center;gap:11px;padding:6px 0 16px'>"
        "<div style='width:34px;height:34px;background:linear-gradient(135deg,#7c6fea,#26d9b0);"
        "border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;"
        "box-shadow:0 4px 16px rgba(124,111,234,.25)'>✦</div>"
        "<div><div style='font-size:15px;font-weight:800;letter-spacing:-.3px'>Ad<span style=\"color:#9d93f0\">Pilot</span> AI</div>"
        "<div style='font-size:9px;font-weight:600;color:#6b7a95;text-transform:uppercase;letter-spacing:.8px'>Analytics Platform</div></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("##### Main")
    page = st.radio(
        "Navigation", ["Dashboard", "Campaigns", "Audiences", "A/B Testing"],
        label_visibility="collapsed",
    )
    st.markdown("##### Intelligence")
    st.radio(
        "Intel", ["AI Insights", "Automations", "Reports"],
        label_visibility="collapsed", key="intel_nav",
    )
    st.markdown("##### Settings")
    st.radio(
        "Settings", ["Integrations", "Settings"],
        label_visibility="collapsed", key="settings_nav",
    )

    st.divider()
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px'>"
        "<div style='width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#7c6fea,#a78bfa);"
        "display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;"
        "border:2px solid #263245'>JD</div>"
        "<div><div style='font-size:12px;font-weight:600'>Jamie Doe</div>"
        "<div style='font-size:11px;color:#6b7a95'>Growth Lead</div></div>"
        "<div style='margin-left:auto;width:7px;height:7px;border-radius:50%;background:#26d9b0;"
        "box-shadow:0 0 6px #26d9b0'></div></div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════
#  Top Bar
# ══════════════════════════════════════════════

top_l, top_r = st.columns([3, 2])
with top_l:
    st.markdown(
        "<div style='margin-bottom:4px'>"
        "<span style='font-size:20px;font-weight:800;letter-spacing:-.3px'>Dashboard</span>"
        " <span style='color:#6b7a95;font-weight:400;font-size:14px'>/ Overview</span></div>"
        "<div style='font-size:11px;color:#6b7a95'>Last synced <b style=\"color:#c8d0df\">just now</b> · Mar 2026</div>",
        unsafe_allow_html=True,
    )
with top_r:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:6px;background:rgba(124,111,234,.18);"
            "border:1px solid rgba(124,111,234,.3);color:#9d93f0;font-size:11px;font-weight:700;"
            "padding:5px 12px;border-radius:20px;width:fit-content'>"
            "<span class='live-dot'></span>AI Active</div>",
            unsafe_allow_html=True,
        )
    with c2:
        csv_data = campaigns_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Export CSV", csv_data, "adpilot_campaigns.csv", "text/csv",
                           use_container_width=True)
    with c3:
        run_ai = st.button("✦ Run AI Analysis", type="primary", use_container_width=True)
    with c4:
        new_camp = st.button("+ New Campaign", use_container_width=True)

# ══════════════════════════════════════════════
#  New Campaign Dialog
# ══════════════════════════════════════════════

@st.dialog("Create New Campaign")
def new_campaign_dialog():
    import html as _html

    name = st.text_input("Campaign Name *", max_chars=50, placeholder="e.g. Summer Sale 2026")
    c1, c2 = st.columns(2)
    with c1:
        platform = st.selectbox("Platform *", ["", "Google Ads", "Meta Ads", "TikTok", "LinkedIn"])
    with c2:
        spend = st.number_input("Monthly Spend ($) *", min_value=100, max_value=999_999, value=5000, step=100)
    c3, c4 = st.columns(2)
    with c3:
        roas = st.number_input("ROAS *", min_value=0.1, max_value=20.0, value=3.5, step=0.1, format="%.1f")
    with c4:
        status = st.selectbox("Status", ["Active", "Paused"])

    if st.button("✦ Create Campaign", type="primary", use_container_width=True):
        errors = []
        clean_name = name.strip()
        if not clean_name:
            errors.append("Campaign name is required.")
        elif clean_name.lower() in {
            n.lower() for n in st.session_state.campaigns["name"].tolist()
        }:
            errors.append(f"A campaign named \"{_html.escape(clean_name)}\" already exists.")
        if not platform:
            errors.append("Please select a platform.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            safe_name = _html.escape(clean_name)
            new_row = pd.DataFrame([{
                "id": st.session_state.next_id,
                "name": safe_name,
                "platform": platform,
                "spend": spend,
                "impressions": 0,
                "ctr": round(0.5 + 3 * (hash(clean_name) % 100) / 100, 2),
                "conv_rate": round(2 + 8 * (hash(clean_name) % 100) / 100, 1),
                "roas": roas,
                "status": status,
            }])
            st.session_state.campaigns = pd.concat(
                [st.session_state.campaigns, new_row], ignore_index=True,
            )
            st.session_state.next_id += 1
            st.success(f'"{safe_name}" added successfully!')
            time.sleep(0.8)
            st.rerun()

if new_camp:
    new_campaign_dialog()

# ══════════════════════════════════════════════
#  Data Sources
# ══════════════════════════════════════════════

st.markdown("---")
ds_header_l, ds_header_r = st.columns([2, 1])
with ds_header_l:
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px'>"
        "<span style='font-size:13px;font-weight:700'>Data Sources</span>"
        "<span style='display:inline-flex;align-items:center;gap:5px;background:rgba(38,217,176,.12);"
        "border:1px solid rgba(38,217,176,.2);border-radius:20px;padding:3px 10px'>"
        "<span class='live-dot'></span>"
        "<span style='font-size:10px;font-weight:700;color:#26d9b0;text-transform:uppercase;letter-spacing:.6px'>Live Data Sync</span>"
        "</span></div>",
        unsafe_allow_html=True,
    )

sources = get_data_sources()
ds_cols = st.columns(len(sources))
for col, ds in zip(ds_cols, sources):
    with col:
        st.markdown(
            f"<div class='ds-item'>"
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:8px'>"
            f"<span style='font-size:18px'>{ds['icon']}</span>"
            f"<span style='font-size:12px;font-weight:700;color:#c8d0df'>{ds['name']}</span>"
            f"<span style='margin-left:auto;width:7px;height:7px;border-radius:50%;"
            f"background:#26d9b0;box-shadow:0 0 6px #26d9b0;display:inline-block'></span></div>"
            f"<div style='display:flex;justify-content:space-between;align-items:center'>"
            f"<span style='font-size:10px;font-weight:700;color:#26d9b0;background:rgba(38,217,176,.12);"
            f"border:1px solid rgba(38,217,176,.2);padding:2px 8px;border-radius:20px'>● Connected</span>"
            f"<span style='font-size:10px;color:#6b7a95'>{ds['records']}</span></div>"
            f"<div style='margin-top:6px;font-size:10px;color:#6b7a95'>Last sync: "
            f"<b style='color:#c8d0df'>{ds['sync']}</b></div></div>",
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════
#  KPI Cards
# ══════════════════════════════════════════════

st.markdown("---")
if campaigns_df.empty:
    avg_roas = avg_ctr = avg_conv = total_spend = 0.0
    st.info("No campaign data available. Add a campaign to see KPIs.")
else:
    avg_roas = campaigns_df["roas"].mean()
    avg_ctr  = campaigns_df["ctr"].mean()
    avg_conv = campaigns_df["conv_rate"].mean()
    total_spend = campaigns_df["spend"].sum()

kpi_data = [
    ("ROAS",              f"{avg_roas:.2f}×", "↑ 12.4%", True,  "#7c6fea", 4.2,  0.8),
    ("Click-Through Rate", f"{avg_ctr:.2f}%",  "↑ 5.2%",  True,  "#26d9b0", 3.1,  0.9),
    ("Conversion Rate",    f"{avg_conv:.2f}%",  "↓ 1.8%",  False, "#f59e0b", 8.5,  1.2),
    ("Monthly Ad Spend",   _fmt_spend(total_spend), "↑ 8.1%", True, "#f43f5e", 75, 18),
]

kpi_cols = st.columns(4)
for col, (label, value, change, is_up, color, sp_base, sp_noise) in zip(kpi_cols, kpi_data):
    with col:
        arrow_cls = "up" if is_up else "down"
        st.markdown(
            f"<div class='kpi-card' style='border-top:2px solid {color}'>"
            f"<div class='kpi-label'>{label}</div>"
            f"<div class='kpi-value'>{value}</div>"
            f"<span class='kpi-change {arrow_cls}'>{change}</span>"
            f"<span class='kpi-period'>vs last month</span></div>",
            unsafe_allow_html=True,
        )
        spark = generate_sparkline(sp_base, sp_noise)
        st.plotly_chart(_sparkline_fig(spark, color), use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
#  Stat Row
# ══════════════════════════════════════════════

winner = get_winner(campaigns_df)
active_count = len(campaigns_df[campaigns_df["status"] == "Active"])

s1, s2, s3 = st.columns(3)

with s1:
    st.markdown(
        f"<div class='stat-card'>"
        f"<div style='font-size:10px;font-weight:700;color:#6b7a95;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px'>🏆 Best Campaign</div>"
        f"<div style='font-size:15px;font-weight:800;letter-spacing:-.2px'>{winner.get('name','—')}</div>"
        f"<div style='font-size:12px;color:#6b7a95;margin-bottom:14px'>{winner.get('platform','')} · Score {winner.get('score',0)}/100</div>"
        f"<div style='margin-bottom:6px'><div style='display:flex;justify-content:space-between;font-size:12px'>"
        f"<span style='color:#c8d0df'>Performance</span><span style='color:#9d93f0;font-weight:700'>{winner.get('score',0)}/100</span></div>"
        f"<div class='prog-track'><div class='prog-fill' style='width:{winner.get('score',0)}%;background:linear-gradient(90deg,#7c6fea,#9d93f0)'></div></div></div>"
        f"<div style='margin-bottom:6px'><div style='display:flex;justify-content:space-between;font-size:12px'>"
        f"<span style='color:#c8d0df'>Budget Used</span><span style='color:#f59e0b;font-weight:700'>72%</span></div>"
        f"<div class='prog-track'><div class='prog-fill' style='width:72%;background:linear-gradient(90deg,#f59e0b,#fb923c)'></div></div></div>"
        f"<div><div style='display:flex;justify-content:space-between;font-size:12px'>"
        f"<span style='color:#c8d0df'>Audience Reach</span><span style='color:#26d9b0;font-weight:700'>93%</span></div>"
        f"<div class='prog-track'><div class='prog-fill' style='width:93%;background:linear-gradient(90deg,#26d9b0,#22d3ee)'></div></div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

with s2:
    st.markdown(
        "<div class='stat-card'>"
        "<div style='font-size:10px;font-weight:700;color:#6b7a95;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px'>👁 Impressions</div>"
        "<div style='font-size:34px;font-weight:800;letter-spacing:-1px;line-height:1;margin-bottom:5px'>12.4M</div>"
        "<div style='font-size:12px;color:#6b7a95'>Across all active campaigns</div>"
        "<div style='display:inline-flex;align-items:center;gap:6px;background:rgba(38,217,176,.08);"
        "border:1px solid rgba(38,217,176,.2);color:#26d9b0;font-size:11px;font-weight:600;"
        "padding:4px 10px;border-radius:20px;margin-top:10px'><span class='live-dot'></span>Live tracking</div>"
        "<div style='display:flex;gap:20px;margin-top:14px'>"
        "<div><div style='font-size:16px;font-weight:700;color:#26d9b0'>6.1M</div><div style='font-size:10px;color:#6b7a95;font-weight:600;text-transform:uppercase'>Paid</div></div>"
        "<div><div style='font-size:16px;font-weight:700;color:#9d93f0'>4.2M</div><div style='font-size:10px;color:#6b7a95;font-weight:600;text-transform:uppercase'>Organic</div></div>"
        "<div><div style='font-size:16px;font-weight:700;color:#f59e0b'>2.1M</div><div style='font-size:10px;color:#6b7a95;font-weight:600;text-transform:uppercase'>Referral</div></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

with s3:
    platform_counts = campaigns_df["platform"].value_counts().to_dict()
    bars_html = ""
    plat_meta = [
        ("Google Ads", "#7c6fea", 75), ("Meta Ads", "#26d9b0", 58),
        ("TikTok", "#f59e0b", 42), ("LinkedIn", "#f43f5e", 25),
    ]
    for pname, pcolor, pwidth in plat_meta:
        cnt = platform_counts.get(pname, 0)
        bars_html += (
            f"<div style='display:flex;align-items:center;gap:10px;padding:4px 0'>"
            f"<span style='font-size:12px;color:#c8d0df;width:72px;flex-shrink:0'>{pname}</span>"
            f"<div style='flex:1;height:4px;background:#1a2130;border-radius:99px;overflow:hidden'>"
            f"<div style='height:100%;width:{pwidth}%;background:{pcolor};border-radius:99px'></div></div>"
            f"<span style='font-size:12px;font-weight:700;width:16px;text-align:right'>{cnt}</span></div>"
        )
    st.markdown(
        f"<div class='stat-card'>"
        f"<div style='font-size:10px;font-weight:700;color:#6b7a95;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px'>📡 Active Campaigns</div>"
        f"<div style='font-size:34px;font-weight:800;letter-spacing:-1px;line-height:1;margin-bottom:5px'>{len(campaigns_df)}</div>"
        f"<div style='font-size:12px;color:#6b7a95;margin-bottom:14px'>Across {len(platform_counts)} platforms</div>"
        f"{bars_html}</div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════
#  Performance Trends Chart
# ══════════════════════════════════════════════

st.markdown("---")
st.markdown("#### 📉 Performance Trends")
st.caption("ROAS, CTR & Conversion rate — last 12 weeks")

trend = get_trend_data()
fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend["weeks"], y=trend["roas"], name="ROAS",
    mode="lines+markers", line=dict(color="#7c6fea", width=2.5),
    marker=dict(size=5), fill="tozeroy", fillcolor="rgba(124,111,234,.08)",
))
fig_trend.add_trace(go.Scatter(
    x=trend["weeks"], y=trend["ctr"], name="CTR",
    mode="lines+markers", line=dict(color="#26d9b0", width=2.5),
    marker=dict(size=5), fill="tozeroy", fillcolor="rgba(38,217,176,.08)",
))
fig_trend.add_trace(go.Scatter(
    x=trend["weeks"], y=trend["conv"], name="Conv. Rate",
    mode="lines+markers", line=dict(color="#f59e0b", width=2.5),
    marker=dict(size=5), fill="tozeroy", fillcolor="rgba(245,158,11,.08)",
))
fig_trend.update_layout(
    **PLOTLY_LAYOUT_DEFAULTS,
    height=260,
    xaxis=dict(showgrid=False, color="#6b7a95"),
    yaxis=dict(showgrid=True, gridcolor="#1f2a3a", color="#6b7a95"),
    legend=dict(orientation="h", y=1.12, font=dict(size=11)),
)
st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
#  Campaign Table
# ══════════════════════════════════════════════

st.markdown("---")
tbl_l, tbl_r = st.columns([2, 1])
with tbl_l:
    st.markdown("#### All Campaigns")
with tbl_r:
    search_q = st.text_input("🔍 Search campaigns", label_visibility="collapsed",
                              placeholder="Search campaigns…", key="camp_search")

filter_col1, filter_col2, _ = st.columns([1, 1, 4])
with filter_col1:
    status_filter = st.selectbox("Status filter", ["All", "Active", "Paused"],
                                  label_visibility="collapsed")

display_df = campaigns_df.copy()
if search_q:
    mask = (
        display_df["name"].str.contains(search_q, case=False, na=False) |
        display_df["platform"].str.contains(search_q, case=False, na=False)
    )
    display_df = display_df[mask]
if status_filter != "All":
    display_df = display_df[display_df["status"] == status_filter]

if display_df.empty:
    st.info("No campaigns match your search or filter. Try adjusting your criteria.")
else:
    avg = campaigns_df["roas"].mean() if not campaigns_df.empty else 1.0
    if avg == 0:
        avg = 1.0  # prevent division by zero
    display_df = display_df.copy()
    display_df["vs_avg"] = display_df["roas"].apply(
        lambda r: f"{'↑' if r >= avg else '↓'} {abs(round((r - avg) / avg * 100))}%"
    )
    display_df["spend_fmt"] = display_df["spend"].apply(_fmt_spend)

    show_cols = {
        "name": "Campaign", "platform": "Platform", "spend_fmt": "Spend",
        "impressions": "Impressions", "ctr": "CTR %", "conv_rate": "Conv %",
        "roas": "ROAS", "vs_avg": "vs Avg", "status": "Status",
    }
    st.dataframe(
        display_df[list(show_cols.keys())].rename(columns=show_cols),
        use_container_width=True,
        hide_index=True,
        height=min(400, 55 + len(display_df) * 38),
    )
    st.caption(f"Sorted by ROAS · {len(display_df)} campaigns")

# ══════════════════════════════════════════════
#  Campaign Comparison
# ══════════════════════════════════════════════

st.markdown("---")
st.markdown("#### 🏅 Campaign Comparison — ROAS Ranking")

comp_l, comp_r = st.columns([1, 2])

with comp_l:
    st.markdown(
        f"<div class='winner-card'>"
        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:16px'>"
        f"<span style='font-size:22px'>👑</span>"
        f"<span class='badge badge-opportunity' style='background:rgba(251,191,36,.12);color:#fbbf24;"
        f"border:1px solid rgba(251,191,36,.25)'>Top Performer</span></div>"
        f"<div style='font-size:17px;font-weight:800;letter-spacing:-.3px'>{winner.get('name','—')}</div>"
        f"<div style='font-size:12px;color:#6b7a95;margin-bottom:18px'>{winner.get('platform','')}</div>"
        f"<div style='display:flex;align-items:baseline;gap:6px;margin-bottom:20px'>"
        f"<span style='font-size:48px;font-weight:900;color:#fbbf24;line-height:1;letter-spacing:-2px'>{winner.get('roas',0)}</span>"
        f"<span style='font-size:14px;font-weight:600;color:#6b7a95'>× ROAS</span></div>"
        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>"
        f"<div style='background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:9px;padding:10px 12px'>"
        f"<div style='font-size:15px;font-weight:800;color:#26d9b0'>{winner.get('ctr',0)}%</div><div style='font-size:10px;color:#6b7a95'>CTR</div></div>"
        f"<div style='background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:9px;padding:10px 12px'>"
        f"<div style='font-size:15px;font-weight:800;color:#f59e0b'>{winner.get('conv_rate',0)}%</div><div style='font-size:10px;color:#6b7a95'>Conv. Rate</div></div>"
        f"<div style='background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:9px;padding:10px 12px'>"
        f"<div style='font-size:15px;font-weight:800'>{_fmt_spend(winner.get('spend',0))}</div><div style='font-size:10px;color:#6b7a95'>Ad Spend</div></div>"
        f"<div style='background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:9px;padding:10px 12px'>"
        f"<div style='font-size:15px;font-weight:800'>{winner.get('impressions','—')}</div><div style='font-size:10px;color:#6b7a95'>Impressions</div></div></div>"
        f"<div style='margin-top:16px;display:inline-flex;align-items:center;gap:5px;background:rgba(251,191,36,.12);"
        f"border:1px solid rgba(251,191,36,.25);color:#fbbf24;font-size:11px;font-weight:700;padding:5px 13px;border-radius:20px'>"
        f"↑ {winner.get('above_avg_pct',0)}% above account average</div></div>",
        unsafe_allow_html=True,
    )

with comp_r:
    sorted_camps = campaigns_df.sort_values("roas", ascending=False)
    max_roas = sorted_camps["roas"].max()
    fig_bars = go.Figure()
    colors = [
        "#fbbf24" if i == 0 else ("#7c6fea" if r["status"] == "Active" else "#263245")
        for i, (_, r) in enumerate(sorted_camps.iterrows())
    ]
    fig_bars.add_trace(go.Bar(
        y=sorted_camps["name"],
        x=sorted_camps["roas"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=sorted_camps["roas"].apply(lambda x: f"{x}×"),
        textposition="outside",
        textfont=dict(color="#c8d0df", size=11, family="Inter"),
    ))
    fig_bars.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        height=max(250, len(sorted_camps) * 38),
        yaxis=dict(autorange="reversed", color="#c8d0df", tickfont=dict(size=11)),
        xaxis=dict(showgrid=True, gridcolor="#1f2a3a", color="#6b7a95",
                   title="ROAS", range=[0, max_roas * 1.25]),
        showlegend=False,
    )
    st.plotly_chart(fig_bars, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
#  Budget Allocation
# ══════════════════════════════════════════════

st.markdown("---")
st.markdown("#### 💰 Budget Allocation")
st.caption("Monthly ad spend distribution · drag sliders to simulate reallocation")

bud_l, bud_r = st.columns([1, 1])

platform_budgets = get_platform_budgets()
budget_spends = st.session_state.budget_spends
total_budget = sum(budget_spends.values())

with bud_l:
    fig_donut = go.Figure()
    fig_donut.add_trace(go.Pie(
        labels=[p["name"] for p in platform_budgets],
        values=[budget_spends[p["name"]] for p in platform_budgets],
        hole=0.62,
        marker=dict(colors=[p["color"] for p in platform_budgets],
                    line=dict(color="#080b12", width=2)),
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(color="#c8d0df", size=11),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig_donut.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        height=320,
        showlegend=False,
        annotations=[dict(
            text=f"<b>${total_budget/1000:.1f}K</b><br><span style='font-size:11px;color:#6b7a95'>Total Spend</span>",
            x=0.5, y=0.5, font=dict(size=22, color="#f1f4f9"), showarrow=False,
        )],
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

with bud_r:
    for p in platform_budgets:
        pct = budget_spends[p["name"]] / total_budget * 100
        st.markdown(
            f"<div class='plat-leg-row'>"
            f"<div style='width:12px;height:12px;border-radius:50%;background:{p['color']};flex-shrink:0'></div>"
            f"<div style='flex:1;min-width:0'>"
            f"<div style='font-size:13px;font-weight:700;margin-bottom:2px'>{p['name']}</div>"
            f"<div style='font-size:11px;color:#6b7a95'>{p['campaigns']} campaigns · CPA: {p['cpa']}</div></div>"
            f"<div style='text-align:right'>"
            f"<div style='font-size:14px;font-weight:800'>{_fmt_spend(budget_spends[p['name']])}</div>"
            f"<div style='font-size:11px;color:#6b7a95'>{pct:.1f}%</div>"
            f"<div style='font-size:11px;font-weight:700;color:{'#26d9b0' if p['up'] else '#f43f5e'}'>{p['change']}</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='font-size:10px;font-weight:700;color:#6b7a95;text-transform:uppercase;letter-spacing:.7px;"
        "margin:16px 0 8px'>🎛 Budget Simulator — drag to reallocate</div>",
        unsafe_allow_html=True,
    )
    for p in platform_budgets:
        new_val = st.slider(
            p["name"], min_value=2000, max_value=60000, value=budget_spends[p["name"]],
            step=200, format="$%d", key=f"slider_{p['name']}",
        )
        st.session_state.budget_spends[p["name"]] = new_val

# ══════════════════════════════════════════════
#  Projected Optimization Impact (Forecast)
# ══════════════════════════════════════════════

st.markdown("---")
fc_head_l, fc_head_r = st.columns([3, 1])
with fc_head_l:
    st.markdown("#### 📈 Projected Optimization Impact")
    st.caption("Estimated uplift if AI recommendations are applied")
with fc_head_r:
    st.markdown(
        "<div style='display:flex;justify-content:flex-end'>"
        "<span style='background:rgba(124,111,234,.08);border:1px solid rgba(124,111,234,.2);"
        "border-radius:20px;padding:4px 12px;font-size:10px;font-weight:700;color:#9d93f0;"
        "text-transform:uppercase;letter-spacing:.6px'>✦ AI Forecast</span></div>",
        unsafe_allow_html=True,
    )

fc_l, fc_r = st.columns([2, 1])
forecasts = get_forecast_actions()
all_recs = analyze_campaigns(campaigns_df)
impact = compute_forecast_impact(all_recs)

with fc_l:
    rows_html = ""
    for f in forecasts:
        conf_color = "#26d9b0" if f["confidence"] >= 85 else ("#f59e0b" if f["confidence"] >= 75 else "#6b7a95")
        rows_html += (
            f"<div class='forecast-row'>"
            f"<div style='display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600;color:#c8d0df'>"
            f"<span>{f['icon']}</span><span>{f['action']}</span></div>"
            f"<div style='font-size:13px;font-weight:800;text-align:center;color:#26d9b0'>{f['metric']}</div>"
            f"<div style='display:flex;align-items:center;justify-content:center;gap:6px'>"
            f"<div style='width:48px;height:4px;background:#1a2130;border-radius:99px;overflow:hidden'>"
            f"<div style='height:100%;width:{f['confidence']}%;background:{conf_color};border-radius:99px'></div></div>"
            f"<span style='font-size:10px;font-weight:700;color:{conf_color}'>{f['confidence']}%</span></div></div>"
        )
    st.markdown(
        f"<div style='background:#141923;border:1px solid #1f2a3a;border-radius:12px;overflow:hidden'>"
        f"<div style='display:grid;grid-template-columns:1fr 140px 100px;padding:10px 16px;"
        f"border-bottom:1px solid #1f2a3a;background:#1a2130'>"
        f"<div style='font-size:10px;font-weight:700;color:#6b7a95;text-transform:uppercase;letter-spacing:.7px'>Optimization Action</div>"
        f"<div style='font-size:10px;font-weight:700;color:#6b7a95;text-transform:uppercase;letter-spacing:.7px;text-align:center'>Est. Impact</div>"
        f"<div style='font-size:10px;font-weight:700;color:#6b7a95;text-transform:uppercase;letter-spacing:.7px;text-align:center'>Confidence</div></div>"
        f"{rows_html}</div>",
        unsafe_allow_html=True,
    )

with fc_r:
    st.markdown(
        f"<div style='background:linear-gradient(145deg,rgba(38,217,176,.06),rgba(124,111,234,.04));"
        f"border:1px solid rgba(38,217,176,.18);border-radius:13px;padding:20px'>"
        f"<div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#26d9b0;margin-bottom:14px'>📊 Estimated Monthly Impact</div>"
        f"<div style='background:rgba(38,217,176,.07);border:1px solid rgba(38,217,176,.15);border-radius:10px;padding:14px 16px;margin-bottom:10px'>"
        f"<div style='font-size:26px;font-weight:900;color:#26d9b0;letter-spacing:-1px;line-height:1;margin-bottom:4px'>+${impact['additional_revenue']:,}</div>"
        f"<div style='font-size:12px;color:#6b7a95'>projected additional revenue</div></div>"
        f"<div style='background:rgba(244,63,94,.06);border:1px solid rgba(244,63,94,.15);border-radius:10px;padding:14px 16px;margin-bottom:10px'>"
        f"<div style='font-size:26px;font-weight:900;color:#f43f5e;letter-spacing:-1px;line-height:1;margin-bottom:4px'>−${impact['reduced_wasted_spend']:,}</div>"
        f"<div style='font-size:12px;color:#6b7a95'>reduced wasted ad spend</div></div>"
        f"<div style='border-top:1px solid #1f2a3a;padding-top:14px;margin-top:4px'>"
        f"<div style='font-size:11px;color:#6b7a95;font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>Net Monthly Gain</div>"
        f"<div style='font-size:30px;font-weight:900;letter-spacing:-1px'>+${impact['net_monthly_gain']:,}</div>"
        f"<div style='font-size:11px;color:#6b7a95;margin-top:3px'>across all campaigns</div></div></div>",
        unsafe_allow_html=True,
    )

if st.button("✦ Apply All Recommendations", type="primary", use_container_width=True, key="apply_all"):
    st.session_state.applied_recs = set(range(len(all_recs)))
    st.success("All recommendations applied!")

# ══════════════════════════════════════════════
#  Standing Recommendations
# ══════════════════════════════════════════════

st.markdown("---")
st.markdown("#### ✦ Standing Recommendations")
st.caption("Persistent optimizations · reviewed weekly")

standing = [
    {"tag": "High", "icon": "🔴", "title": "Reallocate budget from underperforming Meta campaigns",
     "body": "3 Meta ad sets have ROAS below 1.8×. Shifting 22% to top-performing Google Search campaigns could improve overall returns.",
     "impact": "+0.74× ROAS"},
    {"tag": "Medium", "icon": "🟡", "title": "Adjust TikTok bidding strategy to Target CPA",
     "body": "Manual CPC creates off-peak inefficiencies. Target CPA at $14 aligns with conversion data and should reduce cost-per-acquisition.",
     "impact": "−18% CPA"},
    {"tag": "Opportunity", "icon": "🟢", "title": "Enable dayparting on Google Search campaigns",
     "body": "68% of conversions occur 9 AM–3 PM on weekdays. Raising bids during peak hours and reducing overnight spend improves efficiency.",
     "impact": "+1.2% Conv."},
]

rec_cols = st.columns(3)
for col, rec in zip(rec_cols, standing):
    badge_cls = rec["tag"].lower()
    with col:
        st.markdown(
            f"<div class='rec-card'>"
            f"<div class='badge badge-{badge_cls}' style='margin-bottom:10px'>{rec['icon']} {rec['tag']} Priority</div>"
            f"<div style='font-size:13px;font-weight:700;margin-bottom:6px;line-height:1.45'>{rec['title']}</div>"
            f"<div style='font-size:12px;color:#6b7a95;line-height:1.6;margin-bottom:12px'>{rec['body']}</div>"
            f"<div style='display:flex;align-items:center;justify-content:space-between;padding-top:10px;border-top:1px solid #1f2a3a'>"
            f"<span style='font-size:12px;font-weight:700;color:#26d9b0'>{rec['impact']}</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        st.button(f"Apply → {rec['title'][:20]}…", key=f"rec_{badge_cls}", use_container_width=True)

# ══════════════════════════════════════════════
#  AI Analysis Panel (triggered by top-bar btn)
# ══════════════════════════════════════════════

if run_ai:
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            "<div style='font-size:14px;font-weight:800;display:flex;align-items:center;gap:8px'>"
            "✦ AI Insights</div>",
            unsafe_allow_html=True,
        )
        with st.spinner("AdPilot AI is thinking…"):
            for step in [
                "Scanning campaign data…",
                "Cross-referencing benchmarks…",
                "Detecting inefficiencies…",
                "Modelling scenarios…",
                "Generating insights…",
            ]:
                st.caption(step)
                time.sleep(0.5)

        recs = analyze_campaigns(campaigns_df)
        ai_impact = compute_forecast_impact(recs)
        st.session_state.ai_results = recs

        st.markdown(
            f"<div style='background:rgba(124,111,234,.06);border:1px solid rgba(124,111,234,.15);"
            f"border-radius:10px;padding:12px 14px;margin-bottom:14px;font-size:11px;color:#6b7a95;line-height:1.7'>"
            f"Analysed <strong style='color:#9d93f0'>{len(campaigns_df)} campaigns</strong> · "
            f"<strong style='color:#9d93f0'>{len(recs)} recommendations</strong> generated<br>"
            f"Projected net gain: <strong style='color:#26d9b0'>+${ai_impact['net_monthly_gain']:,}</strong></div>",
            unsafe_allow_html=True,
        )

        for i, rec in enumerate(recs):
            badge_cls = rec["impact"].lower()
            icon = IMPACT_ICONS.get(rec["impact"], "")
            st.markdown(
                f"<div style='background:#141923;border:1px solid #1f2a3a;border-radius:11px;"
                f"padding:14px;margin-bottom:12px'>"
                f"<div style='display:flex;justify-content:space-between;gap:8px;margin-bottom:8px'>"
                f"<div style='font-size:13px;font-weight:700;line-height:1.4'>{rec['title']}</div>"
                f"<span class='badge badge-{badge_cls}'>{icon} {rec['impact']}</span></div>"
                f"<div style='font-size:12px;color:#6b7a95;line-height:1.6;margin-bottom:12px'>{rec['body']}</div>"
                f"<div style='display:flex;justify-content:space-between;padding-top:10px;border-top:1px solid #1f2a3a'>"
                f"<span style='background:rgba(124,111,234,.12);border:1px solid rgba(124,111,234,.2);"
                f"border-radius:20px;padding:3px 10px;font-size:11px;font-weight:700;color:#9d93f0'>✦ {rec['perf']}</span>"
                f"</div></div>",
                unsafe_allow_html=True,
            )
            st.button(f"Apply → {rec['title'][:25]}…", key=f"ai_rec_{i}")
