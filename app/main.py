import sys
import calendar
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.sheets_client import CATEGORIES, get_gastos, get_presupuesto
from app.theme import (
    inject_css, render_sidebar, topbar, hero_card, stat_cards,
    cat_list_rows, section_hdr, fmt_month, get_plotly_theme,
    ACCENT, ACCENT_LO, GREEN, RED, AMBER, TXT, TXT3, CAT_META,
)

st.set_page_config(
    page_title="Nassim Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="auto",
)
inject_css()
mes = render_sidebar()


@st.cache_data(ttl=60, show_spinner=False)
def _gastos(m):      return get_gastos(m)

@st.cache_data(ttl=60, show_spinner=False)
def _presupuesto(m): return get_presupuesto(m)


try:
    df_g = _gastos(mes)
    df_p = _presupuesto(mes)
except RuntimeError as e:
    st.error(str(e)); st.stop()

# ── Métricas ──────────────────────────────────────────────────────────────────
total_g    = df_g["monto"].sum()  if not df_g.empty else 0.0
total_p    = df_p["monto"].sum()  if not df_p.empty else 0.0
disponible = total_p - total_g
pct_total  = (total_g / total_p * 100) if total_p > 0 else 0.0
n_trans    = len(df_g)

y_int, m_int = (int(x) for x in mes.split("-"))
now = datetime.now()
if y_int == now.year and m_int == now.month:
    days_in_month = calendar.monthrange(y_int, m_int)[1]
    days_left     = days_in_month - now.day
    days_elapsed  = now.day
else:
    days_left    = 0
    days_elapsed = calendar.monthrange(y_int, m_int)[1]

ppto    = dict(zip(df_p["categoria"], df_p["monto"])) if not df_p.empty else {}
g_by_cat = df_g.groupby("categoria")["monto"].sum().to_dict() if not df_g.empty else {}
n_warn  = sum(1 for cat in CATEGORIES
              if ppto.get(cat, 0) > 0 and g_by_cat.get(cat, 0) / ppto[cat] >= 0.8)
avg_dia = total_g / max(days_elapsed, 1)

# ── Página ────────────────────────────────────────────────────────────────────
topbar("Dashboard", f"Resumen de gastos · {fmt_month(mes)}", show_status=True)

hero_card(total_g, total_p, fmt_month(mes), pct_total, disponible, n_trans, days_left)

stat_cards([
    {"label": "Disponible",
     "value": f"S/ {abs(disponible):,.0f}",
     "sub":   "restante este mes" if disponible >= 0 else "excedido",
     "color": GREEN if disponible >= 0 else RED},
    {"label": "Promedio diario",
     "value": f"S/ {avg_dia:,.0f}",
     "sub":   f"{n_trans} transacciones",
     "color": TXT},
    {"label": "Categorías al límite",
     "value": str(n_warn),
     "sub":   "≥80% del presupuesto",
     "color": AMBER if n_warn > 0 else GREEN},
])

# ── Area chart (gasto acumulado) ──────────────────────────────────────────────
if not df_g.empty:
    df_g["dia"] = df_g["fecha"].dt.day
    daily = df_g.groupby("dia")["monto"].sum().reset_index()
    all_days = pd.DataFrame({"dia": range(1, days_elapsed + 1)})
    daily = all_days.merge(daily, on="dia", how="left").fillna(0)
    daily["acum"] = daily["monto"].cumsum()

    fig = go.Figure()
    if total_p > 0:
        fig.add_shape(
            type="line",
            x0=0.5, x1=days_elapsed + 0.5,
            y0=total_p, y1=total_p,
            line=dict(color="rgba(255,255,255,.08)", width=1, dash="dot"),
        )
    fig.add_trace(go.Scatter(
        x=daily["dia"], y=daily["acum"],
        fill="tozeroy",
        fillcolor="rgba(123,110,246,.10)",
        line=dict(color=ACCENT, width=1.5),
        mode="lines",
        hovertemplate="Día %{x}<br>Acumulado: <b>S/ %{y:,.0f}</b><extra></extra>",
    ))
    lx, ly = daily["dia"].iloc[-1], daily["acum"].iloc[-1]
    fig.add_trace(go.Scatter(
        x=[lx], y=[ly], mode="markers",
        marker=dict(color=ACCENT, size=7, line=dict(color="#08090E", width=2)),
        showlegend=False, hoverinfo="skip",
    ))
    _glass, _axis = get_plotly_theme()
    fig.update_layout(
        **_glass,
        title=dict(text=f"Gasto acumulado — {fmt_month(mes)}",
                   font=dict(size=12, color=TXT, family="system-ui"),
                   x=0.02, xanchor="left", pad=dict(t=8, l=6)),
        height=180, showlegend=False,
        xaxis=dict(**_axis, dtick=3, title=""),
        yaxis=dict(**_axis, title=""),
        margin=dict(l=16, r=16, t=44, b=20),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Category list ─────────────────────────────────────────────────────────────
cats = []
for cat in CATEGORIES:
    g = g_by_cat.get(cat, 0.0)
    p = ppto.get(cat, 0.0)
    if g == 0 and p == 0:
        continue
    meta = CAT_META.get(cat, {"color": ACCENT, "bg": "rgba(123,110,246,.12)", "icon": "💰"})
    pct  = (g / p * 100) if p > 0 else (100.0 if g > 0 else 0.0)
    cats.append({**meta, "name": cat, "spent": g, "budget": p, "pct": pct})

cats.sort(key=lambda x: x["spent"], reverse=True)

if cats:
    badge_text = f"{n_warn} al límite" if n_warn > 0 else "Sin alertas"
    variant    = "warn" if 0 < n_warn <= 2 else "bad" if n_warn > 2 else "ok"
    section_hdr("Por categoría", badge_text, variant)
    cat_list_rows(cats)
elif df_g.empty:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;background:rgba(255,255,255,.02);
                border:1px solid rgba(255,255,255,.05);border-radius:20px;
                color:rgba(240,240,245,.28);font-size:14px">
      No hay datos para este mes.<br>
      <span style="font-size:12px">Configura tu presupuesto y empieza a ingresar gastos.</span>
    </div>""", unsafe_allow_html=True)
