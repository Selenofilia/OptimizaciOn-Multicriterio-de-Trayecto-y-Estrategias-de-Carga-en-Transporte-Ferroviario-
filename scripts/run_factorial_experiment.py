#!/usr/bin/env python3
"""Experimento factorial 3^k sobre la capa de carga del TOPSIS bicapa.

Aplica un diseno factorial 3^k a la capa de carga del simulador del norte de México.
La variable de respuesta es el coeficiente de cercania Ci de la formacion lider.

Factores (3 niveles cada uno: bajo/medio/alto, codificados -1/0/+1):
  A = Rentabilidad/carga     -> total_profit_usd, total_cargo_tons
  B = Eficiencia operativa   -> avg_utilization_pct, avg_maintenance_score,
                                total_op_time_hr, total_fuel_cost_usd
  C = Riesgo/penalizaciones  -> max_weather_risk, hazardous_units,
                                hm_separation_penalty, type_mix_penalty

Cada factor multiplica el peso base del grupo por {0.5, 1.0, 2.0}; los diez
pesos se renormalizan a suma 1 dentro del metodo (los factores son entradas
independientes, por lo que el 3^3 conserva su ortogonalidad).

Replicas: TOPSIS es determinista, por lo que la variacion experimental proviene
de un submuestreo aleatorio (con semilla) de las estrategias factibles del par
origen-destino antes de generar las formaciones candidatas. Con n replicas por
tratamiento se obtienen 3^3 x n corridas y grados de libertad para el error
(n >= 2).

ANOVA: las sumas de cuadrados de cada componente de 1 gl se calculan con la
formula de contrastes:
    SC = (sum_c coef_c * T_c)^2 / (n * sum_c coef_c^2)
usando el contraste lineal (1, 0, -1) y el cuadratico puro (1, -2, 1). Se
reporta la tabla sin desglosar y la desglosada en efectos
lineales/cuadraticos e interacciones, verificando la
identidad SC_A = SC_AL + SC_A2.
"""
from __future__ import annotations

import csv
import json
import os
import random
import sys
from itertools import product
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_topsis_analysis as rt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIGS_DIR = ROOT / "assets" / "figs"
DATA_DIR = ROOT / "data"

# --- Definicion del diseno factorial ---
GROUP_A = ["total_profit_usd", "total_cargo_tons"]
GROUP_B = [
    "avg_utilization_pct",
    "avg_maintenance_score",
    "total_op_time_hr",
    "total_fuel_cost_usd",
]
GROUP_C = [
    "max_weather_risk",
    "hazardous_units",
    "hm_separation_penalty",
    "type_mix_penalty",
]
FACTOR_LABELS = {
    "A": "Rentabilidad/carga",
    "B": "Eficiencia operativa",
    "C": "Riesgo/penalizaciones",
}
FACTOR_LABELS_EN = {
    "A": "Profit/load",
    "B": "Operational efficiency",
    "C": "Risk/penalties",
}
FIG_LABELS = {
    "es": {
        "level_ticks": ["bajo\n(-1)", "medio\n(0)", "alto\n(+1)"],
        "weight_level": "Nivel de peso",
        "main_ylabel": "$C_i$ medio de la formacion lider",
        "main_title": "Efectos principales sobre $C_i$ (capa de carga, Monterrey-Laredo)",
        "level_labels": {-1: "bajo (-1)", 0: "medio (0)", 1: "alto (+1)"},
        "interaction_title": "Interaccion {f1} x {f2}",
        "level_of": "Nivel de {f1}",
        "interaction_ylabel": "$C_i$ medio",
        "interaction_suptitle": "Graficas de interaccion (promediando el tercer factor)",
        "residuals_pred": "Predichos ($\\hat{C_i}$)",
        "residuals": "Residuos",
        "residuals_vs_pred": "Residuos vs. predichos",
        "normal_quantiles": "Cuantiles normales",
        "ordered_residuals": "Residuos ordenados",
        "normal_paper": "Papel normal",
        "run_order": "Orden de corrida",
        "residuals_vs_order": "Residuos vs. orden",
        "residuals_suptitle": "Analisis de residuos del modelo 3^3",
    },
    "en": {
        "level_ticks": ["low\n(-1)", "medium\n(0)", "high\n(+1)"],
        "weight_level": "Weight level",
        "main_ylabel": "Mean leader consist $C_i$",
        "main_title": "Main effects on $C_i$ (load layer, Monterrey–Laredo)",
        "level_labels": {-1: "low (-1)", 0: "medium (0)", 1: "high (+1)"},
        "interaction_title": "Interaction {f1} × {f2}",
        "level_of": "Level of {f1}",
        "interaction_ylabel": "Mean $C_i$",
        "interaction_suptitle": "Interaction plots (averaging the third factor)",
        "residuals_pred": "Fitted ($\\hat{C_i}$)",
        "residuals": "Residuals",
        "residuals_vs_pred": "Residuals vs. fitted",
        "normal_quantiles": "Normal quantiles",
        "ordered_residuals": "Ordered residuals",
        "normal_paper": "Normal probability plot",
        "run_order": "Run order",
        "residuals_vs_order": "Residuals vs. run order",
        "residuals_suptitle": "Residual analysis of the 3^3 model",
    },
}


