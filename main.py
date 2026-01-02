"""
=====================================================================
🧬 DOT AI 2.0: THE ECOSYSTEM EVOLUTION SIMULATOR 🌍
=====================================================================

WELCOME TO THE ADVANCED LESSON IN ARTIFICIAL LIFE!

If you completed the original Dot AI pathfinding project, welcome back!
We've evolved from simple path-finding to a COMPLETE LIVING ECOSYSTEM
with natural selection, combat, reproduction, and emergent behavior!

=====================================================================
WHAT YOU'RE ABOUT TO WITNESS:
=====================================================================

This simulation demonstrates how EVOLUTION discovers optimal solutions
through natural selection - without us programming the "answer"!

THE EXPERIMENT:
1. We spawn 5 dots with RANDOMIZED DNA (different abilities)
2. They compete for food, fight each other, and try to survive
3. Successful dots REPRODUCE and pass on their genes
4. Failed dots DIE and become food for others
5. Over many generations, OPTIMAL STRATEGIES EMERGE naturally

KEY EDUCATIONAL CONCEPTS:

🧬 **Genetic Algorithms**
   - Each dot has DNA: a genetic code defining all abilities
   - DNA has a "budget" (100 points) forcing trade-offs
   - Sexual reproduction MIXES parent DNA to create diversity
   - Mutations add random variation (innovation!)

🎯 **Utility-Based AI**
   - Dots use "utility scores" to make decisions
   - They calculate: "How valuable is THIS action right now?"
   - Example: If hungry → seek_food utility = HIGH
   - No hardcoded rules! Behavior EMERGES from simple math

💑 **Sexual vs Asexual Reproduction**
   - Sexual: Two parents, DNA crossover, more efficient (40% energy each)
   - Asexual: One parent, cloning, less efficient (80% energy)
   - Sexual creates DIVERSITY, Asexual preserves SUCCESS

⚔️ **Resource Competition**
   - Limited food supply creates survival pressure
   - Dots can attack/kill each other for food
   - Dead dots BECOME food (30 + DNA_points energy)
   - This creates predator-prey dynamics!

📊 **Natural Selection**
   - Only successful strategies survive and reproduce
   - Failed strategies die out quickly
   - Over generations, "fitness" increases
   - No single "perfect" solution - context matters!

🔬 **Generational Evolution**
   - If ALL dots die → Generation failed
   - Simulation restarts with RANDOMIZED DNA
   - New strategies tested
   - Eventually, viable ecosystems emerge

=====================================================================
REAL-WORLD APPLICATIONS:
=====================================================================

This type of simulation teaches us how to use AI for:

🏭 ENGINEERING: Find optimal factory layouts through evolution
💊 MEDICINE: Discover ideal drug combinations via genetic algorithms
🤖 ROBOTICS: Evolve control systems for complex tasks
🎮 GAME AI: Create realistic, adaptive NPC behaviors
🧪 RESEARCH: Model population dynamics and ecosystem balance

THE CORE LESSON:
When you don't know the perfect solution, let evolution find it!
This is the foundation of machine learning and AI optimization.

=====================================================================
CONTROLS & USAGE:
=====================================================================

SPACE - Pause/Resume the simulation
ESC   - Quit

WHAT TO WATCH FOR:
- Utility debug output (why dots choose actions)
- Combat events (⚔️)
- Reproduction (💕 sexual, 🧬 asexual)
- Deaths (💀)
- Generation summaries (when all dots die)
- DNA evolution over time

EXPERIMENT IDEAS:
1. Reduce food_spawn_rate → Harsher environment
2. Change initial_dots → Observe population dynamics
3. Track which DNA profiles survive longest
4. Identify successful vs failed strategies

=====================================================================
FILE STRUCTURE:
=====================================================================

core/
  dna.py         - Genetic system (genes, crossover, inheritance)
  dot.py         - Agent AI (utility-based decision making)
  simulation.py  - World engine (update loop, evolution)
  actions.py     - Combat & reproduction mechanics
  senses.py      - Vision & perception
  brain.py       - Memory & cognition
  resources.py   - Energy & health systems

renderers/
  pygame_renderer.py - Visualization (separate from logic!)

main.py        - This file! Entry point & configuration

=====================================================================
LET THE EVOLUTION BEGIN! 🚀🧬✨
=====================================================================
"""

import sys
from datetime import datetime
from core.simulation import DotSimulation
from core.metrics_logger import MetricsLogger
from renderers.pygame_renderer import PygameRenderer


def main():
    """
    Main program entry point - Initialize and run the simulation
    
    THE SIMULATION LOOP:
    1. Initialize world (dots + food)
    2. Each frame (60 FPS):
       - Collect user input (pause/quit)
       - Update simulation (dots think, move, act)
       - Render visualization
    3. Repeat until user quits!
    """
    
    print("=" * 60)
    print("🧬 DOT AI 2.0 - THE ECOSYSTEM EVOLUTION")
    print("=" * 60)
    print("Sexual Reproduction + Combat + Natural Selection")
    print("")
    
    # ===== CONFIGURATION =====
    # Tune these parameters to change the experiment!
    config = {
        'width': 3200,           # World width (pixels) - Wider for ultra-wide monitors
        'height': 1200,          # World height (pixels) - Scaled for Phase 4
        'initial_dots': 10,      # Starting population - DOUBLED for Phase 4
        'initial_food': 40,      # Starting food count - DOUBLED for Phase 4
        # Note: More config options in DotSimulation class!
    }
    
    # Initialize metrics logger
    session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"📊 Starting logging session: {session_name}")
    logger = MetricsLogger(session_name=session_name)
    
    # Initialize simulation (pure logic)
    print("⚙️  Initializing simulation...")
    simulation = DotSimulation(config, logger=logger)
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
    # Close logger
    logger.close()
    
    print(f"📊 Dots created: {simulation.total_dots_created}")
    print(f"💀 Dots died: {simulation.total_dots_died}")
    print(f"🍎 Food consumed: {simulation.total_food_consumed}")
    print("=" * 60)
    
    renderer.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    main()
