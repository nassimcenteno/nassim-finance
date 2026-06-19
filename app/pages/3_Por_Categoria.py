import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.sheets_client import CATEGORIES, get_gastos, get_presupuesto
from app.theme import (
    inject_css, render_sidebar, topbar, stat_cards, cat_list_rows, section_hdr,
    fmt_month, ACCENT, GREEN, RED, AMBER, TXT, TXT3, PLOTLY_GLASS, PLOTLY_AXIS, CAT_META, S1, BORDER,
)

st.set_page_config(page_title="Por Categoría · Nassim Finance",
                   page_icon="🗂️", layout="wide", initial_sidebar_state="auto")
inject_css()
mes = render_sidebar()
topbar("Por Categoría", f"Distribución y detalle · {fmt_month(mes)}")


@st.cache_data(ttl=60, show_spinner=False)
def _gastos(m):      return get_gastos(m)

@st.cache_data(ttl=60, show_spinner=False)
def _presupuesto(m): return get_presupuesto(m)


try:
    df_g = _gastos(mes)
    df_p = _presupuesto(mes)
except RuntimeError as e:
    st.error(str(e)); st.stop()

if df_g.empty:
    st.info("No hay gastos registrados para este mes."); st.stop()

by_cat = df_g.groupby("categoria")["monto"].sum().reset_index()
by_cat.columns = ["categoria", "gastado"]
ppto_d = dict(zip(df_p["categoria"], df_p["monto"])) if not df_p.empty else {}
by_cat["presupuesto"] = by_cat["categoria"].map(ppto_d).fillna(0)
by_cat["pct"] = by_cat.apply(
    lambda r: (r["gastado"] / r["presupuesto"] * 100) if r["presupuesto"] > 0 else None, axis=1
)
by_cat = by_cat.sort_values("gastado", ascending=False)

n_over   = int((by_cat["pct"] > 100).sum())
top_cat  = by_cat.iloc[0]

# ── Stat cards ────────────────────────────────────────────────────────────────
stat_cards([
    {"label": "Total gastado",       "value": f"S/ {by_cat['gastado'].sum():,.0f}",
     "sub": "este mes",              "color": TXT},
    {"label": "Categoría top",       "value": top_cat["categoria"],
     "sub": f"S/ {top_cat['gastado']:,.0f}", "color": ACCENT},
    {"label": "Categorías activas",  "value": str(len(by_cat)),
     "sub": f"de {len(CATEGORIES)}", "color": TXT},
    {"label": "Excedidas",           "value": str(n_over),
     "sub": "sobre presupuesto",     "color": RED if n_over > 0 else GREEN},
])

# ── Charts ────────────────────────────────────────────────────────────────────
DONUT_COLORS = [
    "#7B6EF6", "#00C07A", "#F5A623", "#FF4057", "#06B6D4",
    "#EC4899", "#A78BFA", "#34D399", "#F97316", "#60A5FA", "#FBBF24",
]

total_gastado = by_cat["gastado"].sum()
total_lbl = f"{total_gastado/1000:.1f}k" if total_gastado >= 1000 else f"{total_gastado:,.0f}"

st.markdown("""
<style>
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 0 0 100% !important;
        min-width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

col_pie, col_bar = st.columns(2, gap="large")

with col_pie:
    fig_pie = go.Figure(go.Pie(
        labels=by_cat["categoria"],
        values=by_cat["gastado"],
        hole=0.6,
        textinfo="none",
        opacity=0.85,
        marker=dict(colors=DONUT_COLORS, line=dict(color="#08090E", width=2)),
        hovertemplate="<b>%{label}</b><br>S/ %{value:,.0f} · %{percent}<extra></extra>",
    ))
    fig_pie.update_layout(
        **PLOTLY_GLASS,
        title=dict(text="Distribución", font=dict(size=12, color=TXT, family="system-ui"),
                   x=0.02, xanchor="left", pad=dict(t=8, l=6)),
        height=280, showlegend=False,
        annotations=[
            dict(text="TOTAL", x=0.5, y=0.58, showarrow=False,
                 font=dict(size=9, color="rgba(240,240,245,.4)", family="system-ui")),
            dict(text=f"<b>S/ {total_lbl}</b>", x=0.5, y=0.44, showarrow=False,
                 font=dict(size=14, color=TXT, family="system-ui")),
        ],
        margin=dict(l=16, r=16, t=44, b=16),
    )
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

with col_bar:
    top5 = by_cat.head(5)
    max_spent = top5["gastado"].max() if not top5.empty else 1
    bars_html = ""
    for _, row in top5.iterrows():
        cat  = row["categoria"]
        meta = CAT_META.get(cat, {"color": ACCENT, "icon": "💰"})
        pct_w = (row["gastado"] / max_spent * 100) if max_spent > 0 else 0
        bars_html += (
            '<div style="display:flex;align-items:center;gap:10px;padding:7px 0">'
            f'<span style="font-size:14px;width:20px;text-align:center;flex-shrink:0">{meta["icon"]}</span>'
            '<div style="flex:1;min-width:0">'
            '<div style="display:flex;justify-content:space-between;margin-bottom:5px">'
            f'<span style="font-size:11px;font-weight:600;color:rgba(240,240,245,.75);'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:60%">{cat}</span>'
            f'<span style="font-size:11px;font-weight:700;color:#F0F0F5;flex-shrink:0">S/ {row["gastado"]:,.0f}</span>'
            '</div>'
            '<div style="height:3px;background:rgba(255,255,255,.05);border-radius:3px">'
            f'<div style="height:100%;width:{pct_w:.1f}%;background:{meta["color"]};border-radius:3px"></div>'
            '</div>'
            '</div></div>'
        )
    st.html(
        '<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);'
        'border-radius:16px;padding:20px 22px 14px;margin-bottom:20px">'
        f'<div style="font-size:12px;font-weight:700;color:#F0F0F5;margin-bottom:16px">Top categorías</div>'
        f'{bars_html}</div>'
    )

# ── Category list ─────────────────────────────────────────────────────────────
cats = []
for _, row in by_cat.iterrows():
    cat  = row["categoria"]
    meta = CAT_META.get(cat, {"color": ACCENT, "bg": "rgba(123,110,246,.12)", "icon": "💰"})
    pct  = row["pct"] if row["pct"] is not None else (100.0 if row["gastado"] > 0 else 0.0)
    cats.append({**meta, "name": cat, "spent": row["gastado"],
                 "budget": row["presupuesto"], "pct": pct})

section_hdr("Todas las categorías")
cat_list_rows(cats)

# ── Transaction detail ────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
cat_opts = ["Todas"] + by_cat["categoria"].tolist()
cat_sel  = st.selectbox("Ver transacciones de", cat_opts)

df_det = df_g if cat_sel == "Todas" else df_g[df_g["categoria"] == cat_sel]
df_det = df_det[["fecha", "categoria", "descripcion", "monto"]].copy()
df_det["fecha_str"] = df_det["fecha"].dt.strftime("%d/%m/%Y")
df_det["monto_str"] = df_det["monto"].apply(lambda x: f"S/ {x:,.2f}")
display = df_det[["fecha_str", "categoria", "descripcion", "monto_str"]].copy()
display.columns = ["Fecha", "Categoría", "Descripción", "Monto"]
st.dataframe(display.sort_values("Fecha", ascending=False),
             use_container_width=True, hide_index=True)
