"""
Brain System - Cognitive Processing
Handles memory, decision-making, and age-gated capacity growth
"""

class Brain:
    """
    Manages dot's cognitive abilities
    - Age-gated capacity growth
    - Memory management
    - Sense/action slot calculation
    """
    
    def __init__(self, dna_profile, age=0.0):
        self.dna = dna_profile
        self.age = age  # In seconds
        
        # Capacity parameters
        self.base_capacity = 100
        self.growth_rate = 1.5  # DNA points per second of age
        
        # Calculated values
        self.capacity = self.calculate_capacity()
        self.memory_slots = self.calculate_memory_slots()
        self.sense_slots = self.calculate_sense_slots()
        self.action_slots = self.calculate_action_slots()
        
        # Memory storage (for future phases)
        self.memories = []
    
    def calculate_capacity(self):
        """
        Age-gated brain capacity
        Formula: 100 + (age_seconds * 1.5)
        """
        return self.base_capacity + (self.age * self.growth_rate)
    
    def calculate_memory_slots(self):
        """
        Memory slots based on DNA and age
        Base: 10
        DNA Bonus: gene_points * 0.5
        Age Bonus: age_seconds * 0.5
        """
        if not self.dna.brain_memory.enabled:
            return 0
        
        base = 10
        dna_bonus = self.dna.brain_memory.points * 0.5
        age_bonus = self.age * 0.5
        
        return int(base + dna_bonus + age_bonus)
    
    def calculate_sense_slots(self):
        """
        Sense slots based on DNA
        Base: 2
        DNA Bonus: gene_points * 0.1
        """
        if not self.dna.brain_sense_slots.enabled:
            return 0
        
        base = 2
        dna_bonus = self.dna.brain_sense_slots.points * 0.1
        
        return int(base + dna_bonus)
    
    def calculate_action_slots(self):
        """
        Action slots based on DNA
        Base: 2
        DNA Bonus: gene_points * 0.1
        """
        if not self.dna.brain_action_slots.enabled:
            return 0
        
        base = 2
        dna_bonus = self.dna.brain_action_slots.points * 0.1
        
        return int(base + dna_bonus)
    
    def update_age(self, delta_time):
        """
        Update age and recalculate all age-dependent values
        Called every frame
        """
        self.age += delta_time
        
        # Recalculate capacity and slots
        self.capacity = self.calculate_capacity()
        self.memory_slots = self.calculate_memory_slots()
        # Sense/action slots don't change with age in Phase 1
    
    def can_allocate_dna(self, points):
        """
        Check if brain has capacity for additional DNA points
        Used when dots gain DNA from eating
        """
        current_allocation = self.dna.get_allocated_points()
        return (current_allocation + points) <= self.capacity
    
    def serialize(self):
        """Export brain state"""
        return {
            'age': self.age,
            'capacity': self.capacity,
            'memory_slots': self.memory_slots,
            'sense_slots': self.sense_slots,
            'action_slots': self.action_slots,
            'memories_count': len(self.memories)
        }
    
    def __repr__(self):
        return f"Brain(age={self.age:.1f}s, capacity={self.capacity:.0f}, mem={self.memory_slots})"
