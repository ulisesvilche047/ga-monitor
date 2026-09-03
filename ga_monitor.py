#!/usr/bin/env python3
"""
Gameplay Alliance — Monitor de Órdenes Abiertas
Monitorea en tiempo real la apertura de nuevas órdenes de grabación
y despacha alertas Push instantáneas al celular (vía ntfy / Telegram / WhatsApp).
"""

import os
import sys
import json
import time
import argparse
import datetime
import urllib.request
import urllib.error
from pathlib import Path

# Añadir el directorio actual al path para importar notifiers
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

# Configurar salida UTF-8 para consolas Windows y evitar errores con emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from notifiers import dispatch_all

CONFIG_FILE = CURRENT_DIR / "config.json"
STATE_FILE = CURRENT_DIR / "seen_orders.json"

DEFAULT_CONFIG = {
    "notifications": {
        "ntfy": {
            "enabled": True,
            "topic": "ga_alertas_ulises_7b89",
            "priority": 4,
            "server": "https://ntfy.sh"
        },
        "telegram": {
            "enabled": False,
            "bot_token": "",
            "chat_id": ""
        },
        "whatsapp": {
            "enabled": False,
            "phone_number": "",
            "apikey": ""
        }
    },
    "monitoring": {
        "check_interval_seconds": 300,
        "notify_on_reopen": True,
        "notify_closing_soon": False,
        "closing_soon_percentage": 90.0,
        "category_filter": []
    },
    "api": {
        "url": "https://hdk2i43wuiw3272mtnjgwwsaby0bkood.lambda-url.sa-east-1.on.aws/",
        "dashboard_url": "https://gameplayalliance.gg/dashboard/"
    }
}


def load_config() -> dict:
    """Carga config.json con soporte de overrides por variables de entorno."""
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge básico
                for k, v in loaded.items():
                    if isinstance(v, dict) and k in cfg:
                        cfg[k].update(v)
                    else:
                        cfg[k] = v
        except Exception as e:
            print(f"[Aviso] No se pudo leer {CONFIG_FILE.name}: {e}. Usando configuración por defecto.", file=sys.stderr)

    # Permitir overrides por variables de entorno (ideal para GitHub Actions Secrets)
    env_topic = os.environ.get("NTFY_TOPIC")
    if env_topic:
        cfg["notifications"]["ntfy"]["topic"] = env_topic
        cfg["notifications"]["ntfy"]["enabled"] = True

    env_server = os.environ.get("NTFY_SERVER")
    if env_server:
        cfg["notifications"]["ntfy"]["server"] = env_server

    return cfg


def load_seen_orders() -> dict:
    """Carga el registro de órdenes ya vistas."""
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Aviso] No se pudo leer {STATE_FILE.name}: {e}. Iniciando estado nuevo.", file=sys.stderr)
        return {}


def save_seen_orders(seen: dict):
    """Guarda atómicamente el estado de órdenes vistas."""
    temp_file = STATE_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2, ensure_ascii=False)
    temp_file.replace(STATE_FILE)


def fetch_calls(api_url: str) -> list:
    """Consulta la API de Gameplay Alliance y retorna la lista de llamadas."""
    payload = json.dumps({"action": "list_calls"}).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "GameplayAlliance-Monitor/1.0"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("calls", [])
    except Exception as e:
        print(f"[Error API] Falló la consulta al servidor de Gameplay Alliance: {e}", file=sys.stderr)
        return []


def matches_category_filter(call: dict, filters: list) -> bool:
    """Verifica si la orden coincide con los filtros de categoría/género especificados."""
    if not filters:
        return True  # Si no hay filtros, pasan todas

    haystack = " ".join([
        call.get("titulo", ""),
        call.get("descripcion", ""),
        " ".join(call.get("categorias", [])),
        " ".join(call.get("juegos", []))
    ]).lower()

    for f in filters:
        if f.lower() in haystack:
            return True
    return False


