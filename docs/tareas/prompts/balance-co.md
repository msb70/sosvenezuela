Actualiza el balance oficial del terremoto de Colombia en https://apoyo-fem-vzla.org/colombia.html (sección "Situación oficial" y los KPI de la portada) con las cifras más recientes de la UNGRD. Trabajas sin nadie delante: no preguntes nada, decide y explica al final.

=========================================================
0. DÓNDE ESTÁS Y QUÉ SE ESPERA DE TI
=========================================================
Estás dentro de GitHub Actions (workflow publicar.yml), en un checkout del repo msb70/sosvenezuela. El workflow YA hizo, antes de llamarte:
- recolectar la prensa → docs/tareas/candidatos-co.json (noticias con fecha verificada y cuerpo)
- descargar de PRODUCCIÓN el colombia.html vigente y dejarlo en ./colombia.html (tu base de trabajo)
Y hará DESPUÉS de ti: validar, commitear a main, desplegar y comprobar producción.
- NO uses WebFetch, WebSearch ni ninguna herramienta MCP. Todo está en el repo.
- NO hagas git commit, git push, git checkout ni git stash. NO toques ningún archivo que no sea colombia.html.
- Si algo impide publicar con seguridad, escribe el motivo en NO_PUBLICADO.txt y termina.

=========================================================
1. CONTEXTO Y MATERIA PRIMA
=========================================================
    cat docs/tareas/CRITERIO-CO.md
    python3 -c "import json;d=json.load(open('docs/tareas/candidatos-co.json'));print(d['generado'],d['fuentes_leidas'],'/',d['fuentes_totales'],len(d['candidatos']))"

=========================================================
2. BUSCAR EL BALANCE NUEVO EN LOS CANDIDATOS
=========================================================
En docs/tareas/candidatos-co.json, con el campo cuerpo, busca el balance más reciente de la UNGRD (fallecidos, heridos, desaparecidos, damnificados) con fecha de corte explícita. Fíjate en El Tiempo, Infobae, El Colombiano, Semana, El País (Cali). Exige corte explícito y cita la fuente. Nunca mezcles cortes distintos ni sumes fuentes; si dos se contradicen, gana la UNGRD y anota la discrepancia.

=========================================================
3. COMPARAR Y EDITAR
=========================================================
    grep -o 'id="kpi[A-Za-z]*">[^<]*' colombia.html
Si las cifras no cambiaron respecto a lo que ya hay (o el corte nuevo no es posterior al publicado), NO toques el HTML: no hay nada que publicar y decirlo es un resultado válido; ve directo al resumen final. Si cambiaron, edítalas con un script de Python de reemplazos EXACTOS (comprueba que el texto viejo aparece las veces esperadas); nunca reescribas el archivo entero ni inventes un dato que la fuente no dé. Actualiza también la fecha de corte visible y la fuente citada.

=========================================================
4. COMPROBAR QUE EL HTML SIGUE ENTERO
=========================================================
python3 - <<'PY'
s=open('colombia.html').read()
assert 'kpiFallecidos' in s and 'noticias-colombia.json' in s and '</html>' in s, 'HTML incompleto'
print('OK', len(s), 'bytes')
PY
    git status --porcelain     # SOLO " M colombia.html" (o nada, si no hubo cambios)
Si falla: escribe el motivo en NO_PUBLICADO.txt y termina.

=========================================================
5. AL TERMINAR
=========================================================
No commitees ni pushees: lo hace el workflow. Di qué cifras había, cuáles hay ahora, con qué corte y fuente. Si no cambió nada, dilo en una línea.
