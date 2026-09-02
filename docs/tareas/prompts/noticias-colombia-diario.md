Actualiza la sección de noticias de Colombia del sitio de la FEM (https://apoyo-fem-vzla.org/colombia.html) con lo publicado en las últimas 24-48 horas sobre el terremoto del 10 de agosto de 2026. Trabajas sin nadie delante: no preguntes nada, decide con el criterio guardado y explica tus decisiones al final.

=========================================================
0. LO QUE TE DEJA COLGADO (léelo antes de tocar nada)
=========================================================
Esta sesión es programada: NADIE puede aprobar un permiso. Cualquier herramienta que pida permiso deja la sesión en PENDING para siempre y la web sin actualizar. Por tanto:
- PROHIBIDO `WebFetch` y `WebSearch`. Toda la prensa se lee con `curl` desde `bash` y con el script `docs/tareas/barrer_fuentes.py` del repo.
- PROHIBIDO cualquier herramienta con prefijo `mcp__remote-devices__*` (Desktop Commander, device_bash, project_memory_*, hostinger-api del Mac): necesitan el Mac encendido. **No existe `project_memory_read` aquí: el contexto está en el repo, en `docs/tareas/`.**
- NO uses NINGUNA herramienta MCP (ni `mcp__Hostinger_Connector__*` ni ninguna otra): todas piden permiso en una sesión programada. Se publica con `git push` a `main`: GitHub Actions construye la rama `deploy` y Hostinger la sirve en menos de 1 minuto. Esta rutina está ligada al repo `msb70/sosvenezuela`, así que el push funciona desde `bash`.

=========================================================
1. CONTEXTO (del repo, no de la memoria)
=========================================================
```
git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv && cd /tmp/sv
cat docs/tareas/RUNBOOK-PUBLICAR.md docs/tareas/CRITERIO-CO.md
python3 .github/scripts/reconciliar_noticias.py     # une por id el JSON del repo con producción: PARTE SIEMPRE DE ESTE RESULTADO
```
Síguelos al pie de la letra. El criterio editorial manda sobre este prompt.

=========================================================
2. BARRER LA PRENSA
=========================================================
```
python3 docs/tareas/barrer_fuentes.py co --dias 2
```
Lista candidatos de El País (Cali), El Tiempo, Semana, Infobae, El Colombiano, Noticias ONU y ReliefWeb por RSS/sitemap. Para cada candidato que te interese: descarga el artículo con `curl -sL -A "<user-agent de Chrome>"`, confirma la fecha real (`article:published_time` o `datePublished`), comprueba que la URL da 200 y lee el texto para el resumen. Si sale un balance nuevo de la UNGRD, tiene prioridad. Si una fuente falla, sigue con las demás: nunca la sustituyas por WebFetch.

=========================================================
3. CRITERIO EDITORIAL
=========================================================
El de `CRITERIO-CO.md`. Resumen: terremoto y réplicas, rescates, balance de víctimas y damnificados, reconstrucción y financiación, ayuda humanitaria, albergues, educación y salud afectadas, infraestructura y economía de la reconstrucción; las alertas de estafa a damnificados entran. Fuera farándula, deportes y declaraciones político-partidistas; los anuncios de ayuda del Ejecutivo sí entran pero con el titular despersonalizado. Ojo con los sismos ajenos a la secuencia (Los Santos, Puracé) y con los «temblor hoy» sin daños.

=========================================================
4. ESCRIBIR EL JSON CON UN SCRIPT, NUNCA A MANO
=========================================================
Script en `/tmp/add_noticias.py`: carga `noticias-colombia.json`, añade los items nuevos descartando los que ya tengan ese `id` O esa `url`, reordena por `(fecha, id)` descendente, pone `actualizado` en la fecha de HOY **aunque no haya nada nuevo**, y escribe con `json.dump(..., ensure_ascii=False, indent=2)`.
`id` con patrón `co-AAAAMMDD-medio-tema`. `fuente` EXACTAMENTE igual que las cadenas ya existentes (la prensa de Cali va siempre como `El País (Cali)`).

=========================================================
5. VALIDAR — SI FALLA, NO PUBLIQUES
=========================================================
```
python3 -m json.tool noticias-colombia.json > /dev/null
python3 .github/scripts/validar_noticias.py noticias.json noticias-colombia.json
```

=========================================================
6. PUBLICAR: COMMIT + PUSH A main (sin conector, sin zip)
=========================================================
```
cd /tmp/sv
git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"
git add noticias-colombia.json                      # SOLO este archivo; nunca `git add -A`
git commit -m "Noticias CO $(date -u +%F): <resumen corto de lo que cambió>"
git pull --rebase origin main && git push origin main
git rev-parse --short HEAD              # apunta este SHA
```
Si el push falla por permisos, NO busques otra vía: `PushNotification` («Noticias CO: el push a main está bloqueado — la rutina no está ligada al repo») y respuesta que empieza por «⚠️ NO PUBLICADO».

=========================================================
7. VERIFICAR PRODUCCIÓN, NO EL PUSH
=========================================================
Espera 90 s y comprueba:
```
sleep 90; curl -s "https://apoyo-fem-vzla.org/noticias-colombia.json?v=$RANDOM" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['actualizado'],len(d['items']))"
```
Si no refleja tu cambio, GitHub a veces no dispara el workflow (pasó el 26/08): relánzalo con un commit vacío — `git commit --allow-empty -m "redeploy" && git push origin main` — y vuelve a comprobar a los 90 s. Si a la segunda sigue sin reflejarlo: `PushNotification` («Noticias CO: push OK pero producción no cambió») y respuesta que empieza por «⚠️ NO PUBLICADO», indicando el SHA.

**Que el push salga no es prueba de nada. La única prueba es esta comprobación.**

=========================================================
8. AL TERMINAR
=========================================================
Resume: cuántos items añadiste y de qué fuentes, qué descartaste y por qué, el SHA del commit y el `actualizado` + número de items que devolvió producción. Si algo falló, dilo sin adornos y manda la notificación push.
