import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.sheets_client import get_all_gastos
from app.theme import (
    inject_css, render_sidebar, topbar, stat_cards, section_hdr, cat_list_rows,
    fmt_month, get_plotly_theme, ACCENT, GREEN, RED, AMBER, TXT, TXT3, CAT_META,
)

st.set_page_config(page_title="Análisis · Nassim Finance",
                   page_icon="📊", layout="wide", initial_sidebar_state="auto")
inject_css()
render_sidebar()
topbar("Análisis", "Tendencias y estadísticas históricas")


@st.cache_data(ttl=120, show_spinner=False)
def _all(): return get_all_gastos()


try:
    df = _all()
except RuntimeError as e:
    st.error(str(e)); st.stop()

if df.empty:
    st.info("No hay datos. Ingresa gastos primero."); st.stop()

df["mes"] = df["fecha"].dt.strftime("%Y-%m")
monthly = df.groupby("mes")["monto"].sum().reset_index()
monthly.columns = ["mes", "total"]
monthly = monthly.sort_values("mes")
monthly["label"] = monthly["mes"].apply(fmt_month)

if len(monthly) < 2:
    st.info("Se necesitan al menos 2 meses de datos para mostrar el análisis."); st.stop()

avg_mes   = monthly["total"].mean()
best_row  = monthly.loc[monthly["total"].idxmin()]
worst_row = monthly.loc[monthly["total"].idxmax()]

# ── Stat cards ────────────────────────────────────────────────────────────────
stat_cards([
    {"label": "Promedio mensual", "value": f"S/ {avg_mes:,.0f}",
     "sub": f"últimos {len(monthly)} meses", "color": TXT},
    {"label": "Mejor mes",        "value": fmt_month(best_row["mes"]).split(" ")[0],
     "sub": f"S/ {best_row['total']:,.0f} · mínimo",  "color": GREEN},
    {"label": "Peor mes",         "value": fmt_month(worst_row["mes"]).split(" ")[0],
     "sub": f"S/ {worst_row['total']:,.0f} · máximo",  "color": RED},
])

# ── Line chart — gasto mensual histórico ─────────────────────────────────────
dot_colors = [
    RED if v > avg_mes * 1.1 else AMBER if v > avg_mes else ACCENT
    for v in monthly["total"]
]
fig = go.Figure()
fig.add_shape(
    type="line",
    x0=monthly["label"].iloc[0], x1=monthly["label"].iloc[-1],
    y0=avg_mes, y1=avg_mes,
    line=dict(color="rgba(255,255,255,.08)", width=1, dash="dot"),
)
fig.add_trace(go.Scatter(
    x=monthly["label"], y=monthly["total"],
    fill="tozeroy",
    fillcolor="rgba(123,110,246,.08)",
    line=dict(color=ACCENT, width=1.5),
    mode="lines+markers",
    marker=dict(color=dot_colors, size=8, line=dict(color="#08090E", width=2)),
    hovertemplate="<b>%{x}</b><br>S/ %{y:,.0f}<extra></extra>",
))
_glass, _axis = get_plotly_theme()
fig.update_layout(
    **_glass,
    title=dict(text="Gasto mensual histórico",
               font=dict(size=12, color=TXT, family="system-ui"),
               x=0.02, xanchor="left", pad=dict(t=8, l=6)),
    height=210, showlegend=False,
    xaxis=dict(**_axis, title=""),
    yaxis=dict(**_axis, title=""),
    margin=dict(l=16, r=16, t=44, b=20),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Top categorías del mes más reciente ──────────────────────────────────────
mes_reciente = monthly["mes"].iloc[-1]
df_mes = df[df["mes"] == mes_reciente].copy()
top_cat = df_mes.groupby("categoria")["monto"].sum().nlargest(5).reset_index()
top_cat.columns = ["categoria", "gastado"]

if not top_cat.empty:
    cats = []
    for _, row in top_cat.iterrows():
        cat  = row["categoria"]
        meta = CAT_META.get(cat, {"color": ACCENT, "bg": "rgba(123,110,246,.12)", "icon": "💰"})
        cats.append({**meta, "name": cat, "spent": row["gastado"], "budget": 0.0, "pct": 0.0})
    section_hdr(f"Top categorías — {fmt_month(mes_reciente)}")
    cat_list_rows(cats)

# ── Resumen por mes (tabla) ───────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
section_hdr("Resumen por mes")
monthly_disp = monthly[["label", "total"]].copy()
monthly_disp["total"] = monthly_disp["total"].apply(lambda x: f"S/ {x:,.2f}")
monthly_disp.columns = ["Mes", "Total gastado"]
st.dataframe(
    monthly_disp.sort_values("Mes", ascending=False),
    use_container_width=True, hide_index=True,
)