def _fig_name(base: str, lang: str) -> str:
    stem, ext = base.rsplit(".", 1)
    return f"{stem}_en.{ext}" if lang == "en" else base
LEVELS = [-1, 0, 1]              # codificacion bajo/medio/alto
LEVEL_MULT = {-1: 0.5, 0: 1.0, 1: 2.0}
N_REPLICAS = 5
SUBSAMPLE_FRAC = 0.8
BASE_SEED = 20260703

PRIMARY_ORIGIN = "Monterrey"
PRIMARY_DEST = "Laredo"

# Contrastes ortogonales para 3 niveles equiespaciados
CONTRASTS = {
    "L": {-1: -1.0, 0: 0.0, 1: 1.0},   # lineal (1, 0, -1)
    "Q": {-1: 1.0, 0: -2.0, 1: 1.0},   # cuadratico puro (1, -2, 1)
    "I": {-1: 1.0, 0: 1.0, 1: 1.0},    # identidad (media)
}


def group_of(criterion: str) -> str:
    if criterion in GROUP_A:
        return "A"
    if criterion in GROUP_B:
        return "B"
    return "C"


def dist_weights_from_levels(la: int, lb: int, lc: int) -> list[float]:
    """Pesos de la capa de carga para un tratamiento (la, lb, lc)."""
    mult = {"A": LEVEL_MULT[la], "B": LEVEL_MULT[lb], "C": LEVEL_MULT[lc]}
    raw = [rt.DIST_DEFAULT_WEIGHTS[c] * mult[group_of(c)] for c in rt.DIST_ALL_CRITERIA]
    return rt.normalize_weights(raw)


def prepare_feasible(origin: str, dest: str, dataset: list[dict], slug_map: dict,
                     adj: dict) -> list[dict]:
    """Estrategias factibles del par O-D, alineadas a la ruta Dijkstra."""
    alts = [
        d
        for d in dataset
        if d["origin"] == origin and d["destination"] == dest and d.get("capacity_feasible")
    ]
    start, end = slug_map.get(origin), slug_map.get(dest)
    route_dist = None
    if start and end:
        _, route_dist = rt.dijkstra(adj, start, end)
        if route_dist is not None and not np.isfinite(route_dist):
            route_dist = None
    return rt.align_alternatives_to_route(alts, route_dist)


def candidates_for_subsample(feasible: list[dict], slots: list[dict], seed: int) -> list[dict]:
    """Submuestrea las factibles y genera formaciones candidatas (pre-filtro uniforme)."""
    rng = random.Random(seed)
    k = max(5, round(SUBSAMPLE_FRAC * len(feasible)))
    k = min(k, len(feasible))
    subsample = rng.sample(feasible, k)
    pw = rt.normalize_weights([1 / len(rt.ALL_CRITERIA)] * len(rt.ALL_CRITERIA))
    pool_ranked = rt.topsis_with_criteria(subsample, rt.ALL_CRITERIA, rt.CRITERIA_BENEFIT, pw)
    return rt.generate_distribution_candidates(pool_ranked, slots)


