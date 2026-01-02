# 🎯 PHASE 1 TECHNICAL SPECIFICATION

**Goal:** Core DNA & Resource System with Single Dot Demo  
**Timeline:** Week 1-2  
**Status:** 🟢 READY TO START

---

## 📦 DELIVERABLES

### Must-Have Features
1. ✅ DNA Profile System (switches + points)
2. ✅ Brain class with age-gated capacity
3. ✅ Resource management (energy, health)
4. ✅ Basic dot entity with DNA
5. ✅ Simple movement action
6. ✅ Basic eating action (Stage 1 only)
7. ✅ Energy depletion over time
8. ✅ Death mechanics (energy → 0)
9. ✅ Food entity system
10. ✅ Pygame renderer (simple visualization)
11. ✅ Logging system
12. ✅ Configuration system

### Demo Success Criteria
- Single dot spawns with DNA profile
- Dot moves toward food
- Dot eats food, gains energy
- Energy depletes over time
- Dot dies when energy reaches 0
- All decisions logged and observable

---

## 🏗️ ARCHITECTURE

### Core Principle: **LOGIC ↔ RENDERER SEPARATION**

```
core/
├── dna.py           ← DNA Profile, genes, mutations
├── brain.py         ← Brain, memory, decision-making
├── resources.py     ← Energy, health, hunger tracking
├── dot.py           ← Dot entity (pure logic)
├── food.py          ← Food entity
├── simulation.py    ← Main simulation engine
└── config.py        ← Configuration management

renderers/
└── pygame_renderer.py  ← Pygame visualization

utils/
├── logger.py        ← Logging system
└── math_utils.py    ← Helper functions

main.py              ← Entry point
```

---

## 🧬 DNA SYSTEM SPECIFICATION

### DNA Profile Class

```python
class DNAProfile:
    """Represents a dot's genetic makeup"""
    
    def __init__(self, total_points=100):
        self.total_points = total_points
        self.points_allocated = 0
        
        # Brain genes
        self.brain_memory = Gene("memory", enabled=True, points=10)
        self.brain_sense_slots = Gene("sense_slots", enabled=True, points=12)
        self.brain_action_slots = Gene("action_slots", enabled=True, points=8)
        
        # Sense genes
        self.vision_distance = Gene("vision_distance", enabled=True, points=15)
        self.vision_fov = Gene("vision_fov", enabled=True, points=15)
        self.dot_detection = Gene("dot_detection", enabled=True, points=8)
        self.food_detection = Gene("food_detection", enabled=True, points=12)
        self.power_detection = Gene("power_detection", enabled=False, points=0)
        self.food_amount_detection = Gene("food_amount_detection", enabled=False, points=0)
        self.dna_strength_detection = Gene("dna_strength_detection", enabled=False, points=0)
        self.social_sense = Gene("social_sense", enabled=False, points=0)
        
        # Action genes
        self.movement_speed = Gene("movement_speed", enabled=True, points=8)
        self.movement_max_energy = Gene("movement_max_energy", enabled=True, points=12)
        self.defend = Gene("defend", enabled=False, points=0)
        self.attack = Gene("attack", enabled=False, points=0)
        self.eat = Gene("eat", enabled=True, points=0)  # Always enabled
        self.replicate = Gene("replicate", enabled=False, points=0)
        self.revive = Gene("revive", enabled=False, points=0)
    
    def validate(self):
        """Ensure DNA is valid"""
        allocated = sum(gene.points for gene in self.get_all_genes())
        return allocated <= self.total_points
    
    def get_all_genes(self):
        """Return list of all genes"""
        return [getattr(self, attr) for attr in dir(self) 
                if isinstance(getattr(self, attr), Gene)]
    
    def serialize(self):
        """Export to dict for saving/networking"""
        return {
            'total_points': self.total_points,
            'genes': {gene.name: gene.to_dict() for gene in self.get_all_genes()}
        }

class Gene:
    """Individual gene with switch and point allocation"""
    
    def __init__(self, name, enabled=False, points=0):
        self.name = name
        self.enabled = enabled
        self.points = points
    
    def to_dict(self):
        return {'enabled': self.enabled, 'points': self.points}
```

---

## 🧠 BRAIN SYSTEM SPECIFICATION

### Brain Class

