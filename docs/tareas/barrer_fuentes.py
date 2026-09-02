#!/usr/bin/env python3
"""Barre los feeds RSS / sitemaps de la prensa y lista los candidatos del terremoto.

Uso (desde cualquier carpeta):
    python3 docs/tareas/barrer_fuentes.py ve [--dias 2]     # Venezuela
    python3 docs/tareas/barrer_fuentes.py co [--dias 2]     # Colombia

Todo va por `curl`-equivalente (urllib) con user-agent de Chrome: NO usa WebFetch ni
WebSearch, que en las sesiones programadas piden permiso y dejan la sesión colgada.
Imprime, por fuente, los items de los últimos N días cuyo título o resumen mencionan
el sismo. La fecha que imprime es la del feed: CONFIRMARLA en el HTML del artículo
(`article:published_time`) antes de publicar nada.
"""
import re
import sys
import json
import html
import argparse
import datetime as dt
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")

# fuente -> (url, nombre EXACTO que se usa en el campo `fuente` del JSON)
FUENTES = {
    "ve": [
        ("https://www.elnacional.com/feed/", "El Nacional"),
        ("https://efectococuyo.com/feed/", "Efecto Cocuyo"),
        ("https://cronica.uno/feed/", "Crónica.Uno"),
        ("https://lapatilla.com/feed/", "La Patilla"),
        ("https://lapatilla.com/?s=terremoto", "La Patilla"),
        ("https://efectococuyo.com/?s=terremoto", "Efecto Cocuyo"),
        ("https://www.infobae.com/arc/outboundfeeds/rss/category/venezuela/", "Infobae"),
        ("https://news.un.org/feed/subscribe/es/news/region/americas/feed/rss.xml", "Noticias ONU"),
        ("https://reliefweb.int/updates/rss.xml?advanced-search=%28PC250%29", "ReliefWeb"),
    ],
    "co": [
        ("https://www.elpais.com.co/arc/outboundfeeds/rss/category/cali/?outputType=xml", "El País (Cali)"),
        ("https://www.elpais.com.co/arc/outboundfeeds/rss/?outputType=xml", "El País (Cali)"),
        ("https://www.eltiempo.com/rss/colombia.xml", "El Tiempo"),
        ("https://www.eltiempo.com/sitemap-google-news.xml", "El Tiempo"),
        ("https://www.semana.com/arc/outboundfeeds/rss/?outputType=xml", "Semana"),
        ("https://www.infobae.com/arc/outboundfeeds/rss/category/colombia/", "Infobae"),
        ("https://www.elcolombiano.com/sitemapforgoogle.xml", "El Colombiano"),
        ("https://news.un.org/feed/subscribe/es/news/region/americas/feed/rss.xml", "Noticias ONU"),
        ("https://reliefweb.int/updates/rss.xml?advanced-search=%28PC47%29", "ReliefWeb"),
    ],
}

PALABRAS = re.compile(r"terremoto|sismo|s[ií]smic|r[eé]plica|damnificad|escombro|"
                      r"reconstrucci|albergue|campamento|maiquet|funvisis|ungrd|"
                      r"fondo milagro|rufe", re.I)
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
      "news": "http://www.google.com/schemas/sitemap-news/0.9"}


def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def fecha(s):
    if not s:
        return None
    s = s.strip()
    for f in (parsedate_to_datetime, dt.datetime.fromisoformat):
        try:
            d = f(s.replace("Z", "+00:00"))
            return d.date()
        except Exception:
            pass
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    return dt.date(*map(int, m.groups())) if m else None


def limpiar(t):
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def parse_rss(raw):
    root = ET.fromstring(raw)
    for it in root.iter("item"):
        yield {
            "titulo": limpiar(it.findtext("title")),
            "url": (it.findtext("link") or "").strip(),
            "fecha": fecha(it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")),
            "resumen": limpiar(it.findtext("description"))[:220],
        }


def parse_sitemap(raw):
    root = ET.fromstring(raw)
    for u in root.findall("sm:url", NS):
        yield {
            "titulo": limpiar(u.findtext("news:news/news:title", default="", namespaces=NS)),
            "url": (u.findtext("sm:loc", default="", namespaces=NS)).strip(),
            "fecha": fecha(u.findtext("news:news/news:publication_date", default="", namespaces=NS)
                           or u.findtext("sm:lastmod", default="", namespaces=NS)),
            "resumen": "",
        }


def parse_html(raw):
    txt = raw.decode("utf-8", "ignore")
    vistos = set()
    for m in re.finditer(r'href="(https?://[^"]+/20\d\d/\d\d/[^"]+)"', txt):
        u = m.group(1)
        if u in vistos:
            continue
        vistos.add(u)
        f = re.search(r"/(20\d\d)/(\d\d)/(?:(\d\d)/)?", u)
        d = dt.date(int(f.group(1)), int(f.group(2)), int(f.group(3) or 1)) if f else None
        yield {"titulo": u.rsplit("/", 2)[-2].replace("-", " ") if u.endswith("/") else u.rsplit("/", 1)[-1],
               "url": u, "fecha": d, "resumen": ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pais", choices=("ve", "co"))
    ap.add_argument("--dias", type=int, default=2)
    ap.add_argument("--json", action="store_true", help="salida JSON en vez de texto")
    a = ap.parse_args()
    desde = dt.date.today() - dt.timedelta(days=a.dias)
    salida = []
    ok = 0
    errores = 0
    for url, fuente in FUENTES[a.pais]:
        try:
            raw = bajar(url)
            ok += 1
        except Exception as e:
            errores += 1
            print("## %s — ERROR %s (%s)" % (fuente, e, url), file=sys.stderr)
            continue
        head = raw[:300].lower()
        if b"<rss" in head or b"<feed" in head or b"<item>" in raw[:5000]:
            items = list(parse_rss(raw))
        elif b"<urlset" in head or b"<urlset" in raw[:5000]:
            items = list(parse_sitemap(raw))
        else:
            items = list(parse_html(raw))
        vistos = set()
        cand = []
        for it in items:
            if not it["url"] or it["url"] in vistos:
                continue
            vistos.add(it["url"])
            if it["fecha"] and it["fecha"] < desde:
                continue
            if not PALABRAS.search(it["titulo"] + " " + it["resumen"] + " " + it["url"]):
                continue
            it["fuente"] = fuente
            cand.append(it)
        salida.extend(cand)
        if not a.json:
            print("## %s — %d candidatos de %d items (%s)" % (fuente, len(cand), len(items), url))
            for it in cand:
                print("  %s | %s\n      %s" % (it["fecha"], it["titulo"][:110], it["url"]))
    if a.json:
        print(json.dumps([dict(i, fecha=str(i["fecha"])) for i in salida], ensure_ascii=False, indent=1))

    total = len(FUENTES[a.pais])
    print("RESUMEN: %d/%d fuentes leídas, %d con error, %d candidatos" % (ok, total, errores, len(salida)),
          file=sys.stderr)
    if ok == 0:
        print("::error::NINGUNA fuente respondió: casi seguro la red del entorno está bloqueada "
              "(403 en el proxy). NO publiques nada: no es un día sin noticias, es un día sin lectura.",
              file=sys.stderr)
        return 2
    if ok < total // 2:
        print("::warning::menos de la mitad de las fuentes respondieron; revisa antes de publicar",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
