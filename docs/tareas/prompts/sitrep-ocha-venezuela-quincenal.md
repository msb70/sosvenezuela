Actualización quincenal del sitio SOS Venezuela (https://apoyo-fem-vzla.org/) con el último Reporte de Situación (SitRep) de OCHA sobre los terremotos del 24 de junio de 2026. Trabajas sin nadie delante: no preguntes nada, decide y explica al final.

=========================================================
0. CÓMO FUNCIONA ESTO
=========================================================
Tu entorno SOLO tiene red hacia GitHub. NO leas ReliefWeb ni apoyo-fem-vzla.org (dan 403). Actions (recolectar.yml) ya listó los SitReps y extrajo su texto al repo. NO uses WebFetch, WebSearch, curl ni MCP. Publicas con git push a main; esta rutina está ligada al repo msb70/sosvenezuela.

=========================================================
1. CONTEXTO Y MATERIA PRIMA
=========================================================
    git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv && cd /tmp/sv
    cat docs/tareas/RUNBOOK-PUBLICAR.md docs/tareas/CRITERIO-VE.md
    python3 -c "import json;d=json.load(open('docs/tareas/sitreps-ve.json'));print(d['generado']);[print(r['fecha'],r['texto'] or '(sin texto)','|',r['titulo'][:70]) for r in d['reportes']]"
    git fetch -q origin deploy && git show origin/deploy:index.html > index.html   # base = lo publicado
Trabaja SIEMPRE sobre este index.html (rama deploy = producción), nunca sobre el del clone a secas. Los textos de cada SitRep están en docs/tareas/sitreps/*.txt (el campo texto de cada reporte).

=========================================================
2. QUÉ SITREP REFLEJA HOY LA WEB
=========================================================
Averigua el número integrado mirándolo en TRES sitios (suelen desincronizarse): (a) el <p> del sec-head de <section id="situacion">; (b) el <div class="info-note"> del pie; (c) los sublbl de los tiles de #panorama y el campo vinculacion del modal de OCHA. Si no coinciden, corrígelo aunque no haya SitRep nuevo.
    grep -on "SitRep [0-9]\+\|N\.° [0-9]\+\|corte al [0-9]\+ de [a-z]\+" index.html

=========================================================
3. LEER LOS SITREPS PENDIENTES
=========================================================
En sitreps-ve.json están los reportes de OCHA/OIM/UNICEF más recientes con su texto extraído (docs/tareas/sitreps/<slug>.txt). OCHA publica CADA DOS SEMANAS desde el #34 (27/08): que no haya nuevo es lo normal. REGLA CRÍTICA: si la web va por el #34 y el último es el #36, lee el 35 Y el 36 (cada SitRep actualiza solo algunos bloques; un dato solo aparece en el reporte que lo tocó por última vez: campamentos se fijaron en el #32 y ni #33 ni #34 los repitieron). Para cada bloque anota de qué SitRep viene y su fecha de corte, y consérvalo aunque el reporte más nuevo no lo repita. Revisa también la OIM/UNICEF si su reporte cambió.

=========================================================
4. SI NO HAY SITREP NUEVO
=========================================================
Ejecuta igual el barrido de coherencia del punto 6. Si todo cuadra, no toques nada y termina informando que no hubo novedad. Si hay incoherencias, corrígelas y publica.

=========================================================
5. SI HAY SITREP(S) NUEVO(S): QUÉ ACTUALIZAR EN index.html
=========================================================
Edita con un script de Python de reemplazos EXACTOS (comprueba que el texto viejo aparece las veces esperadas); nunca reescribas el archivo entero.
a. Respaldos estáticos de los KPI (kpiFallecidos, kpiHeridos, kpiDesaparecidos, réplicas, sin vivienda, campamentos, edificios) con su sublbl indicando número de SitRep y fecha de corte de ESE dato.
b. El <p> del sec-head de la sección 04: número y fecha del SitRep que manda y qué bloques vienen de reportes anteriores. Formato: «Resumen basado en el Reporte de Situación N.° XX de OCHA (fecha, corte al …). Los datos de campamentos corresponden al Reporte N.° YY (corte …) y los de edificios al N.° ZZ (corte …).»
c. Las tarjetas de la sección 04 (#situacion), incluidos hechos que cambian (epicentros, canales oficiales, montos del PRH, estado de clases/hospitales, financiación).
d. El info-note del pie: EXACTAMENTE lo mismo que el <p> de entrada sobre qué dato viene de qué reporte.
e. El campo vinculacion del modal de OCHA: añade el SitRep nuevo y los intermedios, cada uno con enlace y «Datos clave»; la cadena no debe tener huecos.
f. El modal de la OIM si su reporte cambió.
Mantén estilo y formato. El KPI de fallecidos lo pisa Wikipedia en vivo si su cifra es mayor (correcto, no es fallo).

=========================================================
6. BARRIDO DE COHERENCIA (OBLIGATORIO)
=========================================================
- Ninguna mención a SitRep/N.°/corte contradice a otra (grep del punto 2).
- Ninguna cifra de la sección 04 contradice al tile de #panorama que muestra ese dato.
- Cada cifra lleva su fecha de corte correcta, no la del reporte más nuevo.
- Cifras huérfanas: grep -on "<cifra vieja>" index.html por cada número sustituido.
- HTML entero: contiene noticias.json, <title y </html>; secciones abiertas == cerradas (python3 -c "import re;s=open('index.html').read();print(len(re.findall(r'<section',s)),len(re.findall(r'</section>',s)))"); arrays ORGANISMOS y ORG_RUBROS con la misma longitud.

=========================================================
7. PUBLICAR Y VERIFICAR
=========================================================
Solo si cambiaste algo:
    git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"
    git add index.html                         # SOLO este archivo; nunca git add -A
    git commit -m "SitRep <N> de OCHA integrado: <cifras clave y corte>"
    git pull --rebase origin main && git push origin main
    git rev-parse --short HEAD
    sleep 90; git fetch -q origin deploy
    git show origin/deploy:index.html | grep -o "Reporte de Situación N.° [0-9]*" | head -3
Debe mostrar el número nuevo. Si no, relanza (git commit --allow-empty -m redeploy && git push origin main) y repite; si sigue igual: PushNotification («SitRep VE: deploy no reflejó el commit») + «⚠️ NO PUBLICADO». Si el push falla: PushNotification («SitRep VE: push a main bloqueado») + «⚠️ NO PUBLICADO».

AL TERMINAR: di qué SitRep había, cuál(es) integraste, qué cifras cambiaron (con corte y fuente), qué quedó igual y por qué. Si no hubo novedad, una línea. No toques noticias.json, noticias-colombia.json ni colombia.html. No hagas commit de docs/tareas/. Si algo falló, dilo sin adornos y manda la notificación push.
