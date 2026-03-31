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

from configs import get_config


class Gene:
    """
    A single tunable trait in a dot's genome.

    Exists as a separate class rather than a plain number because a gene
    has two independent dimensions: whether it is active at all (enabled)
    and how strongly it is expressed (points). A disabled gene consumes
    no budget and produces no effect — dot logic checks enabled before
    applying any gene's formula, so this is a clean on/off gate.

    Separating enabled from points also lets crossover and mutation
    affect them independently: a gene can toggle on without gaining
    points, or gain points without toggling — matching the biology of
    gene expression vs. gene dosage.
    """
    
    def __init__(self, name, enabled=False, points=0):
        self.name = name           # Gene identifier (e.g., "vision_distance")
        self.enabled = enabled     # Is this gene active?
        self.points = points       # How many DNA points invested?
    
    def to_dict(self):
        """Serialize to dict so DNA can be logged and reconstructed across sessions."""
        return {
            'enabled': self.enabled,
            'points': self.points
        }
    
    @classmethod
    def from_dict(cls, name, data):
        """Reconstruct a gene from logged data — needed for session replay and analysis."""
        return cls(name, data['enabled'], data['points'])
    
    def __repr__(self):
        """Short label for console output — human-scannable without printing the full gene table."""
        status = "ON" if self.enabled else "OFF"
        return f"Gene({self.name}: {status}, {self.points} pts)"