def run_factorial(feasible: list[dict], slots: list[dict]) -> list[dict]:
    """Corre el diseno 3^3 con replicas independientes (replicacion pura)."""
    rows = []
    for idx, (la, lb, lc) in enumerate(product(LEVELS, repeat=3)):
        weights = dist_weights_from_levels(la, lb, lc)
        for rep in range(N_REPLICAS):
            seed = BASE_SEED + idx * 997 + rep * 7
            candidates = candidates_for_subsample(feasible, slots, seed)
            if not candidates:
                continue
            ranked = rt.topsis_with_criteria(
                candidates, rt.DIST_ALL_CRITERIA, rt.DIST_CRITERIA_BENEFIT, weights
            )
            ci, leader = ranked[0]
            rows.append(
                {
                    "treatment": idx + 1,
                    "A": la,
                    "B": lb,
                    "C": lc,
                    "A_mult": LEVEL_MULT[la],
                    "B_mult": LEVEL_MULT[lb],
                    "C_mult": LEVEL_MULT[lc],
                    "replica": rep + 1,
                    "ci": ci,
                    "leader_dist_id": leader["dist_id"],
                    "leader_label": leader["label"],
                    "cars": leader["cargo_count"],
                }
            )
    return rows


# --- ANOVA con contrastes ---
def cell_totals(rows: list[dict]) -> tuple[dict, dict, int]:
    """Total y numero de datos por celda (la, lb, lc)."""
    totals: dict[tuple, float] = {}
    counts: dict[tuple, int] = {}
    for r in rows:
        key = (r["A"], r["B"], r["C"])
        totals[key] = totals.get(key, 0.0) + r["ci"]
        counts[key] = counts.get(key, 0) + 1
    n = min(counts.values())
    return totals, counts, n


def contrast_ss(totals: dict, comp: tuple[str, str, str], n: int) -> float:
    """SC de un componente de 1 gl via contraste ortogonal."""
    num = 0.0
    den = 0.0
    for (la, lb, lc), t in totals.items():
        coef = CONTRASTS[comp[0]][la] * CONTRASTS[comp[1]][lb] * CONTRASTS[comp[2]][lc]
        num += coef * t
        den += coef * coef
    return (num * num) / (n * den) if den else 0.0


def component_name(comp: tuple[str, str, str]) -> str:
    parts = []
    for factor, ctype in zip("ABC", comp):
        if ctype == "L":
            parts.append(f"{factor}L")
        elif ctype == "Q":
            parts.append(f"{factor}2")
    return "".join(parts)


def effect_of(comp: tuple[str, str, str]) -> str:
    return "".join(f for f, c in zip("ABC", comp) if c != "I")


