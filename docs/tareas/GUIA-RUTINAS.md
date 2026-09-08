# Guía: publicación automática sin Mac, sin rutinas de claude.ai y sin nadie aprobando

> Vigente desde el 08/09/2026. Sustituye a la arquitectura «recolector en Actions + rutina de
> claude.ai». Aquella nunca publicó sola: las rutinas nacían sin el repo vinculado
> (`sources: []`) y el proxy bloqueaba el `git push` en cada corrida.

## La arquitectura: TODO corre en GitHub Actions
Un solo workflow, `.github/workflows/publicar.yml`, hace la cadena completa en un mismo job:

```
publicar.yml (GitHub Actions, red abierta, sin proxy, sin permisos que aprobar)
  1. recolectar_candidatos.py     → docs/tareas/candidatos-*.json, sitreps (materia prima)
  2. curl a producción             → el archivo a editar parte de LO PUBLICADO, no del repo
  3. claude-code-action            → Claude lee docs/tareas/prompts/<rutina>.md y EDITA el archivo
                                     (solo criterio editorial; sin git, sin internet)
  4. validar                       → validar_noticias.py + solo cambió el archivo de la rutina
  5. commit a main                 → con GITHUB_TOKEN
  6. gh workflow run deploy.yml    → un push con GITHUB_TOKEN no dispara workflows: se lanza a mano
  7. curl a producción             → si no sirve lo publicado en 3 min, el job FALLA en rojo
```
Si Claude decide no publicar, escribe `NO_PUBLICADO.txt` y el job falla en rojo. Un job rojo
manda email de GitHub (a quien hizo el último commit del workflow). Un job verde = publicado y
comprobado en producción. No hay estado intermedio «SUCCEEDED pero sin publicar».

## Rutinas y horarios (cron UTC; GitHub puede retrasarlos minutos u horas)
| Rutina (`inputs.rutina`) | Cron | Madrid | Edita | Prompt |
|---|---|---|---|---|
| `noticias-ve` | `7 6 * * *` | 08:07 | `noticias.json` | `prompts/noticias-ve.md` |
| `noticias-co` | `7 7 * * *` | 09:07 | `noticias-colombia.json` | `prompts/noticias-co.md` |
| `balance-co` | `7 16 * * *` | 18:07 | `colombia.html` | `prompts/balance-co.md` |
| `sitrep-ve` | `7 5 * * 5` (viernes) | 07:07 | `index.html` | `prompts/sitrep-ve.md` |

`recolectar.yml` ya no tiene cron: el recolector corre dentro de `publicar.yml`. Queda con
`workflow_dispatch` por si se quiere refrescar la materia prima a mano. `reconciliar.yml` sigue
igual (red de seguridad si producción y `main` divergen).

## Lo único manual, una sola vez: el secret
El paso de Claude usa la suscripción (Pro/Max), no una API key de pago:
1. En el Mac, en una terminal: `claude setup-token` → copia el token que imprime.
2. GitHub → repo `msb70/sosvenezuela` → Settings → Secrets and variables → Actions →
   New repository secret → nombre `CLAUDE_CODE_OAUTH_TOKEN`, valor el token.
3. Probar: Actions → «Publicar (recolectar + criterio + deploy)» → Run workflow → rutina `noticias-ve`.
Si el secret falta, el job falla en el primer paso con un mensaje claro. Si el token caduca,
falla en el paso 3 (rojo + email): repetir 1-2.

## Lanzar a mano / diagnosticar
- Lanzar: `gh workflow run publicar.yml --repo msb70/sosvenezuela -f rutina=noticias-ve`
- Ver: `gh run list --repo msb70/sosvenezuela --workflow publicar.yml --limit 5`
- Log de un run: `gh run view <id> --repo msb70/sosvenezuela --log`
- La prueba de verdad, siempre: `curl -s "https://apoyo-fem-vzla.org/noticias.json?v=$RANDOM" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['actualizado'],len(d['items']))"`

## Cambiar el criterio editorial
Editar `docs/tareas/CRITERIO-VE.md` / `CRITERIO-CO.md` o el prompt correspondiente en
`docs/tareas/prompts/` y hacer commit a `main`. La siguiente corrida ya lo usa. No hay nada
que tocar en claude.ai.

## Reglas que siguen valiendo
1. Verificar producción, nunca el push. (El workflow lo hace en el paso 7.)
2. El deploy reconstruye la web entera desde `main`: por eso el archivo editado parte de producción
   (paso 2) y así cada publicación reconcilia de paso.
3. Claude solo toca el archivo de su rutina; el workflow falla si cambió algo más.
4. Publicar a mano desde el Mac sigue funcionando igual (commit + push a `main`); reconciliar antes.
