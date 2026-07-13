# Herramienta MCDM ferroviaria TOPSIS bicapa — norte de México

Material de apoyo a *Marco TOPSIS Bicapa para Despacho Ferroviario Multicriterio en el Corredor Norte de México* y a *A Two-Layer TOPSIS Framework for Multicriteria Rail Freight Dispatch in Northern Mexico* (versión `v1.0-paper`, ver `VERSION`).

Aquí publicamos la herramienta web autónoma en español e inglés, los JSON de la red ferroviaria y las estrategias de carga, las salidas del corredor norte (rankings, sensibilidad ±20 %, estabilidad k = 5) y el ANOVA factorial 3³ con su extensión mixta 9×3. Los scripts `run_topsis_analysis.py` y `run_factorial_experiment.py` regeneran esos resultados a partir del mismo núcleo de 587 estrategias que usa el artículo; el archivo `dataset.json` amplía la exploración interactiva a 4235 registros. El manuscrito Springer y las figuras PNG incrustadas en el proceedings no se distribuyen aquí.

Para usar la herramienta, abra `TOPSIS-Bicapa-Ferroviario-MCDM.html` o `TOPSIS-Bicapa-Rail-MCDM.html` en Chrome, Edge o Firefox (modo Guía rápida / Quick guide o Análisis completo / Full analysis). No hace falta servidor backend; los mapas base de OpenStreetMap sí requieren conexión a internet.

Para repetir los análisis numéricos del paper:

```bash
pip install -r requirements.txt
python scripts/run_topsis_analysis.py
python scripts/run_factorial_experiment.py
```

El diseño factorial está descrito en `docs/diseno_experimental_3k.md`. Los JSON principales son `data/cities.json`, `data/wagon_map.json`, `data/dataset.json`, `data/paper_results.json` y `data/factorial_experiment.json`.

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
