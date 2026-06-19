# Session Memory

**IMPORTANT: Read this file at the start of every session before doing anything else.**
This file is the single source of truth for ongoing context. Update it whenever algo significativo cambie.

---

## Project Overview

**Domain:** Personal Finance — registro de gastos y reportes mensuales
**Framework:** WAT (Workflows, Agents, Tools)
**Owner:** nassimcenteno86@gmail.com
**Moneda:** S/ PEN (Perú)
**Despliegue objetivo:** Streamlit Cloud (accesible desde celular como PWA — "Add to Home Screen")
**Storage:** Google Sheets (Service Account local, `st.secrets` en cloud)

---

## Estado actual — Last updated: 2026-06-19

### ✅ App Streamlit COMPLETADA Y FUNCIONANDO (diseño aprobado por el usuario)

La app en `app/` está operativa y con el diseño aprobado. Corre en `localhost:8501`.

**Lo que funciona:**
- Sidebar: brand (N morado + "Nassim Finance" + email), navegación por secciones (PRINCIPAL / REPORTES / CONFIGURAR), selector de mes al fondo con separador visual
- Gap superior eliminado: `padding-top: 24px` en el contenido principal (no los 96px que ponía Streamlit)
- Sidebar sin espacio vacío: `stSidebarHeader` colapsado a 0px, `stLogoSpacer` oculto
- Dashboard: hero KPI full-width + 3 stat cards + chart acumulado + lista de categorías
- Ingresar Gasto: form manual (monto con decimales OK, paso step=0.01) + tab de audio
- Gastos Diarios: stat cards + bar chart + tabla de transacciones
- Por Categoría: stat cards (valores en blanco salvo alertas RED/AMBER/GREEN) + donut + bar chart + lista
- Análisis: stat cards + line chart histórico + top categorías + tabla resumen
- Presupuesto: lista editable de presupuesto por categoría
- Conexión a Google Sheets funcionando (datos reales del usuario)

**Fixes implementados en esta sesión (2026-06-19):**
- Bug decimales: `step=0.01` en `number_input` de "Ingresar Gasto" (antes `step=1.0` causaba que 25.3 → 253)
- Gap superior: CSS `[data-testid="stMainBlockContainer"]{padding-top:24px!important}` + ocultar `stHeader`, `stHeaderFill`
- Sidebar gap: CSS `[data-testid="stSidebarHeader"]{height:0!important;overflow:hidden!important}` + ocultar `stLogoSpacer`
- Brand visible: cambiado a `st.html()` con `background:rgba(8,9,14,1)` explícito
- Stat cards "Por Categoría": valor siempre blanco salvo colores de alerta (RED/AMBER/GREEN), implementado con `_ALERT_COLORS = {RED, AMBER, GREEN}` en `theme.py`

---

## ⚠️ CRÍTICO: Gestión de procesos Streamlit en Windows

**`pkill -f streamlit` en Git Bash NO mata procesos nativos de Windows.** Causa acumulación de zombies en el mismo puerto 8501, y el servidor viejo sigue sirviendo código viejo.

**Forma correcta de reiniciar (PowerShell):**
```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'streamlit run app/main\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```
**O en Bash por PID:** `taskkill //F //PID <pid>` para cada proceso.

**Verificar puerto libre antes de arrancar:**
```bash
netstat -ano | grep ':8501' | grep LISTEN   # debe estar vacío
```

**Arrancar UNA instancia limpia:**
```bash
nohup streamlit run app/main.py --server.port 8501 --server.headless true --server.runOnSave true > /tmp/st.log 2>&1 &
```

