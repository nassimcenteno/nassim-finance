import sys
import uuid
from datetime import date
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from tools.sheets_client import CATEGORIES, add_gasto
from tools.expense_parser import parse
from app.theme import inject_css, render_sidebar, topbar, GREEN, RED, ACCENT, S1, BORDER, TXT3

st.set_page_config(page_title="Ingresar Gasto · Nassim Finance",
                   page_icon="➕", layout="wide", initial_sidebar_state="auto")
inject_css()
render_sidebar()
topbar("Ingresar Gasto", "Registra un nuevo gasto")

st.markdown("""
<style>
[data-testid="stForm"] {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 20px !important;
    padding: 36px 40px 32px !important;
    max-width: 520px !important;
    margin: 16px auto 0 !important;
}
/* Big monto text input */
[data-testid="stForm"] input[placeholder="0.00"] {
    font-size: 32px !important;
    font-weight: 800 !important;
    letter-spacing: -.03em !important;
    padding-top: 14px !important;
    padding-bottom: 14px !important;
    line-height: 1 !important;
    /* re-enable pointer events (overrides the selectbox rule) */
    pointer-events: auto !important;
    caret-color: auto !important;
    user-select: auto !important;
    -webkit-user-select: auto !important;
}
@media (max-width: 768px) {
    [data-testid="stForm"] {
        max-width: 100% !important;
        padding: 24px 18px 20px !important;
        margin: 8px 0 0 !important;
        border-radius: 16px !important;
    }
    [data-testid="stForm"] input[placeholder="0.00"] {
        font-size: 24px !important;
    }
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 0 !important;
    }
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 0 0 100% !important;
        min-width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

if "prefill" not in st.session_state:
    st.session_state.prefill = {}
if "show_audio" not in st.session_state:
    st.session_state.show_audio = False

pf = st.session_state.prefill

with st.form("form_manual", clear_on_submit=True):
    st.html(
        f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
        f'letter-spacing:.15em;margin-bottom:20px">Nuevo gasto</div>'
    )

    st.html(
        f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
        f'letter-spacing:.14em;margin-bottom:6px">Monto</div>'
    )
    # text_input avoids Streamlit number_input's digit-shifting behavior on iOS.
    # We parse manually so "12.3" and "12,3" both register as 12.30.
    prefill_monto = f"{pf['monto']:.2f}" if pf.get("monto") else ""
    monto_raw = st.text_input(
        "Monto", value=prefill_monto, placeholder="0.00",
        label_visibility="collapsed", key="monto_field",
    )
    try:
        monto = max(0.0, round(float(monto_raw.replace(",", ".")), 2))
    except (ValueError, AttributeError):
        monto = 0.0

    col1, col2 = st.columns(2)
    with col1:
        st.html(
            f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
            f'letter-spacing:.14em;margin-bottom:6px">Categoría</div>'
        )
        default_cat = pf.get("categoria", CATEGORIES[0])
        idx = CATEGORIES.index(default_cat) if default_cat in CATEGORIES else 0
        categoria = st.selectbox("Categoría", CATEGORIES, index=idx, label_visibility="collapsed")
    with col2:
        st.html(
            f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
            f'letter-spacing:.14em;margin-bottom:6px">Fecha</div>'
        )
        fecha = st.date_input("Fecha", value=date.today(), label_visibility="collapsed")

    st.html(
        f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
        f'letter-spacing:.14em;margin-top:8px;margin-bottom:6px">Descripción</div>'
    )
    descripcion = st.text_input(
        "Descripción", value=pf.get("descripcion", ""),
        placeholder="ej. Almuerzo con el equipo",
        label_visibility="collapsed",
    )

    col_save, col_mic = st.columns([5, 1])
    with col_save:
        submitted = st.form_submit_button("Guardar gasto", type="primary", use_container_width=True)
    with col_mic:
        mic_clicked = st.form_submit_button("🎤", use_container_width=True)

# ── Handle save ───────────────────────────────────────────────────────────────
if submitted:
    if not descripcion.strip():
        st.error("Ingresa una descripción.")
    elif monto <= 0:
        st.error("El monto debe ser mayor a 0.")
    else:
        try:
            add_gasto({
                "id":          str(uuid.uuid4()),
                "fecha":       str(fecha),
                "categoria":   categoria,
                "descripcion": descripcion.strip(),
                "monto":       monto,
                "metodo":      "manual",
            })
            st.session_state.prefill = {}
            st.session_state.show_audio = False
            st.success(f"✓ Guardado — {descripcion.strip()} · S/ {monto:,.2f} · {categoria}")
        except Exception as e:
            st.error(f"Error al guardar: {e}")

if mic_clicked:
    st.session_state.show_audio = not st.session_state.show_audio
    st.rerun()

# ── Audio recorder ────────────────────────────────────────────────────────────
if st.session_state.show_audio:
    st.markdown(
        f'<div style="max-width:520px;margin:14px auto 0;background:{S1};'
        f'border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:24px 28px">'
        f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
        f'letter-spacing:.14em;margin-bottom:12px">Grabar voz</div>'
        f'<p style="font-size:13px;color:rgba(240,240,245,.5);margin:0 0 16px">Describe tu gasto '
        f'en voz alta. Ejemplo: <em>"Gasté cincuenta soles en almuerzo"</em></p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    try:
        from streamlit_mic_recorder import mic_recorder
        audio = mic_recorder(start_prompt="Grabar", stop_prompt="Detener", key="mic")
        if audio and audio.get("bytes"):
            with st.spinner("Transcribiendo..."):
                try:
                    from tools.audio_transcribe import transcribe
                    texto = transcribe(audio["bytes"])
                except RuntimeError as e:
                    st.error(str(e)); texto = ""
            if texto:
                st.markdown(
                    f'<div style="max-width:520px;margin:10px auto 0;background:{S1};'
                    f'border:1px solid {BORDER};border-radius:12px;padding:14px 18px">'
                    f'<div style="font-size:9px;font-weight:700;color:{TXT3};text-transform:uppercase;'
                    f'letter-spacing:.14em;margin-bottom:6px">Transcripción</div>'
                    f'<p style="margin:0;font-size:14px;color:#F0F0F5">"{texto}"</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                parsed = parse(texto)
                st.session_state.prefill = {
                    "descripcion": parsed["descripcion"],
                    "monto":       parsed["monto"] or 0.0,
                }
                st.session_state.show_audio = False
                st.info("Datos pre-cargados. Revisa y guarda el gasto.")
                st.rerun()
            else:
                st.warning("No se detectó voz. Intenta en un ambiente más silencioso.")
    except ImportError:
        st.warning("Instala `streamlit-mic-recorder` para usar esta función.")
