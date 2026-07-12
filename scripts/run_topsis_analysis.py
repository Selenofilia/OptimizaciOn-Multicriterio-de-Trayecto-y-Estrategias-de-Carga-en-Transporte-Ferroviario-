#!/usr/bin/env python3
"""Run capa de ruteo + pre-filtro + capa de carga for paper results.

Replicates the decision pipeline in TOPSIS-Bicapa-Ferroviario-MCDM.html (handleRun).
"""
from __future__ import annotations

import heapq
import itertools
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- Pre-filtro (11 criterios, estrategias individuales) ---
CRITERIA_BENEFIT = [
    "profit_estimate_usd",
    "maintenance_score",
    "utilization_pct",
    "train_speed_kmh",
]
CRITERIA_COST = [
    "loading_time_hr",
    "unloading_time_hr",
    "fuel_cost_usd",
    "interchange_fee_usd",
    "distance_km",
    "weather_risk_index",
    "hazardous",
]
ALL_CRITERIA = CRITERIA_BENEFIT + CRITERIA_COST

# --- Capa de carga (10 criterios agregados por formación) ---
DIST_CRITERIA_BENEFIT = [
    "total_profit_usd",
    "avg_utilization_pct",
    "total_cargo_tons",
    "avg_maintenance_score",
]
DIST_CRITERIA_COST = [
    "total_op_time_hr",
    "total_fuel_cost_usd",
    "max_weather_risk",
    "hazardous_units",
    "hm_separation_penalty",
    "type_mix_penalty",
]
DIST_ALL_CRITERIA = DIST_CRITERIA_BENEFIT + DIST_CRITERIA_COST
DIST_DEFAULT_WEIGHTS = {
    "total_profit_usd": 0.22,
    "avg_utilization_pct": 0.14,
    "total_cargo_tons": 0.14,
    "avg_maintenance_score": 0.10,
    "total_op_time_hr": 0.14,
    "total_fuel_cost_usd": 0.10,
    "max_weather_risk": 0.08,
    "hazardous_units": 0.04,
    "hm_separation_penalty": 0.02,
    "type_mix_penalty": 0.02,
}
DIST_POOL_SIZE = 12
DIST_MAX_CARS = 6
DIST_MAX_CANDIDATES = 80

NORTH_ORIGINS = {"Chihuahua", "Ciudad Juarez", "Monterrey"}
NORTH_DESTS = {"Laredo", "Torreon", "Saltillo"}


def load_json(name: str):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def normalize_weights(weights: list[float]) -> list[float]:
    s = sum(weights) or 1.0
    return [w / s for w in weights]


def topsis_with_criteria(
    alternatives: list[dict],
    criteria_keys: list[str],
    benefit_keys: list[str],
    weights: list[float],
) -> list[tuple[float, dict]]:
    m = len(alternatives)
    if m == 0:
        return []
    benefit_set = set(benefit_keys)
    matrix = [[float(a[c]) for c in criteria_keys] for a in alternatives]
    denom = []
    for j in range(len(criteria_keys)):
        s = sum(matrix[i][j] ** 2 for i in range(m))
        denom.append(math.sqrt(s) or 1.0)
    norm = [[matrix[i][j] / denom[j] for j in range(len(criteria_keys))] for i in range(m)]
    weighted = [[norm[i][j] * weights[j] for j in range(len(criteria_keys))] for i in range(m)]
    ideal_best = []
    ideal_worst = []
    for j, c in enumerate(criteria_keys):
        col = [weighted[i][j] for i in range(m)]
        if c in benefit_set:
            ideal_best.append(max(col))
            ideal_worst.append(min(col))
        else:
            ideal_best.append(min(col))
            ideal_worst.append(max(col))
    scores = []
    for i in range(m):
        sp = math.sqrt(sum((weighted[i][j] - ideal_best[j]) ** 2 for j in range(len(criteria_keys))))
        sm = math.sqrt(sum((weighted[i][j] - ideal_worst[j]) ** 2 for j in range(len(criteria_keys))))
        ci = sm / (sp + sm + 1e-12)
        scores.append((ci, alternatives[i]))
    scores.sort(key=lambda x: -x[0])
    return scores


