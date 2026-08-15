#!/usr/bin/env python3
"""
leadgen.py
Busca negocios locales para prospeccion de clientes freelance (venta de landing
pages / ecommerce / paginas web).

Fuentes soportadas:
  osm     -> OpenStreetMap / Overpass API. Gratis, sin API key. Calidad de datos
             despareja segun la zona (mejor en capitales, mas floja en pueblos chicos).
  google  -> Google Places API (New). Necesita la variable de entorno
             GOOGLE_PLACES_API_KEY. Tiene 1000 llamadas gratis por mes (SKU
             Enterprise, que incluye telefono y sitio web); despues cuesta
             aprox. USD 35 cada 1000 llamadas. Ver README.md para como conseguir
             la key.
  both    -> combina y deduplica resultados de las dos fuentes.

Requisitos:
  pip install -r requirements.txt

Ejemplos:
  python leadgen.py --city "Cordoba, Argentina" --category cafeterias --source osm --out leads.xlsx
  GOOGLE_PLACES_API_KEY=xxxx python leadgen.py --city "Cordoba, Argentina" --category cafeterias --source google --limit 60

IMPORTANTE:
  - Este script NO scrapea Google Maps (eso viola sus terminos de servicio).
    Usa la API oficial de Google (si le das una key) y la API publica de
    OpenStreetMap. Ambas son formas legitimas de acceder a estos datos.
  - Nominatim (el geocodificador de OSM) pide no mas de 1 request por segundo
    y un User-Agent identificable. Este script ya respeta eso para uso
    ocasional / manual. Si vas a correrlo en loop para muchas ciudades
    seguidas, agrega un time.sleep(1) entre ciudades.
"""

import argparse
import os
import re
import sys
import time
import unicodedata

import requests
import pandas as pd

# ----------------------------------------------------------------------------
# Mapeo de rubros -> tags de OSM y texto de busqueda para Google
# ----------------------------------------------------------------------------
CATEGORY_MAP = {
    "cafeterias": {
        "label": "Cafeterias y gastronomia",
        "osm_tags": [("amenity", "cafe"), ("amenity", "restaurant"), ("amenity", "fast_food")],
        "google_query": "cafeterias, bares y restaurantes en {city}",
    },
    "comercios_barrio": {
        "label": "Comercios de barrio",
        "osm_tags": [("shop", "hardware"), ("shop", "convenience"), ("shop", "greengrocer"), ("shop", "kiosk")],
        "google_query": "ferreterias, kioscos y almacenes de barrio en {city}",
    },
    "profesionales": {
        "label": "Profesionales y servicios",
        "osm_tags": [("amenity", "dentist"), ("office", "lawyer"), ("office", "accountant"), ("shop", "hairdresser")],
        "google_query": "dentistas, abogados, contadores y peluquerias en {city}",
    },
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
GOOGLE_TEXTSEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

HEADERS_UA = {"User-Agent": "leadgen-freelance-script/1.0 (uso personal, no comercial masivo)"}


def geocode_city(city: str):
    """Devuelve bbox (south, west, north, east) para una ciudad usando Nominatim."""
    params = {"q": city, "format": "json", "limit": 1}
    r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS_UA, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError(f"No se pudo geocodificar la ciudad: {city}")
    bbox = data[0]["boundingbox"]  # [south, north, west, east] como strings
    south, north, west, east = map(float, bbox)
    return south, west, north, east


def fetch_osm(city: str, category_key: str, limit: int):
    cat = CATEGORY_MAP[category_key]
    south, west, north, east = geocode_city(city)
    bbox = f"{south},{west},{north},{east}"

    clauses = []
    for k, v in cat["osm_tags"]:
        clauses.append(f'node["{k}"="{v}"]({bbox});')
        clauses.append(f'way["{k}"="{v}"]({bbox});')
    query = f"""
    [out:json][timeout:60];
    (
      {" ".join(clauses)}
    );
    out center tags;
    """
    r = requests.post(OVERPASS_URL, data={"data": query}, headers=HEADERS_UA, timeout=90)
    r.raise_for_status()
    elements = r.json().get("elements", [])

    rows = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        phone = tags.get("phone") or tags.get("contact:phone")
        website = tags.get("website") or tags.get("contact:website")
        addr = " ".join(filter(None, [tags.get("addr:street"), tags.get("addr:housenumber")]))
        rows.append({
            "Nombre": name,
            "Categoria": tags.get("amenity") or tags.get("shop") or tags.get("office") or category_key,
            "Direccion": addr or tags.get("addr:full", ""),
            "Telefono": phone or "",
            "Sitio web": website or "",
            "Fuente": "OpenStreetMap",
        })
        if len(rows) >= limit:
            break
    return rows


def fetch_google(city: str, category_key: str, limit: int, api_key: str):
    cat = CATEGORY_MAP[category_key]
    query_text = cat["google_query"].format(city=city)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.displayName,places.formattedAddress,"
            "places.internationalPhoneNumber,places.websiteUri,places.types,"
            "nextPageToken"
        ),
    }
    rows = []
    page_token = None
    while len(rows) < limit:
        body = {"textQuery": query_text, "languageCode": "es"}
        if page_token:
            body["pageToken"] = page_token
            time.sleep(2)  # Google pide esperar antes de que el pageToken quede activo
        r = requests.post(GOOGLE_TEXTSEARCH_URL, json=body, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"[google] error {r.status_code}: {r.text}", file=sys.stderr)
            break
        data = r.json()
        for place in data.get("places", []):
            rows.append({
                "Nombre": place.get("displayName", {}).get("text", ""),
                "Categoria": ", ".join(place.get("types", [])[:2]),
                "Direccion": place.get("formattedAddress", ""),
                "Telefono": place.get("internationalPhoneNumber", ""),
                "Sitio web": place.get("websiteUri", ""),
                "Fuente": "Google Places",
            })
            if len(rows) >= limit:
                break
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return rows


