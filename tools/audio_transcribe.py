import io
import speech_recognition as sr


def transcribe(audio_bytes: bytes) -> str:
    """
    Transcribe audio bytes (WAV format) a texto en español peruano.
    Usa Google Web Speech API (gratuito, sin API key).
    Retorna string vacío si no se detectó voz.
    """
    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_bytes)

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio_data, language="es-PE")
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        raise RuntimeError(
            f"No se pudo conectar al servicio de transcripción: {exc}"
        ) from exc
