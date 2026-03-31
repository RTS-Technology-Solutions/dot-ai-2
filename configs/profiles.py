"""
configs/profiles.py — Named Simulation Presets
================================================
Add or edit profiles here, then load one in main.py:

    from configs.profiles import PROFILES
    set_config(PROFILES["high_aggression"])

Each profile is a complete SimulationConfig with ONLY the fields you want
to change from the defaults — thanks to dataclass field(default_factory=...),
every unspecified field falls back to the baseline.
"""

from .simulation_config import (
    SimulationConfig,
    WorldConfig,
    BrainConfig,
    DNAConfig,
    DNAGeneDefaults,
    SensesConfig,
    BehaviorConfig,
)


# ---------------------------------------------------------------------------
# "default" — exact reproduction of the original hardcoded values.
# Use this as a regression baseline to confirm nothing changed after wiring.
# ---------------------------------------------------------------------------
_default = SimulationConfig()        # All defaults already match originals


# ---------------------------------------------------------------------------
# "high_aggression"
# Dots attack sooner, stay in the fight longer, and move faster.
# Expect: shorter generation lifetimes, more combat kills, arms-race DNA.
# ---------------------------------------------------------------------------
_high_aggression = SimulationConfig(
    behavior=BehaviorConfig(
        # Lower hunger bar needed before attacking (was 0.3 → now 0.15)
        attack_hunt_threshold=0.15,
        # Stronger incentive to attack (was 3.0 → now 5.0)
        attack_multiplier=5.0,
        # Weaker low-health retreat penalty → fight even when hurt
        attack_low_health_penalty_critical=0.3,    # was 0.1
        attack_low_health_penalty_moderate=0.8,    # was 0.5
        # Faster base movement — aggressive pursuit
        movement_speed_base=65.0,                  # was 50.0
        # Lower mating drive to compensate (avoid overcrowding)
        seek_mate_multiplier=2.5,                  # was 4.0
        replicate_multiplier=1.0,                  # was 2.0
    ),
    dna=DNAConfig(
        gene_defaults=DNAGeneDefaults(
            # Start with stronger attack & defense genes
            attack_enabled=True,
            attack_points=12,
            defend_enabled=True,
            defend_points=10,
            # Keep everything else at default
            brain_memory_enabled=True, brain_memory_points=8,
            brain_sense_slots_enabled=True, brain_sense_slots_points=10,
            brain_action_slots_enabled=True, brain_action_slots_points=7,
            vision_distance_enabled=True, vision_distance_points=15,
            vision_fov_enabled=True, vision_fov_points=15,
            dot_detection_enabled=True, dot_detection_points=7,
            food_detection_enabled=True, food_detection_points=10,
            nearby_dot_density_enabled=True, nearby_dot_density_points=8,
            movement_speed_enabled=True, movement_speed_points=8,
            movement_max_energy_enabled=True, movement_max_energy_points=10,
        ),
        # Total points raised slightly to accommodate beefier defaults
        total_points=120,
    ),
)


# ---------------------------------------------------------------------------
# "rapid_evolution"
# Cheap, frequent reproduction + expanded senses. Watch DNA diversify fast.
# Expect: large populations, diverse gene pools, slower combat.
# ---------------------------------------------------------------------------
_rapid_evolution = SimulationConfig(
    world=WorldConfig(
        # More food → easier to hit the reproduction energy threshold
        initial_food=60,
        food_energy_min=80,
        food_energy_max=200,
    ),
    behavior=BehaviorConfig(
        # Lower the bar for sexual reproduction significantly
        seek_mate_energy_threshold=0.25,           # was 0.4
        seek_mate_multiplier=6.0,                  # was 4.0 — very strong drive
        seek_mate_count_bonus_scale=0.5,           # was 0.3
        # Asexual also cheaper
        replicate_energy_threshold=0.6,            # was 0.8
        replicate_multiplier=3.0,                  # was 2.0
        # Less aggressive — spend energy on reproduction not fighting
        attack_multiplier=1.5,                     # was 3.0
        attack_hunt_threshold=0.5,                 # was 0.3 — only hunt when quite hungry
    ),
    dna=DNAConfig(
        # Bigger budget → more room to specialize
        total_points=130,
        # Higher toggle chance → faster gene discovery
        gene_toggle_chance=0.10,                   # was 0.05
        gene_defaults=DNAGeneDefaults(
            # Start with reproduction enabled and well-funded
            replicate_enabled=True,
            replicate_points=15,
            # Enhanced senses to find mates
            vision_distance_enabled=True, vision_distance_points=20,
            vision_fov_enabled=True, vision_fov_points=20,
            dot_detection_enabled=True, dot_detection_points=12,
            food_detection_enabled=True, food_detection_points=12,
            nearby_dot_density_enabled=True, nearby_dot_density_points=12,
            # Unlock DNA strength detection from the start
            dna_strength_detection_enabled=True, dna_strength_detection_points=5,
            # Keep brain healthy
            brain_memory_enabled=True, brain_memory_points=8,
            brain_sense_slots_enabled=True, brain_sense_slots_points=10,
            brain_action_slots_enabled=True, brain_action_slots_points=7,
            # Lighter combat genes
            attack_enabled=True, attack_points=3,
            defend_enabled=True, defend_points=3,
            movement_speed_enabled=True, movement_speed_points=8,
            movement_max_energy_enabled=True, movement_max_energy_points=10,
        ),
    ),
    senses=SensesConfig(
        # Better sense scaling → evolution pays off more per point
        vision_distance_per_point=14,              # was 10
        dot_detection_per_point=10,                # was 8
        food_detection_per_point=13,               # was 10
        density_radius_per_point=15,               # was 12
    ),
)


# ---------------------------------------------------------------------------
# Public registry — add your own profiles here
# ---------------------------------------------------------------------------
PROFILES: dict[str, SimulationConfig] = {
    "default":          _default,
    "high_aggression":  _high_aggression,
    "rapid_evolution":  _rapid_evolution,
}
