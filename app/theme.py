import streamlit as st
from datetime import datetime
import calendar as _cal

# ── Color tokens ──────────────────────────────────────────────────────────────
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

# Backward-compat aliases
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

# ── Plotly theme ──────────────────────────────────────────────────────────────
# Axis defaults — reference with **PLOTLY_AXIS in each chart
PLOTLY_AXIS = dict(
    gridcolor="rgba(255,255,255,.04)",
    linecolor="rgba(255,255,255,.05)",
    tickfont=dict(color=TXT3, size=9),
    zerolinecolor="rgba(255,255,255,.05)",
)

# Base layout — NO xaxis/yaxis/margin to avoid "multiple values" conflict when pages expand it
PLOTLY_GLASS = dict(
    paper_bgcolor="rgba(255,255,255,.03)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="system-ui,-apple-system,sans-serif", color=TXT3, size=10),
    hoverlabel=dict(bgcolor="#0D0E16", bordercolor=BORDER2,
                    font=dict(family="system-ui", size=12, color=TXT)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=TXT2)),
    colorway=[ACCENT, GREEN, AMBER, CYAN, RED, PURPLE, PINK, "#14B8A6"],
)


# ── Global CSS ────────────────────────────────────────────────────────────────
_CSS = """
<style>
html, body { margin:0; padding:0; }

[data-testid="stApp"] {
  background: radial-gradient(ellipse 60% 40% at 20% 10%, rgba(123,110,246,.07) 0%, transparent 100%), #08090E !important;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif !important;
  color: #F0F0F5 !important;
}

/* Hide ALL Streamlit chrome — stHeader included (custom topbar injected via JS on mobile) */
#MainMenu, footer,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
[data-testid="stToolbar"],
[data-testid="stHeader"],
[data-testid="stHeaderFill"],
[data-testid="stLogoSpacer"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] { display:none !important; }

/* Mobile */
@media (max-width: 768px) {
  .main .block-container { padding: 64px 12px 48px !important; }
  section[data-testid="stMain"] { margin-left: 0 !important; width: 100% !important; }
  [data-testid="stSidebar"] {
    position: fixed !important;
    top: 52px !important; left: 0 !important;
    height: calc(100vh - 52px) !important;
    z-index: 1050 !important;
    box-shadow: 4px 0 40px rgba(0,0,0,.7) !important;
  }
  [data-testid="stSidebarCollapsedControl"] { display:none !important; }
  [data-testid="stSidebarHeader"] {
    height: 0 !important; min-height: 0 !important;
    overflow: hidden !important; padding: 0 !important; margin: 0 !important;
  }
  .nf-stat-grid { grid-template-columns: 1fr 1fr !important; gap: 10px !important; }
  .nf-hero-card { padding: 24px 20px 20px !important; border-radius: 16px !important; }
  .nf-hero-amount { font-size: 52px !important; line-height: .95 !important; }
  .nf-topbar { margin-bottom: 16px !important; }
  .nf-topbar-title { font-size: 16px !important; }
  [data-testid="stFormSubmitButton"] > button,
  [data-testid="stButton"] > button { min-height: 48px !important; }
  #nf-backdrop {
    position: fixed !important; inset: 0 !important; top: 52px !important;
    background: rgba(0,0,0,.55) !important; z-index: 1040 !important;
    backdrop-filter: blur(2px) !important; -webkit-backdrop-filter: blur(2px) !important;
  }
}

/* Fix main content top gap — desktop only */
@media (min-width: 769px) {
  [data-testid="stMainBlockContainer"] { padding-top: 24px !important; }
  .main .block-container { padding-top: 24px !important; }

  /* Collapse stSidebarHeader to zero on desktop only */
  [data-testid="stSidebarHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
  }
}

[data-testid="stAppViewContainer"],
section[data-testid="stMain"] { padding-top: 0 !important; }

/* ── Sidebar shell ── */
[data-testid="stSidebar"] {
  background: rgba(8,9,14,.97) !important;
  border-right: 1px solid rgba(255,255,255,.06) !important;
}

/* Sidebar width = 200px matching HTML mockup */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
  min-width: 200px !important;
  max-width: 200px !important;
  width: 200px !important;
}

/* Remove Streamlit's default sidebar inner padding and element gaps */
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebarContent"]            { padding: 0 !important; }
[data-testid="stSidebarUserContent"]        { padding: 0 !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stSidebar"] [data-testid="stElementContainer"] {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

/* ── Sidebar brand block — full-width, own padding, bottom border ── */
.nf-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 20px 8px 16px;
  border-bottom: 1px solid rgba(255,255,255,.06);
  margin: 0 -8px 4px;
}
.nf-brand-mark {
  width: 30px; height: 30px; border-radius: 9px;
  background: #7B6EF6; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 900; color: #fff; letter-spacing: -.03em;
}
.nf-brand-name { font-size: 13px; font-weight: 700; color: #F0F0F5; letter-spacing: -.02em; }
.nf-brand-sub  { font-size: 10px; color: rgba(240,240,245,.28); margin-top: 1px; }

/* ── Sidebar section labels ── */
.nf-nav-section {
  font-size: 9px; font-weight: 700;
  color: rgba(240,240,245,.28);
  text-transform: uppercase; letter-spacing: .14em;
  padding: 12px 10px 5px;
}

/* ── Sidebar footer separator (above month selector) ── */
.nf-nav-footer {
  border-top: 1px solid rgba(255,255,255,.06);
  margin: 12px 0 0;
  padding: 12px 10px 4px;
}

/* ── Sidebar page_link buttons ── */
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  border-radius: 8px !important;
  padding: 8px 10px !important;
  margin: 0 8px 1px !important;
  color: rgba(240,240,245,.28) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  transition: background .14s, color .14s !important;
  text-decoration: none !important;
  letter-spacing: -.01em !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover,
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
  background: rgba(255,255,255,.06) !important;
  color: rgba(240,240,245,.55) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
  background: rgba(123,110,246,.12) !important;
  color: #7B6EF6 !important;
  font-weight: 600 !important;
}
/* Material icon inside page links — size to 16x16 matching mockup SVG icons */
[data-testid="stSidebar"] [data-testid="stPageLink"] a [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a .material-symbols-rounded {
  font-size: 16px !important;
  line-height: 16px !important;
  width: 16px !important;
  height: 16px !important;
  flex-shrink: 0 !important;
  opacity: .65 !important;
  font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 16 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] .material-symbols-rounded {
  opacity: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a p { margin: 0 !important; color: inherit !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] a span { color: inherit !important; }
[data-testid="stSidebar"] [data-testid="stPageLink"] { border: none !important; background: none !important; }

/* ── Main content ── */
.main .block-container {
  padding: 24px 36px 64px !important;
  max-width: 1200px !important;
}

/* ── Typography — NO !important so inline styles in components win ── */
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

/* Dropdown popover */
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
}
[role="option"]:hover, [role="option"][aria-selected="true"] {
  background: rgba(123,110,246,.15) !important;
  color: #F0F0F5 !important;
}

/* ── Buttons ── */
[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
[data-testid="stButton"] > button[kind="primary"] {
  background: #7B6EF6 !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  color: #fff !important;
  letter-spacing: -.01em !important;
  transition: opacity .15s !important;
}
[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]:hover,
[data-testid="stButton"] > button[kind="primary"]:hover { opacity: .85 !important; }

[data-testid="stFormSubmitButton"] > button[kind="secondaryFormSubmit"],
[data-testid="stButton"] > button:not([kind="primary"]) {
  background: rgba(255,255,255,.06) !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  border-radius: 10px !important;
  color: rgba(240,240,245,.5) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}

/* ── Plotly charts ── */
[data-testid="stPlotlyChart"] {
  border: 1px solid rgba(255,255,255,.06) !important;
  border-radius: 16px !important;
  overflow: hidden !important;
  margin-bottom: 20px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border-radius: 16px !important;
  overflow: hidden !important;
  border: 1px solid rgba(255,255,255,.05) !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
  border-radius: 12px !important;
  background: rgba(255,255,255,.03) !important;
  border: 1px solid rgba(255,255,255,.07) !important;
}
div[data-testid="stSuccess"] {
  background: rgba(0,192,122,.08) !important;
  border-color: rgba(0,192,122,.2) !important;
}
div[data-testid="stError"] {
  background: rgba(255,64,87,.08) !important;
  border-color: rgba(255,64,87,.2) !important;
}
div[data-testid="stWarning"] {
  background: rgba(245,166,35,.08) !important;
  border-color: rgba(245,166,35,.2) !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
  background: rgba(255,255,255,.04) !important;
  border-radius: 10px !important;
  padding: 3px !important;
  border: 1px solid rgba(255,255,255,.06) !important;
  gap: 2px !important;
}
[data-baseweb="tab"] {
  border-radius: 8px !important;
  color: rgba(240,240,245,.35) !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  background: transparent !important;
  padding: 6px 14px !important;
  transition: all .14s !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: rgba(123,110,246,.12) !important;
  color: #7B6EF6 !important;
  font-weight: 600 !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display:none !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: #7B6EF6 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,.02); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.08); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.14); }


/* ── Hero card tag pills ── */
.nf-tag {
  display: inline-flex !important;
  align-items: center !important;
  border: 1px solid rgba(255,255,255,.10) !important;
  border-radius: 20px !important;
  padding: 4px 10px !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  color: rgba(240,240,245,.28) !important;
  background: transparent !important;
  line-height: 1.4 !important;
}
.nf-tag-avail {
  border-color: rgba(0,192,122,.2) !important;
  color: #00C07A !important;
  background: rgba(0,192,122,.10) !important;
}
.nf-tag-over {
  border-color: rgba(255,64,87,.2) !important;
  color: #FF4057 !important;
  background: rgba(255,64,87,.10) !important;
}
</style>
"""


