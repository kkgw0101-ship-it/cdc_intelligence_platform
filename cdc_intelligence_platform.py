"""
CDC Intelligence Platform
Customer-facing Streamlit portal concept for CDC / Timeless Designs Flooring.
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
CDC_GOLD = "#F3D74B"
TIMELESS_BURGUNDY = "#6A2028"
TIMELESS_GOLD = "#D7A85C"
PARTNER_NAVY = "#0E2372"
NAVY = "#13070A"
GOLD = "#F3D74B"
INK = "#F4F7FB"
MIST = "#080506"
PANEL = "#141011"
PANEL2 = "#1D1215"
LINE = "#332024"
GREEN = "#0E9F6E"
RED = "#D64545"
ORANGE = "#C77800"
CUSTOMER_SHARE_MODE = True

PAGE_ICON = os.path.join(APP_DIR, "cdc_distributors_logo.png")
if not os.path.exists(PAGE_ICON):
    PAGE_ICON = "CDC"

st.set_page_config(
    page_title="CDC Intelligence Platform | Permagrain",
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_secret(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, os.environ.get(name, default))
    except Exception:
        return os.environ.get(name, default)


def image_b64(file_name: str) -> str:
    path = os.path.join(APP_DIR, file_name)
    try:
        with open(path, "rb") as handle:
            return base64.b64encode(handle.read()).decode("utf-8")
    except Exception:
        return ""


CDC_LOGO = image_b64("cdc_logo_horizontal.png") or image_b64("cdc_distributors_logo_crop.png") or image_b64("cdc_distributors_logo.png")
CDC_TAGLINE_LOGO = image_b64("cdc_logo_tagline_mark.png")
TIMELESS_LOGO = image_b64("timeless_designs_logo_crop.png") or image_b64("timeless_designs_logo.png")
KCC_LOGO_WHITE = image_b64("logo_white_t.png")
KCC_VIDEO_THUMB = image_b64("kcc_company_video_thumb.jpg")
CDC_HERO_IMAGES = [
    image_b64("cdc_hero_facility_aerial.png"),
    image_b64("cdc_hero_facility_parking.png"),
    image_b64("cdc_hero_facility_exterior.png"),
    image_b64("cdc_hero_team_event.png"),
]
FRED_API_KEY = get_secret("FRED_API_KEY", "")

TIMELESS_URL = "https://www.timelessdesignsflooring.com/"
KCC_ESG_EN = "https://www.kccglass.co.kr/eng/esgManagement/about/report.do"
KCC_ESG_KO = "https://www.kccglass.co.kr/esgManagement/about/report.do"
MENU_ITEMS = ["Account Overview", "Order & Shipment Desk", "Permagrain SKU Room", "Market Signal for CDC", "Next 30 Days", "ESG & Growth Kit"]

if "view" not in st.session_state:
    st.session_state.view = MENU_ITEMS[0]


st.markdown(
    f"""
<style>
[data-testid="stAppViewContainer"] {{ background:{MIST}; color:{INK}; }}
[data-testid="stHeader"] {{ background:transparent; height:0; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility:hidden; }}

