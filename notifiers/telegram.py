"""
Despachador opcional de notificaciones para Telegram Bot API.
"""
import json
import urllib.request
import urllib.error
import sys

def send_telegram_notification(token: str, chat_id: str, title: str, message: str, url: str = None) -> bool:
    if not token or not chat_id:
        return False

    text = f"*{title}*\n\n{message}"
    if url:
        text += f"\n\n🔗 [Abrir Dashboard]({url})"

    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Telegram] Error al enviar mensaje: {e}", file=sys.stderr)
        return False
