# 🎮 Gameplay Alliance — Monitor de Órdenes Abiertas (Alertas Push 24/7)

Sistema automatizado para detectar en tiempo real la apertura o reapertura de órdenes de grabación en **[Gameplay Alliance](https://gameplayalliance.gg/dashboard/)** y enviarte una **notificación Push inmediata a tu celular** con el título, recompensa por hora en USD, horas disponibles y enlace directo.

Diseñado específicamente para personas que pasan muchas horas fuera de casa o no pueden mantener su PC encendida.

---

## 🚀 Paso 1: Configurar las Notificaciones en tu Celular (Toma 1 minuto)

Usamos **ntfy**, un servicio gratuito, de código abierto y sin publicidad ni registros:

1. **Descarga la app en tu teléfono**:
   - [ntfy en Google Play (Android)](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
   - [ntfy en App Store (iPhone/iOS)](https://apps.apple.com/app/ntfy/id1625396347)
2. **Abre la app y suscríbete a tu tema**:
   - Toca el botón **`+`** (Suscribirse a tema).
   - Escribe exactamente este nombre de tema:
     ```
     ga_alertas_ulises_7b89
     ```
   - Toca **Suscribirse**.
3. *(Opcional)* En la configuración de la app en tu teléfono, asegúrate de permitir que emita sonido o vibración de alta prioridad.

---

## 📲 Paso 2: Probar que llegue a tu Celular

Con la app ya instalada y suscrita en tu teléfono:
1. En esta carpeta, haz doble clic en **`test_notification.bat`** (o ejecuta en la terminal `python ga_monitor.py --test-notification`).
2. Tu teléfono debería sonar y mostrar la notificación de prueba al instante.

---

## ☁️ Paso 3: Ejecución 24/7 en la Nube (Con la PC Apagada)

Para que el monitor funcione las 24 horas del día, los 7 días de la semana sin que tengas que dejar tu PC encendida, ya dejamos configurado **GitHub Actions**:

1. Entra a [github.com](https://github.com/) e inicia sesión con tu cuenta.
2. Crea un **nuevo repositorio** (te recomendamos marcarlo como **Privado**):
   - Por ejemplo, nómbralo `ga-monitor`.
3. Sube los archivos de esta carpeta a ese repositorio en GitHub. Puedes hacerlo con Git desde la terminal:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/ga-monitor.git
   git push -u origin main
   ```
4. En tu repositorio de GitHub, ve a la pestaña **Actions**:
   - Si te pregunta si deseas habilitar los workflows, haz clic en **Enable Workflows**.
5. En la configuración del repositorio:
   - Ve a **Settings** -> **Actions** -> **General**.
   - En la sección **Workflow permissions**, selecciona **"Read and write permissions"** y guarda los cambios. *(Esto permite que el bot recuerde qué órdenes ya te avisó para no repetirlas)*.
6. ¡Listo! GitHub ejecutará el monitor automáticamente **cada 10 minutos**. Apenas Gameplay Alliance publique una nueva orden, te llegará la notificación al celular.

---

## 💻 Paso 4: Ejecución Local en tu PC (Opcional)

Si en algún momento estás usando tu computadora y quieres que revise cada 5 minutos:
- Haz doble clic en **`run_local.bat`**. Se abrirá una ventana que chequeará periódicamente en segundo plano.

---

## ⚙️ Personalización (`config.json`)

Puedes editar el archivo `config.json` para ajustar tus preferencias:

```json
{
  "notifications": {
    "ntfy": {
      "enabled": true,
      "topic": "ga_alertas_ulises_7b89",
      "priority": 4,
      "server": "https://ntfy.sh"
    }
  },
  "monitoring": {
    "check_interval_seconds": 300,
    "notify_on_reopen": true,
    "category_filter": []
  }
}
```

- **`topic`**: Puedes cambiar el nombre de tu canal si deseas otro. Solo recuerda actualizar la suscripción en la app del celular.
- **`category_filter`**: Si solo quieres enterarte de géneros específicos (por ejemplo: RPG y Mundo Abierto), puedes colocar:
  ```json
  "category_filter": ["RPG", "Mundo abierto", "Action"]
  ```
  Si lo dejas vacío `[]`, te alertará de **todas** las órdenes abiertas.
- **`notify_on_reopen`**: `true` para avisarte si una orden que estaba llena vuelve a abrir cupos de horas.

---

## 🛠️ Comandos útiles desde la terminal

- Ver el estado de todas las órdenes en vivo:
  ```bash
  python ga_monitor.py --status
  ```
- Hacer una pasada única de verificación:
  ```bash
  python ga_monitor.py --check-once
  ```
- Enviar mensaje de prueba al celular:
  ```bash
  python ga_monitor.py --test-notification
  ```
- Reiniciar el historial de órdenes vistas:
  ```bash
  python ga_monitor.py --reset-state
  ```
- Marcar las órdenes actuales como ya vistas sin enviar alertas:
  ```bash
  python ga_monitor.py --init-current
  ```
