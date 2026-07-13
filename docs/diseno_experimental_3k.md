# Diseño experimental factorial 3^k para la validación de TOPSIS-carga

> Notas de trabajo vinculadas al paper *Marco TOPSIS Bicapa para Despacho Ferroviario Multicriterio en el Corredor Norte de México* / *A Two-Layer TOPSIS Framework for Multicriteria Rail Freight Dispatch in Northern Mexico*. Documenta el diseño factorial **3^k** y la extensión mixta 9×3 sobre la capa de carga. Los números se regeneran con `scripts/run_factorial_experiment.py` y quedan en `data/factorial_experiment.json`.

---

## 1. Justificación metodológica

En el estudio ya se reportaban sensibilidad ±20 % en los pesos y una prueba de estabilidad por partición (k = 5; leave-subset-out, no validación cruzada predictiva). El factorial 3^k cuantifica con ANOVA cómo los pesos de rentabilidad/carga (A), eficiencia operativa (B) y riesgo/penalizaciones (C) desplazan el C_i del líder en Monterrey–Laredo.

A diferencia de un 2^k, tres niveles por factor permiten estimar curvatura además de efectos lineales e interacciones, lo cual conviene cuando los pesos actúan como multiplicadores ordinales sobre grupos de criterios.

## 2. Tipo y diseño de investigación

Se adopta un **diseño factorial 3^3 completo, de efectos fijos y con réplicas**, aplicado sobre la **capa de carga** del marco TOPSIS bicapa. La variable de respuesta es el **coeficiente de cercanía relativa C_i de la formación líder** (la recomendación final del simulador). El par origen-destino de referencia es **Monterrey–Laredo**, el corredor detallado en el paper.

### 2.1 Factores y niveles

Cada factor agrupa un subconjunto de los diez criterios de la capa de carga y actúa como **multiplicador del peso base del grupo**; los diez pesos se renormalizan a \sum w_j = 1 dentro del método. Como los factores son entradas independientes (los sliders crudos) y la renormalización es una transformación determinista posterior, el diseño 3^3 conserva su ortogonalidad. Se descarta con ello un diseño de mezclas, que aplicaría solo si los factores fueran proporciones que suman uno.


| Factor | Grupo de criterios    | Criterios de la capa de carga                                                             | Nivel bajo (−1) | Nivel medio (0) | Nivel alto (+1) |
| ------ | --------------------- | ----------------------------------------------------------------------------------------- | --------------- | --------------- | --------------- |
| **A**  | Rentabilidad/carga    | `total_profit_usd`, `total_cargo_tons`                                                    | ×0.5            | ×1.0            | ×2.0            |
| **B**  | Eficiencia operativa  | `avg_utilization_pct`, `avg_maintenance_score`, `total_op_time_hr`, `total_fuel_cost_usd` | ×0.5            | ×1.0            | ×2.0            |
| **C**  | Riesgo/penalizaciones | `max_weather_risk`, `hazardous_units`, `hm_separation_penalty`, `type_mix_penalty`        | ×0.5            | ×1.0            | ×2.0            |


La codificación −1/0/+1 representa los niveles bajo, medio y alto. El diseño consta de 3^3 = 27 tratamientos.

### 2.2 Réplicas y error experimental

TOPSIS es determinista: con los mismos pesos y el mismo conjunto de alternativas produce siempre el mismo C_i. Para generar la variación que sustenta el error experimental y disponer de grados de libertad para el error, cada corrida toma un **submuestreo aleatorio con semilla del 80 %** de las estrategias factibles del par O-D antes de generar las formaciones candidatas. Con **n = 5 réplicas** por tratamiento se obtienen 27 \times 5 = 135 corridas y 3^3(n-1) = 108 grados de libertad para el error.

**Advertencia metodológica:** las réplicas dentro de cada celda comparten estrategias y no son plenamente independientes; el término de error refleja variabilidad inducida por submuestreo, no error de medición. Las inferencias del ANOVA deben interpretarse como sensibilidad estructural del ranking a los pesos, no como predicción operativa.

## 3. Modelo estadístico e hipótesis

El modelo estadístico de efectos fijos con tres factores se plantea como:


y_{ijkl} = \mu + \gamma_i + \delta_j + \theta_k + (\gamma\delta)*{ij} + (\gamma\theta)*{ik} + (\delta\theta)*{jk} + (\gamma\delta\theta)*{ijk} + \varepsilon_{ijkl}


