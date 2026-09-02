Actualiza el balance oficial del terremoto de Colombia en https://apoyo-fem-vzla.org/colombia.html (sección "Situación oficial" y los KPI de la portada) con las cifras más recientes de la UNGRD. Trabajas sin nadie delante: no preguntes nada, decide y explica al final.

=========================================================
0. LO QUE TE DEJA COLGADO (léelo antes de tocar nada)
=========================================================
Esta sesión es programada: NADIE puede aprobar un permiso. Cualquier herramienta que pida permiso deja la sesión en PENDING para siempre. Por tanto:
- PROHIBIDO `WebFetch` y `WebSearch`. Todo se lee con `curl` desde `bash` (user-agent de Chrome) y con `docs/tareas/barrer_fuentes.py co`.
- PROHIBIDO cualquier herramienta con prefijo `mcp__remote-devices__*` (necesitan el Mac). **No existe `project_memory_read` aquí: el contexto está en el repo, en `docs/tareas/`.**
- NO uses NINGUNA herramienta MCP (ni `mcp__Hostinger_Connector__*` ni ninguna otra): todas piden permiso en una sesión programada. Se publica con `git push` a `main`: GitHub Actions construye la rama `deploy` y Hostinger la sirve en menos de 1 minuto. Esta rutina está ligada al repo `msb70/sosvenezuela`, así que el push funciona desde `bash`.


=========================================================
0-bis. AUTOCOMPROBACIÓN DE RED — ANTES DE NADA
=========================================================
```
curl -s -o /dev/null -w "%{http_code}\n" --max-time 20 "https://apoyo-fem-vzla.org/noticias.json"
```
Si NO devuelve `200` (p. ej. 403 del proxy o 000), **el entorno tiene la red cerrada y esta tarea no puede hacer nada útil**: no clones, no edites, no hagas commit ni push. Manda `PushNotification` («Balance CO: red bloqueada en el entorno (HTTP <código>) — no publicado») y termina con una respuesta que empiece por «⚠️ NO PUBLICADO».

**Regla de oro: si cualquier script devuelve un código de salida distinto de 0, o si el barrido lee 0 fuentes, o si `reconciliar_*.py` falla, PARA. Un día sin noticias es legítimo; un día sin lectura NO lo es, y publicar `actualizado: hoy` sin haber leído nada es mentir en la web.**

=========================================================
PASOS
=========================================================
1. Contexto y punto de partida:
```
git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv && cd /tmp/sv
cat docs/tareas/RUNBOOK-PUBLICAR.md docs/tareas/CRITERIO-CO.md
python3 .github/scripts/reconciliar_html.py      # trae a tu copia el colombia.html de producción si va por delante
```
Si el script termina con error, PARA: «⚠️ NO PUBLICADO» + push.
Trabaja SIEMPRE sobre ese resultado, nunca sobre el HTML del clone a secas.

2. Busca el balance más reciente de la UNGRD (fallecidos, heridos, desaparecidos, damnificados): `python3 docs/tareas/barrer_fuentes.py co --dias 2` y, con `curl -sL -A "<user-agent de Chrome>"`, los artículos de El Tiempo, Infobae, El Colombiano, Semana o la propia UNGRD (`https://www.gestiondelriesgo.gov.co/`). Exige fecha de corte explícita y cita la fuente.

3. Compara con lo que ya hay en la página (`grep -o 'id="kpi[A-Za-z]*">[^<]*' colombia.html`). **Si las cifras no han cambiado, no toques el HTML**: no hay nada que publicar y decirlo es un resultado válido. Si han cambiado, actualiza los KPI y la fecha de corte con un script de Python (reemplazos exactos, nunca reescribir el archivo entero), sin inventar ningún dato que la fuente no dé.

4. Nunca mezcles cortes distintos ni sumes cifras de fuentes distintas. Si dos medios se contradicen, quédate con el balance oficial de la UNGRD y anota la discrepancia.

5. Antes de publicar comprueba que el HTML sigue entero: contiene `kpiFallecidos`, `noticias-colombia.json` y `</html>`, y su tamaño no se desvía más de un 2 % del de producción (`curl -sI https://apoyo-fem-vzla.org/colombia.html | grep -i content-length`).

6. Publica con git (sin conector): en `/tmp/sv`, `git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"`, `git add colombia.html` (SOLO ese archivo), `git commit -m "Balance CO $(date -u +%F): <cifras nuevas y corte>"`, `git pull --rebase origin main && git push origin main`. Si el push falla por permisos, no busques otra vía: `PushNotification` («Balance CO: el push a main está bloqueado») y «⚠️ NO PUBLICADO».

7. Verifica en producción, no el push: `sleep 90; curl -s "https://apoyo-fem-vzla.org/colombia.html?v=$RANDOM" | grep -o 'id="kpiFallecidos">[^<]*'` debe mostrar la cifra nueva. Si no, relanza el despliegue con `git commit --allow-empty -m "redeploy" && git push origin main` y comprueba de nuevo a los 90 s; si sigue igual, `PushNotification` («Balance CO: push OK pero producción no cambió») y respuesta que empieza por «⚠️ NO PUBLICADO».

AL TERMINAR: di qué cifras había, cuáles hay ahora, con qué fecha de corte y de qué fuente. Si no cambió nada, dilo. Si algo falló, dilo sin adornos y manda la notificación push.
