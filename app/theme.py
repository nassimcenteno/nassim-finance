# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime
import calendar as _cal

# ── Color tokens (hex constants — used for LOGIC comparisons) ─────────────────
BG        = "#08090E"
S1        = "rgba(255,255,255,.03)"
S2        = "rgba(255,255,255,.06)"
BORDER    = "rgba(255,255,255,.06)"
BORDER2   = "rgba(255,255,255,.10)"
TXT       = "#F0F0F5"
TXT2      = "rgba(240,240,245,.50)"
TXT3      = "rgba(240,240,245,.28)"
ACCENT    = "#7B6EF6"
ACCENT_LO = "rgba(123,110,246,.12)"
GREEN     = "#00C07A"
GREEN_LO  = "rgba(0,192,122,.10)"
RED       = "#FF4057"
RED_LO    = "rgba(255,64,87,.10)"
AMBER     = "#F5A623"
AMBER_LO  = "rgba(245,166,35,.10)"

INDIGO = ACCENT
PURPLE = "#A78BFA"
CYAN   = "#06B6D4"
PINK   = "#EC4899"
ORANGE = "#F97316"

# ── Category metadata ─────────────────────────────────────────────────────────
CAT_META = {
    "Alquiler":             {"color": "#7B6EF6", "bg": "rgba(123,110,246,.12)", "icon": "🏠"},
    "Mantenimiento depa":   {"color": "#06B6D4", "bg": "rgba(6,182,212,.08)",   "icon": "🔧"},
    "Estacionamiento":      {"color": "#F5A623", "bg": "rgba(245,166,35,.08)",  "icon": "🚗"},
    "Internet":             {"color": "#00C07A", "bg": "rgba(0,192,122,.08)",   "icon": "🌐"},
    "Celulares":            {"color": "#A78BFA", "bg": "rgba(123,110,246,.10)", "icon": "📱"},
    "Seguro de auto":       {"color": "#FF4057", "bg": "rgba(255,64,87,.10)",   "icon": "🛡️"},
    "Combustible":          {"color": "#F5A623", "bg": "rgba(245,166,35,.10)",  "icon": "⛽"},
    "Gastos establecidos":  {"color": "#7B6EF6", "bg": "rgba(123,110,246,.12)", "icon": "📋"},
    "Restaurantes":         {"color": "#00C07A", "bg": "rgba(0,192,122,.10)",   "icon": "🍽️"},
    "Bolsita":              {"color": "#EC4899", "bg": "rgba(236,72,153,.10)",  "icon": "🛍️"},
    "Extra":                {"color": "#F5A623", "bg": "rgba(245,166,35,.10)",  "icon": "✨"},
}

CAT_ICONS  = {k: (v["icon"], v["bg"]) for k, v in CAT_META.items()}
CAT_COLORS = {k: v["color"]           for k, v in CAT_META.items()}

# ── Plotly theme (dark — used by pages that don't call get_plotly_theme) ──────
PLOTLY_AXIS = dict(
    gridcolor="rgba(255,255,255,.04)",
    linecolor="rgba(255,255,255,.05)",
    tickfont=dict(color=TXT3, size=9),
    zerolinecolor="rgba(255,255,255,.05)",
)
PLOTLY_GLASS = dict(
    paper_bgcolor="rgba(255,255,255,.03)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="system-ui,-apple-system,sans-serif", color=TXT3, size=10),
    hoverlabel=dict(bgcolor="#0D0E16", bordercolor=BORDER2,
                    font=dict(family="system-ui", size=12, color=TXT)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TXT2)),
    colorway=[ACCENT, GREEN, AMBER, CYAN, RED, PURPLE, PINK, "#14B8A6"],
)


# ── Dark-mode helpers ─────────────────────────────────────────────────────────

def _dark() -> bool:
    return st.session_state.get("dark_mode", True)


# Light-mode equivalents for each dark constant
_LIGHT_REMAP = {
    BG:        "#F4F5F9",
    S1:        "#FFFFFF",
    S2:        "rgba(0,0,0,.04)",
    BORDER:    "rgba(0,0,0,.07)",
    BORDER2:   "rgba(0,0,0,.12)",
    TXT:       "#0E0F18",
    TXT2:      "rgba(14,15,24,.55)",
    TXT3:      "rgba(14,15,24,.35)",
    ACCENT:    "#6358D4",
    ACCENT_LO: "rgba(99,88,212,.10)",
    GREEN:     "#009E65",
    GREEN_LO:  "rgba(0,158,101,.08)",
    RED:       "#D90030",
    RED_LO:    "rgba(217,0,48,.08)",
    AMBER:     "#B87000",
    AMBER_LO:  "rgba(184,112,0,.08)",
}


def _mc(color: str) -> str:
    """Return color for current theme. Dark constants → light equivalents when needed."""
    if _dark():
        return color
    return _LIGHT_REMAP.get(color, color)