# img onerror executes JS in main page context — beats Emotion CSS inline styles.
# Injects a custom fixed topbar + hamburger on mobile. Sidebar toggled via programmatic .click().
_LAYOUT_PATCH = (
    '<div style="display:none"><img src="x" onerror="'
    "(function(){if(window.__nfP)return;window.__nfP=1;"
    "var d=document;"
    "function isMob(){return window.innerWidth<=768;}"
    # Fix inline layout styles (Emotion overrides !important)
    "function p(){"
    "var sbh=d.querySelector('[data-testid=stSidebarHeader]');"
    "if(sbh){"
    "sbh.style.setProperty('height','0','important');"
    "sbh.style.setProperty('min-height','0','important');"
    "sbh.style.setProperty('overflow','hidden','important');"
    "sbh.style.setProperty('padding','0','important');"
    "sbh.style.setProperty('margin','0','important');}"
    "var sc=d.querySelector('[data-testid=stSidebarContent]');"
    "if(sc)sc.style.setProperty('padding-top','0','important');"
    "var su=d.querySelector('[data-testid=stSidebarUserContent]');"
    "if(su)su.style.setProperty('padding-top','0','important');"
    "var mb=d.querySelector('[data-testid=stMainBlockContainer]');"
    "if(mb)mb.style.setProperty('padding-top',isMob()?'64px':'24px','important');"
    "var mn=d.querySelector('section[data-testid=stMain]');"
    "if(mn&&isMob()){"
    "mn.style.setProperty('margin-left','0','important');"
    "mn.style.setProperty('width','100%','important');}}"
    # Sidebar state: collapse button exists only when sidebar is open
    "function isSbOpen(){return !!d.querySelector('[data-testid=stSidebarCollapseButton]');}"
    "function openSb(){"
    "var b=d.querySelector('[data-testid=stSidebarCollapsedControl] button');"
    "if(b)b.click();}"
    "function closeSb(){"
    "var b=d.querySelector('[data-testid=stSidebarCollapseButton] button');"
    "if(b)b.click();}"
    # Backdrop (appears between sidebar and main content)
    "function showBd(){"
    "if(d.getElementById('nf-backdrop'))return;"
    "var bd=d.createElement('div');"
    "bd.id='nf-backdrop';"
    "bd.style.cssText='position:fixed;inset:0;top:52px;background:rgba(0,0,0,.55);z-index:1040;backdrop-filter:blur(2px);-webkit-backdrop-filter:blur(2px);';"
    "bd.onclick=closeSb;"
    "d.body.appendChild(bd);}"
    "function hideBd(){var bd=d.getElementById('nf-backdrop');if(bd)bd.remove();}"
    # Custom topbar: fixed dark bar + SVG hamburger button, injected into body
    "function setupBar(){"
    "if(!isMob()||d.getElementById('nf-bar'))return;"
    "var bar=d.createElement('div');"
    "bar.id='nf-bar';"
    "bar.style.cssText='position:fixed;top:0;left:0;right:0;height:52px;"
    "background:rgba(8,9,14,.97);z-index:1100;display:flex;align-items:center;"
    "padding:0 6px;border-bottom:1px solid rgba(255,255,255,.06);"
    "-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);';"
    "var btn=d.createElement('button');"
    "btn.style.cssText='width:44px;height:44px;background:transparent;border:none;"
    "cursor:pointer;display:flex;align-items:center;justify-content:center;border-radius:8px;flex-shrink:0;';"
    "var ns='http://www.w3.org/2000/svg';"
    "var svg=d.createElementNS(ns,'svg');"
    "svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('width','22');svg.setAttribute('height','22');"
    "svg.setAttribute('fill','none');svg.setAttribute('stroke','rgba(240,240,245,.8)');"
    "svg.setAttribute('stroke-width','2.5');svg.setAttribute('stroke-linecap','round');"
    "[[3,7,21,7],[3,12,21,12],[3,17,21,17]].forEach(function(c){"
    "var l=d.createElementNS(ns,'line');"
    "l.setAttribute('x1',c[0]);l.setAttribute('y1',c[1]);"
    "l.setAttribute('x2',c[2]);l.setAttribute('y2',c[3]);"
    "svg.appendChild(l);});"
    "btn.appendChild(svg);"
    "btn.onclick=function(){if(isSbOpen())closeSb();else openSb();};"
    "bar.appendChild(btn);"
    "d.body.appendChild(bar);}"
    # Sync backdrop with sidebar state
    "function syncBd(){if(!isMob()){hideBd();return;}if(isSbOpen())showBd();else hideBd();}"
    # Boot sequence
    "p();[80,300,700,1500].forEach(function(ms){setTimeout(p,ms)});"
    "setTimeout(setupBar,100);"
    "[300,700,1500,3000].forEach(function(ms){setTimeout(function(){setupBar();syncBd();},ms)});"
    # Watch DOM for sidebar open/close and page navigation
    "var t;new MutationObserver(function(){clearTimeout(t);t=setTimeout(function(){"
    "p();if(isMob()){setupBar();syncBd();}},25);"
    "}).observe(d.body,{childList:true,subtree:true});"
    "})()\">"
    "</div>"
)


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(_LAYOUT_PATCH, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(mes_key: str = "mes_global") -> str:
    with st.sidebar:
        # Brand header — st.html() bypasses markdown parser entirely
        st.html(
            '<div style="background:rgba(8,9,14,1);display:flex;align-items:center;gap:9px;'
            'padding:20px 16px 16px;'
            'border-bottom:1px solid rgba(255,255,255,.06);'
            'margin-bottom:4px">'
            '<div style="width:30px;height:30px;border-radius:9px;'
            'background:#7B6EF6;flex-shrink:0;display:flex;'
            'align-items:center;justify-content:center;'
            'font-size:15px;font-weight:900;color:#fff;letter-spacing:-.03em">N</div>'
            '<div style="flex:1;min-width:0">'
            '<div style="font-size:13px;font-weight:700;color:#F0F0F5;'
            'letter-spacing:-.02em;line-height:1.3">Nassim Finance</div>'
            '<div style="font-size:10px;color:rgba(240,240,245,.28);'
            'margin-top:1px;line-height:1.3">nassimcenteno86@gmail.com</div>'
            '</div>'
            '</div>'
        )

        # Nav — PRINCIPAL
        st.markdown('<div class="nf-nav-section">Principal</div>', unsafe_allow_html=True)
        st.page_link("main.py",                         label="Dashboard",       icon=":material/dashboard:")
        st.page_link("pages/1_Ingresar_Gasto.py",       label="Ingresar Gasto",  icon=":material/add_circle:")

        # Nav — REPORTES
        st.markdown('<div class="nf-nav-section">Reportes</div>', unsafe_allow_html=True)
        st.page_link("pages/2_Gastos_Diarios.py",       label="Gastos Diarios",  icon=":material/calendar_month:")
        st.page_link("pages/3_Por_Categoria.py",        label="Por Categoría",   icon=":material/donut_large:")
        st.page_link("pages/4_Analisis.py",             label="Análisis",        icon=":material/trending_up:")

        # Nav — CONFIGURAR
        st.markdown('<div class="nf-nav-section">Configurar</div>', unsafe_allow_html=True)
        st.page_link("pages/5_Presupuesto.py",          label="Presupuesto",     icon=":material/tune:")

        # Footer — month selector, visually separated like sb-foot in HTML
        st.markdown('<div class="nf-nav-footer"></div>', unsafe_allow_html=True)
        mes = st.selectbox(
            "",
            available_months(),
            format_func=fmt_month,
            key=mes_key,
            label_visibility="collapsed",
        )
    return mes


# ── Page components ───────────────────────────────────────────────────────────

def topbar(title: str, subtitle: str, show_status: bool = False) -> None:
    status = ""
    if show_status:
        status = (
            '<div style="display:flex;align-items:center;gap:5px;border:1px solid rgba(255,255,255,.10);'
            'border-radius:20px;padding:5px 11px;font-size:10px;font-weight:600;'
            'color:rgba(240,240,245,.28)">'
            '<span style="width:5px;height:5px;border-radius:50%;background:#00C07A;'
            'animation:blink 2.4s ease infinite;flex-shrink:0"></span>'
            'Datos actualizados</div>'
            '<style>@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}</style>'
        )
    st.html(
        '<div class="nf-topbar" style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:28px">'
        '<div>'
        f'<div class="nf-topbar-title" style="font-size:18px;font-weight:800;color:#F0F0F5;letter-spacing:-.03em">{title}</div>'
        f'<div style="font-size:11px;color:rgba(240,240,245,.28);margin-top:3px">{subtitle}</div>'
        '</div>'
        f'{status}'
        '</div>'
    )


def hero_card(spent: float, budget: float, month_label: str,
              pct: float, avail: float, trans: int, days_left: int) -> None:
    bar_color = RED if pct > 100 else AMBER if pct >= 80 else ACCENT
    bar_w     = min(pct, 100)

    # Build tag pills — using CSS classes (short strings, no long inline styles)
    avail_tag = (
        f'<span class="nf-tag nf-tag-avail">S/ {avail:,.0f} disponible</span>'
        if avail >= 0 else
        f'<span class="nf-tag nf-tag-over">S/ {abs(avail):,.0f} excedido</span>'
    )
    pct_tag   = f'<span class="nf-tag">{pct:.0f}% ejecutado</span>'
    trans_tag = f'<span class="nf-tag">{trans} transacciones</span>'
    days_tag  = (
        f'<span class="nf-tag">{days_left} días restantes</span>'
        if days_left > 0 else
        '<span class="nf-tag">Mes cerrado</span>'
    )

    # Join tags on ONE string — avoids multiline indentation → markdown code-block bug
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
            '<div style="padding-bottom:8px">'
            '<div style="font-size:13px;color:rgba(240,240,245,.28);margin-bottom:4px">de un presupuesto de</div>'
            f'<div style="font-size:22px;font-weight:700;color:rgba(240,240,245,.50);letter-spacing:-.02em">S/ {budget:,.0f}</div>'
            '</div>'
        )

    st.html(
        '<div class="nf-hero-card" style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);'
        'border-radius:20px;padding:36px 40px 32px;position:relative;overflow:hidden;margin-bottom:14px">'
        '<div style="font-size:9px;font-weight:700;color:rgba(240,240,245,.28);'
        'text-transform:uppercase;letter-spacing:.15em;margin-bottom:16px">'
        f'Gastado · {month_label}'
        '</div>'
        '<div style="display:flex;align-items:flex-end;gap:20px;margin-bottom:28px;flex-wrap:wrap">'
        f'<div class="nf-hero-amount" style="font-size:80px;font-weight:900;line-height:.95;letter-spacing:-.04em;color:#F0F0F5">S/ {spent:,.0f}</div>'
        f'{budget_line}'
        '</div>'
        '<div style="height:3px;background:rgba(255,255,255,.06);border-radius:3px;overflow:hidden;margin-bottom:14px">'
        f'<div style="height:100%;width:{bar_w:.1f}%;border-radius:3px;background:{bar_color};transition:width .8s"></div>'
        '</div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap">{tags_row}</div>'
        '</div>'
    )