**Verificar que el código nuevo cargó (no asumir):**
- Chrome headless en `/c/Program Files/Google/Chrome/Application/chrome.exe`
- Scripts CDP guardados en `C:\tmp\`: `cdp_probe.py` (estilos computados), `cdp_shot.py` (screenshot)
- `websockets` (asyncio) instalado en Python 3.14; `playwright`/`selenium` NO disponibles
- Diagnóstico clave: `myStyleInjected: true` + `stMainBlockContainer.paddingTop: 24px`

**Detalles internos de Streamlit 1.58 (bundle `index.dkY5s53S.js`):**
- `headerHeight: 3.75rem` (60px) hardcodeado
- `stMainBlockContainer` padding-top sin top-nav = **6rem = 96px** — sobreescribir con CSS `!important`
- `sidebarTopSpace: 6rem` — el espacio del sidebar viene del height de `stSidebarHeader` (60px logo spacer + botón)
- Selectores `[data-testid=...]` SÍ sobreviven al sanitizador de Streamlit en bloques `<style>`

---

## Próximos pasos — en orden de prioridad

### 1. Responsive mobile (APROBADO EN WIREFRAME, pendiente implementar)

El usuario usa la app **principalmente desde celular**. Wireframes discutidos y aprobados:

**Cambios a implementar:**
- **Stat cards**: de N cols → 2×2 grid en mobile (`@media (max-width: 768px)`)
- **Charts**: altura reducida a 160px en mobile (desktop: 220–280px)
- **Ingresar Gasto**: categoría + fecha en 2 cols en desktop → 1 col en mobile
- **Hero card**: font-size 80px → 52px en mobile
- **Padding main**: `24px 36px` → `16px` en mobile
- **Sidebar**: Streamlit ya colapsa automáticamente en mobile (hamburger nativo)

**Acceso desde celular post-deploy:**
- URL de Streamlit Cloud → abrir en Chrome/Safari móvil
- Android: menú `⋮` → "Instalar app" (PWA, sin barra de navegación)
- iOS: Share → "Añadir a pantalla de inicio"

### 2. Deploy a Streamlit Cloud

**Pasos:**
1. Crear repo GitHub (puede ser privado)
2. `git init && git add . && git commit -m "initial"` (desde el directorio del proyecto)
3. `git remote add origin <repo_url> && git push -u origin main`
4. Ir a share.streamlit.io → "New app" → conectar repo → `app/main.py`
5. En "Secrets": copiar contenido del `.env` local + credentials.json adaptado a formato TOML de `st.secrets`
6. El `sheets_client.py` ya tiene lógica dual: `.env` local / `st.secrets` en cloud (**verificar esto antes del deploy**)

**Archivo `.gitignore` necesario** (crear si no existe):
```
.env
credentials.json
token.json
.tmp/
__pycache__/
*.pyc
```

### 3. Pendientes menores
- [ ] Presupuesto (`5_Presupuesto.py`): confirmar que el guardado a Sheets funciona
- [ ] Audio tab en Ingresar Gasto: depende de `streamlit-mic-recorder` — verificar que está en `requirements.txt`

---

## Arquitectura de la app (`app/`)

### `theme.py` — sistema de diseño central

**Funciones exportadas:**
- `inject_css()` — inyecta CSS global + patch JS (`_LAYOUT_PATCH` via `img onerror`) que fuerza inline styles en `stMainBlockContainer`, `stSidebarHeader`, `stSidebarContent`. **Llamar al inicio de cada página.**
- `render_sidebar(mes_key)` → `str` — renderiza brand + nav + mes selector; retorna el mes seleccionado (`"YYYY-MM"`)
- `topbar(title, subtitle, show_status)` — cabecera de página con título y subtítulo
- `hero_card(spent, budget, month_label, pct, avail, trans, days_left)` — tarjeta KPI grande del dashboard
- `stat_cards(stats: list[dict])` — fila de stat cards. Cada dict: `{label, value, sub, color}`. Valores siempre blancos salvo `color in {RED, AMBER, GREEN}`
- `section_hdr(title, badge_text, variant)` — separador de sección con badge opcional
- `cat_list_rows(cats: list[dict])` — filas de categorías con barra de progreso. Cada dict: `{name, icon, bg, color, spent, budget, pct}`

**Tokens de color disponibles:** `BG, S1, S2, BORDER, BORDER2, TXT, TXT2, TXT3, ACCENT, ACCENT_LO, GREEN, GREEN_LO, RED, RED_LO, AMBER, AMBER_LO`

**Plotly:** `PLOTLY_GLASS` (layout base) + `PLOTLY_AXIS` (config de ejes). Uso: `fig.update_layout(**PLOTLY_GLASS, xaxis=dict(**PLOTLY_AXIS), ...)`

**Metadatos de categorías:** `CAT_META[cat]` → `{color, bg, icon}`

### `tools/sheets_client.py` — acceso a datos

- `get_gastos(mes: str)` → DataFrame `[fecha, categoria, descripcion, monto]`
- `get_all_gastos()` → DataFrame todos los meses
- `get_presupuesto(mes: str)` → DataFrame `[categoria, monto]`
- `add_gasto(row: dict)` — agrega fila a Sheet `gastos`
- `CATEGORIES` — lista de 11 categorías

---

## Estructura de archivos

```
app/
  main.py                      # Dashboard principal
  theme.py                     # Sistema de diseño — CSS, componentes, tokens
  pages/
    1_Ingresar_Gasto.py        # Form manual + audio
    2_Gastos_Diarios.py        # Stats + bar chart + tabla
    3_Por_Categoria.py         # Stats + donut + bar chart + lista
    4_Analisis.py              # Stats + line chart histórico + tabla
    5_Presupuesto.py           # Configuración de presupuesto por categoría
