# Simulador TOPSIS bicapa para carga ferroviaria en el norte de México

Repositorio de apoyo al artículo *Optimización Multicriterio de Trayecto y Estrategias de Carga en Transporte Ferroviario Mediante un Marco TOPSIS Bicapa*.

El artefacto principal es **`SIMULADOR_TOPSIS.html`**: una aplicación web autónoma que implementa el marco TOPSIS bicapa (capa de ruteo con Dijkstra y capa de carga sobre formaciones de 1 a 6 vagones) sobre una red ferroviaria de 25 estaciones en Chihuahua, Sonora, Coahuila y Nuevo León, con conexión a Laredo.

## Artefacto principal

| Componente | Descripción |
|------------|-------------|
| `SIMULADOR_TOPSIS.html` | Simulador interactivo del marco TOPSIS bicapa: selección origen–destino, ranking de trayectos, pre-filtro interno, ranking de formaciones, validación MOORA, sensibilidad de pesos y despacho animado |
| `assets/` | Recursos gráficos del simulador (Leaflet, catálogo y sprites de material rodante) |
| `data/cities.json` | Topología de la red ferroviaria modelada |
| `data/dataset.json` | Estrategias de carga embebidas en el simulador (4235 registros; 587 núcleo del artículo) |

### Uso del simulador

1. Clonar o descargar este repositorio.
2. Abrir **`SIMULADOR_TOPSIS.html`** en Chrome, Edge o Firefox.
3. Seleccionar modo **Guía rápida** (flujo operativo) o **Análisis completo** (controles metodológicos y validación).

El simulador opera sin servidor backend. Los mapas base (OpenStreetMap) requieren conexión a internet.

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
| Red modelada (Fig. 2) | `data/cities.json` |
| Rankings por par O-D (Tabla 3, Fig. 3) | `data/paper_results.json` |
| Sensibilidad y validación cruzada | `data/paper_results.json` |
| ANOVA factorial 3³ (Tabla 4, Fig. 4) | `data/factorial_experiment.json` |
| Diseño experimental | `docs/diseno_experimental_3k.md` |

## Cómo citar

```bibtex
@software{norte_mexico_topsis_2026,
  author  = {Colchero Garc{\'i}a, Abraham Isaac and De la Torre Su{\'a}rez, Jos{\'e} Guadalupe and Ochoa Zezzatti, Alberto},
  title   = {{Simulador TOPSIS bicapa para carga ferroviaria en el norte de M{\'e}xico}},
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