donde \gamma_i, \delta_j, \theta_k son los efectos de los factores A, B y C; los términos entre paréntesis, sus interacciones; y \varepsilon_{ijkl} el error aleatorio. Las hipótesis, contrastadas con el ANOVA, son del tipo:


H_0: \gamma_i = 0, \quad H_0: \delta_j = 0, \quad H_0: \theta_k = 0, \quad H_0: (\gamma\delta)_{ij} = 0, \ \ldots


frente a la alternativa de que el efecto correspondiente es distinto de cero (el factor o interacción afecta significativamente a C_i).

### 3.1 Descomposición lineal/cuadrática

La suma de cuadrados de cada efecto (2 gl los principales, 4 gl las interacciones dobles) se descompone en componentes de **un grado de libertad** mediante contrastes ortogonales: el **lineal** con coeficientes (1, 0, -1) y el **cuadrático puro** con (1, -2, 1). La suma de cuadrados de cada componente se calcula con


SC = \frac{\left(\sum_c \text{coef}_c  T_c\right)^2}{n \sum_c \text{coef}_c^2},


donde T_c son los totales por celda. Se verificó numéricamente la identidad SC_A = SC_{A_L} + SC_{A^2} (y análogas para B y C), que se cumple de forma exacta.

## 4. Resultados

Gran media \bar{C_i} = 0.7257; coeficiente de determinación R^2 = 0.797 y R^2_{aj} = 0.749. Cuadrado medio del error CM_E = 0.00052 (108 gl).

### 4.1 ANOVA sin desglosar


| Fuente de variabilidad    | SC     | gl  | CM     | F_0   | Valor-p  |
| ------------------------- | ------ | --- | ------ | ----- | -------- |
| A (rentabilidad/carga)    | 0.0507 | 2   | 0.0254 | 48.71 | < 0.0001 |
| B (eficiencia operativa)  | 0.0609 | 2   | 0.0304 | 58.43 | < 0.0001 |
| C (riesgo/penalizaciones) | 0.0017 | 2   | 0.0009 | 1.68  | 0.1915   |
| AB                        | 0.0995 | 4   | 0.0249 | 47.76 | < 0.0001 |
| AC                        | 0.0027 | 4   | 0.0007 | 1.28  | 0.2832   |
| BC                        | 0.0024 | 4   | 0.0006 | 1.14  | 0.3435   |
| ABC                       | 0.0036 | 8   | 0.0005 | 0.87  | 0.5452   |
| Error                     | 0.0562 | 108 | 0.0005 |       |          |
| Total                     | 0.2777 | 134 |        |       |          |


Con \alpha = 0.05 se **rechazan** H_0 para los efectos **A**, **B** y la interacción **AB** (valores-p < 0.0001), y **no se rechaza** para C, AC, BC ni ABC. Es decir, el peso asignado a la rentabilidad y a la eficiencia operativa —y su interacción— afectan de forma significativa al C_i de la formación líder, mientras que el peso del bloque de riesgo/penalizaciones no lo hace en el rango estudiado. Notablemente, la interacción **AB es la fuente con mayor suma de cuadrados**, lo que indica que el efecto de priorizar la rentabilidad depende del peso dado a la eficiencia.

### 4.2 ANOVA desglosado en componentes de 1 gl

Componentes significativos (valor-p < 0.05):


| Componente | Efecto               | SC      | F_0    | Valor-p  |
| ---------- | -------------------- | ------- | ------ | -------- |
| B_L        | B lineal             | 0.05289 | 101.56 | < 0.0001 |
| A_LB_L     | AB lineal×lineal     | 0.05265 | 101.10 | < 0.0001 |
| A_L        | A lineal             | 0.03476 | 66.74  | < 0.0001 |
| A_LB^2     | AB lineal×cuadrático | 0.02361 | 45.33  | < 0.0001 |
| A^2B_L     | AB cuadrático×lineal | 0.02236 | 42.93  | < 0.0001 |
| A^2        | A cuadrático         | 0.01598 | 30.68  | < 0.0001 |
| B^2        | B cuadrático         | 0.00796 | 15.29  | 0.0002   |


