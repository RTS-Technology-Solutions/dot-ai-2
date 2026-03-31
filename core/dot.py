"""
The dot is defined here, not in simulation.py, because its behavior logic
is complex enough to demand isolation. Keeping the agent class separate from
the world class means neither knows more about the other than it needs to —
the simulation calls update(), the dot calls nothing on the simulation directly;
all communication flows through the world_state dict and the update() return value.
"""

import math
import random
from typing import Optional, Tuple, Dict, Any, List
from .dna import DNAProfile
from .brain import Brain
from .resources import Resources
from .senses import PerceptionSystem
from .actions import ActionManager
from configs import get_config


class Dot:
    """
    A single agent in the ecosystem.

    Exists as a class rather than a data struct because an agent has persistent
    state (memory, current action, target) that must survive across update calls.
    This is also where DNA-to-behavior translation happens — every tunable constant
    lives in get_config(), but the logic for how those constants combine into a
    decision is owned here.

    decide_action() and execute_action() are kept separate because decision and
    execution are distinct cognitive phases. The split makes it possible to inspect
    the elected action before it runs, which matters for metrics and debugging.
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
        Advance this dot by one simulation tick.

        Returns offspring data if reproduction occurred, None otherwise.
        This return pattern lets the simulation collect all new agents in a single
        pass over the dot list without maintaining a separate spawning queue.
        """
        # 1. Deplete energy based on movement
        speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        is_moving = speed > 0.1
        
        # Energy costs
        _bcfg = get_config().behavior
        IDLE_ENERGY_COST = _bcfg.idle_energy_cost
        MOVEMENT_ENERGY_COST = _bcfg.movement_energy_cost
        
        if self.is_defending:
            # Defending costs a configurable fraction of max energy per second
            defend_cost = self.resources.max_energy * _bcfg.defend_energy_cost_pct * dt
            self.resources.deplete_energy(defend_cost)
        elif is_moving:
            self.resources.deplete_energy((IDLE_ENERGY_COST + MOVEMENT_ENERGY_COST) * dt)
        else:
            self.resources.deplete_energy(IDLE_ENERGY_COST * dt)
        
        # 2. Apply starvation damage
        if self.resources.is_starving():
            STARVATION_DAMAGE = _bcfg.starvation_damage
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
        Select the action with the highest utility score.

        Utility AI is used instead of a priority rule tree because it degrades
        gracefully when multiple needs compete. Hunger, danger, and reproductive
        drive are all real-valued scores that compose linearly rather than
        fragmenting into a fragile nested if/else chain. Adding a new behavior
        means adding one utility calculation, not auditing a priority chain.
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
        
        # 1. SEEK FOOD — hunger scales the weight so survival urgency can always outbid other drives
        perceived_food = perceived_world.get('food', [])
        _bcfg = get_config().behavior
        if perceived_food:
            food_utility = hunger_pct * _bcfg.food_hunger_scale
            # Past this threshold other actions can't meaningfully improve survival — lock onto food
            if hunger_pct > _bcfg.food_hungry_threshold:
                food_utility *= _bcfg.food_hungry_bonus
            utilities['seek_food'] = food_utility
        else:
            utilities['seek_food'] = 0.0
        
        # 2. ATTACK — only worth the risk when hunger makes a kill's caloric value exceed the cost of fighting
        perceived_dots = perceived_world.get('dots', [])
        if attack_points > 0 and perceived_dots and hunger_pct > _bcfg.attack_hunt_threshold:
            best_target = None
            max_score = -float('inf')
            
            can_see_dna = self.dna.get_gene_value('dna_strength_detection') > 0
            
            for dot_info in perceived_dots:
                enemy_health = dot_info.get('health', 100)
                enemy_energy = dot_info.get('energy', 100)
                enemy_max_health = dot_info.get('max_health', 100)
                enemy_state = dot_info.get('state', 'alive')
                
                # Strength is HP + energy together; full HP but empty energy still means a poor fighter
                health_weakness = 1.0 - (enemy_health / max(1, enemy_max_health))
                energy_weakness = 1.0 - (enemy_energy / max(1, dot_info.get('max_energy', 100)))
                
                # A starving dot can't flee or deal effective damage — the exploitation window is narrow
                if enemy_state == 'starving':
                    weakness_score = _bcfg.attack_starving_weakness
                else:
                    # Energy weighted higher because it governs movement and action speed, not just durability
                    weakness_score = (energy_weakness * 0.6 + health_weakness * 0.4)
                
                # Calculate expected food value from kill
                if can_see_dna and 'perceived_dna_strength' in dot_info:
                    enemy_dna = dot_info['perceived_dna_strength']
                    food_value = 30 + enemy_dna
                else:
                    food_value = _bcfg.attack_food_value_assumption
                
                # Priority order reflects kill probability: starving → low energy → low health
                score = weakness_score * (food_value / _bcfg.attack_food_value_normalizer)
                
                if score > max_score:
                    max_score = score
                    best_target = dot_info
            
            if best_target:
                own_strength = health_pct
                hunger_motivation = hunger_pct * _bcfg.attack_hunger_motivation_scale
                attack_utility = max_score * (attack_points / 50.0) * own_strength * hunger_motivation * _bcfg.attack_multiplier
                
                # Reduce if low health (risky)
                if health_pct < _bcfg.attack_low_health_critical:
                    attack_utility *= _bcfg.attack_low_health_penalty_critical
                elif health_pct < _bcfg.attack_low_health_moderate:
                    attack_utility *= _bcfg.attack_low_health_penalty_moderate
                
                utilities['attack'] = attack_utility
                self.attack_target = best_target['id']
            else:
                utilities['attack'] = 0.0
        else:
            utilities['attack'] = 0.0
            self.attack_target = None
        
        # 3. DEFEND — blocking caps the damage rate; worth it only when threat level exceeds the energy cost
        if defend_points > 0:
            danger_level = 0.0
            
            # One enemy when healthy can be fought; it's overwhelm + low HP together that demands defense
            threat_count = len(perceived_dots)
            
            if threat_count >= _bcfg.defend_threat_count_threshold:
                danger_level = min(1.0, (threat_count - (_bcfg.defend_threat_count_threshold - 1)) * _bcfg.defend_threat_danger_scale)
            elif health_pct < _bcfg.defend_health_threshold and threat_count > 0:
                danger_level = (1.0 - health_pct) * _bcfg.defend_health_danger_scale
            
            if danger_level > 0:
                defend_utility = danger_level * (defend_points / 50.0) * _bcfg.defend_multiplier
                utilities['defend'] = defend_utility
            else:
                utilities['defend'] = 0.0
        else:
            utilities['defend'] = 0.0
        
        # 4. REPLICATE (asexual) — fallback when no mate is found; high energy threshold because the cost is steep
        if replicate_points > 0:
            # Check if we have enough energy (threshold from config)
            if energy_pct >= _bcfg.replicate_energy_threshold and health_pct >= _bcfg.replicate_health_threshold:
                # Density sensor sees outside the vision cone — prefer it because visible dot count underestimates crowd
                nearby_density = perceived_world.get('nearby_density', len(perceived_dots))
                crowding_penalty = min(1.0, nearby_density * _bcfg.replicate_crowding_scale)
                replicate_utility = (replicate_points / 50.0) * energy_pct * health_pct * (1.0 - crowding_penalty) * _bcfg.replicate_multiplier
                utilities['replicate'] = replicate_utility
            else:
                utilities['replicate'] = 0.0
        else:
            utilities['replicate'] = 0.0
        
        # 5. SEEK MATE (sexual) — preferred over asexual: lower energy cost and offspring inherit novel gene combinations
        if replicate_points > 0:
            if energy_pct >= _bcfg.seek_mate_energy_threshold and health_pct >= _bcfg.seek_mate_health_threshold:
                # Exclude self — mating with self produces a clone, negating the point of sexual reproduction
                potential_mates = [d for d in perceived_dots 
                                  if d.get('id') != self.id and  # Don't mate with self!
                                  d.get('health', 0) > 70 and 
                                  d.get('can_reproduce', False)]
                
                if potential_mates:
                    # Stronger utility than asexual (lower cost = more appealing)
                    mate_count_bonus = min(1.0, len(potential_mates) * _bcfg.seek_mate_count_bonus_scale)
                    mate_utility = (replicate_points / 50.0) * energy_pct * health_pct * (1.0 + mate_count_bonus) * _bcfg.seek_mate_multiplier
                    utilities['seek_mate'] = mate_utility
                    
                    # Health is a fitness proxy: high health at mating time correlates with effective DNA allocation
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
        
        # 6. EXPLORE — without this, dots with no visible stimuli would idle and starve; movement keeps them finding food patches
        nothing_visible = len(perceived_food) == 0 and len(perceived_dots) == 0
        
        if nothing_visible:
            # Scale urgency with hunger: a healthy dot wanders; a hungry dot needs to reach food quickly
            explore_base = _bcfg.explore_base
            hunger_boost = hunger_pct * _bcfg.explore_hunger_scale
            health_boost = health_urgency * _bcfg.explore_health_scale
            explore_utility = explore_base + hunger_boost + health_boost
            utilities['explore'] = explore_utility
        else:
            utilities['explore'] = 0.0
        
        # 7. IDLE — exists as a floor, not a reward; penalized in crowds because stationary dots block mates and food access
        nearby_density = perceived_world.get('nearby_density', 0)
        density_penalty = min(_bcfg.idle_density_penalty_max, nearby_density * _bcfg.idle_density_penalty_scale)
        idle_penalty = health_urgency * _bcfg.idle_health_urgency_scale + hunger_pct * _bcfg.idle_hunger_penalty_scale + density_penalty
        utilities['idle'] = max(_bcfg.idle_min, _bcfg.idle_base - idle_penalty)
        
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
        Dispatch to the appropriate execute_* handler for the chosen action.

        Split from decide_action() so the tick pipeline reads as three
        distinct phases: perceive → decide → execute.
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
        """
        Move toward the elected attack target.

        Actual damage is dealt by the simulation when proximity is confirmed,
        not here, so both dots in a fight are at their final positions before
        damage is resolved.
        """
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
        """
        Activate the defending flag and stop movement.

        The defending flag is what AttackAction checks for mitigation — the
        cost and reduction logic live there, not here. This method exists only
        to set that flag and zero velocity.
        """
        self.is_defending = True
        self.velocity = [0.0, 0.0]
    
    def execute_replicate(self) -> Optional[Dict[str, Any]]:
        """
        Trigger asexual reproduction via the action manager.

        Used as a fallback when no mate is available. The action manager
        owns gene mutation and energy cost logic — this method connects
        the utility decision to that machinery.
        """
        world_state = {'bounds': {'width': 1200, 'height': 800}}
        result = self.action_manager.replicate.execute(self, world_state, 0.0, mate=None)
        
        if result and result.get('result') == 'OFFSPRING_ASEXUAL':
            return result
        
        return None
    
    def execute_seek_mate(self, perceived_world: Dict[str, Any], world_state: Dict[str, Any], dt: float) -> Optional[Dict[str, Any]]:
        """
        Move toward a potential mate; signal mate_request when in range.

        Crossover is handled by the simulation, not here, because both partners
        must independently elect seek_mate and point at each other before the
        simulation will execute the crossover. This method only moves and signals.
        Returns a MATE_REQUEST dict when in range, None while still approaching.
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
        MATING_RANGE = get_config().behavior.mating_range
        
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
        """
        Set velocity toward target and advance position by dt.

        Speed is amplified when the dot is starving because the window for
        finding food before death closes faster — without urgency multipliers,
        a starving dot moves at the same speed as a comfortable one and may
        die before reaching visible food.

        Boundary clamping zeroes the relevant velocity component on contact
        rather than reflecting it, so dots pressed against a wall don’t oscillate.
        """
        # Calculate direction
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1.0:
            # Base speed from DNA
            _bcfg = get_config().behavior
            base_speed = _bcfg.movement_speed_base
            bonus_speed = self.dna.get_gene_value('movement_speed') * _bcfg.movement_speed_per_point
            speed = base_speed + bonus_speed
            
            # Urgency multipliers
            if self.resources.is_starving():
                speed *= _bcfg.starving_speed_multiplier
            elif self.resources.hunger > _bcfg.hungry_speed_threshold:
                speed *= _bcfg.hungry_speed_multiplier
            
            # Normalize and apply speed
            self.velocity[0] = (dx / distance) * speed
            self.velocity[1] = (dy / distance) * speed
            
            # Update position
            self.position[0] += self.velocity[0] * dt
            self.position[1] += self.velocity[1] * dt
            
            # ENFORCE BOUNDARIES - keep dots on screen (use dynamic world bounds)
            BOUNDARY_MARGIN = _bcfg.movement_boundary_margin
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
        """
        Deliver food energy into the resource cascade and record the event.

        The brain reward and memory write happen here rather than in Resources
        because an eating memory connects spatial context to an energy outcome —
        that relationship belongs in the agent layer, not in the resource manager.
        """
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
        Route incoming damage through the action manager’s receive_damage logic.

        Living here rather than directly in Resources lets AttackAction apply
        defense mitigation (which knows the defender’s DNA) before any health
        is subtracted. Returns the result dict so the simulation can log kills.
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
        """
        Produce a snapshot of this dot for the renderer and logger.

        Returns plain data (no object references) so callers can safely
        pass the dict through queues or serialize it without needing to
        know Dot internals.
        """
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
        """Alias for get_state() — exists for call-site compatibility."""
        return self.get_state()