import os
from pathlib import Path

import gspread
import pandas as pd
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CATEGORIES = [
    "Alquiler",
    "Mantenimiento depa",
    "Estacionamiento",
    "Internet",
    "Celulares",
    "Seguro de auto",
    "Combustible",
    "Gastos establecidos",
    "Restaurantes",
    "Bolsita",
    "Extra",
]

_ROOT = Path(__file__).parent.parent


def _get_credentials() -> Credentials:
    creds_path = _ROOT / "credentials.json"
    if creds_path.exists():
        return Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
    try:
        import streamlit as st
        return Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=SCOPES
        )
    except Exception as exc:
        raise RuntimeError(
            "No se encontraron credenciales. Coloca credentials.json en la raíz "
            "del proyecto o configura gcp_service_account en Streamlit secrets."
        ) from exc


def _get_spreadsheet_id() -> str:
    sid = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    if sid:
        return sid
    try:
        import streamlit as st
        return st.secrets["SPREADSHEET_ID"]
    except Exception:
        raise RuntimeError(
            "GOOGLE_SHEETS_SPREADSHEET_ID no está configurado. "
            "Agrégalo al .env o a Streamlit secrets."
        )


def _get_worksheet(sheet_name: str) -> gspread.Worksheet:
    creds = _get_credentials()
    client = gspread.authorize(creds)
    return client.open_by_key(_get_spreadsheet_id()).worksheet(sheet_name)


def get_gastos(mes: str) -> pd.DataFrame:
    """Retorna todos los gastos del mes indicado (formato 'YYYY-MM')."""
    ws = _get_worksheet("gastos")
    records = ws.get_all_records()
    df = pd.DataFrame(records) if records else pd.DataFrame(
        columns=["id", "fecha", "categoria", "descripcion", "monto", "metodo"]
    )
    if df.empty:
        return df
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df[df["fecha"].dt.strftime("%Y-%m") == mes].copy()


def get_all_gastos() -> pd.DataFrame:
    """Retorna todos los gastos sin filtro de mes."""
    ws = _get_worksheet("gastos")
    records = ws.get_all_records()
    df = pd.DataFrame(records) if records else pd.DataFrame(
        columns=["id", "fecha", "categoria", "descripcion", "monto", "metodo"]
    )
    if df.empty:
        return df
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    return df


def add_gasto(row: dict) -> None:
    """Agrega una fila a la sheet 'gastos'."""
    ws = _get_worksheet("gastos")
    ws.append_row([
        row["id"],
        row["fecha"],
        row["categoria"],
        row["descripcion"],
        row["monto"],
        row["metodo"],
    ])


def delete_gasto(gasto_id: str) -> bool:
    """Elimina el gasto con el id indicado. Retorna True si lo encontró."""
    ws = _get_worksheet("gastos")
    cell = ws.find(gasto_id)
    if cell:
        ws.delete_rows(cell.row)
        return True
    return False


def get_presupuesto(mes: str) -> pd.DataFrame:
    """Retorna el presupuesto del mes indicado (formato 'YYYY-MM')."""
    ws = _get_worksheet("presupuesto")
    records = ws.get_all_records()
    df = pd.DataFrame(records) if records else pd.DataFrame(
        columns=["mes", "categoria", "monto"]
    )
    if df.empty:
        return df
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)
    return df[df["mes"] == mes].copy()


def set_presupuesto(mes: str, categoria: str, monto: float) -> None:
    """Crea o actualiza el presupuesto de una categoría en un mes."""
    ws = _get_worksheet("presupuesto")
    records = ws.get_all_records()
    for i, row in enumerate(records, start=2):
        if row["mes"] == mes and row["categoria"] == categoria:
            ws.update_cell(i, 3, monto)
            return
    ws.append_row([mes, categoria, monto])
