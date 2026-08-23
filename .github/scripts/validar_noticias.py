#!/usr/bin/env python3
"""Valida los JSON de noticias antes de publicar el sitio.

Un JSON roto o incompleto deja la sección de noticias vacía en producción, así que
esto corre en CI y bloquea el deploy si algo no cuadra.
"""
import json
import sys

CAMPOS = ("id", "fecha", "titulo", "resumen", "fuente", "categoria", "url")
fallos = []

for ruta in sys.argv[1:]:
    try:
        with open(ruta, encoding="utf-8") as fh:
            datos = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        fallos.append(f"{ruta}: no se pudo leer como JSON -> {exc}")
        continue

    items = datos.get("items")
    if not isinstance(items, list) or not items:
        fallos.append(f"{ruta}: 'items' vacío o no es una lista")
        continue
    if not datos.get("actualizado"):
        fallos.append(f"{ruta}: falta el campo 'actualizado'")

    ids = [i.get("id") for i in items]
    duplicados = {x for x in ids if ids.count(x) > 1}
    if duplicados:
        fallos.append(f"{ruta}: ids duplicados -> {sorted(duplicados)}")

    for item in items:
        faltantes = [c for c in CAMPOS if not item.get(c)]
        if faltantes:
            fallos.append(f"{ruta}: item {item.get('id', '?')} sin {faltantes}")
        url = item.get("url", "")
        if url and not url.startswith(("http://", "https://")):
            fallos.append(f"{ruta}: item {item.get('id', '?')} con url no http -> {url}")

    print(f"OK {ruta}: {len(items)} items, actualizado {datos.get('actualizado')}")

if fallos:
    for f in fallos:
        print(f"::error::{f}")
    sys.exit(1)
print("Validación de noticias correcta.")
