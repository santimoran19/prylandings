# Portfolio de landings — cómo usarlo

Tres sitios demo completos (uno por rubro) más una página índice que los agrupa.
Todo funciona abriendo los archivos directamente en el navegador, sin instalar nada.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | Tu página de portfolio. Es la que le mandás al cliente. |
| `cafeteria.html` | Demo "Café Aurora" — cafetería de especialidad |
| `restaurante.html` | Demo "Terrazza" — restaurante de autor |
| `comida-rapida.html` | Demo "Bravo Burger" — hamburguesería con carrito de pedidos |

Para verlos ahora: hacé doble clic en `index.html`.

## Qué tiene cada uno

**Cafetería** — menú navegable por pestañas (café / brunch / pastelería / fríos),
sección de historia, galería, reseñas, horarios con el día actual destacado, mapa
ilustrado y botón flotante de WhatsApp.

**Restaurante** — estética oscura y sobria, carta completa por secciones incluida
carta de vinos, menú degustación destacado, sección del chef, galería del salón y
**formulario de reservas funcional** (valida campos y no deja elegir fechas pasadas).

**Comida rápida** — el más completo técnicamente: **carrito de pedidos real**. El
cliente filtra por categoría, agrega productos, ajusta cantidades, el envío se
calcula solo (gratis desde cierto monto) y al confirmar **se abre WhatsApp con el
pedido ya escrito**. Ese detalle es el que más impresiona en una demo.

## Antes de mandarlo a un cliente

1. **El número de WhatsApp del carrito.** En `comida-rapida.html`, buscá la línea
   `const TELEFONO_WSP = '5493514220268';` y poné el número real (formato
   internacional, sin `+` ni espacios).
2. **Tus datos en el portfolio.** En `index.html`, sección de contacto, están como
   `+54 351 000-0000` y `tumail@ejemplo.com`. Cambialos por los tuyos.
3. **Los precios de los planes** dicen "Consultar" a propósito. Poné números
   concretos cuando decidas tu lista de precios: un precio visible filtra a los
   curiosos y acelera el cierre.

## Sobre las imágenes

Todas las ilustraciones son SVG dibujados dentro del propio archivo. Eso tiene una
ventaja concreta: **no dependen de ningún servicio externo, cargan instantáneo y no
hay problemas de derechos de autor**. Para un cliente real, se reemplazan por fotos
del local — que además convierten mejor que cualquier ilustración.

Las tipografías sí se cargan de Google Fonts, así que la primera carga necesita
internet. Si querés que funcionen 100% offline, se pueden descargar y embeber.

## Publicarlas online (para tener un link que mandar)

Un archivo local no sirve para mandar por WhatsApp. Necesitás un link. Las tres
opciones gratis más simples:

**Netlify Drop** — la más rápida. Entrás a `app.netlify.com/drop`, arrastrás la
carpeta `landings` completa y en 30 segundos tenés un link público. Sin cuenta,
sin configurar nada.

**GitHub Pages** — si ya usás Git. Subís la carpeta a un repo, activás Pages en
Settings y te queda en `tuusuario.github.io/repo`.

**Vercel** — similar a Netlify, con dominio propio gratis del tipo
`tuproyecto.vercel.app`.

Con cualquiera de las tres, el link del portfolio queda listo para pegar en los
mensajes de WhatsApp que ya tenés armados en `mensajes_whatsapp.txt`.

## Un consejo honesto sobre cómo usarlas

Mandar el link genérico del portfolio funciona, pero funciona **mucho mejor**
personalizar. Si vas a contactar a una cafetería concreta, tomate 10 minutos:
duplicá `cafeteria.html`, cambiale el nombre, los platos y el teléfono por los de
ese negocio, subilo y mandale el link diciendo "te armé una vista de cómo quedaría
la tuya". La tasa de respuesta a eso es muchísimo más alta que a un portfolio
genérico, porque ya no le estás pidiendo que imagine nada.
