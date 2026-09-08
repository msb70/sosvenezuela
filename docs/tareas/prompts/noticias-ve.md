Actualiza la sección de noticias de Venezuela del sitio de la FEM (https://apoyo-fem-vzla.org) con lo publicado en las últimas 24-48 horas sobre el terremoto del 24 de junio de 2026. Trabajas sin nadie delante: no preguntes nada, decide con el criterio guardado y explica tus decisiones al final.

=========================================================
0. DÓNDE ESTÁS Y QUÉ SE ESPERA DE TI
=========================================================
Estás dentro de GitHub Actions (workflow publicar.yml), en un checkout del repo msb70/sosvenezuela. El workflow YA hizo, antes de llamarte:
- recolectar la prensa → docs/tareas/candidatos-ve.json (noticias con fecha verificada y cuerpo)
- descargar de PRODUCCIÓN el noticias.json vigente y dejarlo en ./noticias.json (tu base de trabajo)
Y hará DESPUÉS de ti: validar, commitear a main, desplegar y comprobar producción.
Tu trabajo es solo CRITERIO EDITORIAL: elegir candidatos, redactar y escribir noticias.json.
- NO uses WebFetch, WebSearch ni ninguna herramienta MCP. No hace falta leer internet: todo está en el repo.
- NO hagas git commit, git push, git checkout ni git stash. NO toques ningún archivo que no sea noticias.json (ni docs/tareas/, ni noticias-colombia.json, ni HTML).
- Si concluyes que NO se debe publicar, escribe el motivo en NO_PUBLICADO.txt y termina. El workflow fallará en rojo y avisará.

=========================================================
1. CONTEXTO Y MATERIA PRIMA
=========================================================
    cat docs/tareas/CRITERIO-VE.md
python3 - <<'PY'
import json
d=json.load(open('docs/tareas/candidatos-ve.json'))
print('generado',d['generado'],'| fuentes',d['fuentes_leidas'],'/',d['fuentes_totales'],'| candidatos',len(d['candidatos']))
p=json.load(open('noticias.json')); print('producción: actualizado',p['actualizado'],'| items',len(p['items']))
PY
Si hay 0 candidatos: no es un error; salta al punto 4 y deja actualizado = hoy.

=========================================================
2. PARTIR DE LO PUBLICADO
=========================================================
./noticias.json ES producción (lo descargó el workflow). Añade encima; nunca borres ni reescribas items existentes ni cambies su orden salvo por el sort del paso 4.

=========================================================
3. ELEGIR ENTRE LOS CANDIDATOS (aquí va tu criterio)
=========================================================
docs/tareas/candidatos-ve.json trae, por candidato: fuente, titulo, url, fecha (ya verificada del artículo), resumen_feed y cuerpo (texto del artículo, ~1800 car.). Decide con el cuerpo, no adivines. Aplica CRITERIO-VE.md: entran terremoto, réplicas, reconstrucción, ayuda humanitaria, damnificados, educación y salud por el sismo, infraestructura y economía de la reconstrucción; fuera farándula, política internacional y declaraciones político-partidistas. Titular con carga partidista → reescríbelo describiendo el hecho y atribuyéndolo al organismo (ej.: «Los 6.509 muertos que el régimen de Delcy…» → «OCHA cifra en 6.509 los fallecidos por el terremoto»). Redacta tú titulo y resumen (2-3 frases con el dato y la fuente) a partir del cuerpo. Mínimo 3 fuentes distintas si hay material. Descarta lo que ya esté publicado (mismo id o misma url) y los duplicados entre medios sobre el mismo hecho (quédate con la fuente más completa).

=========================================================
4. ESCRIBIR EL JSON CON UN SCRIPT
=========================================================
Script en /tmp/add.py: carga noticias.json, añade los items que elegiste descartando los que ya tengan ese id O esa url, ordena por (fecha, id) desc, pone actualizado = HOY (fecha UTC, AAAA-MM-DD) aunque no haya nada nuevo, escribe con json.dump(..., ensure_ascii=False, indent=2) y salto de línea final.

ESQUEMA DE CADA ITEM — los 9 campos, todos obligatorios salvo los marcados. `validar_noticias.py` EXIGE id, fecha, titulo, resumen, fuente, categoria y url: si falta uno solo, el workflow falla y no publica. Cópiate un item existente de noticias.json y rellena por encima.
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
5. VALIDAR — SI FALLA, ARRÉGLALO O NO PUBLIQUES
=========================================================
    python3 -m json.tool noticias.json > /dev/null
    python3 .github/scripts/validar_noticias.py noticias.json noticias-colombia.json
    git status --porcelain     # debe salir SOLO " M noticias.json" (y nada de docs/tareas/ ni otros)
Si el validador falla y no puedes corregirlo: escribe el motivo en NO_PUBLICADO.txt y termina. Un JSON roto deja la sección vacía en producción.

=========================================================
6. AL TERMINAR
=========================================================
No commitees ni pushees: lo hace el workflow. Resume: cuántos items añadiste y de qué fuentes, qué descartaste y por qué. Un día sin noticias nuevas es legítimo, pero actualizado queda en hoy igual.