def format_notification(call: dict, is_reopen: bool = False, dashboard_url: str = "") -> tuple[str, str]:
    """Genera el título y cuerpo enriquecido del mensaje."""
    call_id = call.get("call_id", "N/A")
    titulo = call.get("titulo", "Sin título")
    precio = call.get("precio_hora_usd")
    totales = call.get("horas_totales", 0)
    subidas = call.get("horas_subidas", 0)
    sin_limite = call.get("sin_limite", False)
    tipo = call.get("tipo", "Marketplace")
    categorias = call.get("categorias", [])
    juegos = call.get("juegos", [])

    pct = 0.0
    if not sin_limite and totales > 0:
        pct = min(100.0, (subidas / totales) * 100.0)

    if is_reopen:
        title = f"🔄 ¡Orden Reabierta! — {titulo}"
    else:
        title = f"🎮 ¡Nueva Orden Abierta! — {titulo}"

    lines = []
    lines.append(f"📌 {titulo}")
    lines.append(f"🆔 Orden: {call_id} · {tipo} · PC (teclado y mouse)")

    if precio is not None:
        lines.append(f"💰 Pago: US$ {precio:.2f} / hora (si se comercializa)")
    else:
        lines.append("💰 Pago: Por hora (ver dashboard)")

    if sin_limite:
        lines.append(f"⏱️ Horas: {subidas:.1f} hs subidas (Sin límite de horas)")
    else:
        lines.append(f"⏱️ Horas: {subidas:.1f} de {totales:.0f} hs pedidas ({pct:.1f}% completado)")

    if categorias:
        cats_str = ", ".join(categorias[:5])
        if len(categorias) > 5:
            cats_str += f" (+{len(categorias) - 5} más)"
        lines.append(f"📂 Géneros: {cats_str}")

    if juegos:
        lines.append(f"🎯 Juegos especificados: {', '.join(juegos)}")

    if dashboard_url:
        lines.append(f"\n🔗 Ver en dashboard:\n{dashboard_url}")

    message = "\n".join(lines)
    return title, message


def check_orders(cfg: dict, dry_run: bool = False) -> int:
    """
    Ejecuta un ciclo de chequeo. Retorna el número de alertas enviadas.
    """
    api_url = cfg["api"]["url"]
    dashboard_url = cfg["api"]["dashboard_url"]
    monitoring_cfg = cfg.get("monitoring", {})
    filters = monitoring_cfg.get("category_filter", [])
    notify_on_reopen = monitoring_cfg.get("notify_on_reopen", True)

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    seen = load_seen_orders()
    calls = fetch_calls(api_url)

    if not calls:
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No se recibieron órdenes o la API no respondió.")
        return 0

    alerts_sent = 0

    for call in calls:
        call_id = call.get("call_id")
        if not call_id:
            continue

        is_completed = bool(call.get("completo", False))
        horas_subidas = call.get("horas_subidas", 0.0)
        horas_totales = call.get("horas_totales", 0.0)
        titulo = call.get("titulo", "")

        prev = seen.get(call_id)

        # Caso 1: Orden completamente nueva
        is_new = (prev is None)

        # Caso 2: Orden que estaba completa/cerrada y ahora se reabrió
        is_reopened = False
        if prev is not None and prev.get("completo") is True and not is_completed:
            is_reopened = True

        should_notify = False
        reason = ""

        # Solo alertamos si la orden está ABIERTA (!is_completed)
        if not is_completed:
            if is_new:
                should_notify = True
                reason = "Nueva orden abierta"
            elif is_reopened and notify_on_reopen:
                should_notify = True
                reason = "Orden reabierta"

        # Aplicar filtro de categorías si aplica
        if should_notify and not matches_category_filter(call, filters):
            should_notify = False
            print(f"[{call_id}] {titulo} detectada abierta, pero omitida por filtro de categoría.")

        if should_notify:
            title, message = format_notification(call, is_reopen=is_reopened, dashboard_url=dashboard_url)
            print(f"\n⚡ [{reason.upper()}] Notificando: {call_id} — {titulo}")

            if not dry_run:
                dispatch_all(
                    title=title,
                    message=message,
                    url=dashboard_url,
                    tags=["video_game", "moneybag", "tada"],
                    priority=5,  # Máxima prioridad para despertar el celular
                    config=cfg
                )
                alerts_sent += 1
            else:
                print("[Dry Run] Notificación simulada (no enviada):")
                print(f"  Título: {title}")
                print(f"  Mensaje:\n{message}")

        # Actualizar estado de la orden en el registro
        seen[call_id] = {
            "call_id": call_id,
            "titulo": titulo,
            "completo": is_completed,
            "horas_subidas": horas_subidas,
            "horas_totales": horas_totales,
            "precio_hora_usd": call.get("precio_hora_usd"),
            "last_seen": now_str
        }

    if not dry_run:
        save_seen_orders(seen)

    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Chequeo completado. {len(calls)} órdenes analizadas, {alerts_sent} alertas despachadas.")
    return alerts_sent


