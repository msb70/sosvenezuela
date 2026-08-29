#!/usr/bin/env python3
"""Trae a `main` los cambios de index.html / colombia.html hechos solo en producción.

La tarea del balance diario edita los KPI dentro de colombia.html. Si esa sesión publica
a Hostinger sin poder commitear, el siguiente despliegue desde `main` revertiría el balance.
Aquí no se puede fusionar como con los JSON (es un blob), así que **gana producción**, pero
solo si pasa unas comprobaciones de cordura: si no las pasa, el run falla en rojo y se ve.

Salida (GITHUB_OUTPUT): html_cambiado=true|false
"""
import os
import sys
import urllib.request

BASE_PROD = "https://apoyo-fem-vzla.org"

# archivo -> marcadores que el HTML de producción DEBE contener para aceptarlo
ARCHIVOS = {
    "index.html": ["noticias.json", "</html>", "<title"],
    "colombia.html": ["noticias-colombia.json", "kpiFallecidos", "</html>"],
}


def bajar(nombre):
    req = urllib.request.Request("%s/%s" % (BASE_PROD, nombre),
                                 headers={"User-Agent": "sosvzla-reconcile/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8")


def main():
    cambiado = False
    for nombre, marcadores in ARCHIVOS.items():
        with open(nombre, encoding="utf-8") as f:
            repo = f.read()
        try:
            prod = bajar(nombre)
        except Exception as e:
            print("::error::no se pudo leer %s de producción: %s" % (nombre, e))
            return 1

        if prod == repo:
            print("%s: idéntico" % nombre)
            continue

        faltan = [m for m in marcadores if m not in prod]
        if faltan:
            print("::error::%s en producción no contiene %s — no lo traigo a main"
                  % (nombre, ", ".join(repr(m) for m in faltan)))
            return 1
        ratio = len(prod) / float(len(repo))
        if not (0.5 <= ratio <= 2.0):
            print("::error::%s en producción mide %d bytes frente a %d en el repo "
                  "(x%.2f) — demasiado raro, no lo traigo a main"
                  % (nombre, len(prod), len(repo), ratio))
            return 1

        with open(nombre, "w", encoding="utf-8") as f:
            f.write(prod)
        cambiado = True
        print("%s: producción iba por delante (%d -> %d bytes), traído a main"
              % (nombre, len(repo), len(prod)))

    salida = os.environ.get("GITHUB_OUTPUT")
    if salida:
        with open(salida, "a", encoding="utf-8") as f:
            f.write("html_cambiado=%s\n" % str(cambiado).lower())
    return 0


if __name__ == "__main__":
    sys.exit(main())