def build_graph(cities: dict) -> dict[str, list[tuple[str, float]]]:
    adj: dict[str, list[tuple[str, float]]] = {}
    for edge in cities["edges"]:
        a, b, w = edge["from"], edge["to"], float(edge["km"])
        adj.setdefault(a, []).append((b, w))
        adj.setdefault(b, []).append((a, w))
    return adj


def dijkstra(adj: dict[str, list[tuple[str, float]]], start: str, end: str) -> tuple[list[str], float]:
    dist = {start: 0.0}
    prev: dict[str, str | None] = {start: None}
    heap = [(0.0, start)]
    visited: set[str] = set()
    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == end:
            break
        for v, w in adj.get(u, []):
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    if end not in dist or dist[end] == math.inf:
        return [], math.inf
    path = []
    cur: str | None = end
    while cur:
        path.insert(0, cur)
        cur = prev.get(cur)
    return path, dist[end]


def align_alternatives_to_route(alternatives: list[dict], route_dist_km: float | None) -> list[dict]:
    if route_dist_km is None or not math.isfinite(route_dist_km) or not alternatives:
        return alternatives
    out = []
    for r in alternatives:
        row = dict(r)
        old_dist = float(row.get("distance_km") or 0)
        if old_dist <= 0:
            row["distance_km"] = route_dist_km
        elif abs(old_dist - route_dist_km) >= 0.01:
            ratio = route_dist_km / old_dist
            row["distance_km"] = route_dist_km
            fuel = row.get("fuel_cost_usd")
            if fuel is not None:
                row["fuel_cost_usd"] = float(fuel) * ratio
        out.append(row)
    return out


def hm_consecutive_penalty(strategies: list[dict]) -> int:
    pen = 0
    for i in range(len(strategies) - 1):
        if int(strategies[i].get("hazardous") or 0) == 1 and int(strategies[i + 1].get("hazardous") or 0) == 1:
            pen += 1
    return pen


def permute_strategies(arr: list[dict]) -> list[list[dict]]:
    if len(arr) <= 1:
        return [arr[:]]
    out = []
    for i, item in enumerate(arr):
        rest = arr[:i] + arr[i + 1 :]
        for p in permute_strategies(rest):
            out.append([item] + p)
    return out


def best_cargo_order(strategies: list[dict]) -> list[dict]:
    if len(strategies) <= 1:
        return strategies[:]
    if len(strategies) <= 6:
        best = strategies[:]
        best_pen = hm_consecutive_penalty(best)
        for p in permute_strategies(strategies):
            pen = hm_consecutive_penalty(p)
            if pen < best_pen:
                best_pen = pen
                best = p
        return best
    haz = [s for s in strategies if int(s.get("hazardous") or 0) == 1]
    safe = [s for s in strategies if int(s.get("hazardous") or 0) != 1]
    ordered = []
    hi = si = 0
    while hi < len(haz) or si < len(safe):
        if si < len(safe):
            ordered.append(safe[si])
            si += 1
        if hi < len(haz):
            ordered.append(haz[hi])
            hi += 1
    return ordered


def build_distribution_metrics(strategies: list[dict]) -> dict:
    n = len(strategies)
    total_profit = total_cargo = total_load = total_unload = total_fuel = 0.0
    util_sum = maint_sum = max_weather = 0.0
    haz = 0
    for s in strategies:
        total_profit += float(s.get("profit_estimate_usd") or 0)
        total_cargo += float(s.get("cargo_weight_tons") or 0)
        total_load += float(s.get("loading_time_hr") or 0)
        total_unload += float(s.get("unloading_time_hr") or 0)
        total_fuel += float(s.get("fuel_cost_usd") or 0)
        util_sum += float(s.get("utilization_pct") or 0)
        maint_sum += float(s.get("maintenance_score") or 0)
        max_weather = max(max_weather, float(s.get("weather_risk_index") or 0))
        if int(s.get("hazardous") or 0) == 1:
            haz += 1
    type_set = {s["wagon_type"] for s in strategies}
    return {
        "total_profit_usd": total_profit,
        "avg_utilization_pct": util_sum / n,
        "total_cargo_tons": total_cargo,
        "avg_maintenance_score": maint_sum / n,
        "total_op_time_hr": total_load + total_unload,
        "total_fuel_cost_usd": total_fuel,
        "max_weather_risk": max_weather,
        "hazardous_units": haz,
        "hm_separation_penalty": hm_consecutive_penalty(strategies),
        "type_mix_penalty": max(0, len(type_set) - 2) * 5,
        "cargo_count": n,
    }