def print_status(cfg: dict):
    """Muestra en terminal el estado actual de todas las órdenes en la plataforma."""
    api_url = cfg["api"]["url"]
    calls = fetch_calls(api_url)
    seen = load_seen_orders()

    print("\n" + "=" * 80)
    print("🎮 GAMEPLAY ALLIANCE — ESTADO DE ÓRDENES EN TIEMPO REAL")
    print("=" * 80)

    if not calls:
        print("No se pudieron cargar órdenes.")
        return

    for c in calls:
        cid = c.get("call_id", "")
        titulo = c.get("titulo", "")
        completo = c.get("completo", False)
        precio = c.get("precio_hora_usd", 0.0)
        tot = c.get("horas_totales", 0.0)
        sub = c.get("horas_subidas", 0.0)
        sin_lim = c.get("sin_limite", False)

        pct = 0.0 if tot == 0 else min(100.0, (sub / tot) * 100.0)
        estado_str = "🔴 CERRADA / COMPLETA" if completo else "🟢 ABIERTA"

        print(f"\n[{cid}] {titulo}")
        print(f"  Estado:     {estado_str}")
        print(f"  Precio:     US$ {precio:.2f} / hora")
        if sin_lim:
            print(f"  Progreso:   {sub:.1f} hs subidas (Sin límite)")
        else:
            print(f"  Progreso:   {sub:.1f} / {tot:.0f} hs ({pct:.1f}%)")
        print(f"  Categorías: {', '.join(c.get('categorias', [])[:6])}")
        if cid in seen:
            print(f"  Registrada: Sí (Última vez: {seen[cid].get('last_seen', 'N/A')[:19]})")
        else:
            print("  Registrada: Aún no guardada en el historial")

    print("\n" + "=" * 80)


def send_test(cfg: dict):
    """Envía una notificación de prueba instantánea al canal configurado."""
    print("\n🔔 Enviando notificación de prueba a tu celular...")
    title = "🎮 ¡Prueba Exitosa! — Gameplay Alliance Monitor"
    message = (
        "¡Excelente! Tu canal de notificaciones push está funcionando al 100%.\n\n"
        "A partir de ahora, cuando Gameplay Alliance publique una nueva orden o reabra horas "
        "para subir partidas, recibirás una alerta como esta en tu celular al instante."
    )
    res = dispatch_all(
        title=title,
        message=message,
        url=cfg["api"]["dashboard_url"],
        tags=["tada", "white_check_mark", "rocket"],
        priority=4,
        config=cfg
    )
    print(f"Resultado del despacho: {res}")


def main():
    parser = argparse.ArgumentParser(description="Monitor de Órdenes Abiertas de Gameplay Alliance")
    parser.add_argument("--check-once", action="store_true", help="Ejecuta un único chequeo y finaliza (ideal para cron / GitHub Actions)")
    parser.add_argument("--loop", action="store_true", help="Ejecuta de forma continua en bucle local con la frecuencia de config.json")
    parser.add_argument("--status", action="store_true", help="Muestra el estado en vivo de todas las órdenes")
    parser.add_argument("--test-notification", action="store_true", help="Envía una notificación de prueba al celular")
    parser.add_argument("--dry-run", action="store_true", help="Simula el chequeo sin enviar alertas ni guardar cambios de estado")
    parser.add_argument("--init-current", action="store_true", help="Registra las órdenes actuales como ya vistas sin disparar alertas")
    parser.add_argument("--reset-state", action="store_true", help="Borra el archivo de órdenes vistas (seen_orders.json)")

    args = parser.parse_args()
    cfg = load_config()

    if args.reset_state:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
            print("Archivo seen_orders.json eliminado con éxito.")
        else:
            print("seen_orders.json no existía.")
        return

    if args.status:
        print_status(cfg)
        return

    if args.test_notification:
        send_test(cfg)
        return

    if args.init_current:
        print("Guardando las órdenes actuales en seen_orders.json sin disparar alertas...")
        calls = fetch_calls(cfg["api"]["url"])
        seen = load_seen_orders()
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for c in calls:
            cid = c.get("call_id")
            if cid:
                seen[cid] = {
                    "call_id": cid,
                    "titulo": c.get("titulo", ""),
                    "completo": bool(c.get("completo", False)),
                    "horas_subidas": c.get("horas_subidas", 0.0),
                    "horas_totales": c.get("horas_totales", 0.0),
                    "precio_hora_usd": c.get("precio_hora_usd"),
                    "last_seen": now_str
                }
        save_seen_orders(seen)
        print(f"Se registraron {len(calls)} órdenes. En los próximos chequeos solo alertará por novedades.")
        return

    if args.loop:
        interval = cfg.get("monitoring", {}).get("check_interval_seconds", 300)
        print(f"Iniciando monitor en modo bucle continuo (frecuencia: cada {interval} segundos). Presiona Ctrl+C para detener.")
        try:
            while True:
                check_orders(cfg, dry_run=args.dry_run)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitor detenido por el usuario.")
        return

    # Por defecto, si no se pasan argumentos o se pasa --check-once
    check_orders(cfg, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