Los componentes cuadráticos A^2 (F = 30.68) y B^2 (F = 15.29) son **estadísticamente significativos**: existe **curvatura** en el efecto de ambos factores sobre C_i. Esto justifica empíricamente el uso del diseño 3^k frente a un 2^k, que habría sido incapaz de detectar dicha curvatura. En el bloque de riesgo, ni C_L (p = 0.0703) ni C^2 (p = 0.90) alcanzan significancia.

### 4.3 Figuras

**Efectos principales** (tres niveles por factor; la curvatura de A y B es visible):

Efectos principales

**Gráficas de interacción** (promediando el tercer factor; la interacción A×B se aprecia en el cruce de pendientes):

Interacciones

**Análisis de residuos** (residuos vs. predichos, papel normal y orden de corrida):

Residuos

### 4.4 Factorial mixto: par O-D × prioridad de rentabilidad

Como extensión factorial mixta, se corrió un diseño **9 × 3**: el par origen-destino (9 niveles, los nueve pares del corredor norte) cruzado con el factor de peso de rentabilidad (3 niveles), con 5 réplicas por celda (CM_E = 0.00022, 108 gl).


| Fuente de variabilidad | SC     | gl  | CM     | F_0    | Valor-p  |
| ---------------------- | ------ | --- | ------ | ------ | -------- |
| Par O-D                | 0.2070 | 8   | 0.0259 | 116.14 | < 0.0001 |
| Peso rentabilidad (A)  | 0.2558 | 2   | 0.1279 | 574.20 | < 0.0001 |
| O-D × Peso             | 0.0273 | 16  | 0.0017 | 7.66   | < 0.0001 |


Los tres términos son significativos. En particular, la interacción **O-D × Peso** confirma **estadísticamente** el hallazgo cualitativo central del paper (§4.2): la respuesta del ranking a las prioridades del decisor **depende del corredor**, es decir, la estrategia óptima es contingente al par origen-destino.

## 5. Verificación de supuestos

Después del ANOVA, se examinaron los residuos (figura de la §4.3): la gráfica de residuos vs. predichos no muestra patrón sistemático (varianza aproximadamente constante), el papel de probabilidad normal no evidencia desviaciones graves de la normalidad y la gráfica frente al orden de corrida no exhibe tendencias (independencia). No se detectan violaciones que invaliden las conclusiones del ANOVA.

## 6. Discusión

En Monterrey–Laredo, A y B mueven de forma significativa al líder y la interacción AB domina la suma de cuadrados: conviene calibrar rentabilidad/carga y eficiencia en conjunto. Los términos cuadráticos A² y B² significativos confirman curvatura en ese rango. El bloque C no fue significativo aquí. El factorial mixto 9×3 refuerza que la respuesta depende del par O-D, en línea con los rankings del corredor norte del paper.

## 7. Limitaciones

- La variación experimental proviene del submuestreo de un conjunto factible pequeño (11 estrategias en Monterrey–Laredo); con datos operativos reales y mayor tamaño muestral las estimaciones ganarían precisión.
- Las réplicas del ANOVA no son mediciones independientes: comparten estrategias dentro de cada celda y el error modela variabilidad de submuestreo, no incertidumbre operativa.
- La prueba de estabilidad por partición (k = 5) no es validación cruzada predictiva; evalúa si el líder persiste al retirar un quinto de las formaciones candidatas (sensibilidad a reversión de ranking).
- El espacio combinatorio teórico desde un pool de 12 estrategias es del orden de 2.500 formaciones de 1–6 vagones; la heurística evalúa hasta 80 (~3 % en el caso límite).
- Los niveles de los factores son multiplicadores ordinales (bajo/medio/alto); un estudio de superficie de respuesta permitiría optimizar los pesos de forma continua.
- Los resultados son específicos del dataset sintético del corredor norte y no deben extrapolarse a otras redes sin recalibración.



## 8. Uso en el paper

Las tablas y figuras de las §4.1–4.4 alimentan la Metodología (diseño 3³), los Resultados (ANOVA y factorial mixto) y la Discusión del manuscrito Springer. Este archivo conserva el detalle de contrastes y supuestos que no cabe en el proceedings.

---



### Reproducibilidad

```bash
pip install numpy pandas scipy matplotlib
python scripts/run_factorial_experiment.py
```

Genera: `data/factorial_experiment.csv` (datos crudos, 135 corridas), `data/factorial_experiment.json` (tablas ANOVA y factorial mixto) y `assets/figs/factorial_*.png` (figuras). Semilla base fija (`BASE_SEED = 20260703`) para resultados reproducibles.