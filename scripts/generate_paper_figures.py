#!/usr/bin/env python3
"""Generate the embedded diagrams (PNG) for Paper 1 (TOPSIS railway cargo).

All figures are written to assets/figs/ and embedded by generate_paper_docx.py.
The figures are derived strictly from the current simulator context
(SIMULADOR_TOPSIS.html, data/cities.json) and the reported results.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "assets" / "figs"
RESULTS_JSON = ROOT / "data" / "paper_results.json"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_results() -> dict:
    if RESULTS_JSON.exists():
        return json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    return {}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 13,
        "savefig.dpi": 200,
        "figure.dpi": 200,
    }
)

# Muted, print-friendly palette (works in grayscale too).
INK = "#1f2a37"
C_BENEFIT = "#2f6f8f"   # azul
C_COST = "#b5651d"      # ocre
C_NEUTRAL = "#4c5a67"   # gris azulado
C_ACCENT = "#7a4f9c"    # violeta
C_OK = "#3a7d44"        # verde
C_LIGHT = "#eef2f5"
C_LIGHT2 = "#f6efe6"


def _box(ax, x, y, w, h, text, face, edge=INK, fontcolor="white", fontsize=10, lw=1.4):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=lw,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", color=fontcolor,
            fontsize=fontsize, wrap=True, zorder=5)
    return patch


def _arrow(ax, x1, y1, x2, y2, color=INK, lw=1.6, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle=style,
            mutation_scale=14,
            linewidth=lw,
            color=color,
            shrinkA=2,
            shrinkB=2,
        )
    )


def _save(fig, name):
    out = FIG_DIR / name
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  figura: {out.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Figura 1 - Proceso cuantitativo de Hernandez Sampieri
# ---------------------------------------------------------------------------
def fig_sampieri():
    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    steps = [
        ("Idea y\nplanteamiento\ndel problema", "Cap. 3"),
        ("Revisión de\nla literatura y\nmarco teórico", "Cap. 4"),
        ("Definición de\nalcance y\ndiseño", "Caps. 5-8"),
        ("Recolección\nde datos\n(dataset)", "Cap. 7"),
        ("Análisis de\ndatos\n(TOPSIS)", "Cap. 8"),
        ("Reporte de\nresultados", "Cap. 11"),
    ]
    n = len(steps)
    w, h = 1.42, 1.7
    xs = [0.95 + i * (10 - 1.9) / (n - 1) for i in range(n)]
    y = 2.35
    for i, ((text, cap), x) in enumerate(zip(steps, xs)):
        face = C_BENEFIT if i % 2 == 0 else C_NEUTRAL
        _box(ax, x, y, w, h, text, face, fontsize=8.7)
        ax.text(x, y - h / 2 - 0.28, cap, ha="center", va="center",
                color=INK, fontsize=8, style="italic")
        if i < n - 1:
            _arrow(ax, x + w / 2, y, xs[i + 1] - w / 2, y, color=INK)
    ax.text(5, 0.45, "Retroalimentación entre etapas (proceso secuencial e iterativo)",
            ha="center", va="center", color=C_NEUTRAL, fontsize=8.5, style="italic")
    _arrow(ax, xs[-1], 1.35, xs[0], 1.35, color=C_NEUTRAL, lw=1.1, style="-|>")
    _save(fig, "fig1_proceso_sampieri.png")


# ---------------------------------------------------------------------------
# Figura 2 - Arquitectura de dos capas TOPSIS
# ---------------------------------------------------------------------------
def fig_arquitectura():
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    _box(ax, 5, 9.2, 5.6, 0.9, "Selección Origen-Destino (decisor)", INK, fontsize=11)

    # Capa fisica (izquierda)
    ax.add_patch(FancyBboxPatch((0.3, 3.7), 4.4, 4.5, boxstyle="round,pad=0.05,rounding_size=0.1",
                                linewidth=1.3, edgecolor=C_BENEFIT, facecolor=C_LIGHT))
    ax.text(2.5, 7.9, "CAPA FÍSICA (red)", ha="center", color=C_BENEFIT, fontsize=10.5, fontweight="bold")
    _box(ax, 2.5, 7.1, 3.5, 0.85, "Grafo de 25 estaciones", C_BENEFIT, fontsize=9.5)
    _box(ax, 2.5, 5.95, 3.5, 0.95, "Dijkstra + bloqueo de\naristas (hasta 5 rutas)", C_BENEFIT, fontsize=9.2)
    _box(ax, 2.5, 4.7, 3.5, 0.95, "Capa de ruteo\n(6 criterios de red)", C_ACCENT, fontsize=9.5)

    # Capa comercial (derecha)
    ax.add_patch(FancyBboxPatch((5.3, 3.7), 4.4, 4.5, boxstyle="round,pad=0.05,rounding_size=0.1",
                                linewidth=1.3, edgecolor=C_COST, facecolor=C_LIGHT2))
    ax.text(7.5, 7.9, "CAPA COMERCIAL (carga)", ha="center", color=C_COST, fontsize=10.5, fontweight="bold")
    _box(ax, 7.5, 7.1, 3.5, 0.85, "Dataset de estrategias", C_COST, fontsize=9.5)
    _box(ax, 7.5, 6.35, 3.5, 0.75, "Filtro de factibilidad\n(peso) y restricciones", C_COST, fontsize=9.0)
    _box(ax, 7.5, 5.35, 3.5, 0.75, "Pre-filtro interno\n(11 crit., top-12)", C_NEUTRAL, fontsize=8.8)
    _box(ax, 7.5, 4.35, 3.5, 0.75, "Capa de carga\n(10 crit. agregados)", C_ACCENT, fontsize=9.2)

    # Salidas
    _box(ax, 2.5, 2.55, 3.5, 0.85, "Ruta ganadora\nen el mapa", C_OK, fontsize=9.2)
    _box(ax, 7.5, 2.55, 3.5, 0.85, "Formación ganadora\n(1–6 vagones)", C_OK, fontsize=9.2)
    _box(ax, 5, 1.0, 9.0, 0.95,
         "Validación: sensibilidad ±20 %, MOORA, validación cruzada k = 5",
         C_NEUTRAL, fontsize=9.2)

    _arrow(ax, 4.0, 8.75, 2.5, 7.55)
    _arrow(ax, 6.0, 8.75, 7.5, 7.55)
    for x in (2.5, 7.5):
        _arrow(ax, x, 6.68, x, 6.45)
        if x == 7.5:
            _arrow(ax, x, 5.97, x, 5.72)
            _arrow(ax, x, 4.97, x, 4.72)
            _arrow(ax, x, 3.97, x, 2.98)
        else:
            _arrow(ax, x, 5.47, x, 5.20)
            _arrow(ax, x, 4.22, x, 2.98)
        _arrow(ax, x, 2.12, x if x == 2.5 else x, 1.50, color=C_NEUTRAL)
    _arrow(ax, 3.7, 2.55, 5.7, 2.55, color=C_NEUTRAL, lw=1.1, style="<->")
    _save(fig, "fig2_arquitectura_2capas.png")


# ---------------------------------------------------------------------------
# Figura 3 - Flujo de los 6 pasos de TOPSIS
# ---------------------------------------------------------------------------
def fig_topsis_flow():
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")
    steps = [
        ("1. Matriz de\ndecisión X", r"$x_{ij}$"),
        ("2. Normalización\nvectorial", r"$r_{ij}=x_{ij}/\sqrt{\sum_i x_{ij}^2}$"),
        ("3. Matriz\nponderada", r"$v_{ij}=w_j\, r_{ij}$"),
        ("4. Ideal y\nanti-ideal", r"$A^+_j,\ A^-_j$"),
        ("5. Distancias\neuclidianas", r"$S^+_i,\ S^-_i$"),
        ("6. Coeficiente\nde cercanía", r"$C_i=\dfrac{S^-_i}{S^+_i+S^-_i}$"),
    ]
    n = len(steps)
    w, h = 1.7, 1.5
    xs = [1.0 + i * (12 - 2.0) / (n - 1) for i in range(n)]
    y = 2.4
    for i, ((title, formula), x) in enumerate(zip(steps, xs)):
        _box(ax, x, y, w, h, title, C_BENEFIT if i < 3 else C_ACCENT, fontsize=8.8)
        ax.text(x, y - h / 2 - 0.42, formula, ha="center", va="center",
                color=INK, fontsize=8.6)
        if i < n - 1:
            _arrow(ax, x + w / 2, y, xs[i + 1] - w / 2, y)
    ax.text(6, 0.35, "Ordenamiento por $C_i$ descendente  →  ranking de alternativas",
            ha="center", color=C_NEUTRAL, fontsize=9.5, style="italic")
    _save(fig, "fig3_flujo_topsis.png")


# ---------------------------------------------------------------------------
# Figura 4 - Red ferroviaria del norte (data/cities.json)
# ---------------------------------------------------------------------------
def fig_red():
    data = json.loads((ROOT / "data" / "cities.json").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in data["nodes"]}
    edges = data["edges"]
    states = data["states"]

    corridor_pairs = {
        ("chihuahua", "laredo"), ("ciudad_juarez", "laredo"), ("monterrey", "laredo"),
        ("chihuahua", "saltillo"), ("ciudad_juarez", "saltillo"), ("monterrey", "saltillo"),
        ("chihuahua", "torreon"), ("ciudad_juarez", "torreon"), ("monterrey", "torreon"),
    }
    corridor_nodes = {"chihuahua", "ciudad_juarez", "monterrey", "laredo", "torreon", "saltillo"}

    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    for e in edges:
        a, b = nodes[e["from"]], nodes[e["to"]]
        ax.plot([a["lng"], b["lng"]], [a["lat"], b["lat"]],
                color="#b7c2cc", lw=1.2, zorder=1)
        mx, my = (a["lng"] + b["lng"]) / 2, (a["lat"] + b["lat"]) / 2
        ax.text(mx, my, f"{e['km']}", fontsize=6.0, color="#7c8794",
                ha="center", va="center", zorder=2)

    for nid, n in nodes.items():
        color = states.get(n["state"], {}).get("color", "#888")
        is_corr = nid in corridor_nodes
        ax.scatter(n["lng"], n["lat"],
                   s=150 if is_corr else (70 if n.get("major") else 36),
                   c=color, edgecolors=INK if is_corr else "#5b6770",
                   linewidths=1.6 if is_corr else 0.7, zorder=4,
                   marker="*" if is_corr else "o")
        ax.annotate(n["name"], (n["lng"], n["lat"]),
                    textcoords="offset points", xytext=(5, 4),
                    fontsize=7.4 if is_corr else 6.2,
                    fontweight="bold" if is_corr else "normal",
                    color=INK if is_corr else "#5b6770", zorder=5)

    legend_handles = [
        plt.Line2D([0], [0], marker="*", color="w", markerfacecolor="#bbb",
                   markeredgecolor=INK, markersize=13, label="Terminal corredor norte (O-D del paper)"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#bbb",
                   markeredgecolor="#5b6770", markersize=8, label="Estación intermedia / mayor"),
    ]
    for code, st in states.items():
        legend_handles.append(
            plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=st["color"],
                       markeredgecolor="none", markersize=9, label=st["name"])
        )
    ax.legend(handles=legend_handles, loc="lower left", fontsize=7.5, framealpha=0.92)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title("Red ferroviaria del norte de México (25 estaciones; corredor norte resaltado)",
                 fontsize=11.5)
    ax.grid(True, ls=":", color="#dde3e8", zorder=0)
    _save(fig, "fig4_red_ferroviaria.png")


# ---------------------------------------------------------------------------
# Figura 5 - Pipeline del procedimiento del simulador
# ---------------------------------------------------------------------------
def fig_pipeline():
    fig, ax = plt.subplots(figsize=(7.6, 7.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    ax.axis("off")
    stages = [
        "1. Selección de origen y destino",
        "2. Generar rutas (Dijkstra + bloqueo de aristas)",
        "3. Capa de ruteo: ranking de trayectos y mapa",
        "4. Filtrar dataset por O-D y restricciones (factibilidad)",
        "5. Alinear distance_km del pre-filtro a ruta Dijkstra",
        "6. Pre-filtro interno (11 crit., top-12 estrategias)",
        "7. Generar formaciones candidatas (1–6 vagones)",
        "8. Capa de carga: ranking de formaciones",
        "9. Cargar formación ganadora (reglas FXE/CPKC)",
        "10. Validación sobre formaciones: sensibilidad, MOORA, CV k=5",
        "11. Exportar resultados (JSON)",
    ]
    n = len(stages)
    w, h = 7.8, 0.78
    ys = [10.4 - i * (10.4 - 0.6) / (n - 1) for i in range(n)]
    for i, (text, y) in enumerate(zip(stages, ys)):
        if i in (1, 2):
            face = C_BENEFIT
        elif i in (3, 4, 5, 6, 7, 8, 9):
            face = C_COST
        elif i == 10:
            face = C_NEUTRAL
        else:
            face = INK
        _box(ax, 5, y, w, h, text, face, fontsize=9.4)
        if i < n - 1:
            _arrow(ax, 5, y - h / 2, 5, ys[i + 1] + h / 2)
    _save(fig, "fig5_pipeline_procedimiento.png")


# ---------------------------------------------------------------------------
# Figura 6 - Ci del líder por par O-D (corredor norte)
# ---------------------------------------------------------------------------
def fig_ci_pares():
    results = _load_results().get("north_corridor", [])
    if results:
        pares = [
            (
                f"{r['origin'][:4]}–{r['dest'][:4]}".replace("Ciud", "CdJ").replace("Mont", "Mty"),
                r["ci"],
                f"{r['cars']}v",
            )
            for r in results
        ]
    else:
        pares = [
            ("Chih–Laredo", 0.757, "3v"),
            ("Chih–Saltillo", 0.673, "3v"),
            ("Chih–Torreón", 0.656, "3v"),
            ("CdJ–Laredo", 0.705, "3v"),
            ("CdJ–Saltillo", 0.666, "3v"),
            ("CdJ–Torreón", 0.785, "2v"),
            ("Mty–Laredo", 0.714, "3v"),
            ("Mty–Saltillo", 0.647, "3v"),
            ("Mty–Torreón", 0.692, "3v"),
        ]
    labels = [p[0] for p in pares]
    vals = [p[1] for p in pares]
    leaders = [p[2] for p in pares]

    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    bars = ax.bar(labels, vals, color=C_BENEFIT, edgecolor=INK, linewidth=0.7)
    bars[vals.index(max(vals))].set_color(C_OK)
    bars[vals.index(min(vals))].set_color(C_COST)
    ax.set_ylim(0.5, 0.80)
    ax.set_ylabel("Coeficiente de cercanía $C_i$ del líder")
    ax.set_title("Líder de la capa de carga por par O-D (pesos fijos de formación)", fontsize=11.5)
    for rect, v, ld in zip(bars, vals, leaders):
        ax.text(rect.get_x() + rect.get_width() / 2, v + 0.004, f"{v:.3f}",
                ha="center", va="bottom", fontsize=8.2, color=INK)
        ax.text(rect.get_x() + rect.get_width() / 2, 0.512, ld,
                ha="center", va="bottom", fontsize=6.8, color="white", rotation=90)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8.5)
    ax.grid(True, axis="y", ls=":", color="#dde3e8")
    _save(fig, "fig6_ci_por_par.png")


# ---------------------------------------------------------------------------
# Figura 7 - Ejemplo Monterrey-Laredo (Top 3)
# ---------------------------------------------------------------------------
def fig_mty_laredo():
    top3 = _load_results().get("monterrey_laredo", {}).get("top3", [])
    if top3:
        colors = [C_OK, C_BENEFIT, C_NEUTRAL]
        alts = [
            (t["formation"].replace(", ", ",\n"), t["ci"], colors[i % 3])
            for i, t in enumerate(top3)
        ]
    else:
        alts = [
            ("3× Refrig.,\nBoxcar, Gondola", 0.7136, C_OK),
            ("3× Refrig.,\nHopper, Gondola", 0.7088, C_BENEFIT),
            ("3× Refrig.,\nFlatcar, Boxcar", 0.6975, C_NEUTRAL),
        ]
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    labels = [a[0] for a in alts]
    vals = [a[1] for a in alts]
    colors = [a[2] for a in alts]
    bars = ax.barh(range(len(alts)), vals, color=colors, edgecolor=INK, linewidth=0.8)
    ax.set_yticks(range(len(alts)))
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.75)
    ax.set_xlabel("Coeficiente de cercanía $C_i$")
    ax.set_title("Top 3 capa de carga: Monterrey–Laredo (80 formaciones candidatas)", fontsize=11)
    for rect, v in zip(bars, vals):
        ax.text(v + 0.008, rect.get_y() + rect.get_height() / 2, f"{v:.4f}",
                va="center", fontsize=9, color=INK)
    ax.text(0.74, 2.35, "Líder: formación de 3 vagones\n(compromiso en utilidad, tonelaje y riesgo)",
            ha="right", va="top", fontsize=7.6, color=C_NEUTRAL, style="italic")
    ax.grid(True, axis="x", ls=":", color="#dde3e8")
    _save(fig, "fig7_monterrey_laredo.png")


def main() -> None:
    print("Generando figuras del paper...")
    fig_sampieri()
    fig_arquitectura()
    fig_topsis_flow()
    fig_red()
    fig_pipeline()
    fig_ci_pares()
    fig_mty_laredo()
    print(f"Listo. Figuras en: {FIG_DIR}")


if __name__ == "__main__":
    main()