def get_plotly_theme() -> tuple:
    """Return (layout_dict, axis_dict) tuned for current light/dark theme."""
    d = _dark()
    glass = dict(
        paper_bgcolor="rgba(255,255,255,.03)" if d else "rgba(255,255,255,1)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="system-ui,-apple-system,sans-serif",
                  color=TXT3 if d else "rgba(14,15,24,.35)", size=10),
        hoverlabel=dict(
            bgcolor="#0D0E16" if d else "#FFFFFF",
            bordercolor=BORDER2 if d else "rgba(0,0,0,.12)",
            font=dict(family="system-ui", size=12, color=TXT if d else "#0E0F18"),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11, color=TXT2 if d else "rgba(14,15,24,.55)")),
        colorway=[ACCENT, GREEN, AMBER, CYAN, RED, PURPLE, PINK, "#14B8A6"],
    )
    axis = dict(
        gridcolor="rgba(255,255,255,.04)" if d else "rgba(0,0,0,.06)",
        linecolor="rgba(255,255,255,.05)" if d else "rgba(0,0,0,.08)",
        tickfont=dict(color=TXT3 if d else "rgba(14,15,24,.35)", size=9),
        zerolinecolor="rgba(255,255,255,.05)" if d else "rgba(0,0,0,.08)",
    )
    return glass, axis