```python
class Brain:
    """Manages dot's cognitive abilities and decision-making"""
    
    def __init__(self, dna_profile, age=0):
        self.dna = dna_profile
        self.age = age  # In seconds
        
        # Age-gated capacity
        self.base_capacity = 100
        self.growth_rate = 1.5  # Points per second
        self.capacity = self.calculate_capacity()
        
        # Memory system
        self.memory_slots = self.calculate_memory_slots()
        self.memories = []
        
        # Sense/Action slots
        self.sense_slots = self.calculate_sense_slots()
        self.action_slots = self.calculate_action_slots()
        
        # Active senses (static loadout)
        self.active_senses = self.load_senses()
        
        # Active actions
        self.active_actions = self.load_actions()
    
    def calculate_capacity(self):
        """Age-gated brain capacity"""
        return self.base_capacity + (self.age * self.growth_rate)
    
    def calculate_memory_slots(self):
        if not self.dna.brain_memory.enabled:
            return 0
        base = 10
        bonus = self.dna.brain_memory.points * 0.5
        age_bonus = self.age * 0.5
        return int(base + bonus + age_bonus)
    
    def calculate_sense_slots(self):
        if not self.dna.brain_sense_slots.enabled:
            return 0
        base = 2
        bonus = self.dna.brain_sense_slots.points * 0.1
        return int(base + bonus)
    
    def calculate_action_slots(self):
        if not self.dna.brain_action_slots.enabled:
            return 0
        base = 2
        bonus = self.dna.brain_action_slots.points * 0.1
        return int(base + bonus)
    
    def update_age(self, delta_time):
        """Update age and recalculate capacity"""
        self.age += delta_time
        self.capacity = self.calculate_capacity()
        self.memory_slots = self.calculate_memory_slots()
```

---

## 💧 RESOURCE SYSTEM SPECIFICATION

### Resources Class

```python
class Resources:
    """Manages energy, health, and hunger"""
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Energy
        self.max_energy = self.calculate_max_energy()
        self.energy = self.max_energy
        
        # Health
        self.max_health = 100  # Base value for now
        self.health = self.max_health
        
        # Hunger (derived from energy ratio)
        self.hunger = 0.0
    
    def calculate_max_energy(self):
        """Based on movement_max_energy gene"""
        base = 100
        bonus = self.dna.movement_max_energy.points * 5
        return base + bonus
    
    def update_hunger(self):
        """Hunger increases as energy decreases"""
        self.hunger = 1.0 - (self.energy / self.max_energy)
    
    def deplete_energy(self, amount):
        """Remove energy"""
        self.energy = max(0, self.energy - amount)
        self.update_hunger()
    
    def add_energy(self, amount):
        """Add energy (from eating)"""
        self.energy = min(self.max_energy, self.energy + amount)
        self.update_hunger()
    
    def deplete_health(self, amount):
        """Damage health"""
        self.health = max(0, self.health - amount)
    
    def add_health(self, amount):
        """Heal health"""
        self.health = min(self.max_health, self.health + amount)
    
    def is_alive(self):
        """Check if resources support life"""
        return self.health > 0
    
    def is_starving(self):
        """Check if in starvation state"""
        return self.energy <= 0 and self.health > 0
```

---

## 🔵 DOT ENTITY SPECIFICATION

### Dot Class (Phase 1 - Minimal)

