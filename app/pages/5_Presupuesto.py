import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.sheets_client import CATEGORIES, get_presupuesto, set_presupuesto
from app.theme import (
    inject_css, render_sidebar, topbar, stat_cards,
    fmt_month, GREEN, RED, AMBER, TXT, TXT3, ACCENT, ACCENT_LO, BORDER2, CAT_META,
)

st.set_page_config(page_title="Presupuesto · Nassim Finance",
                   page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
inject_css()
mes = render_sidebar()
topbar("Presupuesto", f"Configura tu presupuesto mensual · {fmt_month(mes)}")

# Page-specific CSS: form as cat-wrap card with compact rows
st.markdown("""
<style>
[data-testid="stForm"] {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    padding: 0 !important;
}
[data-testid="stForm"] > div > [data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    border-bottom: 1px solid rgba(255,255,255,.03) !important;
    padding: 4px 20px !important;
    gap: 0 !important;
}
[data-testid="stForm"] [data-testid="stNumberInput"] input {
    font-size: 13px !important;
    font-weight: 700 !important;
    text-align: right !important;
    padding: 8px 10px !important;
}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] {
    padding: 16px 20px !important;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60, show_spinner=False)
def _presupuesto(m): return get_presupuesto(m)


try:
    df_p = _presupuesto(mes)
except RuntimeError as e:
    st.error(str(e)); st.stop()

ppto_actual  = dict(zip(df_p["categoria"], df_p["monto"])) if not df_p.empty else {}
total_actual = sum(ppto_actual.values())
n_config     = len([v for v in ppto_actual.values() if v > 0])

# ── Stat summary ──────────────────────────────────────────────────────────────
stat_cards([
    {"label": "Total presupuestado",     "value": f"S/ {total_actual:,.0f}",
     "sub": fmt_month(mes),             "color": GREEN if total_actual > 0 else TXT3},
    {"label": "Categorías configuradas", "value": f"{n_config} / {len(CATEGORIES)}",
     "sub": "con presupuesto > 0",      "color": ACCENT},
])

# ── Budget form ───────────────────────────────────────────────────────────────
st.markdown(
    f'<p style="font-size:13px;color:{TXT3};margin-bottom:20px">'
    f'Ingresa S/ 0 en las categorías que no aplican este mes.</p>',
    unsafe_allow_html=True,
)

with st.form("form_ppto"):
    valores: dict[str, float] = {}
    total_preview = 0.0

    for cat in CATEGORIES:
        meta = CAT_META.get(cat, {"icon": "💰", "bg": "rgba(123,110,246,.12)"})
        col_left, col_right = st.columns([7, 2])
        with col_left:
            st.html(
                f'<div style="display:flex;align-items:center;gap:12px;padding:10px 0">'
                f'<div style="width:34px;height:34px;border-radius:9px;background:{meta["bg"]};'
                f'flex-shrink:0;display:flex;align-items:center;justify-content:center;'
                f'font-size:16px">{meta["icon"]}</div>'
                f'<span style="font-size:13px;font-weight:600;color:rgba(240,240,245,.85)">{cat}</span>'
                f'</div>'
            )
        with col_right:
            val = float(ppto_actual.get(cat, 0.0))
            new_val = st.number_input(
                cat, min_value=0.0, step=50.0,
                value=val, format="%.0f", key=f"p_{cat}",
                label_visibility="collapsed",
            )
        valores[cat] = new_val
        total_preview += new_val

    # Total preview
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    pct_change  = ((total_preview - total_actual) / total_actual * 100) if total_actual > 0 else 0
    change_str  = (f"{'↑' if pct_change >= 0 else '↓'} {abs(pct_change):.1f}% vs actual"
                   if total_actual > 0 else "")
    change_color = GREEN if pct_change >= 0 else RED

    st.markdown(f"""
    <div style="background:{ACCENT_LO};border:1px solid rgba(123,110,246,.25);
                border-radius:14px;padding:16px 22px;display:flex;
                justify-content:space-between;align-items:center;margin-bottom:12px">
      <div>
        <div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;
                    letter-spacing:.14em;margin-bottom:4px">Total presupuestado</div>
        <div style="font-size:11px;color:{change_color}">{change_str}</div>
      </div>
      <div style="font-size:28px;font-weight:800;color:#F0F0F5;letter-spacing:-.03em">
        S/ {total_preview:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    submitted = st.form_submit_button(
        "Guardar presupuesto", type="primary", use_container_width=True,
    )

if submitted:
    errors = []
    with st.spinner("Guardando..."):
        for cat, monto in valores.items():
            try:
                set_presupuesto(mes, cat, monto)
            except Exception as e:
                errors.append(f"{cat}: {e}")
    _presupuesto.clear()
    if errors:
        st.error("Errores al guardar:\n" + "\n".join(errors))
    else:
        st.success(f"✓ Presupuesto guardado — {fmt_month(mes)} · S/ {total_preview:,.0f} total")