# ── Global CSS ────────────────────────────────────────────────────────────────
_CSS = """
<style>
html, body { margin:0; padding:0; }

[data-testid="stApp"] {
  background: radial-gradient(ellipse 60% 40% at 20% 10%, rgba(123,110,246,.07) 0%, transparent 100%), #08090E !important;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif !important;
  color: #F0F0F5 !important;
}

/* Hide Streamlit chrome globally — stHeader/stToolbar handled per breakpoint below */
#MainMenu, footer,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
[data-testid="stMainMenuButton"],
[data-testid="stHeaderFill"],
[data-testid="stLogoSpacer"],
[data-testid="stToolbarActions"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display:none !important; }

/* Desktop: hide native header (sidebar always visible) */
@media (min-width: 769px) {
  [data-testid="stHeader"]  { display:none !important; }
  [data-testid="stToolbar"] { display:none !important; }
}

/* ── Mobile topbar ── */
@media (max-width: 768px) {
  /* Transparent header — just provides layout height so content clears below it */
  [data-testid="stHeader"] {
    display: flex !important;
    align-items: center !important;
    height: 52px !important;
    min-height: 52px !important;
    background: transparent !important;
    border-bottom: none !important;
    padding: 0 !important;
    z-index: 1000 !important;
  }
  /* Toolbar pinned top-left — holds the hamburger */
  [data-testid="stToolbar"] {
    display: flex !important;
    align-items: center !important;
    position: absolute !important;
    left: 8px !important; right: auto !important; top: 6px !important;
    padding: 0 !important;
  }
  /* Hamburger: frosted-glass pill button */
  [data-testid="stExpandSidebarButton"] {
    display: inline-flex !important;
    width: 40px !important; height: 40px !important;
    min-width: 40px !important; min-height: 40px !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,.10) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    backdrop-filter: blur(12px) !important;
    align-items: center !important; justify-content: center !important;
    padding: 0 !important;
  }
  /* Replace native glyph with 3-bar hamburger */
  [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
    font-size: 0 !important;
    position: relative !important;
    width: 18px !important; height: 14px !important;
    display: inline-block !important;
  }
  [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"]::before {
    content: "" !important;
    position: absolute !important;
    left: 50% !important; top: 50% !important;
    transform: translate(-50%, -50%) !important;
    width: 18px !important; height: 2px !important;
    background: rgba(240,240,245,.85) !important;
    border-radius: 2px !important;
    box-shadow: 0 -6px 0 rgba(240,240,245,.85), 0 6px 0 rgba(240,240,245,.85) !important;
  }

  /* Sidebar close button → same hamburger icon */
  [data-testid="stSidebarCollapseButton"] button {
    width: 40px !important; height: 40px !important;
    min-width: 40px !important; min-height: 40px !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,.10) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    display: inline-flex !important;
    align-items: center !important; justify-content: center !important;
  }
  [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
    font-size: 0 !important;
    position: relative !important;
    width: 18px !important; height: 14px !important;
    display: inline-block !important;
  }
  [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::before {
    content: "" !important;
    position: absolute !important;
    left: 50% !important; top: 50% !important;
    transform: translate(-50%, -50%) !important;
    width: 18px !important; height: 2px !important;
    background: rgba(240,240,245,.85) !important;
    border-radius: 2px !important;
    box-shadow: 0 -6px 0 rgba(240,240,245,.85), 0 6px 0 rgba(240,240,245,.85) !important;
  }

  /* Content clears 52px header + 12px breathing room */
  [data-testid="stMainBlockContainer"] {
    padding: 64px 14px 48px !important;
  }
  /* Sidebar full-height overlay */
  [data-testid="stSidebar"] {
    top: 0 !important;
    height: 100vh !important;
    z-index: 999999 !important;
    box-shadow: 4px 0 40px rgba(0,0,0,.7) !important;
  }
  /* Responsive layout */
  .nf-stat-grid { grid-template-columns: 1fr 1fr !important; gap: 10px !important; }
  .nf-hero-card { padding: 24px 20px 20px !important; border-radius: 16px !important; }
  .nf-hero-amount { font-size: 52px !important; line-height: .95 !important; }
  .nf-topbar { margin-bottom: 16px !important; }
  .nf-topbar-title { font-size: 16px !important; }
  [data-testid="stFormSubmitButton"] > button,
  [data-testid="stButton"] > button { min-height: 48px !important; }
}

/* Desktop gap + sidebar header fix */
@media (min-width: 769px) {
  [data-testid="stMainBlockContainer"] { padding-top: 24px !important; }
  .main .block-container { padding-top: 24px !important; }
  [data-testid="stSidebarHeader"] {
    height: 0 !important; min-height: 0 !important;
    overflow: hidden !important; padding: 0 !important; margin: 0 !important;
  }
}

[data-testid="stAppViewContainer"],
section[data-testid="stMain"] { padding-top: 0 !important; }

/* ── Sidebar shell ── */
[data-testid="stSidebar"] {
  background: rgba(8,9,14,.97) !important;
  border-right: 1px solid rgba(255,255,255,.06) !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
  min-width: 200px !important;
  max-width: 200px !important;
  width: 200px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebarContent"]            { padding: 0 !important; }
[data-testid="stSidebarUserContent"]        { padding: 0 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stSidebar"] [data-testid="stElementContainer"] {
  padding-top: 0 !important; padding-bottom: 0 !important;
  margin-top: 0 !important; margin-bottom: 0 !important;
}

/* ── Sidebar nav links ── */
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
  display: flex !important; align-items: center !important; gap: 8px !important;
  border-radius: 8px !important; padding: 8px 10px !important; margin: 0 8px 1px !important;
  color: rgba(240,240,245,.28) !important; font-size: 12px !important;
  font-weight: 500 !important; transition: background .14s, color .14s !important;
  text-decoration: none !important; letter-spacing: -.01em !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover,
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
  background: rgba(255,255,255,.06) !important;
  color: rgba(240,240,245,.55) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
  background: rgba(123,110,246,.12) !important;
  color: #7B6EF6 !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a .material-symbols-rounded {
  font-size: 16px !important; line-height: 16px !important;
  width: 16px !important; height: 16px !important;
  flex-shrink: 0 !important; opacity: .65 !important;
  font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 16 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] [data-testid="stIconMaterial"] { opacity: 1 !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a p { margin: 0 !important; color: inherit !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a span { color: inherit !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] { border: none !important; background: none !important; }

/* ── Sidebar section labels ── */
.nf-nav-section {
  font-size: 9px; font-weight: 700; color: rgba(240,240,245,.28);
  text-transform: uppercase; letter-spacing: .14em; padding: 12px 10px 5px;
}
.nf-nav-footer {
  border-top: 1px solid rgba(255,255,255,.06); margin: 12px 0 0; padding: 12px 10px 4px;
}

/* ── Dark mode toggle button in sidebar ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
  background: transparent !important;
  border: 1px solid rgba(255,255,255,.08) !important;
  color: rgba(240,240,245,.35) !important;
  font-size: 11px !important;
  border-radius: 8px !important;
  margin: 4px 10px 12px !important;
  width: calc(100% - 20px) !important;
  min-height: 32px !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
  background: rgba(255,255,255,.05) !important;
  color: rgba(240,240,245,.6) !important;
}

/* ── Main content ── */
.main .block-container { padding: 24px 36px 64px !important; max-width: 1200px !important; }

/* ── Typography ── */
p, span, div, label { color: rgba(240,240,245,.85); }
h1, h2, h3 { color: #F0F0F5; letter-spacing: -.02em; }

/* ── Inputs ── */
[data-baseweb="select"] > div:first-child,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
textarea {
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  border-radius: 10px !important;
  color: #F0F0F5 !important;
  font-family: system-ui, sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}
[data-baseweb="select"] > div:first-child:focus-within,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: rgba(123,110,246,.5) !important;
  box-shadow: 0 0 0 3px rgba(123,110,246,.10) !important;
  outline: none !important;
}
[data-testid="stNumberInput"] button {
  background: rgba(255,255,255,.04) !important;
  border-color: rgba(255,255,255,.08) !important;
  color: rgba(240,240,245,.5) !important;
}

/* Prevent keyboard from opening when tapping selectbox or date dropdowns on mobile */
[data-baseweb="select"] input,
[data-testid="stDateInput"] input {
  pointer-events: none !important;
  caret-color: transparent !important;
  user-select: none !important;
  -webkit-user-select: none !important;
}

/* ── Dropdown popover ── */
[data-baseweb="popover"] {
  background: #0D0E16 !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 60px rgba(0,0,0,.7) !important;
}
[role="option"] {
  background: transparent !important;
  color: rgba(240,240,245,.65) !important;
  font-size: 13px !important;
  border-radius: 6px !important;
  margin: 2px 4px !important;
  padding: 10px 12px !important;
  min-height: 40px !important;
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
  background: rgba(123,110,246,.15) !important;
  color: #F0F0F5 !important;
}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
[data-testid="stButton"] > button[kind="primary"] {
  background: #7B6EF6 !important; border: none !important;
  border-radius: 10px !important; font-weight: 700 !important;
  font-size: 13px !important; color: #fff !important;
  letter-spacing: -.01em !important; transition: opacity .15s !important;
}
[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]:hover,
[data-testid="stButton"] > button[kind="primary"]:hover { opacity: .85 !important; }
[data-testid="stFormSubmitButton"] > button[kind="secondaryFormSubmit"],
[data-testid="stButton"] > button:not([kind="primary"]) {
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  border-radius: 10px !important;
  color: rgba(240,240,245,.5) !important;
  font-size: 13px !important; font-weight: 600 !important;
}

/* ── Plotly charts ── */
[data-testid="stPlotlyChart"] {
  border: 1px solid rgba(255,255,255,.06) !important;
  border-radius: 16px !important; overflow: hidden !important; margin-bottom: 20px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border-radius: 16px !important; overflow: hidden !important;
  border: 1px solid rgba(255,255,255,.05) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
  border-radius: 12px !important;
  background: rgba(255,255,255,.03) !important;
  border: 1px solid rgba(255,255,255,.07) !important;
}
div[data-testid="stSuccess"] { background: rgba(0,192,122,.08) !important; border-color: rgba(0,192,122,.2) !important; }
div[data-testid="stError"]   { background: rgba(255,64,87,.08) !important; border-color: rgba(255,64,87,.2) !important; }
div[data-testid="stWarning"] { background: rgba(245,166,35,.08) !important; border-color: rgba(245,166,35,.2) !important; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
  background: rgba(255,255,255,.04) !important; border-radius: 10px !important;
  padding: 3px !important; border: 1px solid rgba(255,255,255,.06) !important; gap: 2px !important;
}
[data-baseweb="tab"] {
  border-radius: 8px !important; color: rgba(240,240,245,.35) !important;
  font-weight: 500 !important; font-size: 12px !important;
  background: transparent !important; padding: 6px 14px !important; transition: all .14s !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: rgba(123,110,246,.12) !important; color: #7B6EF6 !important; font-weight: 600 !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display:none !important; }

/* ── Spinner / Scrollbar ── */
[data-testid="stSpinner"] > div { border-top-color: #7B6EF6 !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,.02); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.08); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.14); }

/* ── Tag pills ── */
.nf-tag {
  display: inline-flex !important; align-items: center !important;
  border: 1px solid rgba(255,255,255,.10) !important; border-radius: 20px !important;
  padding: 4px 10px !important; font-size: 11px !important; font-weight: 600 !important;
  color: rgba(240,240,245,.28) !important; background: transparent !important; line-height: 1.4 !important;
}
.nf-tag-avail { border-color: rgba(0,192,122,.2) !important; color: #00C07A !important; background: rgba(0,192,122,.10) !important; }
.nf-tag-over  { border-color: rgba(255,64,87,.2) !important;  color: #FF4057 !important; background: rgba(255,64,87,.10) !important; }
</style>
"""