```python
class Dot:
    """Autonomous agent with DNA, brain, and resources"""
    
    def __init__(self, dot_id, position, dna_profile):
        self.id = dot_id
        self.position = list(position)  # [x, y]
        self.velocity = [0.0, 0.0]
        
        # Core systems
        self.dna = dna_profile
        self.brain = Brain(dna_profile)
        self.resources = Resources(dna_profile)
        
        # State
        self.age = 0.0
        self.state = "alive"  # alive, starving, dead
        self.current_action = None
        
        # Visual properties (calculated)
        self.color = self.calculate_color()
        self.size = self.calculate_size()
    
    def update(self, delta_time, world_state):
        """Main update loop"""
        if self.state == "dead":
            return
        
        # Age
        self.age += delta_time
        self.brain.update_age(delta_time)
        
        # Energy depletion (idle cost)
        idle_cost = 0.1 * delta_time
        self.resources.deplete_energy(idle_cost)
        
        # Check starvation
        if self.resources.is_starving():
            self.enter_starvation()
        
        # Check death
        if not self.resources.is_alive():
            self.die()
            return
        
        # Make decision
        action = self.decide_action(world_state)
        self.execute_action(action, delta_time, world_state)
        
        # Update visuals
        self.color = self.calculate_color()
        self.size = self.calculate_size()
    
    def decide_action(self, world_state):
        """Utility-based decision making (Phase 1: simple)"""
        # For now, just seek food if hungry
        if self.resources.hunger > 0.3:
            return "seek_food"
        return "idle"
    
    def execute_action(self, action, delta_time, world_state):
        """Perform action"""
        if action == "seek_food":
            self.move_toward_food(world_state, delta_time)
        elif action == "idle":
            pass  # Just burn idle energy
    
    def move_toward_food(self, world_state, delta_time):
        """Simple movement toward nearest food"""
        if not world_state['food']:
            return
        
        # Find nearest food
        nearest_food = min(world_state['food'], 
                          key=lambda f: self.distance_to(f['position']))
        
        # Move toward it
        direction = self.vector_to(nearest_food['position'])
        speed = self.get_movement_speed()
        
        self.velocity = [direction[0] * speed, direction[1] * speed]
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
        
        # Energy cost for movement
        movement_cost = speed * 0.1 * delta_time
        self.resources.deplete_energy(movement_cost)
    
    def get_movement_speed(self):
        """Calculate speed from DNA"""
        base = 50  # pixels per second
        bonus = self.dna.movement_speed.points * 5
        return base + bonus
    
    def enter_starvation(self):
        """Enter starvation state"""
        self.state = "starving"
        # Health drains
        self.resources.deplete_health(1.5)
    
    def die(self):
        """Death"""
        self.state = "dead"
    
    def calculate_color(self):
        """Color based on energy (red→yellow→green)"""
        ratio = self.resources.energy / self.resources.max_energy
        if ratio > 0.6:
            return (76, 175, 80)  # Green
        elif ratio > 0.3:
            return (255, 235, 59)  # Yellow
        else:
            return (255, 107, 107)  # Red
    
    def calculate_size(self):
        """Size based on DNA strength"""
        min_size = 3
        max_size = 10
        ratio = min(1.0, self.dna.total_points / 200)
        return min_size + (max_size - min_size) * ratio
    
    def serialize(self):
        """Export state for renderer"""
        return {
            'id': self.id,
            'position': self.position,
            'velocity': self.velocity,
            'age': self.age,
            'state': self.state,
            'energy': self.resources.energy,
            'max_energy': self.resources.max_energy,
            'health': self.resources.health,
            'max_health': self.resources.max_health,
            'dna_points': self.dna.total_points,
            'color': self.color,
            'size': self.size,
            'current_action': self.current_action
        }
    
    # Helper methods
    def distance_to(self, position):
        dx = self.position[0] - position[0]
        dy = self.position[1] - position[1]
        return (dx*dx + dy*dy) ** 0.5
    
    def vector_to(self, position):
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        length = (dx*dx + dy*dy) ** 0.5
        if length > 0:
            return [dx/length, dy/length]
        return [0, 0]
```

---

## 🍎 FOOD ENTITY SPECIFICATION

```python
class Food:
    """Food entity"""
    
    def __init__(self, food_id, position, energy_value):
        self.id = food_id
        self.position = list(position)
        self.energy_value = energy_value
        self.max_energy = energy_value
        self.depleted = False
    
    def consume(self, amount):
        """Consume food energy"""
        taken = min(amount, self.energy_value)
        self.energy_value -= taken
        if self.energy_value <= 0:
            self.depleted = True
        return taken
    
    def serialize(self):
        return {
            'id': self.id,
            'position': self.position,
            'energy_value': self.energy_value,
            'max_energy': self.max_energy,
            'size': 3 + (self.energy_value / self.max_energy) * 3
        }
```

---

## 🎮 SIMULATION ENGINE SPECIFICATION

```python
class DotSimulation:
    """Main simulation engine (pure logic, no rendering)"""
    
    def __init__(self, config):
        self.config = config
        self.dots = []
        self.food = []
        self.generation = 1
        self.time_elapsed = 0.0
        self.paused = False
        
        # Counters
        self.next_dot_id = 0
        self.next_food_id = 0
    
    def initialize(self):
        """Set up initial state"""
        # Spawn initial dot
        dna = DNAProfile(total_points=100)
        dot = Dot(self.next_dot_id, [400, 300], dna)
        self.dots.append(dot)
        self.next_dot_id += 1
        
        # Spawn initial food
        for _ in range(10):
            pos = [random.randint(50, 750), random.randint(50, 550)]
            energy = random.randint(50, 150)
            food = Food(self.next_food_id, pos, energy)
            self.food.append(food)
            self.next_food_id += 1
    
    def update(self, delta_time):
        """Update simulation state"""
        if self.paused:
            return
        
        self.time_elapsed += delta_time
        
        # Update all dots
        world_state = self.get_world_state()
        for dot in self.dots:
            dot.update(delta_time, world_state)
        
        # Check eating
        self.check_eating()
        
        # Remove depleted food
        self.food = [f for f in self.food if not f.depleted]
        
        # Remove dead dots
        self.dots = [d for d in self.dots if d.state != "dead"]
    
    def check_eating(self):
        """Check if dots are touching food"""
        for dot in self.dots:
            for food in self.food:
                distance = dot.distance_to(food.position)
                if distance < 10:  # Eating range
                    # Consume food
                    energy_gained = food.consume(10)  # 10 per frame
                    dot.resources.add_energy(energy_gained)
    
    def get_world_state(self):
        """Serialized world state for dot decision-making"""
        return {
            'dots': [d.serialize() for d in self.dots],
            'food': [f.serialize() for f in self.food],
            'time': self.time_elapsed
        }
    
    def get_state(self):
        """Full state for renderer"""
        return {
            'dots': [d.serialize() for d in self.dots],
            'food': [f.serialize() for f in self.food],
            'generation': self.generation,
            'time': self.time_elapsed,
            'stats': {
                'dot_count': len(self.dots),
                'food_count': len(self.food)
            }
        }
```

