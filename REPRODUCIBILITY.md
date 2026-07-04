# Reproducibilidad

Este documento vincula las secciones del paper con los artefactos de este repositorio.

## Principio

- **Simulador (`SIMULADOR_TOPSIS.html`)**: implementación interactiva del marco TOPSIS bicapa.
- **Scripts Python**: fuente reproducible de tablas y ANOVA reportados en el paper.
- **Dataset núcleo (587)**: subconjunto analítico del paper; el simulador incluye 4235 registros para demo ampliada.

## Mapeo paper → artefacto

| Sección del paper | Artefacto | Comando |
|-------------------|-----------|---------|
| Rankings por par O-D (corredor norte) | `data/paper_results.json` | `python scripts/run_topsis_analysis.py` |
| Sensibilidad ±20 %, CV k=5 (Monterrey–Laredo) | `data/paper_results.json` | idem |
| ANOVA factorial 3³ | `data/factorial_experiment.json` | `python scripts/run_factorial_experiment.py` |
| Corridas crudas factorial | `data/factorial_experiment.csv` | idem |
| Diseño experimental | `docs/diseno_experimental_3k.md` | — |
| Red ferroviaria | `data/cities.json` | — |
| Estrategias de carga | `data/dataset.json` | — |

## Notas metodológicas

1. **`run_topsis_analysis.py`** replica el pipeline de decisión del simulador (pre-filtro + capa de carga + capa de ruteo) sin interfaz gráfica.
2. **`run_factorial_experiment.py`** ejecuta 27 tratamientos × 5 réplicas (135 corridas) sobre Monterrey–Laredo; la variación experimental proviene del submuestreo aleatorio con semilla del 80 % de estrategias factibles.
3. Regenerar figuras requiere `matplotlib` y crea `assets/figs/` (no incluido en el release mínimo; se genera al ejecutar el script).

## Verificación rápida

Tras clonar el repo:

```bash
pip install -r requirements.txt
python scripts/run_topsis_analysis.py
python scripts/run_factorial_experiment.py
```

Compare `data/paper_results.json` y `data/factorial_experiment.json` con los valores reportados en el paper (Ci por par, estabilidad de sensibilidad, R² ajustado del ANOVA).
