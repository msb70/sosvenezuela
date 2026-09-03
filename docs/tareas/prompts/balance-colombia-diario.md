Actualiza el balance oficial del terremoto de Colombia en https://apoyo-fem-vzla.org/colombia.html (sección "Situación oficial" y los KPI de la portada) con las cifras más recientes de la UNGRD. Trabajas sin nadie delante: no preguntes nada, decide y explica al final.

=========================================================
0. CÓMO FUNCIONA ESTO
=========================================================
Tu entorno SOLO tiene red hacia GitHub. NO leas prensa ni apoyo-fem-vzla.org (dan 403). Actions (recolectar.yml) ya dejó la materia prima en el repo. NO uses WebFetch, WebSearch, curl a prensa ni MCP. Publicas con git push a main; esta rutina está ligada al repo msb70/sosvenezuela.

=========================================================
1. CONTEXTO Y MATERIA PRIMA
=========================================================
    git clone --depth 1 https://github.com/msb70/sosvenezuela.git /tmp/sv && cd /tmp/sv
    cat docs/tareas/RUNBOOK-PUBLICAR.md docs/tareas/CRITERIO-CO.md
python3 - <<'PY'
import json,datetime,sys
d=json.load(open('docs/tareas/candidatos-co.json'))
print('generado',d['generado'],'| fuentes',d['fuentes_leidas'],'/',d['fuentes_totales'],'| candidatos',len(d['candidatos']))
if d['generado'][:10]!=datetime.date.today().isoformat() or d['fuentes_leidas']==0:
    print('STOP'); sys.exit(2)
PY
Si termina en STOP: PushNotification («Balance CO: sin materia prima de Actions») + «⚠️ NO PUBLICADO».

=========================================================
2. PARTIR DEL HTML PUBLICADO
=========================================================
La rama deploy es lo que sirve producción. Trae colombia.html de ahí (solo GitHub, sin red):
    git fetch -q origin deploy && git show origin/deploy:colombia.html > colombia.html
Trabaja SIEMPRE sobre este archivo, nunca sobre el colombia.html del clone a secas.

=========================================================
3. BUSCAR EL BALANCE NUEVO EN LOS CANDIDATOS
=========================================================
En docs/tareas/candidatos-co.json, con el campo cuerpo, busca el balance más reciente de la UNGRD (fallecidos, heridos, desaparecidos, damnificados) con fecha de corte explícita. Fíjate en El Tiempo, Infobae, El Colombiano, Semana. Exige corte explícito y cita la fuente. Nunca mezcles cortes distintos ni sumes fuentes; si dos se contradicen, gana la UNGRD y anota la discrepancia.

=========================================================
4. COMPARAR Y EDITAR
=========================================================
    grep -o 'id="kpi[A-Za-z]*">[^<]*' colombia.html
Si las cifras no cambiaron respecto a lo que ya hay, NO toques el HTML: no hay nada que publicar y decirlo es un resultado válido; ve directo al resumen final. Si cambiaron, edítalas con un script de Python de reemplazos EXACTOS (comprueba que el texto viejo aparece las veces esperadas); nunca reescribas el archivo entero ni inventes un dato que la fuente no dé. Actualiza también la fecha de corte visible.

=========================================================
5. COMPROBAR QUE EL HTML SIGUE ENTERO
=========================================================
python3 - <<'PY'
s=open('colombia.html').read()
assert 'kpiFallecidos' in s and 'noticias-colombia.json' in s and '</html>' in s, 'HTML incompleto'
print('OK', len(s), 'bytes')
PY
Si falla, PARA: «⚠️ NO PUBLICADO» + push.

=========================================================
6. PUBLICAR: COMMIT + PUSH A main
=========================================================
    git config user.name "sosvenezuela-bot" && git config user.email "bot@apoyo-fem-vzla.org"
    git add colombia.html                      # SOLO este archivo; nunca git add -A
    git commit -m "Balance CO $(date -u +%F): <cifras nuevas y corte>"
    git pull --rebase origin main && git push origin main
    git rev-parse --short HEAD
Si el push falla: PushNotification («Balance CO: push a main bloqueado») + «⚠️ NO PUBLICADO».

=========================================================
7. VERIFICAR POR LA RAMA deploy
=========================================================
    sleep 90; git fetch -q origin deploy
    git show origin/deploy:colombia.html | grep -o 'id="kpiFallecidos">[^<]*'
Debe mostrar la cifra nueva. Si no, relanza (git commit --allow-empty -m redeploy && git push origin main) y repite; si sigue igual: PushNotification («Balance CO: deploy no reflejó el commit») + «⚠️ NO PUBLICADO».

AL TERMINAR: di qué cifras había, cuáles hay ahora, con qué corte y fuente. Si no cambió nada, dilo. No hagas commit de docs/tareas/ (son del recolector). Si algo falló, dilo sin adornos y manda la notificación push.
