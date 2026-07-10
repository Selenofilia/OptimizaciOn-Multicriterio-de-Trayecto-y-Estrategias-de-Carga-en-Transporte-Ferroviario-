#!/usr/bin/env python3
"""Generate PNG figures embedded in Paper 1 (TOPSIS railway cargo).

Only the four figures listed in PAPER_FIGURES are produced by default.
Color is used sparingly: grayscale flowcharts and charts; the network map
uses state colors and highlights corredor-norte O-D terminals.
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

# Monochrome base; ACCENT only where it encodes study O-D terminals on the map.
INK = "#1f2a37"
GRAY = "#9aa5b1"
GRAY_LIGHT = "#d8dee4"
ACCENT = "#1f2a37"

PAPER_FIGURES = (
    "fig2_arquitectura_2capas.png",
    "fig4_red_ferroviaria.png",
    "fig5_pipeline_procedimiento.png",
    "fig6_ci_por_par.png",
    "fig7_monterrey_laredo.png",
)


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


def _box(ax, x, y, w, h, text, fill=INK, fontcolor="white", fontsize=10, lw=1.2):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=lw,
        edgecolor=INK,
        facecolor=fill,
    )
    ax.add_patch(patch)
    ax.text(
        x, y, text, ha="center", va="center", color=fontcolor,
        fontsize=fontsize, wrap=True, zorder=5,
    )
    return patch


def _box_outline(ax, x, y, w, h, text, fontsize=10):
    return _box(ax, x, y, w, h, text, fill="white", fontcolor=INK, fontsize=fontsize)


def _arrow(ax, x1, y1, x2, y2, lw=1.4, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle=style, mutation_scale=12, linewidth=lw,
            color=INK, shrinkA=2, shrinkB=2,
        )
    )


def _save(fig, name):
    out = FIG_DIR / name
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  figura: {out.relative_to(ROOT)}")


def fig_arquitectura():
    """Fig. 1 — Marco bicapa (único diagrama de flujo del paper)."""
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.2)
    ax.axis("off")

    _box(ax, 5, 7.6, 5.0, 0.7, "Origen–Destino (decisor)", fontsize=10)

    for x0, title in ((0.4, "Capa física"), (5.4, "Capa comercial")):
        ax.add_patch(FancyBboxPatch(
            (x0, 2.2), 4.2, 4.35, boxstyle="round,pad=0.04,rounding_size=0.08",
            linewidth=0.9, edgecolor=GRAY, facecolor="white", linestyle="--",
        ))
        ax.text(x0 + 2.1, 6.35, title, ha="center", color=INK, fontsize=9.5, fontweight="bold")

    cx_l, cx_r = 2.5, 7.5
    _box_outline(ax, cx_l, 5.55, 3.3, 0.9, "Red ferroviaria\nDijkstra (≤5 rutas)", fontsize=9)
    _box_outline(ax, cx_l, 4.35, 3.3, 0.8, "Capa de ruteo TOPSIS\n(6 criterios)", fontsize=9)
    _box_outline(ax, cx_r, 5.55, 3.3, 0.9, "Dataset filtrado\n(factibilidad, top-12)", fontsize=8.8)
    _box_outline(ax, cx_r, 4.35, 3.3, 0.8, "Capa de carga TOPSIS\n(1–6 vagones)", fontsize=8.8)
    _box_outline(ax, cx_l, 3.05, 3.3, 0.7, "Ruta ganadora", fontsize=9)
    _box_outline(ax, cx_r, 3.05, 3.3, 0.7, "Formación ganadora", fontsize=9)
    _box(ax, 5, 1.45, 8.4, 0.65,
         "Validación: sensibilidad ±20 % · MOORA · CV k = 5", fontsize=8.5)

    _arrow(ax, 4.2, 7.25, cx_l, 6.05)
    _arrow(ax, 5.8, 7.25, cx_r, 6.05)
    for cx in (cx_l, cx_r):
        _arrow(ax, cx, 5.08, cx, 4.78)
        _arrow(ax, cx, 3.93, cx, 3.43)
        _arrow(ax, cx, 2.68, cx, 1.82)
    _arrow(ax, 3.55, 3.05, 6.45, 3.05, lw=1.0, style="<->")
    _save(fig, "fig2_arquitectura_2capas.png")


def fig_red():
    """Fig. 2 — Red ferroviaria con color por estado (terminales O-D resaltadas)."""
    data = json.loads((ROOT / "data" / "cities.json").read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in data["nodes"]}
    edges = data["edges"]
    states = data["states"]

    corridor_nodes = {
        "chihuahua", "ciudad_juarez", "monterrey", "laredo", "torreon", "saltillo",
    }

    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    for e in edges:
        a, b = nodes[e["from"]], nodes[e["to"]]
        ax.plot(
            [a["lng"], b["lng"]], [a["lat"], b["lat"]],
            color="#b7c2cc", lw=1.2, zorder=1,
        )
        mx, my = (a["lng"] + b["lng"]) / 2, (a["lat"] + b["lat"]) / 2
        ax.text(
            mx, my, f"{e['km']}", fontsize=6.0, color="#7c8794",
            ha="center", va="center", zorder=2,
        )

    for nid, n in nodes.items():
        color = states.get(n["state"], {}).get("color", "#888")
        is_corr = nid in corridor_nodes
        ax.scatter(
            n["lng"], n["lat"],
            s=150 if is_corr else (70 if n.get("major") else 36),
            c=color,
            edgecolors=INK if is_corr else "#5b6770",
            linewidths=1.6 if is_corr else 0.7,
            zorder=4,
            marker="*" if is_corr else "o",
        )
        ax.annotate(
            n["name"], (n["lng"], n["lat"]),
            textcoords="offset points", xytext=(5, 4),
            fontsize=7.4 if is_corr else 6.2,
            fontweight="bold" if is_corr else "normal",
            color=INK if is_corr else "#5b6770",
            zorder=5,
        )

    legend_handles = [
        plt.Line2D(
            [0], [0], marker="*", color="w", markerfacecolor="#bbb",
            markeredgecolor=INK, markersize=13,
            label="Terminal corredor norte (O-D del paper)",
        ),
        plt.Line2D(
            [0], [0], marker="o", color="w", markerfacecolor="#bbb",
            markeredgecolor="#5b6770", markersize=8,
            label="Estación intermedia / mayor",
        ),
    ]
    for _code, st in states.items():
        legend_handles.append(
            plt.Line2D(
                [0], [0], marker="o", color="w", markerfacecolor=st["color"],
                markeredgecolor="none", markersize=9, label=st["name"],
            )
        )
    ax.legend(handles=legend_handles, loc="lower left", fontsize=7.5, framealpha=0.92)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.set_title(
        "Red ferroviaria del norte de México (25 estaciones; corredor norte resaltado)",
        fontsize=11.5,
    )
    ax.grid(True, ls=":", color="#dde3e8", zorder=0)
    _save(fig, "fig4_red_ferroviaria.png")


def fig_ci_pares():
    """Fig. 3 — Ranking por par O-D (monocromo)."""
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
            ("Chih–Laredo", 0.757, "3v"), ("Chih–Saltillo", 0.673, "3v"),
            ("Chih–Torreón", 0.656, "3v"), ("CdJ–Laredo", 0.705, "3v"),
            ("CdJ–Saltillo", 0.666, "3v"), ("CdJ–Torreón", 0.785, "2v"),
            ("Mty–Laredo", 0.714, "3v"), ("Mty–Saltillo", 0.647, "3v"),
            ("Mty–Torreón", 0.692, "3v"),
        ]

    labels = [p[0] for p in pares]
    vals = [p[1] for p in pares]
    leaders = [p[2] for p in pares]

    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    bars = ax.bar(labels, vals, color="white", edgecolor=INK, linewidth=0.9)
    ax.set_ylim(0.5, 0.80)
    ax.set_ylabel("Coeficiente de cercanía $C_i$ del líder")
    ax.set_title("Líder de la capa de carga por par O-D", fontsize=11)
    for rect, v, ld in zip(bars, vals, leaders):
        ax.text(rect.get_x() + rect.get_width() / 2, v + 0.004, f"{v:.3f}",
                ha="center", va="bottom", fontsize=8, color=INK)
        ax.text(rect.get_x() + rect.get_width() / 2, 0.512, ld,
                ha="center", va="bottom", fontsize=6.5, color=INK, rotation=90)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8.5)
    ax.grid(True, axis="y", ls=":", color=GRAY_LIGHT)
    _save(fig, "fig6_ci_por_par.png")


def fig_pipeline():
    """Fig. 3 — Pipeline operativo (metodología)."""
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    steps = [
        (5, 9.2, "1. Origen–Destino"),
        (5, 8.0, "2. Dijkstra + capa de ruteo"),
        (5, 6.8, "3. Filtro factibilidad"),
        (5, 5.6, "4. Pre-filtro top-12"),
        (5, 4.4, "5. Formaciones 1–6 vagones"),
        (5, 3.2, "6. Capa de carga TOPSIS"),
        (5, 2.0, "7. Validación (MOORA, CV, sens.)"),
        (5, 0.8, "8. Despacho / exportación JSON"),
    ]
    for x, y, label in steps:
        _box_outline(ax, x, y, 6.8, 0.72, label, fontsize=9.2)
    for i in range(len(steps) - 1):
        _arrow(ax, 5, steps[i][1] - 0.38, 5, steps[i + 1][1] + 0.38)
    ax.set_title("Pipeline del simulador TOPSIS bicapa", fontsize=11.5)
    _save(fig, "fig5_pipeline_procedimiento.png")


def fig_monterrey_laredo():
    """Fig. — Top 3 formaciones Monterrey–Laredo."""
    top3 = _load_results().get("monterrey_laredo", {}).get("top3", [])
    if not top3:
        top3 = [
            {"formation": "3× (Refrigerated, Boxcar, Gondola)", "ci": 0.7136},
            {"formation": "3× (Refrigerated, Hopper, Gondola)", "ci": 0.7088},
            {"formation": "3× (Refrigerated, Flatcar, Boxcar)", "ci": 0.6975},
        ]
    labels = [f"#{i+1}" for i in range(len(top3))]
    vals = [t["ci"] for t in top3]
    formations = [t.get("formation", "").replace("3× ", "") for t in top3]

    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    bars = ax.bar(labels, vals, color="white", edgecolor=INK, linewidth=0.9)
    ax.set_ylim(0.68, 0.73)
    ax.set_ylabel("Coeficiente $C_i$")
    ax.set_title("Top 3 — capa de carga (Monterrey–Laredo)", fontsize=11)
    for rect, v, form in zip(bars, vals, formations):
        ax.text(rect.get_x() + rect.get_width() / 2, v + 0.0015, f"{v:.4f}",
                ha="center", va="bottom", fontsize=8.5, color=INK)
        ax.text(rect.get_x() + rect.get_width() / 2, 0.6815, form,
                ha="center", va="bottom", fontsize=6.2, color=INK, rotation=0)
    ax.grid(True, axis="y", ls=":", color=GRAY_LIGHT)
    _save(fig, "fig7_monterrey_laredo.png")


def main() -> None:
    print("Generando figuras del paper...")
    fig_arquitectura()
    fig_red()
    fig_pipeline()
    fig_ci_pares()
    fig_monterrey_laredo()
    print("  (efectos principales factorial: scripts/run_factorial_experiment.py)")
    print(f"Listo. Figuras en: {FIG_DIR}")


if __name__ == "__main__":
    main()