_ALERT_COLORS = {RED, AMBER, GREEN}

def stat_cards(stats: list) -> None:
    cols = "1fr " * len(stats)
    cards_html = ""
    for s in stats:
        color = s.get("color", TXT)
        label = s.get("label", "")
        value = s.get("value", "")
        sub   = s.get("sub", "")
        # Value text is always white except for explicit alert colors (RED/AMBER/GREEN)
        value_color = color if color in _ALERT_COLORS else TXT
        cards_html += (
            f'<div style="background:{S1};border:1px solid {BORDER};border-radius:16px;'
            f'padding:20px 22px 18px;position:relative;overflow:hidden">'
            f'<div style="position:absolute;top:0;left:0;right:0;height:1px;'
            f'background:linear-gradient(90deg,{color},transparent)"></div>'
            f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
            f'letter-spacing:.14em;margin-bottom:12px">{label}</div>'
            f'<div style="font-size:28px;font-weight:800;letter-spacing:-.03em;line-height:1;'
            f'margin-bottom:5px;color:{value_color}">{value}</div>'
            f'<div style="font-size:11px;color:{TXT3}">{sub}</div>'
            '</div>'
        )
    st.html(
        f'<div class="nf-stat-grid" style="display:grid;grid-template-columns:{cols.strip()};gap:12px;margin-bottom:28px">'
        f'{cards_html}</div>'
    )


