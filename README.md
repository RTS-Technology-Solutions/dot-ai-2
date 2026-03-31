# Dot AI 2.0

## Why does this exist?

Concepts like natural selection, emergent behavior, and genetic optimization are easy to define but hard to intuit. Reading about them builds vocabulary. Watching them happen builds understanding. This simulator exists to make those invisible dynamics visible — to give you a system where you can *see* why diversity outcompetes monocultures, why utility functions produce richer behavior than hardcoded rules, and why evolution reliably finds solutions no programmer would have written.

It builds on Dot AI 1.0 (pathfinding with a genetic algorithm and Q-learning), but where that project had dots chasing a goal, this one has dots *surviving*. Survival turns out to be a much richer problem — there is no correct answer, and the fitness landscape keeps shifting as the population changes.

---

## Why an Ecosystem and Not Just a Pathfinder?

A goal-and-reach pathfinder has a known optimal solution. The simulation converges on it, you see it work, and learning stops. An ecosystem has no correct answer — strategies interact with each other, not just with the environment. Aggressive dots work until prey populations collapse. Passive dots thrive until predators evolve. The simulation does not converge — it adapts, which is what actually happens in nature and in real optimization problems.

The ecosystem model also creates genuinely difficult tradeoffs that a pathfinder cannot:
- Dots allocate a fixed DNA budget across competing abilities — speed, vision, combat, reproduction
- Decisions happen under uncertainty with incomplete environmental information
- What succeeds at population 3 fails at population 20, because the selection landscape changes

---

## Architecture: Why It Is Designed This Way

### Why a Gene Budget?

Each dot gets 100 DNA points to distribute across its abilities. The scarcity is the point — without a constraint, every dot would max everything and there would be nothing to select on. The budget is what forces specialization: a dot that invests heavily in attack cannot also invest in reproduction. That trade-off is what makes natural selection meaningful.

**Brain Genes** — why they exist: cognitive capacity must be earned. A dot that cannot build memory restarts fresh every frame with no accumulated associations.
- `brain_memory` — without memory capacity, there is no substrate for learned patterns
- `brain_sense_slots` — limits simultaneous inputs; a cap here means the brain must prioritize what it notices
- `brain_action_slots` — limits candidate actions evaluated per frame; forces triage

**Sense Genes** — why they exist: a dot that cannot perceive its environment cannot respond to it. Perception range is reaction time. FOV is blind-spot coverage. Omnidirectional detection is threat awareness that does not require facing the threat.
- `vision_distance` — directional range; more range means more time between detection and arrival
- `vision_fov` — cone angle; high points approach 360° and eliminate directional blind spots
- `dot_detection` — omnidirectional; detects threats regardless of facing direction
- `food_detection` — omnidirectional scent-analog; finds food outside line of sight
- `nearby_dot_density` — area-count sensor; required for crowding-aware reproduction decisions
- `dna_strength_detection` — distinguishes easy prey from dangerous opponents; disabled by default because it must be *evolved* to be valued

**Action Genes** — why they exist: every behavior costs points to unlock, so every behavior must justify its cost against what else those points could buy.
- `movement_speed` — faster movement improves pursuit and escape, but points spent here cannot go elsewhere
- `movement_max_energy` — a higher energy ceiling extends foraging range before starvation forces a return
- `attack` — enables combat; produces high food reward on success, costs energy on miss
- `defend` — reduces incoming damage while stationary; trade-off between durability and action opportunity cost
- `replicate` — must be evolved; a dot that does not invest here dies with its DNA

---

### Why Utility-Based AI and Not Hardcoded Rules?

Hardcoded rules ("if hungry, seek food; else attack") fail when multiple conditions are simultaneously true, because there is no principled way to resolve them. A utility function assigns a score to every possible action and picks the highest — the same code produces different decisions depending on context:

- A dot at 10% health surrounded by enemies will not attack, because defend utility exceeds attack utility
- A dot that is full and healthy will not eat, because reproduction utility scores higher than food-seeking
- A dot with nothing in range will not idle, because explore always scores above the idle floor

The utility weights and thresholds that govern this are all configurable in [`configs/simulation_config.py`](configs/simulation_config.py).

---

### Why Two Reproduction Modes?

**Asexual (cloning, 80% energy cost):** Preserves a proven strategy exactly. The high energy cost is why it is the fallback — a dot spending 80% of its reserves to clone itself needs to already be in a strong position.

**Sexual (crossover, 40% energy each):** Creates novel DNA combinations that neither parent carries. The lower individual cost is why dots prefer it when mates are available — but it requires finding a compatible partner, which creates indirect selection pressure on sense genes and population density behavior.

Without both modes: asexual-only locks in whatever strategy currently exists; sexual-only fails when populations are too sparse to pair. Both modes co-existing is what produces the hybrid strategies you see emerge.

---

### Why Do Dead Dots Become Food?

A predator ecosystem without a nutrition return loop collapses — attackers burn energy to kill but receive nothing. By converting corpses to food, combat becomes a viable energy strategy rather than a pure cost. Stronger DNA produces more nutritious corpses (gene points translate directly to food energy), which creates selection pressure toward hunting high-value targets and avoiding attacks on weak ones.

---

## Running It

**Install:**
```bash
pip install -r requirements.txt
```

**Run:**
```bash
python main.py
```

**Optional — live metrics dashboard (separate terminal):**
```bash
python monitor.py
```

**Controls:**
- `SPACE` — pause/resume
- `ESC` — quit

---

## Configuring the Experiment

Every tunable constant lives in [`configs/simulation_config.py`](configs/simulation_config.py) as documented dataclass fields. Switch presets in `main.py`:

```python
set_config(PROFILES["high_aggression"])   # or "rapid_evolution", "default"
```

Override individual values without creating a full profile:
```python
set_config(SimulationConfig(
    behavior=BehaviorConfig(attack_multiplier=6.0, seek_mate_multiplier=1.0)
))
```

See [`configs/profiles.py`](configs/profiles.py) for the three built-in presets and instructions for adding your own.

---

## Data & Analysis

Every run logs automatically to `logs/YYYYMMDD_HHMMSS/`:

| File | Why it exists |
|---|---|
| `events.jsonl` | Immutable event stream — every birth, death, attack; lets you reconstruct any moment |
| `colony_metrics.jsonl` | 1-second population snapshots — tracks colony-level trends over time |
| `generation_summary.csv` | Per-generation roll-up — the unit of evolutionary comparison |
| `dot_lifetimes.csv` | Per-dot record — maps individual strategies to survival outcomes |

See [`METRICS_LOGGING_GUIDE.md`](METRICS_LOGGING_GUIDE.md) for analysis examples.

---

## Project Structure

```
dot-ai-2/
├── main.py                   # Entry point + profile selection
├── configs/
│   ├── simulation_config.py  # All tunable constants as typed dataclasses
│   ├── profiles.py           # Named experiment presets
│   └── __init__.py           # Singleton get_config / set_config
├── core/
│   ├── dna.py                # Gene budget system, defaults, crossover logic
│   ├── dot.py                # Utility-based AI agent
│   ├── simulation.py         # World engine and evolutionary loop
│   ├── actions.py            # Combat and reproduction mechanics
│   ├── senses.py             # Vision cone and detection systems
│   ├── brain.py              # Age-gated cognition and memory
│   ├── resources.py          # Energy, health, hunger
│   ├── food.py               # Food entity
│   └── metrics_logger.py     # Structured data logging
├── renderers/
│   └── pygame_renderer.py    # Visualization (isolated from logic)
├── analysis/                 # Post-run analysis scripts
└── logs/                     # Auto-created, one folder per session
```

---

*Built with Python and Pygame. No external ML frameworks — the intelligence emerges from the rules, not from a pre-trained model.*