claude/
  MEMORY.md                    # Este archivo
.tmp/
  design_preview.html          # Mockup HTML de referencia (aprobado)
tools/
  sheets_client.py             # Leer/escribir Google Sheets
  audio_transcribe.py          # Audio → texto (OpenAI Whisper)
  expense_parser.py            # Texto libre → {monto, descripcion}
  setup_sheets.py              # Script one-time de configuración inicial
workflows/
  register_expense.md
  view_reports.md
.streamlit/
  config.toml                  # showSidebarNavigation = false
.env                           # GOOGLE_SHEETS_SPREADSHEET_ID (local, no subir a git)
credentials.json               # Google Service Account (gitignored)
requirements.txt
```

---

## Google Sheets — estructura de datos

**Sheet `gastos`:** `id | fecha | categoria | descripcion | monto | metodo`
**Sheet `presupuesto`:** `mes | categoria | monto` *(formato mes: YYYY-MM)*

---

## Filosofía de diseño (aprobada)

**Referencia visual:** Mercury Bank + Revolut + Linear.
- El número es el protagonista: hero KPI 80px/900 weight
- Color = señal únicamente (verde=disponible, rojo=excedido, amber=por vencer)
- Cero ruido: borders apenas visibles, fondos casi transparentes
- Paleta: `bg:#08090E`, `accent:#7B6EF6`, `green:#00C07A`, `red:#FF4057`, `amber:#F5A623`, `txt:#F0F0F5`

---

## Reglas permanentes

1. **Reiniciar Streamlit:** usar PowerShell `Stop-Process` — NO `pkill` desde Git Bash
2. **UI changes (`app/`):** diseñar mockup propio (experto fintech UX/UI) → aprobación → implementar
3. **Secrets:** nunca en código ni chat → `.env` local, `st.secrets` en cloud
4. **No crear/sobreescribir workflows sin preguntar**
5. **No pedir datos sensibles por chat** — indicar al usuario el archivo exacto donde ponerlos

---

## Cómo arrancar la próxima sesión

1. Leer este archivo
2. Verificar que no haya procesos zombie: `netstat -ano | grep ':8501' | grep LISTEN` — si hay más de uno, matar todos y arrancar uno limpio
3. Si Streamlit no está corriendo: `nohup streamlit run app/main.py --server.port 8501 --server.headless true > /tmp/st.log 2>&1 &`
4. Preguntar al usuario qué quiere hacer (opciones: responsive mobile, deploy, o algo nuevo)