/* Fixed terminal sidebar */
[data-testid="stSidebarCollapsedControl"] {{
  display:none !important;
}}
[data-testid="stSidebarCollapseButton"] {{
  display:none !important;
}}
[data-testid="stSidebar"] {{ transform:none !important; visibility:visible !important; min-width:230px !important; width:230px !important; background:linear-gradient(180deg,#1A070A 0%,#11080A 58%,#070506 100%); border-right:1px solid rgba(239,0,31,.36); }}
[data-testid="stSidebar"][aria-expanded="false"] {{ margin-left:0 !important; }}
[data-testid="stMain"] {{ left:230px !important; width:calc(100% - 230px) !important; }}
.block-container {{ padding:0.75rem 1.2rem 2rem 1.2rem; max-width:100%; width:100% !important; }}
* {{ font-variant-numeric: tabular-nums; letter-spacing:0; }}
[data-testid="stSidebar"] * {{ color:#FFFFFF !important; }}
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button {{
  background:rgba(255,255,255,.06) !important; border:1px solid rgba(255,255,255,.10) !important;
  color:#fff !important; border-radius:7px !important; min-height:34px !important;
}}
.side-brand {{ font-weight:900; font-size:15px; letter-spacing:1.4px; margin:2px 0 4px; }}
.side-sub {{ color:#D9BFC3 !important; font-size:11px; line-height:1.45; padding-bottom:14px; border-bottom:1px solid rgba(243,215,75,.22); margin-bottom:14px; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding:8px 10px; border-radius:7px; margin:2px 0; font-size:13px; transition:background .15s; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background:rgba(239,0,31,.16); }}
.sb-nav-label {{ color:#D9BFC3 !important; font-size:10px; font-weight:900; letter-spacing:.8px; text-transform:uppercase; margin:14px 0 6px 0; }}
.sidebar-logo {{ width:96px; max-width:100%; background:#050505; border-radius:7px; padding:5px; margin-bottom:10px; border:1px solid rgba(243,215,75,.34); }}
.market-marquee {{ height:32px; overflow:hidden; background:#090405; border:1px solid {LINE}; border-radius:8px; margin-bottom:10px; display:flex; align-items:center; box-shadow:0 12px 28px rgba(0,0,0,.20); }}
.market-track {{ display:flex; width:max-content; animation:marketFlow 42s linear infinite; }}
.market-set {{ display:flex; align-items:center; flex-shrink:0; min-width:max-content; }}
.market-item {{ display:inline-flex; align-items:center; gap:8px; padding:0 22px; color:#E4E9F0; font-size:12px; font-weight:900; white-space:nowrap; font-family:Consolas, monospace; }}
.market-dot {{ width:5px; height:5px; border-radius:50%; background:rgba(255,255,255,.74); display:inline-block; }}
.market-label {{ color:#A79296; font-weight:900; text-transform:uppercase; }}
.market-up {{ color:#4ADE80; }}
.market-dn {{ color:#FF6B6E; }}
@keyframes marketFlow {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}
.topbar {{
  display:flex; align-items:center; justify-content:space-between; gap:18px;
  background:linear-gradient(90deg,#090405 0%,#16080B 48%,#2B0B10 100%); color:#fff; border-bottom:2px solid {GOLD};
  border-top:1px solid rgba(239,0,31,.55);
  border-radius:8px; padding:12px 18px; margin-bottom:12px;
  box-shadow:0 18px 50px rgba(0,0,0,.24);
}}
.brand-lockup {{ display:flex; align-items:center; gap:14px; min-width:0; }}
.cdc-mark {{ height:58px; width:210px; object-fit:contain; background:#FFFFFF; border-radius:7px; padding:8px 12px; }}
.timeless-mark {{ height:44px; width:172px; object-fit:contain; background:#FFFFFF; border-radius:7px; padding:7px 10px; }}
.partner-mark {{ display:flex; align-items:center; gap:8px; color:#E9D6B5; font-size:10px; font-weight:900; text-transform:uppercase; }}
.partner-mark img {{ height:18px; width:auto; background:{PARTNER_NAVY}; border-radius:4px; padding:4px 6px; }}
.top-meta {{ display:flex; gap:22px; align-items:center; text-align:right; }}
.top-k {{ font-size:9px; color:#D9BFC3; text-transform:uppercase; font-weight:800; }}
.top-v {{ font-size:13px; color:#fff; font-weight:900; font-family:Consolas, monospace; }}
.stButton button {{
  border-radius:7px !important; min-height:36px !important; font-weight:900 !important;
  white-space:normal !important; line-height:1.15 !important;
}}
.hero {{ margin-bottom:14px; }}
.hero-main {{
  position:relative; min-height:640px; border-radius:14px; overflow:hidden;
  background:#12070A;
  border:1px solid {LINE}; box-shadow:0 24px 80px rgba(0,0,0,.32);
}}
.hero-bg {{
  position:absolute; inset:0; z-index:0; background-size:cover; background-position:center;
  opacity:0; transform:scale(1.045); animation:cdcHeroFade 28s infinite;
}}
.hero-bg:nth-child(1) {{ animation-delay:0s; }}
.hero-bg:nth-child(2) {{ animation-delay:7s; }}
.hero-bg:nth-child(3) {{ animation-delay:14s; }}
.hero-bg:nth-child(4) {{ animation-delay:21s; }}
.hero-main::before {{
  content:""; position:absolute; inset:0; z-index:0; pointer-events:none;
  background:
    radial-gradient(circle at 84% 14%, rgba(243,215,75,.17), transparent 30%),
    linear-gradient(90deg, rgba(7,4,5,.96) 0%, rgba(17,7,9,.82) 38%, rgba(17,7,9,.44) 70%, rgba(7,4,5,.22) 100%);
}}
.hero-main::after {{
  content:""; position:absolute; inset:-35%; z-index:0;
  background:linear-gradient(115deg,transparent 0%,rgba(255,255,255,.00) 42%,rgba(243,215,75,.15) 48%,rgba(255,255,255,.18) 51%,rgba(243,215,75,.08) 55%,transparent 62%);
  transform:translateX(-55%); pointer-events:none; animation:cdcShine 8s ease-in-out infinite;
}}
@keyframes cdcHeroFade {{
  0% {{ opacity:0; transform:scale(1.045); }}
  5% {{ opacity:1; }}
  25% {{ opacity:1; transform:scale(1.015); }}
  32% {{ opacity:0; }}
  100% {{ opacity:0; transform:scale(1.045); }}
}}
@keyframes cdcShine {{
  0%, 38% {{ transform:translateX(-55%); opacity:0; }}
  52% {{ opacity:1; }}
  70%, 100% {{ transform:translateX(55%); opacity:0; }}
}}
.hero-content {{ position:absolute; inset:0; z-index:1; padding:54px 62px; display:flex; flex-direction:column; justify-content:space-between; }}
.hero-brand-row {{ display:flex; align-items:center; gap:16px; margin-bottom:18px; }}
.hero-cdc-logo {{ height:76px; width:260px; object-fit:contain; background:#FFFFFF; border-radius:8px; padding:10px 14px; border:1px solid rgba(243,215,75,.30); }}
.hero-timeless-logo {{ height:62px; width:230px; object-fit:contain; background:#fff; border-radius:8px; padding:8px 12px; }}
.eyebrow {{ color:{GOLD}; font-size:13px; text-transform:uppercase; font-weight:900; letter-spacing:3px; }}
.h1 {{ color:#fff; font-size:54px; line-height:1.04; font-weight:900; max-width:820px; margin-top:18px; }}
.h-sub {{ color:#DDE7F0; font-size:16px; line-height:1.6; max-width:760px; margin-top:18px; }}
.hero-bottom {{ display:flex; flex-direction:column; gap:18px; }}
.hero-actions {{ display:flex; gap:8px; flex-wrap:wrap; }}
.pill {{
  display:inline-flex; align-items:center; gap:6px; border:1px solid rgba(232,179,57,.48);
  background:rgba(12,18,29,.72); color:#fff; border-radius:999px; padding:9px 14px; font-size:12px; font-weight:900;
}}
.hero-signal-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; max-width:900px; }}
.signal {{
  background:rgba(12,12,15,.82); border:1px solid rgba(255,255,255,.14); border-radius:9px; padding:13px 14px;
  display:flex; flex-direction:column; justify-content:center;
  backdrop-filter:blur(8px); min-height:116px; box-shadow:0 14px 36px rgba(0,0,0,.28);
}}
.signal-k {{ color:#9AA4B4; font-size:10px; text-transform:uppercase; font-weight:900; }}
.signal-v {{ color:{INK}; font-size:21px; font-weight:900; margin-top:2px; font-family:Consolas, monospace; }}
.signal-d {{ color:#8A95A5; font-size:11px; margin-top:3px; }}
.grid4 {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-bottom:12px; }}
.grid6 {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-bottom:12px; }}
.metric {{
  background:{PANEL}; border:1px solid {LINE}; border-radius:8px; padding:14px;
  min-height:98px;
}}
.metric-k {{ color:#8A95A5; font-size:10px; text-transform:uppercase; font-weight:900; }}
.metric-v {{ color:{INK}; font-size:25px; line-height:1.1; font-weight:900; margin-top:8px; font-family:Consolas, monospace; }}
.metric-c {{ color:#8A95A5; font-size:11px; margin-top:6px; }}
.next-action {{
  background:{PANEL}; border:1px solid {LINE}; border-left:4px solid {GOLD};
  border-radius:8px; padding:14px; margin-bottom:12px;
}}
.next-action-k {{ color:#8A95A5; font-size:10px; text-transform:uppercase; font-weight:900; }}
.next-action-v {{ color:{INK}; font-size:20px; font-weight:900; margin-top:4px; }}
.next-action-d {{ color:#8A95A5; font-size:12px; margin-top:5px; line-height:1.45; }}
.timeline {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; }}
.step {{ background:{PANEL}; border:1px solid {LINE}; border-radius:8px; padding:13px; min-height:128px; }}
.step-k {{ color:{GOLD}; font-size:11px; font-weight:900; text-transform:uppercase; }}
.step-v {{ color:{INK}; font-size:15px; font-weight:900; margin-top:7px; line-height:1.25; }}
.step-d {{ color:#8A95A5; font-size:12px; line-height:1.45; margin-top:7px; }}
.meaning {{ background:{PANEL2}; border:1px solid {LINE}; border-left:4px solid {GOLD}; border-radius:8px; padding:12px; color:{INK}; font-size:13px; line-height:1.55; }}
.panel {{ background:{PANEL}; border:1px solid {LINE}; border-radius:8px; overflow:hidden; margin-bottom:12px; }}
.panel-h {{
  display:flex; justify-content:space-between; align-items:center; gap:12px;
  padding:12px 14px; border-bottom:1px solid {LINE}; border-left:4px solid {GOLD};
  background:linear-gradient(90deg,rgba(239,0,31,.18),rgba(106,32,40,.22),{PANEL2});
}}
.panel-t {{ font-weight:900; color:{INK}; font-size:13px; }}
.panel-m {{ color:#8A95A5; font-size:10px; font-family:Consolas, monospace; }}
.panel-b {{ padding:14px; }}
.care-grid {{ display:grid; grid-template-columns:1.05fr .95fr; gap:12px; }}
.sku-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
.sku {{ border:1px solid {LINE}; border-radius:8px; overflow:hidden; background:{PANEL}; min-height:238px; }}
.swatch {{ height:112px; background-size:cover; border-bottom:1px solid {LINE}; }}
.sku-body {{ padding:12px; }}
.sku-code {{ color:{CDC_RED}; font-size:11px; font-weight:900; font-family:Consolas, monospace; }}
.sku-name {{ color:{INK}; font-size:18px; font-weight:900; margin-top:2px; }}
.sku-copy {{ color:#8A95A5; font-size:12px; line-height:1.45; margin-top:8px; min-height:50px; }}
.tagline {{ display:flex; gap:6px; flex-wrap:wrap; margin-top:9px; }}
.tag {{ border:1px solid {LINE}; background:{PANEL2}; color:#C9D3EA; border-radius:999px; padding:3px 7px; font-size:10px; font-weight:800; }}
.brief {{ background:{PANEL2}; border:1px solid {LINE}; border-radius:8px; padding:12px; color:#D6DEE8; font-size:13px; line-height:1.55; }}
.alert {{ border-left:4px solid {GREEN}; }}
.alert.warn {{ border-left-color:{ORANGE}; }}
.alert.risk {{ border-left-color:{RED}; }}
.link-btn {{
  display:inline-flex; padding:8px 10px; border-radius:7px; background:{CDC_RED}; color:#fff !important;
  font-weight:900; font-size:12px; text-decoration:none; margin-right:6px;
}}
.link-btn.secondary {{ background:{PANEL2}; color:#FFFFFF !important; border:1px solid {LINE}; }}
.note {{ color:#8A95A5; font-size:11px; line-height:1.55; }}
.small-table {{ font-size:12px; }}
@media (max-width: 1400px) {{
  .top-meta {{ display:none; }}
  .cdc-mark {{ width:190px; }}
  .timeless-mark {{ width:155px; }}
}}
@media (max-width: 1050px) {{
  .care-grid {{ grid-template-columns:1fr; }}
  .grid4, .grid6, .sku-grid, .timeline {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
  .hero-signal-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); max-width:100%; }}
  .partner-mark {{ display:none; }}
  .hero-main {{ min-height:1140px; }}
  .hero-brand-row {{ flex-direction:column; align-items:flex-start; }}
  .hero-cdc-logo {{ width:250px; }}
  .hero-timeless-logo {{ width:190px; }}
  .h1 {{ font-size:34px; }}
}}
@media (max-width: 700px) {{
  .grid4, .grid6, .sku-grid, .timeline {{ grid-template-columns:1fr; }}
  .hero-signal-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
  .topbar {{ min-height:58px; padding:9px 12px; }}
  .top-meta {{ display:none; }}
  .brand-lockup {{ flex-direction:row; align-items:center; text-align:left; gap:8px; }}
  .timeless-mark {{ display:none; }}
  .partner-mark {{ font-size:9px; }}
  .cdc-mark {{ height:42px; width:145px; padding:6px 9px; }}
  .hero-main {{ min-height:1140px; }}
  .hero-content {{ padding:24px 24px; }}
  .hero-brand-row {{ gap:10px; margin-bottom:12px; }}
  .hero-cdc-logo {{ height:58px; width:190px; padding:8px 10px; }}
  .hero-timeless-logo {{ height:48px; width:160px; }}
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
            ["CDC-PO-2504-01", "Permagrain Launch Set", "2026-04-18", "40HC x 2", "Delivered", "Completed"],
            ["CDC-PO-2505-02", "PG-101 / PG-203 / PG-304", "2026-05-23", "40HC x 3", "On Water", "Next ETA update due"],
            ["CDC-PO-2506-01", "PG-405 / PG-506", "2026-06-12", "40HC x 1", "Production", "Weekly production follow-up"],
            ["CDC-FC-2507", "Forecast replenishment", "2026-07-20", "40HC x 4", "Forecast", "CDC confirmation pending"],
        ],
        columns=["PO", "Program", "Order Date", "Volume", "Status", "Next Action"],
    )


def default_shipments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["KRPUS-2505-17", "Busan", "Savannah", "2026-06-04", "2026-07-09", "On water", "Docs ready"],
            ["KRPUS-2506-03", "Busan", "Houston", "2026-06-28", "2026-08-01", "Booking", "Space secured"],
            ["KRPUS-2506-11", "Busan", "Savannah", "2026-07-12", "2026-08-16", "Planned", "Awaiting final PO"],
        ],
        columns=["Shipment", "POL", "POD", "ETD", "ETA", "Stage", "Service Note"],
    )


def default_credit() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Account Status", "On Track", "Program is active and service rhythm is in place"],
            ["Open Program Capacity", "Available", "Capacity view can be finalized before external sharing"],
            ["Documentation", "Ready", "Shipment and ESG support materials can be shared as needed"],
            ["Next Review", "Monthly", "Recommended cadence for launch-stage account care"],
        ],
        columns=["Area", "Status", "Program Note"],
    )


def default_order_shipment_desk() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["CDC-PO-2505-02", "PG-101", "Natural Reserve Oak", "Planning Qty", "On Water", "2026-06-04 / 2026-07-09", "Forwarder TBC", "No critical issue", "2026-07-01"],
            ["CDC-PO-2505-02", "PG-203", "Coastal Sand Oak", "Planning Qty", "On Water", "2026-06-04 / 2026-07-09", "Forwarder TBC", "Docs follow-up", "2026-07-01"],
            ["CDC-PO-2505-02", "PG-304", "Urban Greige Oak", "Planning Qty", "On Water", "2026-06-04 / 2026-07-09", "Forwarder TBC", "No critical issue", "2026-07-01"],
            ["CDC-PO-2506-01", "PG-405", "Smoked Valley Oak", "Planning Qty", "Production", "2026-06-28 / 2026-08-01", "Forwarder TBC", "Production status check", "2026-07-03"],
            ["CDC-PO-2506-01", "PG-506", "Heritage Brown Oak", "Planning Qty", "Production", "2026-06-28 / 2026-08-01", "Forwarder TBC", "Production status check", "2026-07-03"],
            ["CDC-FC-2507", "PG-607", "Nordic Linen Oak", "Forecast Qty", "Forecast", "TBC", "TBC", "Launch decision pending", "2026-07-10"],
        ],
        columns=["PO", "SKU", "Color", "Quantity", "Production Status", "ETD / ETA", "Forwarder", "Current Issue", "Next Update Date"],
    )


def sku_readiness_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["PG-101", "Confirmed", '7" x 48" / 5.0 mm', "Ready", "Ready", "In progress", "In progress", "85%"],
            ["PG-203", "Confirmed", '7" x 48" / 5.0 mm', "Ready", "Ready", "In progress", "In progress", "85%"],
            ["PG-304", "Confirmed", '7" x 48" / 5.0 mm', "Ready", "Ready", "Ready", "In progress", "90%"],
            ["PG-405", "Confirmed", '7" x 48" / 5.0 mm', "Review", "Ready", "In progress", "Pending", "70%"],
            ["PG-506", "Confirmed", '7" x 48" / 5.0 mm', "Review", "Ready", "In progress", "Pending", "70%"],
            ["PG-607", "Pending", '7" x 48" / 5.0 mm', "Pending", "Pending", "Pending", "Pending", "40%"],
        ],
        columns=["SKU", "Status", "Size / Spec", "Carton Artwork", "Label", "Hand Board", "1' Cut Sample", "Launch Readiness"],
    )


def next_30_days_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["This week", "Shipment snapshot 공유", "CDC can see where the launch program stands without asking first."],
            ["Next week", "Hand board arrival follow-up", "Keep showroom and sales-sample readiness moving."],
            ["July", "SKU launch prep", "Confirm artwork, labels, sample status, and launch sequence."],
            ["August", "Replenishment discussion", "Use first launch status to discuss the next order rhythm."],
            ["September", "2027 collection planning", "Open the path from Permagrain launch to broader CDC growth."],
        ],
        columns=["Timing", "Action", "What CDC Feels"],
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


def style_currency(frame: pd.DataFrame, columns: list[str]) -> pd.io.formats.style.Styler:
    return frame.style.format({column: "${:,.0f}" for column in columns})


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
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=32, b=10),
        title=dict(text=title, font=dict(size=13, color=INK)),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=11)),
        xaxis=dict(showgrid=True, gridcolor="#EEF2F7", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#EEF2F7", zeroline=False),
    )
    return fig


def create_customer_brief_pdf() -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError:
        lines = [
            "CDC Intelligence Platform - Permagrain Collection",
            f"Prepared {datetime.now().strftime('%Y-%m-%d %H:%M')} KST",
            "",
            "Customer Care Agenda",
            "- Orders: Launch orders and replenishment forecast",
            "- Logistics: Busan to Savannah/Houston shipment visibility",
            "- Program capacity: account status and replenishment readiness",
            "- Market: Housing, freight, PVC/DOTP cost indicators",
            "- ESG: Manufacturing partner sustainability material for CDC sales use",
            "",
            "Suggested Message",
            "This portal is designed as CDC's private operating room for Permagrain: order visibility, shipment timing, launch readiness, market indicators, collection content, and ESG documents in one place.",
        ]
        return simple_pdf_bytes(lines)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("CDC Intelligence Platform - Permagrain Collection", styles["Title"]),
        Spacer(1, 8),
        Paragraph(f"Prepared {datetime.now().strftime('%Y-%m-%d %H:%M')} KST", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Customer Care Agenda", styles["Heading2"]),
    ]
    care_rows = [
        ["Area", "Current Focus", "Next Action"],
        ["Orders", "Launch orders and replenishment forecast", "Confirm July/August replenishment timing"],
        ["Logistics", "Busan to Savannah/Houston shipment visibility", "Share weekly ETA and document status"],
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
                "This portal is designed as CDC's private operating room for Permagrain: order visibility, shipment timing, "
                "launch readiness, market indicators, collection content, and ESG documents in one place.",
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
    sidebar_cdc = f'<img src="data:image/png;base64,{sidebar_logo}" style="width:150px;max-width:100%;background:#050505;border-radius:7px;padding:5px;margin-bottom:8px;" alt="CDC Distributors">' if sidebar_logo else ""
    st.markdown(sidebar_cdc + '<div class="side-brand">CDC PRIVATE DESK</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-sub">Timeless Designs brand workspace<br>Permagrain Collection launch care</div>',
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
        st.markdown("#### Review Version")
        st.caption("Prepared for CDC and Timeless Designs review.")
        st.caption(f"Updated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    else:
        st.markdown("#### Data Mode")
        order_upload = st.file_uploader("Approved order data", type=["csv"], help="Optional: upload approved order data for this workspace.")
        shipment_upload = st.file_uploader("Approved shipment data", type=["csv"], help="Optional: upload approved shipment data for this workspace.")
    st.download_button(
        "Download Customer Brief PDF",
        data=create_customer_brief_pdf(),
        file_name="CDC_Permagrain_Customer_Brief.pdf",
        mime="application/pdf",
        width="stretch",
    )
    st.caption("Customer review workspace for the Permagrain launch program.")


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

open_order_count = int(len(orders))
on_water = int((shipments.get("Stage", pd.Series(dtype=str)).astype(str).str.contains("water|booking", case=False, na=False)).sum())
confirmed_skus = int((sku_readiness["Status"] == "Confirmed").sum())
pending_skus = int((sku_readiness["Status"] == "Pending").sum())
program_capacity = "Available"
scfi_now = float(freight["SCFI"].dropna().iloc[-1]) if not freight.empty else 0.0
scfi_delta = pct_delta(freight["SCFI"], 4) if not freight.empty else 0.0
pvc_now = float(purchase["PVC"].dropna().iloc[-1])
pvc_delta = pct_delta(purchase["PVC"])


cdc_logo = f'<img class="cdc-mark" src="data:image/png;base64,{CDC_LOGO}" alt="CDC Distributors">' if CDC_LOGO else '<strong>CDC</strong>'
timeless_logo = f'<img class="timeless-mark" src="data:image/png;base64,{TIMELESS_LOGO}" alt="Timeless Designs">' if TIMELESS_LOGO else '<strong>Timeless Designs</strong>'
kcc_partner = f'<img src="data:image/png;base64,{KCC_LOGO_WHITE}" alt="KCC Glass">' if KCC_LOGO_WHITE else "<span>KCC GLASS</span>"
hero_slides = "".join(
    f'<div class="hero-bg" style="background-image:url(\'data:image/png;base64,{image}\');"></div>'
    for image in CDC_HERO_IMAGES
    if image
)
market_items = [
    ("USD/KRW", "Live FX watch", "market-up"),
    ("SCFI", f"{scfi_now:,.0f} {scfi_delta:+.1f}%", "market-up" if scfi_delta >= 0 else "market-dn"),
    ("PVC", f"{pvc_now:,.1f} {pvc_delta:+.1f}%", "market-up" if pvc_delta >= 0 else "market-dn"),
    ("MORTGAGE", "Rate-sensitive demand", "market-dn"),
    ("HOUSING", "U.S. flooring pulse", "market-up"),
    ("PERMAGRAIN", "Launch readiness active", "market-up"),
]
market_html = "".join(
    f'<span class="market-item"><span class="market-dot"></span><span class="market-label">{label}</span><span class="{cls}">{value}</span></span>'
    for label, value, cls in market_items
)
st.markdown(f'<div class="market-marquee"><div class="market-track"><div class="market-set">{market_html}</div><div class="market-set">{market_html}</div></div></div>', unsafe_allow_html=True)
st.markdown(
    f"""
<div class="topbar">
  <div class="brand-lockup">
    {cdc_logo}
    {timeless_logo}
    <div class="partner-mark"><span>Strategic manufacturing partner</span>{kcc_partner}</div>
  </div>
  <div class="top-meta">
    <div><div class="top-k">Company</div><div class="top-v">CDC Distributors</div></div>
    <div><div class="top-k">Brand</div><div class="top-v">Timeless Designs</div></div>
    <div><div class="top-k">Collection</div><div class="top-v">Permagrain Collection</div></div>
    <div><div class="top-k">Updated</div><div class="top-v">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div></div>
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
        <div class="hero-brand-row">
          {cdc_logo.replace('cdc-mark', 'hero-cdc-logo')}
          {timeless_logo.replace('timeless-mark', 'hero-timeless-logo')}
        </div>
        <div class="eyebrow">Private account command center</div>
        <div class="h1">CDC x Timeless Designs Permagrain Intelligence Platform</div>
        <div class="h-sub">
          Built for CDC Distributors and the Timeless Designs team: Permagrain orders, shipment visibility,
          SKU launch readiness, ESG support, and market signals in one customer-specific workspace.
        </div>
      </div>
      <div class="hero-bottom">
        <div class="hero-actions">
          <span class="pill">CDC order desk</span>
          <span class="pill">Timeless sales support</span>
          <span class="pill">Permagrain SKU room</span>
          <span class="pill">FRED + freight + PVC signals</span>
        </div>
        <div class="hero-signal-grid">
          <div class="signal alert"><div class="signal-k">Account Health</div><div class="signal-v">GREEN</div><div class="signal-d">Launch account under active management</div></div>
          <div class="signal"><div class="signal-k">Open Orders</div><div class="signal-v">{open_order_count}</div><div class="signal-d">Active order and forecast lines</div></div>
          <div class="signal warn"><div class="signal-k">SCFI Freight Signal</div><div class="signal-v">{scfi_now:,.0f}</div><div class="signal-d">4W {scfi_delta:+.1f}% from local SCFI records</div></div>
          <div class="signal"><div class="signal-k">PVC Index</div><div class="signal-v">{pvc_now:,.1f}</div><div class="signal-d">MoM {pvc_delta:+.1f}% purchase index</div></div>
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
  <div class="metric"><div class="metric-k">Open Orders</div><div class="metric-v">{open_order_count}</div><div class="metric-c">Launch + replenishment pipeline</div></div>
  <div class="metric"><div class="metric-k">Active shipments</div><div class="metric-v">{on_water}</div><div class="metric-c">On water or booked lanes</div></div>
  <div class="metric"><div class="metric-k">Account Status</div><div class="metric-v">On Track</div><div class="metric-c">Launch support is active</div></div>
  <div class="metric"><div class="metric-k">Program Capacity</div><div class="metric-v">{program_capacity}</div><div class="metric-c">Available for next expansion</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_overview_metrics() -> None:
    st.markdown(
        f"""
<div class="grid6">
  <div class="metric"><div class="metric-k">Account Health</div><div class="metric-v">Green</div><div class="metric-c">Launch account under active care</div></div>
  <div class="metric"><div class="metric-k">Open Orders</div><div class="metric-v">{open_order_count}</div><div class="metric-c">Order and forecast lines</div></div>
  <div class="metric"><div class="metric-k">Active Shipments</div><div class="metric-v">{on_water}</div><div class="metric-c">On water or booked</div></div>
  <div class="metric"><div class="metric-k">Account Status</div><div class="metric-v">On Track</div><div class="metric-c">Launch support is active</div></div>
  <div class="metric"><div class="metric-k">Program Capacity</div><div class="metric-v">Available</div><div class="metric-c">Ready for next expansion</div></div>
  <div class="metric"><div class="metric-k">Launch SKUs</div><div class="metric-v">{confirmed_skus}+{pending_skus}</div><div class="metric-c">Confirmed + pending</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_next_action() -> None:
    st.markdown(
        """
<div class="next-action">
  <div class="next-action-k">Next Action</div>
  <div class="next-action-v">Share shipment snapshot and sample readiness status</div>
  <div class="next-action-d">This gives CDC one clear weekly view of what is moving, what is ready, and what needs a decision.</div>
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
  <div class="step-d">{row['What CDC Feels']}</div>
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
        panel("Account Overview", "team / executive report view")
        st.markdown(
            """
<div class="brief">
  <b>This is the CDC room.</b> Use this view for quick team updates and management reporting:
  account health, open orders, active shipments, program status, next action, and the next 30-day plan.
</div>
""",
            unsafe_allow_html=True,
        )
        st.dataframe(credit, hide_index=True, width="stretch")
        close_panel()
    with right:
        panel("Next 30 Days", "care actions")
        st.dataframe(next_30_days, hide_index=True, width="stretch")
        close_panel()

    panel("CDC-Facing Message", "copy block")
    st.markdown(
        """
<div class="brief">
  CDC is being managed as a strategic launch partner. This workspace gives your team one place to see
  the Permagrain program, shipment movement, sample readiness, market indicators, and sales-ready ESG assets.
  The intent is simple: faster answers, smoother launch execution, and a stronger path to future collections.
</div>
""",
        unsafe_allow_html=True,
    )
    close_panel()

elif view == "Order & Shipment Desk":
    render_metrics()
    panel("Order & Shipment Desk", "PO / SKU / ETA / issue tracking")
    st.markdown(
        """
<div class="brief">
  This is the most practical customer-care view for CDC and AJ: every PO line has a SKU, color,
  production status, ETD/ETA, current issue, and next update date.
</div>
""",
        unsafe_allow_html=True,
    )
    st.dataframe(order_shipment, hide_index=True, width="stretch")
    st.download_button(
        "Download order & shipment desk",
        order_shipment.to_csv(index=False).encode("utf-8-sig"),
        "CDC_Order_Shipment_Desk.csv",
        "text/csv",
        width="stretch",
    )
    close_panel()

    panel("Shipment Status", "ETD / ETA / service note")
    st.dataframe(shipments, hide_index=True, width="stretch")
    close_panel()

elif view == "Permagrain SKU Room":
    panel("Permagrain SKU Room", "confirmed / pending / launch readiness")
    st.markdown(
        f"""
<div class="brief">
  Use this section as CDC's launch-room view: confirmed SKUs, pending SKU, specs, carton artwork,
  label, hand board, 1' cut sample, and launch readiness.
  Brand reference: <a href="{TIMELESS_URL}" target="_blank" rel="noopener noreferrer">Timeless Designs Flooring</a>.
</div>
""",
        unsafe_allow_html=True,
    )
    st.dataframe(sku_readiness, hide_index=True, width="stretch")
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
    st.dataframe(notes, hide_index=True, width="stretch")
    close_panel()

elif view == "Market Signal for CDC":
    panel("Market Signal for CDC", "indicator + buyer meaning")
    st.markdown(
        """
<div class="brief">
  These indicators are compressed for CDC: not just the number, but what it means for launch timing,
  replenishment, pricing conversation, and sales planning.
</div>
""",
        unsafe_allow_html=True,
    )
    signal_rows = pd.DataFrame(
        [
            ["USD/KRW", "FX movement affects quote timing and landed-cost confidence.", "Use a clear quote validity window when FX is moving quickly."],
            ["SCFI", f"Latest SCFI {scfi_now:,.0f}, 4-week change {scfi_delta:+.1f}%.", "If freight is rising, CDC may benefit from earlier replenishment planning."],
            ["PVC / DOTP", f"PVC purchase index {pvc_now:,.1f}, MoM {pvc_delta:+.1f}%.", "Raw-material pressure should be watched before the next large forecast discussion."],
            ["U.S. Housing Signal", "Housing starts and new-home sales indicate flooring demand backdrop.", "Use demand signals to decide whether to push builder-oriented SKUs first."],
            ["Mortgage", "Mortgage rates influence new-home and remodeling sentiment.", "If rates remain high, keep the assortment practical and low-risk for dealers."],
        ],
        columns=["Signal", "Current Read", "What this means for CDC"],
    )
    st.dataframe(signal_rows, hide_index=True, width="stretch")
    st.markdown(
        """
<div class="meaning"><b>What this means for CDC:</b> Permagrain should be managed with weekly shipment visibility, practical SKU prioritization, and early replenishment discussion when freight or raw-material signals begin to move.</div>
""",
        unsafe_allow_html=True,
    )
    close_panel()

    c1, c2 = st.columns(2)
    with c1:
        panel("U.S. Housing Demand", "FRED: HOUST / HSN1F")
        if not housing.empty:
            fig = line_chart(housing.tail(36), ["Housing Starts"], "Housing Starts")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        else:
            st.info("FRED chart waiting for API key.")
        if not new_home_sales.empty:
            fig = line_chart(new_home_sales.tail(36), ["New Home Sales"], "New Home Sales")
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        close_panel()
    with c2:
        panel("Rates & Retail Pulse", "FRED: MORTGAGE30US / MRTSSM4441USN")
        if not mortgage.empty:
            st.plotly_chart(line_chart(mortgage.tail(80), ["30Y Mortgage"], "30Y Mortgage Rate"), width="stretch", config={"displayModeBar": False})
        else:
            st.info("FRED chart waiting for API key.")
        if not building_retail.empty:
            st.plotly_chart(line_chart(building_retail.tail(36), ["Building Materials Retail"], "Building Materials & Garden Retail Sales"), width="stretch", config={"displayModeBar": False})
        close_panel()

    c3, c4 = st.columns(2)
    with c3:
        panel("SCFI / CCFI Freight Index", "local weekly records")
        if not freight.empty:
            st.plotly_chart(line_chart(freight.tail(80), ["SCFI", "CCFI"], "Container Freight Indices"), width="stretch", config={"displayModeBar": False})
            st.caption(f"Latest SCFI {scfi_now:,.0f}, 4-week change {scfi_delta:+.1f}%.")
        close_panel()
    with c4:
        panel("PVC / DOTP Cost Index", "purchase reference")
        st.plotly_chart(line_chart(purchase, ["PVC", "DOTP"], "PVC / DOTP Purchase Index"), width="stretch", config={"displayModeBar": False})
        st.caption(f"Latest PVC {pvc_now:,.1f}, month-over-month change {pvc_delta:+.1f}%.")
        close_panel()

elif view == "Next 30 Days":
    panel("Next 30 Days", "visible care rhythm")
    st.markdown(
        """
<div class="brief">
  This is the confidence-builder. It shows CDC that the next action is already known,
  owned, and connected to their launch schedule.
</div>
""",
        unsafe_allow_html=True,
    )
    render_30_day_timeline()
    close_panel()

    panel("30-Day Action Table", "shareable operating plan")
    st.dataframe(next_30_days, hide_index=True, width="stretch")
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
        st.dataframe(esg, hide_index=True, width="stretch")
        close_panel()
    with c2:
        panel("Growth Roadmap", "lead CDC to larger account status")
        roadmap = pd.DataFrame(
            [
                ["Phase 1", "Launch Discipline", "Protect first 6 SKUs, weekly service visibility, clean claims response"],
                ["Phase 2", "Replenishment Engine", "Use sell-through and program rhythm to lock recurring order cycle"],
                ["Phase 3", "Collection Expansion", "Add colorways, special formats, or adjacent LVT programs"],
                ["Phase 4", "Strategic Account", "Joint forecast, quarterly business review, co-branded assets"],
            ],
            columns=["Phase", "Focus", "What It Means"],
        )
        st.dataframe(roadmap, hide_index=True, width="stretch")
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
    '<div class="note">Prepared as a customer review workspace for CDC Distributors, Timeless Designs, and the Permagrain Collection launch program.</div>',
    unsafe_allow_html=True,
)