def anova(rows: list[dict]) -> dict:
    totals, counts, n = cell_totals(rows)
    y = np.array([r["ci"] for r in rows], dtype=float)
    grand = y.mean()
    ss_total = float(((y - grand) ** 2).sum())

    # SC del error: variacion dentro de cada celda
    ss_error = 0.0
    for key in totals:
        vals = np.array([r["ci"] for r in rows if (r["A"], r["B"], r["C"]) == key])
        ss_error += float(((vals - vals.mean()) ** 2).sum())
    n_cells = len(totals)
    df_error = len(y) - n_cells
    ms_error = ss_error / df_error if df_error else float("nan")

    # Componentes de 1 gl (excluye el gran promedio I,I,I)
    components = {}
    for comp in product(["I", "L", "Q"], repeat=3):
        if comp == ("I", "I", "I"):
            continue
        components[comp] = contrast_ss(totals, comp, n)

    # Tabla desglosada (1 gl cada uno)
    desglosado = []
    for comp, ss in components.items():
        f0 = (ss / 1) / ms_error if ms_error else float("nan")
        p = float(stats.f.sf(f0, 1, df_error)) if df_error else float("nan")
        desglosado.append(
            {
                "componente": component_name(comp),
                "efecto": effect_of(comp),
                "SC": ss,
                "gl": 1,
                "CM": ss,
                "F0": f0,
                "valor_p": p,
            }
        )

    # Tabla agregada por efecto (A, B, C, AB, AC, BC, ABC)
    agg_order = ["A", "B", "C", "AB", "AC", "BC", "ABC"]
    agg: dict[str, dict] = {e: {"SC": 0.0, "gl": 0} for e in agg_order}
    for comp, ss in components.items():
        e = effect_of(comp)
        agg[e]["SC"] += ss
        agg[e]["gl"] += 1
    sin_desglosar = []
    for e in agg_order:
        ss = agg[e]["SC"]
        gl = agg[e]["gl"]
        cm = ss / gl
        f0 = cm / ms_error if ms_error else float("nan")
        p = float(stats.f.sf(f0, gl, df_error)) if df_error else float("nan")
        sin_desglosar.append(
            {"efecto": e, "SC": ss, "gl": gl, "CM": cm, "F0": f0, "valor_p": p}
        )

    ss_model = sum(a["SC"] for a in sin_desglosar)
    r2 = ss_model / ss_total if ss_total else float("nan")
    df_model = sum(a["gl"] for a in sin_desglosar)
    r2_adj = 1 - (ss_error / df_error) / (ss_total / (len(y) - 1)) if df_error else float("nan")

    # Verificacion SC_A = SC_AL + SC_A2, etc.
    checks = {}
    for factor in "ABC":
        comp_l = tuple("L" if f == factor else "I" for f in "ABC")
        comp_q = tuple("Q" if f == factor else "I" for f in "ABC")
        checks[factor] = {
            "SC_efecto": agg[factor]["SC"],
            "SC_L_mas_Q": components[comp_l] + components[comp_q],
        }

    return {
        "n_replicas_efectivas": n,
        "n_celdas": n_cells,
        "grados_libertad_error": df_error,
        "grados_libertad_modelo": df_model,
        "grand_mean": grand,
        "ss_total": ss_total,
        "ss_error": ss_error,
        "ms_error": ms_error,
        "R2": r2,
        "R2_ajustado": r2_adj,
        "anova_sin_desglosar": sin_desglosar,
        "anova_desglosado": desglosado,
        "verificacion_SC": checks,
    }


# --- Factorial mixto: par O-D (hasta 9 niveles) x factor de peso (3 niveles) ---
def run_mixed_factorial(dataset: list[dict], slug_map: dict, adj: dict, slots: list[dict]) -> dict:
    pairs = []
    for o in sorted(rt.NORTH_ORIGINS):
        for d in sorted(rt.NORTH_DESTS):
            feas = prepare_feasible(o, d, dataset, slug_map, adj)
            if len(feas) >= 5:
                pairs.append((f"{o}-{d}", feas))
    rows = []
    for pi, (name, feas) in enumerate(pairs):
        for wl in LEVELS:  # nivel del factor de peso A (rentabilidad)
            weights = dist_weights_from_levels(wl, 0, 0)
            for rep in range(N_REPLICAS):
                seed = BASE_SEED + 500000 + pi * 3001 + (wl + 1) * 101 + rep * 7
                candidates = candidates_for_subsample(feas, slots, seed)
                if not candidates:
                    continue
                ranked = rt.topsis_with_criteria(
                    candidates, rt.DIST_ALL_CRITERIA, rt.DIST_CRITERIA_BENEFIT, weights
                )
                rows.append({"od": name, "W": wl, "replica": rep + 1, "ci": ranked[0][0]})

    # ANOVA de dos vias con interaccion (efectos fijos)
    ods = sorted({r["od"] for r in rows})
    ws = sorted({r["W"] for r in rows})
    y = np.array([r["ci"] for r in rows], dtype=float)
    grand = y.mean()
    a, b = len(ods), len(ws)

    def mean_where(pred):
        vals = [r["ci"] for r in rows if pred(r)]
        return float(np.mean(vals)) if vals else float("nan")

    n_cell = min(
        sum(1 for r in rows if r["od"] == o and r["W"] == w) for o in ods for w in ws
    )
    ss_od = sum(
        sum(1 for r in rows if r["od"] == o) * (mean_where(lambda r, o=o: r["od"] == o) - grand) ** 2
        for o in ods
    )
    ss_w = sum(
        sum(1 for r in rows if r["W"] == w) * (mean_where(lambda r, w=w: r["W"] == w) - grand) ** 2
        for w in ws
    )
    ss_cells = 0.0
    ss_error = 0.0
    for o in ods:
        for w in ws:
            cell = [r["ci"] for r in rows if r["od"] == o and r["W"] == w]
            if not cell:
                continue
            cm = float(np.mean(cell))
            ss_cells += len(cell) * (cm - grand) ** 2
            ss_error += float(np.sum((np.array(cell) - cm) ** 2))
    ss_inter = ss_cells - ss_od - ss_w
    ss_total = float(np.sum((y - grand) ** 2))
    df_od, df_w, df_inter = a - 1, b - 1, (a - 1) * (b - 1)
    df_error = len(y) - a * b
    ms_error = ss_error / df_error if df_error else float("nan")

    def frow(name, ss, df):
        cm = ss / df
        f0 = cm / ms_error if ms_error else float("nan")
        p = float(stats.f.sf(f0, df, df_error)) if df_error else float("nan")
        return {"efecto": name, "SC": ss, "gl": df, "CM": cm, "F0": f0, "valor_p": p}

    return {
        "diseno": f"{a}x{b} mixto (par O-D x peso rentabilidad)",
        "niveles_od": ods,
        "niveles_peso": [LEVEL_MULT[w] for w in ws],
        "n_replicas_celda": n_cell,
        "grados_libertad_error": df_error,
        "ms_error": ms_error,
        "anova": [
            frow("O-D", ss_od, df_od),
            frow("Peso (A)", ss_w, df_w),
            frow("O-D x Peso", ss_inter, df_inter),
        ],
        "ss_total": ss_total,
    }