# Light-mode CSS overrides — injected when dark_mode is False
_CSS_LIGHT = """
<style>
[data-testid="stApp"] {
  background: linear-gradient(135deg, rgba(99,88,212,.04) 0%, transparent 60%), #F4F5F9 !important;
  color: #0E0F18 !important;
}
[data-testid="stSidebar"] {
  background: rgba(255,255,255,.98) !important;
  border-right-color: rgba(0,0,0,.08) !important;
}
p, span, div, label { color: rgba(14,15,24,.80); }
h1, h2, h3 { color: #0E0F18; }

[data-baseweb="select"] > div:first-child,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
textarea {
  background: rgba(0,0,0,.05) !important;
  border-color: rgba(0,0,0,.12) !important;
  color: #0E0F18 !important;
}
[data-baseweb="popover"] { background: #FFFFFF !important; border-color: rgba(0,0,0,.10) !important; }
[role="option"] { color: rgba(14,15,24,.65) !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] {
  background: rgba(99,88,212,.10) !important; color: #0E0F18 !important;
}

[data-testid="stFormSubmitButton"] > button[kind="secondaryFormSubmit"],
[data-testid="stButton"] > button:not([kind="primary"]) {
  background: rgba(0,0,0,.06) !important;
  border-color: rgba(0,0,0,.12) !important;
  color: rgba(14,15,24,.6) !important;
}
[data-testid="stAlert"] { background: rgba(0,0,0,.03) !important; border-color: rgba(0,0,0,.08) !important; }
[data-testid="stPlotlyChart"]  { border-color: rgba(0,0,0,.08) !important; }
[data-testid="stDataFrame"]    { border-color: rgba(0,0,0,.08) !important; }
[data-baseweb="tab-list"] { background: rgba(0,0,0,.05) !important; border-color: rgba(0,0,0,.08) !important; }
[data-baseweb="tab"] { color: rgba(14,15,24,.35) !important; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,.15); }

[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { color: rgba(14,15,24,.35) !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background: rgba(0,0,0,.05) !important; color: rgba(14,15,24,.65) !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] { background: rgba(99,88,212,.10) !important; color: #6358D4 !important; }
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
  border-color: rgba(0,0,0,.10) !important; color: rgba(14,15,24,.45) !important;
}

/* Fix inline-style dark text colors emitted by st.html() components */
[style*="color:rgba(240,240,245,.85)"] { color: rgba(14,15,24,.85) !important; }
[style*="color:rgba(240,240,245,.65)"] { color: rgba(14,15,24,.65) !important; }
[style*="color:rgba(240,240,245,.50)"] { color: rgba(14,15,24,.55) !important; }
[style*="color:rgba(240,240,245,.40)"] { color: rgba(14,15,24,.45) !important; }
[style*="color:rgba(240,240,245,.28)"] { color: rgba(14,15,24,.35) !important; }
[style*="color:rgba(240,240,245,.25)"] { color: rgba(14,15,24,.30) !important; }
[style*="color:rgba(240,240,245,.2)"]  { color: rgba(14,15,24,.22) !important; }
[style*="color:#F0F0F5"]               { color: #0E0F18 !important; }
/* Fix inline-style dark backgrounds */
[style*="background:rgba(255,255,255,.03)"] { background: #FFFFFF !important; }
[style*="background:rgba(255,255,255,.06)"] { background: rgba(0,0,0,.04) !important; }
[style*="background:rgba(255,255,255,.04)"] { background: rgba(0,0,0,.03) !important; }
[style*="border:1px solid rgba(255,255,255,.06)"]  { border-color: rgba(0,0,0,.08) !important; }
[style*="border:1px solid rgba(255,255,255,.05)"]  { border-color: rgba(0,0,0,.07) !important; }
[style*="border-bottom:1px solid rgba(255,255,255,.03)"] { border-bottom-color: rgba(0,0,0,.05) !important; }
/* Mobile hamburger buttons in light mode */
@media (max-width: 768px) {
  [data-testid="stExpandSidebarButton"] {
    background: rgba(14,15,24,.08) !important;
    border-color: rgba(14,15,24,.14) !important;
  }
  [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"]::before {
    background: #0E0F18 !important;
    box-shadow: 0 -6px 0 #0E0F18, 0 6px 0 #0E0F18 !important;
  }
  [data-testid="stSidebarCollapseButton"] button {
    background: rgba(14,15,24,.08) !important;
    border-color: rgba(14,15,24,.14) !important;
  }
  [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::before {
    background: #0E0F18 !important;
    box-shadow: 0 -6px 0 #0E0F18, 0 6px 0 #0E0F18 !important;
  }
}
</style>
"""

