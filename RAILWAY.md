# Despliegue en Railway

1. Sube el contenido del proyecto a un repositorio GitHub privado o público.
2. En Railway crea un proyecto desde ese repositorio; se detectará el `Dockerfile`.
3. Añade un servicio PostgreSQL y enlaza `DATABASE_URL` con la referencia del servicio, por ejemplo `${{Postgres.DATABASE_URL}}` si el servicio se llama `Postgres`.
4. Configura `SECRET_KEY` con un valor aleatorio de al menos 32 caracteres. No uses el ejemplo.
5. Mantén `ALLOW_REGISTRATION=true` solo durante el alta inicial; después cambia a `false`.
6. Espera el despliegue y revisa `/api/health` y los logs.

Variables opcionales de WhatsApp: consulta `WHATSAPP.md`. No las guardes en el repositorio ni en archivos del frontend.
