Actualiza la sección de noticias de Venezuela del sitio de la FEM (https://apoyo-fem-vzla.org) con lo publicado en las últimas 24-48 horas sobre el terremoto del 24 de junio de 2026. Trabajas sin nadie delante: no preguntes nada, decide con el criterio guardado y explica tus decisiones al final.

=========================================================
0. CÓMO FUNCIONA ESTO (léelo antes de tocar nada)
=========================================================
Tu entorno SOLO tiene red hacia GitHub: NO puedes leer prensa ni apoyo-fem-vzla.org (dan 403). No hace falta: un workflow de GitHub Actions (recolectar.yml) ya leyó la prensa y dejó la materia prima en el repo. Tu trabajo es CRITERIO + PUBLICAR, no leer internet.
- NO uses WebFetch, WebSearch, curl a sitios de prensa, ni ninguna herramienta MCP (todas piden permiso o fallan). Todo sale de archivos del repo y de git.
- Publicas con git push a main: Actions construye la rama deploy y Hostinger la sirve en <1 min. Esta rutina está ligada al repo msb70/sosvenezuela, así que el push funciona desde bash.

=========================================================
1. CONTEXTO Y COMPROBACIÓN DE QUE HAY MATERIA PRIMA
=========================================================
    git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv && cd /tmp/sv
    cat docs/tareas/RUNBOOK-PUBLICAR.md docs/tareas/CRITERIO-VE.md
python3 - <<'PY'
import json,datetime,sys
d=json.load(open('docs/tareas/candidatos-ve.json'))
gen=d['generado'][:10]; hoy=datetime.date.today().isoformat()
print('generado',d['generado'],'| fuentes',d['fuentes_leidas'],'/',d['fuentes_totales'],'| candidatos',len(d['candidatos']))
if gen!=hoy or d['fuentes_leidas']==0:
    print('STOP: la materia prima no es de hoy o no se leyó ninguna fuente'); sys.exit(2)
PY
Si ese bloque termina con STOP / código distinto de 0, el recolector de Actions no corrió hoy: NO publiques a ciegas. Manda PushNotification («Noticias VE: sin materia prima fresca de Actions — no publicado») y responde empezando por «⚠️ NO PUBLICADO». (Puedes forzar el recolector si tienes gh: `gh workflow run recolectar.yml` y reintentar en 3 min; si no, para.)

=========================================================
2. PARTIR DE LO PUBLICADO
=========================================================
docs/tareas/produccion-ve.json es copia EXACTA de lo que sirve producción ahora (la capturó Actions). Es tu base: cópiala a noticias.json y añade encima. Nunca partas del noticias.json del repo a secas.
    cp docs/tareas/produccion-ve.json noticias.json

=========================================================
3. ELEGIR ENTRE LOS CANDIDATOS (aquí va tu criterio)
=========================================================
docs/tareas/candidatos-ve.json trae, por candidato: fuente, titulo, url, fecha (ya verificada del artículo), resumen_feed y cuerpo (texto del artículo, ~1800 car.). Decide con el cuerpo, no adivines. Aplica CRITERIO-VE.md: entran terremoto, réplicas, reconstrucción, ayuda humanitaria, damnificados, educación y salud por el sismo, infraestructura y economía de la reconstrucción; fuera farándula, política internacional y declaraciones político-partidistas. Titular con carga partidista → reescríbelo describiendo el hecho y atribuyéndolo al organismo (ej.: «Los 6.509 muertos que el régimen de Delcy…» → «OCHA cifra en 6.509 los fallecidos por el terremoto»). Redacta tú titulo y resumen (2-3 frases con el dato y la fuente) a partir del cuerpo. Mínimo 3 fuentes distintas si hay material.

=========================================================
4. ESCRIBIR EL JSON CON UN SCRIPT
=========================================================
Script en /tmp/add.py: carga noticias.json, añade los items que elegiste descartando los que ya tengan ese id O esa url, ordena por (fecha, id) desc, pone actualizado = HOY aunque no haya nada nuevo, escribe con json.dump(..., ensure_ascii=False, indent=2).

ESQUEMA DE CADA ITEM — los 9 campos, todos obligatorios salvo los marcados. `validar_noticias.py` EXIGE id, fecha, titulo, resumen, fuente, categoria y url: si falta uno solo, el paso 5 falla y no publicas. Cópiate un item existente de produccion-ve.json y rellena por encima.
  id          "ve-AAAAMMDD-medio-tema"
  fecha       "AAAA-MM-DD" (la del artículo, no la de hoy)
  titulo      redactado por ti
  resumen     redactado por ti, 2-3 frases con el dato y la fuente
  fuente      EXACTAMENTE una de las cadenas ya existentes en el archivo
  categoria   EXACTAMENTE una de: Ayuda humanitaria | Reconstrucción | Infraestructura y servicios | Educación | Salud | Balance y cifras | Réplicas y sismología | Opinión | Colombia
  tipo        "noticia" | "oficial" (organismos: OCHA, OIM, Unicef, PMA…) | "opinion"
  tipoFuente  "medio" | "oficial"
  url         la del artículo, empezando por https://
  autor       opcional, solo si el artículo lo firma
  espejo      opcional, solo si tienes URL alternativa

=========================================================
5. VALIDAR — SI FALLA, NO PUBLIQUES
=========================================================
    python3 -m json.tool noticias.json > /dev/null
    python3 .github/scripts/validar_noticias.py noticias.json noticias-colombia.json
Si falla: «⚠️ NO PUBLICADO» + push. Un JSON roto deja la sección vacía en producción.

=========================================================
6. PUBLICAR: COMMIT + PUSH A main
=========================================================
    git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"
    git add noticias.json                      # SOLO este archivo; nunca git add -A
    git commit -m "Noticias VE $(date -u +%F): <resumen corto>"
    git pull --rebase origin main && git push origin main
    git rev-parse --short HEAD                 # apunta este SHA
Si el push falla por permisos: PushNotification («Noticias VE: push a main bloqueado») + «⚠️ NO PUBLICADO».

=========================================================
7. VERIFICAR POR LA RAMA deploy (sin red, solo GitHub)
=========================================================
deploy.yml reconstruye la rama deploy desde tu commit; Hostinger sirve esa rama tal cual. Así que comprobar la rama deploy en GitHub equivale a comprobar producción, y sí puedes hacerlo:
    sleep 90
    git fetch -q origin deploy
    git show origin/deploy:noticias.json | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['actualizado'],len(d['items']))"
Debe salir la fecha de HOY y el número de items que esperas. Si no, relanza el deploy con un commit vacío (git commit --allow-empty -m redeploy && git push origin main) y repite a los 90 s. Si sigue sin cuadrar: PushNotification («Noticias VE: deploy no reflejó el commit <SHA>») + «⚠️ NO PUBLICADO».

Que el push salga no es prueba. La prueba es que la rama deploy cite tu contenido.

=========================================================
8. AL TERMINAR
=========================================================
Resume: cuántos items añadiste y de qué fuentes, qué descartaste y por qué, el SHA, y lo que devolvió la rama deploy (fecha + items). Un día sin noticias nuevas es legítimo, pero actualizado queda en hoy igual. Si algo falló, dilo sin adornos y manda la notificación push. No hagas commit de los archivos de docs/tareas/ (son del recolector).
