"""
Dot AI 2.0 - Main Entry Point
Phase 1: DNA System + Single Dot Demo
"""

import sys
from core.simulation import DotSimulation
from renderers.pygame_renderer import PygameRenderer


def main():
    """Main program entry point"""
    
    print("=" * 60)
    print("🧬 DOT AI 2.0 - PHASE 3")
    print("=" * 60)
    print("Combat + Reproduction + Death Mechanics")
    print("")
    
    # Configuration
    config = {
        'width': 1200,  # Larger world!
        'height': 800,
        'initial_dots': 5,
        'initial_food': 20,
    }
    
    # Initialize simulation (pure logic)
    print("⚙️  Initializing simulation...")
    simulation = DotSimulation(config)
    simulation.initialize()
    
    # Initialize renderer (pure visuals)
    print("🎨 Initializing renderer...")
    renderer = PygameRenderer(config['width'], config['height'])
    
    print("")
    print("✅ READY!")
    print("")
    print("CONTROLS:")
    print("  SPACE - Pause/Resume")
    print("  ESC   - Quit")
    print("")
    print("=" * 60)
    print("")
    
    # Main loop
    running = True
    while running:
        # Handle input
        event = renderer.handle_events()
        
        if event == "quit":
            running = False
        elif event == "pause":
            simulation.toggle_pause()
        
        # Update simulation (logic)
        delta_time = 1.0 / 60.0  # Fixed timestep for now
        simulation.update(delta_time)
        
        # Render (visuals)
        state = simulation.get_state()
        actual_delta = renderer.render(state)
    
    # Cleanup
    print("")
    print("=" * 60)
    print("🛑 SIMULATION ENDED")
    print(f"⏱️  Total time: {simulation.time_elapsed:.1f} seconds")
    print(f"📊 Dots created: {simulation.total_dots_created}")
    print(f"💀 Dots died: {simulation.total_dots_died}")
    print(f"🍎 Food consumed: {simulation.total_food_consumed}")
    print("=" * 60)
    
    renderer.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    main()