_LAYOUT_PATCH = (
    '<div style="display:none"><img src="x" onerror="'
    "(function(){if(window.__nfP)return;window.__nfP=1;var d=document;"
    "function isMob(){return window.innerWidth<=768;}"
    "function p(){"
    "var mob=isMob();"
    "var sbh=d.querySelector('[data-testid=stSidebarHeader]');"
    "if(sbh){"
    "if(mob){sbh.style.removeProperty('height');sbh.style.removeProperty('min-height');sbh.style.removeProperty('overflow');}"
    "else{sbh.style.setProperty('height','0','important');sbh.style.setProperty('min-height','0','important');"
    "sbh.style.setProperty('overflow','hidden','important');sbh.style.setProperty('padding','0','important');"
    "sbh.style.setProperty('margin','0','important');}}"
    "var mb=d.querySelector('[data-testid=stMainBlockContainer]');"
    "if(mb)mb.style.setProperty('padding-top',mob?'64px':'24px','important');}"
    "p();[80,300,700,1500].forEach(function(ms){setTimeout(p,ms)});"
    "var t;new MutationObserver(function(){clearTimeout(t);t=setTimeout(p,25)})"
    ".observe(d.body,{childList:true,subtree:true})})()\"></div>"
)


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(_LAYOUT_PATCH, unsafe_allow_html=True)
    if not _dark():
        st.markdown(_CSS_LIGHT, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(mes_key: str = "mes_global") -> str:
    d = _dark()
    sidebar_bg  = "rgba(8,9,14,1)" if d else "rgba(255,255,255,1)"
    brand_txt   = "#F0F0F5"        if d else "#0E0F18"
    brand_sub   = "rgba(240,240,245,.28)" if d else "rgba(14,15,24,.35)"
    border_clr  = "rgba(255,255,255,.06)" if d else "rgba(0,0,0,.08)"

    with st.sidebar:
        st.html(
            f'<div style="background:{sidebar_bg};display:flex;align-items:center;gap:9px;'
            f'padding:20px 16px 16px;border-bottom:1px solid {border_clr};margin-bottom:4px">'
            f'<div style="width:30px;height:30px;border-radius:9px;background:#7B6EF6;'
            f'flex-shrink:0;display:flex;align-items:center;justify-content:center;'
            f'font-size:15px;font-weight:900;color:#fff;letter-spacing:-.03em">N</div>'
            f'<div style="flex:1;min-width:0">'
            f'<div style="font-size:13px;font-weight:700;color:{brand_txt};'
            f'letter-spacing:-.02em;line-height:1.3">Nassim Finance</div>'
            f'<div style="font-size:10px;color:{brand_sub};margin-top:1px;line-height:1.3">'
            f'nassimcenteno86@gmail.com</div>'
            f'</div></div>'
        )

        st.markdown('<div class="nf-nav-section">Principal</div>', unsafe_allow_html=True)
        st.page_link("main.py",                         label="Dashboard",      icon=":material/dashboard:")
        st.page_link("pages/1_Ingresar_Gasto.py",       label="Ingresar Gasto", icon=":material/add_circle:")

        st.markdown('<div class="nf-nav-section">Reportes</div>', unsafe_allow_html=True)
        st.page_link("pages/2_Gastos_Diarios.py",       label="Gastos Diarios", icon=":material/calendar_month:")
        st.page_link("pages/3_Por_Categoria.py",        label="Por Categoría",  icon=":material/donut_large:")
        st.page_link("pages/4_Analisis.py",             label="Análisis",       icon=":material/trending_up:")

        st.markdown('<div class="nf-nav-section">Configurar</div>', unsafe_allow_html=True)
        st.page_link("pages/5_Presupuesto.py",          label="Presupuesto",    icon=":material/tune:")

        st.markdown('<div class="nf-nav-footer"></div>', unsafe_allow_html=True)
        mes = st.selectbox(
            "", available_months(), format_func=fmt_month,
            key=mes_key, label_visibility="collapsed",
        )

        # Dark mode toggle
        toggle_label = "Modo claro" if d else "Modo oscuro"
        if st.button(toggle_label, key="_nf_theme", use_container_width=True):
            st.session_state.dark_mode = not d
            st.rerun()

    return mes


# ── Page components ───────────────────────────────────────────────────────────

def topbar(title: str, subtitle: str, show_status: bool = False) -> None:
    txt  = _mc(TXT)
    txt3 = _mc(TXT3)
    grn  = _mc(GREEN)
    status = ""
    if show_status:
        status = (
            f'<div style="display:flex;align-items:center;gap:5px;border:1px solid rgba(255,255,255,.10);'
            f'border-radius:20px;padding:5px 11px;font-size:10px;font-weight:600;color:{txt3}">'
            f'<span style="width:5px;height:5px;border-radius:50%;background:{grn};'
            f'animation:blink 2.4s ease infinite;flex-shrink:0"></span>'
            f'Datos actualizados</div>'
            f'<style>@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}</style>'
        )
    st.html(
        f'<div class="nf-topbar" style="display:flex;align-items:flex-start;'
        f'justify-content:space-between;margin-bottom:28px">'
        f'<div>'
        f'<div class="nf-topbar-title" style="font-size:18px;font-weight:800;color:{txt};'
        f'letter-spacing:-.03em">{title}</div>'
        f'<div style="font-size:11px;color:{txt3};margin-top:3px">{subtitle}</div>'
        f'</div>{status}</div>'
    )


def hero_card(spent: float, budget: float, month_label: str,
              pct: float, avail: float, trans: int, days_left: int) -> None:
    s1     = _mc(S1)
    border = _mc(BORDER)
    txt    = _mc(TXT)
    txt3   = _mc(TXT3)
    accent = _mc(ACCENT)
    red    = _mc(RED)
    amber  = _mc(AMBER)

    bar_color = red if pct > 100 else amber if pct >= 80 else accent
    bar_w     = min(pct, 100)

    avail_tag = (
        f'<span class="nf-tag nf-tag-avail">S/ {avail:,.0f} disponible</span>'
        if avail >= 0 else
        f'<span class="nf-tag nf-tag-over">S/ {abs(avail):,.0f} excedido</span>'
    )
    pct_tag   = f'<span class="nf-tag">{pct:.0f}% ejecutado</span>'
    trans_tag = f'<span class="nf-tag">{trans} transacciones</span>'
    days_tag  = (
        f'<span class="nf-tag">{days_left} días restantes</span>'
        if days_left > 0 else '<span class="nf-tag">Mes cerrado</span>'
    )

    tag_parts = []
    if budget > 0:
        tag_parts.append(avail_tag)
        tag_parts.append(pct_tag)
    tag_parts.append(trans_tag)
    tag_parts.append(days_tag)
    tags_row = " ".join(tag_parts)

    budget_line = ""
    if budget > 0:
        budget_line = (
            f'<div style="padding-bottom:8px">'
            f'<div style="font-size:13px;color:{txt3};margin-bottom:4px">de un presupuesto de</div>'
            f'<div style="font-size:22px;font-weight:700;color:rgba(240,240,245,.50);'
            f'letter-spacing:-.02em">S/ {budget:,.0f}</div>'
            f'</div>'
        )

    st.html(
        f'<div class="nf-hero-card" style="background:{s1};border:1px solid {border};'
        f'border-radius:20px;padding:36px 40px 32px;position:relative;overflow:hidden;margin-bottom:14px">'
        f'<div style="font-size:9px;font-weight:700;color:{txt3};text-transform:uppercase;'
        f'letter-spacing:.15em;margin-bottom:16px">Gastado · {month_label}</div>'
        f'<div style="display:flex;align-items:flex-end;gap:20px;margin-bottom:28px;flex-wrap:wrap">'
        f'<div class="nf-hero-amount" style="font-size:80px;font-weight:900;line-height:.95;'
        f'letter-spacing:-.04em;color:{txt}">S/ {spent:,.0f}</div>'
        f'{budget_line}</div>'
        f'<div style="height:3px;background:rgba(255,255,255,.06);border-radius:3px;'
        f'overflow:hidden;margin-bottom:14px">'
        f'<div style="height:100%;width:{bar_w:.1f}%;border-radius:3px;background:{bar_color};'
        f'transition:width .8s"></div></div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap">{tags_row}</div>'
        f'</div>'
    )


_ALERT_COLORS = {RED, AMBER, GREEN}


def stat_cards(stats: list) -> None:
    s1     = _mc(S1)
    border = _mc(BORDER)
    txt3   = _mc(TXT3)
    alert_map = {RED: _mc(RED), GREEN: _mc(GREEN), AMBER: _mc(AMBER)}

    cols = "1fr " * len(stats)
    cards_html = ""
    for s in stats:
        color = s.get("color", TXT)
        label = s.get("label", "")
        value = s.get("value", "")
        sub   = s.get("sub", "")
        value_color = alert_map.get(color, _mc(TXT))
        cards_html += (
            f'<div style="background:{s1};border:1px solid {border};border-radius:16px;'
            f'padding:20px 22px 18px;position:relative;overflow:hidden">'
            f'<div style="position:absolute;top:0;left:0;right:0;height:1px;'
            f'background:linear-gradient(90deg,{color},transparent)"></div>'
            f'<div style="font-size:9px;font-weight:700;color:{txt3};text-transform:uppercase;'
            f'letter-spacing:.14em;margin-bottom:12px">{label}</div>'
            f'<div style="font-size:28px;font-weight:800;letter-spacing:-.03em;line-height:1;'
            f'margin-bottom:5px;color:{value_color}">{value}</div>'
            f'<div style="font-size:11px;color:{txt3}">{sub}</div>'
            f'</div>'
        )
    st.html(
        f'<div class="nf-stat-grid" style="display:grid;grid-template-columns:{cols.strip()};'
        f'gap:12px;margin-bottom:28px">{cards_html}</div>'
    )


def section_hdr(title: str, badge_text: str = None, variant: str = "warn") -> None:
    txt = _mc(TXT)
    BADGE_COLORS = {
        "warn": (_mc(AMBER), _mc(AMBER_LO)),
        "ok":   (_mc(GREEN), _mc(GREEN_LO)),
        "bad":  (_mc(RED),   _mc(RED_LO)),
    }
    c, bg = BADGE_COLORS.get(variant, (_mc(AMBER), _mc(AMBER_LO)))
    badge_html = ""
    if badge_text:
        badge_html = (
            f'<span style="font-size:10px;font-weight:600;padding:3px 9px;border-radius:20px;'
            f'color:{c};background:{bg}">{badge_text}</span>'
        )
    st.html(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'margin-bottom:8px;padding:0 2px">'
        f'<span style="font-size:12px;font-weight:700;color:{txt};letter-spacing:-.01em">'
        f'{title}</span>{badge_html}</div>'
    )


def cat_list_rows(cats: list) -> None:
    s1     = _mc(S1)
    border = _mc(BORDER)
    txt3   = _mc(TXT3)
    txt85  = "rgba(240,240,245,.85)" if _dark() else "rgba(14,15,24,.85)"
    txt20  = "rgba(240,240,245,.2)"  if _dark() else "rgba(14,15,24,.2)"

    rows_html = ""
    for c in cats:
        pct    = c.get("pct", 0.0)
        spent  = c.get("spent", 0.0)
        budget = c.get("budget", 0.0)
        name   = c.get("name", "")
        icon   = c.get("icon", "💰")
        bg     = c.get("bg", _mc(S2))
        color  = c.get("color", _mc(ACCENT))
        bar_w  = min(pct, 100)

        if pct > 100:
            fill_color = _mc(RED);   pct_color = _mc(RED)
        elif pct >= 80:
            fill_color = _mc(AMBER); pct_color = _mc(AMBER)
        elif pct == 0:
            fill_color = "rgba(255,255,255,.06)" if _dark() else "rgba(0,0,0,.06)"
            pct_color  = "rgba(240,240,245,.25)" if _dark() else "rgba(14,15,24,.25)"
        else:
            fill_color = color; pct_color = "rgba(240,240,245,.40)" if _dark() else "rgba(14,15,24,.40)"

        pct_str    = f"{pct:.0f}%" if budget > 0 else "—"
        budget_str = (
            f'S/ {spent:,.0f} <span style="color:{txt20}">/ {budget:,.0f}</span>'
            if budget > 0 else f"S/ {spent:,.0f}"
        )

        rows_html += (
            f'<div style="display:flex;align-items:center;gap:14px;padding:14px 20px;'
            f'border-bottom:1px solid rgba(255,255,255,.03)">'
            f'<div style="width:34px;height:34px;border-radius:9px;background:{bg};'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:16px;flex-shrink:0">{icon}</div>'
            f'<div style="flex:1;min-width:0">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px">'
            f'<span style="font-size:13px;font-weight:600;color:{txt85}">{name}</span>'
            f'<span style="font-size:11px;color:{txt3}">{budget_str}</span>'
            f'</div>'
            f'<div style="height:2px;background:rgba(255,255,255,.05);border-radius:2px;overflow:hidden">'
            f'<div style="height:100%;width:{bar_w:.1f}%;background:{fill_color};border-radius:2px"></div>'
            f'</div></div>'
            f'<div style="flex-shrink:0;text-align:right;min-width:44px">'
            f'<div style="font-size:12px;font-weight:700;color:{pct_color}">{pct_str}</div>'
            f'</div></div>'
        )

    st.html(
        f'<div style="background:{s1};border:1px solid {border};border-radius:16px;'
        f'overflow:hidden;margin-bottom:20px">{rows_html}</div>'
    )


def badge(text: str, kind: str = "neutral") -> str:
    styles = {
        "success": (_mc(GREEN_LO), "rgba(0,192,122,.2)",  _mc(GREEN)),
        "warning": (_mc(AMBER_LO), "rgba(245,166,35,.2)", _mc(AMBER)),
        "danger":  (_mc(RED_LO),   "rgba(255,64,87,.2)",  _mc(RED)),
        "neutral": (_mc(S2),       _mc(BORDER2),          _mc(TXT2)),
    }
    bg, border, color = styles.get(kind, styles["neutral"])
    return (
        f'<span style="display:inline-flex;align-items:center;padding:3px 10px;'
        f'border-radius:20px;font-size:11px;font-weight:600;border:1px solid {border};'
        f'background:{bg};color:{color}">{text}</span>'
    )


# Backward compat
def page_header(title: str, subtitle: str = "") -> None:
    topbar(title.replace("💰 ", "").replace("➕ ", "").replace("📅 ", "")
           .replace("🗂️ ", "").replace("📊 ", "").replace("⚙️ ", ""), subtitle)

def kpi_cards(cards: list) -> None:
    mapped = [{"label": c["label"], "value": c["value"],
               "sub": c.get("sub", ""), "color": c.get("color", TXT)} for c in cards]
    stat_cards(mapped)

def cat_tiles_grid(rows) -> None:
    cats = []
    for row in rows:
        if isinstance(row, dict):
            cat, g, p, pct = row["categoria"], row["gastado"], row["presupuesto"], row["pct"]
        else:
            cat, g, p, pct = row
        meta = CAT_META.get(cat, {"color": ACCENT, "bg": S2, "icon": "💰"})
        cats.append({**meta, "name": cat, "spent": g, "budget": p, "pct": pct})
    cat_list_rows(cats)


# ── Utilities ─────────────────────────────────────────────────────────────────

def fmt_month(m: str) -> str:
    MESES = {
        "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
        "05": "Mayo",  "06": "Junio",   "07": "Julio", "08": "Agosto",
        "09": "Setiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
    }
    y, mo = m.split("-")
    return f"{MESES[mo]} {y}"


def available_months(n: int = 12) -> list:
    now = datetime.now()
    year, month = now.year, now.month
    result = []
    for _ in range(n):
        result.append(f"{year}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12; year -= 1
    return result