def find_slot_for_strategy_unused(alt: dict, used_slots: set[int], slots: list[dict]) -> dict | None:
    def free(s: dict | None) -> bool:
        return bool(s and not s.get("is_locomotive") and s["slot"] not in used_slots)

    if alt.get("catalog_slot"):
        by_slot = next((s for s in slots if s.get("slot") == alt["catalog_slot"]), None)
        if free(by_slot):
            return by_slot
    if alt.get("car_number"):
        by_car = next((s for s in slots if s.get("car_number") == alt["car_number"]), None)
        if free(by_car):
            return by_car
    pool = [
        s
        for s in slots
        if not s.get("is_locomotive") and s.get("wagon_type") == alt.get("wagon_type") and s["slot"] not in used_slots
    ]
    if alt.get("owner_railroad"):
        owned = next((s for s in pool if s.get("owner_railroad") == alt["owner_railroad"]), None)
        if owned:
            return owned
    return pool[0] if pool else None


def can_resolve_distribution_slots(strategies: list[dict], slots: list[dict]) -> bool:
    used: set[int] = set()
    for s in strategies:
        slot = find_slot_for_strategy_unused(s, used, slots)
        if not slot:
            return False
        used.add(slot["slot"])
    return True


def unique_strategy_pool(ranked: list[tuple[float, dict]]) -> list[dict]:
    seen: set[str] = set()
    pool = []
    for _, alt in ranked:
        key = alt.get("car_number") or alt.get("wagon_id")
        if key in seen:
            continue
        seen.add(key)
        pool.append(alt)
    return pool[:DIST_POOL_SIZE]


def generate_distribution_candidates(ranked_alts: list[tuple[float, dict]], slots: list[dict]) -> list[dict]:
    pool = unique_strategy_pool(ranked_alts)
    candidates: list[dict] = []
    seen: set[str] = set()

    def try_add(strategies: list[dict], desc: str | None = None) -> None:
        if not strategies or len(strategies) > DIST_MAX_CARS:
            return
        if not can_resolve_distribution_slots(strategies, slots):
            return
        ids = "+".join(sorted(s["wagon_id"] for s in strategies))
        if ids in seen:
            return
        order = best_cargo_order(strategies)
        metrics = build_distribution_metrics(order)
        types = " + ".join(dict.fromkeys(s["wagon_type"] for s in order))
        seen.add(ids)
        candidates.append(
            {
                "dist_id": f"FD{len(candidates) + 1}",
                "label": desc or (f"{len(order)} vagón(es) · {types}"),
                "strategies": order,
                "wagon_ids": [s["wagon_id"] for s in order],
                **metrics,
            }
        )

    for s in pool:
        try_add([s], f"1× {s['wagon_type']}")

    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            try_add([pool[i], pool[j]], f"2× {pool[i]['wagon_type']} + {pool[j]['wagon_type']}")

    top8 = pool[:8]
    for combo in itertools.combinations(range(len(top8)), 3):
        try_add([top8[i] for i in combo], "3× mix")

    top6 = pool[:6]
    for combo in itertools.combinations(range(len(top6)), 4):
        try_add([top6[i] for i in combo], "4× mix")

    for combo in itertools.combinations(range(min(6, len(pool))), 5):
        idx = list(combo)
        for m in range(max(idx) + 1, len(pool)):
            try_add([pool[i] for i in idx] + [pool[m]], "5× mix")

    for combo in itertools.combinations(range(min(5, len(pool))), 6):
        try_add([pool[i] for i in combo], "6× mix")

    return candidates[:DIST_MAX_CANDIDATES]


