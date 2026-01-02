"""
Action System - Combat, Reproduction, and Interactions
Handles all dot-to-dot and dot-to-world interactions
"""

import random


class Action:
    """Base class for actions"""
    
    def __init__(self, name, energy_cost):
        self.name = name
        self.energy_cost = energy_cost
    
    def can_execute(self, dot, world_state):
        """Check if action can be executed"""
        return dot.resources.energy >= self.energy_cost
    
    def execute(self, dot, world_state, delta_time):
        """Execute the action"""
        raise NotImplementedError


class AttackAction(Action):
    """Attack another dot"""
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        self.range = self.calculate_range()
        self.damage = self.calculate_damage()
        
        # Energy cost: 5% of max energy
        energy_cost = 0  # Will be calculated per dot
        super().__init__("attack", energy_cost)
    
    def calculate_range(self):
        """Attack range from DNA"""
        if not self.dna.attack.enabled:
            return 0
        
        base = 30  # pixels
        bonus = self.dna.attack.points * 2
        return base + bonus
    
    def calculate_damage(self):
        """Damage dealt from DNA"""
        if not self.dna.attack.enabled:
            return 0
        
        base = 10  # health points
        bonus = self.dna.attack.points * 0.5
        return base + bonus
    
    def can_execute(self, dot, world_state):
        """Can attack if gene enabled and energy available"""
        if not self.dna.attack.enabled:
            return False
        
        cost = dot.resources.max_energy * 0.05
        return dot.resources.energy >= cost
    
    def execute(self, dot, target_dot, delta_time):
        """Execute attack on target"""
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
    """Defensive stance - reduces incoming damage"""
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        self.reduction = self.calculate_reduction()
        super().__init__("defend", 0)  # Cost is per-second
    
    def calculate_reduction(self):
        """Damage reduction percentage"""
        if not self.dna.defend.enabled:
            return 0
        
        base = 0.3  # 30% base reduction
        bonus = self.dna.defend.points * 0.01
        return min(0.8, base + bonus)  # Cap at 80%
    
    def can_execute(self, dot, world_state):
        """Can defend if gene enabled and energy available"""
        if not self.dna.defend.enabled:
            return False
        
        cost = dot.resources.max_energy * 0.03
        return dot.resources.energy >= cost
    
    def execute(self, dot, world_state, delta_time):
        """Activate defensive stance"""
        # Energy cost: 3% per second
        cost = dot.resources.max_energy * 0.03 * delta_time
        dot.resources.deplete_energy(cost)
        
        dot.is_defending = True
        return {"result": "DEFENDING", "reduction": self.reduction}


class ReplicateAction(Action):
    """Reproduction - both sexual and asexual modes"""
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        super().__init__("replicate", 0)  # Cost varies by mode
    
    def can_execute_asexual(self, dot):
        """Can do asexual reproduction if energy > 80%"""
        if not self.dna.replicate.enabled:
            return False
        
        threshold = dot.resources.max_energy * 0.8
        return dot.resources.energy >= threshold and dot.resources.health > 70
    
    def can_execute_sexual(self, dot):
        """Can do sexual reproduction if energy > 40%"""
        if not self.dna.replicate.enabled:
            return False
        
        threshold = dot.resources.max_energy * 0.4
        return dot.resources.energy >= threshold and dot.resources.health > 70
    
    def can_execute(self, dot, world_state):
        """Can replicate (either mode) if gene enabled and minimum energy met"""
        return self.can_execute_sexual(dot) or self.can_execute_asexual(dot)
    
    def execute(self, dot, world_state, delta_time, mate=None):
        """Create offspring - sexual if mate provided, asexual otherwise"""
        from .dna import DNAProfile
        from .dot import Dot
        
        if mate is not None:
            # SEXUAL REPRODUCTION
            return self.execute_sexual(dot, mate, world_state)
        else:
            # ASEXUAL REPRODUCTION
            return self.execute_asexual(dot, world_state)
    
    def execute_sexual(self, parent_a, parent_b, world_state):
        """Sexual reproduction with DNA crossover"""
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
        """Asexual reproduction (clone with mutations)"""
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
        """Create mutated copy of parent DNA"""
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
    """Manages all available actions for a dot"""
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Initialize actions
        self.attack = AttackAction(dna_profile)
        self.defend = DefendAction(dna_profile)
        self.replicate = ReplicateAction(dna_profile)
    
    def get_available_actions(self, dot, world_state):
        """Get list of actions that can currently be executed"""
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