def section_hdr(title: str, badge_text: str = None, variant: str = "warn") -> None:
    BADGE_COLORS = {
        "warn": (AMBER, AMBER_LO),
        "ok":   (GREEN, GREEN_LO),
        "bad":  (RED,   RED_LO),
    }
    c, bg = BADGE_COLORS.get(variant, (AMBER, AMBER_LO))
    badge_html = ""
    if badge_text:
        badge_html = (
            f'<span style="font-size:10px;font-weight:600;padding:3px 9px;border-radius:20px;'
            f'color:{c};background:{bg}">{badge_text}</span>'
        )
    st.html(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'margin-bottom:8px;padding:0 2px">'
        f'<span style="font-size:12px;font-weight:700;color:{TXT};letter-spacing:-.01em">'
        f'{title}</span>{badge_html}</div>'
    )


def cat_list_rows(cats: list) -> None:
    rows_html = ""
    for c in cats:
        pct    = c.get("pct", 0.0)
        spent  = c.get("spent", 0.0)
        budget = c.get("budget", 0.0)
        name   = c.get("name", "")
        icon   = c.get("icon", "💰")
        bg     = c.get("bg", S2)
        color  = c.get("color", ACCENT)
        bar_w  = min(pct, 100)

        if pct > 100:
            fill_color = RED;   pct_color = RED
        elif pct >= 80:
            fill_color = AMBER; pct_color = AMBER
        elif pct == 0:
            fill_color = "rgba(255,255,255,.06)"
            pct_color  = "rgba(240,240,245,.25)"
        else:
            fill_color = color; pct_color = "rgba(240,240,245,.40)"

        pct_str    = f"{pct:.0f}%" if budget > 0 else "—"
        budget_str = (
            f'S/ {spent:,.0f} <span style="color:rgba(240,240,245,.2)">/ {budget:,.0f}</span>'
            if budget > 0 else f"S/ {spent:,.0f}"
        )

        rows_html += (
            '<div style="display:flex;align-items:center;gap:14px;padding:14px 20px;'
            'border-bottom:1px solid rgba(255,255,255,.03)">'
            f'<div style="width:34px;height:34px;border-radius:9px;background:{bg};'
            'display:flex;align-items:center;justify-content:center;'
            f'font-size:16px;flex-shrink:0">{icon}</div>'
            '<div style="flex:1;min-width:0">'
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px">'
            f'<span style="font-size:13px;font-weight:600;color:rgba(240,240,245,.85)">{name}</span>'
            f'<span style="font-size:11px;color:{TXT3}">{budget_str}</span>'
            '</div>'
            '<div style="height:2px;background:rgba(255,255,255,.05);border-radius:2px;overflow:hidden">'
            f'<div style="height:100%;width:{bar_w:.1f}%;background:{fill_color};border-radius:2px"></div>'
            '</div>'
            '</div>'
            f'<div style="flex-shrink:0;text-align:right;min-width:44px">'
            f'<div style="font-size:12px;font-weight:700;color:{pct_color}">{pct_str}</div>'
            '</div>'
            '</div>'
        )

    st.html(
        f'<div style="background:{S1};border:1px solid {BORDER};border-radius:16px;'
        f'overflow:hidden;margin-bottom:20px">{rows_html}</div>'
    )


def badge(text: str, kind: str = "neutral") -> str:
    styles = {
        "success": (GREEN_LO, "rgba(0,192,122,.2)",  GREEN),
        "warning": (AMBER_LO, "rgba(245,166,35,.2)", AMBER),
        "danger":  (RED_LO,   "rgba(255,64,87,.2)",  RED),
        "neutral": (S2,       BORDER2,               TXT2),
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


# ── Utility ───────────────────────────────────────────────────────────────────

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
