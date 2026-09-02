Actualización quincenal del sitio SOS Venezuela (https://apoyo-fem-vzla.org/) con el último Reporte de Situación (SitRep) de OCHA sobre los terremotos del 24 de junio de 2026. Trabajas sin nadie delante: no preguntes nada, decide y explica al final.

=========================================================
0. LO QUE TE DEJA COLGADO (léelo antes de tocar nada)
=========================================================
Esta sesión es programada: NADIE puede aprobar un permiso. Cualquier herramienta que pida permiso deja la sesión en PENDING para siempre. Por tanto:
- PROHIBIDO `WebFetch` y `WebSearch`. ReliefWeb se lee con `curl -sL -A "<user-agent de Chrome>"` desde `bash` (RSS, página del reporte y PDF responden 200 desde el contenedor; verificado 02/09/2026) y el PDF con `pdftotext`.
- PROHIBIDO cualquier herramienta con prefijo `mcp__remote-devices__*` (Playwright del Mac, PDF Tools, Desktop Commander, project_memory_*): necesitan el Mac. **No existe `project_memory_read` aquí: el contexto está en el repo, en `docs/tareas/`.**
- NO uses NINGUNA herramienta MCP (ni `mcp__Hostinger_Connector__*` ni ninguna otra): todas piden permiso en una sesión programada. Se publica con `git push` a `main`: GitHub Actions construye la rama `deploy` y Hostinger la sirve en menos de 1 minuto. Esta rutina está ligada al repo `msb70/sosvenezuela`, así que el push funciona desde `bash`.

=========================================================
1. CONTEXTO Y PUNTO DE PARTIDA
=========================================================
```
git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv && cd /tmp/sv
cat docs/tareas/RUNBOOK-PUBLICAR.md docs/tareas/CRITERIO-VE.md
python3 .github/scripts/reconciliar_html.py      # trae a tu copia el index.html de producción si va por delante
```
Trabaja SIEMPRE sobre ese resultado. NO toques `noticias.json`, `noticias-colombia.json` ni `colombia.html`: los mantienen otras tareas.

=========================================================
2. QUÉ SITREP REFLEJA HOY LA WEB
=========================================================
Averigua qué número de SitRep está integrado mirándolo en TRES sitios, porque suelen desincronizarse: (a) el `<p>` del `sec-head` de `<section id="situacion">`; (b) el `<div class="info-note">` del pie de esa sección; (c) los `sublbl` de los tiles del `#panorama` y el campo `vinculacion` del modal de OCHA. Si no coinciden, ya hay un fallo que debes corregir aunque no haya SitRep nuevo.
`grep -on "SitRep [0-9]\+\|N\.° [0-9]\+\|corte al [0-9]\+ de [a-z]\+" index.html`

=========================================================
3. BUSCAR TODOS LOS SITREPS PENDIENTES, NO SOLO EL ÚLTIMO
=========================================================
```
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
curl -sL -A "$UA" "https://reliefweb.int/updates/rss.xml?advanced-search=%28PC250%29_%28F10%29" | grep -oE '<title>[^<]+|<link>[^<]+|<pubDate>[^<]+'
```
Busca los «Terremotos en Venezuela: Reporte de situación N.° XX» de OCHA. **OCHA publica cada dos semanas desde el #34 (27/08/2026)**: que no haya reporte nuevo es lo normal, no un fallo. Revisa también si hay reportes nuevos de la OIM («Respuesta a Terremotos - Reporte de Situación #NN»), UNICEF y PMA.
Para leer uno: `curl -sL -A "$UA" "<url del reporte>" -o /tmp/r.html`; el texto está dentro de `<article>`; el PDF completo está en el `href` que empieza por `/attachments/` (`curl -sL -A "$UA" "https://reliefweb.int<href>" -o /tmp/r.pdf && pdftotext -layout /tmp/r.pdf /tmp/r.txt`). **No inventes URLs de adjuntos**: el uuid no es adivinable.
REGLA CRÍTICA: si la web va por el #34 y el último es el #36, lee el 35 Y el 36. Cada SitRep actualiza solo algunos bloques y omite el resto; un dato solo aparece en el reporte que lo tocó por última vez (los campamentos se actualizaron en el #32 y ni el #33 ni el #34 los repitieron). Para cada bloque anota de qué SitRep viene y su fecha de corte, y consérvalo aunque el reporte más nuevo no lo repita.

=========================================================
4. SI NO HAY SITREP NUEVO
=========================================================
Ejecuta igualmente el barrido de coherencia del punto 6. Si todo está coherente, no toques nada y termina informando que no hubo novedad. Si hay incoherencias, corrígelas y publica.

=========================================================
5. SI HAY SITREP(S) NUEVO(S): QUÉ ACTUALIZAR EN index.html
=========================================================
Edita con un script de Python de reemplazos exactos (`s.replace(viejo, nuevo)` comprobando que `viejo` aparece exactamente las veces esperadas). Nunca reescribas el archivo entero.
a. Respaldos estáticos de los KPI (kpiFallecidos, kpiHeridos, kpiDesaparecidos, réplicas, sin vivienda, campamentos, edificios) con su `sublbl` indicando número de SitRep y fecha de corte de ESE dato.
b. El párrafo de entrada de la sección 04 (el `<p>` del `sec-head`): número y fecha del SitRep que manda, y qué bloques vienen de reportes anteriores. Formato: «Resumen basado en el Reporte de Situación N.° XX de OCHA (fecha, cifras oficiales con corte al …). Los datos de campamentos corresponden al Reporte N.° YY (corte …) y los de edificios e infraestructura al Reporte N.° ZZ (corte …), últimos reportes en actualizarlos.»
c. Las tarjetas de la sección 04 (#situacion), incluidos hechos que cambian (epicentros reubicados, canales oficiales, montos del PRH, estado de clases/hospitales, financiación).
d. El `info-note` del pie de la sección 04, que debe decir EXACTAMENTE lo mismo que el párrafo de entrada sobre qué dato viene de qué reporte.
e. El campo `vinculacion` del modal de OCHA: añade el SitRep nuevo y los intermedios, cada uno con enlace y línea de «Datos clave». La cadena no debe tener huecos.
f. El modal de la OIM si su reporte cambió.
Mantén estilo y formato. Ojo al KPI de fallecidos: Wikipedia lo pisa en vivo si su cifra es mayor (eso es correcto, no un fallo).

=========================================================
6. BARRIDO DE COHERENCIA (OBLIGATORIO ANTES DE PUBLICAR)
=========================================================
- Ninguna mención a SitRep/N.°/corte contradice a otra (grep del punto 2).
- Ninguna cifra de la sección 04 contradice al tile del #panorama que muestra ese mismo dato.
- Cada cifra lleva su fecha de corte correcta, no la del reporte más nuevo.
- Cifras huérfanas: `grep -on "<cifra vieja>" index.html` por cada número sustituido.
- El HTML sigue entero: contiene `noticias.json`, `<title` y `</html>`; `python3 -c "import re,sys;s=open('index.html').read();print(len(re.findall(r'<section',s)),len(re.findall(r'</section>',s)))"` da iguales; el tamaño no se desvía más de un 3 % del de producción (`curl -sI https://apoyo-fem-vzla.org/index.html | grep -i content-length`).
- Arrays `ORGANISMOS` y `ORG_RUBROS` con la misma longitud (cuéntalos con Python).

=========================================================
7. PUBLICAR Y VERIFICAR (git, sin conector)
=========================================================
Solo si cambiaste algo: en `/tmp/sv`, `git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"`, `git add index.html` (SOLO ese archivo), `git commit -m "SitRep <N> de OCHA integrado: <cifras clave y corte>"`, `git pull --rebase origin main && git push origin main`. Si el push falla por permisos, no busques otra vía: `PushNotification` («SitRep VE: el push a main está bloqueado») y «⚠️ NO PUBLICADO».
Verifica en producción, no el push: `sleep 90; curl -s "https://apoyo-fem-vzla.org/?v=$RANDOM" | grep -o "Reporte de Situación N.° [0-9]*" | head -3` debe mostrar el número nuevo, y `/`, `/colombia.html`, `/noticias.json`, `/noticias-colombia.json` deben dar 200. Si no, relanza con `git commit --allow-empty -m "redeploy" && git push origin main` y comprueba a los 90 s; si sigue igual: `PushNotification` («SitRep VE: push OK pero producción no cambió») y respuesta que empieza por «⚠️ NO PUBLICADO».

AL TERMINAR: di qué SitRep había, cuál(es) integraste, qué cifras cambiaron (con corte y fuente), qué quedó igual y por qué. Si no hubo novedad, dilo en una línea. Si algo falló, dilo sin adornos y manda la notificación push.
