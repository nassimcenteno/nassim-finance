# Workflow: Ver Reportes y Análisis

## Objetivo
Consultar el estado de gastos vs presupuesto y obtener insights financieros.

## Páginas disponibles

### 1. Home — Resumen mensual (`app/main.py`)
- Selector de mes
- KPIs: presupuesto total, total gastado, disponible, nº de gastos
- Gráfico overlay: presupuesto vs gastado por categoría
- Barras de progreso por categoría con semáforo (🟢🟡🔴)

### 2. Gastos Diarios (`pages/2_Gastos_Diarios.py`)
- Gráfico de barras: gasto por día del mes
- Línea acumulada opcional
- Métricas: total, promedio diario, día con más gasto
- Tabla detallada de todas las transacciones

### 3. Por Categoría (`pages/3_Por_Categoria.py`)
- Pie chart de distribución del gasto
- Bar chart horizontal por monto
- Tabla: categoría / gastado / presupuesto / disponible / % usado
- Detalle de transacciones filtrado por categoría

### 4. Análisis (`pages/4_Analisis.py`)
- Tendencia de los últimos 6 meses por categoría (seleccionable)
- Top 5 gastos del mes actual
- Estadísticas: promedio diario, gasto mayor/menor, categoría dominante
- Gasto total mensual histórico

### 5. Presupuesto (`pages/5_Presupuesto.py`)
- Configurar montos por categoría para cualquier mes
- Pre-carga el presupuesto existente si ya fue definido
- Permite planificar con hasta 2 meses de anticipación

## Herramientas usadas
- `tools/sheets_client.py` → `get_gastos(mes)`, `get_presupuesto(mes)`, `get_all_gastos()`

## Prerequisitos
1. `credentials.json` o `st.secrets["gcp_service_account"]` configurado
2. `GOOGLE_SHEETS_SPREADSHEET_ID` en `.env` o `st.secrets`
3. Setup inicial ejecutado: `python tools/setup_sheets.py`

## Cómo correr la app
```bash
# Instalar dependencias (primera vez)
pip install -r requirements.txt

# Correr localmente
streamlit run app/main.py
```

## Actualizar presupuesto mensual
1. Ir a la página **Presupuesto**
2. Seleccionar el mes deseado
3. Completar los montos por categoría
4. Guardar — se actualiza en Google Sheets automáticamente

## Edge cases
- **Mes sin gastos**: las páginas muestran un mensaje informativo, sin crash
- **Mes sin presupuesto**: los gráficos muestran solo gastos, presupuesto en 0
- **Datos lentos**: Streamlit recarga desde Sheets en cada navegación; agregar `@st.cache_data(ttl=60)` si la latencia es molesta
