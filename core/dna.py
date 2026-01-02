"""
DNA System - Genetic Profile Management
Handles genes (switches + points), validation, and serialization
"""

class Gene:
    """Individual gene with binary switch and point allocation"""
    
    def __init__(self, name, enabled=False, points=0):
        self.name = name
        self.enabled = enabled
        self.points = points
    
    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'enabled': self.enabled,
            'points': self.points
        }
    
    @classmethod
    def from_dict(cls, name, data):
        """Deserialize from dictionary"""
        return cls(name, data['enabled'], data['points'])
    
    def __repr__(self):
        status = "ON" if self.enabled else "OFF"
        return f"Gene({self.name}: {status}, {self.points} pts)"


class DNAProfile:
    """
    Complete genetic profile for a dot
    Manages all genes with validation and inheritance
    """
    
    def __init__(self, total_points=100):
        self.total_points = total_points
        
        # BRAIN GENES
        self.brain_memory = Gene("memory", enabled=True, points=8)  # Reduced from 10
        self.brain_sense_slots = Gene("sense_slots", enabled=True, points=10)  # Reduced from 12
        self.brain_action_slots = Gene("action_slots", enabled=True, points=7)  # Reduced from 8
        
        # SENSE GENES
        self.vision_distance = Gene("vision_distance", enabled=True, points=15)
        self.vision_fov = Gene("vision_fov", enabled=True, points=15)
        self.dot_detection = Gene("dot_detection", enabled=True, points=7)  # Reduced from 8
        self.food_detection = Gene("food_detection", enabled=True, points=10)  # Reduced from 12
        self.power_detection = Gene("power_detection", enabled=False, points=0)
        self.food_amount_detection = Gene("food_amount_detection", enabled=False, points=0)
        self.dna_strength_detection = Gene("dna_strength_detection", enabled=False, points=0)
        self.social_sense = Gene("social_sense", enabled=False, points=0)
        
        # ACTION GENES
        self.movement_speed = Gene("movement_speed", enabled=True, points=8)
        self.movement_max_energy = Gene("movement_max_energy", enabled=True, points=10)  # Reduced from 12
        self.defend = Gene("defend", enabled=True, points=5)  # Enable combat
        self.attack = Gene("attack", enabled=True, points=5)  # Enable combat
        self.eat = Gene("eat", enabled=True, points=0)  # Always enabled, no cost
        self.replicate = Gene("replicate", enabled=False, points=0)
        self.revive = Gene("revive", enabled=False, points=0)
    
    def get_all_genes(self):
        """Return list of all genes"""
        genes = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, Gene):
                genes.append(attr)
        return genes
    
    def get_allocated_points(self):
        """Calculate total points currently allocated"""
        return sum(gene.points for gene in self.get_all_genes())
    
    def get_gene_value(self, gene_name):
        """Get the points value for a gene (returns 0 if disabled or doesn't exist)"""
        if hasattr(self, gene_name):
            gene = getattr(self, gene_name)
            if isinstance(gene, Gene):
                return gene.points if gene.enabled else 0
        return 0
    
    def get_total_points(self):
        """Get total DNA points allocated (alias for get_allocated_points)"""
        return self.get_allocated_points()
    
    def get_available_points(self):
        """Calculate remaining unallocated points"""
        return self.total_points - self.get_allocated_points()
    
    def is_valid(self):
        """Check if DNA profile is valid"""
        allocated = self.get_allocated_points()
        return allocated <= self.total_points
    
    def unlock_random_ability(self):
        """
        Unlock a random disabled gene
        Returns True if successful, False if all enabled
        """
        import random
        disabled_genes = [g for g in self.get_all_genes() 
                         if not g.enabled and g.name != "eat"]
        
        if disabled_genes:
            gene = random.choice(disabled_genes)
            gene.enabled = True
            return True
        return False
    
    def add_dna_points(self, points):
        """Add points to total DNA budget"""
        self.total_points += points
    
    def serialize(self):
        """Export to dictionary for saving/networking"""
        return {
            'total_points': self.total_points,
            'allocated_points': self.get_allocated_points(),
            'genes': {gene.name: gene.to_dict() for gene in self.get_all_genes()}
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create DNA profile from serialized data"""
        profile = cls(total_points=data['total_points'])
        for gene_name, gene_data in data['genes'].items():
            if hasattr(profile, gene_name):
                gene = getattr(profile, gene_name)
                gene.enabled = gene_data['enabled']
                gene.points = gene_data['points']
        return profile
    
    def clone(self):
        """Create a deep copy of this DNA profile"""
        return DNAProfile.from_dict(self.serialize())
    
    def __repr__(self):
        allocated = self.get_allocated_points()
        return f"DNAProfile({allocated}/{self.total_points} points, {sum(1 for g in self.get_all_genes() if g.enabled)} genes active)"
