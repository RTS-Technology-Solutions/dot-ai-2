"""
Simulation Engine - Main Logic Loop
Pure logic, no rendering code
"""

import random
import math
from .dot import Dot
from .food import Food
from .dna import DNAProfile


class DotSimulation:
    """
    Main simulation engine
    - Manages dots and food
    - Updates world state
    - Handles spawning and cleanup
    - Exports state for renderers
    """
    
    def __init__(self, config):
        self.config = config
        
        # Entities
        self.dots = []
        self.food = []
        
        # World bounds
        self.width = config.get('width', 800)
        self.height = config.get('height', 600)
        
        # State
        self.generation = 1
        self.time_elapsed = 0.0
        self.paused = False
        
        # Counters
        self.next_dot_id = 0
        self.next_food_id = 0
        
        # Stats
        self.total_dots_created = 0
        self.total_dots_died = 0
        self.total_food_consumed = 0
        self.total_births = 0
        self.total_attacks = 0
    
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
            self.dots.append(dot)
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
        """Spawn a new dot"""
        dot = Dot(self.next_dot_id, position, dna_profile)
        self.dots.append(dot)
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
                    else:
                        print(f"❌ Dot #{attacker.id} missed Dot #{target.id}!")
                
                # Clear target
                attacker.attack_target = None
    
    def dot_to_food(self, dot):
        """Convert dead dot to food"""
        # Food energy = remaining dot energy + half of health
        food_energy = dot.resources.energy + (dot.resources.health * 0.5)
        
        if food_energy > 0:
            food = Food(self.next_food_id, dot.position, food_energy)
            self.food.append(food)
            self.next_food_id += 1
    
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
        
        for dot in self.dots:
            result = dot.update(delta_time, world_state)
            # Collect offspring data
            if result and result.get('result') == 'OFFSPRING':
                offspring_data.append(result)
        
        # 2. Handle combat
        self.handle_combat()
        
        # 3. Spawn offspring
        for data in offspring_data:
            self.spawn_dot(data['child_pos'], data['child_dna'])
            self.total_births += 1
        
        # 4. Check eating
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
            self.dot_to_food(dot)
        
        before_dots = len(self.dots)
        self.dots = [d for d in self.dots if d.resources.is_alive()]
        died = before_dots - len(self.dots)
        if died > 0:
            self.total_dots_died += died
            print(f"💀 {died} dot(s) died (Bodies → Food)")
        
        # 7. Respawn food if running low
        if len(self.food) < 8:
            self.spawn_food()
        
        # 8. Update time
        self.time_elapsed += delta_time
    
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
                        # Add energy to dot
                        overflow = dot.resources.add_energy(energy_gained)
                        
                        # Overflow converts to DNA points (Phase 1: just track it)
                        if overflow > 0:
                            # In future: convert to DNA points
                            pass
    
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
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        status = "PAUSED" if self.paused else "RUNNING"
        print(f"⏸️  Simulation {status}")
    
    def __repr__(self):
        return f"DotSimulation(dots={len(self.dots)}, food={len(self.food)}, time={self.time_elapsed:.1f}s)"
