"""
=====================================================================
SIMULATION ENGINE - THE WORLD WHERE DOTS EVOLVE 🌍
=====================================================================

This is the "game engine" - the core logic that runs the entire
ecosystem simulation. Think of it as the "laws of physics" for
the dot world!

WHAT THIS FILE DOES:
- Creates and manages all dots (living agents)
- Spawns and tracks food resources
- Runs the update loop (like a game engine's tick())
- Handles reproduction (sexual & asexual)
- Manages combat and death
- Triggers generational evolution
- Tracks metrics for analysis

KEY CONCEPTS:

1. ENTITY MANAGEMENT:
   - Dots: Living agents with DNA, energy, health
   - Food: Resource items that dots consume for energy

2. THE UPDATE LOOP (60 times per second):
   - Dots perceive their environment (vision)
   - Dots decide what to do (utility-based AI)
   - Dots execute actions (move, eat, attack, reproduce)
   - Energy drains, health changes
   - Dead dots removed, food spawned

3. NATURAL SELECTION:
   - Dots with good DNA survive longer
   - Survivors reproduce and pass on genes
   - Weak strategies die out quickly
   - Strong strategies spread through population

4. GENERATIONAL EVOLUTION:
   - If ALL dots die → Generation failed
   - Simulation restarts with RANDOMIZED DNA
   - Each restart tries different genetic strategies
   - Over many generations, optimal builds emerge

REAL-WORLD PARALLEL:
This is like running Earth's evolution on fast-forward! We create
the environment and rules, then let natural selection discover
what works. We don't TELL dots how to behave - they figure it out
through millions of tiny survival decisions over many generations.
=====================================================================
"""

import random
import math
from .dot import Dot
from .food import Food
from .dna import DNAProfile
from .metrics_logger import MetricsLogger


