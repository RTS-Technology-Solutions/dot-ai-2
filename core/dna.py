"""
=====================================================================
DNA SYSTEM - THE GENETIC CODE OF LIFE 🧬
=====================================================================

Think of this as the "instruction manual" for each dot - just like how
your DNA determines if you have blue eyes or brown hair, a dot's DNA
decides if it can see far, run fast, or fight well!

KEY CONCEPT: Resource Allocation Trade-offs
Each dot has a "DNA budget" (default: 100 points). Want better vision?
You'll have fewer points for speed! This creates DIVERSITY - no single
"perfect" build exists. Some dots evolve as hunters, others as scouts,
others as reproducers.

REAL-WORLD PARALLEL:
This mirrors real biology! A cheetah evolved speed but sacrificed
strength. An elephant evolved strength but sacrificed speed. Every
organism makes genetic trade-offs based on survival needs.

HOW IT WORKS:
1. Each Gene has a switch (ON/OFF) and a point value (strength)
2. Genes are grouped into Brain, Sense, and Action categories
3. Total points can't exceed the budget (enforced by validation)
4. Sexual reproduction creates offspring by mixing parent genes
=====================================================================
"""

class Gene:
    """
    GENE: The Basic Building Block of DNA 🧬
    
    A gene is like a "skill" the dot can have. Each gene has:
    - enabled: Is this skill turned ON or OFF?
    - points: How strong is this skill? (0-50 typical range)
    
    Example:
    - vision_distance: enabled=True, points=15 → Can see 15 units away
    - attack: enabled=False, points=0 → Cannot attack at all
    
    BIOLOGY LESSON:
    This mirrors real genes! You have genes for eye color that are
    either "expressed" (enabled=True) or not. The gene's "strength"
    determines how much melanin you produce (points value).
    """
    
    def __init__(self, name, enabled=False, points=0):
        self.name = name           # Gene identifier (e.g., "vision_distance")
        self.enabled = enabled     # Is this gene active?
        self.points = points       # How many DNA points invested?
    
    def to_dict(self):
        """
        Serialize gene to dictionary format
        Used for saving/loading and sending DNA over networks
        """
        return {
            'enabled': self.enabled,
            'points': self.points
        }
    
    @classmethod
    def from_dict(cls, name, data):
        """
        Recreate a gene from dictionary data
        Used when loading saved genomes or receiving DNA from network
        """
        return cls(name, data['enabled'], data['points'])
    
    def __repr__(self):
        """
        Human-readable gene description
        Example: "Gene(vision_distance: ON, 15 pts)"
        """
        status = "ON" if self.enabled else "OFF"
        return f"Gene({self.name}: {status}, {self.points} pts)"