class DNAProfile:
    """
    The complete genome for one dot.

    Exists as its own class because the genome is shared across multiple
    systems — brain capacity, sense ranges, action availability, and
    resource limits all read from the same DNA object. A standalone class
    lets each system query only the genes it cares about without coupling
    to the others.

    The budget system (total_points) is enforced here rather than in
    each consuming system so that the constraint has one source of truth.
    A DNAProfile can only produce dots within its budget — any crossover
    or mutation that would exceed it is automatically corrected.

    earned_dna_points creates a second layer of selection pressure:
    dots that behave successfully during their lifetime grow the DNA
    budget their offspring inherit, rewarding strategies that generate
    energy surpluses beyond what survival alone requires.
    """
    
    def __init__(self, total_points=100):
        """
        Initialize with defaults drawn from config so gene starting values
        can be tuned per experiment profile without touching this class.

        Basic survival genes start enabled because a dot that cannot
        perceive or move cannot survive long enough to demonstrate any
        other gene's value to the selection process.

        Advanced genes (replicate, dna_strength_detection) start disabled
        so the simulation must discover their value through mutation rather
        than receiving them as gifts — this mirrors the evolutionary
        challenge of evolving complex traits from simpler precursors.
        """
        self.total_points = total_points  # DNA budget cap — scarcity is what makes gene allocation meaningful
        self.earned_dna_points = 0  # Lifetime behavioral reward → inherited budget; creates pressure beyond just surviving

        # Load gene defaults from config
        _gd = get_config().dna.gene_defaults

        # ===== BRAIN GENES =====
        # These exist because cognitive capacity should cost something.
        # A dot that perceives everything and evaluates all options with perfect memory
        # would trivialize selection — the budget forces triage.
        
        self.brain_memory = Gene("memory", enabled=_gd.brain_memory_enabled, points=_gd.brain_memory_points)
        # Without this, every frame is a fresh start — no way to reinforce or avoid experienced patterns
        
        self.brain_sense_slots = Gene("sense_slots", enabled=_gd.brain_sense_slots_enabled, points=_gd.brain_sense_slots_points)
        # Limits how many simultaneous inputs the brain processes — forces the dot to prioritize what it notices
        
        self.brain_action_slots = Gene("action_slots", enabled=_gd.brain_action_slots_enabled, points=_gd.brain_action_slots_points)
        # Limits the candidate-action pool evaluated per frame — triage pressure on the decision engine
        
        # ===== SENSE GENES =====
        # These exist because dots with no perception cannot react to anything.
        # Sense gene investment is what converts environmental information into decision inputs.
        
        self.vision_distance = Gene("vision_distance", enabled=_gd.vision_distance_enabled, points=_gd.vision_distance_points)
        # Determines reaction window — a short-sighted dot gets ambushed because detection and contact happen simultaneously
        
        self.vision_fov = Gene("vision_fov", enabled=_gd.vision_fov_enabled, points=_gd.vision_fov_points)
        # Narrows the directional blind spot — at max points this approaches 360° and eliminates ambush vulnerability
        
        self.dot_detection = Gene("dot_detection", enabled=_gd.dot_detection_enabled, points=_gd.dot_detection_points)
        # Omnidirectional — a dot that can only see forward still needs to know when something is behind it
        
        self.food_detection = Gene("food_detection", enabled=_gd.food_detection_enabled, points=_gd.food_detection_points)
        # Omnidirectional scent-analog — without this, food that falls outside the vision cone is invisible
        
        self.power_detection = Gene("power_detection", enabled=_gd.power_detection_enabled, points=_gd.power_detection_points)
        # Reserved for future power-up mechanics — disabled until those features exist
        
        self.food_amount_detection = Gene("food_amount_detection", enabled=_gd.food_amount_detection_enabled, points=_gd.food_amount_detection_points)
        # Lets a dot prioritize high-energy food vs. depleted scraps — strategic foraging requires knowing what to chase
        
        self.dna_strength_detection = Gene("dna_strength_detection", enabled=_gd.dna_strength_detection_enabled, points=_gd.dna_strength_detection_points)
        # Disabled by default — must be evolved because knowing opponent strength makes predation optimal,
        # and we don't want to hand that advantage to first-generation dots
        
        self.nearby_dot_density = Gene("nearby_dot_density", enabled=_gd.nearby_dot_density_enabled, points=_gd.nearby_dot_density_points)
        # Needed for crowding-aware reproduction decisions — a dot that can't sense density reproduces into overcrowding
        
        self.social_sense = Gene("social_sense", enabled=_gd.social_sense_enabled, points=_gd.social_sense_points)
        # Reserved for cooperative mechanics — disabled until alliance/relationship features are implemented
        
        # ===== ACTION GENES =====
        # These exist because every behavior should cost something to unlock.
        # An action gene being disabled is a categorical limitation, not a weak version of the action —
        # a dot with attack disabled never enters combat logic at all.
        
        self.movement_speed = Gene("movement_speed", enabled=_gd.movement_speed_enabled, points=_gd.movement_speed_points)
        # Faster movement improves both pursuit and escape, but every point here cannot go to attack or senses
        
        self.movement_max_energy = Gene("movement_max_energy", enabled=_gd.movement_max_energy_enabled, points=_gd.movement_max_energy_points)
        # A higher energy ceiling extends how far a dot can forage before starvation forces it back
        
        self.defend = Gene("defend", enabled=_gd.defend_enabled, points=_gd.defend_points)
        # Damage reduction while stationary — the cost is the actions foregone while defending
        
        self.attack = Gene("attack", enabled=_gd.attack_enabled, points=_gd.attack_points)
        # Enables combat — high food reward on kill, energy cost on miss, health risk if target fights back
        
        self.eat = Gene("eat", enabled=True, points=0)
        # Always enabled with no cost — eating is a prerequisite for all other strategies, not a strategy itself
        
        self.replicate = Gene("replicate", enabled=_gd.replicate_enabled, points=_gd.replicate_points)
        # Disabled by default — a dot that has not evolved reproduction carries its DNA to extinction
        
        self.revive = Gene("revive", enabled=_gd.revive_enabled, points=_gd.revive_points)
        # Reserved for cooperative revival mechanics — disabled until that system is implemented
    
    def get_all_genes(self):
        """
        Returns all Gene objects via introspection.

        Exists so iteration-based operations (validation, logging, mutation)
        don't need to maintain a separate registry that can drift out of sync
        with the actual gene attributes.
        """
        genes = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, Gene):
                genes.append(attr)
        return genes
    
    def get_allocated_points(self):
        """
        Sum of all gene point values — needed to enforce the budget cap.

        Called by is_valid() and by crossover after mutations to ensure
        DNA integrity before an offspring is created.
        """
        return sum(gene.points for gene in self.get_all_genes())
    
    def get_gene_value(self, gene_name):
        """
        Returns the effective strength of a gene, or 0 if disabled/missing.

        Consuming systems call this instead of reading gene attributes
        directly so they get a 0 for disabled genes without needing to
        check the enabled flag themselves. Disabled = zero effect,
        regardless of stored point value.
        """
        if hasattr(self, gene_name):
            gene = getattr(self, gene_name)
            if isinstance(gene, Gene):
                return gene.points if gene.enabled else 0
        return 0
    
    def get_total_points(self):
        """
        Returns the full DNA budget including lifetime-earned points.

        Earned points are added to the inherited budget so offspring of
        high-performing parents start with more allocation capacity —
        the key mechanism linking individual behavior to generational fitness.
        """
        return self.total_points + self.earned_dna_points
    
    def earn_dna_points(self, amount):
        """
        Records behavioral success as an inherited budget increase.

        Called by the resources cascade when a dot has full energy AND
        full health and keeps eating — meaning it is thriving, not just
        surviving. That surplus converts to offspring advantage.
        """
        if amount > 0:
            self.earned_dna_points += amount
    
    def get_available_points(self):
        """Remaining budget — used to check whether a gene can be strengthened before committing."""
        return self.total_points - self.get_allocated_points()
    
    def is_valid(self):
        """
        Guards against over-allocation before offspring are created.

        The budget constraint only matters if it is actually enforced.
        Calling this after every crossover and mutation prevents an
        invalid genome from silently entering the population.
        """
        allocated = self.get_allocated_points()
        return allocated <= self.total_points
    
    def unlock_random_ability(self):
        """
        Enables one randomly-chosen disabled gene.

        The "eat" gene is excluded because it is always on — including it
        would waste mutation events on a no-op.

        Returns True if a gene was unlocked, False if all genes are
        already active so callers can decide whether to fall back to
        a different mutation strategy.
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
        Expands the inherited budget directly.

        Used when an external system wants to increase a dot's genetic
        potential in a tracked way that is preserved through crossover.
        """
        self.total_points += points
    
    def serialize(self):
        """
        Converts the genome to a plain dict for logging and persistence.

        Paired with from_dict() to form the save/load round-trip. The
        combined gene dict is what the metrics logger reads when recording
        lineage data.
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
        Reconstructs a genome from a previously serialized dict.

        Used by the logger when reloading saved sessions and by clone()
        to produce independent copies that do not share gene references
        with the original.
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
        Deep-copies this genome via serialize/from_dict.

        The round-trip through plain data ensures no gene object is shared
        between original and clone — mutations to one cannot silently
        affect the other.
        """
        return DNAProfile.from_dict(self.serialize())
    
    @staticmethod
    def crossover(parent_a, parent_b):
        """
        Produces one offspring genome by blending two parent genomes.

        Budget is averaged so a high-earning parent lifts the child's
        capacity, giving behavioral success measurable influence over
        the next generation's genetic range.

        Each gene's enabled flag is drawn randomly from one parent (50/50).
        Points are averaged then jittered ±2 to introduce variation without
        discarding either parent's strategy entirely. Over many generations
        this random walk finds combinations neither parent could reach alone.

        If the resulting allocation exceeds the budget, all gene values are
        scaled down proportionally rather than truncated arbitrarily, so the
        relative specialization ratios of the parents are preserved.
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
        """One-line budget and activity summary for console output and logs."""
        allocated = self.get_allocated_points()
        active_count = sum(1 for g in self.get_all_genes() if g.enabled)
        return f"DNAProfile({allocated}/{self.total_points} points, {active_count} genes active)"