class DotSimulation:
    """
    =====================================================================
    SIMULATION ENGINE: The Living World
    =====================================================================
    
    This class is the "universe" where dots live, compete, and evolve.
    It manages:
    - Time (delta time updates)
    - Space (world bounds, positions)
    - Life (dots, food, births, deaths)
    - Evolution (generations, DNA inheritance)
    
    THE SIMULATION LOOP:
    1. update() called 60 times/second
    2. Each dot perceives → decides → acts
    3. Resources consumed, energy drained
    4. Reproduction happens (if conditions met)
    5. Deaths processed
    6. Metrics tracked
    7. Repeat!
    
    GENERATIONAL CYCLE:
    Gen 1: Random DNA → Some dots die, some survive → Survivors reproduce
    Gen 2: Inherited DNA → Better strategies emerge → Weak strategies removed
    Gen N: Optimal DNA discovered → Dominant strategy stabilizes
    
    EXTINCTION & RESTART:
    If all dots die:
    - Current generation deemed "failed"
    - Print generation summary (survival time, deaths, etc.)
    - Randomize DNA and spawn new generation
    - Evolution tries again with different strategies!
    
    This teaches: THERE IS NO SINGLE "CORRECT" DNA PROFILE!
    Success depends on environment, competition, and randomness.
    =====================================================================
    """
    
    def __init__(self, config, logger=None):
        """
        Initialize the simulation world
        
        CONFIG DICTIONARY contains all tunable parameters:
        - width, height: World dimensions (pixels)
        - initial_dots: Starting population
        - initial_food: Starting food count
        - food_spawn_rate: Food per second
        - max_food: Food capacity limit
        
        Args:
            config: Configuration dictionary
            logger: MetricsLogger instance (optional, for data collection)
        """
        self.config = config
        self.logger = logger
        
        # ===== ENTITY LISTS =====
        # These lists hold all living/existing entities
        self.dots = []   # All living dots (agents)
        self.food = []   # All food items (resources)
        
        # ===== WORLD BOUNDARIES =====
        # Define the physical space (like a Minecraft world border)
        self.width = config.get('width', 800)
        self.height = config.get('height', 600)
        
        # ===== SIMULATION STATE =====
        self.generation = 1       # Current generation number
        self.time_elapsed = 0.0   # Seconds since generation started
        self.paused = False       # Is simulation paused?
        self.restarting = False   # Prevent recursive restarts (safety)
        
        # ===== ID COUNTERS =====
        # Unique IDs for every entity ever created (debugging!)
        self.next_dot_id = 0
        self.next_food_id = 0
        
        # ===== LIFETIME STATISTICS =====
        # Track totals across ALL generations
        self.total_dots_created = 0
        self.total_dots_died = 0
        self.total_food_consumed = 0
        self.total_births = 0
        self.total_attacks = 0
        
        # ===== METRICS TRACKING =====
        # Collect data for analysis and research
        self.metrics_log = []  # History of all generation summaries
        
        # ===== EVOLUTIONARY MEMORY SYSTEM (Phase 4 - Meta-Learning) =====
        # This is the "model brain" - it learns what works across generations
        # Individual dots learn within a generation, this learns across ALL generations
        self.champion_archive = []  # Hall of fame - top 10 DNA configs ever
        self.generation_champions = []  # Best performers from each generation
        self.current_gen_dots_tracker = {}  # Track all dots for end-of-gen analysis (dict keyed by dot_id)
        self.max_archive_size = 10  # Keep top 10 champions in hall of fame
        
        # Per-generation metrics (reset each generation)
        self.current_gen_metrics = {
            'births': 0,               # Total offspring born
            'deaths': 0,               # Total dots died
            'sexual_births': 0,        # Births via sexual reproduction
            'asexual_births': 0,       # Births via cloning
            'combat_kills': 0,         # Deaths from combat
            'starvation_deaths': 0,    # Deaths from hunger
            'peak_population': 0,      # Max dots alive at once
            'avg_dna_snapshots': []    # DNA evolution over time
        }
    
    def initialize(self):
        """
        Set up initial simulation state
        - Spawn initial dot(s)
        - Spawn initial food
        """
        # Spawn initial population of dots
        num_dots = self.config.get('initial_dots', 3)
        margin = 100
        
        for i in range(num_dots):
            # Random position with margin
            x = random.randint(margin, self.width - margin)
            y = random.randint(margin, self.height - margin)
            pos = [x, y]
            
            # Create DNA (slight variations)
            dna = DNAProfile(total_points=100)
            
            # Spawn dot
            dot = Dot(self.next_dot_id, pos, dna)
            dot.offspring_count = 0  # Track reproduction success
            self.dots.append(dot)
            
            # Track for end-of-generation analysis
            self.current_gen_dots_tracker[self.next_dot_id] = {
                'dot_id': self.next_dot_id,
                'birth_time': self.time_elapsed,
                'birth_dna': dna,  # Store actual DNA object, not serialized
                'dot_ref': dot
            }
            
            self.next_dot_id += 1
            self.total_dots_created += 1
        
        print(f"✅ Spawned {num_dots} initial dots")
        print(f"   DNA: {self.dots[0].dna}")
        print(f"   Brain: {self.dots[0].brain}")
        print(f"   Resources: {self.dots[0].resources}")
        
        # Spawn initial food scattered around
        num_food = self.config.get('initial_food', 10)
        for _ in range(num_food):
            self.spawn_food()
        
        print(f"✅ Spawned {num_food} food items")
    
    def spawn_food(self, position=None):
        """Spawn a single food item"""
        if position is None:
            # Random position with margin, avoid center where dot spawns
            margin = 50
            center_x, center_y = self.width / 2, self.height / 2
            
            # Try to spawn away from center
            max_attempts = 10
            for _ in range(max_attempts):
                x = random.randint(margin, self.width - margin)
                y = random.randint(margin, self.height - margin)
                
                # Check distance from center
                dx = x - center_x
                dy = y - center_y
                distance = (dx*dx + dy*dy) ** 0.5
                
                # Accept if far enough from center (> 100 pixels)
                if distance > 100:
                    position = [x, y]
                    break
            else:
                # Fallback if all attempts failed
                position = [x, y]
        
        # Random energy value
        energy = random.randint(50, 150)
        
        food = Food(self.next_food_id, position, energy)
        self.food.append(food)
        self.next_food_id += 1
        
        return food
    
    def spawn_dot(self, position, dna_profile):
        """Spawn a new dot (during reproduction)"""
        dot = Dot(self.next_dot_id, position, dna_profile)
        dot.offspring_count = 0  # Track reproduction success
        self.dots.append(dot)
        
        # Track for end-of-generation analysis
        self.current_gen_dots_tracker[self.next_dot_id] = {
            'dot_id': self.next_dot_id,
            'birth_time': self.time_elapsed,
            'birth_dna': dna_profile,  # Store actual DNA object, not serialized
            'dot_ref': dot
        }
        
        self.next_dot_id += 1
        self.total_dots_created += 1
        return dot
    
    def handle_combat(self):
        """Handle all combat interactions"""
        for attacker in self.dots:
            if attacker.current_action == "attack" and attacker.attack_target is not None:
                # Find actual target dot object
                target = next((d for d in self.dots if d.id == attacker.attack_target), None)
                
                if target and target.resources.is_alive():
                    # Execute attack
                    result = attacker.action_manager.attack.execute(attacker, target, 0)
                    self.total_attacks += 1
                    
                    if result['result'] == "HIT":
                        print(f"⚔️  Dot #{attacker.id} attacked Dot #{target.id} for {result['damage']:.1f} damage!")
                        
                        # Phase 4: Reward for successful attack
                        reward = result['damage'] / 10.0  # Damage dealt = reward
                        attacker.brain.add_reward('attack', reward)
                        attacker.brain.add_memory('attack', {
                            'target_id': target.id,
                            'outcome': 'hit',
                            'damage': result['damage']
                        }, reward)
                        
                        # Target gets penalty for being hit
                        penalty = -result['damage'] / 20.0
                        target.brain.add_reward('defend', penalty)
                        target.brain.add_memory('attacked_by', {
                            'attacker_id': attacker.id,
                            'damage': result['damage']
                        }, penalty)
                        
                        if self.logger:
                            self.logger.log_attack(attacker.id, target.id, result['damage'], True, self.time_elapsed)
                    else:
                        print(f"❌ Dot #{attacker.id} missed Dot #{target.id}!")
                        
                        # Phase 4: Small penalty for missing
                        attacker.brain.add_reward('attack', -0.1)
                        
                        if self.logger:
                            self.logger.log_attack(attacker.id, target.id, 0, False, self.time_elapsed)
                
                # Clear target
                attacker.attack_target = None
    
    def handle_mating(self, mate_requests):
        """
        Handle sexual reproduction requests.
        Returns list of offspring data for successful matings.
        Safety: Limits processing to prevent infinite loops.
        """
        offspring = []
        processed_pairs = set()  # Track which pairs have already mated
        
        # Safety limit: process max 20 matings per frame to prevent hangs
        MAX_MATINGS_PER_FRAME = 20
        matings_processed = 0
        
        # Group requests by pairs (mutual consent required)
        for request in mate_requests:
            if matings_processed >= MAX_MATINGS_PER_FRAME:
                break  # Safety limit reached
            
            requester_id = request['requester_id']
            mate_id = request['mate_id']
            
            # Safety: prevent self-mating
            if requester_id == mate_id:
                continue
            
            # Create sorted pair ID (so A+B == B+A)
            pair = tuple(sorted([requester_id, mate_id]))
            
            # Skip if this pair already processed
            if pair in processed_pairs:
                continue
            
            # Check if mate also wants to reproduce with requester (mutual consent)
            mutual = False
            for other_request in mate_requests:
                if (other_request['requester_id'] == mate_id and 
                    other_request['mate_id'] == requester_id):
                    mutual = True
                    break
            
            if mutual:
                # Find both dot objects
                dot_a = next((d for d in self.dots if d.id == requester_id), None)
                dot_b = next((d for d in self.dots if d.id == mate_id), None)
                
                if dot_a and dot_b:
                    # Check both can still reproduce (in case state changed)
                    if (dot_a.action_manager.replicate.can_execute_sexual(dot_a) and
                        dot_b.action_manager.replicate.can_execute_sexual(dot_b)):
                        
                        # Execute sexual reproduction
                        world_state = self.get_world_state()
                        result = dot_a.action_manager.replicate.execute_sexual(dot_a, dot_b, world_state)
                        offspring.append(result)
                        
                        # Mark pair as processed
                        processed_pairs.add(pair)
                        matings_processed += 1
        
        return offspring
    
    def dot_to_food(self, dot):
        """Convert dead dot to food based on its DNA investment"""
        # Food energy based on DNA strength, not remaining resources
        # More DNA points = better nutrition (risk/reward for evolution)
        
        base_nutrition = 30  # Minimum food value
        dna_nutrition = dot.dna.get_total_points()  # Direct conversion: 1 DNA point = 1 food energy
        
        # Total food energy from corpse
        food_energy = base_nutrition + dna_nutrition
        
        food = Food(self.next_food_id, dot.position, food_energy)
        self.food.append(food)
        self.next_food_id += 1
        
        print(f"  💀➡️🍎 Dot #{dot.id} ({dot.dna.get_total_points()} DNA pts) became {food_energy:.0f} energy food")
    
    def update(self, delta_time):
        """
        Main simulation update
        1. Update all dots
        2. Handle combat
        3. Handle reproduction
        4. Check eating interactions
        5. Cleanup depleted food
        6. Cleanup dead dots (convert to food)
        7. Respawn food if needed
        8. Update time
        """
        if self.paused:
            return
        
        # 1. Update all dots
        world_state = self.get_world_state()
        offspring_data = []
        mate_requests = []  # Track mating requests
        
        for dot in self.dots:
            result = dot.update(delta_time, world_state)
            # Collect offspring data (asexual reproduction)
            if result and result.get('result') == 'OFFSPRING_ASEXUAL':
                offspring_data.append(result)
            # Collect mate requests (sexual reproduction)
            elif result and result.get('result') == 'MATE_REQUEST':
                mate_requests.append(result)
        
        # 2. Handle combat
        self.handle_combat()
        
        # 3. Handle sexual reproduction (mate requests)
        sexual_offspring = self.handle_mating(mate_requests)
        offspring_data.extend(sexual_offspring)
        
        # 4. Spawn offspring (both sexual and asexual)
        population_before = len(self.dots)
        
        for data in offspring_data:
            new_dot = self.spawn_dot(data['child_pos'], data['child_dna'])
            self.total_births += 1
            self.current_gen_metrics['births'] += 1
            
            # Track reproduction type
            if data.get('result') == 'OFFSPRING_SEXUAL':
                self.current_gen_metrics['sexual_births'] += 1
                
                # Track offspring count for both parents
                parent1_id = data.get('parent_a_id')
                parent2_id = data.get('parent_b_id')
                
                parent1 = next((d for d in self.dots if d.id == parent1_id), None)
                parent2 = next((d for d in self.dots if d.id == parent2_id), None)
                
                if parent1:
                    parent1.offspring_count += 1
                    parent1.brain.add_reward('seek_mate', 2.0)  # Good reward for sexual reproduction
                    parent1.brain.add_memory('reproduce_sexual', {
                        'partner_id': parent2_id,
                        'child_id': new_dot.id
                    }, 2.0)
                
                if parent2:
                    parent2.offspring_count += 1
                    parent2.brain.add_reward('seek_mate', 2.0)
                    parent2.brain.add_memory('reproduce_sexual', {
                        'partner_id': parent1_id,
                        'child_id': new_dot.id
                    }, 2.0)
                parent_ids = [data['parent_a_id'], data['parent_b_id']]
                print(f"  💕 Dot #{data['parent_a_id']} + Dot #{data['parent_b_id']} → Offspring #{self.next_dot_id - 1} (sexual)")
                
                if self.logger:
                    self.logger.log_reproduction(parent_ids, new_dot.id, 'sexual', self.time_elapsed)
                    self.logger.log_dot_birth(new_dot.id, self.generation, parent_ids, 
                                             data['child_dna'].get_total_points(), self.time_elapsed)
                    
            elif data.get('result') == 'OFFSPRING_ASEXUAL':
                self.current_gen_metrics['asexual_births'] += 1
                parent_id = data.get('parent_id', -1)
                parent_ids = [parent_id]
                
                # Phase 4: Reward parent for asexual reproduction (smaller than sexual)
                parent = next((d for d in self.dots if d.id == parent_id), None)
                if parent:
                    parent.offspring_count += 1
                    parent.brain.add_reward('replicate', 1.5)  # Less than sexual
                    parent.brain.add_memory('reproduce_asexual', {
                        'child_id': new_dot.id
                    }, 1.5)
                
                print(f"  🧬 Dot #{parent_id} → Offspring #{self.next_dot_id - 1} (asexual)")
                
                if self.logger:
                    self.logger.log_reproduction(parent_ids, new_dot.id, 'asexual', self.time_elapsed)
                    self.logger.log_dot_birth(new_dot.id, self.generation, parent_ids,
                                             data['child_dna'].get_total_points(), self.time_elapsed)
        
        # Phase 4: Population growth reward
        # If population increased, all parents who contributed get bonus reward
        population_after = len(self.dots)
        if population_after > population_before:
            population_increase = population_after - population_before
            population_reward = population_increase * 0.5  # 0.5 reward per new dot
            
            for data in offspring_data:
                if data.get('result') == 'OFFSPRING_SEXUAL':
                    parent1 = next((d for d in self.dots if d.id == data.get('parent1_id')), None)
                    parent2 = next((d for d in self.dots if d.id == data.get('parent2_id')), None)
                    if parent1:
                        parent1.brain.add_reward('population_growth', population_reward)
                    if parent2:
                        parent2.brain.add_reward('population_growth', population_reward)
                elif data.get('result') == 'OFFSPRING_ASEXUAL':
                    parent = next((d for d in self.dots if d.id == data.get('parent_id')), None)
                    if parent:
                        parent.brain.add_reward('population_growth', population_reward)
        
        # Update peak population
        if len(self.dots) > self.current_gen_metrics['peak_population']:
            self.current_gen_metrics['peak_population'] = len(self.dots)
        
        # 5. Check eating
        self.check_eating()
        
        # 5. Remove depleted food
        before_food = len(self.food)
        self.food = [f for f in self.food if not f.depleted]
        consumed = before_food - len(self.food)
        if consumed > 0:
            self.total_food_consumed += consumed
        
        # 6. Remove dead dots and convert to food
        dead_dots = [d for d in self.dots if not d.resources.is_alive()]
        for dot in dead_dots:
            # Determine death cause
            death_cause = "starvation" if dot.resources.energy <= 0 else "combat"
            if death_cause == "starvation":
                self.current_gen_metrics['starvation_deaths'] += 1
            else:
                self.current_gen_metrics['combat_kills'] += 1
            
            # Track dot stats at death for champion selection
            if dot.id in self.current_gen_dots_tracker:
                tracker = self.current_gen_dots_tracker[dot.id]
                tracker['death_time'] = self.time_elapsed
                tracker['lifetime'] = self.time_elapsed - tracker['birth_time']
                tracker['final_dna'] = dot.dna.get_total_points()
                tracker['total_reward'] = dot.brain.total_reward
                tracker['offspring_count'] = dot.offspring_count
            
            # Log death
            if self.logger:
                self.logger.log_dot_death(dot.id, death_cause, self.time_elapsed)
            
            self.dot_to_food(dot)
        
        before_dots = len(self.dots)
        self.dots = [d for d in self.dots if d.resources.is_alive()]
        died = before_dots - len(self.dots)
        if died > 0:
            self.total_dots_died += died
            self.current_gen_metrics['deaths'] += died
            print(f"💀 {died} dot(s) died (Bodies → Food)")
        
        # 7. Respawn food if critically low (scaled for larger environment)
        # Force dots to compete for scarce resources
        if len(self.food) < 8:  # Increased from 3 to 8 for larger world
            self.spawn_food()
        
        # 8. Check for extinction
        if len(self.dots) == 0 and not self.restarting:
            self.restarting = True
            
            # Log extinction
            if self.logger:
                self.logger.log_extinction(self.generation, self.time_elapsed)
            
            print("")
            print("=" * 60)
            print("💀 EXTINCTION - All dots have died!")
            print(f"   Generation {self.generation} survived {self.time_elapsed:.1f} seconds")
            print(f"   Stats: Created={self.total_dots_created}, Died={self.total_dots_died}")
            print(f"   Births={self.total_births}, Attacks={self.total_attacks}")
            print("")
            print("🔄 Starting new generation...")
            print("=" * 60)
            print("")
            self.restart_simulation()
            self.restarting = False
        
        # 9. Update time
        self.time_elapsed += delta_time
        
        # 10. Log colony metrics periodically
        if self.logger:
            self.logger.log_colony_metrics(self)
    
    def check_eating(self):
        """
        Check if any dots are touching food
        Handle eating interaction
        """
        eating_range = 15  # Distance to start eating
        
        for dot in self.dots:
            if not dot.resources.is_alive():
                continue
            
            for food in self.food:
                if food.depleted:
                    continue
                
                # Check distance
                dx = dot.position[0] - food.position[0]
                dy = dot.position[1] - food.position[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < eating_range:
                    # Eat food (10 energy per frame at 60fps = 600/second)
                    energy_gained = food.consume(10)
                    
                    if energy_gained > 0:
                        # Use cascading eat system: energy → health → DNA
                        dot.eat(energy_gained)
    
    def get_world_state(self):
        """
        Get serialized world state for dot decision-making
        Simplified view of the world
        """
        return {
            'dots': [d.serialize() for d in self.dots],
            'food': [f.serialize() for f in self.food],
            'time': self.time_elapsed,
            'bounds': {
                'width': self.width,
                'height': self.height
            }
        }
    
    def get_state(self):
        """
        Get full simulation state for renderer
        Complete state export
        """
        return {
            'dots': [d.serialize() for d in self.dots],
            'food': [f.serialize() for f in self.food],
            'generation': self.generation,
            'time': self.time_elapsed,
            'paused': self.paused,
            'stats': {
                'dot_count': len(self.dots),
                'food_count': len(self.food),
                'total_created': self.total_dots_created,
                'total_died': self.total_dots_died,
                'total_food_consumed': self.total_food_consumed,
                'total_births': self.total_births,
                'total_attacks': self.total_attacks
            },
            'bounds': {
                'width': self.width,
                'height': self.height
            }
        }
    
    def restart_simulation(self):
        """Restart simulation with new generation after extinction"""
        # Select champions from the generation that just died
        self.select_generation_champions()
        
        # Log final generation metrics
        self.current_gen_metrics['survival_time'] = self.time_elapsed
        summary = {
            'generation': self.generation,
            **self.current_gen_metrics
        }
        self.metrics_log.append(summary)
        
        # Log to external logger
        if self.logger:
            self.logger.log_generation_end(summary)
        
        # Print generation summary
        self.print_generation_summary(summary)
        
        # Increment generation
        self.generation += 1
        
        # Reset stats (keep historical totals)
        self.time_elapsed = 0.0
        self.current_gen_metrics = {
            'births': 0,
            'deaths': 0,
            'sexual_births': 0,
            'asexual_births': 0,
            'combat_kills': 0,
            'starvation_deaths': 0,
            'peak_population': 0,
            'avg_dna_snapshots': []
        }
        
        # Clear dot tracker for new generation
        self.current_gen_dots_tracker = {}
        
        # Clear food
        self.food = []
        
        # Respawn initial population with RANDOMIZED DNA
        # Create new generation using evolved DNA strategies
        num_dots = self.config.get('initial_dots', 5)
        margin = 100
        
        print(f"🧬 Generation {self.generation}: Creating evolved DNA strategies...")
        
        for i in range(num_dots):
            x = random.randint(margin, self.width - margin)
            y = random.randint(margin, self.height - margin)
            pos = [x, y]
            
            # Create DNA using evolutionary memory (60% champion, 30% weighted, 10% random)
            dna = self._create_evolved_dna()
            
            # Spawn dot
            dot = Dot(self.next_dot_id, pos, dna)
            self.dots.append(dot)
            
            # Log birth
            if self.logger:
                self.logger.log_dot_birth(
                    self.next_dot_id,
                    self.generation,
                    [],  # No parents (new generation)
                    dna.get_total_points(),
                    self.time_elapsed
                )
            
            self.next_dot_id += 1
            self.total_dots_created += 1
        
        # Respawn food
        num_food = self.config.get('initial_food', 20)
        for _ in range(num_food):
            self.spawn_food()
        
        print(f"✅ Generation {self.generation}: Spawned {num_dots} dots with evolved DNA and {num_food} food")
    
    def select_generation_champions(self):
        """
        Select the top 3 performers from the generation that just ended.
        Fitness = lifetime × (1 + offspring) × (1 + reward/100)
        """
        if not self.current_gen_dots_tracker:
            print("📊 No dots tracked - skipping champion selection")
            return
        
        # Calculate fitness for all tracked dots
        candidates = []
        for dot_id, tracker in self.current_gen_dots_tracker.items():
            # Skip dots still alive (shouldn't happen in restart, but be safe)
            if 'lifetime' not in tracker:
                continue
            
            lifetime = tracker.get('lifetime', 0)
            offspring = tracker.get('offspring_count', 0)
            reward = tracker.get('total_reward', 0)
            
            # Fitness formula: lifetime × (1 + offspring) × (1 + reward/100)
            fitness = lifetime * (1 + offspring) * (1 + reward / 100.0)
            
            candidates.append({
                'dot_id': dot_id,
                'fitness': fitness,
                'lifetime': lifetime,
                'offspring': offspring,
                'reward': reward,
                'dna': tracker['birth_dna']  # DNA they were born with
            })
        
        # Sort by fitness descending
        candidates.sort(key=lambda x: x['fitness'], reverse=True)
        
        # Select top 3 as generation champions
        champions = candidates[:3]
        
        if champions:
            print(f"\n🏆 Generation {self.generation} Champions:")
            for i, champ in enumerate(champions, 1):
                print(f"  {i}. Dot #{champ['dot_id']}: Fitness={champ['fitness']:.1f} "
                      f"(lifetime={champ['lifetime']:.1f}s, offspring={champ['offspring']}, "
                      f"reward={champ['reward']:.1f})")
            
            # Store champions for this generation
            self.generation_champions.append({
                'generation': self.generation,
                'champions': champions
            })
            
            # Update hall of fame (all-time best)
            self.update_hall_of_fame(champions)
    
    def update_hall_of_fame(self, new_champions):
        """
        Update the all-time hall of fame with new champions.
        Maintains top 10 performers across all generations.
        """
        # Add new champions to archive with generation tag
        for champ in new_champions:
            champ['generation'] = self.generation  # Tag with current generation
            self.champion_archive.append(champ)
        
        # Sort by fitness and keep top 10
        self.champion_archive.sort(key=lambda x: x['fitness'], reverse=True)
        self.champion_archive = self.champion_archive[:self.max_archive_size]
        
        if len(self.champion_archive) > 0:
            print(f"\n🎖️  Hall of Fame (Top {len(self.champion_archive)}):")
            for i, champ in enumerate(self.champion_archive[:3], 1):  # Show top 3
                print(f"  {i}. Gen {champ.get('generation', '?')}: Fitness={champ['fitness']:.1f}")
    
    def _create_evolved_dna(self):
        """
        Create DNA using evolutionary memory.
        60% - Clone a champion and mutate
        30% - Create weighted random based on successful patterns
        10% - Pure random exploration
        """
        roll = random.random()
        
        if roll < 0.6 and self.champion_archive:
            # 60%: Clone a champion with mutations
            champion = random.choice(self.champion_archive)
            return self._mutate_dna(champion['dna'])
        
        elif roll < 0.9 and self.champion_archive:
            # 30%: Weighted random based on champion patterns
            return self._create_weighted_random_dna()
        
        else:
            # 10%: Pure random exploration
            return self._create_randomized_dna()
    
    def _mutate_dna(self, base_dna):
        """
        Create a mutated copy of champion DNA.
        Small random changes to point allocations.
        """
        # Create a copy of the base DNA
        new_dna = DNAProfile(total_points=base_dna.get_total_points())
        
        # Build lookup of base genes by name
        base_genes = {gene.name: gene for gene in base_dna.get_all_genes()}
        
        # Copy gene settings
        for gene in new_dna.get_all_genes():
            if gene.name in base_genes:
                base_gene = base_genes[gene.name]
                gene.enabled = base_gene.enabled
                gene.points = base_gene.points
        
        # Mutate: randomly adjust 1-3 genes
        num_mutations = random.randint(1, 3)
        all_genes = new_dna.get_all_genes()
        
        for _ in range(num_mutations):
            gene = random.choice(all_genes)
            
            if random.random() < 0.5:
                # Increase points (small amount)
                increase = random.randint(1, 5)
                gene.points = min(gene.points + increase, 20)  # Cap at 20
                gene.enabled = True
            else:
                # Decrease points
                decrease = random.randint(1, 5)
                gene.points = max(gene.points - decrease, 0)
                if gene.points == 0 and gene.name != 'eat':
                    gene.enabled = False
        
        return new_dna
    
    def _create_weighted_random_dna(self):
        """
        Create DNA biased toward successful patterns from champions.
        Analyzes champion gene usage and creates similar but randomized DNA.
        """
        if not self.champion_archive:
            return self._create_randomized_dna()
        
        # Analyze champion gene patterns
        gene_usage = {}
        for champ in self.champion_archive[:5]:  # Use top 5 champions
            dna = champ['dna']
            for gene in dna.get_all_genes():
                if gene.name not in gene_usage:
                    gene_usage[gene.name] = {'enabled_count': 0, 'avg_points': 0, 'samples': 0}
                
                if gene.enabled:
                    gene_usage[gene.name]['enabled_count'] += 1
                    gene_usage[gene.name]['avg_points'] += gene.points
                    gene_usage[gene.name]['samples'] += 1
        
        # Calculate averages
        for gene_name, stats in gene_usage.items():
            if stats['samples'] > 0:
                stats['avg_points'] = stats['avg_points'] / stats['samples']
                stats['enable_probability'] = stats['enabled_count'] / len(self.champion_archive[:5])
        
        # Create new DNA based on patterns
        new_dna = DNAProfile(total_points=100)
        budget = 100
        
        # Disable all genes first
        for gene in new_dna.get_all_genes():
            gene.enabled = False
            gene.points = 0
        
        # Always enable eat
        new_dna.eat.enabled = True
        
        # Enable genes based on champion patterns
        for gene in new_dna.get_all_genes():
            if gene.name == 'eat':
                continue
            
            stats = gene_usage.get(gene.name, {})
            enable_prob = stats.get('enable_probability', 0.1)
            
            if random.random() < enable_prob and budget >= 2:
                gene.enabled = True
                # Use avg from champions as baseline, with some randomness
                avg_pts = stats.get('avg_points', 5)
                variation = random.randint(-3, 3)
                points = max(1, min(int(avg_pts + variation), budget))
                gene.points = points
                budget -= points
        
        return new_dna
    
    def _create_randomized_dna(self):
        """Create a DNA profile with randomized point allocation"""
        dna = DNAProfile(total_points=100)
        
        # Start with baseline (all disabled except essentials)
        for gene in dna.get_all_genes():
            if gene.name not in ['eat']:  # Keep eat always enabled
                gene.enabled = False
                gene.points = 0
        
        # Budget to allocate - start with 100
        budget = 100
        allocated_genes = []
        
        # CRITICAL: Always enable core survival genes with safe allocation
        # These are REQUIRED for dots to survive
        essentials = [
            ('brain_memory', 5, 12),
            ('brain_sense_slots', 5, 12),
            ('brain_action_slots', 5, 12),
            ('vision_distance', 10, 20),
            ('vision_fov', 10, 20),
            ('food_detection', 8, 15),
            ('movement_speed', 5, 12),
            ('movement_max_energy', 5, 12),
        ]
        
        for gene_name, min_pts, max_pts in essentials:
            if hasattr(dna, gene_name):
                gene = getattr(dna, gene_name)
                gene.enabled = True
                # Safe allocation - never exceed budget
                safe_max = min(max_pts, budget - 1)  # Always keep 1 point reserve
                if safe_max < min_pts:
                    safe_max = min_pts
                
                points = random.randint(min_pts, safe_max)
                gene.points = points
                budget -= points
                allocated_genes.append((gene_name, points))
        
        # CRITICAL: Always enable replicate gene (otherwise no reproduction = extinction!)
        dna.replicate.enabled = True
        replicate_pts = random.randint(1, min(5, max(1, budget // 4)))  # Small allocation
        dna.replicate.points = replicate_pts
        budget -= replicate_pts
        allocated_genes.append(('replicate', replicate_pts))
        
        # Optional: Combat genes (50% chance)
        if random.random() > 0.5 and budget >= 5:
            dna.attack.enabled = True
            attack_pts = random.randint(1, min(10, budget // 2))
            dna.attack.points = attack_pts
            budget -= attack_pts
            allocated_genes.append(('attack', attack_pts))
            
            if budget >= 3:
                dna.defend.enabled = True
                defend_pts = random.randint(1, min(8, budget // 2))
                dna.defend.points = defend_pts
                budget -= defend_pts
                allocated_genes.append(('defend', defend_pts))
        
        # Optional: Dot detection (70% chance)
        if random.random() > 0.3 and budget >= 3:
            dna.dot_detection.enabled = True
            dot_detect_pts = random.randint(1, min(10, budget))
            dna.dot_detection.points = dot_detect_pts
            budget -= dot_detect_pts
            allocated_genes.append(('dot_detection', dot_detect_pts))
        
        # Optional: DNA strength detection (20% chance)
        if random.random() > 0.8 and budget >= 3:
            dna.dna_strength_detection.enabled = True
            dna_detect_pts = random.randint(1, min(8, budget))
            dna.dna_strength_detection.points = dna_detect_pts
            budget -= dna_detect_pts
            allocated_genes.append(('dna_strength_detection', dna_detect_pts))
        
        # Sanity check: ensure budget is non-negative
        if budget < 0:
            print(f"⚠️  WARNING: DNA budget went negative ({budget})! This should not happen.")
            print(f"   Allocated: {allocated_genes}")
            # Emergency: disable optional genes to fix budget
            if dna.dna_strength_detection.enabled:
                budget += dna.dna_strength_detection.points
                dna.dna_strength_detection.enabled = False
                dna.dna_strength_detection.points = 0
            if budget < 0 and dna.dot_detection.enabled:
                budget += dna.dot_detection.points
                dna.dot_detection.enabled = False
                dna.dot_detection.points = 0
        
        return dna
    
    def print_generation_summary(self, summary):
        """Print detailed generation summary"""
        print("")
        print("=" * 70)
        print(f"📊 GENERATION {summary['generation']} SUMMARY")
        print("=" * 70)
        print(f"⏱️  Survival Time: {summary.get('survival_time', 0):.1f} seconds")
        print(f"👥 Peak Population: {summary['peak_population']}")
        print(f"")
        print(f"REPRODUCTION:")
        print(f"  Total Births: {summary['births']}")
        print(f"    💕 Sexual: {summary['sexual_births']} ({summary['sexual_births']/max(1, summary['births'])*100:.0f}%)")
        print(f"    🧬 Asexual: {summary['asexual_births']} ({summary['asexual_births']/max(1, summary['births'])*100:.0f}%)")
        print(f"")
        print(f"DEATHS:")
        print(f"  Total Deaths: {summary['deaths']}")
        print(f"    ⚔️  Combat: {summary['combat_kills']}")
        print(f"    🍽️  Starvation: {summary['starvation_deaths']}")
        print(f"")
        if summary.get('avg_dna_snapshots'):
            avg_dna_final = summary['avg_dna_snapshots'][-1][1] if summary['avg_dna_snapshots'] else 0
            print(f"DNA EVOLUTION:")
            print(f"  Final Avg DNA: {avg_dna_final:.1f} points")
        print("=" * 70)
        print("")
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RUNNING"
        print(f"⏸️  Simulation {status}")
    
    def __repr__(self):
        return f"DotSimulation(dots={len(self.dots)}, food={len(self.food)}, time={self.time_elapsed:.1f}s)"
