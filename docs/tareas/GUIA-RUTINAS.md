# Guía: rutinas que publican solas (sin Mac, sin nadie aprobando)

## El problema que resuelve
Las rutinas creadas desde una conversación de Cowork (`create_trigger`) nacen **sin repositorio**.
En ellas, `git push` a `msb70/sosvenezuela` da 403 («not in this session's authorized
repository set») y la única vía de publicar era el conector Hostinger, que **pide permiso en
cada sesión** → la rutina se queda en PENDING y no publica (02/09/2026).

La solución es que la rutina nazca **ligada al repo**: entonces `git push` funciona desde
`bash` sin pedir permiso, y `.github/workflows/deploy.yml` publica en <1 min.

## Paso a paso (se hace UNA vez por rutina, desde claude.ai/code)
1. Abre https://claude.ai/code y elige el repositorio **msb70/sosvenezuela** (si no aparece,
   instala/autoriza la app de GitHub de Claude para ese repo desde ahí).
2. Con el repo seleccionado, abre **Rutinas** (icono del reloj / «Routines») → **Nueva rutina**.
3. Nombre y horario (UTC):
   | Rutina | Cron UTC | Prompt |
   |---|---|---|
   | noticias-terremoto-venezuela-diario | `0 8 * * *` | `docs/tareas/prompts/noticias-venezuela-diario.md` |
   | noticias-terremoto-colombia-diario | `0 9 * * *` | `docs/tareas/prompts/noticias-colombia-diario.md` |
   | balance-colombia-diario | `0 18 * * *` | `docs/tareas/prompts/balance-colombia-diario.md` |
   | sitrep-ocha-venezuela-quincenal | `0 7 * * 5` | `docs/tareas/prompts/sitrep-ocha-venezuela-quincenal.md` |
4. Pega el contenido del archivo de prompt correspondiente (tal cual, entero).
5. Notificaciones: push ON.
6. Guarda y **lánzala a mano una vez** («Run now»). Abre la sesión y comprueba que:
   - no aparece ningún cuadro «¿Permitir…?»;
   - termina con un SHA y producción muestra `actualizado` de hoy.
7. Cuando la nueva funcione, **desactiva o borra la rutina vieja del mismo nombre**
   (las creadas desde Cowork; se ven en la misma lista de Rutinas) para que no corran dos.

## Cómo saber que va bien sin abrir nada
`curl -s "https://apoyo-fem-vzla.org/noticias.json?v=1" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['actualizado'],len(d['items']))"`
→ `actualizado` debe ser la fecha de hoy después de las 10:15 (VE) / 11:15 (CO) Madrid.
Si la rutina falla, manda una notificación push que empieza por «⚠️ NO PUBLICADO».

## Qué NO hacer
- No volver a meter WebFetch, WebSearch ni ninguna herramienta MCP en los prompts: piden permiso.
- No pushear a `main` desde el Mac sin antes reconciliar con producción (`reconciliar_noticias.py`
  + `reconciliar_html.py`): el deploy reconstruye la web entera desde `main`.
- No meter un token de la API de Hostinger en un prompt: da acceso a toda la cuenta.
