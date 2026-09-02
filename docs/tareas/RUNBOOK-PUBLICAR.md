# Runbook: publicar en apoyo-fem-vzla.org

> **Arquitectura vigente (02/09/2026): recolector en Actions + rutina que solo consume del repo.**
> El entorno de las rutinas (Claude Code) solo tiene red a GitHub; no lee prensa. GitHub Actions
> (`recolectar.yml`) lee la prensa y deja la materia prima en `docs/tareas/` (candidatos-*.json,
> produccion-*.json, sitreps). La rutina clona, aplica criterio, edita y hace `git push` a `main`;
> `deploy.yml` publica. Verificación por la rama `deploy` (sin red). Guía completa y paso a paso
> en `GUIA-RUTINAS.md`; prompts en `prompts/`. Lo de abajo (subida TUS con el conector Hostinger)
> es la vía LEGADO, solo para publicar a mano con alguien delante.

## Las tres reglas que evitan que la tarea se cuelgue

1. **Ninguna herramienta que pida permiso.** En una sesión programada no hay nadie para
   aprobar: la sesión se queda en `PENDING` para siempre (pasó el 02/09/2026 con un
   `WebFetch` a elnacional.com y con la primera llamada al conector Hostinger).
   - **NO uses `WebFetch` ni `WebSearch`.** Toda la prensa se barre con
     `python3 docs/tareas/barrer_fuentes.py ve|co` y con `curl` desde `bash`.
   - **NO uses nada con prefijo `mcp__remote-devices__*`** (Desktop Commander, device_bash,
     hostinger-api del Mac, project_memory_*): necesitan el Mac encendido.
   - **Ninguna herramienta MCP.** El conector Hostinger de la nube (`mcp__Hostinger_Connector__*`)
     también pide permiso en cada sesión programada (comprobado el 02/09/2026): solo vale con alguien delante.
2. **Verificar producción, nunca la subida.** Un 204 en el PATCH y un `SUCCEEDED` de la
   sesión no prueban nada. Solo prueba el `curl` final contra el sitio.
3. **Una tarea que no publica y no avisa es peor que una caída.** Si algo falla,
   `PushNotification` + respuesta que empieza por «⚠️ NO PUBLICADO».

## Dos vías de publicación
- **Vía A (preferida): `git push` a `main`.** Solo funciona si la rutina se creó desde claude.ai/code
  con el repo `msb70/sosvenezuela` seleccionado (ver `GUIA-RUTINAS.md`). Sin MCP, sin permisos.
  Los prompts de `docs/tareas/prompts/` usan esta vía.
- **Vía B (legado): subida TUS con el conector Hostinger de la nube.** Pide permiso en cada sesión
  programada → solo sirve con alguien delante. Descrita abajo (pasos 5-7) por si hace falta a mano.

## El flujo

```bash
# 1. Partir de lo publicado, no del repo (producción suele ir por delante)
git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv
cd /tmp/sv && python3 .github/scripts/reconciliar_noticias.py     # une por id repo + producción
# Para colombia.html (tarea de balance): python3 .github/scripts/reconciliar_html.py

# 2. Barrer la prensa (RSS/sitemaps por curl, sin WebFetch). ~10 s.
python3 docs/tareas/barrer_fuentes.py ve --dias 2      # o `co`
# Confirmar la fecha real de cada candidato en su HTML:
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
curl -sL -A "$UA" "$URL" | grep -oE '(article:published_time|datePublished)"?[^>]{0,40}20[0-9-]+T[0-9:]+' | head -1
# Y leer el artículo para el resumen:
curl -sL -A "$UA" "$URL" | python3 -c "import sys,re,html;t=sys.stdin.read();t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S);print(html.unescape(re.sub(r'<[^>]+>',' ',t))[:6000])"

# 3. Escribir el JSON con un script (/tmp/add_noticias.py), NUNCA a mano:
#    carga el JSON, añade los items nuevos descartando los que ya tengan ese id O esa url,
#    ordena por (fecha, id) desc, pone "actualizado" = HOY aunque no haya nada nuevo,
#    json.dump(..., ensure_ascii=False, indent=2).

# 4. Validar — si falla, NO publicar
python3 -m json.tool noticias.json > /dev/null
python3 .github/scripts/validar_noticias.py noticias.json noticias-colombia.json
```

**5A. Vía A — commit + push (rutina ligada al repo):**

```bash
cd /tmp/sv
git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"
git add noticias.json            # SOLO el archivo que tocaste; nunca `git add -A`
git commit -m "Noticias VE $(date -u +%F): <resumen>"
git pull --rebase origin main && git push origin main
sleep 90                          # Actions construye `deploy` y Hostinger lo sirve
```
Luego el paso 6. Si producción no cambia, relanzar con `git commit --allow-empty -m redeploy && git push origin main`
(GitHub a veces no dispara el workflow). Si el push da 403, la rutina no está ligada al repo: avisar y parar.

**5B. Vía B — subida TUS (solo con alguien delante).** Pedir credenciales frescas en cada pasada (caducan en horas) con
`mcp__Hostinger_Connector__hosting_generateUploadURLV1` (`username` y `domain` van en el
prompt de la tarea). Devuelve `url`, `auth_key`, `rest_auth_key`. Luego, desde `bash`
(la ruta es relativa a `public_html`):

```bash
F=noticias.json; SIZE=$(stat -c%s "$F")
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$URL/$F?override=true" \
  -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
  -H "Upload-Length: $SIZE" -H "Upload-Offset: 0"                 # espera 201
curl -s -D - -o /dev/null -X PATCH "$URL/$F?override=true" \
  -H "X-Auth: $AUTH" -H "X-Auth-Rest: $REST" -H "Tus-Resumable: 1.0.0" \
  -H "Content-Type: application/offset+octet-stream" -H "Upload-Offset: 0" \
  --data-binary "@$F" | grep -iE '^HTTP|upload-offset'            # espera 204 y offset == SIZE
```

No usar `hosting_deployStaticSiteArchiveV1` ni ningún deploy por zip: reemplazan el
sitio entero y borran lo que no incluyas.

**6. Verificar producción (la única prueba válida):**

```bash
sleep 5; curl -s "https://apoyo-fem-vzla.org/noticias.json?v=$RANDOM" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['actualizado'],len(d['items']))"
```
Si `actualizado` no es hoy o faltan items, reintentar una vez a los 60 s; si sigue igual,
notificación push y «⚠️ NO PUBLICADO».

**7. Si publicaste por la vía B, no hagas commit ni push** (el proxy lo rechaza en rutinas
sin repo). El workflow *Reconciliar noticias con produccion* (12:30 y 21:30 UTC) une por
`id` lo publicado con `main` sin borrar nada.

## Estructura del JSON

`{actualizado, nota, items:[{id, fecha, titulo, resumen, fuente, autor?, tipoFuente,
categoria, tipo, url, espejo?}]}`

- `tipoFuente`: `"medio"` | `"oficial"`. `tipo`: `"noticia"` | `"opinion"` | `"oficial"`.
- **`fuente` idéntica a las cadenas ya existentes en el archivo** (es la clave del filtro;
  una variante duplica entradas en el desplegable). Sacar la lista vigente con:
  `python3 -c "import json;print(sorted({i['fuente'] for i in json.load(open('noticias.json'))['items']}))"`
- `id`: `ve-AAAAMMDD-medio-tema` / `co-AAAAMMDD-medio-tema`.
- Un JSON roto deja la sección vacía en producción. Por eso el paso 4 es obligatorio.
