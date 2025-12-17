# DocuDash CLI - Scraping Tool

## Descripción

Herramienta CLI para hacer scraping de nombres de aplicaciones desde el sistema de disponibilidad y mapearlos con las aplicaciones en la base de datos.

## Instalación

Las dependencias ya están en `requirements.txt`. Si necesitas instalarlas:

```bash
pip install -r requirements.txt
```

## Migración de Base de Datos

Antes de usar el scraping, ejecuta la migración para agregar las columnas `asset_id` y `bapp_id`:

```bash
python migrate_add_asset_bapp_ids.py
```

## Uso

### Comando Principal

```bash
python cli.py scrape-apps-names --headed true --timeout 60 --delay 0.5
```

### Opciones

- `--headed`: Ejecuta el navegador en modo visible (por defecto: `true`)
- `--headless`: Ejecuta el navegador en modo headless (sin ventana)
- `--timeout`: Timeout del navegador en segundos (por defecto: `60`)
- `--delay`: Delay entre requests en segundos (por defecto: `0.5`)

### Ejemplo con Headless

```bash
python cli.py scrape-apps-names --headless --timeout 60 --delay 0.5
```

## Proceso

1. **Inicialización**: El script abre un navegador Chrome
2. **Login Manual**: Se pausa para que hagas login con Google manualmente
3. **Scraping**: Para cada aplicación sin `bapp_id`:
   - Navega a `https://pruebasdisponibilidad.cloud.osde.ar/`
   - Busca el nombre de la aplicación en los elementos `<h2>`
   - Extrae el `app_id` del href del enlace padre
   - Actualiza la base de datos si encuentra el ID
4. **Resultados**: Guarda los resultados en `output/mapping_apps.json`

## Output

El archivo `output/mapping_apps.json` contiene:

```json
[
  {
    "app_name": "ConsultorioDigitalv2",
    "asset_id": 64468,
    "bapp_id": 520
  },
  {
    "app_name": "Credencial Digital OSDE",
    "asset_id": 64469,
    "bapp_id": 521
  }
]
```

## Notas

- Solo procesa aplicaciones que no tienen `bapp_id` (null)
- Si no encuentra un `app_id`, deja el campo como `null` en la base de datos
- La sesión del navegador se mantiene durante todo el proceso
- Los errores se imprimen en consola pero el proceso continúa

## Troubleshooting

### Error: "ChromeDriver not found"
- El WebDriver Manager debería descargarlo automáticamente
- Asegúrate de tener conexión a internet

### Error: "Timeout loading page"
- Aumenta el `--timeout` a un valor mayor (ej: `120`)

### No encuentra las aplicaciones
- Verifica que el selector CSS sea correcto para la estructura HTML actual
- Revisa que el nombre de la aplicación en la BD coincida exactamente con el del sitio

