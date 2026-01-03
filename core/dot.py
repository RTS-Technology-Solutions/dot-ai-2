"""
Dot entity implementation for DOT AI 2.0
Autonomous agent with DNA-based abilities, brain, resources, and senses.
"""

import math
import random
from typing import Optional, Tuple, Dict, Any, List
from .dna import DNAProfile
from .brain import Brain
from .resources import Resources
from .senses import PerceptionSystem
from .actions import ActionManager


class Dot:
    """
    Autonomous agent with DNA, brain, resources, and senses.
    Makes decisions based on utility calculations and executes actions.
    """
    
    def __init__(self, dot_id: int, position: Tuple[float, float], dna: DNAProfile):
        self.id = dot_id
        self.position = list(position)
        self.dna = dna
        self.brain = Brain(dna)
        self.resources = Resources(dna)
        self.perception = PerceptionSystem(dna)
        self.action_manager = ActionManager(dna)  # Pass DNA, not self
        
        # Movement state
        self.velocity = [0.0, 0.0]
        self.target_position = None
        
        # Action state
        self.current_action = "idle"
        self.is_defending = False
        self.attack_target = None
        self.mate_target = None  # ID of dot being sought for mating
        
        # Evolutionary tracking
        self.offspring_count = 0  # Track reproductive success
        
        # Visual debugging
        self.vision_debug_circles = []
    
    def update(self, dt: float, world_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Main update loop for the dot.
        Returns offspring data dict if reproduction occurred, None otherwise.
        """
        # 1. Deplete energy based on movement
        speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        is_moving = speed > 0.1
        
        # Energy costs
        IDLE_ENERGY_COST = 2.0  # per second
        MOVEMENT_ENERGY_COST = 1.0  # per second
        
        if self.is_defending:
            # Defending costs 3% of max energy per second
            defend_cost = self.resources.max_energy * 0.03 * dt
            self.resources.deplete_energy(defend_cost)
        elif is_moving:
            self.resources.deplete_energy((IDLE_ENERGY_COST + MOVEMENT_ENERGY_COST) * dt)
        else:
            self.resources.deplete_energy(IDLE_ENERGY_COST * dt)
        
        # 2. Apply starvation damage
        if self.resources.is_starving():
            STARVATION_DAMAGE = 1.5  # per second
            self.resources.deplete_health(STARVATION_DAMAGE * dt)
        
        # 3. Check if dead
        if not self.resources.is_alive():
            return None
        
        # 4. Update perception
        perceived_world = self.perception.perceive(self.position, self.velocity, world_state)
        
        # 5. Decide next action
        self.current_action = self.decide_action(perceived_world)
        
        # 6. Give small reward for taking action (Phase 4: Action-based learning)
        # Idle gets no reward, all other actions get small positive reward
        if self.current_action != 'idle':
            self.brain.add_reward(self.current_action, 0.1)  # Small action reward
        
        # 7. Execute action
        offspring_result = self.execute_action(perceived_world, world_state, dt)
        
        # 8. Update visuals
        self.vision_debug_circles = self.perception.get_debug_visuals(self.position)
        
        return offspring_result
    
    def decide_action(self, perceived_world: Dict[str, Any]) -> str:
        """
        Utility-based AI decision making.
        Calculates utility scores for each action and picks the highest.
        """
        # Get current state
        energy_pct = self.resources.energy / self.resources.max_energy
        health_pct = self.resources.health / self.resources.max_health
        hunger_pct = self.resources.hunger
        
        # Get DNA points
        attack_points = self.dna.get_gene_value('attack')
        defend_points = self.dna.get_gene_value('defend')
        replicate_points = self.dna.get_gene_value('replicate')
        
        # Health urgency - penalize if losing health
        health_urgency = 0.0
        if health_pct < 0.9:  # Any health loss
            health_urgency = (1.0 - health_pct) * 2.0  # 0.2 at 90% health, 2.0 at 0% health
        
        # Initialize utilities
        utilities = {}
        
        # 1. SEEK FOOD UTILITY
        # Higher when hungry, lower when satiated
        perceived_food = perceived_world.get('food', [])
        if perceived_food:
            food_utility = hunger_pct * 10.0
            # Bonus if very hungry
            if hunger_pct > 0.7:
                food_utility *= 2.0
            utilities['seek_food'] = food_utility
        else:
            utilities['seek_food'] = 0.0
        
        # 2. ATTACK UTILITY
        # GOAL: Attack when hungry AND enemy will provide good food
        # Attack = Risk (energy cost, damage) vs Reward (food from kill)
        perceived_dots = perceived_world.get('dots', [])
        if attack_points > 0 and perceived_dots and hunger_pct > 0.3:  # Only attack if moderately hungry
            best_target = None
            max_score = -float('inf')
            
            can_see_dna = self.dna.get_gene_value('dna_strength_detection') > 0
            
            for dot_info in perceived_dots:
                enemy_health = dot_info.get('health', 100)
                enemy_energy = dot_info.get('energy', 100)
                enemy_max_health = dot_info.get('max_health', 100)
                enemy_state = dot_info.get('state', 'alive')
                
                # Calculate weakness based on BOTH health and energy
                health_weakness = 1.0 - (enemy_health / max(1, enemy_max_health))
                energy_weakness = 1.0 - (enemy_energy / max(1, dot_info.get('max_energy', 100)))
                
                # Starving dots are PRIME targets (huge multiplier)
                if enemy_state == 'starving':
                    weakness_score = 2.0  # 200% - easy kill, slow movement, dying
                else:
                    # Combine health and energy weakness (energy more important - indicates capability)
                    weakness_score = (energy_weakness * 0.6 + health_weakness * 0.4)
                
                # Calculate expected food value from kill
                if can_see_dna and 'perceived_dna_strength' in dot_info:
                    enemy_dna = dot_info['perceived_dna_strength']
                    food_value = 30 + enemy_dna
                else:
                    food_value = 100  # Assume average
                
                # Score prioritizes: starving > low energy > low health, with food value consideration
                score = weakness_score * (food_value / 130.0)
                
                if score > max_score:
                    max_score = score
                    best_target = dot_info
            
            if best_target:
                # Attack utility based on:
                # - Own strength (health)
                # - Hunger level (need food)
                # - Attack points (capability)
                # - Target score (weakness + food value)
                own_strength = health_pct
                hunger_motivation = hunger_pct * 1.5  # More hungry = more motivated
                attack_utility = max_score * (attack_points / 50.0) * own_strength * hunger_motivation * 3.0
                
                # Reduce if low health (risky)
                if health_pct < 0.3:
                    attack_utility *= 0.1  # Very risky when weak
                elif health_pct < 0.6:
                    attack_utility *= 0.5  # Somewhat risky
                
                utilities['attack'] = attack_utility
                self.attack_target = best_target['id']
            else:
                utilities['attack'] = 0.0
        else:
            utilities['attack'] = 0.0
            self.attack_target = None
        
        # 3. DEFEND UTILITY
        # GOAL: Only defend when ACTIVELY under threat (being attacked OR very weak)
        # Defending costs energy and prevents food-seeking
        if defend_points > 0:
            danger_level = 0.0
            
            # REAL danger: Multiple enemies nearby AND low health
            threat_count = len(perceived_dots)
            
            # Only defend if:
            # 1. Surrounded (3+ enemies) OR
            # 2. Low health (<40%) with enemies nearby
            if threat_count >= 3:
                danger_level = min(1.0, (threat_count - 2) * 0.4)  # Ramps up with crowd
            elif health_pct < 0.4 and threat_count > 0:
                danger_level = (1.0 - health_pct) * 0.8  # Desperate defense when weak
            
            if danger_level > 0:
                defend_utility = danger_level * (defend_points / 50.0) * 2.0
                utilities['defend'] = defend_utility
            else:
                utilities['defend'] = 0.0
        else:
            utilities['defend'] = 0.0
        
        # 4. REPLICATE UTILITY (Asexual - high cost backup)
        # Higher when: high energy, high health, have replicate points, fewer dots nearby
        # Only triggers at 80% energy (fallback if no mate found)
        # Phase 4: Use density sensor for better crowding awareness
        if replicate_points > 0:
            # Check if we have enough energy (need 80%)
            if energy_pct >= 0.8 and health_pct >= 0.7:
                # Use density sensor if available, otherwise fall back to visible dots
                nearby_density = perceived_world.get('nearby_density', len(perceived_dots))
                crowding_penalty = min(1.0, nearby_density * 0.15)  # Less penalty, but still matters
                replicate_utility = (replicate_points / 50.0) * energy_pct * health_pct * (1.0 - crowding_penalty) * 2.0  # Lower than mate-seeking
                utilities['replicate'] = replicate_utility
            else:
                utilities['replicate'] = 0.0
        else:
            utilities['replicate'] = 0.0
        
        # 5. SEEK MATE UTILITY (Sexual - preferred, lower cost)
        # Higher when: moderate energy (40%+), healthy, potential mates nearby
        # Preferred over asexual due to lower cost and genetic diversity
        if replicate_points > 0:
            if energy_pct >= 0.4 and health_pct >= 0.7:
                # Look for potential mates (exclude self!)
                potential_mates = [d for d in perceived_dots 
                                  if d.get('id') != self.id and  # Don't mate with self!
                                  d.get('health', 0) > 70 and 
                                  d.get('can_reproduce', False)]
                
                if potential_mates:
                    # Stronger utility than asexual (lower cost = more appealing)
                    mate_count_bonus = min(1.0, len(potential_mates) * 0.3)  # More mates = better
                    mate_utility = (replicate_points / 50.0) * energy_pct * health_pct * (1.0 + mate_count_bonus) * 4.0
                    utilities['seek_mate'] = mate_utility
                    
                    # Choose best mate (prioritize health, proximity)
                    best_mate = max(potential_mates, key=lambda m: m.get('health', 0))
                    self.mate_target = best_mate['id']
                else:
                    utilities['seek_mate'] = 0.0
                    self.mate_target = None
            else:
                utilities['seek_mate'] = 0.0
                self.mate_target = None
        else:
            utilities['seek_mate'] = 0.0
            self.mate_target = None
        
        # Filter out self from perceived dots
        perceived_food = perceived_world.get('food', [])
        perceived_dots = [d for d in perceived_world.get('dots', []) if d.get('id') != self.id]
        
        # 6. EXPLORE UTILITY (when nothing visible)
        # Small reward for movement to encourage exploration
        nothing_visible = len(perceived_food) == 0 and len(perceived_dots) == 0
        
        if nothing_visible:
            # Encourage exploration when blind - desperate when low resources
            explore_base = 3.0  # Higher baseline
            hunger_boost = hunger_pct * 5.0  # Strong hunger motivation (0-5)
            health_boost = health_urgency * 2.0  # Panic when hurt (0-2)
            explore_utility = explore_base + hunger_boost + health_boost  # 3-10 utility
            utilities['explore'] = explore_utility
        else:
            utilities['explore'] = 0.0
        
        # 7. IDLE UTILITY (heavily penalized, especially in crowds)
        # Idling when resources are low = death sentence
        # Idling in crowds = starvation trap (Phase 4 density awareness)
        # Severe penalties for lazy behavior
        nearby_density = perceived_world.get('nearby_density', 0)
        density_penalty = min(nearby_density * 0.3, 3.0)  # Up to 3.0 penalty for crowds
        idle_penalty = health_urgency * 1.5 + hunger_pct * 2.0 + density_penalty
        utilities['idle'] = max(0.01, 0.3 - idle_penalty)  # Very low baseline, minimum 0.01
        
        # Pick action with highest utility
        best_action = max(utilities, key=utilities.get)
        
        # Debug: Print utilities occasionally
        if random.random() < 0.008:  # ~0.8% chance per frame
            print(f"Dot #{self.id} utilities: ", end="")
            for action, util in sorted(utilities.items(), key=lambda x: -x[1])[:3]:
                print(f"{action}={util:.2f} ", end="")
            print(f"-> {best_action}")
        
        return best_action
    
    def execute_action(self, perceived_world: Dict[str, Any], world_state: Dict[str, Any], dt: float) -> Optional[DNAProfile]:
        """
        Execute the decided action.
        Returns offspring DNA if replication occurred, None otherwise.
        """
        if self.current_action == "seek_food":
            self.is_defending = False
            perceived_food = perceived_world.get('food', [])
            if perceived_food:
                target_food = perceived_food[0]
                # Debug: Log occasionally to check if movement is happening
                if random.random() < 0.01:
                    print(f"Dot #{self.id} seeking food at {target_food['position']}, current pos: {self.position}")
                self.move_toward(target_food['position'], world_state, dt)
            return None
        
        elif self.current_action == "explore":
            self.is_defending = False
            # Random walk - pick a direction and move
            if self.target_position is None or random.random() < 0.05:  # 5% chance to pick new direction each frame
                # Pick random point in world
                angle = random.random() * 2 * math.pi
                distance = 200  # Explore in 200px radius
                self.target_position = [
                    self.position[0] + math.cos(angle) * distance,
                    self.position[1] + math.sin(angle) * distance
                ]
            self.move_toward(self.target_position, world_state, dt)
            return None
        
        elif self.current_action == "attack":
            self.is_defending = False
            return self.execute_attack(perceived_world, world_state, dt)
        
        elif self.current_action == "defend":
            self.execute_defend()
            return None
        
        elif self.current_action == "replicate":
            self.is_defending = False
            return self.execute_replicate()
        
        elif self.current_action == "seek_mate":
            self.is_defending = False
            return self.execute_seek_mate(perceived_world, world_state, dt)
        
        else:  # idle
            self.is_defending = False
            self.velocity = [0.0, 0.0]
            return None
    
    def execute_attack(self, perceived_world: Dict[str, Any], world_state: Dict[str, Any], dt: float) -> None:
        """Execute attack action - move toward target."""
        if self.attack_target is not None:
            # Find target dot
            perceived_dots = perceived_world.get('dots', [])
            for dot_info in perceived_dots:
                if dot_info['id'] == self.attack_target:
                    self.move_toward(dot_info['position'], world_state, dt)
                    return
        
        # Target not found, idle
        self.velocity = [0.0, 0.0]
        return None
    
    def execute_defend(self):
        """Execute defend action - stop moving and activate defense."""
        self.is_defending = True
        self.velocity = [0.0, 0.0]
    
    def execute_replicate(self) -> Optional[Dict[str, Any]]:
        """
        Execute asexual replication action.
        Returns offspring data if successful, None otherwise.
        """
        world_state = {'bounds': {'width': 1200, 'height': 800}}
        result = self.action_manager.replicate.execute(self, world_state, 0.0, mate=None)
        
        if result and result.get('result') == 'OFFSPRING_ASEXUAL':
            return result
        
        return None
    
    def execute_seek_mate(self, perceived_world: Dict[str, Any], world_state: Dict[str, Any], dt: float) -> Optional[Dict[str, Any]]:
        """
        Execute mate-seeking action - move toward mate and attempt sexual reproduction if in range.
        Returns offspring data or mate request if successful, None otherwise.
        """
        if self.mate_target is None:
            return None
        
        # Find mate in perceived dots
        perceived_dots = perceived_world.get('dots', [])
        mate_info = None
        
        for dot_info in perceived_dots:
            if dot_info['id'] == self.mate_target:
                mate_info = dot_info
                break
        
        if mate_info is None:
            # Mate not visible, idle
            self.velocity = [0.0, 0.0]
            return None
        
        # Calculate distance to mate
        mate_pos = mate_info['position']
        dx = mate_pos[0] - self.position[0]
        dy = mate_pos[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Check if in mating range (30 pixels)
        MATING_RANGE = 30.0
        
        if distance <= MATING_RANGE:
            # In range! Signal ready for mating
            # Return mate_request that simulation will handle
            return {
                'result': 'MATE_REQUEST',
                'mate_id': self.mate_target,
                'requester_id': self.id
            }
        else:
            # Move toward mate
            self.move_toward(mate_pos, world_state, dt)
            return None
    
    def move_toward(self, target: Tuple[float, float], world_state: Dict[str, Any], dt: float):
        """Move toward a target position."""
        # Calculate direction
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1.0:
            # Base speed from DNA
            base_speed = 50  # pixels/second
            bonus_speed = self.dna.get_gene_value('movement_speed') * 5
            speed = base_speed + bonus_speed
            
            # Urgency multipliers
            if self.resources.is_starving():
                speed *= 0.1  # 10% speed when starving (weak)
            elif self.resources.hunger > 0.7:
                speed *= 1.5  # 50% faster when very hungry (desperate)
            
            # Normalize and apply speed
            self.velocity[0] = (dx / distance) * speed
            self.velocity[1] = (dy / distance) * speed
            
            # Update position
            self.position[0] += self.velocity[0] * dt
            self.position[1] += self.velocity[1] * dt
            
            # ENFORCE BOUNDARIES - keep dots on screen (use dynamic world bounds)
            BOUNDARY_MARGIN = 10  # pixels from edge
            bounds = world_state.get('bounds', {'width': 1200, 'height': 800})  # Fallback to old size
            MAX_X = bounds['width'] - BOUNDARY_MARGIN
            MAX_Y = bounds['height'] - BOUNDARY_MARGIN
            
            if self.position[0] < BOUNDARY_MARGIN:
                self.position[0] = BOUNDARY_MARGIN
                self.velocity[0] = 0  # Stop at boundary
            elif self.position[0] > MAX_X:
                self.position[0] = MAX_X
                self.velocity[0] = 0
            
            if self.position[1] < BOUNDARY_MARGIN:
                self.position[1] = BOUNDARY_MARGIN
                self.velocity[1] = 0
            elif self.position[1] > MAX_Y:
                self.position[1] = MAX_Y
                self.velocity[1] = 0
        else:
            self.velocity = [0.0, 0.0]
    
    def eat(self, food_energy: float):
        """Consume food with cascading priority: energy → health → DNA."""
        result = self.resources.eat(food_energy, self.brain)
        
        # Reward for successful eating (energy gained)
        eating_reward = result['energy_gained'] / 10.0
        self.brain.add_reward('eat', eating_reward)
        
        # Add memory of eating
        self.brain.add_memory('eat', {
            'energy_gained': result['energy_gained'],
            'health_gained': result['health_gained'],
            'dna_gained': result['dna_gained'],
            'age': self.brain.age
        }, eating_reward)
        
        # Log DNA growth when it happens
        if result['dna_gained'] > 0:
            print(f"🧬 Dot #{self.id} earned +{result['dna_gained']:.2f} DNA from eating (total: {self.dna.get_total_points():.1f})")
    
    def take_damage(self, damage: float, attacker_id: int) -> Dict[str, Any]:
        """
        Take damage from an attack.
        Returns dict with damage taken and whether killed.
        """
        result = self.action_manager.attack.receive_damage(
            self, 
            damage, 
            attacker_id, 
            self.is_defending
        )
        
        # Apply damage
        self.resources.health = result['health_after']
        
        return result
    
    def get_state(self) -> Dict[str, Any]:
        """Export current state for rendering/serialization."""
        # Determine state string
        if not self.resources.is_alive():
            state = "dead"
        elif self.resources.is_starving():
            state = "starving"
        else:
            state = "alive"
        
        return {
            'id': self.id,
            'position': self.position.copy(),
            'velocity': self.velocity.copy(),
            'energy': self.resources.energy,
            'max_energy': self.resources.max_energy,
            'health': self.resources.health,
            'max_health': self.resources.max_health,
            'hunger': self.resources.hunger,
            'is_alive': self.resources.is_alive(),
            'state': state,
            'current_action': self.current_action,
            'is_defending': self.is_defending,
            'dna_capacity': self.brain.capacity,
            'dna_points_used': self.dna.get_total_points(),
            'vision_debug': self.vision_debug_circles,
            'resources': self.resources.serialize(),
            'age': self.brain.age,  # Age in seconds
            'brain': self.brain.serialize(),
            'offspring_count': self.offspring_count  # Evolutionary success
        }
    
    def serialize(self) -> Dict[str, Any]:
        """Alias for get_state() for compatibility with simulation"""
        return self.get_state()