# --- Figuras ---
def _cell_mean_grid(rows: list[dict]):
    means = {}
    for la, lb, lc in product(LEVELS, repeat=3):
        vals = [r["ci"] for r in rows if (r["A"], r["B"], r["C"]) == (la, lb, lc)]
        means[(la, lb, lc)] = float(np.mean(vals)) if vals else float("nan")
    return means


def factor_level_means(rows: list[dict], factor: str) -> list[float]:
    out = []
    for lv in LEVELS:
        vals = [r["ci"] for r in rows if r[factor] == lv]
        out.append(float(np.mean(vals)))
    return out


def fig_main_effects(rows: list[dict], path: Path, lang: str = "es") -> None:
    t = FIG_LABELS[lang]
    factor_labels = FACTOR_LABELS_EN if lang == "en" else FACTOR_LABELS
    ink = "#1f2a37"
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    for ax, factor in zip(axes, "ABC"):
        m = factor_level_means(rows, factor)
        ax.plot([0, 1, 2], m, "o-", color=ink, lw=2, ms=7)
        ax.set_title(f"Factor {factor}: {factor_labels[factor]}", fontsize=9)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(t["level_ticks"], fontsize=8)
        ax.set_xlabel(t["weight_level"], fontsize=8)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(t["main_ylabel"])
    fig.suptitle(t["main_title"], fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=800)
    plt.close(fig)


def fig_interactions(rows: list[dict], path: Path, lang: str = "es") -> None:
    t = FIG_LABELS[lang]
    means = _cell_mean_grid(rows)
    pairs = [("A", "B", "C"), ("A", "C", "B"), ("B", "C", "A")]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    level_colors = {-1: "#b5651d", 0: "#5c4d8a", 1: "#3a7d44"}
    for ax, (f1, f2, fixed) in zip(axes, pairs):
        for lv2 in LEVELS:
            ys = []
            for lv1 in LEVELS:
                sel = [
                    means[k]
                    for k in means
                    if dict(zip("ABC", k))[f1] == lv1 and dict(zip("ABC", k))[f2] == lv2
                ]
                ys.append(float(np.nanmean(sel)))
            ax.plot(
                [0, 1, 2], ys, "o-", color=level_colors[lv2],
                label=t["level_labels"][lv2], lw=1.8,
            )
        ax.set_title(t["interaction_title"].format(f1=f1, f2=f2), fontsize=9)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["-1", "0", "+1"], fontsize=8)
        ax.set_xlabel(t["level_of"].format(f1=f1), fontsize=8)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, title=None)
    axes[0].set_ylabel(t["interaction_ylabel"])
    fig.suptitle(t["interaction_suptitle"], fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=800)
    plt.close(fig)


