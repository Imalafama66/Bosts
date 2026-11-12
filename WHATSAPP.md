# WhatsApp Cloud API

Configura `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN` y `WHATSAPP_APP_SECRET` únicamente como variables privadas del servicio Railway. El envío exige consentimiento registrado en cada contacto. Respeta las políticas de WhatsApp; fuera de la ventana de atención pueden ser necesarias plantillas aprobadas.

El webhook GET verifica el token y el POST valida la firma HMAC. El procesamiento de eventos entrantes y las respuestas automáticas todavía no están implementados. Los perfiles de bots son registros administrativos, no procesos autónomos conectados.
