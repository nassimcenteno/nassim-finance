"""
Script de configuración inicial.
Crea el Google Spreadsheet y las sheets necesarias.
Ejecutar una sola vez: python tools/setup_sheets.py
"""
import os
import sys
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

ROOT = Path(__file__).parent.parent
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def main():
    creds_path = ROOT / "credentials.json"
    if not creds_path.exists():
        print("ERROR: credentials.json no encontrado en la raíz del proyecto.")
        print("Descárgalo desde Google Cloud Console > APIs > Credenciales > Cuenta de Servicio.")
        sys.exit(1)

    creds = Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
    client = gspread.authorize(creds)

    spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "").strip() or None

    if not spreadsheet_id:
        print("\n" + "="*60)
        print("ACCIÓN REQUERIDA:")
        print("="*60)
        print("1. Ve a drive.google.com y crea un Google Sheets en blanco")
        print("2. Ponle nombre: 'Finanzas Personales'")
        print(f"3. Compártelo con este email (rol: Editor):")
        print(f"   {creds.service_account_email}")
        print("4. Copia el ID de la URL:")
        print("   https://docs.google.com/spreadsheets/d/[ESTE_ES_EL_ID]/edit")
        print("5. Agrégalo al .env:")
        print("   GOOGLE_SHEETS_SPREADSHEET_ID=[el ID copiado]")
        print("6. Corre este script de nuevo")
        print("="*60)
        sys.exit(0)

    sh = client.open_by_key(spreadsheet_id)
    print(f"Conectado a spreadsheet: '{sh.title}' (ID: {sh.id})")

    # Sheet: gastos
    try:
        ws = sh.worksheet("gastos")
        print("\nSheet 'gastos' ya existe — sin cambios.")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet("gastos", rows=2000, cols=6)
        ws.append_row(["id", "fecha", "categoria", "descripcion", "monto", "metodo"])
        ws.format("A1:F1", {"textFormat": {"bold": True}})
        print("\nSheet 'gastos' creada con headers.")

    # Sheet: presupuesto
    try:
        ws = sh.worksheet("presupuesto")
        print("Sheet 'presupuesto' ya existe — sin cambios.")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet("presupuesto", rows=500, cols=3)
        ws.append_row(["mes", "categoria", "monto"])
        ws.format("A1:C1", {"textFormat": {"bold": True}})
        print("Sheet 'presupuesto' creada con headers.")

    # Remove default Sheet1 if empty
    try:
        default = sh.worksheet("Sheet1")
        if not default.get_all_values():
            sh.del_worksheet(default)
    except gspread.WorksheetNotFound:
        pass

    print("\nSetup completado. Puedes correr la app con:")
    print("  streamlit run app/main.py")


if __name__ == "__main__":
    main()
