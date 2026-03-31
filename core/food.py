"""
Food is its own class rather than a position/value tuple because it can be
partially consumed. A dot that eats only some of a piece of food does not
remove it — the remainder stays available for other dots. That model requires
persistent state, which is what makes a class necessary here instead of a
simple coordinate.
"""

class Food:
    """
    One food item in the world.

    The partial consumption model (consume() depletes rather than removes)
    is why this is a class and not a plain coordinate — the energy_value
    state must survive between the moment a dot starts eating and when the
    item is fully exhausted. Multiple dots can visit the same item on
    different ticks and each finds what’s left.
    """
    
    def __init__(self, food_id, position, energy_value):
        self.id = food_id
        self.position = list(position)  # [x, y]
        self.energy_value = energy_value
        self.max_energy = energy_value
        self.depleted = False
    
    def consume(self, amount):
        """
        Takes up to `amount` energy from this item.

        Returns the actual amount taken so callers can account for partial
        pickups — a dot arriving at a near-empty item gets only what’s left,
        not a full serving.
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
        """
        Returns remaining energy as a 0–1 fraction.

        Used by the renderer to size the food dot — smaller items are more
        depleted, giving foragers a visual signal about patch quality.
        """
        return self.energy_value / self.max_energy if self.max_energy > 0 else 0
    
    def serialize(self):
        """
        Snapshot for the renderer.

        Size is derived here from energy_ratio so the renderer doesn’t need
        to implement the sizing formula — it just draws what serialize() provides.
        """
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
