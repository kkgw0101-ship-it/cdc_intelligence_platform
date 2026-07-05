"""
CDC Partner Portal
Customer-facing Streamlit portal for CDC and KCC Glass.
"""

from __future__ import annotations

import base64
import io
import json
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


APP_DIR = os.path.dirname(__file__)
CDC_RED = "#EF001F"
CDC_BLACK = "#050505"
CDC_GOLD = "#EF001F"
PARTNER_NAVY = "#0E2372"
NAVY = "#101418"
GOLD = "#EF001F"
INK = "#F4F7FB"
MIST = "#07090C"
PANEL = "#111418"
PANEL2 = "#171B21"
LINE = "#2A3038"
GREEN = "#0E9F6E"
RED = "#D64545"
ORANGE = "#C77800"
CUSTOMER_SHARE_MODE = True

PAGE_ICON = os.path.join(APP_DIR, "cdc_distributors_logo.png")
if not os.path.exists(PAGE_ICON):
    PAGE_ICON = "CDC"

st.set_page_config(
    page_title="CDC Partner Portal | Permagrain",
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_secret(name: str, default: str = "") -> str:
    env_value = os.environ.get(name)
    if env_value:
        return env_value
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def require_portal_password() -> None:
    expected = get_secret("CDC_PORTAL_PASSWORD", "") or get_secret("PORTAL_PASSWORD", "")
    if not expected:
        st.error("Portal password is not configured. Add CDC_PORTAL_PASSWORD in Streamlit secrets before sharing this portal.")
        st.stop()

    if st.session_state.get("portal_authenticated"):
        return

    st.markdown("### CDC Partner Portal")
    st.caption("Private access for the Permagrain launch workspace.")
    entered = st.text_input("Password", type="password")
    if st.button("Enter portal", type="primary"):
        if entered == expected:
            st.session_state.portal_authenticated = True
            st.rerun()
        st.error("Incorrect password.")
    st.stop()


require_portal_password()


def image_b64(file_name: str) -> str:
    path = os.path.join(APP_DIR, file_name)
    try:
        with open(path, "rb") as handle:
            return base64.b64encode(handle.read()).decode("utf-8")
    except Exception:
        return ""


CDC_LOGO = image_b64("cdc_logo_horizontal.png") or image_b64("cdc_distributors_logo_crop.png") or image_b64("cdc_distributors_logo.png")
CDC_TAGLINE_LOGO = image_b64("cdc_logo_tagline_mark.png")
KCC_LOGO_WHITE = image_b64("logo_white_t.png")
KCC_VIDEO_THUMB = image_b64("kcc_company_video_thumb.jpg")
KCC_CERT_BADGES = image_b64("kcc_certification_badges.png")
KCC_4RE_IMAGE = image_b64("kcc_4re_solution.png")
KCC_BROCHURE_FILE = "kcc_lvt_blue_brochure_2026.pdf"
CDC_HERO_IMAGES = [
    image_b64("cdc_hero_facility_aerial.png"),
    image_b64("cdc_hero_team_event.png"),
    image_b64("cdc_hero_facility_parking.png"),
]
FRED_API_KEY = get_secret("FRED_API_KEY", "")
SHIPMENT_AS_OF = "2026-07-01"
SHIPMENT_SOURCE = "KCC shipping desk"
MARKET_SOURCE = "Latest available source data"

KCC_ESG_EN = "https://www.kccglass.co.kr/eng/esgManagement/about/report.do"
KCC_ESG_KO = "https://www.kccglass.co.kr/esgManagement/about/report.do"
MENU_ITEMS = ["Account Overview", "Order & Shipment Desk", "Permagrain SKU Room", "Sales Playbook", "Market Signal for CDC", "Next 30 Days", "ESG & Growth Kit"]

if "view" not in st.session_state:
    st.session_state.view = MENU_ITEMS[0]

TEXT_SIZE_OPTIONS = ["Default", "Large", "Extra Large"]
if "text_size_mode" not in st.session_state or st.session_state.text_size_mode not in TEXT_SIZE_OPTIONS:
    st.session_state.text_size_mode = "Default"

TEXT_SCALE = {"Default": 1.0, "Large": 1.08, "Extra Large": 1.16}.get(st.session_state.text_size_mode, 1.0)

st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{ background:{MIST}; color:{INK}; --ui-scale:{TEXT_SCALE}; }}
[data-testid="stHeader"] {{ background:transparent; height:0; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}

/* Fixed terminal sidebar */
[data-testid="stSidebarCollapsedControl"] {{
  display:none !important;
}}
[data-testid="stSidebarCollapseButton"] {{
  display:none !important;
}}
[data-testid="stSidebar"] {{ transform:none !important; visibility:visible !important; min-width:230px !important; width:230px !important; background:linear-gradient(180deg,#160709 0%,#0E0708 58%,#050505 100%); border-right:1px solid rgba(239,0,31,.30); }}
[data-testid="stSidebar"][aria-expanded="false"] {{ margin-left:0 !important; }}
[data-testid="stMain"] {{ width:100% !important; max-width:none !important; flex:1 1 auto !important; }}
[data-testid="stMain"] > div {{ max-width:none !important; }}
.block-container {{
  padding:0.75rem 1.2rem 2rem 1.2rem;
  max-width:min(1680px, 100%) !important;
  width:100% !important;
  margin-left:0 !important;
  margin-right:auto !important;
}}
* {{ font-variant-numeric: tabular-nums; letter-spacing:0; }}
[data-testid="stSidebar"] * {{ color:#FFFFFF !important; }}
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button {{
  background:rgba(255,255,255,.06) !important; border:1px solid rgba(255,255,255,.10) !important;
  color:#fff !important; border-radius:7px !important; min-height:34px !important;
}}
.sidebar-brand-block {{ text-align:center; padding:12px 0 18px; border-bottom:1px solid rgba(243,215,75,.18); margin-bottom:16px; }}
.sidebar-logo-main {{ width:150px; max-width:100%; display:block; margin:0 auto 12px; background:#050505; border-radius:7px; padding:8px; border:1px solid rgba(239,0,31,.24); box-shadow:0 18px 40px rgba(0,0,0,.26); }}
.side-brand {{ font-weight:700; font-size:calc(15px * var(--ui-scale)); letter-spacing:1.2px; margin:2px 0 4px; }}
.side-sub {{ color:#B8AEB2 !important; font-size:calc(11px * var(--ui-scale)); line-height:1.45; }}
.side-tool-label {{ color:#8F9AAA !important; font-size:10px; font-weight:600; letter-spacing:.8px; text-transform:uppercase; margin:20px 0 8px; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding:8px 10px; border-radius:7px; margin:2px 0; font-size:calc(13px * var(--ui-scale)); transition:background .15s; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background:rgba(239,0,31,.16); }}
.sb-nav-label {{ color:#D9BFC3 !important; font-size:10px; font-weight:600; letter-spacing:.8px; text-transform:uppercase; margin:14px 0 6px 0; }}
.sidebar-logo {{ width:96px; max-width:100%; background:#050505; border-radius:7px; padding:5px; margin-bottom:10px; border:1px solid rgba(243,215,75,.34); }}
.data-strip {{ display:none; }}
.market-marquee {{ height:34px; overflow:hidden; background:#0A0D11; border:1px solid {LINE}; border-radius:8px; margin-bottom:10px; display:flex; align-items:center; box-shadow:0 10px 24px rgba(0,0,0,.16); }}
.market-track {{ display:flex; width:max-content; animation:marketFlow 58s linear infinite; }}
.market-set {{ display:flex; align-items:center; flex-shrink:0; min-width:max-content; }}
.market-item {{ display:inline-flex; align-items:center; gap:8px; padding:0 24px; color:#DDE5F0; font-size:12px; font-weight:600; white-space:nowrap; font-family:Consolas, monospace; }}
.market-dot {{ width:5px; height:5px; border-radius:50%; background:{CDC_RED}; display:inline-block; }}
.market-label {{ color:#8F9AAD; font-weight:600; text-transform:uppercase; }}
.market-value {{ color:#FFFFFF; font-weight:700; }}
.market-source {{ color:#8A95A5; font-size:10px; }}
@keyframes marketFlow {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}
.topbar {{
  display:flex; align-items:center; justify-content:space-between; gap:18px;
  background:#101419; color:#fff; border-bottom:2px solid {CDC_RED};
  border-top:1px solid rgba(239,0,31,.42);
  border-radius:8px; padding:12px 18px; margin-bottom:12px;
  box-shadow:0 12px 34px rgba(0,0,0,.18);
}}
.brand-lockup {{ display:flex; align-items:center; gap:14px; min-width:0; }}
.cdc-emblem {{ height:48px; width:72px; object-fit:contain; background:#050505; border-radius:6px; padding:4px; border:1px solid rgba(239,0,31,.25); }}
.platform-name {{ display:flex; flex-direction:column; gap:2px; }}
.platform-title {{ color:#FFFFFF; font-size:18px; font-weight:700; letter-spacing:.2px; text-transform:uppercase; }}
.platform-sub {{ color:#B8AEB2; font-size:11px; font-weight:500; text-transform:uppercase; }}
.kcc-lockup {{ display:flex; align-items:center; gap:10px; margin-left:12px; padding-left:16px; border-left:1px solid rgba(255,255,255,.12); }}
.kcc-lockup span {{ color:#D8DCE8; font-size:10px; font-weight:600; text-transform:uppercase; }}
.kcc-lockup img {{ height:32px; width:auto; background:{PARTNER_NAVY}; border-radius:5px; padding:6px 10px; box-shadow:0 10px 24px rgba(0,0,0,.20); }}
.top-meta {{ display:flex; gap:22px; align-items:center; text-align:right; }}
.top-k {{ font-size:9px; color:#D9BFC3; text-transform:uppercase; font-weight:800; }}
.top-v {{ font-size:13px; color:#fff; font-weight:700; font-family:Consolas, monospace; }}
.stButton button {{
  border-radius:7px !important; min-height:36px !important; font-weight:700 !important;
  white-space:normal !important; line-height:1.15 !important;
}}
.hero {{ margin-bottom:14px; }}
.hero-main {{
  position:relative; min-height:318px; border-radius:10px; overflow:hidden; width:100%;
  background:#0D1015;
  border:1px solid {LINE}; box-shadow:0 14px 44px rgba(0,0,0,.22);
}}
.hero-bg {{
  position:absolute; inset:0; z-index:0; display:block; background-size:cover; background-position:center;
  opacity:0; transform:scale(1.02); filter:saturate(.82) contrast(1.05) brightness(.58); animation:cdcHeroFade 30s infinite;
}}
.hero-bg:nth-child(1) {{ animation-delay:0s; }}
.hero-bg:nth-child(2) {{ animation-delay:10s; }}
.hero-bg:nth-child(3) {{ animation-delay:20s; }}
.hero-main::before {{
  content:""; position:absolute; inset:0; z-index:0; pointer-events:none;
  background:
    linear-gradient(90deg,rgba(6,8,11,.96) 0%,rgba(10,13,17,.82) 42%,rgba(10,13,17,.45) 72%,rgba(10,13,17,.30) 100%),
    linear-gradient(180deg,rgba(0,0,0,.10),rgba(0,0,0,.22));
}}
.hero-main::after {{ display:none; }}
.hero-content {{ position:relative; z-index:1; padding:28px 32px; display:flex; align-items:flex-end; justify-content:space-between; gap:20px; min-height:318px; }}
@keyframes cdcHeroFade {{
  0% {{ opacity:0; transform:scale(1.04); }}
  7% {{ opacity:1; }}
  31% {{ opacity:1; transform:scale(1.015); }}
  38% {{ opacity:0; }}
  100% {{ opacity:0; transform:scale(1.04); }}
}}
.hero-brand-row {{ display:flex; align-items:center; gap:14px; margin-bottom:22px; }}
.hero-brand-chip {{ display:flex; align-items:center; gap:12px; background:rgba(5,5,5,.68); border:1px solid rgba(255,255,255,.13); border-radius:8px; padding:11px 14px; backdrop-filter:blur(10px); box-shadow:0 20px 44px rgba(0,0,0,.26); }}
.hero-brand-chip img {{ height:54px; width:74px; object-fit:contain; }}
.hero-brand-text {{ display:flex; flex-direction:column; gap:2px; }}
.hero-brand-main {{ color:#fff; font-size:15px; font-weight:700; text-transform:uppercase; letter-spacing:.8px; }}
.hero-brand-sub {{ color:#AFB8C7; font-size:10px; font-weight:600; text-transform:uppercase; }}
.eyebrow {{ color:#AAB4C3; font-size:calc(11px * var(--ui-scale)); text-transform:uppercase; font-weight:600; letter-spacing:.8px; }}
.h1 {{ color:#fff; font-size:calc(30px * var(--ui-scale)); line-height:1.12; font-weight:700; max-width:760px; margin-top:8px; }}
.h-sub {{ color:#C7D0DD; font-size:calc(13px * var(--ui-scale)); line-height:1.5; max-width:820px; margin-top:8px; }}
.hero-bottom {{ display:flex; flex-direction:column; gap:18px; }}
.hero-actions {{ display:flex; gap:8px; flex-wrap:wrap; }}
.pill {{
  display:inline-flex; align-items:center; gap:6px; border:1px solid rgba(232,179,57,.48);
  background:rgba(5,5,5,.70); color:#fff; border-radius:999px; padding:9px 14px; font-size:calc(12px * var(--ui-scale)); font-weight:600;
}}
.hero-signal-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; max-width:900px; }}
.signal {{
  background:rgba(12,12,15,.82); border:1px solid rgba(255,255,255,.14); border-radius:9px; padding:13px 14px;
  display:flex; flex-direction:column; justify-content:center;
  backdrop-filter:blur(8px); min-height:116px; box-shadow:0 14px 36px rgba(0,0,0,.28);
}}
.signal-k {{ color:#9AA4B4; font-size:calc(10px * var(--ui-scale)); text-transform:uppercase; font-weight:600; }}
.signal-v {{ color:{INK}; font-size:calc(21px * var(--ui-scale)); font-weight:700; margin-top:2px; font-family:Consolas, monospace; }}
.signal-d {{ color:#8A95A5; font-size:calc(11px * var(--ui-scale)); margin-top:3px; }}
.grid4 {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-bottom:12px; }}
.grid6 {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-bottom:12px; }}
.metric {{
  background:{PANEL}; border:1px solid {LINE}; border-radius:8px; padding:14px;
  min-height:98px;
}}
.metric-k {{ color:#8A95A5; font-size:calc(10px * var(--ui-scale)); text-transform:uppercase; font-weight:600; }}
.metric-v {{ color:{INK}; font-size:calc(25px * var(--ui-scale)); line-height:1.1; font-weight:700; margin-top:8px; font-family:Consolas, monospace; }}
.metric-c {{ color:#8A95A5; font-size:calc(11px * var(--ui-scale)); margin-top:6px; }}
.next-action {{
  background:{PANEL}; border:1px solid {LINE}; border-left:4px solid {GOLD};
  border-radius:8px; padding:14px; margin-bottom:12px;
}}
.next-action-k {{ color:#8A95A5; font-size:calc(10px * var(--ui-scale)); text-transform:uppercase; font-weight:600; }}
.next-action-v {{ color:{INK}; font-size:calc(20px * var(--ui-scale)); font-weight:700; margin-top:4px; }}
.next-action-d {{ color:#8A95A5; font-size:calc(12px * var(--ui-scale)); margin-top:5px; line-height:1.45; }}
.timeline {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; }}
.step {{ background:{PANEL}; border:1px solid {LINE}; border-radius:8px; padding:13px; min-height:128px; }}
.step-k {{ color:#AAB4C3; font-size:calc(11px * var(--ui-scale)); font-weight:600; text-transform:uppercase; }}
.step-v {{ color:{INK}; font-size:calc(15px * var(--ui-scale)); font-weight:700; margin-top:7px; line-height:1.25; }}
.step-d {{ color:#8A95A5; font-size:calc(12px * var(--ui-scale)); line-height:1.45; margin-top:7px; }}
.meaning {{ background:{PANEL2}; border:1px solid {LINE}; border-left:4px solid {GOLD}; border-radius:8px; padding:12px; color:{INK}; font-size:calc(13px * var(--ui-scale)); line-height:1.55; }}
.panel {{ background:{PANEL}; border:1px solid {LINE}; border-radius:8px; overflow:hidden; margin-bottom:12px; }}
.panel-h {{
  display:flex; justify-content:space-between; align-items:center; gap:12px;
  padding:12px 14px; border-bottom:1px solid {LINE}; border-left:4px solid {GOLD};
  background:linear-gradient(90deg,rgba(239,0,31,.18),rgba(106,32,40,.22),{PANEL2});
}}
.panel-t {{ font-weight:700; color:{INK}; font-size:calc(13px * var(--ui-scale)); }}
.panel-m {{ color:#8A95A5; font-size:10px; font-family:Consolas, monospace; }}
.panel-b {{ padding:14px; }}
.care-grid {{ display:grid; grid-template-columns:1.05fr .95fr; gap:12px; }}
.sku-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.sku {{ border:1px solid {LINE}; border-radius:8px; overflow:hidden; background:{PANEL}; min-height:238px; }}
.swatch {{ height:112px; background-size:cover; border-bottom:1px solid {LINE}; }}
.sku-body {{ padding:12px; }}
.sku-code {{ color:{CDC_RED}; font-size:calc(11px * var(--ui-scale)); font-weight:700; font-family:Consolas, monospace; }}
.sku-name {{ color:{INK}; font-size:calc(18px * var(--ui-scale)); font-weight:700; margin-top:2px; }}
.sku-copy {{ color:#8A95A5; font-size:calc(12px * var(--ui-scale)); line-height:1.45; margin-top:8px; min-height:50px; }}
.tagline {{ display:flex; gap:6px; flex-wrap:wrap; margin-top:9px; }}
.tag {{ border:1px solid {LINE}; background:{PANEL2}; color:#C9D3EA; border-radius:999px; padding:3px 7px; font-size:10px; font-weight:800; }}
.brief {{ background:{PANEL2}; border:1px solid {LINE}; border-radius:8px; padding:12px; color:#D6DEE8; font-size:calc(13px * var(--ui-scale)); line-height:1.55; }}
.alert {{ border-left:4px solid {GREEN}; }}
.alert.warn {{ border-left-color:{ORANGE}; }}
.alert.risk {{ border-left-color:{RED}; }}
.link-btn {{
  display:inline-flex; padding:8px 10px; border-radius:7px; background:{CDC_RED}; color:#fff !important;
  font-weight:700; font-size:12px; text-decoration:none; margin-right:6px;
}}
.link-btn.secondary {{ background:{PANEL2}; color:#FFFFFF !important; border:1px solid {LINE}; }}
.note {{ color:#8A95A5; font-size:calc(11px * var(--ui-scale)); line-height:1.55; }}
.small-table {{ font-size:12px; }}
.dark-table-scroll {{ width:100%; overflow:auto; border:1px solid {LINE}; border-radius:8px; background:#100B0D; }}
.dark-data-table {{ width:100%; border-collapse:collapse; color:#E8EDF6; font-size:calc(12px * var(--ui-scale)); }}
.dark-data-table thead th {{ background:#210B10; color:#F5F7FB; text-align:left; padding:10px 11px; border-bottom:1px solid rgba(239,0,31,.30); font-weight:600; white-space:nowrap; }}
.dark-data-table tbody td {{ background:#120D0F; color:#DDE5F0; padding:9px 11px; border-top:1px solid rgba(255,255,255,.06); vertical-align:top; }}
.dark-data-table tbody tr:nth-child(even) td {{ background:#171012; }}
.dark-data-table tbody tr:hover td {{ background:#211418; }}
.playbook-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-top:10px; }}
.play-card {{ background:linear-gradient(180deg,#171012,#100B0D); border:1px solid {LINE}; border-top:2px solid rgba(239,0,31,.62); border-radius:8px; padding:13px; min-height:128px; }}
.play-k {{ color:#AAB4C3; font-size:calc(10px * var(--ui-scale)); font-weight:600; text-transform:uppercase; }}
.play-v {{ color:{INK}; font-size:calc(16px * var(--ui-scale)); font-weight:700; line-height:1.22; margin-top:7px; }}
.play-d {{ color:#A8B2C0; font-size:calc(11px * var(--ui-scale)); line-height:1.45; margin-top:8px; }}
.script-box {{ background:#0D1117; border:1px solid rgba(239,0,31,.28); border-left:4px solid {CDC_RED}; border-radius:8px; padding:13px; color:#F4F7FB; font-size:calc(15px * var(--ui-scale)); line-height:1.55; }}
.spec-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:10px 0 12px; }}
.spec-card {{ background:#100B0D; border:1px solid {LINE}; border-radius:8px; padding:12px; }}
.spec-k {{ color:#8F9AAD; font-size:calc(10px * var(--ui-scale)); font-weight:600; text-transform:uppercase; }}
.spec-v {{ color:#FFFFFF; font-size:calc(19px * var(--ui-scale)); font-weight:700; margin-top:5px; }}
.spec-d {{ color:#A8B2C0; font-size:calc(11px * var(--ui-scale)); line-height:1.35; margin-top:4px; }}
.compare-card {{ background:linear-gradient(135deg,#1B0E12,#101217); border:1px solid rgba(255,255,255,.10); border-left:4px solid {GOLD}; border-radius:8px; padding:13px; margin:10px 0; }}
.compare-title {{ color:#FFFFFF; font-size:calc(18px * var(--ui-scale)); font-weight:700; }}
.compare-body {{ color:#C9D3EA; font-size:calc(12px * var(--ui-scale)); line-height:1.55; margin-top:6px; max-width:980px; }}
.asset-img {{ width:100%; border-radius:8px; border:1px solid {LINE}; background:#FFFFFF; }}
@media (max-width: 1400px) {{
  .top-meta {{ display:none; }}
  .platform-title {{ font-size:16px; }}
  .kcc-lockup img {{ height:28px; }}
}}
@media (max-width: 860px) {{
  .care-grid {{ grid-template-columns:1fr; }}
  .grid4, .grid6, .sku-grid, .timeline, .playbook-grid, .spec-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
  .hero-signal-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); max-width:100%; }}
  .kcc-lockup {{ display:none; }}
  .hero-main {{ min-height:340px; }}
  .hero-content {{ flex-direction:column; align-items:flex-start; }}
  .h1 {{ font-size:34px; }}
}}
@media (max-width: 700px) {{
  .grid4, .grid6, .sku-grid, .timeline, .playbook-grid, .spec-grid {{ grid-template-columns:1fr; }}
  .hero-signal-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
  .topbar {{ min-height:58px; padding:9px 12px; }}
  .top-meta {{ display:none; }}
  .brand-lockup {{ flex-direction:row; align-items:center; text-align:left; gap:8px; }}
  .cdc-emblem {{ height:42px; width:58px; }}
  .platform-title {{ font-size:13px; }}
  .platform-sub {{ font-size:9px; }}
  .hero-main {{ min-height:360px; }}
  .hero-content {{ padding:18px 18px; }}
  .hero-brand-row {{ gap:10px; margin-bottom:12px; }}
  .h1 {{ font-size:28px; line-height:1.1; }}
  .h-sub {{ font-size:13px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"${value:,.0f}"


def pct_delta(series: pd.Series, periods: int = 1) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) <= periods or clean.iloc[-1 - periods] == 0:
        return 0.0
    return (clean.iloc[-1] - clean.iloc[-1 - periods]) / clean.iloc[-1 - periods] * 100


def amount_column(frame: pd.DataFrame, column: str) -> pd.Series:
    source = frame.get(column, pd.Series(0, index=frame.index))
    cleaned = source.astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)


@st.cache_data(ttl=3600)
def get_fred(series_id: str, label: str) -> pd.DataFrame:
    if not FRED_API_KEY:
        return pd.DataFrame()
    url = (
        "https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
        "&observation_start=2021-01-01"
    )
    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        rows = response.json().get("observations", [])
        frame = pd.DataFrame(rows)
        frame["date"] = pd.to_datetime(frame["date"])
        frame[label] = pd.to_numeric(frame["value"], errors="coerce")
        return frame[["date", label]].dropna()
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_freight() -> pd.DataFrame:
    path = os.path.join(APP_DIR, "freight_index_records.json")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            rows = json.load(handle)
        frame = pd.DataFrame(rows)
        frame["date"] = pd.to_datetime(frame["date"])
        return frame
    except Exception:
        return pd.DataFrame()


@st.cache_data
def purchase_index() -> pd.DataFrame:
    rows = [
        {"month": "2025-01", "PVC": 726.33, "DOTP": 1042.50},
        {"month": "2025-02", "PVC": 717.50, "DOTP": 1025.00},
        {"month": "2025-03", "PVC": 701.75, "DOTP": 1017.00},
        {"month": "2025-04", "PVC": 692.50, "DOTP": 993.75},
        {"month": "2025-05", "PVC": 692.50, "DOTP": 971.25},
        {"month": "2025-06", "PVC": 707.50, "DOTP": 990.00},
        {"month": "2025-07", "PVC": 701.25, "DOTP": 990.00},
        {"month": "2025-08", "PVC": 698.00, "DOTP": 970.00},
        {"month": "2025-09", "PVC": 703.00, "DOTP": 955.00},
        {"month": "2025-10", "PVC": 688.00, "DOTP": 908.33},
        {"month": "2025-11", "PVC": 671.25, "DOTP": 871.25},
        {"month": "2025-12", "PVC": 635.00, "DOTP": 914.00},
        {"month": "2026-01", "PVC": 652.50, "DOTP": 941.25},
        {"month": "2026-02", "PVC": 693.33, "DOTP": 970.00},
        {"month": "2026-03", "PVC": 907.69, "DOTP": 1110.00},
        {"month": "2026-04", "PVC": 1022.50, "DOTP": 1317.50},
        {"month": "2026-05", "PVC": 894.50, "DOTP": 1196.25},
        {"month": "2026-06", "PVC": 817.50, "DOTP": None},
    ]
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["month"] + "-01")
    return frame


def default_orders() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["1st", "Permagrain launch shipment", "04/04", "05/15-05/19", "12 CNTR", "Delivered", "Paid"],
            ["2nd", "Permagrain launch shipment", "04/25", "05/30", "6 CNTR", "Delivered", "Paid"],
            ["3rd", "Permagrain + handboard shipment", "05/20", "07/01", "7 CNTR", "Delivered", "Due on arrival (7d)"],
        ],
        columns=["Round", "Program", "ETD", "ETA", "Volume", "Status", "Payment"],
    )


def default_shipments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["1st", "JSBCV2603755", 4, "04/04", "05/15", "Cincinnati", "Delivered", "$119,700.00", "Paid", ""],
            ["1st", "JSBCV2603756", 4, "04/04", "05/19", "Cincinnati", "Delivered", "$119,700.00", "Paid", ""],
            ["1st", "JSBCV2603757", 4, "04/04", "05/15", "Cincinnati", "Delivered", "$119,700.00", "Paid", ""],
            ["2nd", "JSBDE2604764", 3, "04/25", "05/30", "Michigan", "Delivered", "$89,775.00", "Paid", ""],
            ["2nd", "JSBDE2604765", 3, "04/25", "05/30", "Michigan", "Delivered", "$89,775.00", "Paid", ""],
            ["3rd", "JSBCV2605758", 3, "05/20", "07/01", "Cincinnati", "Delivered", "$89,775.00", "Due on arrival (7d)", ""],
            ["3rd", "JSBCV2605759", 3, "05/20", "07/01", "Cincinnati", "Delivered", "$89,775.00", "Due on arrival (7d)", ""],
            ["3rd", "JSBCV2605760", 1, "05/20", "07/01", "Cincinnati", "Delivered", "$15,200.00", "Due on arrival (7d)", "Handboard (1,002 pcs)"],
        ],
        columns=["Round", "B/L No.", "Containers", "ETD", "ETA", "Destination", "Status", "Amount", "Payment", "Remarks"],
    )


def default_credit() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Shipment Status", "25 CNTR Delivered", "24 product containers + 1 handboard container"],
            ["Payment Status", "1st / 2nd Paid", "$538,650.00 paid for the first two shipment groups"],
            ["Arrival Payment", "3rd Due on Arrival (7d)", "$194,750.00 tied to the July 1 arrival shipment"],
            ["Sample Support", "Handboard Included", "1 container / 1,002 pcs handboard shipment included in the 3rd group"],
        ],
        columns=["Area", "Status", "Program Note"],
    )


def default_order_shipment_desk() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["1st", "JSBCV2603755", 4, "04/04", "05/15", "Cincinnati", "Delivered", "$119,700.00", "Paid", ""],
            ["1st", "JSBCV2603756", 4, "04/04", "05/19", "Cincinnati", "Delivered", "$119,700.00", "Paid", ""],
            ["1st", "JSBCV2603757", 4, "04/04", "05/15", "Cincinnati", "Delivered", "$119,700.00", "Paid", ""],
            ["2nd", "JSBDE2604764", 3, "04/25", "05/30", "Michigan", "Delivered", "$89,775.00", "Paid", ""],
            ["2nd", "JSBDE2604765", 3, "04/25", "05/30", "Michigan", "Delivered", "$89,775.00", "Paid", ""],
            ["3rd", "JSBCV2605758", 3, "05/20", "07/01", "Cincinnati", "Delivered", "$89,775.00", "Due on arrival (7d)", ""],
            ["3rd", "JSBCV2605759", 3, "05/20", "07/01", "Cincinnati", "Delivered", "$89,775.00", "Due on arrival (7d)", ""],
            ["3rd", "JSBCV2605760", 1, "05/20", "07/01", "Cincinnati", "Delivered", "$15,200.00", "Due on arrival (7d)", "Handboard (1,002 pcs)"],
        ],
        columns=["Round", "B/L No.", "Containers", "ETD", "ETA", "Destination", "Status", "Amount", "Payment", "Remarks"],
    )


def sku_readiness_rows() -> pd.DataFrame:
    launch_spec = '9" x 60" / 5.0 mm / 20 mil'
    return pd.DataFrame(
        [
            ["PG-101", "Confirmed", launch_spec, "Ready", "Ready", "In progress", "In progress", "85%"],
            ["PG-203", "Confirmed", launch_spec, "Ready", "Ready", "In progress", "In progress", "85%"],
            ["PG-304", "Confirmed", launch_spec, "Ready", "Ready", "Ready", "In progress", "90%"],
            ["PG-405", "Confirmed", launch_spec, "Review", "Ready", "In progress", "Pending", "70%"],
            ["PG-506", "Confirmed", launch_spec, "Review", "Ready", "In progress", "Pending", "70%"],
            ["PG-607", "Pending", launch_spec, "Pending", "Pending", "Pending", "Pending", "40%"],
        ],
        columns=["SKU", "Status", "Size / Spec", "Carton Artwork", "Label", "Hand Board", "1' Cut Sample", "Launch Readiness"],
    )


def next_30_days_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["This week", "Shipment snapshot review", "CDC can see where the launch program stands without asking first."],
            ["Next week", "Hand board arrival follow-up", "Keep showroom and sales-sample readiness moving."],
            ["July", "SKU launch prep", "Confirm artwork, labels, sample status, and launch sequence."],
            ["August", "Replenishment discussion", "Use first launch status to discuss the next order rhythm."],
            ["September", "2027 collection planning", "Open the path from Permagrain launch to broader CDC growth."],
        ],
        columns=["Timing", "Action", "Why It Matters"],
    )


def sku_rows() -> list[dict[str, str]]:
    return [
        {
            "code": "PG-101",
            "name": "Natural Reserve Oak",
            "look": "Warm natural oak with balanced grain movement.",
            "tags": ["Core", "Builder", "Warm Neutral"],
            "gradient": "linear-gradient(135deg,#C39967 0%,#E0C296 36%,#9C6D3F 64%,#D5B27F 100%)",
        },
        {
            "code": "PG-203",
            "name": "Coastal Sand Oak",
            "look": "Lighter coastal tone for clean showroom boards.",
            "tags": ["Light", "Retail", "Coastal"],
            "gradient": "linear-gradient(135deg,#D7C7A5 0%,#F0E2C5 42%,#BCA782 70%,#EADABB 100%)",
        },
        {
            "code": "PG-304",
            "name": "Urban Greige Oak",
            "look": "Gray-beige bridge color for modern multifamily jobs.",
            "tags": ["Greige", "Multi-Family", "Low Risk"],
            "gradient": "linear-gradient(135deg,#8C8B80 0%,#C8C4B6 34%,#77756E 65%,#DAD4C6 100%)",
        },
        {
            "code": "PG-405",
            "name": "Smoked Valley Oak",
            "look": "Medium smoke character with commercial durability cues.",
            "tags": ["Medium", "Commercial", "Texture"],
            "gradient": "linear-gradient(135deg,#7B6251 0%,#AE9277 42%,#594338 70%,#C1A68B 100%)",
        },
        {
            "code": "PG-506",
            "name": "Heritage Brown Oak",
            "look": "Traditional brown plank for replacement and dealer stock.",
            "tags": ["Brown", "Dealer Stock", "Classic"],
            "gradient": "linear-gradient(135deg,#6C4628 0%,#A87345 38%,#4E311E 68%,#BC8756 100%)",
        },
        {
            "code": "PG-607",
            "name": "Nordic Linen Oak",
            "look": "Soft pale oak designed for brighter interior palettes.",
            "tags": ["Pale Oak", "Design Trend", "Expansion"],
            "gradient": "linear-gradient(135deg,#E1D6BD 0%,#F5ECD8 40%,#CDBF9F 67%,#EFE4CD 100%)",
        },
    ]


def sales_pitch_cards() -> list[dict[str, str]]:
    return [
        {
            "k": "Lead proof",
            "v": "Longest Annealing System",
            "d": "Use this as the first manufacturing story: controlled stress relief for dimensional confidence.",
        },
        {
            "k": "LX switch story",
            "v": "Comparable stability, easier handling",
            "d": "Position KCC as a practical installer-friendly program, not just a replacement SKU.",
        },
        {
            "k": "Close line",
            "v": "A documented launch line CDC can sell with confidence",
            "d": "Back the pitch with certifications, slip data, surface design, ESG, and KCC manufacturing discipline.",
        },
    ]


def launch_spec_cards() -> list[dict[str, str]]:
    return [
        {"k": "Total thickness", "v": "5.0 mm", "d": "CDC launch construction"},
        {"k": "Wear layer", "v": "0.50 mm", "d": "20 mil commercial-ready story"},
        {"k": "Plank size", "v": '9" x 60"', "d": "Long plank residential + project appeal"},
        {"k": "Core message", "v": "Balanced", "d": "Stable, flexible, installer-friendly"},
    ]


def objection_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            [
                "Will it stay stable?",
                "Yes. Lead with KCC's Longest Annealing System and glass fiber reinforced construction.",
                "ASTM F2199 dimensional stability and curl PASS; EN ISO 23999 PASS.",
                "Builders, multifamily, temperature / humidity concerns.",
            ],
            [
                "Why move from LX?",
                "KCC gives CDC a similar stability story with a stronger workability and cutting story.",
                "Technical feedback: KCC is not overly rigid, so knife cutting can feel smoother.",
                "Dealer training, installer conversations, launch conversion.",
            ],
            [
                "Will installers waste material?",
                "The product is easier to cut and handle around stairs, walls, and tight finishing areas.",
                "Smoother cutting can reduce loss and support faster installation work.",
                "Project managers, installers, labor-sensitive jobs.",
            ],
            [
                "Will scratches stand out?",
                "Wood5 visuals help minor scratches look less noticeable in everyday use.",
                "Surface design advantage: scratch visibility is reduced by the wood visual structure.",
                "Retail showroom, family use, light commercial spaces.",
            ],
            [
                "Is it safe underfoot?",
                "Use the slip-resistance proof when the customer asks about active spaces.",
                "DIN 51130 R11 rating; EN slip resistance R9-R11 PASS; ASTM slip tests PASS.",
                "Healthcare, education, multifamily common areas, retail.",
            ],
            [
                "Can we support bids?",
                "Yes. The program has specification-ready product and system documentation.",
                "FloorScore, GREENGUARD Gold, CE, HPD v2.3, Carbon Footprint, ISO 9001, ISO 14001.",
                "Architects, designers, commercial bids, public projects.",
            ],
        ],
        columns=["Customer Objection", "How CDC Should Answer", "Proof To Use", "Best Sales Moment"],
    )


def competitive_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            [
                "Dimensional stability",
                "Keep the message balanced: stability is comparable, and KCC adds a strong process story.",
                "Longest Annealing System + ASTM F2199 / EN ISO 23999 PASS.",
            ],
            [
                "Flexibility / workability",
                "KCC should feel easier to cut and less overly rigid in real installation conditions.",
                "Technical feedback: smoother knife cutting can reduce loss at stairs, walls, and edge finishing.",
            ],
            [
                "Labor efficiency",
                "Cleaner handling can help installers work faster and reduce material waste.",
                "Use with contractors and project managers who care about labor time.",
            ],
            [
                "Surface appearance",
                "KCC's Wood5 visual helps minor scratches look less obvious.",
                "Use for retail floors, family homes, pets, and showroom demonstrations.",
            ],
            [
                "Color quality",
                "Surface color stability is a key KCC confidence point.",
                "Use when CDC wants a design-quality answer, not only a price answer.",
            ],
        ],
        columns=["CDC Question", "KCC Answer", "Proof / Sales Use"],
    )


def certification_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["FloorScore", "Product certification", "Indoor air quality confidence for flooring specifications."],
            ["GREENGUARD Gold", "Product certification", "Use with schools, healthcare, multifamily, and indoor-air-sensitive projects."],
            ["CE", "Product certification", "Supports international compliance language in project documentation."],
            ["HPD v2.3", "Product certification", "Use when architects or specifiers ask for material transparency."],
            ["Carbon Footprint", "Product certification", "Supports lower-carbon and responsible sourcing conversations."],
            ["ISO 9001", "System certification", "Quality management system credibility."],
            ["ISO 14001", "System certification", "Environmental management system credibility."],
            ["EcoVadis Platinum", "ESG rating", "Use for corporate, public, and large-project sustainability screening."],
        ],
        columns=["Badge", "Category", "How CDC Can Use It"],
    )


def four_re_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Recycle", "Materials prepared from plasticizers extracted from discarded PET bottles."],
            ["Reuse", "Method developed to reuse discarded plasticizers generated during sheet vinyl manufacturing."],
            ["Replacement", "Bio-mass material from corn stalks used as an alternative material for UV coating."],
            ["Reduce", "Development work to reduce petroleum-based chemical raw materials."],
        ],
        columns=["4Re Theme", "Bid / Project Message"],
    )


def local_file_bytes(file_name: str) -> bytes:
    path = os.path.join(APP_DIR, file_name)
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except Exception:
        return b""


def style_currency(frame: pd.DataFrame, columns: list[str]) -> pd.io.formats.style.Styler:
    return frame.style.format({column: "${:,.0f}" for column in columns})


PLOT_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": True,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "cdc_market_signal",
        "height": 720,
        "width": 1280,
        "scale": 2,
    },
}


def apply_chart_layout(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=56, b=18),
        title=dict(text=""),
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color="#DDE5F0"),
        colorway=["#F3D74B", "#EF001F", "#7AA7FF", "#4ADE80"],
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            x=0,
            font=dict(size=11, color="#DDE5F0"),
            bgcolor="rgba(20,16,17,.82)",
        ),
        xaxis=dict(showgrid=True, gridcolor="#2B1D22", zeroline=False, tickfont=dict(color="#9AA4B4"), showspikes=True, spikemode="across", spikesnap="cursor", spikecolor="#6B7280"),
        yaxis=dict(showgrid=True, gridcolor="#2B1D22", zeroline=False, tickfont=dict(color="#9AA4B4"), showspikes=True, spikecolor="#6B7280"),
    )
    return fig


def line_chart(frame: pd.DataFrame, y_cols: list[str], title: str, height: int = 250) -> go.Figure:
    fig = go.Figure()
    for col in y_cols:
        if col in frame:
            fig.add_trace(
                go.Scatter(
                    x=frame["date"],
                    y=frame[col],
                    mode="lines",
                    name=col,
                    line=dict(width=2.4),
                    hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.2f}<extra></extra>",
                )
            )
    return apply_chart_layout(fig, height)


def filter_years(frame: pd.DataFrame, years: int) -> pd.DataFrame:
    if frame.empty or "date" not in frame:
        return frame
    end_date = frame["date"].max()
    start_date = end_date - pd.DateOffset(years=years)
    return frame[frame["date"] >= start_date].copy()


def housing_mortgage_chart(housing_frame: pd.DataFrame, mortgage_frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    chart_start = None
    if not housing_frame.empty:
        housing_plot = filter_years(housing_frame, 5)
        chart_start = housing_plot["date"].min() if not housing_plot.empty else None
        fig.add_trace(
            go.Bar(
                x=housing_plot["date"],
                y=housing_plot["Housing Starts"],
                name="Housing Starts (K)",
                marker=dict(color="rgba(66,133,244,.72)"),
                hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.0f}K<extra></extra>",
                yaxis="y",
            )
        )
    if not mortgage_frame.empty:
        mortgage_plot = mortgage_frame.copy()
        if chart_start is not None:
            mortgage_plot = mortgage_plot[mortgage_plot["date"] >= chart_start]
        else:
            mortgage_plot = filter_years(mortgage_plot, 5)
        fig.add_trace(
            go.Scatter(
                x=mortgage_plot["date"],
                y=mortgage_plot["30Y Mortgage"],
                mode="lines",
                name="30Y Mortgage (%)",
                line=dict(color="#FF4D4F", width=2.6),
                hovertemplate="%{x|%Y-%m-%d}<br>%{y:.2f}%<extra></extra>",
                yaxis="y2",
            )
        )
    fig.update_layout(
        height=340,
        margin=dict(l=12, r=12, t=56, b=18),
        title=dict(text=""),
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color="#DDE5F0"),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            x=0,
            font=dict(size=11, color="#DDE5F0"),
            bgcolor="rgba(20,16,17,.82)",
        ),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#9AA4B4"), showspikes=True, spikemode="across", spikesnap="cursor", spikecolor="#6B7280"),
        yaxis=dict(title="", showgrid=True, gridcolor="#2B1D22", zeroline=False, tickfont=dict(color="#9AA4B4"), showspikes=True, spikecolor="#6B7280"),
        yaxis2=dict(title="", overlaying="y", side="right", showgrid=False, zeroline=False, tickfont=dict(color="#9AA4B4"), showspikes=True, spikecolor="#6B7280"),
    )
    return fig


def format_market_value(value: float, decimals: int = 0, suffix: str = "") -> str:
    if pd.isna(value):
        return "-"
    number = f"{value:,.{decimals}f}"
    return f"{number}{suffix}"


def pct_change(current: float, prior: float) -> str:
    if pd.isna(current) or pd.isna(prior) or prior == 0:
        return "-"
    change = (current - prior) / prior * 100
    color = "#4ADE80" if change >= 0 else "#FF6B6E"
    return f'<span style="color:{color};font-weight:700;">{change:+.1f}%</span>'


def market_summary_row(
    frame: pd.DataFrame,
    label: str,
    column: str,
    unit: str,
    decimals: int = 0,
    previous_periods: int = 1,
    year_periods: int = 12,
) -> list[str]:
    if frame.empty or column not in frame:
        return [label, unit, "-", "-", "-", "-", "-", "-"]
    clean = frame[["date", column]].dropna().copy()
    if clean.empty:
        return [label, unit, "-", "-", "-", "-", "-", "-"]
    current = float(clean[column].iloc[-1])
    previous = float(clean[column].iloc[-1 - previous_periods]) if len(clean) > previous_periods else float("nan")
    year_ago = float(clean[column].iloc[-1 - year_periods]) if len(clean) > year_periods else float("nan")
    latest_date = clean["date"].iloc[-1].strftime("%Y-%m-%d")
    return [
        label,
        unit,
        latest_date,
        format_market_value(current, decimals),
        format_market_value(previous, decimals),
        pct_change(current, previous),
        format_market_value(year_ago, decimals),
        pct_change(current, year_ago),
    ]


def render_table(frame: pd.DataFrame) -> None:
    html = frame.to_html(index=False, escape=False, classes="dark-data-table", border=0)
    st.markdown(f'<div class="dark-table-scroll">{html}</div>', unsafe_allow_html=True)


def render_play_cards(cards: list[dict[str, str]]) -> None:
    html = '<div class="playbook-grid">'
    for card in cards:
        html += f"""
<div class="play-card">
  <div class="play-k">{card['k']}</div>
  <div class="play-v">{card['v']}</div>
  <div class="play-d">{card['d']}</div>
</div>
"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_spec_cards(cards: list[dict[str, str]]) -> None:
    html = '<div class="spec-grid">'
    for card in cards:
        html += f"""
<div class="spec-card">
  <div class="spec-k">{card['k']}</div>
  <div class="spec-v">{card['v']}</div>
  <div class="spec-d">{card['d']}</div>
</div>
"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_asset_image(image: str, alt: str) -> None:
    if image:
        st.markdown(f'<img class="asset-img" src="data:image/png;base64,{image}" alt="{alt}">', unsafe_allow_html=True)


def create_customer_brief_pdf() -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError:
        lines = [
            "CDC Partner Portal - Permagrain Collection",
            f"Prepared {datetime.now().strftime('%Y-%m-%d %H:%M')} KST",
            "",
            "Customer Care Agenda",
            "- Orders: Launch orders and replenishment forecast",
            "- Logistics: Cincinnati / Michigan delivery and B/L visibility",
            "- Program capacity: account status and replenishment readiness",
            "- Market: Housing, freight, PVC/DOTP cost indicators",
            "- ESG: Manufacturing partner sustainability material for CDC sales use",
            "",
            "Suggested Message",
            "This portal gives CDC one secure workspace for Permagrain order visibility, shipment timing, launch readiness, market indicators, collection content, and ESG documents.",
        ]
        return simple_pdf_bytes(lines)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("CDC Partner Portal - Permagrain Collection", styles["Title"]),
        Spacer(1, 8),
        Paragraph(f"Prepared {datetime.now().strftime('%Y-%m-%d %H:%M')} KST", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Customer Care Agenda", styles["Heading2"]),
    ]
    care_rows = [
        ["Area", "Current Focus", "Next Action"],
        ["Orders", "Launch orders and replenishment forecast", "Confirm July/August replenishment timing"],
        ["Logistics", "Cincinnati / Michigan delivery and B/L visibility", "Share weekly delivery and payment follow-up status"],
        ["Program Capacity", "Account status is on track", "Keep replenishment path visible for growth"],
        ["Market", "Housing, freight, PVC/DOTP cost indicators", "Use as quote timing and promotion evidence"],
        ["ESG", "Manufacturing partner sustainability materials", "Support CDC's customer-facing sales narrative"],
    ]
    table = Table(care_rows, colWidths=[28 * mm, 72 * mm, 66 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(CDC_BLACK)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DDE4EE")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ]
        )
    )
    story.extend([table, Spacer(1, 14)])
    story.extend(
        [
            Paragraph("Suggested Message to CDC", styles["Heading2"]),
            Paragraph(
                "This portal gives CDC one secure workspace for Permagrain order visibility, shipment timing, "
                "launch readiness, market indicators, collection content, and ESG documents.",
                styles["BodyText"],
            ),
        ]
    )
    doc.build(story)
    return buffer.getvalue()


def simple_pdf_bytes(lines: list[str]) -> bytes:
    escaped_lines = [
        line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        for line in lines
    ]
    text_commands = ["BT", "/F1 16 Tf", "72 790 Td", f"({escaped_lines[0]}) Tj"]
    text_commands.extend(["/F1 10 Tf"])
    for line in escaped_lines[1:]:
        text_commands.append("0 -18 Td")
        text_commands.append(f"({line}) Tj")
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("latin-1", errors="replace")
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n" + stream + b"\nendstream endobj\n",
    ]
    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(output.tell())
        output.write(obj)
    xref = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.write(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return output.getvalue()


with st.sidebar:
    sidebar_logo = CDC_TAGLINE_LOGO or CDC_LOGO
    sidebar_cdc = f'<img class="sidebar-logo-main" src="data:image/png;base64,{sidebar_logo}" alt="CDC Distributors">' if sidebar_logo else ""
    st.markdown(
        f"""
<div class="sidebar-brand-block">
  {sidebar_cdc}
  <div class="side-brand">CDC PARTNER PORTAL</div>
  <div class="side-sub">Permagrain launch workspace<br>Managed with KCC Glass</div>
</div>
""",
        unsafe_allow_html=True,
    )
    view = st.radio(
        "Workspace",
        MENU_ITEMS,
        key="view",
        label_visibility="collapsed",
    )
    order_upload = None
    shipment_upload = None
    if CUSTOMER_SHARE_MODE:
        st.markdown('<div class="side-tool-label">Text Size</div>', unsafe_allow_html=True)
        st.radio(
            "Text Size",
            TEXT_SIZE_OPTIONS,
            key="text_size_mode",
            label_visibility="collapsed",
        )
    else:
        st.markdown("#### Data Mode")
        order_upload = st.file_uploader("Approved order data", type=["csv"], help="Optional: upload approved order data for this workspace.")
        shipment_upload = st.file_uploader("Approved shipment data", type=["csv"], help="Optional: upload approved shipment data for this workspace.")


try:
    orders = pd.read_csv(order_upload) if order_upload else default_orders()
except Exception:
    st.sidebar.warning("Order data could not be read. Standard review data is shown.")
    orders = default_orders()

try:
    shipments = pd.read_csv(shipment_upload) if shipment_upload else default_shipments()
except Exception:
    st.sidebar.warning("Shipment data could not be read. Standard review data is shown.")
    shipments = default_shipments()

credit = default_credit()
order_shipment = default_order_shipment_desk()
sku_readiness = sku_readiness_rows()
next_30_days = next_30_days_rows()
freight = load_freight()
purchase = purchase_index()
housing = get_fred("HOUST", "Housing Starts")
mortgage = get_fred("MORTGAGE30US", "30Y Mortgage")
new_home_sales = get_fred("HSN1F", "New Home Sales")
building_retail = get_fred("MRTSSM4441USN", "Building Materials Retail")
usdkrw = get_fred("DEXKOUS", "USD/KRW")

shipment_group_count = int(len(orders))
shipment_containers = pd.to_numeric(shipments.get("Containers", pd.Series(0, index=shipments.index)), errors="coerce").fillna(0)
shipment_amounts = amount_column(shipments, "Amount")
status_text = shipments.get("Status", pd.Series("", index=shipments.index)).astype(str)
payment_text = shipments.get("Payment", pd.Series("", index=shipments.index)).astype(str)
remarks_text = shipments.get("Remarks", pd.Series("", index=shipments.index)).astype(str)
delivered_mask = status_text.str.contains("delivered", case=False, na=False)
paid_mask = payment_text.str.fullmatch("Paid", case=False, na=False)
due_mask = payment_text.str.contains("due", case=False, na=False)
handboard_mask = remarks_text.str.contains("handboard", case=False, na=False)
shipment_container_total = int(shipment_containers.sum())
delivered_container_count = int(shipment_containers[delivered_mask].sum())
paid_container_count = int(shipment_containers[paid_mask].sum())
due_container_count = int(shipment_containers[due_mask].sum())
handboard_container_count = int(shipment_containers[handboard_mask].sum())
product_container_count = max(shipment_container_total - handboard_container_count, 0)
paid_amount = float(shipment_amounts[paid_mask].sum())
due_amount = float(shipment_amounts[due_mask].sum())
confirmed_skus = int((sku_readiness["Status"] == "Confirmed").sum())
pending_skus = int((sku_readiness["Status"] == "Pending").sum())
program_capacity = "Available"
scfi_now = float(freight["SCFI"].dropna().iloc[-1]) if not freight.empty else 0.0
scfi_delta = pct_delta(freight["SCFI"], 4) if not freight.empty else 0.0
pvc_now = float(purchase["PVC"].dropna().iloc[-1])
pvc_delta = pct_delta(purchase["PVC"])


cdc_emblem_image = CDC_TAGLINE_LOGO or image_b64("cdc_distributors_logo.png") or CDC_LOGO
cdc_emblem = f'<img class="cdc-emblem" src="data:image/png;base64,{cdc_emblem_image}" alt="CDC Distributors">' if cdc_emblem_image else '<strong>CDC</strong>'
kcc_partner = f'<img src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<strong>KCC GLASS</strong>"
hero_slides = "".join(
    f'<div class="hero-bg" style="background-image:url(\'data:image/png;base64,{image}\');"></div>'
    for image in CDC_HERO_IMAGES
    if image
)
data_chips = [
    ("SCFI", f"{scfi_now:,.0f}", "Source: freight index file"),
    ("PVC", f"{pvc_now:,.1f}", "Source: purchase index file"),
]
if not usdkrw.empty:
    usd_latest = float(usdkrw["USD/KRW"].dropna().iloc[-1])
    usd_date = pd.to_datetime(usdkrw["date"].dropna().iloc[-1]).strftime("%Y-%m-%d")
    data_chips.insert(0, ("USD/KRW", f"{usd_latest:,.0f}", f"As of {usd_date} · Source: FRED DEXKOUS"))

data_strip_html = "".join(
    f"""
<div class="data-chip">
  <div class="data-k">{label}</div>
  <div class="data-v">{value}</div>
  <div class="data-d">{detail}</div>
</div>
"""
    for label, value, detail in data_chips
)
st.markdown(f'<div class="data-strip">{data_strip_html}</div>', unsafe_allow_html=True)
ticker_items = [
    ("SCFI", f"{scfi_now:,.0f}", "freight index file"),
    ("PVC", f"{pvc_now:,.1f}", "purchase index file"),
]
dotp_clean = purchase["DOTP"].dropna() if "DOTP" in purchase else pd.Series(dtype=float)
if not dotp_clean.empty:
    ticker_items.append(("DOTP", f"{float(dotp_clean.iloc[-1]):,.1f}", "purchase index file"))
if not usdkrw.empty:
    usd_latest = float(usdkrw["USD/KRW"].dropna().iloc[-1])
    usd_date = pd.to_datetime(usdkrw["date"].dropna().iloc[-1]).strftime("%Y-%m-%d")
    ticker_items.insert(0, ("USD/KRW", f"{usd_latest:,.0f}", f"as of {usd_date} / FRED DEXKOUS"))
ticker_items.append(("SHIPMENT DATA", f"As of {SHIPMENT_AS_OF}", SHIPMENT_SOURCE))

market_html = "".join(
    f"""
<span class="market-item">
  <span class="market-dot"></span>
  <span class="market-label">{label}</span>
  <span class="market-value">{value}</span>
  <span class="market-source">{detail}</span>
</span>
"""
    for label, value, detail in ticker_items
)
st.markdown(f'<div class="market-marquee"><div class="market-track"><div class="market-set">{market_html}</div><div class="market-set">{market_html}</div></div></div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="topbar">
  <div class="brand-lockup">
    {cdc_emblem}
    <div class="platform-name">
      <div class="platform-title">CDC Partner Portal</div>
      <div class="platform-sub">Permagrain launch workspace</div>
    </div>
    <div class="kcc-lockup"><span>Managed with</span>{kcc_partner}</div>
  </div>
  <div class="top-meta">
    <div><div class="top-k">Company</div><div class="top-v">CDC Distributors</div></div>
    <div><div class="top-k">Partner</div><div class="top-v">KCC Glass</div></div>
    <div><div class="top-k">Collection</div><div class="top-v">Permagrain Collection</div></div>
    <div><div class="top-k">Shipment Data</div><div class="top-v">As of {SHIPMENT_AS_OF}</div></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

view = st.session_state.view


def render_hero() -> None:
    st.markdown(
        f"""
<div class="hero">
  <div class="hero-main">
    {hero_slides}
    <div class="hero-content">
      <div>
        <div class="eyebrow">CDC Distributors / Permagrain Collection</div>
        <div class="h1">CDC Partner Portal</div>
        <div class="h-sub">
          A secure launch workspace for shipment visibility, payment follow-up, SKU readiness,
          sales materials, and selected market indicators.
        </div>
      </div>
      <div class="hero-bottom">
        <div class="hero-actions">
          <span class="pill">Shipment desk</span>
          <span class="pill">SKU readiness</span>
          <span class="pill">Sales playbook</span>
          <span class="pill">Market signals</span>
        </div>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_metrics() -> None:
    st.markdown(
        f"""
<div class="grid4">
  <div class="metric"><div class="metric-k">Total Containers</div><div class="metric-v">{shipment_container_total}</div><div class="metric-c">{shipment_group_count} shipment groups delivered</div></div>
  <div class="metric"><div class="metric-k">Product / Handboard</div><div class="metric-v">{product_container_count}+{handboard_container_count}</div><div class="metric-c">Product CNTR + handboard support</div></div>
  <div class="metric"><div class="metric-k">Delivery Status</div><div class="metric-v">Delivered</div><div class="metric-c">{delivered_container_count} CNTR delivery confirmed</div></div>
  <div class="metric"><div class="metric-k">Payment Follow-Up</div><div class="metric-v">{money(due_amount)}</div><div class="metric-c">{paid_container_count} CNTR paid / {due_container_count} CNTR due</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_overview_metrics() -> None:
    st.markdown(
        f"""
<div class="grid6">
  <div class="metric"><div class="metric-k">Account Health</div><div class="metric-v">Green</div><div class="metric-c">Launch account under active care</div></div>
  <div class="metric"><div class="metric-k">Total Containers</div><div class="metric-v">{shipment_container_total}</div><div class="metric-c">{product_container_count} product + {handboard_container_count} handboard</div></div>
  <div class="metric"><div class="metric-k">Delivered Containers</div><div class="metric-v">{delivered_container_count}</div><div class="metric-c">Cincinnati and Michigan lanes</div></div>
  <div class="metric"><div class="metric-k">Payment Status</div><div class="metric-v">{paid_container_count} Paid</div><div class="metric-c">{due_container_count} CNTR due on arrival (7d)</div></div>
  <div class="metric"><div class="metric-k">Payment Follow-Up</div><div class="metric-v">{money(due_amount)}</div><div class="metric-c">{money(paid_amount)} already paid</div></div>
  <div class="metric"><div class="metric-k">Launch SKUs</div><div class="metric-v">{confirmed_skus}+{pending_skus}</div><div class="metric-c">Confirmed + pending</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_next_action() -> None:
    st.markdown(
        f"""
<div class="next-action">
  <div class="next-action-k">Next Action</div>
  <div class="next-action-v">Confirm 3rd shipment payment window and handboard readiness</div>
  <div class="next-action-d">1st and 2nd shipment groups are paid; the 3rd group was delivered on July 1 with {due_container_count} CNTR due on arrival (7d), including the 1,002 pcs handboard support.</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_30_day_timeline() -> None:
    cards = []
    for _, row in next_30_days.iterrows():
        cards.append(
            f"""
<div class="step">
  <div class="step-k">{row['Timing']}</div>
  <div class="step-v">{row['Action']}</div>
  <div class="step-d">{row['Why It Matters']}</div>
</div>
"""
        )
    st.markdown('<div class="timeline">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def panel(title: str, meta: str = "") -> None:
    st.markdown(
        f'<div class="panel"><div class="panel-h"><div class="panel-t">{title}</div><div class="panel-m">{meta}</div></div><div class="panel-b">',
        unsafe_allow_html=True,
    )


def close_panel() -> None:
    st.markdown("</div></div>", unsafe_allow_html=True)


if view == "Account Overview":
    render_hero()
    render_overview_metrics()
    render_next_action()
    left, right = st.columns([1.05, 0.95])
    with left:
        panel("Account Overview", f"As of {SHIPMENT_AS_OF} · Source: {SHIPMENT_SOURCE}")
        st.markdown(
            """
<div class="brief">
  This view summarizes the current Permagrain launch status: delivered containers, handboard support,
  payment follow-up, next action, and the next 30-day operating plan.
</div>
""",
            unsafe_allow_html=True,
        )
        render_table(credit)
        close_panel()
    with right:
        panel("Next 30 Days", "operating plan")
        render_table(next_30_days)
        close_panel()

    panel("Program Summary", "customer view")
    st.markdown(
        """
<div class="brief">
  This portal gives CDC one place to review the Permagrain program, shipment movement,
  sample readiness, market indicators, and sales-ready support material. The purpose is simple:
  clearer weekly visibility and smoother launch execution.
</div>
""",
        unsafe_allow_html=True,
    )
    close_panel()

elif view == "Order & Shipment Desk":
    render_metrics()
    panel("B/L-Level Shipment Desk", f"As of {SHIPMENT_AS_OF} · Source: {SHIPMENT_SOURCE}")
    st.markdown(
        """
<div class="brief">
  This is the most practical customer-care view for CDC and AJ: each B/L line shows container count,
  destination, delivery status, payment status, and the handboard note tied to the 3rd shipment group.
</div>
""",
        unsafe_allow_html=True,
    )
    render_table(order_shipment)
    st.download_button(
        "Download order & shipment desk",
        order_shipment.to_csv(index=False).encode("utf-8-sig"),
        "CDC_Order_Shipment_Desk.csv",
        "text/csv",
        width="stretch",
    )
    close_panel()

    panel("Shipment Group Summary", f"As of {SHIPMENT_AS_OF}")
    render_table(orders)
    close_panel()

elif view == "Permagrain SKU Room":
    panel("Permagrain SKU Room", "confirmed / pending / launch readiness")
    st.markdown(
        f"""
<div class="brief">
  Use this section as CDC's launch-room view: confirmed SKUs, pending SKU, specs, carton artwork,
  label, hand board, 1' cut sample, and launch readiness.
</div>
""",
        unsafe_allow_html=True,
    )
    render_table(sku_readiness)
    close_panel()

    panel("Permagrain Design View", "6 launch visuals")
    sku_html = '<div class="sku-grid">'
    for item in sku_rows():
        tags = "".join(f'<span class="tag">{tag}</span>' for tag in item["tags"])
        sku_html += f"""
<div class="sku">
  <div class="swatch" style="background:{item['gradient']};"></div>
  <div class="sku-body">
    <div class="sku-code">{item['code']}</div>
    <div class="sku-name">{item['name']}</div>
    <div class="sku-copy">{item['look']}</div>
    <div class="tagline">{tags}</div>
  </div>
</div>
"""
    sku_html += "</div>"
    st.markdown(sku_html, unsafe_allow_html=True)
    close_panel()

    panel("Sales Enablement Notes", "dealer-ready positioning")
    notes = pd.DataFrame(
        [
            ["Builder / Multi-family", "PG-304, PG-405", "Neutral tones and controlled pattern variation lower selection risk."],
            ["Retail showroom", "PG-101, PG-203, PG-607", "Clear light-to-warm good/better/best storytelling."],
            ["Replacement market", "PG-506, PG-101", "Traditional oak visuals with dependable stock logic."],
            ["Expansion path", "Add stone visual / wider plank / herringbone accent", "Use CDC launch performance to justify next collection."],
        ],
        columns=["Use Case", "Hero SKUs", "How CDC Can Use It"],
    )
    render_table(notes)
    close_panel()

elif view == "Sales Playbook":
    panel("CDC Sales Playbook", "how to sell Permagrain")
    render_spec_cards(launch_spec_cards())
    st.markdown(
        """
<div class="script-box">
  <b>Say this first:</b> Permagrain is CDC's 5.0 mm / 20 mil / 9" x 60" KCC Glass LVT launch program.
  Lead with the Longest Annealing System, balanced core handling, smoother cutting workability, Wood5 scratch visibility,
  and project-ready certification support.
</div>
""",
        unsafe_allow_html=True,
    )
    render_play_cards(sales_pitch_cards())
    close_panel()

    panel("KCC vs LX Sales Answer", "what CDC reps can say")
    st.markdown(
        """
<div class="compare-card">
  <div class="compare-title">Do not attack LX. Position KCC as the easier program to sell and install.</div>
  <div class="compare-body">
    The clean message is: comparable dimensional stability, stronger KCC process story, smoother cutting,
    lower installation loss risk around difficult areas, and surface visuals that help minor scratches look less obvious.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    competitive_table = competitive_rows()
    render_table(competitive_table)
    st.download_button(
        "Download KCC vs LX sales answer",
        competitive_table.to_csv(index=False).encode("utf-8-sig"),
        "CDC_KCC_vs_LX_Sales_Answer.csv",
        "text/csv",
        width="stretch",
    )
    close_panel()

    panel("Objection-Handling Cards", "customer concern -> proof -> sales moment")
    objection_table = objection_rows()
    render_table(objection_table)
    st.download_button(
        "Download objection-handling sheet",
        objection_table.to_csv(index=False).encode("utf-8-sig"),
        "CDC_Permagrain_Objection_Handling.csv",
        "text/csv",
        width="stretch",
    )
    close_panel()

    c1, c2 = st.columns([1.05, 0.95])
    with c1:
        panel("Certification Badge Library", "proposal-ready proof points")
        render_asset_image(KCC_CERT_BADGES, "KCC Glass certification badges")
        badge_table = certification_rows()
        render_table(badge_table)
        cert_bytes = local_file_bytes("kcc_certification_badges.png")
        if cert_bytes:
            st.download_button(
                "Download certification badge strip",
                cert_bytes,
                "KCC_Glass_Certification_Badges.png",
                "image/png",
                width="stretch",
            )
        st.download_button(
            "Download badge usage matrix",
            badge_table.to_csv(index=False).encode("utf-8-sig"),
            "KCC_Glass_Certification_Badge_Usage.csv",
            "text/csv",
            width="stretch",
        )
        close_panel()
    with c2:
        panel("30-Second Selling Points", "copy-ready scripts")
        scripts = pd.DataFrame(
            [
                ["Builder / multifamily", "Lead with dimensional stability, Longest Annealing, and installer-friendly handling."],
                ["Retail dealer", "Lead with 5.0 mm / 20 mil / 9 x 60, Wood5 scratch visibility, and a managed launch program."],
                ["Commercial / public bid", "Lead with FloorScore, GREENGUARD Gold, HPD, ISO systems, and ESG / 4Re support."],
                ["Installer conversation", "Lead with smoother cutting, less over-rigid handling, and lower loss risk at stairs and walls."],
            ],
            columns=["Audience", "Tell Them This"],
        )
        render_table(scripts)
        st.markdown(
            """
<div class="meaning"><b>Customer line:</b> This is not only a color launch. It is a documented LVT program CDC can sell into residential, commercial, and specification-driven accounts.</div>
""",
            unsafe_allow_html=True,
        )
        close_panel()

    c3, c4 = st.columns([1, 1])
    with c3:
        panel("ESG / 4Re Section", "large project and bid support")
        render_asset_image(KCC_4RE_IMAGE, "KCC Glass 4Re eco friendly solutions")
        render_table(four_re_rows())
        esg_img = local_file_bytes("kcc_4re_solution.png")
        if esg_img:
            st.download_button(
                "Download 4Re visual",
                esg_img,
                "KCC_Glass_4Re_Solution.png",
                "image/png",
                width="stretch",
            )
        close_panel()
    with c4:
        panel("Longest Annealing System", "manufacturing proof story")
        annealing_rows = pd.DataFrame(
            [
                ["Customer Concern", "Will this LVT stay stable after installation?"],
                ["Sales Answer", "KCC uses the Longest Annealing System as a process story for controlled stress relief."],
                ["Proof", "Dimensional stability / curl PASS under ASTM F2199 and EN ISO 23999."],
                ["Best Use", "Builders, multifamily projects, replacement work, and customers comparing KCC against LX."],
            ],
            columns=["Area", "Message"],
        )
        st.markdown(
            """
<div class="meaning"><b>Customer line:</b> KCC does not rely only on a test result. The manufacturing process itself is part of the stability story.</div>
""",
            unsafe_allow_html=True,
        )
        render_table(annealing_rows)
        close_panel()

    panel("Source Material", "brochure download")
    brochure_bytes = local_file_bytes(KCC_BROCHURE_FILE)
    if brochure_bytes:
        st.download_button(
            "Download KCC Glass LVT brochure",
            brochure_bytes,
            "KCC_Glass_LVT_Blue_Brochure_2026.pdf",
            "application/pdf",
            width="stretch",
        )
    else:
        st.info("Brochure file is not available in this deployment package yet.")
    close_panel()

elif view == "Market Signal for CDC":
    panel("Market Signal for CDC", MARKET_SOURCE)
    st.markdown(
        """
<div class="brief">
  These indicators are provided for launch timing, replenishment planning, pricing discussion,
  and sales planning. External data panels appear only when source data is available.
</div>
""",
        unsafe_allow_html=True,
    )
    signal_data = [
        ["SCFI", f"Latest SCFI {scfi_now:,.0f}, 4-week change {scfi_delta:+.1f}%.", "If freight is rising, CDC may benefit from earlier replenishment planning."],
        ["PVC / DOTP", f"PVC purchase index {pvc_now:,.1f}, MoM {pvc_delta:+.1f}%.", "Raw-material pressure should be watched before the next large forecast discussion."],
    ]
    if not usdkrw.empty:
        signal_data.insert(0, ["USD/KRW", "FX movement affects quote timing and landed-cost confidence.", "Use a clear quote validity window when FX is moving quickly."])
    if not housing.empty or not new_home_sales.empty:
        signal_data.append(["U.S. Housing Signal", "Housing starts and new-home sales indicate flooring demand backdrop.", "Use demand signals to decide whether to push builder-oriented SKUs first."])
    if not mortgage.empty:
        signal_data.append(["Mortgage", "Mortgage rates influence new-home and remodeling sentiment.", "If rates remain high, keep the assortment practical and low-risk for dealers."])
    signal_rows = pd.DataFrame(
        signal_data,
        columns=["Signal", "Current Read", "What this means for CDC"],
    )
    render_table(signal_rows)
    st.markdown(
        """
<div class="meaning"><b>What this means for CDC:</b> Permagrain should be managed with weekly shipment visibility, practical SKU prioritization, and early replenishment discussion when freight or raw-material signals begin to move.</div>
""",
        unsafe_allow_html=True,
    )
    close_panel()

    if not usdkrw.empty:
        panel("USD/KRW Exchange Rate Trend", "Source: FRED DEXKOUS")
        fx_window = st.radio(
            "USD/KRW period",
            ["1Y", "3Y", "5Y"],
            horizontal=True,
            label_visibility="collapsed",
            key="usdkrw_window",
        )
        fx_years = {"1Y": 1, "3Y": 3, "5Y": 5}[fx_window]
        fx_frame = filter_years(usdkrw, fx_years)
        st.plotly_chart(line_chart(fx_frame, ["USD/KRW"], "USD/KRW Exchange Rate", height=330), width="stretch", config=PLOT_CONFIG)
        fx_summary = pd.DataFrame(
            [
                market_summary_row(usdkrw, "USD/KRW", "USD/KRW", "KRW", 0, 20, 252),
            ],
            columns=["Indicator", "Unit", "Latest", "Current", "20D Prior", "20D Change", "1Y Prior", "YoY"],
        )
        render_table(fx_summary)
        close_panel()

    if not housing.empty or not mortgage.empty:
        panel("US Housing & Mortgage Rate", "Source: FRED")
        st.plotly_chart(housing_mortgage_chart(housing, mortgage), width="stretch", config=PLOT_CONFIG)
        housing_summary = pd.DataFrame(
            [
                market_summary_row(housing, "Housing Starts", "Housing Starts", "K", 0, 1, 12),
                market_summary_row(new_home_sales, "New Home Sales", "New Home Sales", "K", 0, 1, 12),
                market_summary_row(mortgage, "30Y Mortgage", "30Y Mortgage", "%", 2, 4, 52),
            ],
            columns=["Indicator", "Unit", "Latest", "Current", "Prior", "Prior Change", "Year Ago", "YoY"],
        )
        render_table(housing_summary)
        close_panel()

    c1, c2 = st.columns(2)
    with c1:
        panel("Freight Index Watch", "SCFI / CCFI")
        if not freight.empty:
            st.plotly_chart(line_chart(freight.tail(80), ["SCFI", "CCFI"], "Container Freight Indices", height=310), width="stretch", config=PLOT_CONFIG)
            freight_summary = pd.DataFrame(
                [
                    market_summary_row(freight, "SCFI", "SCFI", "Index", 0, 4, 52),
                    market_summary_row(freight, "CCFI", "CCFI", "Index", 0, 4, 52),
                ],
                columns=["Indicator", "Unit", "Latest", "Current", "4W Prior", "4W Change", "Year Ago", "YoY"],
            )
            render_table(freight_summary)
        close_panel()
    with c2:
        panel("PVC / DOTP Cost Watch", "purchase reference")
        st.plotly_chart(line_chart(purchase, ["PVC", "DOTP"], "PVC / DOTP Purchase Index", height=310), width="stretch", config=PLOT_CONFIG)
        raw_material_summary = pd.DataFrame(
            [
                market_summary_row(purchase, "PVC", "PVC", "Index", 1, 1, 12),
                market_summary_row(purchase, "DOTP", "DOTP", "Index", 1, 1, 12),
            ],
            columns=["Indicator", "Unit", "Latest", "Current", "Prior", "Prior Change", "Year Ago", "YoY"],
        )
        render_table(raw_material_summary)
        close_panel()

    if not building_retail.empty:
        panel("Retail Demand Pulse", "Source: FRED")
        st.plotly_chart(line_chart(building_retail.tail(48), ["Building Materials Retail"], "Building Materials & Garden Retail Sales", height=300), width="stretch", config=PLOT_CONFIG)
        retail_summary = pd.DataFrame(
            [
                market_summary_row(building_retail, "Building Materials Retail", "Building Materials Retail", "USD MM", 0, 1, 12),
            ],
            columns=["Indicator", "Unit", "Latest", "Current", "Prior", "Prior Change", "Year Ago", "YoY"],
        )
        render_table(retail_summary)
        close_panel()

elif view == "Next 30 Days":
    panel("Next 30 Days", "operating plan")
    st.markdown(
        """
<div class="brief">
  This plan shows the next operating steps for the Permagrain launch program and keeps
  shipment, sample, replenishment, and collection-planning conversations aligned.
</div>
""",
        unsafe_allow_html=True,
    )
    render_30_day_timeline()
    close_panel()

    panel("30-Day Action Table", "customer operating view")
    render_table(next_30_days)
    close_panel()

elif view == "ESG & Growth Kit":
    c1, c2 = st.columns([1, 1])
    with c1:
        panel("ESG Report Room", "customer-facing source links")
        st.markdown(
            f"""
<div class="brief">
  CDC can use manufacturing partner ESG material as a credibility layer for builders, commercial accounts,
  and dealers asking about responsible supply chains, quality discipline, and long-term vendor stability.
</div>
<br>
<a class="link-btn" href="{KCC_ESG_EN}" target="_blank" rel="noopener noreferrer">Open English ESG Page</a>
<a class="link-btn secondary" href="{KCC_ESG_KO}" target="_blank" rel="noopener noreferrer">Korean ESG Archive</a>
""",
            unsafe_allow_html=True,
        )
        close_panel()

        panel("ESG Talking Points for CDC", "sales-ready")
        esg = pd.DataFrame(
            [
                ["Supply stability", "Position the manufacturing partner as disciplined and stable, not only price-driven."],
                ["Responsible sourcing", "Use in commercial bids where vendor governance and documentation matter."],
                ["Quality management", "Connect ESG governance with consistent product and service standards."],
                ["Long-term partnership", "Frame Permagrain as a managed growth program, not a one-time launch."],
            ],
            columns=["Theme", "CDC Sales Use"],
        )
        render_table(esg)
        close_panel()
    with c2:
        panel("Growth Roadmap", "future program planning")
        roadmap = pd.DataFrame(
            [
                ["Phase 1", "Launch Readiness", "Confirm first SKUs, weekly service visibility, and clean issue response"],
                ["Phase 2", "Replenishment Planning", "Use sell-through and shipment timing to plan the next order cycle"],
                ["Phase 3", "Collection Expansion", "Review additional colorways, formats, or adjacent LVT programs"],
                ["Phase 4", "Joint Planning", "Quarterly review, shared forecast view, and customer-ready support assets"],
            ],
            columns=["Phase", "Focus", "What It Means"],
        )
        render_table(roadmap)
        close_panel()

        panel("What to Ask CDC Next", "conversation prompts")
        st.markdown(
            """
<div class="brief">
  1. Which three Permagrain colors are your sales team showing first?<br>
  2. Which port and lane are most sensitive for your replenishment plan?<br>
  3. Do your builder or commercial customers ask for ESG/vendor documentation?<br>
  4. What would make the next collection expansion easiest for CDC to commit to?
</div>
""",
            unsafe_allow_html=True,
        )
        close_panel()

st.markdown(
    '<div class="note">CDC Partner Portal · Permagrain Collection · Managed with KCC Glass.</div>',
    unsafe_allow_html=True,
)
