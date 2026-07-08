# Norte de México — Simulador TOPSIS de carga ferroviaria

Repositorio de apoyo al paper *Optimización multicriterio de trayecto y estrategias de carga en transporte ferroviario mediante un marco TOPSIS bicapa*.

Contiene el simulador interactivo **del norte de México**, los datasets del experimento y los scripts que reproducen los resultados numéricos del artículo (rankings, sensibilidad, validación cruzada y ANOVA factorial 3³).

## Contenido

| Componente | Descripción |
|------------|-------------|
| `SIMULADOR_TOPSIS.html` | Simulador standalone (TOPSIS bicapa, Dijkstra, MOORA, validación) |
| `data/dataset.json` | 4235 estrategias (587 núcleo del paper + extensiones regionales) |
| `data/cities.json` | Red ferroviaria de 25 estaciones |
| `data/paper_results.json` | Resultados del corredor norte y Monterrey–Laredo |
| `data/factorial_experiment.*` | Corridas y tablas ANOVA del diseño 3³ |
| `scripts/run_topsis_analysis.py` | Reproduce `paper_results.json` |
| `scripts/run_factorial_experiment.py` | Reproduce el experimento factorial 3³ |
| `docs/diseno_experimental_3k.md` | Diseño experimental documentado |

## Uso rápido del simulador

1. Clonar o descargar este repositorio.
2. Abrir **`SIMULADOR_TOPSIS.html`** en Chrome, Edge o Firefox.
3. Leaflet carga localmente; los mapas base (OpenStreetMap) requieren internet.

Modos disponibles: **Guía rápida** (despacho operativo) y **Análisis completo** (pesos, rankings, validación).

## Reproducibilidad de resultados del paper

### Requisitos

```bash
pip install -r requirements.txt
```

Python 3.9 o superior.

### Comandos

```bash
# Rankings del corredor norte, sensibilidad y validación cruzada
python scripts/run_topsis_analysis.py

# Diseño factorial 3³ sobre la capa de carga (Monterrey–Laredo)
python scripts/run_factorial_experiment.py

# Figuras PNG para el paper (opcional; crea assets/figs/)
python scripts/generate_paper_figures.py
```

Los scripts escriben en `data/paper_results.json` y `data/factorial_experiment.json`. El experimento del paper usa el **subconjunto núcleo de 587 estrategias** dentro del dataset; el simulador embebe el bundle completo (4235) para exploración interactiva.

Ver **`REPRODUCIBILITY.md`** para el mapeo sección-del-paper → artefacto.

## Estructura

```
.
├── SIMULADOR_TOPSIS.html
├── assets/
│   ├── vendor/leaflet/
│   ├── wagon_catalog.json
│   └── wagon_sprites.json
├── data/
├── docs/
├── scripts/
├── README.md
├── REPRODUCIBILITY.md
├── requirements.txt
├── CITATION.cff
└── LICENSE
```

## Cómo citar

```bibtex
@software{ruta_norte_2026,
  author  = {Colchero Garc{'i}a, Abraham Isaac and Ochoa, Alberto},
  title   = {{Norte de M{\'e}xico}: Multicriteria Railway Load and Route Simulator},
  year    = {2026},
  version = {v1.0-paper},
  url     = {https://github.com/Selenofilia/OptimizaciOn-Multicriterio-de-Trayecto-y-Estrategias-de-Carga-en-Transporte-Ferroviario-}
}
```

Sustituir la URL cuando publique el repositorio o el DOI de Zenodo.

## Licencia

MIT — ver `LICENSE`.

## Autores

- Abraham Isaac Colchero García — Universidad Autónoma de Guerrero
- Alberto Ochoa — Universidad Autónoma de Ciudad Juárez
