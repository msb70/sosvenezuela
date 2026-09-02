# Criterio editorial — Noticias de Venezuela (`noticias.json`, sección 05 del index)

Sección de noticias del terremoto del **24 de junio de 2026** en Venezuela. Multifuente:
una sola fuente no es una sección de noticias, es el feed de un medio. **Mínimo 3 fuentes
distintas** entre lo más reciente cuando hay material.

## Qué entra
Terremoto y réplicas, reconstrucción, respuesta y ayuda humanitaria, damnificados y
campamentos, educación y salud **afectadas por el sismo**, infraestructura y servicios
dañados (Maiquetía, puerto de La Guaira, vías, agua, electricidad), economía de la
reconstrucción (vivienda, subsidios, créditos, ley de vivienda), balances oficiales
(OCHA, Funvisis, gobierno), informes de organismos (OCHA/ReliefWeb, Noticias ONU, OPS,
UNICEF, OIM, PMA, ACNUR).

## Qué NO entra
- Farándula, deportes, tecnología general, cultura sin relación con el sismo.
- Política internacional y **declaraciones político-partidistas** (acuerdo petrolero con
  EEUU, reforma del TSJ, presos políticos, María Corina Machado, Trump, partidos): la FEM
  opera dentro de Venezuela y mantiene neutralidad. Aunque dominen la agenda del día.
- Fallos de servicios previos al sismo (p. ej. hospitales o diálisis que ya fallaban).
- Sismos ajenos a la secuencia del 24-J.

## Titulares con carga partidista → reescribir
Si un titular personaliza («régimen de…», «AN chavista…», «Delcy…»), **describe el hecho
y atribúyelo al organismo que lo anuncia**, o busca el mismo hecho en otro medio.
Ejemplos ya aplicados: «El puerto de La Guaira reactiva sus operaciones de importación y
gestión aduanera» (anuncio del Seniat) en vez del titular de La Patilla; «Promulgada la
ley para acelerar la construcción de viviendas…» en vez de personalizar.

## Zona gris: piezas de rendición de cuentas (ONG pidiendo transparencia, denuncias de
opacidad, Provea, Cecodap, Redhnna)
De facto se están publicando cuando describen un hecho verificable (registro de
desaparecidos, condiciones de retorno a clases). Publicarlas con titular descriptivo y
atribuido a la organización, nunca con lenguaje de campaña. Si dudas, descarta.

## Fuentes y cómo responden (verificado 02/09/2026 — todo por curl/RSS, sin WebFetch)
`python3 docs/tareas/barrer_fuentes.py ve` las barre todas de golpe. Detalle:
- **El Nacional**: `https://www.elnacional.com/feed/` (100 items) y
  `news-sitemap.xml`. La web está renderizada en JS: **no** sirve `/?s=` ni `/tag/`.
  Bloqueado por CANTV en Venezuela → si existe, añadir `espejo` (dominios rotatorios).
- **Efecto Cocuyo**: `https://efectococuyo.com/feed/` y `efectococuyo.com/?s=terremoto`.
- **Crónica.Uno**: `https://cronica.uno/feed/` (robots.txt bloquea WebFetch, curl sí).
- **La Patilla**: `https://lapatilla.com/?s=terremoto` **sin www** (con www da 301 y
  rompe el scrape). Ojo: el buscador mezcla un widget de «recientes»; confirmar por
  fecha en el HTML del artículo o en `lapatilla.com/AAAA/MM/DD/`.
- **Infobae**: `https://www.infobae.com/arc/outboundfeeds/rss/category/venezuela/`.
- **Noticias ONU**: RSS de Américas en español. **ReliefWeb**: RSS con filtro país
  (PC250). La API v1 de ReliefWeb está retirada (410) y la v2 da 403 desde el contenedor.
- CNN Español (451), unocha.org (403), eldiario.com (bucle de redirecciones): no perder
  tiempo. WebFetch está prohibido en las tareas (pide permiso y cuelga la sesión).

## Campos
- Categorías en uso: Reconstrucción · Infraestructura y servicios · Ayuda humanitaria ·
  Educación · Salud · Balance y cifras · Réplicas y sismología · Colombia · Opinión.
  Los chips se calculan solos desde el JSON. Reutilizar antes que inventar.
- `fuente` vigentes (escribir EXACTAMENTE así): CNN Español · Crónica.Uno · Efecto Cocuyo ·
  El Diario · El Nacional · Infobae · La Patilla · OCHA · OIM · ReliefWeb · Telemundo ·
  Vanguardia · Noticias ONU. Comprobar la lista real en el JSON antes de escribir.
- `tipoFuente: "oficial"` para OCHA/ONU/OPS/OIM/organismos; `tipo: "opinion"` para columnas.
- Resumen: 2-3 frases con el hecho, la cifra y la fuente del dato. Sin adjetivos.
- No mezclar el balance de OCHA con el de la prensa: son cortes distintos; citar fecha.

## Contexto vigente (para no repetir ni contradecir lo publicado)
- Maiquetía reabrió el 1/09/2026 con terminales temporales (hasta 2027); aerolíneas
  volviendo (Air Europa, Iberia, Copa, Avianca, American el 3/09). Puerto de La Guaira
  reactivó importación y aduana el 31/08 (Seniat).
- OCHA publica SitRep **cada dos semanas** desde el #34 (27/08). Cifras vigentes del #34:
  6.509 fallecidos (corte 24/08), 60.785 viviendas evaluadas, 11.001 de alto riesgo,
  28,61 % de escombros, 335 viviendas entregadas, 363.900 personas asistidas (26/08).
- Vivienda: subsidios 80 %/50 % según precio, crédito hasta 25 años; ~17.900
  damnificados; el Parlamento estima 25.000 unidades necesarias. Son estimaciones de
  fuentes distintas: no sumarlas.
- Funvisis (27/08): 1.861 eventos sísmicos desde el 24-J.
- Educación: +900 planteles dañados (MinEducación vía SitRep 34); Cecodap/Redhnna (31/08)
  dice que no hay condiciones para el retorno presencial.
