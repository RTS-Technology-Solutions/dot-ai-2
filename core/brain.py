"""
The brain is separated from Dot because cognitive capacity is a genetic trait
that scales with both DNA investment and age. Any system that needs to know a
dot's memory limit or slot counts reads from Brain, so the capacity formula has
exactly one owner. Computing it inside Dot would couple cognitive growth to agent
logic and make the formula impossible to profile or tune independently.
"""

from configs import get_config

class Brain:
    """
    Tracks cognitive resources and experience for one dot.

    Age-gated capacity exists because a dot that has survived longer has had
    more time to develop — this prevents newly-spawned dots from being
    cognitively equal to veterans and gives longevity a measurable advantage
    beyond just accumulating more food.
    """
    
    def __init__(self, dna_profile, age=0.0):
        self.dna = dna_profile
        self.age = age  # In seconds
        
        # Capacity parameters (read from config at construction time)
        _bcfg = get_config().brain
        self.base_capacity = _bcfg.base_capacity
        self.growth_rate = _bcfg.growth_rate
        
        # Calculated values
        self.capacity = self.calculate_capacity()
        self.memory_slots = self.calculate_memory_slots()
        self.sense_slots = self.calculate_sense_slots()
        self.action_slots = self.calculate_action_slots()
        
        # Memory storage - Phase 4 implementation
        self.memories = []  # List of interaction memories
        self.max_memories = get_config().brain.max_memories
        
        # Reward tracking - Phase 4 intelligence (DNA growth via eating)
        self.total_reward = 0.0  # Cumulative reward score
        self.action_rewards = {}  # Track rewards per action type
    
    def calculate_capacity(self):
        """
        Returns current cognitive capacity.

        Grows with age so surviving longer yields measurably better cognition,
        creating a selection pressure for strategies that extend lifespan rather
        than strategies that reproduce quickly and die young.
        """
        return self.base_capacity + (self.age * self.growth_rate)
    
    def calculate_memory_slots(self):
        """
        Returns how many memories this dot can store.

        DNA provides the genetic ceiling, age provides accumulated experience.
        Both contribute because a dot with strong memory genes but a short life
        still learns less than one that survives long enough to use those genes.
        """
        if not self.dna.brain_memory.enabled:
            return 0
        
        _bcfg = get_config().brain
        base = _bcfg.memory_slot_base
        dna_bonus = self.dna.brain_memory.points * _bcfg.memory_slot_dna_scale
        age_bonus = self.age * _bcfg.memory_slot_age_scale
        
        return int(base + dna_bonus + age_bonus)
    
    def calculate_sense_slots(self):
        """
        Returns how many sense channels are active.

        Determined by DNA alone (not age) because perception is structural —
        a dot either has the neural architecture for extended sensing or it
        doesn't, regardless of how long it has lived.
        """
        if not self.dna.brain_sense_slots.enabled:
            return 0
        
        _bcfg = get_config().brain
        base = _bcfg.sense_slot_base
        dna_bonus = self.dna.brain_sense_slots.points * _bcfg.sense_slot_dna_scale
        
        return int(base + dna_bonus)
    
    def calculate_action_slots(self):
        """
        Returns how many distinct action types this dot can consider.

        Like sense slots, action capacity is structural (DNA only) because
        the repertoire of possible actions a dot can plan for is set by its
        gene layout, not by its experience.
        """
        if not self.dna.brain_action_slots.enabled:
            return 0
        
        _bcfg = get_config().brain
        base = _bcfg.action_slot_base
        dna_bonus = self.dna.brain_action_slots.points * _bcfg.action_slot_dna_scale
        
        return int(base + dna_bonus)
    
    def update_age(self, delta_time):
        """
        Advances age and recalculates capacity so cognitive growth is continuous
        rather than stepping at discrete milestones.
        """
        self.age += delta_time
        
        # Recalculate capacity and slots
        self.capacity = self.calculate_capacity()
        self.memory_slots = self.calculate_memory_slots()
        # Sense/action slots don't change with age in Phase 1
    
    def can_allocate_dna(self, points):
        """
        Guards DNA growth by checking remaining cognitive room.

        Earned DNA only converts to genetic capacity when the brain has room
        to process it — this prevents runaway DNA inflation in dots that have
        outgrown their cognitive architecture.
        """
        current_allocation = self.dna.get_allocated_points()
        return (current_allocation + points) <= self.capacity
    
    def add_memory(self, memory_type, data, reward_impact):
        """
        Records an experience in the memory buffer.

        FIFO eviction (pop from index 0) keeps the most recent experiences
        current rather than burying them under ancient history from juvenile
        behavior that may no longer reflect the dot's circumstances.
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
        Accumulates action outcome data for lifetime analysis.

        The reward history lets the generation summary identify which actions
        were profitable for this dot without needing to replay the simulation.
        """
        self.total_reward += reward_value
        
        if action_type not in self.action_rewards:
            self.action_rewards[action_type] = 0.0
        self.action_rewards[action_type] += reward_value
    
    def get_action_success_rate(self, action_type):
        """
        Aggregates memory into a success ratio for one action type.

        Returns 0.5 (neutral) when no data exists so callers treat unknown
        actions as neither promising nor dangerous rather than pessimistically
        avoiding them.
        """
        relevant_memories = [m for m in self.memories if m['type'] == action_type]
        
        if not relevant_memories:
            return 0.5  # No data, assume neutral
        
        # Positive rewards = successes
        successes = sum(1 for m in relevant_memories if m['reward'] > 0)
        return successes / len(relevant_memories)
    
    def get_memory_of_dot(self, dot_id):
        """
        Retrieves all memories of interactions with a specific dot.

        Used to check combat or mate history before committing to an action
        with a dot already encountered, so prior outcomes can inform the decision.
        """
        return [m for m in self.memories 
                if m['data'].get('target_id') == dot_id or 
                   m['data'].get('partner_id') == dot_id]
    
    def serialize(self):
        """Snapshot for the renderer and logger. Excludes raw memory objects to keep output serializable."""
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
