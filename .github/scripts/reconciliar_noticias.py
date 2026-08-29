#!/usr/bin/env python3
"""Reconcilia los JSON de noticias entre el repositorio y producción.

Las tareas programadas de Cowork pueden publicar directamente a Hostinger sin pasar
por git. Cuando eso ocurre, producción se adelanta al repositorio y el siguiente
despliegue desde `main` borraría lo publicado. Este script hace lo contrario de elegir
un ganador: **une los items por `id`**, de modo que ni el repositorio ni producción
pierden nada nunca.

Salida (para GITHUB_OUTPUT):
  repo_cambiado=true|false   -> hay que commitear a main
  prod_desfasada=true|false  -> hay que relanzar el deploy para actualizar la web
"""
import json
import os
import sys
import urllib.request

BASE_PROD = "https://apoyo-fem-vzla.org"
ARCHIVOS = ["noticias.json", "noticias-colombia.json"]
CAMPOS = ("id", "fecha", "titulo", "resumen", "fuente", "tipoFuente", "categoria", "tipo", "url")


def bajar(nombre):
    url = "%s/%s" % (BASE_PROD, nombre)
    req = urllib.request.Request(url, headers={"User-Agent": "sosvzla-reconcile/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def valido(doc, origen):
    if not isinstance(doc, dict) or "items" not in doc or "actualizado" not in doc:
        print("::error::%s no tiene la forma esperada" % origen)
        return False
    for it in doc["items"]:
        faltan = [c for c in CAMPOS if not it.get(c)]
        if faltan:
            print("::error::%s: item %r sin %s" % (origen, it.get("id"), ", ".join(faltan)))
            return False
    return True


def unir(repo, prod):
    """Union por id. Ante el mismo id gana la versión de producción (es la más reciente)."""
    fusion = {}
    for it in repo["items"]:
        fusion[it["id"]] = it
    for it in prod["items"]:
        fusion[it["id"]] = it
    items = sorted(fusion.values(), key=lambda x: (x["fecha"], x["id"]), reverse=True)
    doc = dict(repo)
    doc.update({k: v for k, v in prod.items() if k != "items"})
    doc["items"] = items
    doc["actualizado"] = max(repo["actualizado"], prod["actualizado"])
    return doc


def firma(doc):
    return json.dumps(doc, ensure_ascii=False, sort_keys=True)


def main():
    repo_cambiado = False
    prod_desfasada = False
    resumen = []

    for nombre in ARCHIVOS:
        with open(nombre, encoding="utf-8") as f:
            repo = json.load(f)
        try:
            prod = bajar(nombre)
        except Exception as e:
            print("::error::no se pudo leer %s de producción: %s" % (nombre, e))
            return 1

        if not valido(repo, "repo/" + nombre) or not valido(prod, "prod/" + nombre):
            return 1

        fusion = unir(repo, prod)
        ids_repo = {i["id"] for i in repo["items"]}
        ids_prod = {i["id"] for i in prod["items"]}

        if firma(fusion) != firma(repo):
            with open(nombre, "w", encoding="utf-8") as f:
                json.dump(fusion, f, ensure_ascii=False, indent=2)
                f.write("\n")
            repo_cambiado = True
        if firma(fusion) != firma(prod):
            prod_desfasada = True

        resumen.append(
            "%s: repo %d, prod %d, fusion %d | solo en prod: %d | solo en repo: %d"
            % (nombre, len(ids_repo), len(ids_prod), len(fusion["items"]),
               len(ids_prod - ids_repo), len(ids_repo - ids_prod))
        )

    for linea in resumen:
        print(linea)

    salida = os.environ.get("GITHUB_OUTPUT")
    if salida:
        with open(salida, "a", encoding="utf-8") as f:
            f.write("repo_cambiado=%s\n" % str(repo_cambiado).lower())
            f.write("prod_desfasada=%s\n" % str(prod_desfasada).lower())
    return 0


if __name__ == "__main__":
    sys.exit(main())
