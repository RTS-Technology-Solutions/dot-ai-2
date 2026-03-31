"""
Action logic is separated from Dot because actions involving two entities have
outcomes that depend on both participants' DNA. Keeping AttackAction here means
damage calculation, defense mitigation, and range math have one owner — the
alternative would be attack logic in one class and defense logic in another with
no clear place for the mitigation formula.
"""

import random


class Action:
    """
    Base interface that all actions share.

    The energy_cost field and can_execute() check live here because every
    action must gate on available energy — the cost differs by action, but
    the enforcement pattern is the same for all of them.
    """
    
    def __init__(self, name, energy_cost):
        self.name = name
        self.energy_cost = energy_cost
    
    def can_execute(self, dot, world_state):
        """Returns True when the dot has enough energy. Called before execute() to prevent unaffordable actions."""
        return dot.resources.energy >= self.energy_cost
    
    def execute(self, dot, world_state, delta_time):
        """Override point for action-specific logic. Raises NotImplementedError to force subclass implementation."""
        raise NotImplementedError


class AttackAction(Action):
    """
    Combat for dots that have invested in the attack gene.

    Lives as a class because attack involves attacker DNA (damage, range) and
    defender DNA (damage reduction), and co-locating those calculations prevents
    them from drifting independently when either formula changes.
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        self.range = self.calculate_range()
        self.damage = self.calculate_damage()
        
        # Energy cost: 5% of max energy
        energy_cost = 0  # Will be calculated per dot
        super().__init__("attack", energy_cost)
    
    def calculate_range(self):
        """
        Returns melee range in pixels.

        Scales with gene points so attack-gene investment increases reach —
        a distinct tactical advantage from damage that makes the gene worth
        more than just its damage output.
        """
        if not self.dna.attack.enabled:
            return 0
        
        base = 30  # pixels
        bonus = self.dna.attack.points * 2
        return base + bonus
    
    def calculate_damage(self):
        """
        Returns base damage before defense mitigation.

        Scales with gene points so high-investment attackers deal meaningfully
        more damage — the gene must produce a real payoff to be worth the
        budget cost in the DNA allocation system.
        """
        if not self.dna.attack.enabled:
            return 0
        
        base = 10  # health points
        bonus = self.dna.attack.points * 0.5
        return base + bonus
    
    def can_execute(self, dot, world_state):
        """
        Attack gene must be present and energy must cover the 5% cost.

        Without the energy check, low-energy dots could attempt attacks they
        cannot afford, accelerating their own starvation.
        """
        if not self.dna.attack.enabled:
            return False
        
        cost = dot.resources.max_energy * 0.05
        return dot.resources.energy >= cost
    
    def execute(self, dot, target_dot, delta_time):
        """
        Applies damage to target. The 5% miss chance prevents combat from
        being purely deterministic — the randomness mirrors the uncertainty
        of real-world fights and keeps attack from being a guaranteed trade.
        """
        # 5% probabilistic failure
        if random.random() < 0.05:
            return {"result": "MISS", "damage": 0}
        
        # Calculate damage
        damage = self.damage
        
        # Apply defense reduction if target is defending
        # NOTE: Defending reduces damage but still loses health (just less)
        # Defender also pays 3% max_energy/second while defending
        if hasattr(target_dot, 'is_defending') and target_dot.is_defending:
            defense_reduction = 0.3 + (target_dot.dna.defend.points * 0.01)
            damage *= (1.0 - min(0.8, defense_reduction))
        
        # Apply damage
        target_dot.resources.deplete_health(damage)
        
        # Energy cost for attacker
        cost = dot.resources.max_energy * 0.05
        dot.resources.deplete_energy(cost)
        
        return {"result": "HIT", "damage": damage}


class DefendAction(Action):
    """
    Manages the defending state that reduces incoming damage.

    Separated from Dot because the mitigation formula combines the defender's
    gene points with the incoming damage value — both sides of that equation
    are only meaningful together, and this class is where they meet.
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        self.reduction = self.calculate_reduction()
        super().__init__("defend", 0)  # Cost is per-second
    
    def calculate_reduction(self):
        """
        Returns the fraction of incoming damage this dot blocks.

        Capped at 80% so even max-invest defenders cannot become invulnerable —
        a gap that keeps attacking viable against heavily-defended opponents.
        """
        if not self.dna.defend.enabled:
            return 0
        
        base = 0.3  # 30% base reduction
        bonus = self.dna.defend.points * 0.01
        return min(0.8, base + bonus)  # Cap at 80%
    
    def can_execute(self, dot, world_state):
        """
        Defend drains 3% max-energy/second, so critically low-energy dots
        cannot sustain a stance. This makes fleeing more viable than defending
        indefinitely when energy runs out.
        """
        if not self.dna.defend.enabled:
            return False
        
        cost = dot.resources.max_energy * 0.03
        return dot.resources.energy >= cost
    
    def execute(self, dot, world_state, delta_time):
        """
        Deducts per-second energy cost and sets the defending flag.

        The flag is what receive_damage() checks for mitigation — the cost
        is deducted here so each tick of defending has a real energy price.
        """
        # Energy cost: 3% per second
        cost = dot.resources.max_energy * 0.03 * delta_time
        dot.resources.deplete_energy(cost)
        
        dot.is_defending = True
        return {"result": "DEFENDING", "reduction": self.reduction}