def dist_weights() -> list[float]:
    raw = [DIST_DEFAULT_WEIGHTS.get(k, 1 / len(DIST_ALL_CRITERIA)) for k in DIST_ALL_CRITERIA]
    return normalize_weights(raw)


def format_formation(dist: dict) -> str:
    types = [s["wagon_type"] for s in dist["strategies"]]
    cargos = [s.get("cargo_type") or s.get("specific_material", "") for s in dist["strategies"]]
    if len(dist["strategies"]) == 1:
        return f"{types[0]} / {cargos[0]}"
    return f"{len(dist['strategies'])}× ({', '.join(types)})"


def run_pipeline(
    origin: str,
    dest: str,
    dataset: list[dict],
    slug_map: dict[str, str],
    adj: dict[str, list[tuple[str, float]]],
    slots: list[dict],
    prefilter_weights: list[float] | None = None,
) -> dict:
    alts = [d for d in dataset if d["origin"] == origin and d["destination"] == dest and d.get("capacity_feasible")]
    start = slug_map.get(origin)
    end = slug_map.get(dest)
    route_dist = None
    if start and end:
        _, route_dist = dijkstra(adj, start, end)
        if not math.isfinite(route_dist):
            route_dist = None
    aligned = align_alternatives_to_route(alts, route_dist)
    pw = prefilter_weights or normalize_weights([1 / len(ALL_CRITERIA)] * len(ALL_CRITERIA))
    pool_ranked = topsis_with_criteria(aligned, ALL_CRITERIA, CRITERIA_BENEFIT, pw)
    candidates = generate_distribution_candidates(pool_ranked, slots)
    dw = dist_weights()
    dist_ranked = topsis_with_criteria(candidates, DIST_ALL_CRITERIA, DIST_CRITERIA_BENEFIT, dw)
    return {
        "origin": origin,
        "dest": dest,
        "n_factibles": len(alts),
        "n_candidates": len(candidates),
        "route_dist_km": route_dist,
        "pool_ranked": pool_ranked,
        "dist_ranked": dist_ranked,
        "candidates": candidates,
        "dist_weights": dw,
    }


def sensitivity_distribution(candidates: list[dict], base_weights: list[float]) -> tuple[float, str | None]:
    if not candidates:
        return 0.0, None
    base_top = topsis_with_criteria(candidates, DIST_ALL_CRITERIA, DIST_CRITERIA_BENEFIT, base_weights)[0]
    baseline = base_top[1]["dist_id"]
    changed = 0
    total = 0
    for j in range(len(DIST_ALL_CRITERIA)):
        for delta in (-0.2, 0.2):
            w2 = base_weights.copy()
            w2[j] = max(0.01, w2[j] * (1 + delta))
            w2 = normalize_weights(w2)
            leader = topsis_with_criteria(candidates, DIST_ALL_CRITERIA, DIST_CRITERIA_BENEFIT, w2)[0][1]["dist_id"]
            total += 1
            if leader != baseline:
                changed += 1
    return 1 - changed / total, baseline


def cv_k5_distribution(candidates: list[dict], weights: list[float]) -> tuple[int, str | None]:
    k = 5
    if len(candidates) < k:
        return 0, None
    global_top = topsis_with_criteria(candidates, DIST_ALL_CRITERIA, DIST_CRITERIA_BENEFIT, weights)[0][1]["dist_id"]
    ordered = sorted(candidates, key=lambda c: c["dist_id"])
    fold_size = len(ordered) // k
    matches = 0
    for f in range(k):
        start = f * fold_size
        end = len(ordered) if f == k - 1 else start + fold_size
        train = ordered[:start] + ordered[end:]
        train_top = topsis_with_criteria(train, DIST_ALL_CRITERIA, DIST_CRITERIA_BENEFIT, weights)[0][1]["dist_id"]
        if train_top == global_top:
            matches += 1
    return matches, global_top


