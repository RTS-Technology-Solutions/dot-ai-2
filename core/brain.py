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
        self.growth_rate = 2.0  # DNA points per second of age (increased for Phase 4 memory)
        
        # Calculated values
        self.capacity = self.calculate_capacity()
        self.memory_slots = self.calculate_memory_slots()
        self.sense_slots = self.calculate_sense_slots()
        self.action_slots = self.calculate_action_slots()
        
        # Memory storage - Phase 4 implementation
        self.memories = []  # List of interaction memories
        self.max_memories = 50  # Keep last 50 memories
        
        # Reward tracking - Phase 4 intelligence (DNA growth via eating)
        self.total_reward = 0.0  # Cumulative reward score
        self.action_rewards = {}  # Track rewards per action type
    
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
    
    def add_memory(self, memory_type, data, reward_impact):
        """
        Add a memory of an interaction/event
        
        Args:
            memory_type: Type of memory ('attack', 'defend', 'reproduce', 'eat', etc.)
            data: Dict with memory details (target_id, outcome, etc.)
            reward_impact: Float reward/penalty from this memory
        """
        memory = {
            'type': memory_type,
            'timestamp': self.age,
            'data': data,
            'reward': reward_impact
        }
        
        self.memories.append(memory)
        
        # Limit memory size (keep most recent)
        if len(self.memories) > self.max_memories:
            self.memories.pop(0)
    
    def add_reward(self, action_type, reward_value):
        """
        Track rewards for actions taken
        
        Phase 4: Reward tracking for learning (DNA growth now via eating)
        
        Args:
            action_type: Type of action ('attack', 'replicate', 'seek_food', etc.)
            reward_value: Reward/penalty amount
        """
        self.total_reward += reward_value
        
        if action_type not in self.action_rewards:
            self.action_rewards[action_type] = 0.0
        self.action_rewards[action_type] += reward_value
    
    def get_action_success_rate(self, action_type):
        """
        Calculate success rate for an action based on memory
        
        Returns: Float between 0.0-1.0 representing success rate
        """
        relevant_memories = [m for m in self.memories if m['type'] == action_type]
        
        if not relevant_memories:
            return 0.5  # No data, assume neutral
        
        # Positive rewards = successes
        successes = sum(1 for m in relevant_memories if m['reward'] > 0)
        return successes / len(relevant_memories)
    
    def get_memory_of_dot(self, dot_id):
        """
        Retrieve memories involving a specific dot
        
        Returns: List of memory dicts
        """
        return [m for m in self.memories 
                if m['data'].get('target_id') == dot_id or 
                   m['data'].get('partner_id') == dot_id]
    
    def serialize(self):
        """Export brain state"""
        return {
            'age': self.age,
            'capacity': self.capacity,
            'memory_slots': self.memory_slots,
            'sense_slots': self.sense_slots,
            'action_slots': self.action_slots,
            'memories_count': len(self.memories),
            'total_reward': self.total_reward,
            'action_rewards': self.action_rewards.copy(),
            'earned_dna': self.dna.earned_dna_points
        }
    
    def __repr__(self):
        return f"Brain(age={self.age:.1f}s, capacity={self.capacity:.0f}, mem={self.memory_slots})"
