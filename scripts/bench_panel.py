import importlib.util, pathlib, json, copy, statistics
import kaggle_environments

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load_agent(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent

lug = json.load(open(ROOT / "rivals" / "lugovoy_schedule.json"))
def make_lug_agent():
    def ag(obs, config=None):
        try:
            step = int(obs.get("step", 0) or 0)
            raw = obs.get("step", None)
            server = raw is not None
            idx = min(step + 1 if server else step, len(lug) - 1)
            base = copy.deepcopy(lug[idx] or {})
            if server and step == 0:
                opening = lug[0] or {}
                merged = [list(o) for o in (opening.get("market") or [])]
                for o in (base.get("market") or []):
                    if len(merged) >= 10: break
                    merged.append(list(o))
                base["market"] = merged[:10]
            farm = (obs.get("farms", []) or [{}])[int(obs.get("player", 0) or 0)]
            n = len(farm.get("hands", []) or [])
            hands = list(base.get("hands") or [])
            if len(hands) < n: hands += [["PASS"]] * (n - len(hands))
            base["hands"] = hands[:n]
            return {"farmer": list(base.get("farmer") or ["PASS"]), "hands": [list(h or ["PASS"]) for h in (base.get("hands") or [])], "market": [list(o) for o in (base.get("market") or [])][:10]}
        except: return {"farmer": ["PASS"], "hands": [], "market": []}
    return ag

lug_agent = make_lug_agent()

def run_match(a, b, a_name, b_name, seeds=4, center_interval=24, shop_interval=4, starter=False):
    rows = []
    wins = [0, 0]; ties = 0
    margins = []
    for seed in range(seeds):
        for swap in (False, True):
            cfg = {"episodeSteps": 720, "seed": seed, "townCenterSellInterval": center_interval, "townShopSellInterval": shop_interval}
            env = kaggle_environments.make("kaggriculture", configuration=cfg, debug=False)
            if starter:
                if swap:
                    env.run([b, a])
                    ra = env.steps[-1][1].reward; rb = env.steps[-1][0].reward
                else:
                    env.run([a, b])
                    ra = env.steps[-1][0].reward; rb = env.steps[-1][1].reward
            else:
                if swap:
                    env.run([b, a])
                    ra = env.steps[-1][1].reward; rb = env.steps[-1][0].reward
                else:
                    env.run([a, b])
                    ra = env.steps[-1][0].reward; rb = env.steps[-1][1].reward
            if ra > rb: wins[0] += 1
            elif rb > ra: wins[1] += 1
            else: ties += 1
            margins.append(ra - rb)
            rows.append((seed, swap, ra, rb))
    n = len(rows)
    avg_a = sum(r[2] for r in rows) / n
    avg_b = sum(r[3] for r in rows) / n
    avg_m = sum(margins) / n if margins else 0
    return {"wins": wins, "ties": ties, "avg_a": avg_a, "avg_b": avg_b, "avg_margin": avg_m}

def evaluate_panel(agent_fn, agent_name, seeds=2):
    c95 = load_agent(ROOT / "rivals" / "kernels" / "c95_main.py", "c95")
    c94 = load_agent(ROOT / "rivals" / "kernels" / "c94_main.py", "c94")
    v27 = load_agent(ROOT / "rivals" / "kernels" / "v27_main.py", "v27")
    
    print(f"=== BENCHMARKING {agent_name} (seeds={seeds}) ===", flush=True)
    
    res = run_match(agent_fn, "starter", agent_name, "starter", seeds=seeds, starter=True)
    print(f"vs Starter:      avg {res['avg_a']:,.0f} vs {res['avg_b']:,.0f} | Margin: {res['avg_margin']:+,.0f} | Record: {res['wins'][0]}-{res['wins'][1]}-{res['ties']}", flush=True)
    
    res = run_match(agent_fn, lug_agent, agent_name, "lug_pure", seeds=seeds)
    print(f"vs Lug Pure:     avg {res['avg_a']:,.0f} vs {res['avg_b']:,.0f} | Margin: {res['avg_margin']:+,.0f} | Record: {res['wins'][0]}-{res['wins'][1]}-{res['ties']}", flush=True)

    res = run_match(agent_fn, agent_fn, agent_name, f"{agent_name}_mirror", seeds=seeds)
    print(f"vs Mirror:       avg {res['avg_a']:,.0f} vs {res['avg_b']:,.0f} | Margin: {res['avg_margin']:+,.0f} | Record: {res['wins'][0]}-{res['wins'][1]}-{res['ties']}", flush=True)

    res = run_match(agent_fn, c95, agent_name, "c95", seeds=seeds)
    print(f"vs C95:          avg {res['avg_a']:,.0f} vs {res['avg_b']:,.0f} | Margin: {res['avg_margin']:+,.0f} | Record: {res['wins'][0]}-{res['wins'][1]}-{res['ties']}", flush=True)

    res = run_match(agent_fn, c94, agent_name, "c94", seeds=seeds)
    print(f"vs C94:          avg {res['avg_a']:,.0f} vs {res['avg_b']:,.0f} | Margin: {res['avg_margin']:+,.0f} | Record: {res['wins'][0]}-{res['wins'][1]}-{res['ties']}", flush=True)

    res = run_match(agent_fn, v27, agent_name, "v27", seeds=seeds)
    print(f"vs V27:          avg {res['avg_a']:,.0f} vs {res['avg_b']:,.0f} | Margin: {res['avg_margin']:+,.0f} | Record: {res['wins'][0]}-{res['wins'][1]}-{res['ties']}", flush=True)
    print(flush=True)

if __name__ == "__main__":
    v52 = load_agent(ROOT / "build" / "main_v52.py", "v52")
    v53 = load_agent(ROOT / "build" / "main_v53.py", "v53")
    
    print("=== H2H: v53 vs v52 (seeds=4) ===", flush=True)
    res = run_match(v53, v52, "v53", "v52", seeds=4)
    print(f"v53 vs v52:      avg {res['avg_a']:,.0f} vs {res['avg_b']:,.0f} | Margin: {res['avg_margin']:+,.0f} | Record: {res['wins'][0]}-{res['wins'][1]}-{res['ties']}", flush=True)
    print(flush=True)

    evaluate_panel(v53, "v53", seeds=2)
