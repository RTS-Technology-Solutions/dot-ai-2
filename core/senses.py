"""
Sense System - Vision and Detection
Handles what dots can perceive about their environment
"""

import math


class VisionSense:
    """
    Vision cone - dots can see entities within distance and FOV
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Calculate vision parameters from DNA
        self.distance = self.calculate_distance()
        self.fov = self.calculate_fov()  # Field of view in degrees
    
    def calculate_distance(self):
        """Vision distance from DNA"""
        if not self.dna.vision_distance.enabled:
            return 0
        
        base = 100  # pixels
        bonus = self.dna.vision_distance.points * 10
        return base + bonus
    
    def calculate_fov(self):
        """Field of view angle from DNA"""
        if not self.dna.vision_fov.enabled:
            return 0
        
        base = 90  # degrees
        bonus = self.dna.vision_fov.points * 6
        return min(360, base + bonus)
    
    def can_see(self, observer_pos, observer_facing, target_pos):
        """
        Check if target is visible
        observer_facing: [vx, vy] direction vector
        Returns: True if within distance and FOV
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
        Filter entities to only those visible
        entities: list of dicts with 'position' key
        Returns: list of visible entities
        """
        visible = []
        for entity in entities:
            if self.can_see(observer_pos, observer_facing, entity['position']):
                visible.append(entity)
        return visible


class DetectionSense:
    """
    Detection - sense nearby entities regardless of facing direction
    Simpler than vision, just distance-based
    """
    
    def __init__(self, dna_profile):
        self.dna = dna_profile
        
        # Different detection ranges for different entity types
        self.dot_range = self.calculate_dot_range()
        self.food_range = self.calculate_food_range()
    
    def calculate_dot_range(self):
        """Detection range for other dots"""
        if not self.dna.dot_detection.enabled:
            return 0
        
        base = 50  # pixels
        bonus = self.dna.dot_detection.points * 8
        return base + bonus
    
    def calculate_food_range(self):
        """Detection range for food"""
        if not self.dna.food_detection.enabled:
            return 0
        
        base = 80  # pixels
        bonus = self.dna.food_detection.points * 10
        return base + bonus
    
    def detect_dots(self, observer_pos, dots):
        """Get dots within detection range"""
        if self.dot_range == 0:
            return []
        
        detected = []
        for dot in dots:
            distance = self._distance(observer_pos, dot['position'])
            if distance <= self.dot_range:
                detected.append(dot)
        return detected
    
    def detect_food(self, observer_pos, food):
        """Get food within detection range"""
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
    Combines all senses to create world perception for a dot
    """
    
    def __init__(self, dna_profile):
        self.vision = VisionSense(dna_profile)
        self.detection = DetectionSense(dna_profile)
        self.dna = dna_profile
        
        # Density sensing radius
        self.density_radius = self.calculate_density_radius()
    
    def calculate_density_radius(self):
        """Calculate nearby dot density sensing radius from DNA"""
        if not self.dna.nearby_dot_density.enabled:
            return 0
        
        base = 100  # pixels
        bonus = self.dna.nearby_dot_density.points * 12  # 12px per point
        return base + bonus
    
    def perceive(self, dot_pos, dot_velocity, world_state):
        """
        Create perception of world from dot's perspective
        Returns: dict with visible/detected entities
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
        """Get debug visualization data for rendering"""
        return []  # Empty for now, can add visual debug circles later
    
    def _unique_entities(self, entities):
        """Remove duplicates based on ID"""
        seen = set()
        unique = []
        for entity in entities:
            entity_id = entity.get('id')
            if entity_id not in seen:
                seen.add(entity_id)
                unique.append(entity)
        return unique
