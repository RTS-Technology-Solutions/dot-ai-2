"""
Food System - Food Entities
Handles food creation, consumption, and depletion
"""

class Food:
    """
    Food entity that dots can consume
    - Provides energy when eaten
    - Can be partially consumed
    - Depletes and disappears when empty
    """
    
    def __init__(self, food_id, position, energy_value):
        self.id = food_id
        self.position = list(position)  # [x, y]
        self.energy_value = energy_value
        self.max_energy = energy_value
        self.depleted = False
    
    def consume(self, amount):
        """
        Consume food energy
        Returns: Amount actually consumed (may be less than requested)
        """
        if self.depleted:
            return 0
        
        # Take up to requested amount
        taken = min(amount, self.energy_value)
        self.energy_value -= taken
        
        # Mark as depleted if empty
        if self.energy_value <= 0:
            self.energy_value = 0
            self.depleted = True
        
        return taken
    
    def get_energy_ratio(self):
        """Get remaining energy as ratio 0-1"""
        return self.energy_value / self.max_energy if self.max_energy > 0 else 0
    
    def serialize(self):
        """Export food state for rendering"""
        # Size scales with remaining energy
        base_size = 3
        max_size = 8
        size = base_size + (self.get_energy_ratio() * (max_size - base_size))
        
        return {
            'id': self.id,
            'position': self.position,
            'energy_value': self.energy_value,
            'max_energy': self.max_energy,
            'energy_ratio': self.get_energy_ratio(),
            'size': int(size),
            'depleted': self.depleted
        }
    
    def __repr__(self):
        return f"Food({self.id}: {self.energy_value:.0f}/{self.max_energy:.0f} at {self.position})"
