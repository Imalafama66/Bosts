# GHOST BOTS — Starter Python

Panel web inicial con FastAPI, autenticación, gestión básica de bots/contactos y estructura para WhatsApp Cloud API.

## Probar localmente
1. Instala Python 3.11 o superior.
2. Crea un entorno virtual (opcional).
3. Ejecuta `pip install -r requirements.txt`.
4. Copia `.env.example` a `.env` y cambia `SECRET_KEY`.
5. Ejecuta `uvicorn main:app --host 0.0.0.0 --port 8000`.
6. Abre `http://localhost:8000`.

## Railway
1. Sube el contenido de esta carpeta a un repositorio GitHub.
2. En Railway crea un proyecto con Deploy from GitHub Repo.
3. Añade un servicio PostgreSQL y configura `DATABASE_URL` con la referencia de Railway `${{Postgres.DATABASE_URL}}` (ajusta el nombre del servicio si es distinto).
4. Configura `SECRET_KEY` con un valor aleatorio largo.
5. Railway detecta el Dockerfile. Genera un dominio público desde Settings > Networking.

## WhatsApp
Para envíos reales necesitas una cuenta de Meta Business y WhatsApp Cloud API. Configura `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` y `WHATSAPP_VERIFY_TOKEN` como variables privadas en Railway. No las pongas en el frontend ni en GitHub.

El endpoint de webhook POST es solo un marcador inicial: antes de producción debe validar `X-Hub-Signature-256`, procesar eventos de forma segura y manejar duplicados. Respeta siempre el consentimiento de los destinatarios y las políticas/ventanas de mensajería de WhatsApp. No uses el sistema para spam ni mensajes no solicitados.

## Estado
Este starter sirve para pruebas y desarrollo. Antes de producción necesita pruebas, migraciones de base de datos, límites de uso, backups, auditoría de seguridad y endurecimiento del webhook.
