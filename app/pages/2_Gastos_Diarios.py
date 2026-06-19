import sys
import calendar
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.sheets_client import get_gastos
from app.theme import (
    inject_css, render_sidebar, topbar, stat_cards, section_hdr,
    fmt_month, ACCENT, AMBER, GREEN, TXT, TXT3, PLOTLY_GLASS, PLOTLY_AXIS, CAT_META, S1, BORDER,
)

st.set_page_config(page_title="Gastos Diarios · Nassim Finance",
                   page_icon="📅", layout="wide", initial_sidebar_state="expanded")
inject_css()
mes = render_sidebar()
topbar("Gastos Diarios", f"Gasto por día del mes · {fmt_month(mes)}")


@st.cache_data(ttl=60, show_spinner=False)
def _gastos(m): return get_gastos(m)


try:
    df = _gastos(mes)
except RuntimeError as e:
    st.error(str(e)); st.stop()

if df.empty:
    st.info("No hay gastos registrados para este mes."); st.stop()

y_int, m_int = (int(x) for x in mes.split("-"))
now = datetime.now()
days_in_month = calendar.monthrange(y_int, m_int)[1]
max_day = now.day if (y_int == now.year and m_int == now.month) else days_in_month

df["dia"] = df["fecha"].dt.day
daily = df.groupby("dia")["monto"].sum().reset_index()
all_days = pd.DataFrame({"dia": range(1, max_day + 1)})
daily = all_days.merge(daily, on="dia", how="left").fillna(0)
daily["acum"] = daily["monto"].cumsum()

# ── Stats ─────────────────────────────────────────────────────────────────────
dias_con_gasto = (daily["monto"] > 0).sum()
promedio_dia   = daily[daily["monto"] > 0]["monto"].mean()
dia_max_row    = daily.loc[daily["monto"].idxmax()]

stat_cards([
    {"label": "Total del mes",   "value": f"S/ {daily['monto'].sum():,.0f}",
     "sub": f"{len(df)} transacciones", "color": TXT},
    {"label": "Promedio diario", "value": f"S/ {promedio_dia:,.0f}",
     "sub": f"en días con gasto",       "color": ACCENT},
    {"label": "Día más alto",    "value": f"S/ {dia_max_row['monto']:,.0f}",
     "sub": f"Día {int(dia_max_row['dia'])}",  "color": AMBER},
    {"label": "Días con gasto",  "value": str(dias_con_gasto),
     "sub": f"de {max_day} días",       "color": GREEN},
])

# ── Bar chart ─────────────────────────────────────────────────────────────────
bar_colors = [ACCENT if v > 0 else "rgba(255,255,255,.05)" for v in daily["monto"]]
fig = go.Figure()
fig.add_trace(go.Bar(
    x=daily["dia"], y=daily["monto"],
    marker=dict(color=bar_colors, opacity=0.8),
    hovertemplate="Día %{x}<br><b>S/ %{y:,.0f}</b><extra></extra>",
))
fig.update_layout(
    **PLOTLY_GLASS,
    title=dict(text=f"Gasto por día — {fmt_month(mes)}",
               font=dict(size=12, color=TXT, family="system-ui"),
               x=0.02, xanchor="left", pad=dict(t=8, l=6)),
    height=220, showlegend=False, bargap=0.25,
    xaxis=dict(**PLOTLY_AXIS, dtick=1, title=""),
    yaxis=dict(**PLOTLY_AXIS, title=""),
    margin=dict(l=16, r=16, t=44, b=20),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Transaction list ──────────────────────────────────────────────────────────
section_hdr("Detalle de transacciones")

df_show = df[["fecha", "categoria", "descripcion", "monto"]].copy()
df_show = df_show.sort_values("fecha", ascending=False)

rows_html = ""
for _, row in df_show.iterrows():
    meta  = CAT_META.get(row["categoria"], {"icon": "💰", "bg": "rgba(123,110,246,.12)"})
    fecha = row["fecha"].strftime("%d %b") if hasattr(row["fecha"], "strftime") else str(row["fecha"])[:10]
    rows_html += f"""
    <div style="display:flex;align-items:center;gap:14px;padding:13px 20px;
                border-bottom:1px solid rgba(255,255,255,.03)">
      <div style="min-width:52px;font-size:11px;color:{TXT3};font-weight:500">{fecha}</div>
      <div style="width:34px;height:34px;border-radius:9px;background:{meta['bg']};
                  display:flex;align-items:center;justify-content:center;
                  font-size:15px;flex-shrink:0">{meta['icon']}</div>
      <div style="flex:1;min-width:0">
        <div style="font-size:13px;font-weight:600;color:rgba(240,240,245,.85);
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
          {row['descripcion']}</div>
        <div style="font-size:11px;color:{TXT3}">{row['categoria']}</div>
      </div>
      <div style="font-size:14px;font-weight:700;color:#F0F0F5;flex-shrink:0">
        S/ {row['monto']:,.2f}</div>
    </div>"""

st.markdown(
    f'<div style="background:{S1};border:1px solid {BORDER};border-radius:16px;'
    f'overflow:hidden;margin-bottom:20px">{rows_html}</div>',
    unsafe_allow_html=True,
)
