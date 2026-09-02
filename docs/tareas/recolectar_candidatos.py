#!/usr/bin/env python3
"""Recolector de materia prima para las rutinas de noticias. CORRE EN GITHUB ACTIONS.

El entorno donde corren las rutinas (Claude Code en la nube) solo tiene red hacia GitHub:
no puede leer prensa ni apoyo-fem-vzla.org. GitHub Actions sí tiene red abierta. Así que
este script hace TODA la parte que necesita internet y deja el resultado en el repo:

  docs/tareas/candidatos-ve.json   — noticias candidatas de Venezuela, ya con fecha
                                     verificada del artículo y cuerpo de texto extraído.
  docs/tareas/candidatos-co.json   — idem Colombia.
  docs/tareas/produccion-ve.json   — copia EXACTA del noticias.json que sirve producción
                                     ahora mismo (para reconciliar sin tocar la red).
  docs/tareas/produccion-co.json   — idem noticias-colombia.json.
  docs/tareas/sitreps-ve.json      — lista de SitReps de OCHA/OIM/UNICEF disponibles + el
                                     texto plano de los que trae adjunto (para la rutina
                                     quincenal), extraído del PDF con pdftotext.

La rutina, que solo ve GitHub, clona el repo y trabaja con estos archivos: no necesita
red más allá de GitHub. El criterio editorial (qué entra, reescribir titulares, etc.) lo
aplica la rutina, no este script.

Uso:  python3 docs/tareas/recolectar_candidatos.py            # todo
       python3 docs/tareas/recolectar_candidatos.py --solo ve # solo Venezuela
       python3 docs/tareas/recolectar_candidatos.py --dias 3
"""
import os
import re
import sys
import json
import html
import time
import shutil
import argparse
import subprocess
import datetime as dt
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
PROD = "https://apoyo-fem-vzla.org"
AQUI = os.path.dirname(os.path.abspath(__file__))

FUENTES = {
    "ve": [
        ("https://www.elnacional.com/feed/", "El Nacional"),
        ("https://efectococuyo.com/feed/", "Efecto Cocuyo"),
        ("https://cronica.uno/feed/", "Crónica.Uno"),
        ("https://lapatilla.com/feed/", "La Patilla"),
        ("https://lapatilla.com/?s=terremoto", "La Patilla"),
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
                      r"fondo milagro|rufe|guaira|catia", re.I)
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
      "news": "http://www.google.com/schemas/sitemap-news/0.9"}


