"""
Simulation Configuration System
================================
All tunable parameters for DOT AI 2.0 in one place.

Edit these values (or load a named profile from profiles.py) to change
simulation behavior without touching any core logic files.

Structure:
  SimulationConfig        <- root config passed to set_config()
  ├── WorldConfig         <- world size, food, spawning
  ├── BrainConfig         <- cognition, memory, slot scaling
  ├── DNAGeneDefaults     <- starting gene enabled/points per gene
  ├── DNAConfig           <- DNA budget, mutation rules, gene defaults
  ├── SensesConfig        <- sense base ranges and per-point scaling
  └── BehaviorConfig      <- utility weights, thresholds, energy costs
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# World / Environment
# ---------------------------------------------------------------------------

@dataclass
class WorldConfig:
    """Simulation world parameters — size, food, spawning rules."""

    # World dimensions (pixels)
    width: int = 3200
    height: int = 1200

    # Initial population & food
    initial_dots: int = 10
    initial_food: int = 40

    # Spawning margins (pixels from world edge)
    dot_spawn_margin: int = 100    # Initial dot spawn clearance
    food_spawn_margin: int = 50    # Food spawn clearance from edge
    food_center_avoid_radius: int = 100  # Food tries to stay this far from center

    # Food energy values (random in [min, max] per food item)
    food_energy_min: int = 50
    food_energy_max: int = 150

    # Eating interaction
    eating_range: int = 15         # Pixels a dot must be within to eat
    eating_energy_per_frame: int = 10  # Energy drained from food per frame

    # Corpse nutrition
    dead_dot_base_nutrition: int = 30  # Minimum energy in a dead dot's corpse

    # Food respawn threshold — spawn a batch when fewer than this many remain
    food_respawn_threshold: int = 8


# ---------------------------------------------------------------------------
# Brain / Cognition
# ---------------------------------------------------------------------------

@dataclass
class BrainConfig:
    """Brain capacity, memory, and sense/action slot scaling."""

    # Capacity growth
    base_capacity: float = 100.0   # Starting cognitive capacity
    growth_rate: float = 2.0       # Capacity points gained per second of age

    # Memory
    max_memories: int = 50         # FIFO memory buffer size (oldest discarded)
    memory_slot_base: int = 10     # Memory slots before DNA bonus
    memory_slot_dna_scale: float = 0.5   # Extra slots per brain_memory gene point
    memory_slot_age_scale: float = 0.5   # Extra slots per second of age

    # Sense slots
    sense_slot_base: int = 2
    sense_slot_dna_scale: float = 0.1    # Extra slots per brain_sense_slots point

    # Action slots
    action_slot_base: int = 2
    action_slot_dna_scale: float = 0.1   # Extra slots per brain_action_slots point


# ---------------------------------------------------------------------------
# DNA — per-gene defaults
# ---------------------------------------------------------------------------

@dataclass
class DNAGeneDefaults:
    """
    Default enabled/points for every gene in a freshly created DNAProfile.

    Change these to shift the starting conditions for new generations.
    Note: total allocated points must not exceed DNAConfig.total_points.
    """

    # Brain genes
    brain_memory_enabled: bool = True
    brain_memory_points: int = 8

    brain_sense_slots_enabled: bool = True
    brain_sense_slots_points: int = 10

    brain_action_slots_enabled: bool = True
    brain_action_slots_points: int = 7

    # Sense genes
    vision_distance_enabled: bool = True
    vision_distance_points: int = 15

    vision_fov_enabled: bool = True
    vision_fov_points: int = 15

    dot_detection_enabled: bool = True
    dot_detection_points: int = 7

    food_detection_enabled: bool = True
    food_detection_points: int = 10

    power_detection_enabled: bool = False
    power_detection_points: int = 0

    food_amount_detection_enabled: bool = False
    food_amount_detection_points: int = 0

    dna_strength_detection_enabled: bool = False
    dna_strength_detection_points: int = 0

    nearby_dot_density_enabled: bool = True
    nearby_dot_density_points: int = 8

    social_sense_enabled: bool = False
    social_sense_points: int = 0

    # Action genes
    movement_speed_enabled: bool = True
    movement_speed_points: int = 8

    movement_max_energy_enabled: bool = True
    movement_max_energy_points: int = 10

    defend_enabled: bool = True
    defend_points: int = 5

    attack_enabled: bool = True
    attack_points: int = 5

    replicate_enabled: bool = False
    replicate_points: int = 0

    revive_enabled: bool = False
    revive_points: int = 0


@dataclass
class DNAConfig:
    """DNA budget and mutation rules."""

    # Total DNA points available to a fresh DNAProfile
    total_points: int = 100

    # Mutation — random chance per gene to toggle enabled/disabled during reproduction
    gene_toggle_chance: float = 0.05   # 5% per gene per reproduction event

    # Maximum points that can be allocated to any single gene
    gene_point_max: int = 50

    # Default gene starting states (see DNAGeneDefaults above)
    gene_defaults: DNAGeneDefaults = field(default_factory=DNAGeneDefaults)


# ---------------------------------------------------------------------------
# Senses — perception formulas
# ---------------------------------------------------------------------------

@dataclass
class SensesConfig:
    """Base ranges and per-DNA-point scaling for every sense."""

    # Vision cone distance: base_px + (gene_points * per_point_px)
    vision_distance_base: int = 100
    vision_distance_per_point: int = 10

    # Field of view: base_deg + (gene_points * per_point_deg), capped at fov_max
    vision_fov_base: int = 90
    vision_fov_per_point: int = 6
    vision_fov_max: int = 360

    # Omnidirectional dot detection: base_px + (gene_points * per_point_px)
    dot_detection_base: int = 50
    dot_detection_per_point: int = 8

    # Omnidirectional food detection: base_px + (gene_points * per_point_px)
    food_detection_base: int = 80
    food_detection_per_point: int = 10

    # Density sensing radius: base_px + (gene_points * per_point_px)
    density_radius_base: int = 100
    density_radius_per_point: int = 12


# ---------------------------------------------------------------------------
# Behavior — AI utility weights and energy economics
# ---------------------------------------------------------------------------

@dataclass
class BehaviorConfig:
    """
    Controls the AI's decision-making incentives and energy costs.

    Utility multipliers directly affect how strongly the AI prefers each
    action. Higher multiplier = that action wins more utility comparisons.
    """

    # ---- Energy costs (per second unless noted) ----
    idle_energy_cost: float = 2.0          # Metabolic upkeep while stationary
    movement_energy_cost: float = 1.0      # Additional drain while moving
    defend_energy_cost_pct: float = 0.03   # Fraction of max_energy per second when defending
    starvation_damage: float = 1.5         # Health lost per second when energy == 0

    # ---- Movement ----
    movement_speed_base: float = 50.0      # Base pixels/second before DNA bonus
    movement_speed_per_point: float = 5.0  # Extra pixels/second per movement_speed gene point
    movement_boundary_margin: int = 10     # Pixels from world edge where dots are stopped

    # Urgency speed modifiers (applied as multipliers)
    starving_speed_multiplier: float = 0.1    # Speed when energy == 0 (very slow)
    hungry_speed_multiplier: float = 1.5      # Speed boost when very hungry
    hungry_speed_threshold: float = 0.7       # Hunger fraction (0-1) that triggers boost

    # ---- Reproduction ----
    mating_range: float = 30.0             # Pixels within which sexual mating triggers

    # ---- SEEK FOOD utility ----
    # utility = hunger_pct * food_hunger_scale  [* food_hungry_bonus if hungry]
    food_hunger_scale: float = 10.0
    food_hungry_bonus: float = 2.0
    food_hungry_threshold: float = 0.7     # hunger_pct above which bonus applies

    # ---- ATTACK utility ----
    # Base: weakness_score * (attack_pts/50) * health_pct * hunger_motivation * attack_multiplier
    attack_hunt_threshold: float = 0.3         # Minimum hunger_pct to even consider attacking
    attack_multiplier: float = 3.0             # Top-level incentive for attacking
    attack_hunger_motivation_scale: float = 1.5  # hunger_pct is multiplied by this for motivation
    attack_starving_weakness: float = 2.0       # Weakness score assigned to starving enemies
    attack_food_value_assumption: float = 100.0  # Assumed food energy if DNA sense is disabled
    attack_food_value_normalizer: float = 130.0  # Divisor for food_value in score formula
    # Low-health risk penalties (applied to attack_utility if own health is low)
    attack_low_health_critical: float = 0.3     # Health fraction below which critical penalty applies
    attack_low_health_penalty_critical: float = 0.1  # Multiplier on utility (very risky)
    attack_low_health_moderate: float = 0.6     # Health fraction below which moderate penalty applies
    attack_low_health_penalty_moderate: float = 0.5  # Multiplier on utility (somewhat risky)

    # ---- DEFEND utility ----
    # utility = danger_level * (defend_pts/50) * defend_multiplier
    defend_multiplier: float = 2.0
    defend_threat_count_threshold: int = 3      # Minimum visible enemies before crowd-danger kicks in
    defend_threat_danger_scale: float = 0.4     # Danger per enemy beyond threshold
    defend_health_threshold: float = 0.4        # Own health below which "low health" danger triggers
    defend_health_danger_scale: float = 0.8     # Scales low-health danger level

    # ---- REPLICATE (asexual) utility ----
    # utility = (replicate_pts/50) * energy_pct * health_pct * (1-crowding) * replicate_multiplier
    replicate_multiplier: float = 2.0
    replicate_energy_threshold: float = 0.8     # Minimum energy_pct to attempt
    replicate_health_threshold: float = 0.7     # Minimum health_pct to attempt
    replicate_crowding_scale: float = 0.15      # Crowding penalty per nearby dot (capped at 1.0)

    # ---- SEEK MATE (sexual) utility ----
    # utility = (replicate_pts/50) * energy_pct * health_pct * (1+mate_bonus) * seek_mate_multiplier
    seek_mate_multiplier: float = 4.0           # Higher than replicate → prefers sexual repro
    seek_mate_energy_threshold: float = 0.4     # Lower energy bar vs asexual
    seek_mate_health_threshold: float = 0.7
    seek_mate_count_bonus_scale: float = 0.3    # Bonus per visible potential mate (capped at 1.0)

    # ---- EXPLORE utility ----
    # utility = explore_base + hunger_pct * explore_hunger_scale + health_urgency * explore_health_scale
    explore_base: float = 3.0
    explore_hunger_scale: float = 5.0
    explore_health_scale: float = 2.0

    # ---- IDLE utility (heavily penalized) ----
    # utility = max(idle_min, idle_base - (urgency*health_scale + hunger*hunger_scale + density_penalty))
    idle_base: float = 0.3
    idle_min: float = 0.01                      # Floor so idle is always valid but unattractive
    idle_health_urgency_scale: float = 1.5
    idle_hunger_penalty_scale: float = 2.0
    idle_density_penalty_scale: float = 0.3     # Penalty per nearby dot
    idle_density_penalty_max: float = 3.0       # Cap on density penalty


# ---------------------------------------------------------------------------
# Root config
# ---------------------------------------------------------------------------

@dataclass
class SimulationConfig:
    """Root configuration object. Pass to set_config() before starting."""

    world: WorldConfig = field(default_factory=WorldConfig)
    brain: BrainConfig = field(default_factory=BrainConfig)
    dna: DNAConfig = field(default_factory=DNAConfig)
    senses: SensesConfig = field(default_factory=SensesConfig)
    behavior: BehaviorConfig = field(default_factory=BehaviorConfig)
