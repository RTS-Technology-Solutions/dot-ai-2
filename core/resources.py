"""
Resource management is separated from Dot because the cascading eat() logic
(energy → health → DNA) is its own non-trivial subsystem. Isolating it means
the cascade rules can change without touching the agent loop, and the resource
system can be tested against known inputs without needing a full Dot instance.
"""

class Resources:
    """
    Owns energy, health, and derived hunger for one dot.

    The cascade priority (energy fills first, then health, then DNA) mirrors
    a biological hierarchy: immediate survival takes precedence over recovery,
    which takes precedence over genetic long-term investment. That ordering is
    enforced here so the Dot doesn’t need to implement it.
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
        Tank capacity grows with the movement_max_energy gene because a dot
        that invests in sustained activity needs a larger fuel reserve to
        operate without constant refueling interrupting other behaviors.
        """
        base = 100
        if self.dna.movement_max_energy.enabled:
            bonus = self.dna.movement_max_energy.points * 5
            return base + bonus
        return base
    
    def update_hunger(self):
        """
        Derives hunger from the current energy ratio.

        Not stored independently — recalculated after every change so hunger
        can never drift out of sync with the energy value it reflects.
        """
        self.hunger = 1.0 - (self.energy / self.max_energy)
    
    def deplete_energy(self, amount):
        """
        Reduces energy and refreshes hunger.

        Floor at 0 prevents underflow errors from compounding depletion calls.
        """
        self.energy = max(0.0, self.energy - amount)
        self.update_hunger()
    
    def add_energy(self, amount):
        """
        Fills energy up to max and returns the overflow.

        Overflow is what the caller (eat()) routes onward to health and then
        DNA — this method is responsible only for the energy portion of the
        cascade.
        """
        old_energy = self.energy
        self.energy = min(self.max_energy, self.energy + amount)
        self.update_hunger()
        
        # Return overflow amount
        overflow = amount - (self.energy - old_energy)
        return max(0.0, overflow)
    
    def deplete_health(self, amount):
        """
        Reduces health. Floor at 0 ensures a dot dies cleanly
        rather than accumulating negative health over multiple hits.
        """
        self.health = max(0.0, self.health - amount)
    
    def add_health(self, amount):
        """
        Increases health up to max and returns overflow.

        Overflow continues up the cascade to DNA growth, so a fully-healed
        dot converts excess food into improved offspring potential.
        """
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        
        # Return overflow amount
        overflow = amount - (self.health - old_health)
        return max(0.0, overflow)
    
    def eat(self, food_energy: float, brain):
        """
        Routes food energy through the priority cascade.

        Energy fills first — immediate fuel matters more than recovery. Health
        fills second — survival outlasts the current meal. Only a dot with both
        full converts surplus to DNA, signaling genuine thriving rather than
        narrow survival. The 10% conversion rate is intentionally conservative
        so DNA growth requires sustained performance, not a single lucky meal.
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
        """False when health reaches 0 — the only death condition after starvation depletes health."""
        return self.health > 0
    
    def is_starving(self):
        """True when energy is gone but the dot hasn’t died yet — triggers starvation damage in the update loop."""
        return self.energy <= 0 and self.health > 0
    
    def is_satiated(self):
        """True when energy is at max — this is the threshold at which food overflow starts refilling health."""
        return self.energy >= self.max_energy
    
    def is_healthy(self):
        """True when health is at max — threshold at which food overflow converts to DNA growth."""
        return self.health >= self.max_health
    
    def get_energy_ratio(self):
        """Energy as a 0–1 fraction for hunger calculation and renderer display."""
        return self.energy / self.max_energy if self.max_energy > 0 else 0
    
    def get_health_ratio(self):
        """Health as a 0–1 fraction for renderer display and utility calculations."""
        return self.health / self.max_health if self.max_health > 0 else 0
    
    def serialize(self):
        """Snapshot for the renderer and logger — returns plain values, no object references."""
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
