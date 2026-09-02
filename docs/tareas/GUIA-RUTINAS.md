# Guía: publicación automática sin Mac y sin nadie aprobando

## La arquitectura (por qué son dos piezas)
El entorno donde corren las rutinas (Claude Code en la nube) puede hacer `git push` pero
**solo tiene red hacia GitHub**: no puede leer prensa ni `apoyo-fem-vzla.org`. GitHub Actions
sí tiene red abierta pero no aplica criterio editorial. Así que el trabajo se parte:

```
GitHub Actions (recolectar.yml)          Rutina (Claude Code, ligada al repo)
  · lee la prensa por RSS                   · clona el repo (solo GitHub)
  · verifica fecha y baja el cuerpo         · lee candidatos-*.json y produccion-*.json
  · snapshot de producción                  · aplica el criterio editorial
  · baja los PDF de los SitReps      ──▶    · edita el JSON / HTML
  · commitea la materia prima a main        · git push a main
                                            · verifica por la rama deploy
                              deploy.yml construye deploy → Hostinger sirve en <1 min
```
Ninguna pieza usa el conector Hostinger, ni WebFetch, ni el Mac. Nada pide permiso.

## Horarios (todo UTC)
| Pieza | Cron UTC | Madrid |
|---|---|---|
| recolectar.yml (mañana: prensa VE+CO) | `40 7 * * *` | 09:40 |
| rutina noticias VE | `0 8 * * *` | 10:00 |
| rutina noticias CO | `0 9 * * *` | 11:00 |
| recolectar.yml (tarde: prensa CO) | `40 16 * * *` | 18:40 |
| rutina balance CO | `0 18 * * *` | 20:00 |
| recolectar.yml (viernes: SitReps + PDF) | `30 6 * * 5` | vie 08:30 |
| rutina SitRep VE | `0 7 * * 5` | vie 09:00 |

El recolector corre ~20 min antes de cada rutina. Si un día no corre, la rutina lo detecta
(la materia prima no es de hoy) y avisa por push sin publicar a ciegas.

## Paso a paso (una vez, desde claude.ai/code con el repo msb70/sosvenezuela seleccionado)
Ya comprobaste que en ese contexto `git push` a `main` funciona. Ahora:

1. Menú lateral → **Rutinas** → **Nueva rutina**, con el chip **sosvenezuela · main** puesto.
2. Crea las cuatro, pegando ENTERO el archivo de prompt indicado (están en el repo):
   | nombre | cron | prompt |
   |---|---|---|
   | noticias-terremoto-venezuela-diario | `0 8 * * *` | prompts/noticias-venezuela-diario.md |
   | noticias-terremoto-colombia-diario | `0 9 * * *` | prompts/noticias-colombia-diario.md |
   | balance-colombia-diario | `0 18 * * *` | prompts/balance-colombia-diario.md |
   | sitrep-ocha-venezuela-quincenal | `0 7 * * 5` | prompts/sitrep-ocha-venezuela-quincenal.md |
   Modelo: Opus. Notificaciones: push ON.
3. Antes de fiarte, lanza a mano el recolector y una rutina:
   - En el chat (contexto sosvenezuela · main): `gh workflow run recolectar.yml` y espera ~2 min,
     o entra a GitHub → Actions → "Recolectar materia prima" → Run workflow.
   - Comprueba que en el repo aparecieron/actualizaron `docs/tareas/candidatos-ve.json`
     y `produccion-ve.json` con la fecha de hoy.
   - Lanza la rutina de Venezuela ("Run now"), abre la sesión: debe terminar SIN ningún cuadro
     «¿Permitir…?», con un SHA, y el bloque de verificación debe mostrar la rama `deploy` con
     `actualizado` de hoy.
   - Abre `https://apoyo-fem-vzla.org/noticias.json` en el navegador: `actualizado` de hoy.
4. Cuando funcione, avísame y **desactivo las cuatro rutinas viejas** (las creadas desde Cowork)
   para que no corran dos a la vez.

## Qué NO hacer
- No metas WebFetch, WebSearch, curl a prensa ni MCP en los prompts: la rutina no necesita red
  más allá de GitHub, y esas herramientas piden permiso o fallan.
- No pongas protección de rama en `main`: rompería el push de las rutinas. La red de seguridad
  está en `deploy.yml` (valida los JSON antes de publicar), no en la rama.
- El recolector escribe en `docs/tareas/`, que NO se despliega (no está en la lista `ARCHIVOS`
  de deploy.yml). Las rutinas no deben commitear esos archivos.
