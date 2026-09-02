Actualiza la sección de noticias de Venezuela del sitio de la FEM (https://apoyo-fem-vzla.org) con lo publicado en las últimas 24-48 horas sobre el terremoto del 24 de junio de 2026. Trabajas sin nadie delante: no preguntes nada, decide con el criterio guardado y explica tus decisiones al final.

=========================================================
0. LO QUE TE DEJA COLGADO (léelo antes de tocar nada)
=========================================================
Esta sesión es programada: NADIE puede aprobar un permiso. Cualquier herramienta que pida permiso deja la sesión en PENDING para siempre y la web sin actualizar (pasó el 02/09/2026 con un WebFetch a elnacional.com). Por tanto:
- PROHIBIDO `WebFetch` y `WebSearch`. Toda la prensa se lee con `curl` desde `bash` y con el script `docs/tareas/barrer_fuentes.py` del repo.
- PROHIBIDO cualquier herramienta con prefijo `mcp__remote-devices__*` (Desktop Commander, device_bash, project_memory_*, hostinger-api del Mac): necesitan el Mac encendido. **No existe `project_memory_read` aquí: el contexto está en el repo, en `docs/tareas/`.**
- NO uses NINGUNA herramienta MCP (ni `mcp__Hostinger_Connector__*` ni ninguna otra): todas piden permiso en una sesión programada. Se publica con `git push` a `main`: GitHub Actions construye la rama `deploy` y Hostinger la sirve en menos de 1 minuto. Esta rutina está ligada al repo `msb70/sosvenezuela`, así que el push funciona desde `bash`.


=========================================================
0-bis. AUTOCOMPROBACIÓN DE RED — ANTES DE NADA
=========================================================
```
curl -s -o /dev/null -w "%{http_code}\n" --max-time 20 "https://apoyo-fem-vzla.org/noticias.json"
```
Si NO devuelve `200` (p. ej. 403 del proxy o 000), **el entorno tiene la red cerrada y esta tarea no puede hacer nada útil**: no clones, no edites, no hagas commit ni push. Manda `PushNotification` («Noticias VE: red bloqueada en el entorno (HTTP <código>) — no publicado») y termina con una respuesta que empiece por «⚠️ NO PUBLICADO».

**Regla de oro: si cualquier script devuelve un código de salida distinto de 0, o si el barrido lee 0 fuentes, o si `reconciliar_*.py` falla, PARA. Un día sin noticias es legítimo; un día sin lectura NO lo es, y publicar `actualizado: hoy` sin haber leído nada es mentir en la web.**

=========================================================
1. CONTEXTO (del repo, no de la memoria)
=========================================================
```
git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv && cd /tmp/sv
cat docs/tareas/RUNBOOK-PUBLICAR.md docs/tareas/CRITERIO-VE.md
python3 .github/scripts/reconciliar_noticias.py     # une por id el JSON del repo con producción: PARTE SIEMPRE DE ESTE RESULTADO
```
Si `reconciliar_noticias.py` termina con error (no pudo leer producción), PARA: «⚠️ NO PUBLICADO» + push. Nunca publiques desde el JSON del repo a secas: pisarías lo que hay en la web.
Síguelos al pie de la letra. El criterio editorial manda sobre este prompt.

=========================================================
2. BARRER LA PRENSA
=========================================================
```
python3 docs/tareas/barrer_fuentes.py ve --dias 2; echo "exit=$?"
```
Si `exit` no es 0 (ninguna fuente respondió), PARA: «⚠️ NO PUBLICADO» + push. Mira también la línea `RESUMEN:` de stderr: si menos de la mitad de las fuentes respondieron, dilo en el resumen final.
Lista candidatos de El Nacional, Efecto Cocuyo, Crónica.Uno, La Patilla, Infobae, Noticias ONU y ReliefWeb por RSS/sitemap (~10 s). Para cada candidato que te interese: descarga el artículo con `curl -sL -A "<user-agent de Chrome>"`, confirma la fecha real (`article:published_time`), comprueba que la URL da 200 y lee el texto para el resumen. Mínimo 3 fuentes distintas si hay material. Si una fuente falla, sigue con las demás: nunca la sustituyas por WebFetch.

=========================================================
3. CRITERIO EDITORIAL
=========================================================
El de `CRITERIO-VE.md`. Resumen: entran terremoto, réplicas, reconstrucción, ayuda humanitaria, damnificados, educación y salud afectadas por el sismo, infraestructura y economía de la reconstrucción. Fuera farándula, política internacional y declaraciones político-partidistas. Titular con carga partidista → reescríbelo describiendo el hecho y atribuyéndolo al organismo que lo anuncia.

=========================================================
4. ESCRIBIR EL JSON CON UN SCRIPT, NUNCA A MANO
=========================================================
Script en `/tmp/add_noticias.py`: carga `noticias.json`, añade los items nuevos descartando los que ya tengan ese `id` O esa `url`, reordena por `(fecha, id)` descendente, pone `actualizado` en la fecha de HOY **aunque no haya nada nuevo**, y escribe con `json.dump(..., ensure_ascii=False, indent=2)`.
`id` con patrón `ve-AAAAMMDD-medio-tema`. `fuente` EXACTAMENTE igual que las cadenas ya existentes en el archivo.

=========================================================
5. VALIDAR — SI FALLA, NO PUBLIQUES
=========================================================
```
python3 -m json.tool noticias.json > /dev/null
python3 .github/scripts/validar_noticias.py noticias.json noticias-colombia.json
```

=========================================================
6. PUBLICAR: COMMIT + PUSH A main (sin conector, sin zip)
=========================================================
```
cd /tmp/sv
git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"
git add noticias.json                      # SOLO este archivo; nunca `git add -A`
git commit -m "Noticias VE $(date -u +%F): <resumen corto de lo que cambió>"
git pull --rebase origin main && git push origin main
git rev-parse --short HEAD              # apunta este SHA
```
Si el push falla por permisos, NO busques otra vía: `PushNotification` («Noticias VE: el push a main está bloqueado — la rutina no está ligada al repo») y respuesta que empieza por «⚠️ NO PUBLICADO».

=========================================================
7. VERIFICAR PRODUCCIÓN, NO EL PUSH
=========================================================
Espera 90 s y comprueba:
```
sleep 90; curl -s "https://apoyo-fem-vzla.org/noticias.json?v=$RANDOM" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['actualizado'],len(d['items']))"
```
Si no refleja tu cambio, GitHub a veces no dispara el workflow (pasó el 26/08): relánzalo con un commit vacío — `git commit --allow-empty -m "redeploy" && git push origin main` — y vuelve a comprobar a los 90 s. Si a la segunda sigue sin reflejarlo: `PushNotification` («Noticias VE: push OK pero producción no cambió») y respuesta que empieza por «⚠️ NO PUBLICADO», indicando el SHA.

**Que el push salga no es prueba de nada. La única prueba es esta comprobación.**

=========================================================
8. AL TERMINAR
=========================================================
Resume: cuántos items añadiste y de qué fuentes, qué descartaste y por qué, el SHA del commit y el `actualizado` + número de items que devolvió producción. Un día sin noticias nuevas es legítimo, pero `actualizado` tiene que quedar en hoy igual. Si algo falló, dilo sin adornos y manda la notificación push. Si descubres que una fuente dejó de responder o que el script de barrido necesita un ajuste, dilo en el resumen.
