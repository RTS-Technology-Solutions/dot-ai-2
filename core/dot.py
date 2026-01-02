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
        DEFEND_ENERGY_COST = 3.0  # per second (3% of max per second, approximated)
        
        if self.is_defending:
            self.resources.deplete_energy(DEFEND_ENERGY_COST * dt)
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
        
        # 6. Execute action
        offspring_result = self.execute_action(perceived_world, dt)
        
        # 7. Update visuals
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
        hunger_pct = self.resources.hunger / 100.0
        
        # Get DNA points
        attack_points = self.dna.get_gene_value('attack')
        defend_points = self.dna.get_gene_value('defend')
        replicate_points = self.dna.get_gene_value('replicate')
        
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
        # Higher when: enemy weak, self strong, have attack points
        perceived_dots = perceived_world.get('dots', [])
        if attack_points > 0 and perceived_dots:
            weakest_enemy = None
            min_enemy_health = float('inf')
            
            for dot_info in perceived_dots:
                enemy_health = dot_info.get('health', 100)
                if enemy_health < min_enemy_health:
                    min_enemy_health = enemy_health
                    weakest_enemy = dot_info
            
            if weakest_enemy:
                enemy_weakness = 1.0 - (min_enemy_health / 100.0)
                own_strength = health_pct
                attack_utility = enemy_weakness * (attack_points / 50.0) * own_strength * 5.0
                
                # Only attack if reasonably healthy
                if health_pct < 0.5:
                    attack_utility *= 0.2
                
                utilities['attack'] = attack_utility
                self.attack_target = weakest_enemy['id']
            else:
                utilities['attack'] = 0.0
        else:
            utilities['attack'] = 0.0
            self.attack_target = None
        
        # 3. DEFEND UTILITY
        # Higher when: low health, enemies nearby, have defend points
        if defend_points > 0:
            danger_level = 0.0
            
            # Danger from visible enemies
            threat_count = len(perceived_dots)
            if threat_count > 0:
                danger_level = min(1.0, threat_count * 0.3)
            
            # Danger from low health
            if health_pct < 0.5:
                danger_level = max(danger_level, 1.0 - health_pct)
            
            defend_utility = danger_level * (defend_points / 50.0) * (1 + threat_count * 0.5)
            utilities['defend'] = defend_utility
        else:
            utilities['defend'] = 0.0
        
        # 4. REPLICATE UTILITY
        # Higher when: high energy, high health, have replicate points, fewer dots nearby
        if replicate_points > 0:
            # Check if we have enough energy (need 80%)
            if energy_pct >= 0.8 and health_pct >= 0.7:
                crowding_penalty = min(1.0, len(perceived_dots) * 0.2)
                replicate_utility = (replicate_points / 50.0) * energy_pct * health_pct * (1.0 - crowding_penalty) * 3.0
                utilities['replicate'] = replicate_utility
            else:
                utilities['replicate'] = 0.0
        else:
            utilities['replicate'] = 0.0
        
        # 5. IDLE UTILITY (baseline)
        utilities['idle'] = 1.0
        
        # Pick action with highest utility
        best_action = max(utilities, key=utilities.get)
        
        return best_action
    
    def execute_action(self, perceived_world: Dict[str, Any], dt: float) -> Optional[DNAProfile]:
        """
        Execute the decided action.
        Returns offspring DNA if replication occurred, None otherwise.
        """
        if self.current_action == "seek_food":
            self.is_defending = False
            perceived_food = perceived_world.get('food', [])
            if perceived_food:
                target_food = perceived_food[0]
                self.move_toward(target_food['position'], dt)
            return None
        
        elif self.current_action == "attack":
            self.is_defending = False
            return self.execute_attack(perceived_world, dt)
        
        elif self.current_action == "defend":
            self.execute_defend()
            return None
        
        elif self.current_action == "replicate":
            self.is_defending = False
            return self.execute_replicate()
        
        else:  # idle
            self.is_defending = False
            self.velocity = [0.0, 0.0]
            return None
    
    def execute_attack(self, perceived_world: Dict[str, Any], dt: float) -> None:
        """Execute attack action - move toward target."""
        if self.attack_target is not None:
            # Find target dot
            perceived_dots = perceived_world.get('dots', [])
            for dot_info in perceived_dots:
                if dot_info['id'] == self.attack_target:
                    self.move_toward(dot_info['position'], dt)
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
        Execute replication action.
        Returns offspring data if successful, None otherwise.
        """
        result = self.action_manager.replicate.execute(self)
        
        if result['success']:
            # Deduct energy cost
            self.resources.energy = result['parent_energy_after']
            
            # Calculate offset for child position (spawn nearby)
            angle = random.random() * 2 * math.pi
            distance = 30  # spawn 30 pixels away
            child_x = self.position[0] + math.cos(angle) * distance
            child_y = self.position[1] + math.sin(angle) * distance
            
            # Return offspring data in expected format
            return {
                'result': 'OFFSPRING',
                'child_dna': result['offspring_dna'],
                'child_pos': [child_x, child_y]
            }
        
        return None
    
    def move_toward(self, target: Tuple[float, float], dt: float):
        """Move toward a target position."""
        # Calculate direction
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1.0:
            # Normalize and apply speed
            speed = self.dna.get_gene_value('movement_speed') * 0.5  # 0-25 pixels/sec (max 50 points)
            self.velocity[0] = (dx / distance) * speed
            self.velocity[1] = (dy / distance) * speed
            
            # Update position
            self.position[0] += self.velocity[0] * dt
            self.position[1] += self.velocity[1] * dt
        else:
            self.velocity = [0.0, 0.0]
    
    def eat(self, food_energy: float):
        """Consume food and gain energy."""
        self.resources.eat(food_energy, self.brain)
    
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
            'brain': self.brain.serialize()
        }
    
    def serialize(self) -> Dict[str, Any]:
        """Alias for get_state() for compatibility with simulation"""
        return self.get_state()