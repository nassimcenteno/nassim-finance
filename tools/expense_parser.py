"""
Parsea texto libre (transcripción de audio o escritura rápida) y extrae
monto y descripción para pre-llenar el formulario de ingreso de gasto.
"""
import re

_WORD_TO_NUM: dict[str, float] = {
    "cero": 0, "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3,
    "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9,
    "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14,
    "quince": 15, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18,
    "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidos": 22,
    "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
    "veintiseis": 26, "veintisiete": 27, "veintiocho": 28,
    "veintinueve": 29, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
    "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90,
    "cien": 100, "ciento": 100, "doscientos": 200, "trescientos": 300,
    "cuatrocientos": 400, "quinientos": 500, "seiscientos": 600,
    "setecientos": 700, "ochocientos": 800, "novecientos": 900,
    "mil": 1000,
}

_AMOUNT_PATTERNS = [
    r"s/\s*(\d+(?:[.,]\d{1,2})?)",
    r"(\d+(?:[.,]\d{1,2})?)\s*soles?",
    r"(\d+(?:[.,]\d{1,2})?)",
]

_STRIP_VERBS = re.compile(
    r"\b(gast[eé]|pagu[eé]|cost[oó]|gast[oó]|pag[oó]|compré|compr[eé])\b",
    re.IGNORECASE,
)
_STRIP_AMOUNT = re.compile(
    r"s/\s*\d+(?:[.,]\d{1,2})?\s*|"
    r"\d+(?:[.,]\d{1,2})?\s*soles?\s*|"
    r"\b\d+(?:[.,]\d{1,2})?\b",
    re.IGNORECASE,
)
_STRIP_FILLER = re.compile(
    r"\b(en|de|para|por|un|una|el|la|los|las)\b", re.IGNORECASE
)


def _words_to_number(text: str) -> float | None:
    text = text.lower()
    for word, val in sorted(_WORD_TO_NUM.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(word)}\b", text):
            return float(val)
    return None


def parse(text: str) -> dict:
    """
    Extrae monto y descripción de un texto libre.

    Returns:
        {"monto": float | None, "descripcion": str}
    """
    monto: float | None = None

    for pattern in _AMOUNT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1).replace(",", ".")
            monto = float(raw)
            break

    if monto is None:
        monto = _words_to_number(text)

    descripcion = _STRIP_VERBS.sub("", text)
    descripcion = _STRIP_AMOUNT.sub("", descripcion)
    descripcion = _STRIP_FILLER.sub("", descripcion)
    descripcion = re.sub(r"\s{2,}", " ", descripcion).strip().capitalize()

    if not descripcion:
        descripcion = text.strip().capitalize()

    return {"monto": monto, "descripcion": descripcion}