def fig_residuals(rows: list[dict], path: Path, lang: str = "es") -> None:
    t = FIG_LABELS[lang]
    means = _cell_mean_grid(rows)
    fitted = np.array([means[(r["A"], r["B"], r["C"])] for r in rows])
    y = np.array([r["ci"] for r in rows])
    resid = y - fitted
    resid_color = "#1f2a37"
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    axes[0].scatter(fitted, resid, s=14, color=resid_color, alpha=0.7)
    axes[0].axhline(0, color="k", lw=0.8)
    axes[0].set_xlabel(t["residuals_pred"], fontsize=8)
    axes[0].set_ylabel(t["residuals"], fontsize=8)
    axes[0].set_title(t["residuals_vs_pred"], fontsize=9)
    axes[0].grid(alpha=0.3)

    (osm, osr), _ = stats.probplot(resid, dist="norm")
    axes[1].scatter(osm, osr, s=14, color=resid_color, alpha=0.7)
    axes[1].plot(osm, osm * resid.std() + resid.mean(), "k-", lw=0.8)
    axes[1].set_xlabel(t["normal_quantiles"], fontsize=8)
    axes[1].set_ylabel(t["ordered_residuals"], fontsize=8)
    axes[1].set_title(t["normal_paper"], fontsize=9)
    axes[1].grid(alpha=0.3)

    axes[2].scatter(range(len(resid)), resid, s=14, color=resid_color, alpha=0.7)
    axes[2].axhline(0, color="k", lw=0.8)
    axes[2].set_xlabel(t["run_order"], fontsize=8)
    axes[2].set_ylabel(t["residuals"], fontsize=8)
    axes[2].set_title(t["residuals_vs_order"], fontsize=9)
    axes[2].grid(alpha=0.3)
    fig.suptitle(t["residuals_suptitle"], fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=800)
    plt.close(fig)


# --- Exportacion ---
def export_csv(rows: list[dict], path: Path) -> None:
    cols = [
        "treatment", "A", "B", "C", "A_mult", "B_mult", "C_mult",
        "replica", "ci", "leader_dist_id", "leader_label", "cars",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r[c] for c in cols})


def anova_markdown(res: dict) -> str:
    lines = ["| FV | SC | gl | CM | F0 | valor-p |", "|----|----|----|----|----|---------|"]
    for a in res["anova_sin_desglosar"]:
        lines.append(
            f"| {a['efecto']} | {a['SC']:.4f} | {a['gl']} | {a['CM']:.4f} | {a['F0']:.2f} | {a['valor_p']:.4f} |"
        )
    lines.append(
        f"| Error | {res['ss_error']:.4f} | {res['grados_libertad_error']} | {res['ms_error']:.4f} |  |  |"
    )
    lines.append(f"| Total | {res['ss_total']:.4f} | {res['n_celdas'] * res['n_replicas_efectivas'] - 1} |  |  |  |")
    return "\n".join(lines)


