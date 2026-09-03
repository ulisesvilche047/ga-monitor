"""
Despachador de notificaciones Push instantáneas vía ntfy.sh
"""
import json
import urllib.request
import urllib.error
import sys

def send_ntfy_notification(
    topic: str,
    title: str,
    message: str,
    url: str = None,
    tags: list = None,
    priority: int = 4,
    server: str = "https://ntfy.sh"
) -> bool:
    """
    Envía una notificación Push instantánea a un tópico de ntfy.
    """
    if not topic or not topic.strip():
        print("[ntfy] Error: No se especificó un topic en la configuración.", file=sys.stderr)
        return False

    server = server.rstrip("/")
    endpoint = f"{server}"

    payload = {
        "topic": topic.strip(),
        "title": title,
        "message": message,
        "priority": priority,
        "tags": tags or ["video_game", "bell"]
    }

    if url:
        payload["click"] = url
        payload["actions"] = [
            {
                "action": "view",
                "label": "Abrir Dashboard",
                "url": url,
                "clear": False
            }
        ]

    data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data_bytes,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "GameplayAlliance-Monitor/1.0"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                print(f"[ntfy] Notificación push enviada con éxito al topic '{topic}' (HTTP {resp.status})")
                return True
            else:
                print(f"[ntfy] Respuesta inesperada del servidor: HTTP {resp.status}", file=sys.stderr)
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='replace')
        print(f"[ntfy] Error HTTP {e.code}: {err_msg}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[ntfy] Error de conexión: {e}", file=sys.stderr)
        return False
