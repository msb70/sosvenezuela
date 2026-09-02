# Criterio editorial — Noticias de Colombia (`noticias-colombia.json`, sección 03 de colombia.html) y balance

Terremoto del **10 de agosto de 2026** (Chocó / Valle del Cauca; Cali es la ciudad más
golpeada; también Buenaventura, Pereira, Trujillo). Archivo propio, independiente del de
Venezuela. `id`: `co-AAAAMMDD-medio-tema`.

## Qué entra
Terremoto y réplicas de la secuencia del Chocó, rescates y búsqueda, balance de víctimas
y damnificados (UNGRD, Alcaldía de Cali, Gobernación del Valle), reconstrucción y
financiación (Fondo Milagro, emergencia económica, subsidios, SAE, Camacol), ayuda
humanitaria y donaciones, albergues, educación y salud afectadas, infraestructura y
servicios, economía de la reconstrucción, **alertas de estafa a damnificados** (de lo más
útil: el único trámite real es el RUFE; canal oficial WhatsApp Alcaldía de Cali
324 6900888).

## Qué NO entra
- Farándula, deportes, tecnología, sucesos sin relación con el sismo.
- Política internacional ajena a la emergencia y **declaraciones político-partidistas**.
  Los anuncios de ayuda del Ejecutivo SÍ entran, pero **despersonalizados**: «El Gobierno
  anuncia…», nunca el nombre del presidente en el titular (De la Espriella).
- Sismos ajenos a la secuencia: el nido de Los Santos (Santander) y los microsismos del
  Cauca ligados al volcán Puracé no cuentan. Los «temblor hoy» de M<4 sin daños, tampoco.
- Emergencias no sísmicas (combates en Chocó, lluvias sin relación).

## Fuentes (todo por curl/RSS, sin WebFetch — `python3 docs/tareas/barrer_fuentes.py co`)
- **El País (Cali)** — la más productiva: RSS `arc/outboundfeeds/rss/category/cali/` y
  el general. La portada por curl solo trae 3 URLs (JS): usar el RSS. **Fuente = `El País (Cali)`.**
- **El Tiempo**: `rss/colombia.xml` y `sitemap-google-news.xml` (600 items).
- **Semana**, **Infobae** (`rss/category/colombia/`), **El Colombiano** (`sitemapforgoogle.xml`).
- **Noticias ONU** (RSS Américas), **ReliefWeb** (filtro PC47).
- CNN Español (451), France 24 (robots), Pulzo/Portafolio/El Heraldo (sin RSS útil).
- La fecha de la portada no siempre coincide con `article:published_time`: **fechar por
  el HTML del artículo**.

## Campos
- Categorías en uso: Balance y cifras · Rescates y búsqueda · Reconstrucción · Ayuda
  humanitaria · Educación · Salud · Infraestructura y servicios · Réplicas y sismología ·
  Opinión. Las piezas de impacto económico van en «Reconstrucción».
- `fuente` vigentes: CNN Español · Cruz Roja Colombiana · El Colombiano · El Heraldo ·
  El Nuevo Siglo · El País (Cali) · El Tiempo · Forbes Colombia · France 24 · Infobae ·
  Noticias ONU · Portafolio · Pulzo · Radio Santa Fe · Semana · TuBarco Noticias ·
  Vanguardia. Comprobar la lista real en el JSON antes de escribir.
- No se usan `espejo`s (la prensa colombiana no está bloqueada).

## Trampas de cifras
- **Hay DOS subsidios distintos**: 1.050.000 COP/mes × 3 (Buenaventura 24/08 y Valle
  28/08) y Fondo Milagro nacional 875.452 COP/mes × 3 (pagos desde el 26/08). No
  fusionarlos; si sale una pieza que aclare si uno absorbe al otro, es prioritaria.
- Balances de Cali de días consecutivos no cuadran entre sí (30/08: 32.882 familias y
  610 no habitables; 31/08: 36.427 familias, 631 no habitables, 154 fallecidos). Citar
  siempre la fecha de corte; nunca promediar ni mezclar.
- Las cifras de Confecámaras (269.786 empresas expuestas) son PREVIAS al sismo: no son daños.

## Balance oficial (tarea `balance-colombia-diario`, KPI de colombia.html)
- Fuente de verdad: **balance nacional de la UNGRD** con fecha de corte explícita (vía
  El Tiempo, Infobae, El Colombiano, Vanguardia o ungrd.gov.co). Último publicado en la
  página: **331 fallecidos y 213.40x damnificados (30/08)**.
- Si dos medios se contradicen, gana la UNGRD; anotar la discrepancia en el resumen.
- **Si las cifras no cambiaron, no tocar el HTML** y decirlo: es un resultado válido.
- Antes de subir `colombia.html`: debe contener `kpiFallecidos`, `noticias-colombia.json`
  y `</html>`, y su tamaño no debe desviarse más de un 2 % del de producción.
