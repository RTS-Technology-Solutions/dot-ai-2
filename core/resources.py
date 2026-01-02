"""
Resource System - Energy, Health, and Hunger Management
Handles resource tracking, depletion, and regeneration
"""

class Resources:
    """
    Manages a dot's vital resources
    - Energy: Primary fuel for actions
    - Health: Life force, death at 0
    - Hunger: Derived from energy ratio
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Energy
        self.max_energy = self.calculate_max_energy()
        self.energy = self.max_energy * 0.6  # Start at 60% energy (hungry!)
        
        # Health
        self.max_health = 100  # Base value (may add DNA scaling later)
        self.health = self.max_health  # Start full
        
        # Hunger (derived, not stored separately in simple model)
        self.hunger = 0.0  # 0 = satisfied, 1 = starving
    
    def calculate_max_energy(self):
        """
        Calculate maximum energy from DNA
        Base: 100
        DNA Bonus: movement_max_energy gene_points * 5
        """
        base = 100
        if self.dna.movement_max_energy.enabled:
            bonus = self.dna.movement_max_energy.points * 5
            return base + bonus
        return base
    
    def update_hunger(self):
        """
        Recalculate hunger based on energy ratio
        Hunger = 1 - (current_energy / max_energy)
        """
        self.hunger = 1.0 - (self.energy / self.max_energy)
    
    def deplete_energy(self, amount):
        """
        Remove energy (movement, actions, idle)
        Energy cannot go below 0
        """
        self.energy = max(0.0, self.energy - amount)
        self.update_hunger()
    
    def add_energy(self, amount):
        """
        Add energy (from eating)
        Energy cannot exceed max
        Returns: Amount of overflow (for DNA conversion)
        """
        old_energy = self.energy
        self.energy = min(self.max_energy, self.energy + amount)
        self.update_hunger()
        
        # Return overflow amount
        overflow = amount - (self.energy - old_energy)
        return max(0.0, overflow)
    
    def deplete_health(self, amount):
        """
        Damage health (from starvation, attacks)
        Health cannot go below 0
        """
        self.health = max(0.0, self.health - amount)
    
    def add_health(self, amount):
        """
        Heal health (from energy overflow)
        Health cannot exceed max
        Returns: Amount of overflow (for DNA conversion)
        """
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        
        # Return overflow amount
        overflow = amount - (self.health - old_health)
        return max(0.0, overflow)
    
    def eat(self, food_energy: float, brain):
        """
        Consume food with cascading priority system:
        1. Fill energy first
        2. Overflow goes to health
        3. When both full, overflow converts to DNA points (10% conversion rate)
        
        Args:
            food_energy: Energy value from food
            brain: Brain reference for DNA growth
        
        Returns: Dict with energy_gained, health_gained, dna_gained
        """
        result = {'energy_gained': 0, 'health_gained': 0, 'dna_gained': 0}
        
        # Priority 1: Fill energy
        energy_overflow = self.add_energy(food_energy)
        result['energy_gained'] = food_energy - energy_overflow
        
        # Priority 2: Overflow goes to health (if any)
        if energy_overflow > 0:
            health_overflow = self.add_health(energy_overflow)
            result['health_gained'] = energy_overflow - health_overflow
            
            # Priority 3: When both full, convert to DNA (10% conversion)
            if health_overflow > 0:
                # 10% of overflow becomes DNA points (prevents runaway growth)
                dna_gain = health_overflow * 0.10
                brain.dna.earn_dna_points(dna_gain)
                result['dna_gained'] = dna_gain
        
        return result
    
    def is_alive(self):
        """Check if dot is alive (health > 0)"""
        return self.health > 0
    
    def is_starving(self):
        """Check if in starvation state (energy = 0 but health > 0)"""
        return self.energy <= 0 and self.health > 0
    
    def is_satiated(self):
        """Check if energy is maxed out (for DNA point gain)"""
        return self.energy >= self.max_energy
    
    def is_healthy(self):
        """Check if health is maxed out (for ability unlocking)"""
        return self.health >= self.max_health
    
    def get_energy_ratio(self):
        """Get energy as ratio 0-1"""
        return self.energy / self.max_energy if self.max_energy > 0 else 0
    
    def get_health_ratio(self):
        """Get health as ratio 0-1"""
        return self.health / self.max_health if self.max_health > 0 else 0
    
    def serialize(self):
        """Export resource state"""
        return {
            'energy': self.energy,
            'max_energy': self.max_energy,
            'energy_ratio': self.get_energy_ratio(),
            'health': self.health,
            'max_health': self.max_health,
            'health_ratio': self.get_health_ratio(),
            'hunger': self.hunger,
            'is_alive': self.is_alive(),
            'is_starving': self.is_starving(),
            'is_satiated': self.is_satiated()
        }
    
    def __repr__(self):
        return f"Resources(E:{self.energy:.0f}/{self.max_energy:.0f}, H:{self.health:.0f}/{self.max_health:.0f})"
