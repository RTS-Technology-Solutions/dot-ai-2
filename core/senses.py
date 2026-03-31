"""
Perception is isolated from Dot because vision cone math, detection radii, and
perceived-world enrichment all form their own non-trivial subsystem. The Dot calls
perceive() and gets back a plain dict; it never needs to know how that dict was built.
This boundary also makes it straightforward to add new sense types without touching
agent logic.
"""

import math
from configs import get_config


class VisionSense:
    """
    Directional perception — the dot sees what is in front of it.

    Exists because vision_distance and vision_fov genes need a concrete payoff:
    a dot that allocates points to vision should see measurably farther and wider
    than one that doesn't. The cone model makes that investment quantifiable and
    creates a spatial tradeoff (narrow but long vs wide but short) that selection
    can act on.
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Calculate vision parameters from DNA
        self.distance = self.calculate_distance()
        self.fov = self.calculate_fov()  # Field of view in degrees
    
    def calculate_distance(self):
        """
        Returns how far this dot can see.

        Scales with gene points so investing in vision_distance produces
        a measurable range advantage over dots that skip it.
        """
        if not self.dna.vision_distance.enabled:
            return 0
        
        _scfg = get_config().senses
        base = _scfg.vision_distance_base
        bonus = self.dna.vision_distance.points * _scfg.vision_distance_per_point
        return base + bonus
    
    def calculate_fov(self):
        """
        Returns the cone angle in degrees.

        A wider FOV catches peripheral threats without extending range, creating
        a different strategic tradeoff from investing in vision_distance.
        """
        if not self.dna.vision_fov.enabled:
            return 0
        
        _scfg = get_config().senses
        base = _scfg.vision_fov_base
        bonus = self.dna.vision_fov.points * _scfg.vision_fov_per_point
        return min(_scfg.vision_fov_max, base + bonus)
    
    def can_see(self, observer_pos, observer_facing, target_pos):
        """
        True if target is within distance and inside the FOV cone.

        Uses velocity as the facing direction so a moving dot automatically
        looks in the direction it’s traveling. No separate orientation state
        is needed, which keeps the Dot simpler.
        """
        if self.distance == 0 or self.fov == 0:
            return False
        
        # Distance check
        dx = target_pos[0] - observer_pos[0]
        dy = target_pos[1] - observer_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.distance or distance == 0:
            return False
        
        # FOV check
        if self.fov >= 360:
            return True  # Can see all around
        
        # Calculate angle between facing direction and target
        # Normalize facing direction
        facing_length = math.sqrt(observer_facing[0]**2 + observer_facing[1]**2)
        if facing_length == 0:
            # Not moving, assume facing right
            facing_dir = [1, 0]
        else:
            facing_dir = [observer_facing[0]/facing_length, observer_facing[1]/facing_length]
        
        # Direction to target
        target_dir = [dx/distance, dy/distance]
        
        # Dot product to get angle
        dot = facing_dir[0]*target_dir[0] + facing_dir[1]*target_dir[1]
        angle = math.acos(max(-1, min(1, dot)))  # Clamp for numerical stability
        angle_degrees = math.degrees(angle)
        
        # Check if within FOV cone
        half_fov = self.fov / 2
        return angle_degrees <= half_fov
    
    def get_visible_entities(self, observer_pos, observer_facing, entities):
        """
        Filters an entity list to those visible from this vantage point.

        Callers pass the full world entity list; this method shields them
        from the cone geometry so add_dot / add_food callers don’t need
        to know how vision is calculated.
        """
        visible = []
        for entity in entities:
            if self.can_see(observer_pos, observer_facing, entity['position']):
                visible.append(entity)
        return visible


class DetectionSense:
    """
    Omnidirectional perception — the dot senses what is nearby regardless of facing.

    A separate class from VisionSense because detection is not direction-dependent:
    a dot with food_detection gene can sense food behind it, while vision requires
    turning to face it first. This distinction creates a meaningful gene tradeoff
    the simulation can exploit through selection.
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Different detection ranges for different entity types
        self.dot_range = self.calculate_dot_range()
        self.food_range = self.calculate_food_range()
    
    def calculate_dot_range(self):
        """
        Returns omnidirectional awareness range for other dots.

        Independent of facing direction, so even a stationary dot can sense
        approaching threats from any angle — this is why the gene is worth
        investing in beyond what vision alone provides.
        """
        if not self.dna.dot_detection.enabled:
            return 0
        
        _scfg = get_config().senses
        base = _scfg.dot_detection_base
        bonus = self.dna.dot_detection.points * _scfg.dot_detection_per_point
        return base + bonus
    
    def calculate_food_range(self):
        """
        Returns food detection range — effectively smell.

        Allows food-finding without line of sight, which matters when food
        has been partially consumed and is tucked behind a cluster of other dots.
        """
        if not self.dna.food_detection.enabled:
            return 0
        
        _scfg = get_config().senses
        base = _scfg.food_detection_base
        bonus = self.dna.food_detection.points * _scfg.food_detection_per_point
        return base + bonus
    
    def detect_dots(self, observer_pos, dots):
        """Returns dots within omnidirectional range. Pre-filtered so callers receive only relevant entities."""
        if self.dot_range == 0:
            return []
        
        detected = []
        for dot in dots:
            distance = self._distance(observer_pos, dot['position'])
            if distance <= self.dot_range:
                detected.append(dot)
        return detected
    
    def detect_food(self, observer_pos, food):
        """Returns food within omnidirectional range. Pre-filtered so callers receive only relevant entities."""
        if self.food_range == 0:
            return []
        
        detected = []
        for f in food:
            distance = self._distance(observer_pos, f['position'])
            if distance <= self.food_range:
                detected.append(f)
        return detected
    
    def _distance(self, pos1, pos2):
        """Calculate distance between positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx*dx + dy*dy)


class PerceptionSystem:
    """
    Aggregates all sense channels into a single perception call.

    Exists so the Dot calls perceive() once per tick rather than managing
    VisionSense, DetectionSense, and density objects separately. This class
    also owns the union logic (merge + deduplicate vision and detection results)
    and the enrichment passes (can_reproduce flags, DNA strength) so those
    concerns don’t leak into agent logic.
    """
    
    def __init__(self, dna_profile):
        self.vision = VisionSense(dna_profile)
        self.detection = DetectionSense(dna_profile)
        self.dna = dna_profile
        
        # Density sensing radius
        self.density_radius = self.calculate_density_radius()
    
    def calculate_density_radius(self):
        """
        Returns the population density sensing radius.

        Density awareness enables a dot to detect crowding even when individual
        dots fall outside the vision cone — essential for avoiding reproductive
        attempts in already-saturated areas.
        """
        if not self.dna.nearby_dot_density.enabled:
            return 0
        
        _scfg = get_config().senses
        base = _scfg.density_radius_base
        bonus = self.dna.nearby_dot_density.points * _scfg.density_radius_per_point
        return base + bonus
    
    def perceive(self, dot_pos, dot_velocity, world_state):
        """
        Build the full world snapshot this dot sees this tick.

        Merges directional vision and omnidirectional detection into a unified
        entity list, then enriches it with can_reproduce flags and DNA strength
        when the corresponding genes are active. Returns plain dicts so the Dot
        can pass perceived_world to decide_action without creating system coupling.
        """
        # Get all entities from world
        all_dots = world_state.get('dots', [])
        all_food = world_state.get('food', [])
        
        # Vision (directional)
        visible_dots = self.vision.get_visible_entities(dot_pos, dot_velocity, all_dots)
        visible_food = self.vision.get_visible_entities(dot_pos, dot_velocity, all_food)
        
        # Detection (omnidirectional)
        detected_dots = self.detection.detect_dots(dot_pos, all_dots)
        detected_food = self.detection.detect_food(dot_pos, all_food)
        
        # Combine (union of visible and detected)
        perceived_dots = self._unique_entities(visible_dots + detected_dots)
        perceived_food = self._unique_entities(visible_food + detected_food)
        
        # Add DNA strength perception if enabled
        if self.dna.dna_strength_detection.enabled:
            for dot in perceived_dots:
                if 'dna_points_used' in dot:
                    dot['perceived_dna_strength'] = dot['dna_points_used']
        
        # Add can_reproduce flag for mate selection
        # Dot can reproduce if it has 40%+ energy and 70%+ health
        for dot in perceived_dots:
            energy_pct = dot.get('energy', 0) / max(1, dot.get('max_energy', 100))
            health_pct = dot.get('health', 0) / max(1, dot.get('max_health', 100))
            dot['can_reproduce'] = (energy_pct >= 0.4 and health_pct >= 0.7)
        
        # Calculate nearby dot density if enabled
        nearby_density = 0
        density_dots_list = []
        if self.density_radius > 0:
            for dot in all_dots:
                dx = dot['position'][0] - dot_pos[0]
                dy = dot['position'][1] - dot_pos[1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist <= self.density_radius:
                    nearby_density += 1
                    density_dots_list.append(dot)
        
        return {
            'dots': perceived_dots,
            'food': perceived_food,
            'vision_range': self.vision.distance,
            'vision_fov': self.vision.fov,
            'detection_dot_range': self.detection.dot_range,
            'detection_food_range': self.detection.food_range,
            'nearby_density': nearby_density,  # Phase 4: Density awareness
            'density_radius': self.density_radius,
            'density_dots': density_dots_list  # Full list for advanced decisions
        }
    
    def get_debug_visuals(self, dot_pos):
        """Returns circles/arcs for the renderer’s debug overlay. Stub — sense system owns the range values so visuals are generated here when needed."""
        return []  # Empty for now, can add visual debug circles later
    
    def _unique_entities(self, entities):
        """Deduplicates the merged vision+detection list so a dot visible via both channels isn’t processed twice."""
        seen = set()
        unique = []
        for entity in entities:
            entity_id = entity.get('id')
            if entity_id not in seen:
                seen.add(entity_id)
                unique.append(entity)
        return unique
