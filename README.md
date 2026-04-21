<div align="center">

<img src="https://i.ibb.co/q3RkZTV9/dorky.png" width="120" alt="Dorky mascot"/>

# DORKY

**Google Dorking con interfaz gráfica, paginación automática y exportación de resultados**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)

</div>

---

## ¿Qué es Dorky?

Dorky es una herramienta de escritorio para realizar **Google Dorking** de forma visual e intuitiva. Permite construir consultas avanzadas de Google (dorks), ejecutarlas contra dos APIs de scraping y recopilar los resultados en tiempo real, todo sin tocar el navegador ni la línea de comandos.

Ideal para pentesters, investigadores de seguridad, bug hunters y cualquier persona que necesite buscar información específica en Google de forma sistemática.

---

## Características

- 🎯 **Biblioteca de dorks** organizada por categorías cargada desde `dorks.txt`
- ✏️ **Modo manual** — escribe tus propios dorks directamente en el editor
- 🔧 **Modificadores de un clic** — `site:`, `inurl:`, `intext:`, `filetype:` y más
  - Con dorks de la biblioteca: se aplican/quitan en todas las líneas a la vez
  - En modo manual: se insertan en la posición del cursor para que el usuario complete el valor
- 📄 **Paginación automática** — obtén 10, 20, 30... resultados haciendo múltiples llamadas paginadas (Google devuelve máx. 10 por llamada)
- 🔁 **Deduplicación** — elimina URLs repetidas entre páginas automáticamente
- ⚡ **Resultados en tiempo real** con log coloreado y URLs clicables
- 📋 **Exportación** a `.txt` con timestamp, API utilizada y dork de origen
- 🔑 **Soporte para dos APIs**: [scrape.do](https://scrape.do) y [ScraperAPI](https://www.scraperapi.com)
- 🧹 **Limpieza total** con un clic — resetea dorks, resultados y modificadores
- 🚀 **Instalación automática** de dependencias al primer arranque

---

## Capturas de pantalla

<div align="center">
<img src="https://i.ibb.co/q3RkZTV9/dorky.png" width="80" alt="Dorky"/>

*Interfaz principal de Dorky*
<img width="1908" height="1045" alt="{0FAFF8DC-10C8-479E-9B82-20250981268D}" src="https://github.com/user-attachments/assets/082e9ac4-eff2-43a5-8ca0-633d2abf8da1" />
<img width="503" height="382" alt="{3E79A735-3DE9-4899-8717-1A7A801E25C0}" src="https://github.com/user-attachments/assets/e1b3eadd-aac1-4bc7-b510-b681371dc781" /> 

</div>

---

## Requisitos

- Python **3.10 o superior**
- Conexión a internet
- Una API key de [scrape.do](https://scrape.do) y/o [ScraperAPI](https://www.scraperapi.com) (ambas tienen plan gratuito)

Las dependencias Python se instalan automáticamente al arrancar:

```
customtkinter
requests
Pillow
```

---

## Instalación y uso

```bash
# 1. Clona el repositorio
git clone https://github.com/aisurf3r/Dorky.git
cd Dorky

# 2. Ejecuta el script (las dependencias se instalan solas)
python dorky.py
```

> En el primer arranque aparecerá una barra de progreso mientras se instalan las dependencias. A partir del segundo arranque es instantáneo.

---

## Configuración de APIs

Haz clic en el botón **🔑 APIs** (esquina superior derecha) e introduce tus claves:

| API | Dónde conseguirla | Plan gratuito |
|-----|------------------|---------------|
| scrape.do | [scrape.do/register](https://scrape.do) | ✅ Sí |
| ScraperAPI | [scraperapi.com/signup](https://www.scraperapi.com) | ✅ Sí |

Las claves se guardan en memoria durante la sesión. No se almacenan en disco.

---

## Estructura del archivo `dorks.txt`

Dorky carga los dorks desde un fichero `dorks.txt` en el mismo directorio. El formato es:

```
# === Nombre de categoría ===
dork uno
dork dos
dork tres

# === Otra categoría ===
otro dork
```

Puedes editar este archivo para añadir tus propias categorías y dorks. El script lo recarga automáticamente en cada arranque.

---

## Workflow típico

### Con la biblioteca de dorks

1. Selecciona una **categoría** en el desplegable superior
2. Haz clic en los dorks del panel izquierdo para agregarlos al editor
3. (Opcional) Activa modificadores como `site:` para filtrar por dominio — se aplican a todos los dorks a la vez
4. Elige el **número de resultados** (10–30) y pulsa **Buscar con scrape.do** o **Buscar con ScraperAPI**
5. Los resultados aparecen en tiempo real. Haz clic en cualquier URL para abrirla en el navegador
6. Pulsa **📋 Exportar URLs** para guardar los resultados en un `.txt`

### Modo manual

1. Escribe directamente en el editor de dorks
2. Usa los checkboxes de modificadores para insertar `site:`, `inurl:`, etc. en la posición del cursor
3. Completa el valor del modificador (ej: `site:ES`, `inurl:admin`, `filetype:pdf`)
4. Combina varios modificadores en la misma línea
5. Lanza la búsqueda normalmente

---

## Paginación

Dorky divide automáticamente la búsqueda en páginas de 10 resultados:

- **scrape.do** — usa el parámetro `start=0, 10, 20...`
- **ScraperAPI** — usa el parámetro `page=1, 2, 3...`

Si seleccionas 20 resultados, se harán 2 llamadas. Si seleccionas 30, se harán 3. El log muestra el progreso por página. Si Google no tiene suficientes resultados para alguna página, la búsqueda se detiene anticipadamente sin hacer llamadas vacías.

---

## Aviso legal

Esta herramienta está pensada para uso en **entornos autorizados** — auditorías de seguridad, investigación, bug bounty y aprendizaje. El uso de Google Dorking contra sistemas sin permiso explícito puede vulnerar los términos de servicio de Google y la legislación vigente.

**Úsala de forma responsable y ética.**

---

## Contribuir

Los PRs son bienvenidos. Si encuentras un bug o tienes una idea, abre un issue.

---

<div align="center">
Hecho con 🖤 por <a href="https://github.com/aisurf3r">aisurf3r</a>
</div>