class ReplicateAction(Action):
    """
    Manages both reproduction modes under one gene.

    The asexual path exists as a fallback when no suitable mate is within range
    — it costs more energy but doesn’t depend on another dot’s cooperation,
    so population growth doesn’t stall when the population is sparse.
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        super().__init__("replicate", 0)  # Cost varies by mode
    
    def can_execute_asexual(self, dot):
        """
        Asexual requires 80% energy because producing a clone is expensive —
        the offspring inherits the full genome and the parent must be thriving
        to afford the investment without dying from the energy drain.
        """
        if not self.dna.replicate.enabled:
            return False
        
        threshold = dot.resources.max_energy * 0.8
        return dot.resources.energy >= threshold and dot.resources.health > 70
    
    def can_execute_sexual(self, dot):
        """
        Sexual only requires 40% energy because the cost is split between two
        parents — each contributes a smaller share, making sexual reproduction
        accessible at lower resource levels than asexual.
        """
        if not self.dna.replicate.enabled:
            return False
        
        threshold = dot.resources.max_energy * 0.4
        return dot.resources.energy >= threshold and dot.resources.health > 70
    
    def can_execute(self, dot, world_state):
        """True if either reproduction mode is currently affordable — sexual is preferred but asexual is the fallback."""
        return self.can_execute_sexual(dot) or self.can_execute_asexual(dot)
    
    def execute(self, dot, world_state, delta_time, mate=None):
        """Routes to sexual or asexual reproduction depending on whether a mate was provided."""
        from .dna import DNAProfile
        from .dot import Dot
        
        if mate is not None:
            # SEXUAL REPRODUCTION
            return self.execute_sexual(dot, mate, world_state)
        else:
            # ASEXUAL REPRODUCTION
            return self.execute_asexual(dot, world_state)
    
    def execute_sexual(self, parent_a, parent_b, world_state):
        """
        Crossover two parent genomes and produce offspring.

        Spawn position is midpoint ± random offset so the child starts near
        where its parents met rather than at an arbitrary world coordinate.
        """
        from .dna import DNAProfile
        
        # Energy cost: 40% each parent
        cost_a = parent_a.resources.max_energy * 0.4
        cost_b = parent_b.resources.max_energy * 0.4
        
        parent_a.resources.deplete_energy(cost_a)
        parent_b.resources.deplete_energy(cost_b)
        
        # Health factor for offspring quality (0.8-1.0)
        health_factor_a = 0.8 + (parent_a.resources.health / parent_a.resources.max_health) * 0.2
        health_factor_b = 0.8 + (parent_b.resources.health / parent_b.resources.max_health) * 0.2
        avg_health_factor = (health_factor_a + health_factor_b) / 2.0
        
        # Create offspring DNA via crossover
        child_dna = DNAProfile.crossover(parent_a.dna, parent_b.dna)
        
        # Apply minor mutations (5% chance per gene, smaller changes)
        child_dna = self.mutate_dna(child_dna, mutation_rate=0.05, mutation_amount=2)
        
        # Spawn position (between parents)
        mid_x = (parent_a.position[0] + parent_b.position[0]) / 2.0
        mid_y = (parent_a.position[1] + parent_b.position[1]) / 2.0
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        child_pos = [mid_x + offset_x, mid_y + offset_y]
        
        # Clamp to world bounds
        bounds = world_state.get('bounds', {'width': 1200, 'height': 800})
        child_pos[0] = max(50, min(bounds['width'] - 50, child_pos[0]))
        child_pos[1] = max(50, min(bounds['height'] - 50, child_pos[1]))
        
        return {
            "result": "OFFSPRING_SEXUAL",
            "child_dna": child_dna,
            "child_pos": child_pos,
            "parent_a_id": parent_a.id,
            "parent_b_id": parent_b.id,
            "health_factor": avg_health_factor
        }
    
    def execute_asexual(self, dot, world_state):
        """
        Clone the parent with mutations and deduct the steep energy cost.

        The 80% energy drain ensures asexual reproduction is a meaningful
        sacrifice rather than a cheap shortcut to population growth.
        """
        from .dna import DNAProfile
        
        # Energy cost: 80%
        cost = dot.resources.max_energy * 0.8
        dot.resources.deplete_energy(cost)
        
        # Create mutated DNA
        child_dna = self.mutate_dna(dot.dna)
        
        # Spawn position (nearby parent)
        offset_x = random.randint(-30, 30)
        offset_y = random.randint(-30, 30)
        child_pos = [dot.position[0] + offset_x, dot.position[1] + offset_y]
        
        # Clamp to world bounds
        bounds = world_state.get('bounds', {'width': 1200, 'height': 800})
        child_pos[0] = max(50, min(bounds['width'] - 50, child_pos[0]))
        child_pos[1] = max(50, min(bounds['height'] - 50, child_pos[1]))
        
        return {
            "result": "OFFSPRING_ASEXUAL",
            "child_dna": child_dna,
            "child_pos": child_pos,
            "parent_id": dot.id
        }
    
    def mutate_dna(self, parent_dna, mutation_rate=0.1, mutation_amount=5):
        """
        Produces a mutated clone of the parent genome.

        Both point values and enabled flags are subject to random change so
        asexual offspring can discover new gene configurations, not just
        reproduce the parent’s allocation with minor numerical variation.
        The budget validation at the end ensures no invalid genome leaves
        the mutation step.
        """
        from .dna import DNAProfile
        
        # Clone parent DNA
        child_dna = parent_dna.clone()
        
        # Mutation parameters (configurable)
        
        for gene in child_dna.get_all_genes():
            # Skip eat gene (always enabled, no cost)
            if gene.name == "eat":
                continue
            
            # Mutate points
            if random.random() < mutation_rate:
                change = random.randint(-mutation_amount, mutation_amount)
                gene.points = max(0, min(50, gene.points + change))
            
            # Mutate enabled state (lower chance)
            if random.random() < 0.05:  # 5% chance to toggle
                gene.enabled = not gene.enabled
        
        # Ensure DNA is valid (doesn't exceed capacity)
        allocated = child_dna.get_allocated_points()
        if allocated > child_dna.total_points:
            # Reduce random genes until valid
            while child_dna.get_allocated_points() > child_dna.total_points:
                genes = [g for g in child_dna.get_all_genes() if g.points > 0 and g.name != "eat"]
                if genes:
                    gene = random.choice(genes)
                    gene.points = max(0, gene.points - 1)
        
        return child_dna


class ActionManager:
    """
    Assembles the action objects for one dot from its DNA.

    Exists so each dot gets its own action instances with pre-computed gene
    values rather than recalculating range and damage every tick. The manager
    also provides the canonical list of executable actions for the UI and logger.
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Initialize actions
        self.attack = AttackAction(dna_profile)
        self.defend = DefendAction(dna_profile)
        self.replicate = ReplicateAction(dna_profile)
    
    def get_available_actions(self, dot, world_state):
        """Returns the subset of actions currently affordable for this dot, for display or logging."""
        available = []
        
        if self.attack.can_execute(dot, world_state):
            available.append("attack")
        
        if self.defend.can_execute(dot, world_state):
            available.append("defend")
        
        if self.replicate.can_execute(dot, world_state):
            available.append("replicate")
        
        # Always available
        available.extend(["seek_food", "idle"])
        
        return available