---

## 🎨 PYGAME RENDERER SPECIFICATION

```python
class PygameRenderer:
    """Simple Pygame visualization"""
    
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dot AI 2.0 - Phase 1")
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
    
    def render(self, simulation_state):
        """Render current state"""
        # Clear screen
        self.screen.fill((18, 18, 18))  # Dark background
        
        # Draw food
        for food in simulation_state['food']:
            pos = (int(food['position'][0]), int(food['position'][1]))
            size = int(food['size'])
            pygame.draw.circle(self.screen, (76, 175, 80), pos, size)
        
        # Draw dots
        for dot in simulation_state['dots']:
            pos = (int(dot['position'][0]), int(dot['position'][1]))
            size = int(dot['size'])
            color = tuple(dot['color'])
            pygame.draw.circle(self.screen, color, pos, size)
            
            # Draw health/energy bars
            self.draw_dot_stats(dot, pos)
        
        # Draw HUD
        self.draw_hud(simulation_state)
        
        pygame.display.flip()
        return self.clock.tick(60) / 1000.0  # Delta time
    
    def draw_dot_stats(self, dot, pos):
        """Draw mini health/energy bars above dot"""
        bar_width = 30
        bar_height = 3
        x = pos[0] - bar_width // 2
        y = pos[1] - 15
        
        # Energy bar
        energy_ratio = dot['energy'] / dot['max_energy']
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (76, 175, 80), (x, y, int(bar_width * energy_ratio), bar_height))
        
        # Health bar
        y += 5
        health_ratio = dot['health'] / dot['max_health']
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (255, 107, 107), (x, y, int(bar_width * health_ratio), bar_height))
    
    def draw_hud(self, state):
        """Draw stats overlay"""
        texts = [
            f"Generation: {state['generation']}",
            f"Time: {state['time']:.1f}s",
            f"Dots: {state['stats']['dot_count']}",
            f"Food: {state['stats']['food_count']}",
            "",
            "Controls:",
            "SPACE - Pause",
            "ESC - Quit"
        ]
        
        y = 10
        for text in texts:
            surface = self.font.render(text, True, (76, 175, 80))
            self.screen.blit(surface, (10, y))
            y += 25
    
    def handle_events(self):
        """Process input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                if event.key == pygame.K_SPACE:
                    return "pause"
        return None
```

---

## 📝 MAIN ENTRY POINT

```python
# main.py
def main():
    # Load configuration
    config = load_config("configs/default_config.yaml")
    
    # Initialize simulation
    simulation = DotSimulation(config)
    simulation.initialize()
    
    # Initialize renderer
    renderer = PygameRenderer()
    
    # Main loop
    running = True
    while running:
        # Handle input
        event = renderer.handle_events()
        if event == "quit":
            running = False
        elif event == "pause":
            simulation.paused = not simulation.paused
        
        # Update simulation
        delta_time = renderer.clock.get_time() / 1000.0
        simulation.update(delta_time)
        
        # Render
        state = simulation.get_state()
        renderer.render(state)
    
    pygame.quit()

if __name__ == "__main__":
    main()
```

---

## ✅ PHASE 1 ACCEPTANCE CRITERIA

1. ✅ Single dot spawns with valid DNA profile
2. ✅ Dot moves toward nearest food
3. ✅ Dot eats food when in range, gains energy
4. ✅ Energy depletes over time (idle + movement)
5. ✅ Dot enters starvation at 0 energy
6. ✅ Dot dies when health reaches 0
7. ✅ Visualization shows energy/health with color + bars
8. ✅ Can pause/resume simulation
9. ✅ Stats displayed on screen
10. ✅ All decisions logged to console

---

## 🎯 NEXT STEPS AFTER PHASE 1

Once Phase 1 is complete and tested:
- Phase 2: Add more senses (vision, detection)
- Phase 3: Add more actions (attack, defend, replicate)
- Phase 4: Add food ecosystem (death→food, spawning)
- Phase 5: Add evolution and reproduction

**Ready to start coding!** 🚀
