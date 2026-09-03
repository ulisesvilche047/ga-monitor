"""
Despachador opcional de WhatsApp vía CallMeBot API.
"""
import urllib.parse
import urllib.request
import sys

def send_whatsapp_notification(phone: str, apikey: str, title: str, message: str) -> bool:
    if not phone or not apikey:
        return False

    clean_phone = "".join(ch for ch in phone if ch.isdigit() or ch == "+").lstrip("+")
    full_text = f"*{title}*\n\n{message}"
    encoded_text = urllib.parse.quote(full_text)

    url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={apikey}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GameplayAlliance-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[WhatsApp] Error al enviar mensaje: {e}", file=sys.stderr)
        return False
