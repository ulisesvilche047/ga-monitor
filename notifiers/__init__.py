"""
Módulo de despachadores de notificaciones.
"""
from .ntfy import send_ntfy_notification
from .telegram import send_telegram_notification
from .whatsapp import send_whatsapp_notification

def dispatch_all(title: str, message: str, url: str = None, tags: list = None, priority: int = 4, config: dict = None) -> dict:
    """
    Envía la notificación por todos los canales habilitados en la configuración.
    """
    if config is None:
        return {}

    results = {}
    notif_cfg = config.get("notifications", {})

    # 1. ntfy (Push)
    ntfy_cfg = notif_cfg.get("ntfy", {})
    if ntfy_cfg.get("enabled", False):
        topic = ntfy_cfg.get("topic")
        server = ntfy_cfg.get("server", "https://ntfy.sh")
        prio = ntfy_cfg.get("priority", priority)
        results["ntfy"] = send_ntfy_notification(
            topic=topic,
            title=title,
            message=message,
            url=url,
            tags=tags or ["video_game", "bell"],
            priority=prio,
            server=server
        )

    # 2. Telegram (opcional)
    tg_cfg = notif_cfg.get("telegram", {})
    if tg_cfg.get("enabled", False):
        token = tg_cfg.get("bot_token")
        chat_id = tg_cfg.get("chat_id")
        results["telegram"] = send_telegram_notification(
            token=token,
            chat_id=chat_id,
            title=title,
            message=message,
            url=url
        )

    # 3. WhatsApp (opcional)
    wa_cfg = notif_cfg.get("whatsapp", {})
    if wa_cfg.get("enabled", False):
        phone = wa_cfg.get("phone_number")
        apikey = wa_cfg.get("apikey")
        results["whatsapp"] = send_whatsapp_notification(
            phone=phone,
            apikey=apikey,
            title=title,
            message=message
        )

    return results
