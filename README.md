# Materiales de apoyo al paper — TOPSIS bicapa (norte de México)

Repositorio con los **documentos y datos estrictamente necesarios** para comprender el artículo:

*Optimización Multicriterio de Trayecto y Estrategias de Carga en Transporte Ferroviario Mediante un Marco TOPSIS Bicapa*.

## Contenido

| Archivo | Rol en la comprensión del paper |
|---------|----------------------------------|
| `paper.tex` | Texto completo del artículo (LNCS) |
| `docs/diseno_experimental_3k.md` | Diseño factorial 3³, factores, hipótesis y ANOVA |
| `data/cities.json` | Red ferroviaria de 25 estaciones (Fig. 2, metodología) |
| `data/paper_results.json` | Rankings del corredor norte, sensibilidad ±20 % y validación cruzada k = 5 |
| `data/factorial_experiment.json` | Tablas ANOVA factorial 3³ y factorial mixto 9×3 |
| `data/factorial_experiment.csv` | 135 corridas del experimento factorial (Monterrey–Laredo) |

## Mapeo sección del paper → artefacto

| Sección del paper | Artefacto |
|-------------------|-----------|
| Red modelada y pares O-D | `data/cities.json` |
| Tabla 3 y Fig. 3 (rankings por par) | `data/paper_results.json` |
| Sensibilidad y validación cruzada (Monterrey–Laredo) | `data/paper_results.json` |
| Tabla 4 y Fig. 4 (ANOVA factorial 3³) | `data/factorial_experiment.json` |
| Factorial mixto O-D × rentabilidad | `data/factorial_experiment.json` |
| Diseño experimental detallado | `docs/diseno_experimental_3k.md` |

## Alcance de este repositorio

Este release **no** incluye el simulador interactivo, scripts de reproducción ni el dataset completo de 4235 estrategias. Solo conserva lo indispensable para **leer, interpretar y contrastar** los resultados reportados en el artículo.

## Autores

- Abraham Isaac Colchero García — Universidad Autónoma de Guerrero
- José Guadalupe De la Torre Suárez — Universidad Autónoma de Guerrero
- Alberto Ochoa Zezzatti — Universidad Autónoma de Ciudad Juárez

## Licencia

MIT — ver `LICENSE`.
