# leadgen.py — buscador de leads locales

Script en Python que genera una planilla de negocios (nombre, dirección, teléfono,
sitio web) para prospección de clientes freelance. Usa fuentes de datos legítimas,
no scrapea Google Maps directamente.

## Por qué así

Scrapear Google Maps con bots viola sus términos de servicio y puede terminar en
bloqueo de IP. Este script usa dos caminos legales:

- **OpenStreetMap** (Overpass API): gratis, sin cuenta ni API key. Datos de
  teléfono/web incompletos en algunas zonas, pero suficiente para arrancar.
- **Google Places API (New)**: datos más completos (requiere API key propia y
  cuenta de Google Cloud con tarjeta cargada, aunque tiene cuota gratis mensual —
  ver más abajo).

## Instalación

```bash
pip install -r requirements.txt
```

Requiere Python 3.9+.

## Uso básico (sin costo, sin API key)

```bash
python leadgen.py --city "Córdoba, Argentina" --category cafeterias --source osm --out leads_cordoba.xlsx
```

Categorías disponibles: `cafeterias`, `comercios_barrio`, `profesionales`
(están definidas en `CATEGORY_MAP` dentro de `leadgen.py` — se pueden agregar más
rubros ahí mismo).

El resultado es un `.xlsx` con columnas: Nombre, Categoría, Dirección, Teléfono,
Sitio web, Fuente, **Sin sitio web** (los `True` son tu prioridad de contacto),
Estado contacto y Notas (para ir marcando a mano a quién contactaste).

## Usar también Google Places (opcional, mejor calidad de datos)

1. Andá a [console.cloud.google.com](https://console.cloud.google.com/), creá un
   proyecto.
2. Activá la API **"Places API (New)"** (no la legacy).
3. Generá una API key en "Credenciales" y restringila a esa API únicamente.
4. Cargá una tarjeta (Google la pide para habilitar el proyecto, pero no te cobra
   si te mantenés dentro de la cuota gratis).

```bash
export GOOGLE_PLACES_API_KEY="tu_key_aca"
python leadgen.py --city "Córdoba, Argentina" --category cafeterias --source both --limit 60 --out leads_cordoba.xlsx
```

Con `--source both` combina OSM + Google y deduplica por nombre, completando
teléfono/web faltante de una fuente con el dato de la otra.

## Costos de Google Places API (2026)

Desde marzo 2025 Google eliminó el crédito universal de USD 200/mes y lo
reemplazó por cuotas gratis por producto. Para el tipo de consulta que usa este
script (Text Search con teléfono y sitio web incluidos, SKU "Enterprise"), la
cuota gratis es de **1.000 llamadas por mes**; por encima de eso cuesta
aproximadamente **USD 35 cada 1.000 llamadas**. Cada ciudad+rubro que busques
consume varias llamadas (una por página de ~20 resultados), así que con la cuota
gratis alcanza para probar bastantes ciudades antes de gastar un centavo. Precios
sujetos a cambio — confirmá en la [página oficial de precios](https://developers.google.com/maps/billing-and-pricing/pricing).

## Límites a tener en cuenta

- Nominatim (el geocodificador que ubica la ciudad) pide no más de 1 request
  por segundo. El script hace un solo geocodeo por corrida, así que no hay problema
  en uso normal.
- Overpass API es un servicio comunitario gratuito: no lo satures corriendo el
  script en loop muy seguido para muchas ciudades. Si vas a automatizar corridas
  masivas, conviene levantar tu propia instancia de Overpass o pasarte a Google
  Places para volumen alto.

## Próximos pasos sugeridos

Este script resuelve la parte de "encontrar negocios". Lo que define si esto se
convierte en ventas es el mensaje de contacto y el seguimiento. Puedo armar
después:

1. Plantillas de mensaje de WhatsApp/mail por rubro (con variantes A/B).
2. Una planilla de seguimiento (CRM simple) con estados: contactado, respondió,
   reunión agendada, cerrado, descartado.
3. Un portfolio/landing propia para linkear en los mensajes (mostrar ejemplos
   de trabajo genera mucha más conversión que un mensaje sin nada que mostrar).

Avisame y seguimos con eso.
