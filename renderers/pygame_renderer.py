"""
Pygame Renderer - Visual Display
Clean separation: only receives state, renders visuals
"""

import pygame


class PygameRenderer:
    """
    Simple Pygame visualization with emoji support
    - Receives simulation state
    - Renders dots, food, UI
    - Handles window events
    - Returns delta time
    """
    
    def __init__(self, width=1200, height=800):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dot AI 2.0 - Phase 3")
        
        # Fonts (using system font for emoji support)
        try:
            self.font_emoji = pygame.font.SysFont('segoeuiemoji', 32)  # Windows emoji font
        except:
            self.font_emoji = pygame.font.Font(None, 32)
        
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        
        # Clock for FPS
        self.clock = pygame.time.Clock()
        
        # Colors
        self.bg_color = (18, 18, 18)  # Dark background
        self.text_color = (76, 175, 80)  # Green
        
        # Emojis
        self.dot_emoji = "🔵"  # Blue circle for dots
        self.food_emoji = "🍎"  # Apple for food
        self.starving_emoji = "😵"  # Dizzy face for starving
        self.dead_emoji = "💀"  # Skull for dead
        
        # Debug mode
        self.debug_mode = True  # Show vision cones
        
    def render(self, simulation_state):
        """
        Render current simulation state
        Returns: delta_time in seconds
        """
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw food
        self.draw_food(simulation_state['food'])
        
        # Draw dots
        self.draw_dots(simulation_state['dots'])
        
        # Draw HUD
        self.draw_hud(simulation_state)
        
        # Update display
        pygame.display.flip()
        
        # Return delta time
        return self.clock.tick(60) / 1000.0
    
    def draw_food(self, food_list):
        """Draw all food items as apples"""
        for food in food_list:
            pos = (int(food['position'][0]), int(food['position'][1]))
            
            # Render apple emoji
            emoji_surface = self.font_emoji.render(self.food_emoji, True, (255, 255, 255))
            emoji_rect = emoji_surface.get_rect(center=pos)
            self.screen.blit(emoji_surface, emoji_rect)
            
            # Draw energy amount below
            energy_text = f"{int(food['energy_value'])}"
            text_surface = self.font_small.render(energy_text, True, (150, 150, 150))
            text_rect = text_surface.get_rect(center=(pos[0], pos[1] + 20))
            self.screen.blit(text_surface, text_rect)
    
    def draw_dots(self, dot_list):
        """Draw all dots with emoji and status bars"""
        for dot in dot_list:
            pos = (int(dot['position'][0]), int(dot['position'][1]))
            
            # Draw vision cone (debug mode)
            if self.debug_mode and 'perception' in dot:
                self.draw_vision_cone(dot)
            
            # Draw movement vector (direction indicator)
            if dot['velocity'][0] != 0 or dot['velocity'][1] != 0:
                # Normalize and scale velocity for visual
                vx, vy = dot['velocity']
                length = (vx*vx + vy*vy) ** 0.5
                if length > 0:
                    scale = 30
                    end_x = pos[0] + int((vx / length) * scale)
                    end_y = pos[1] + int((vy / length) * scale)
                    pygame.draw.line(self.screen, (100, 100, 255), pos, (end_x, end_y), 2)
                    # Arrow head
                    pygame.draw.circle(self.screen, (100, 100, 255), (end_x, end_y), 3)
            
            # Choose emoji based on state
            if dot['state'] == 'dead':
                emoji = self.dead_emoji
            elif dot['state'] == 'starving':
                emoji = self.starving_emoji
            else:
                emoji = self.dot_emoji
            
            # Render emoji
            emoji_surface = self.font_emoji.render(emoji, True, (255, 255, 255))
            emoji_rect = emoji_surface.get_rect(center=pos)
            self.screen.blit(emoji_surface, emoji_rect)
            
            # Draw ID below
            id_text = f"#{dot['id']}"
            text_surface = self.font_small.render(id_text, True, (150, 150, 150))
            text_rect = text_surface.get_rect(center=(pos[0], pos[1] + 25))
            self.screen.blit(text_surface, text_rect)
            
            # Draw status bars above dot
            self.draw_dot_stats(dot, pos)
    
    def draw_vision_cone(self, dot):
        """Draw vision cone for debugging"""
        import math
        
        pos = dot['position']
        perception = dot['perception']
        velocity = dot['velocity']
        
        # Vision range circle
        vision_range = perception['vision_range']
        if vision_range > 0:
            pygame.draw.circle(self.screen, (50, 50, 100), 
                             (int(pos[0]), int(pos[1])), int(vision_range), 1)
        
        # Detection range circles
        dot_range = perception['detection_dot_range']
        food_range = perception['detection_food_range']
        
        if dot_range > 0:
            pygame.draw.circle(self.screen, (100, 50, 50), 
                             (int(pos[0]), int(pos[1])), int(dot_range), 1)
        
        if food_range > 0:
            pygame.draw.circle(self.screen, (50, 100, 50), 
                             (int(pos[0]), int(pos[1])), int(food_range), 1)
    
    def draw_dot_stats(self, dot, pos):
        """Draw energy and health bars above dot"""
        bar_width = 50
        bar_height = 5
        x = pos[0] - bar_width // 2
        y = pos[1] - 30
        
        # Energy bar (green) with label
        energy_ratio = dot['resources']['energy_ratio']
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (76, 175, 80), 
                        (x, y, int(bar_width * energy_ratio), bar_height))
        
        # Energy value text
        energy_text = f"E:{int(dot['resources']['energy'])}"
        text_surface = self.font_small.render(energy_text, True, (76, 175, 80))
        self.screen.blit(text_surface, (x + bar_width + 5, y - 3))
        
        # Health bar (red) with label
        y += 8
        health_ratio = dot['resources']['health_ratio']
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (255, 107, 107), 
                        (x, y, int(bar_width * health_ratio), bar_height))
        
        # Health value text
        health_text = f"H:{int(dot['resources']['health'])}"
        text_surface = self.font_small.render(health_text, True, (255, 107, 107))
        self.screen.blit(text_surface, (x + bar_width + 5, y - 3))
    
    def draw_hud(self, state):
        """Draw heads-up display with stats"""
        # Left panel - simulation stats
        y = 10
        texts = [
            f"Generation: {state['generation']}",
            f"Time: {state['time']:.1f}s",
            f"",
            f"Dots: {state['stats']['dot_count']}",
            f"Food: {state['stats']['food_count']}",
            f"Births: {state['stats']['total_births']}",
            f"Deaths: {state['stats']['total_died']}",
            f"Attacks: {state['stats']['total_attacks']}",
            f"Food Eaten: {state['stats']['total_food_consumed']}",
        ]
        
        for text in texts:
            surface = self.font_medium.render(text, True, self.text_color)
            self.screen.blit(surface, (10, y))
            y += 25
        
        # Legend at top right
        legend_x = self.width - 180
        legend_y = 10
        
        # Legend items (using text symbols instead of emoji for compatibility)
        legend_items = [
            ("DOT", "Dot (Alive)", (100, 100, 255)),
            ("SICK", "Starving", (255, 235, 59)),
            ("DEAD", "Dead", (150, 150, 150)),
            ("FOOD", "Food", (76, 175, 80)),
        ]
        
        surface = self.font_small.render("LEGEND:", True, (200, 200, 200))
        self.screen.blit(surface, (legend_x, legend_y))
        legend_y += 20
        
        for symbol, label, color in legend_items:
            # Draw colored circle/square as icon
            if symbol == "DOT":
                pygame.draw.circle(self.screen, color, (legend_x + 8, legend_y + 8), 6)
            elif symbol == "FOOD":
                pygame.draw.circle(self.screen, color, (legend_x + 8, legend_y + 8), 5)
            elif symbol == "SICK":
                pygame.draw.circle(self.screen, color, (legend_x + 8, legend_y + 8), 6, 2)
            else:  # DEAD
                pygame.draw.line(self.screen, color, (legend_x + 4, legend_y + 4), (legend_x + 12, legend_y + 12), 2)
                pygame.draw.line(self.screen, color, (legend_x + 12, legend_y + 4), (legend_x + 4, legend_y + 12), 2)
            
            # Label
            text_surface = self.font_small.render(label, True, (150, 150, 150))
            self.screen.blit(text_surface, (legend_x + 20, legend_y))
            legend_y += 20
        
        # Controls below legend
        legend_y += 10
        controls = [
            "CONTROLS:",
            "SPACE - Pause",
            "ESC - Quit",
        ]
        
        for text in controls:
            surface = self.font_small.render(text, True, (150, 150, 150))
            self.screen.blit(surface, (legend_x, legend_y))
            legend_y += 20
        
        # Pause indicator
        if state['paused']:
            pause_text = "PAUSED"
            surface = self.font_large.render(pause_text, True, (255, 235, 59))
            text_rect = surface.get_rect(center=(self.width // 2, 30))
            self.screen.blit(surface, text_rect)
        
        # Dot detail (if there are dots)
        if state['dots']:
            dot = state['dots'][0]  # Show first dot's details
            y = self.height - 150
            detail_texts = [
                "DOT DETAILS:",
                f"ID: {dot['id']}",
                f"Age: {dot['age']:.1f}s",
                f"State: {dot['state']}",
                f"Action: {dot['current_action']}",
                f"Energy: {dot['resources']['energy']:.0f}/{dot['resources']['max_energy']:.0f}",
                f"Health: {dot['resources']['health']:.0f}/{dot['resources']['max_health']:.0f}",
                f"Brain Capacity: {dot['brain']['capacity']:.0f}",
                f"DNA Points: {dot['dna_points_used']:.1f}",
                f"DNA Earned: {dot['brain']['earned_dna']:.1f}",
            ]
            
            for text in detail_texts:
                surface = self.font_small.render(text, True, (150, 150, 150))
                self.screen.blit(surface, (10, y))
                y += 20
    
    def handle_events(self):
        """
        Process pygame events
        Returns: event type string or None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                if event.key == pygame.K_SPACE:
                    return "pause"
        
        return None
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()