def north_summary(dataset: list[dict], slug_map: dict, adj: dict, slots: list[dict]) -> list[dict]:
    rows = []
    for o in sorted(NORTH_ORIGINS):
        for d in sorted(NORTH_DESTS):
            res = run_pipeline(o, d, dataset, slug_map, adj, slots)
            if not res["n_factibles"]:
                continue
            leader = res["dist_ranked"][0] if res["dist_ranked"] else None
            rows.append(
                {
                    "origin": o,
                    "dest": d,
                    "n": res["n_factibles"],
                    "n_candidates": res["n_candidates"],
                    "leader": format_formation(leader[1]) if leader else "—",
                    "ci": leader[0] if leader else 0,
                    "dist_id": leader[1]["dist_id"] if leader else None,
                    "cars": leader[1]["cargo_count"] if leader else 0,
                    "label": leader[1]["label"] if leader else "",
                }
            )
    return rows


def export_results_json(path: Path, north_rows: list[dict], mty: dict) -> None:
    payload = {
        "model": "capa de ruteo + pre-filtro + capa de carga",
        "north_corridor": north_rows,
        "monterrey_laredo": {
            "top8": [
                {
                    "dist_id": r[1]["dist_id"],
                    "label": r[1]["label"],
                    "formation": format_formation(r[1]),
                    "ci": round(r[0], 4),
                    "cars": r[1]["cargo_count"],
                }
                for r in mty["dist_ranked"][:8]
            ],
            "n_candidates": mty["n_candidates"],
            "sensitivity_stability": mty.get("sensitivity_stability"),
            "cv_concordance": mty.get("cv_concordance"),
        },
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    dataset = load_json("dataset.json")
    cities = load_json("cities.json")
    wagon_map = load_json("wagon_map.json")
    slug_map = cities["slug_map"]
    adj = build_graph(cities)
    slots = wagon_map["slots"]
    dw = dist_weights()

    print("=== Capa de carga — corredor norte ===\n")
    north_rows = north_summary(dataset, slug_map, adj, slots)
    wagon_freq = Counter()
    multi_count = 0
    for row in north_rows:
        if row["cars"] > 1:
            multi_count += 1
        wt = row["leader"].split("/")[0].strip() if "/" in row["leader"] else row["leader"]
        if "×" not in wt:
            wagon_freq[wt.split()[0] if wt else ""] += 1
        print(
            f"{row['origin']} -> {row['dest']}: n={row['n']} candidatos={row['n_candidates']} "
            f"lider={row['leader']} Ci={row['ci']:.3f} ({row['cars']} vagones)"
        )
    print(f"\nFormaciones multi-vagón como líder: {multi_count}/{len(north_rows)}")
    print("freq líderes (vagón único):", dict(wagon_freq))

    mty = run_pipeline("Monterrey", "Laredo", dataset, slug_map, adj, slots)
    print(f"\n=== Monterrey -> Laredo (detalle) ===")
    print(f"Estrategias factibles: {mty['n_factibles']}")
    print(f"Formaciones candidatas: {mty['n_candidates']}")
    print("Top 8 capa de carga:")
    for i, (ci, dist) in enumerate(mty["dist_ranked"][:8], 1):
        print(f"  #{i} {dist['dist_id']} {dist['label']} Ci={ci:.4f} · {format_formation(dist)}")

    stab, baseline = sensitivity_distribution(mty["candidates"], dw)
    mty["sensitivity_stability"] = stab
    print(f"\nSensibilidad capa de carga (±20%): estabilidad={stab:.2f} líder={baseline}")

    agree, cv_top = cv_k5_distribution(mty["candidates"], dw)
    mty["cv_concordance"] = agree
    print(f"CV k=5 (particiones determinísticas por dist_id): {agree}/5")

    out = ROOT / "data" / "paper_results.json"
    export_results_json(out, north_rows, mty)
    print(f"\nResultados exportados: {out}")


if __name__ == "__main__":
    main()
