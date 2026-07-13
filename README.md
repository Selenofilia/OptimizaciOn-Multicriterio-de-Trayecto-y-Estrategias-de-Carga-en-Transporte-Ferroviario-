# Herramienta MCDM ferroviaria TOPSIS bicapa — norte de México

Repositorio de apoyo reproducible a los artículos:

- *Marco TOPSIS Bicapa para Despacho Ferroviario Multicriterio en el Corredor Norte de México* (español)
- *A Two-Layer TOPSIS Framework for Multicriteria Rail Freight Dispatch in Northern Mexico* (inglés)

**Versión:** `v1.0-paper` (ver `VERSION`).

Este repositorio incluye **solo** lo necesario para replicar la herramienta interactiva y los **resultados numéricos** citados en el paper. **No** contiene el manuscrito Springer (Word/LaTeX), figuras PNG embebidas en el artículo ni scripts de maquetación editorial.

## Contenido incluido

| Ruta | Descripción |
|------|-------------|
| `TOPSIS-Bicapa-Ferroviario-MCDM.html` | Herramienta MCDM autónoma (español) |
| `TOPSIS-Bicapa-Rail-MCDM.html` | Misma herramienta (inglés) |
| `data/cities.json` | Red ferroviaria modelada (25 estaciones) |
| `data/wagon_map.json` | Slots visuales de material rodante |
| `data/dataset.json` | 4235 estrategias (587 núcleo analítico del artículo) |
| `data/paper_results.json` | Rankings del corredor, sensibilidad ±20 %, estabilidad k = 5 |
| `data/factorial_experiment.json` | ANOVA 3³ y factorial mixto 9×3 |
| `data/factorial_experiment.csv` | 135 corridas del diseño factorial |
| `scripts/run_topsis_analysis.py` | Regenera `paper_results.json` |
| `scripts/run_factorial_experiment.py` | Regenera salidas factorial |
| `docs/diseno_experimental_3k.md` | Protocolo factorial 3^k |
| `assets/vendor/leaflet/` | Mapa interactivo offline |
| `assets/wagon_catalog.json`, `assets/wagon_sprites.json` | Catálogo gráfico de vagones |

## Uso de la herramienta MCDM

1. Clonar o descargar este repositorio.
2. Abrir **`TOPSIS-Bicapa-Ferroviario-MCDM.html`** o **`TOPSIS-Bicapa-Rail-MCDM.html`** en Chrome, Edge o Firefox.
3. Elegir **Guía rápida** / **Quick guide** o **Análisis completo** / **Full analysis**.

La herramienta no requiere servidor backend. Los tiles de OpenStreetMap sí requieren internet.

## Reproducibilidad numérica

```bash
pip install -r requirements.txt
python scripts/run_topsis_analysis.py
python scripts/run_factorial_experiment.py
```

| Resultado en el artículo | Artefacto en este repo |
|---------------------------|-------------------------|
| Red y restricciones (Sección 2) | `data/cities.json`, HTML MCDM |
| Tabla 4 / Fig. 2 (rankings corredor) | `data/paper_results.json` |
| Tabla 5 (Top-5 Monterrey–Laredo) | HTML MCDM + `data/paper_results.json` |
| Sensibilidad ±20 %, k = 5 | `data/paper_results.json` |
| Tabla 6 / Fig. 4 (ANOVA 3³) | `data/factorial_experiment.json` |
| Protocolo factorial | `docs/diseno_experimental_3k.md` |

## Qué no incluye este repositorio

- Manuscrito `.docx` / fuentes LaTeX del proceedings Springer
- Figuras estáticas (PNG) incrustadas en el paper
- Scripts de generación Word/LaTeX, capturas de pantalla o verificación editorial
- Excel comercial fuente (`dataset_exact_materials.xlsx`)

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

- Abraham Isaac Colchero García — Facultad de Matemáticas Nodo Acapulco, UAGRO
- José Guadalupe De la Torre Suárez — Facultad de Matemáticas Nodo Acapulco, UAGRO
- Alberto Ochoa Zezzatti — Universidad Autónoma de Ciudad Juárez

## Licencia

MIT — ver `LICENSE`.
