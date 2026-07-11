# Herramienta MCDM ferroviaria TOPSIS bicapa — norte de México

Repositorio de apoyo al artículo *Marco TOPSIS Bicapa para Despacho Ferroviario Multicriterio en el Corredor Norte de México*.

El artefacto principal es **`TOPSIS-Bicapa-Ferroviario-MCDM.html`** (español) o **`TOPSIS-Bicapa-Rail-MCDM.html`** (inglés): una aplicación web autónoma que implementa el marco TOPSIS bicapa (capa de ruteo con Dijkstra y capa de carga sobre formaciones de 1 a 6 vagones) sobre una red ferroviaria de 25 estaciones en Chihuahua, Sonora, Coahuila y Nuevo León, con conexión a Laredo.

## Artefacto principal

| Componente | Descripción |
|------------|-------------|
| `TOPSIS-Bicapa-Ferroviario-MCDM.html` | Herramienta MCDM interactiva (español): selección origen–destino, ranking de trayectos, pre-filtro interno, ranking de formaciones, validación MOORA, sensibilidad de pesos y despacho animado |
| `TOPSIS-Bicapa-Rail-MCDM.html` | Misma herramienta en inglés (*Two-Layer TOPSIS Rail MCDM Tool — Northern Mexico freight corridor*) |
| `assets/` | Recursos gráficos (Leaflet, catálogo y sprites de material rodante) |
| `data/cities.json` | Topología de la red ferroviaria modelada |
| `data/dataset.json` | Estrategias de carga embebidas (4235 registros; 587 núcleo del artículo) |

### Uso

1. Clonar o descargar este repositorio.
2. Abrir **`TOPSIS-Bicapa-Ferroviario-MCDM.html`** (español) o **`TOPSIS-Bicapa-Rail-MCDM.html`** (inglés) en Chrome, Edge o Firefox.
3. Seleccionar modo **Guía rápida** / **Quick guide** (flujo operativo) o **Análisis completo** / **Full analysis** (controles metodológicos y validación).

La herramienta opera sin servidor backend. Los mapas base (OpenStreetMap) requieren conexión a internet.

## Materiales de apoyo al artículo

| Archivo | Función |
|---------|---------|
| `docs/diseno_experimental_3k.md` | Diseño factorial 3³ sobre la capa de carga |
| `data/paper_results.json` | Rankings del corredor norte, sensibilidad ±20 % y validación cruzada k = 5 |
| `data/factorial_experiment.json` | Tablas ANOVA factorial 3³ y factorial mixto 9×3 |
| `data/factorial_experiment.csv` | Corridas del experimento factorial (135 observaciones) |

## Reproducibilidad de resultados

Los scripts en `scripts/` replican los análisis numéricos reportados en el artículo:

```bash
pip install -r requirements.txt
python scripts/run_topsis_analysis.py
python scripts/run_factorial_experiment.py
```

| Sección del artículo | Artefacto |
|----------------------|-----------|
| Red modelada (Sección 2; `data/cities.json`) | `data/cities.json` |
| Rankings por par O-D (Tabla 4, Fig. 2) | `data/paper_results.json` |
| Sensibilidad y validación cruzada (Tablas 5–6) | `data/paper_results.json` |
| ANOVA factorial 3³ (Tabla 6, Figs. 3–4) | `data/factorial_experiment.json` |
| Diseño experimental | `docs/diseno_experimental_3k.md` |

## Cómo citar

```bibtex
@software{norte_mexico_topsis_2026,
  author  = {Colchero Garc{\'i}a, Abraham Isaac and De la Torre Su{\'a}rez, Jos{\'e} Guadalupe and Ochoa Zezzatti, Alberto},
  title   = {{Herramienta MCDM ferroviaria TOPSIS bicapa para el corredor del norte de M{\'e}xico}},
  year    = {2026},
  version = {v1.0-paper},
  url     = {https://github.com/Selenofilia/OptimizaciOn-Multicriterio-de-Trayecto-y-Estrategias-de-Carga-en-Transporte-Ferroviario-}
}
```

## Autores

- Abraham Isaac Colchero García — Universidad Autónoma de Guerrero
- José Guadalupe De la Torre Suárez — Universidad Autónoma de Guerrero
- Alberto Ochoa Zezzatti — Universidad Autónoma de Ciudad Juárez

## Licencia

MIT — ver `LICENSE`.