class DNAProfile:
    """
    =====================================================================
    DNA PROFILE: The Complete Genetic Blueprint 📋
    =====================================================================
    
    This is the ENTIRE genetic code for one dot - like a complete genome!
    It contains ALL possible genes organized into three categories:
    
    🧠 BRAIN GENES: Cognitive capacity (how smart the dot is)
       - memory_size: How much information can it remember?
       - sense_slots: How many different senses can it process?
       - action_slots: How many different actions can it consider?
    
    👁️ SENSE GENES: What can the dot perceive?
       - vision_distance: How far can it see?
       - vision_fov: How wide is its field of view? (degrees)
       - dot_detection: Can it sense other dots?
       - food_detection: Can it smell food?
       - dna_strength_detection: Can it identify strong vs weak opponents?
    
    💪 ACTION GENES: What can the dot DO?
       - movement_speed: How fast can it move?
       - attack: Combat damage capability
       - defend: Damage reduction when defending
       - replicate: Can it reproduce? (asexual or sexual)
    
    THE BUDGET SYSTEM:
    Each dot has a total_points budget (default: 100). Every gene with
    points > 0 COSTS those points. This creates strategic choices!
    
    Example:
    - Spend 20 points on vision → Only 80 left for other abilities
    - Spend 30 points on attack → Only 70 left for speed/senses
    
    WHY THIS MATTERS:
    This forces dots to SPECIALIZE. A dot can't be perfect at everything!
    This creates ECOLOGICAL NICHES:
    - Hunters: High attack, high vision → Find and kill prey
    - Scouts: High speed, high vision → Explore and find food
    - Tanks: High defend, moderate attack → Survive battles
    - Breeders: High replicate → Rapid population growth
    
    EVOLUTION DISCOVERS THE BEST MIX!
    We don't program which build is "best" - the simulation finds it
    through natural selection over many generations.
    =====================================================================
    """
    
    def __init__(self, total_points=100):
        """
        Initialize a DNA profile with default gene configuration
        
        STARTING GENES:
        We enable basic survival genes by default (vision, movement, eating)
        Advanced genes (attack, defend, replicate) start disabled until
        evolution discovers they're useful.
        
        This mirrors real evolution: Complex traits evolve over time,
        they don't appear fully-formed in the first generation!
        """
        self.total_points = total_points  # Total DNA points available (starting budget)
        self.earned_dna_points = 0  # DNA points earned during lifetime (Phase 4: Reward-based growth)
        
        # ===== BRAIN GENES: Cognitive Capacity =====
        # These determine how "smart" the dot is
        
        self.brain_memory = Gene("memory", enabled=True, points=8)
        # 📚 Memory: How many past experiences the dot remembers
        # Higher = better decision-making (learns from mistakes)
        
        self.brain_sense_slots = Gene("sense_slots", enabled=True, points=10)
        # 👁️ Sense Slots: How many things it can perceive simultaneously
        # Higher = aware of more food/threats at once
        
        self.brain_action_slots = Gene("action_slots", enabled=True, points=7)
        # 🎯 Action Slots: How many possible actions it can evaluate
        # Higher = considers more options (attack? flee? eat?)
        
        # ===== SENSE GENES: Perception Systems =====
        # What can the dot detect in its environment?
        
        self.vision_distance = Gene("vision_distance", enabled=True, points=15)
        # 🔭 Vision Distance: How far the dot can see (in pixels)
        # 15 points = ~150 pixel range
        
        self.vision_fov = Gene("vision_fov", enabled=True, points=15)
        # 📐 Field of View: Vision cone angle (in degrees)
        # 15 points = ~150 degree FOV (wide peripheral vision)
        
        self.dot_detection = Gene("dot_detection", enabled=True, points=7)
        # 🔵 Dot Detection: Can it sense other dots?
        # Essential for combat and mating!
        
        self.food_detection = Gene("food_detection", enabled=True, points=10)
        # 🍎 Food Detection: Can it smell/see food?
        # Essential for survival!
        
        self.power_detection = Gene("power_detection", enabled=False, points=0)
        # ⚡ Power Detection: Can it sense power-ups? (Future feature)
        
        self.food_amount_detection = Gene("food_amount_detection", enabled=False, points=0)
        # 📊 Food Amount: Can it tell how MUCH energy a food has?
        # Strategic advantage - prioritize high-value food
        
        self.dna_strength_detection = Gene("dna_strength_detection", enabled=False, points=0)
        # 💪 DNA Strength: Can it identify strong vs weak opponents?
        # Crucial for smart hunting - avoid tough enemies, target weak ones
        
        self.nearby_dot_density = Gene("nearby_dot_density", enabled=True, points=8)
        # 🔢 Nearby Dot Density: Sense concentration of dots in area
        # Helps avoid crowding, detect threats, find social groups
        # Higher points = larger detection radius for density awareness
        
        self.social_sense = Gene("social_sense", enabled=False, points=0)
        # 👥 Social Sense: Can it detect alliances/relationships? (Future)
        
        # ===== ACTION GENES: Physical Capabilities =====
        # What can the dot physically DO?
        
        self.movement_speed = Gene("movement_speed", enabled=True, points=8)
        # 🏃 Movement Speed: Pixels per second movement rate
        # 8 points = ~80 px/s base speed (increased when hungry)
        
        self.movement_max_energy = Gene("movement_max_energy", enabled=True, points=10)
        # 🔋 Max Energy: Maximum energy storage capacity
        # Higher = can go longer without food
        
        self.defend = Gene("defend", enabled=True, points=5)
        # 🛡️ Defend: Damage reduction when in defensive stance
        # 5 points = -25% damage taken
        
        self.attack = Gene("attack", enabled=True, points=5)
        # ⚔️ Attack: Damage dealt to enemies in combat
        # 5 points = ~25 damage per attack
        
        self.eat = Gene("eat", enabled=True, points=0)
        # 🍴 Eat: ALWAYS enabled, no cost (all dots must eat to survive!)
        # This is a "fundamental right" - you can't disable eating
        
        self.replicate = Gene("replicate", enabled=False, points=0)
        # 👶 Replicate: Can reproduce (asexual or sexual)
        # Must be evolved - not all dots can reproduce!
        
        self.revive = Gene("revive", enabled=False, points=0)
        # 💚 Revive: Can resurrect dead allies (Future cooperative feature)
    
    def get_all_genes(self):
        """
        Return list of ALL genes in this DNA profile
        
        This uses Python introspection to find all Gene objects
        attached to this DNA profile. Useful for iteration!
        """
        genes = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, Gene):
                genes.append(attr)
        return genes
    
    def get_allocated_points(self):
        """
        Calculate TOTAL DNA points currently allocated to genes
        
        This sums up all the points from every enabled gene.
        Example: vision(15) + speed(8) + attack(5) = 28 points allocated
        
        VALIDATION CHECK:
        allocated_points MUST be ≤ total_points (the budget!)
        """
        return sum(gene.points for gene in self.get_all_genes())
    
    def get_gene_value(self, gene_name):
        """
        Get the effective point value for a specific gene
        
        Returns 0 if:
        - Gene is disabled (enabled=False)
        - Gene doesn't exist
        
        Otherwise returns the gene's point value.
        
        USAGE:
        This is how the simulation reads gene strength!
        speed = dna.get_gene_value("movement_speed")  # Returns 8 if enabled
        """
        if hasattr(self, gene_name):
            gene = getattr(self, gene_name)
            if isinstance(gene, Gene):
                return gene.points if gene.enabled else 0
        return 0
    
    def get_total_points(self):
        """
        Get total DNA budget (starting + earned)
        
        Phase 4: Dots earn DNA points during their lifetime based on successful actions.
        Offspring inherit their parent's EARNED DNA total, creating evolutionary pressure
        toward successful strategies.
        
        TOTAL DNA BUDGET = starting budget + earned points
        """
        return self.total_points + self.earned_dna_points
    
    def earn_dna_points(self, amount):
        """
        Award DNA points for successful actions during lifetime.
        
        Phase 4: Reward-based DNA growth
        - Dots that survive longer earn more DNA
        - Successful actions grant DNA growth
        - Offspring inherit parent's earned DNA total
        
        This creates evolutionary pressure: Successful parents → stronger offspring!
        """
        if amount > 0:
            self.earned_dna_points += amount
    
    def get_available_points(self):
        """
        Calculate how many DNA points are still UNUSED
        
        Formula: available = budget - allocated
        Example: 100 total - 85 allocated = 15 points available
        
        USE CASE:
        Check if dot can afford to evolve a new gene!
        if dna.get_available_points() >= 10:
            enable_new_ability()
        """
        return self.total_points - self.get_allocated_points()
    
    def is_valid(self):
        """
        Validate that DNA doesn't exceed budget
        
        CRITICAL SAFETY CHECK:
        Prevents "over-allocated" DNA profiles where total gene points
        exceed the available budget. Invalid DNA can crash the simulation!
        
        Returns True if: allocated ≤ total_points
        Returns False if: allocated > total_points (BUDGET OVERFLOW!)
        """
        allocated = self.get_allocated_points()
        return allocated <= self.total_points
    
    def unlock_random_ability(self):
        """
        Enable a random currently-disabled gene
        
        EVOLUTION IN ACTION!
        This simulates "genetic mutation" - randomly gaining new abilities.
        
        Returns:
        - True if a gene was enabled
        - False if all genes are already enabled (no more mutations possible)
        
        NOTE: The "eat" gene is excluded - it's ALWAYS enabled!
        
        USAGE:
        When a dot survives a long time, it might "evolve" a new ability
        as a reward for successful adaptation.
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
        """
        Increase the total DNA budget
        
        USE CASE:
        Reward successful dots with more genetic potential!
        Example: Survive 5 minutes → gain +10 DNA points
        
        This allows dots to evolve MORE COMPLEX over time.
        Simple organisms → Complex organisms
        """
        self.total_points += points
    
    def serialize(self):
        """
        Convert DNA profile to dictionary format for saving/transmitting
        
        IMPORTANT FOR:
        - Saving genomes to disk
        - Sending DNA over network (multiplayer)
        - Analyzing evolution data
        
        Returns a complete snapshot of the genome state.
        """
        return {
            'total_points': self.total_points,
            'earned_dna_points': self.earned_dna_points,
            'allocated_points': self.get_allocated_points(),
            'genes': {gene.name: gene.to_dict() for gene in self.get_all_genes()}
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Recreate a DNA profile from serialized dictionary
        
        DESERIALIZATION:
        Reverse of serialize() - takes saved data and rebuilds DNA.
        
        USAGE:
        - Load saved genomes from disk
        - Receive DNA from network
        - Clone champion genomes for testing
        """
        profile = cls(total_points=data['total_points'])
        profile.earned_dna_points = data.get('earned_dna_points', 0)  # Phase 4: Restore earned DNA
        for gene_name, gene_data in data['genes'].items():
            if hasattr(profile, gene_name):
                gene = getattr(profile, gene_name)
                gene.enabled = gene_data['enabled']
                gene.points = gene_data['points']
        return profile
    
    def clone(self):
        """
        Create an exact copy of this DNA profile
        
        DEEP COPY:
        Changes to the clone won't affect the original!
        
        USAGE:
        - Asexual reproduction (parent clones itself)
        - Testing "what-if" scenarios
        - Preserving champion genomes
        
        BIOLOGY PARALLEL:
        This is like bacteria reproduction - one cell splits into
        two identical cells with the same DNA!
        """
        return DNAProfile.from_dict(self.serialize())
    
    @staticmethod
    def crossover(parent_a, parent_b):
        """
        =====================================================================
        SEXUAL REPRODUCTION: DNA Crossover & Genetic Mixing 💕
        =====================================================================
        
        This is the HEART of sexual reproduction! Two parents combine their
        DNA to create offspring with a MIX of both genetic codes.
        
        WHY SEXUAL REPRODUCTION?
        In nature, sexual reproduction creates GENETIC DIVERSITY:
        - Parent A: Fast runner, weak fighter
        - Parent B: Slow runner, strong fighter
        - Child: MAYBE fast AND strong! (best of both)
        - OR: Maybe slow AND weak (worst of both)
        
        This randomness is CRUCIAL for evolution:
        - Some offspring will be better than parents (breakthrough!)
        - Some will be worse (evolutionary dead-end)
        - Only the BEST survive and pass on genes
        
        THE ALGORITHM:
        1. Average the DNA budgets: child gets (100 + 120) / 2 = 110 points
        2. For each gene:
           - Enabled state: 50/50 chance from either parent
           - Points value: Average both parents ± random variation
        3. Validation: Scale down if total exceeds budget
        
        BIOLOGY LESSON:
        This mirrors real sexual reproduction! You get ~50% of genes from
        mom, ~50% from dad. But WHICH genes? Random! That's why siblings
        look different despite having the same parents.
        
        MACHINE LEARNING CONCEPT:
        This is a "genetic algorithm" - we're searching the solution space
        by combining successful strategies and adding random variation.
        Over generations, optimal DNA patterns emerge!
        =====================================================================
        """
        import random
        
        # STEP 1: Create child with averaged DNA budget
        # Child inherits total capacity (starting + earned) from both parents
        # Phase 4: This now includes DNA points parents earned during their lifetime!
        avg_points = (parent_a.get_total_points() + parent_b.get_total_points()) // 2
        child_dna = DNAProfile(total_points=avg_points)
        
        # Get dictionaries of all parent genes for lookup
        parent_a_genes = {gene.name: gene for gene in parent_a.get_all_genes()}
        parent_b_genes = {gene.name: gene for gene in parent_b.get_all_genes()}
        
        # STEP 2: Crossover each gene from both parents
        for gene in child_dna.get_all_genes():
            gene_name = gene.name
            
            # SPECIAL CASE: "eat" gene always enabled (fundamental survival)
            if gene_name == "eat":
                gene.enabled = True
                gene.points = 0
                continue
            
            # Get corresponding genes from both parents
            gene_a = parent_a_genes.get(gene_name)
            gene_b = parent_b_genes.get(gene_name)
            
            if gene_a and gene_b:
                # INHERITANCE: Enabled state (50/50 random from either parent)
                # Example:
                #   Parent A: attack=ON,  Parent B: attack=OFF
                #   Child: 50% chance ON, 50% chance OFF
                gene.enabled = gene_a.enabled if random.random() < 0.5 else gene_b.enabled
                
                # POINTS: Average with random mutation
                if gene.enabled:
                    # Average both parent values
                    # Parent A: 10 points, Parent B: 20 points → avg = 15
                    avg = (gene_a.points + gene_b.points) / 2.0
                    
                    # Add small random variation (-2 to +2)
                    # This is MUTATION - small random changes!
                    # avg=15 + variation(-2 to +2) → final: 13 to 17
                    variation = random.randint(-2, 2)
                    
                    # Clamp to valid range (0-50)
                    gene.points = max(0, min(50, int(avg) + variation))
                else:
                    # If gene disabled, no points allocated
                    gene.points = 0
        
        # STEP 3: Budget Validation & Scaling
        # If total gene points > available budget, scale down proportionally
        allocated = child_dna.get_allocated_points()
        total_budget = child_dna.get_total_points()  # Phase 4: Use total (starting + earned)
        if allocated > total_budget:
            # PROPORTIONAL SCALING:
            # Example: 120 points allocated, 100 budget
            # scale_factor = 100/120 = 0.833
            # All genes multiplied by 0.833 to fit budget
            scale_factor = total_budget / allocated
            for gene in child_dna.get_all_genes():
                if gene.enabled and gene.name != "eat":
                    gene.points = int(gene.points * scale_factor)
        
        # Return the new offspring DNA!
        return child_dna
    
    def __repr__(self):
        """
        String representation for debugging and logging
        
        Example output:
        "DNAProfile(85/100 points, 12 genes active)"
        
        Shows:
        - allocated/total points
        - how many genes are currently enabled
        """
        allocated = self.get_allocated_points()
        active_count = sum(1 for g in self.get_all_genes() if g.enabled)
        return f"DNAProfile({allocated}/{self.total_points} points, {active_count} genes active)"