def normalize(s: str) -> str:
    s = s.lower().strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return s


def dedupe(rows):
    seen = {}
    out = []
    for row in rows:
        key = normalize(row["Nombre"])
        if key in seen:
            prev = seen[key]
            if not prev["Telefono"] and row["Telefono"]:
                prev["Telefono"] = row["Telefono"]
            if not prev["Sitio web"] and row["Sitio web"]:
                prev["Sitio web"] = row["Sitio web"]
            continue
        seen[key] = row
        out.append(row)
    return out


def main():
    parser = argparse.ArgumentParser(description="Genera una lista de negocios locales para prospeccion.")
    parser.add_argument("--city", required=True, help='Ej: "Cordoba, Argentina"')
    parser.add_argument("--category", required=True, choices=CATEGORY_MAP.keys())
    parser.add_argument("--source", choices=["osm", "google", "both"], default="osm")
    parser.add_argument("--limit", type=int, default=100, help="Maximo de resultados por fuente")
    parser.add_argument("--out", default="leads.xlsx")
    args = parser.parse_args()

    rows = []
    if args.source in ("osm", "both"):
        print(f"Buscando en OpenStreetMap: {args.category} en {args.city}...")
        rows += fetch_osm(args.city, args.category, args.limit)

    if args.source in ("google", "both"):
        api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
        if not api_key:
            print("ERROR: falta la variable de entorno GOOGLE_PLACES_API_KEY.", file=sys.stderr)
            if args.source == "google":
                sys.exit(1)
        else:
            print(f"Buscando en Google Places: {args.category} en {args.city}...")
            rows += fetch_google(args.city, args.category, args.limit, api_key)

    rows = dedupe(rows)

    df = pd.DataFrame(rows, columns=["Nombre", "Categoria", "Direccion", "Telefono", "Sitio web", "Fuente"])
    df["Sin sitio web"] = df["Sitio web"].eq("")
    df["Estado contacto"] = ""
    df["Notas"] = ""

    # Priorizar los que no tienen sitio web: son el mejor lead
    df = df.sort_values(by="Sin sitio web", ascending=False)

    df.to_excel(args.out, index=False)
    print(f"\nListo. {len(df)} negocios guardados en {args.out}")
    print(f"  Sin sitio web: {int(df['Sin sitio web'].sum())}")
    print(f"  Con sitio web: {int((~df['Sin sitio web']).sum())}")


if __name__ == "__main__":
    main()