def bajar(url, binario=False, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binario else data.decode("utf-8", "ignore")


def a_fecha(s):
    if not s:
        return None
    s = s.strip()
    for f in (parsedate_to_datetime, dt.datetime.fromisoformat):
        try:
            return f(s.replace("Z", "+00:00")).date()
        except Exception:
            pass
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    return dt.date(*map(int, m.groups())) if m else None


def limpiar(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip()


def items_de(raw, url):
    head = raw[:400].lower()
    es_xml = "<urlset" in head or "<rss" in head or "<feed" in head or "<?xml" in head
    if es_xml:
        root = ET.fromstring(raw.encode("utf-8") if isinstance(raw, str) else raw)
        if "<urlset" in head:
            for u in root.findall("sm:url", NS):
                yield {"titulo": limpiar(u.findtext("news:news/news:title", default="", namespaces=NS)),
                       "url": (u.findtext("sm:loc", default="", namespaces=NS)).strip(),
                       "fecha": a_fecha(u.findtext("news:news/news:publication_date", default="", namespaces=NS)),
                       "resumen": ""}
        else:
            for it in root.iter("item"):
                yield {"titulo": limpiar(it.findtext("title")),
                       "url": (it.findtext("link") or "").strip(),
                       "fecha": a_fecha(it.findtext("pubDate")),
                       "resumen": limpiar(it.findtext("description"))[:220]}
    else:
        vistos = set()
        for m in re.finditer(r'href="(https?://[^"]+/20\d\d/\d\d/[^"]+)"', raw):
            u = m.group(1)
            if u in vistos:
                continue
            vistos.add(u)
            f = re.search(r"/(20\d\d)/(\d\d)/(?:(\d\d)/)?", u)
            d = dt.date(int(f.group(1)), int(f.group(2)), int(f.group(3) or 1)) if f else None
            yield {"titulo": u.rstrip("/").rsplit("/", 1)[-1].replace("-", " "),
                   "url": u, "fecha": d, "resumen": ""}


META_FECHA = re.compile(
    r'(?:article:published_time|datePublished)"?\s*[:=]?\s*["\']?'
    r'(\d{4}-\d{2}-\d{2}[T ][\d:]+)', re.I)


def leer_articulo(url):
    """Devuelve (fecha_real, cuerpo_texto) del artículo, o (None, '') si falla."""
    try:
        raw = bajar(url, timeout=30)
    except Exception:
        return None, ""
    m = META_FECHA.search(raw)
    fecha = a_fecha(m.group(1)) if m else None
    cuerpo = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    m2 = re.search(r"<article[^>]*>(.*?)</article>", cuerpo, re.S | re.I)
    cuerpo = limpiar(m2.group(1) if m2 else cuerpo)
    return fecha, cuerpo[:1800]


def recolectar_pais(pais, dias):
    desde = dt.date.today() - dt.timedelta(days=dias)
    fuentes_ok = 0
    candidatos = []
    vistos = set()
    for url, fuente in FUENTES[pais]:
        try:
            raw = bajar(url)
            fuentes_ok += 1
        except Exception as e:
            print("  [%s] ERROR feed: %s (%s)" % (fuente, e, url), file=sys.stderr)
            continue
        try:
            items = list(items_de(raw, url))
        except Exception as e:
            print("  [%s] ERROR parse: %s" % (fuente, e), file=sys.stderr)
            continue
        for it in items:
            u = it["url"]
            if not u or u in vistos:
                continue
            if not PALABRAS.search(it["titulo"] + " " + it["resumen"] + " " + u):
                continue
            if it["fecha"] and it["fecha"] < desde:
                continue
            vistos.add(u)
            fecha_art, cuerpo = leer_articulo(u)
            fecha = fecha_art or it["fecha"]
            if fecha and fecha < desde:
                continue
            candidatos.append({
                "fuente": fuente,
                "titulo": it["titulo"],
                "url": u,
                "fecha": str(fecha) if fecha else None,
                "resumen_feed": it["resumen"],
                "cuerpo": cuerpo,
                "http_ok": bool(cuerpo),
            })
            time.sleep(0.3)
    candidatos.sort(key=lambda c: (c["fecha"] or "", c["fuente"]), reverse=True)
    candidatos = candidatos[:40]   # el repo no necesita más; la rutina filtra por criterio
    if fuentes_ok == 0:
        raise RuntimeError("[%s] ninguna fuente respondió: red bloqueada" % pais)
    salida = {
        "generado": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "pais": pais,
        "dias": dias,
        "fuentes_leidas": fuentes_ok,
        "fuentes_totales": len(FUENTES[pais]),
        "candidatos": candidatos,
    }
    ruta = os.path.join(AQUI, "candidatos-%s.json" % pais)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print("[%s] %d candidatos de %d/%d fuentes -> %s"
          % (pais, len(candidatos), fuentes_ok, len(FUENTES[pais]), ruta))
    return salida


def snapshot_produccion():
    """Copia el noticias.json / noticias-colombia.json que sirve producción AHORA."""
    for nombre, dest in (("noticias.json", "produccion-ve.json"),
                         ("noticias-colombia.json", "produccion-co.json")):
        try:
            data = bajar("%s/%s?v=%d" % (PROD, nombre, int(time.time())))
            doc = json.loads(data)
            with open(os.path.join(AQUI, dest), "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            print("[prod] %s -> %s (%s, %d items)"
                  % (nombre, dest, doc.get("actualizado"), len(doc.get("items", []))))
        except Exception as e:
            print("[prod] ERROR %s: %s" % (nombre, e), file=sys.stderr)


def recolectar_sitreps():
    """Lista los SitReps de OCHA para Venezuela y baja el texto de los recientes."""
    dir_txt = os.path.join(AQUI, "sitreps")
    if os.path.isdir(dir_txt):
        shutil.rmtree(dir_txt)   # solo quedan los reportes vigentes, no se acumulan
    os.makedirs(dir_txt, exist_ok=True)
    try:
        raw = bajar("https://reliefweb.int/updates/rss.xml?advanced-search=%28PC250%29_%28F10%29")
        root = ET.fromstring(raw)
    except Exception as e:
        print("[sitrep] ERROR RSS: %s" % e, file=sys.stderr)
        return
    reportes = []
    for it in list(root.iter("item"))[:8]:
        titulo = limpiar(it.findtext("title"))
        link = (it.findtext("link") or "").strip()
        fecha = a_fecha(it.findtext("pubDate"))
        txt_rel = ""
        try:
            pag = bajar(link, timeout=30)
            m = re.search(r'href="(/attachments/[^"]+\.pdf[^"]*)"', pag)
            if m:
                pdf_url = "https://reliefweb.int" + html.unescape(m.group(1))
                slug = re.sub(r"[^a-z0-9]+", "-", titulo.lower())[:60].strip("-")
                pdf_path = os.path.join(dir_txt, slug + ".pdf")
                with open(pdf_path, "wb") as f:
                    f.write(bajar(pdf_url, binario=True, timeout=90))
                if shutil.which("pdftotext"):
                    txt_path = os.path.join(dir_txt, slug + ".txt")
                    subprocess.run(["pdftotext", "-layout", pdf_path, txt_path], check=False)
                    txt_rel = "sitreps/" + slug + ".txt"
                os.remove(pdf_path)
        except Exception as e:
            print("[sitrep] %s: %s" % (titulo[:40], e), file=sys.stderr)
        reportes.append({"titulo": titulo, "url": link,
                         "fecha": str(fecha) if fecha else None, "texto": txt_rel})
    with open(os.path.join(AQUI, "sitreps-ve.json"), "w", encoding="utf-8") as f:
        json.dump({"generado": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                   "reportes": reportes}, f, ensure_ascii=False, indent=2)
    print("[sitrep] %d reportes listados, %d con texto"
          % (len(reportes), sum(1 for r in reportes if r["texto"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=("ve", "co"), help="recolectar solo un país")
    ap.add_argument("--dias", type=int, default=2)
    ap.add_argument("--sitreps", action="store_true", help="incluir SitReps (más lento)")
    a = ap.parse_args()
    fallo = False
    paises = [a.solo] if a.solo else ["ve", "co"]
    for pais in paises:
        try:
            recolectar_pais(pais, a.dias)
        except Exception as e:
            print("ERROR %s" % e, file=sys.stderr)
            fallo = True
    snapshot_produccion()
    if a.sitreps or not a.solo:
        recolectar_sitreps()
    return 1 if fallo else 0


if __name__ == "__main__":
    sys.exit(main())
