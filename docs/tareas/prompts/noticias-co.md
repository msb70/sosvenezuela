Actualiza la sección de noticias de Colombia del sitio de la FEM (https://apoyo-fem-vzla.org/colombia.html) con lo publicado en las últimas 24-48 horas sobre el terremoto del 10 de agosto de 2026. Trabajas sin nadie delante: no preguntes nada, decide con el criterio guardado y explica tus decisiones al final.

=========================================================
0. DÓNDE ESTÁS Y QUÉ SE ESPERA DE TI
=========================================================
Estás dentro de GitHub Actions (workflow publicar.yml), en un checkout del repo msb70/sosvenezuela. El workflow YA hizo, antes de llamarte:
- recolectar la prensa → docs/tareas/candidatos-co.json (noticias con fecha verificada y cuerpo)
- descargar de PRODUCCIÓN el noticias-colombia.json vigente y dejarlo en ./noticias-colombia.json (tu base de trabajo)
Y hará DESPUÉS de ti: validar, commitear a main, desplegar y comprobar producción.
Tu trabajo es solo CRITERIO EDITORIAL: elegir candidatos, redactar y escribir noticias-colombia.json.
- NO uses WebFetch, WebSearch ni ninguna herramienta MCP. No hace falta leer internet: todo está en el repo.
- NO hagas git commit, git push, git checkout ni git stash. NO toques ningún archivo que no sea noticias-colombia.json (ni docs/tareas/, ni noticias.json, ni HTML).
- Si concluyes que NO se debe publicar, escribe el motivo en NO_PUBLICADO.txt y termina. El workflow fallará en rojo y avisará.

=========================================================
1. CONTEXTO Y MATERIA PRIMA
=========================================================
    cat docs/tareas/CRITERIO-CO.md
python3 - <<'PY'
import json
d=json.load(open('docs/tareas/candidatos-co.json'))
print('generado',d['generado'],'| fuentes',d['fuentes_leidas'],'/',d['fuentes_totales'],'| candidatos',len(d['candidatos']))
p=json.load(open('noticias-colombia.json')); print('producción: actualizado',p['actualizado'],'| items',len(p['items']))
PY
Si hay 0 candidatos: no es un error; salta al punto 4 y deja actualizado = hoy.

=========================================================
2. PARTIR DE LO PUBLICADO
=========================================================
./noticias-colombia.json ES producción (lo descargó el workflow). Añade encima; nunca borres ni reescribas items existentes ni cambies su orden salvo por el sort del paso 4.

=========================================================
3. ELEGIR ENTRE LOS CANDIDATOS (aquí va tu criterio)
=========================================================
docs/tareas/candidatos-co.json trae, por candidato: fuente, titulo, url, fecha (ya verificada del artículo), resumen_feed y cuerpo (texto del artículo, ~1800 car.). Decide con el cuerpo, no adivines. Aplica CRITERIO-CO.md: entran terremoto y réplicas, rescates, balance de víctimas y damnificados, reconstrucción y financiación, ayuda humanitaria, albergues, educación y salud por el sismo, infraestructura y economía; fuera farándula, deportes y declaraciones político-partidistas. Titular con carga partidista → reescríbelo describiendo el hecho y despersonalizando al Ejecutivo («El Gobierno anuncia…», no el nombre del presidente). Ojo con los sismos ajenos a la secuencia (Los Santos, Puracé) y los «temblor hoy» sin daños. Las alertas de estafa a damnificados entran. Redacta tú titulo y resumen (2-3 frases con el dato y la fuente) a partir del cuerpo. Mínimo 3 fuentes distintas si hay material. Descarta lo que ya esté publicado (mismo id o misma url) y los duplicados entre medios sobre el mismo hecho (quédate con la fuente más completa).

=========================================================
4. ESCRIBIR EL JSON CON UN SCRIPT
=========================================================
Script en /tmp/add.py: carga noticias-colombia.json, añade los items que elegiste descartando los que ya tengan ese id O esa url, ordena por (fecha, id) desc, pone actualizado = HOY (fecha UTC, AAAA-MM-DD) aunque no haya nada nuevo, escribe con json.dump(..., ensure_ascii=False, indent=2) y salto de línea final.

ESQUEMA DE CADA ITEM — los 8 campos, todos obligatorios. `validar_noticias.py` EXIGE id, fecha, titulo, resumen, fuente, categoria y url: si falta uno solo, el workflow falla y no publica. Cópiate un item existente de noticias-colombia.json y rellena por encima.
  id          "co-AAAAMMDD-medio-tema"
  fecha       "AAAA-MM-DD" (la del artículo, no la de hoy)
  titulo      redactado por ti
  resumen     redactado por ti, 2-3 frases con el dato y la fuente
  fuente      EXACTAMENTE una de las cadenas ya existentes (la prensa de Cali va siempre como El País (Cali))
  categoria   EXACTAMENTE una de: Ayuda humanitaria | Reconstrucción | Infraestructura y servicios | Educación | Salud | Balance y cifras | Réplicas y sismología | Rescates y búsqueda
  tipo        "noticia" | "oficial" (organismos: UNGRD, OCHA, Unicef…)
  tipoFuente  "medio" | "oficial"
  url         la del artículo, empezando por https://

=========================================================
5. VALIDAR — SI FALLA, ARRÉGLALO O NO PUBLIQUES
=========================================================
    python3 -m json.tool noticias-colombia.json > /dev/null
    python3 .github/scripts/validar_noticias.py noticias.json noticias-colombia.json
    git status --porcelain     # debe salir SOLO " M noticias-colombia.json" (y nada de docs/tareas/ ni otros)
Si el validador falla y no puedes corregirlo: escribe el motivo en NO_PUBLICADO.txt y termina. Un JSON roto deja la sección vacía en producción.

=========================================================
6. AL TERMINAR
=========================================================
No commitees ni pushees: lo hace el workflow. Resume: cuántos items añadiste y de qué fuentes, qué descartaste y por qué. Un día sin noticias nuevas es legítimo, pero actualizado queda en hoy igual.