def main() -> None:
    dataset = rt.load_json("dataset.json")
    cities = rt.load_json("cities.json")
    wagon_map = rt.load_json("wagon_map.json")
    slug_map = cities["slug_map"]
    adj = rt.build_graph(cities)
    slots = wagon_map["slots"]

    FIGS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Experimento factorial 3^3 (capa de carga) ===")
    print(f"Par O-D primario: {PRIMARY_ORIGIN}-{PRIMARY_DEST}")
    feasible = prepare_feasible(PRIMARY_ORIGIN, PRIMARY_DEST, dataset, slug_map, adj)
    print(f"Estrategias factibles: {len(feasible)} | submuestreo {int(SUBSAMPLE_FRAC*100)}% | replicas={N_REPLICAS}")

    rows = run_factorial(feasible, slots)
    print(f"Corridas registradas: {len(rows)} (esperado 27 x {N_REPLICAS} = {27*N_REPLICAS})")

    res = anova(rows)
    print(f"\nGran media Ci = {res['grand_mean']:.4f} | R2 = {res['R2']:.3f} | R2_aj = {res['R2_ajustado']:.3f}")
    print(f"CM error = {res['ms_error']:.5f} (gl={res['grados_libertad_error']})\n")
    print("ANOVA sin desglosar:")
    print(f"{'FV':<6}{'SC':>10}{'gl':>4}{'CM':>10}{'F0':>10}{'valor-p':>10}")
    for a in res["anova_sin_desglosar"]:
        print(f"{a['efecto']:<6}{a['SC']:>10.4f}{a['gl']:>4}{a['CM']:>10.4f}{a['F0']:>10.2f}{a['valor_p']:>10.4f}")
    print(f"{'Error':<6}{res['ss_error']:>10.4f}{res['grados_libertad_error']:>4}{res['ms_error']:>10.4f}")

    print("\nVerificacion SC_efecto = SC_L + SC_Q:")
    for f, c in res["verificacion_SC"].items():
        print(f"  {f}: efecto={c['SC_efecto']:.5f}  L+Q={c['SC_L_mas_Q']:.5f}")

    print("\nComponentes significativos (valor-p < 0.05, ANOVA desglosado):")
    for d in sorted(res["anova_desglosado"], key=lambda x: x["valor_p"]):
        if d["valor_p"] < 0.05:
            print(f"  {d['componente']:<8} F0={d['F0']:>8.2f}  p={d['valor_p']:.4f}")

    # Figuras incluidas en el paper (ES + EN).
    for lang in ("es", "en"):
        fig_main_effects(rows, FIGS_DIR / _fig_name("factorial_efectos_principales.png", lang), lang)
        fig_interactions(rows, FIGS_DIR / _fig_name("factorial_interacciones.png", lang), lang)
        fig_residuals(rows, FIGS_DIR / _fig_name("factorial_residuos.png", lang), lang)
    print(f"\nFiguras guardadas en {FIGS_DIR} (es + en)")

    # Factorial mixto
    print("\n=== Factorial mixto (par O-D x peso) ===")
    mixed = run_mixed_factorial(dataset, slug_map, adj, slots)
    print(f"Diseno: {mixed['diseno']} | replicas/celda={mixed['n_replicas_celda']}")
    print(f"{'FV':<12}{'SC':>10}{'gl':>4}{'CM':>10}{'F0':>10}{'valor-p':>10}")
    for a in mixed["anova"]:
        print(f"{a['efecto']:<12}{a['SC']:>10.4f}{a['gl']:>4}{a['CM']:>10.4f}{a['F0']:>10.2f}{a['valor_p']:>10.4f}")

    # Exportacion
    export_csv(rows, DATA_DIR / "factorial_experiment.csv")
    payload = {
        "diseno": "factorial 3^3 sobre la capa de carga (Ci de la formacion lider)",
        "referencia": "procedimiento factorial 3^3 reproducible del proyecto",
        "par_od_primario": f"{PRIMARY_ORIGIN}-{PRIMARY_DEST}",
        "factores": {
            "A": {"label": FACTOR_LABELS["A"], "criterios": GROUP_A},
            "B": {"label": FACTOR_LABELS["B"], "criterios": GROUP_B},
            "C": {"label": FACTOR_LABELS["C"], "criterios": GROUP_C},
        },
        "niveles_multiplicador": LEVEL_MULT,
        "n_replicas": N_REPLICAS,
        "submuestreo_frac": SUBSAMPLE_FRAC,
        "n_factibles": len(feasible),
        "resultado_anova": res,
        "anova_markdown": anova_markdown(res),
        "factorial_mixto": mixed,
    }
    (DATA_DIR / "factorial_experiment.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nDatos exportados: {DATA_DIR / 'factorial_experiment.csv'}")
    print(f"Resumen ANOVA exportado: {DATA_DIR / 'factorial_experiment.json'}")


if __name__ == "__main__":
    main()
