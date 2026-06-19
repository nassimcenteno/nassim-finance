# Workflow: Registrar un Gasto

## Objetivo
Agregar un nuevo gasto a Google Sheets desde la app Streamlit.

## Inputs requeridos
- Fecha del gasto
- Categoría (una de las 11 definidas)
- Descripción breve
- Monto en S/ (PEN)
- Método de ingreso: `manual` o `audio`

## Pasos

### Ruta A — Ingreso manual
1. Abrir la app: `streamlit run app/main.py`
2. Ir a la página **Ingresar Gasto** (sidebar)
3. Seleccionar tab **Manual**
4. Completar el formulario: fecha, categoría, descripción, monto
5. Clic en **Guardar**
6. Verificar el mensaje de confirmación

### Ruta B — Ingreso por audio
1. Abrir la app y navegar a **Ingresar Gasto**
2. Seleccionar tab **Audio**
3. Clic en **Grabar** y hablar claramente:
   - Ejemplo: "Gasté cincuenta soles en almuerzo"
   - Ejemplo: "Pagué 120 soles de combustible"
4. Clic en **Detener** cuando termines
5. Esperar la transcripción (1-3 segundos)
6. Revisar el texto transcrito
7. Ir a tab **Manual** → los campos monto y descripción estarán pre-llenados
8. Ajustar si es necesario y clic en **Guardar**

## Herramientas usadas
- `tools/audio_transcribe.py` — transcripción de audio (SpeechRecognition)
- `tools/expense_parser.py` — extracción de monto y descripción
- `tools/sheets_client.py` → `add_gasto(row)` — escritura en Google Sheets

## Edge cases
- **Audio no detectado**: reintentar en ambiente silencioso, o usar ingreso manual
- **Monto no extraído del audio**: el campo aparece en 0, ingresar manualmente
- **Error de conexión a Sheets**: verificar credenciales y SPREADSHEET_ID en `.env`
- **Categoría incorrecta sugerida**: ajustar en el selectbox antes de guardar

## Output esperado
Nueva fila en la sheet `gastos` con los 6 campos: `id`, `fecha`, `categoria`, `descripcion`, `monto`, `metodo`.
