# 🌍 Dot AI 2.0: Environmental Simulation - Project Plan

## 📋 Project Overview

**Current State:** Simple pathfinding simulation with Genetic Algorithm and Q-Learning
**Target State:** Complex environmental simulation with autonomous agents, resource management, and emergent behaviors

**Vision:** Transform the dot training exercise into a full-fledged ecosystem where dots are autonomous agents with their own brains, needs, wants, and survival mechanics.

**Status:** ✅ **ALL DESIGN DECISIONS FINALIZED** - See [DESIGN_DECISIONS_FINAL.md](DESIGN_DECISIONS_FINAL.md) for complete specifications

---

## 🎯 Core Concept Shift

### From:
- Simple goal-seeking behavior
- Single objective (reach target)
- Binary success/failure

### To:
- Complex autonomous agents
- Multiple competing needs and wants
- Survival-based ecosystem with emergent behaviors
- Resource management and competition

---

## � DNA SYSTEM - Core Architecture

**Philosophy:** Each dot is defined by a DNA profile that determines what abilities it has (binary on/off), how effective those abilities are (DNA point allocation), and how it can grow over its lifetime.

### DNA Structure Overview
```
DNA Profile = {
    DNA_Points_Total: 100 (base starting points)
    DNA_Points_Available: (calculated based on eating beyond satiation)
    
    Brain: {
        memory_size: [ENABLED: bool, POINTS: int]
        sense_slots: [ENABLED: bool, POINTS: int]
        action_slots: [ENABLED: bool, POINTS: int]
    }
    
    Senses: {
        vision_distance: [ENABLED: bool, POINTS: int]
        vision_fov: [ENABLED: bool, POINTS: int]
        dot_detection: [ENABLED: bool, POINTS: int]
        food_detection: [ENABLED: bool, POINTS: int]
        power_detection: [ENABLED: bool, POINTS: int]
        food_amount_detection: [ENABLED: bool, POINTS: int]
        dna_strength_detection: [ENABLED: bool, POINTS: int]
    }
    
    Actions: {
        movement_speed: [ENABLED: bool, POINTS: int]
        movement_max_energy: [ENABLED: bool, POINTS: int]
        defend: [ENABLED: bool, POINTS: int]
        attack: [ENABLED: bool, POINTS: int]
        eat: [ENABLED: bool, POINTS: int]
        replicate: [ENABLED: bool, POINTS: int]
        revive: [ENABLED: bool, POINTS: int]
    }
}
```

### DNA Point System
- **Starting DNA Points:** Each newborn dot gets a base allocation (e.g., 100 points)
- **Point Distribution:** Must be allocated across enabled abilities
- **Trade-offs:** Limited points force strategic choices (e.g., vision distance OR field of view)
- **Growth:** Dots can earn additional DNA points by eating beyond full satiation
- **Inheritance:** DNA profile is inherited and mutated from parents

---

## 🧠 Architecture Overview

### 1. **The Brain - Central Processor**

The brain is the command center that processes all information and coordinates the dot's behavior.

#### Brain Capabilities (DNA-Controlled)

**A. Memory System**
- **DNA Switch:** `brain.memory_size.ENABLED` (binary on/off)
- **DNA Points:** `brain.memory_size.POINTS` (determines capacity)
- **Functionality:**
  - Stores recent experiences, food locations, threat areas
  - Memory slots = base_memory + (DNA_POINTS × memory_multiplier)
  - Example: 10 base slots + (20 points × 0.5) = 20 memory slots
  - Increases with age: additional slots gained per X seconds survived

**B. Sense Slots**
- **DNA Switch:** `brain.sense_slots.ENABLED`
- **DNA Points:** `brain.sense_slots.POINTS`
- **Functionality:**
  - Limits how many senses the brain can actively process
  - Starting slots = 2-3, can grow with age and DNA points
  - More slots = can monitor more senses simultaneously
  - Forces prioritization: "Do I watch for food or watch for threats?"

**C. Action Slots**
- **DNA Switch:** `brain.action_slots.ENABLED`
- **DNA Points:** `brain.action_slots.POINTS`
- **Functionality:**
  - Limits how many actions the brain can manage
  - Starting slots = 2-3 (e.g., move + eat)
  - Advanced actions (attack, defend) require available slots
  - Grows with age and DNA point investment

**D. Brain Processing**
The brain continuously processes:
1. **Age** - How long the dot has been alive (affects growth)
2. **Active Senses** - Current sensory input within available slots
3. **Available Actions** - Actions the dot can currently perform
4. **Power Level** - Current energy reserves
5. **Life Level** - Current health status
6. **Need vs Want Priority** - Which needs are most urgent
7. **Priority Order** - Dynamic ranking of actions based on needs
8. **Life Status** - Overall state (healthy, hungry, critical, etc.)

#### Brain Growth System
- **Age-Based Growth:** Every X seconds alive, gain:
  - +1 memory slot (if memory enabled)
  - Chance for +1 sense slot (if at max capacity and DNA allows)
  - Chance for +1 action slot (if at max capacity and DNA allows)
  
- **DNA Point Investment:** Eating beyond satiation grants DNA points that can:
  - Unlock new abilities (if DNA switch allows evolution)
  - Strengthen existing abilities
  - Expand brain capacity

---

### 2. **Senses - Environmental Awareness**

Senses are the dot's eyes and ears, limited by DNA and brain capacity.

#### Sense Slot System
- Dots have limited sense slots (2-5 based on brain.sense_slots)
- Must "equip" senses from available DNA-enabled options
- Can dynamically switch senses based on priorities (advanced AI)

#### Available Senses

**A. Vision Distance**
- **DNA Switch:** `senses.vision_distance.ENABLED`
- **DNA Points:** `senses.vision_distance.POINTS` (0-50)
- **Functionality:**
  - How far the dot can see (in pixels)
  - Formula: `vision_range = base_range + (DNA_POINTS × distance_multiplier)`
  - Example: 50 base + (30 points × 5) = 200 pixel range
  - **Trade-off with Vision FOV:** High distance often means lower FOV

**B. Vision Field of View (FOV)**
- **DNA Switch:** `senses.vision_fov.ENABLED`
- **DNA Points:** `senses.vision_fov.POINTS` (0-50)
- **Functionality:**
  - Angular field of view in degrees (0-360°)
  - Formula: `fov_angle = base_fov + (DNA_POINTS × fov_multiplier)`
  - Example: 90° base + (40 points × 3) = 210° FOV
  - **Trade-off with Vision Distance:** Wide FOV often means shorter range

**C. Dot Detection**
- **DNA Switch:** `senses.dot_detection.ENABLED`
- **DNA Points:** `senses.dot_detection.POINTS`
- **Functionality:**
  - Can sense other dots within vision range
  - Higher points = can sense more details (count, distance, direction)
  - If DISABLED: Dot is "blind" to other dots, cannot avoid/target them

**D. Food Detection**
- **DNA Switch:** `senses.food_detection.ENABLED`
- **DNA Points:** `senses.food_detection.POINTS`
- **Functionality:**
  - Can sense food locations within vision range
  - Higher points = more accurate food localization
  - If DISABLED: Must randomly stumble upon food, no targeted seeking

**E. Power Detection**
- **DNA Switch:** `senses.power_detection.ENABLED`
- **DNA Points:** `senses.power_detection.POINTS`
- **Functionality:**
  - Can sense the power/strength level of nearby dots
  - Higher points = more accurate power assessment
  - Critical for attack/flee decisions
  - If DISABLED: Cannot assess threats, risky behavior

**F. Food Amount Detection**
- **DNA Switch:** `senses.food_amount_detection.ENABLED`
- **DNA Points:** `senses.food_amount_detection.POINTS`
- **Functionality:**
  - Can estimate how much food is available at detected food locations
  - Higher points = more accurate food quantity estimates
  - Helps prioritize which food sources to target
  - Low priority = might target depleted food, waste energy
  - If DISABLED: All food looks the same, inefficient foraging

**G. DNA Strength Detection**
- **DNA Switch:** `senses.dna_strength_detection.ENABLED`
- **DNA Points:** `senses.dna_strength_detection.POINTS`
- **Functionality:**
  - Can assess the total DNA strength/quality of nearby dots
  - DNA Strength = Total DNA points accumulated by target dot
  - Higher points = more accurate assessment of genetic fitness
  - **Critical for multiple strategies:**
    - **Mate Selection:** Choose strong partners for replication
    - **Combat Decisions:** Attack weak dots, flee from strong ones
    - **Social Hierarchy:** Recognize dominant/successful dots
  - Assessment accuracy: `strength_estimate = actual_strength ± (error_range / DNA_POINTS)`
  - Example: 5 points might give ±20% accuracy, 30 points might give ±5% accuracy
  - **Mate Quality Control:** Can refuse replication with weak partners
  - If DISABLED: Cannot assess mate quality or threat level, poor decisions

#### Sense Priority System
- Brain ranks active senses by urgency
- Example priority when low energy:
  1. Food Detection (critical)
  2. Food Amount Detection (optimization)
  3. Dot Detection (avoid competition)
  4. Power Detection (if space available)

---

### 3. **Actions - What Dots Can Do**

Actions are behaviors that consume energy and affect the world.

#### Action Slot System
- Dots have limited action slots (2-4 based on brain.action_slots)
- Must "equip" actions from DNA-enabled options
- Some actions are mutually exclusive (can't attack and defend simultaneously)

#### Available Actions

**A. Movement**
- **DNA Switch:** `actions.movement_speed.ENABLED` & `actions.movement_max_energy.ENABLED`
- **DNA Points:** Distributed between speed and energy capacity
- **Functionality:**

  **Movement Speed:**
  - DNA Points → Velocity
  - Formula: `max_velocity = base_velocity + (DNA_POINTS × velocity_multiplier)`
  - Example: 2 base + (25 points × 0.2) = 7 max velocity
  - **Energy Cost:** Higher speed = more energy per frame
  - Formula: `energy_cost = base_cost × (1 + speed_factor)`
  
  **Movement Max Energy:**
  - DNA Points → Energy Capacity
  - Formula: `max_energy = base_energy + (DNA_POINTS × energy_multiplier)`
  - Example: 100 base + (40 points × 5) = 300 max energy
  - **Trade-off:** High capacity = slower movement OR less DNA points for speed
  
  **The Trade-off:**
  - Limited DNA points must be split between speed and capacity
  - Fast dots: High speed, low energy capacity (sprint hunters)
  - Endurance dots: Low speed, high energy capacity (marathon survivors)

**B. Defend**
- **DNA Switch:** `actions.defend.ENABLED`
- **DNA Points:** `actions.defend.POINTS`
- **Functionality:**
  - Activated when under attack or threat detected
  - Prevents or reduces health loss from attacks
  - Defense effectiveness: `damage_reduction = base_defense + (DNA_POINTS × defense_multiplier)`
  - Example: 20% base + (30 points × 1%) = 50% damage reduction
  - **Energy Cost:** High - uses 2-3x normal movement energy per frame
  - **Trade-off:** Energy-intensive, can't move as far while defending
  - If DISABLED: Dot takes full damage, cannot protect itself

**C. Attack**
- **DNA Switch:** `actions.attack.ENABLED`
- **DNA Points:** `actions.attack.POINTS`
- **Functionality:**
  - Activated when targeting another dot in proximity
  - Deals damage to target dot's health
  - Attack damage: `damage = base_damage + (DNA_POINTS × damage_multiplier)`
  - Example: 5 base + (25 points × 0.5) = 17.5 damage per attack
  - **Energy Cost:** Very High - uses 3-5x normal movement energy per attack
  - **Strategic Complexity:**
    - Only smart (high brain) dots may prioritize this
    - Long-term strategy: turn competitors into food
    - Risk vs reward: high energy cost, might fail
  - **Success Condition:** Target's health reduced to 0 → becomes food
  - If DISABLED: Dot is pacifist, cannot create food from other dots

**D. Eat**
- **DNA Switch:** `actions.eat.ENABLED` (should always be enabled for survival)
- **DNA Points:** `actions.eat.POINTS` (eating efficiency)
- **Functionality:**
  - Activated when dot is at food location
  - **NO ENERGY COST** - This is the energy recovery action!
  - Eating efficiency: `energy_gained = food_value × (base_efficiency + DNA_POINTS × efficiency_multiplier)`
  - Example: 50 food × (0.5 base + 20 points × 0.02) = 50 food × 0.9 = 45 energy gained
  - If DISABLED: Dot cannot eat, will always die (mutation death sentence)

**E. Replicate (Sexual Reproduction)**
- **DNA Switch:** `actions.replicate.ENABLED`
- **DNA Points:** `actions.replicate.POINTS` (affects offspring quality and energy cost)
- **Functionality:**
  - Activated when near another dot and both choose to replicate
  - **MUTUAL CONSENT REQUIRED:** Both dots must select replicate action
  - **Proximity Required:** Must be within replication range (e.g., 20-50 pixels)
  - **Minimum Energy Threshold:** Both dots must have ≥ minimum energy (e.g., 60% of max)
  - **Energy Cost:** High - consumes 30-50% of current energy from both parents
  - **Defense Blocks Replication:** If one dot chooses defend, replication prevented
    - Allows dots to refuse poor genetic matches
    - Mate quality control mechanism
  
  **Replication Process:**
  1. Both dots in proximity detect each other (requires dot_detection sense)
  2. Both assess partner's DNA strength (if dna_strength_detection enabled)
  3. Both decide to activate replicate action (AI decision based on priorities)
  4. Energy threshold check: both must have sufficient energy
  5. If all conditions met → create offspring
  6. Both parents lose energy (reproduction cost)
  
  **Offspring DNA Creation:**
  - **Genetic Mixing:** Offspring inherits DNA from both parents
  - **Crossover:** Each gene has 50/50 chance from parent A or parent B
  - **Point Averaging:** Some attributes averaged between parents
  - **Mutations:** Small chance of random changes (±5-15% per gene)
  - **Quality Bonus:** Higher parent DNA_POINTS → slightly better offspring base
  
  **Strategic Implications:**
  - **Long-term Strategy:** Only advanced dots with sufficient brain capacity
  - **Mate Selection:** Dots with DNA strength sense can be selective
  - **Minimum Standards:** Population can evolve mate quality thresholds
  - **Energy Investment:** Must be well-fed and successful to afford reproduction
  - **Selective Breeding:** Strong dots reproduce, weak dots filtered out
  - If DISABLED: Dot cannot reproduce sexually, relies on population respawn

  **DNA Points Effect on Replication:**
  - Higher points = lower energy cost for reproduction
  - Higher points = better genetic transfer (less mutation noise)
  - Higher points = may produce twins/multiple offspring (advanced feature)

**F. Revive (Energy Transfer / Altruism)**
- **DNA Switch:** `actions.revive.ENABLED`
- **DNA Points:** `actions.revive.POINTS` (affects transfer efficiency and cost)
- **Functionality:**
  - Activated when near a dot with 0 energy (dying/dead state)
  - Transfers energy from self to target dot
  - **Energy Transfer:** Donates portion of own energy to revive another
  - **Proximity Required:** Must be within revive range (e.g., 20-30 pixels)
  - **Minimum Energy Threshold:** Donor must have surplus energy (e.g., >50%)
  - **Energy Cost:** Donates energy but loses some to "transfer inefficiency"
  
  **Revive Process:**
  1. Detect dot with 0 energy nearby (requires dot_detection sense)
  2. Optionally assess target's DNA strength (if dna_strength_detection enabled)
  3. AI decides whether to revive or let die/attack
  4. Energy threshold check: donor must have enough to spare
  5. Transfer energy to target
  6. Target revived if energy > 0 threshold
  
  **Energy Transfer Formula:**
  ```
  transfer_efficiency = base_efficiency + (DNA_POINTS × efficiency_multiplier)
  energy_donated = donor_energy × donation_percentage
  energy_received = energy_donated × transfer_efficiency
  
  # Example: 50% donation, 70% efficiency
  # Donor has 200 energy, donates 100, loses 100
  # Recipient receives 100 × 0.7 = 70 energy
  # 30 energy "lost" to transfer inefficiency
  ```
  
  **Strategic Implications:**
  - **Altruistic Strategy:** Revive valuable genetic partners for replication
  - **Investment Strategy:** Save dying strong dots, reproduce later
  - **Cooperative Evolution:** Dots that help each other survive longer
  - **Reciprocal Altruism:** Revived dots may later help donor (emergent behavior)
  
  **Critical Decision Point:**
  When encountering a 0-energy dot, brain must choose:
  1. **Attack** → Kill for food (immediate energy gain)
  2. **Revive** → Save for potential reproduction partner (long-term investment)
  3. **Ignore** → Conserve energy, let nature take course
  
  **Revive → Replicate Strategy:**
  - Dot finds high-DNA strength dot with 0 energy
  - Revives it with energy transfer
  - Waits for target to recover
  - Attempts replication with now-revived strong partner
  - Combines strong genetics if successful
  - Long-term strategy only smart/successful dots can execute
  
  **DNA Points Effect on Revive:**
  - Higher points = better transfer efficiency (less energy lost)
  - Higher points = can transfer energy faster
  - Higher points = can revive from lower energy states
  - If DISABLED: Dot is purely selfish, cannot help others

#### Energy-Action Relationship
```
Energy Cost Per Action (per frame or per use):
- Idle/Rest: 0.1 energy/frame
- Movement: 0.5-3.0 energy/frame (based on speed DNA)
- Eating: 0 energy/frame (GAINS energy instead)
- Defend: 1.5-4.5 energy/frame (based on defense DNA)
- Attack: 3.0-10.0 energy/attack (based on attack DNA)
- Replicate: 30-50% of current energy (one-time cost, both parents)
- Revive: Variable - transfers 10-50% of energy to target (donor loses energy)
```

---

### 4. **The Eating → Growth Progression System**

This is the key to dot advancement and evolution during their lifetime.

#### Progression Stages

**Stage 1: Energy Recovery (Hungry → Satiated)**
- **Condition:** Current energy < Max energy
- **Effect:** Eating increases energy
- **Formula:** `energy += food_consumed × eating_efficiency`
- **Visual:** Dot color shifts from red → yellow → green

**Stage 2: Health Recovery (Low Health → Full Health)**
- **Condition:** Energy at max AND current health < Max health
- **Effect:** Excess food consumption heals the dot
- **Formula:** `health += (food_consumed × eating_efficiency) × health_conversion_rate`
- **Conversion Rate:** e.g., 0.5 (50% of food energy converts to health)
- **Visual:** Dot outline/glow shifts to indicate healing

**Stage 3: DNA Point Accumulation (Growth & Evolution)**
- **Condition:** Energy at max AND health at max
- **Effect:** Continued eating grants DNA points
- **Formula:** `DNA_points += (food_consumed × eating_efficiency) × DNA_conversion_rate`
- **Conversion Rate:** e.g., 0.1 (10% of food energy converts to DNA points)
- **DNA Point Uses:**
  1. Strengthen existing abilities (increase DNA_POINTS allocation)
  2. Unlock new abilities (enable DNA switches, if allowed by evolution rules)
  3. Expand brain capacity (more memory, sense slots, action slots)
  
- **Visual:** Dot sparkles or has special aura indicating growth
- **Strategic Depth:** 
  - Dots must survive long enough to reach satiation
  - Only successful, efficient dots can reach Stage 3
  - Creates natural selection: thrivers get stronger, strugglers die

#### Growth Distribution AI
When a dot earns DNA points, its brain must decide how to allocate them:
- **Reinforcement Learning Approach:** 
  - Reward allocation that led to better survival
  - Punish allocation that didn't help
  
- **Genetic Algorithm Approach:**
  - Random allocation with mutation
  - Successful allocations survive via natural selection
  
- **Hybrid Approach:**
  - Some points auto-allocated based on recent challenges
  - Example: If frequently attacked → invest in defense
  - Example: If often starving → invest in food detection or movement efficiency

---

### 5. **Natural Selection Through DNA**

#### DNA Inheritance & Mutation

**Reproduction (Genetic Algorithm):**
1. Parent's DNA profile is cloned
2. Mutations occur:
   - **Switch Flips:** Small chance (1-5%) to enable/disable abilities
   - **Point Mutations:** DNA point allocations shift by ±5-15%
   - **Total Point Mutation:** Slight variation in starting DNA points (±10)

3. Trade-off enforcement: After mutation, ensure total DNA points allocated ≤ DNA_points_total
4. If over budget, reduce random allocations proportionally

**Natural Selection Pressure:**
- Dots with poor DNA combinations die quickly
- Examples of bad DNA:
  - No food detection + low memory = can't find food
  - High attack + low energy capacity = dies while attacking
  - No defend + high aggression = killed by others
  
- Examples of good DNA (context-dependent):
  - Abundant food environment: High eating efficiency, low attack
  - Scarce food environment: High food detection, high movement efficiency
  - Aggressive environment: High defend, power detection

#### Death → Food Conversion (DNA-Based)

When a dot dies:
```python
food_created = (
    remaining_energy × 0.5 +
    remaining_health × 0.3 +
    (DNA_points_total / 100) × DNA_bonus_multiplier
)

# Example:
# Weak dot: 20 energy + 10 health + (100/100)*50 = 10 + 3 + 50 = 63 food
# Strong dot: 50 energy + 30 health + (250/100)*50 = 25 + 9 + 125 = 159 food
```

**Effect:** Killing or outlasting stronger dots yields more food, incentivizing targeting strong dots OR surviving long enough to get strong.

#### Sexual Reproduction & Mate Selection

**Reproduction Mechanics:**
1. **Mutual Consent System:**
   - Both dots must actively choose replicate action
   - Defense action blocks unwanted reproduction
   - Creates natural mate selection pressure

2. **Mate Quality Assessment:**
   - Dots with `dna_strength_detection` can evaluate potential mates
   - AI prioritizes high DNA strength partners if sense enabled
   - Creates selective breeding within population

3. **Genetic Combination:**
   ```python
   offspring_DNA = {
       'DNA_points_total': (parent_A.DNA_points + parent_B.DNA_points) / 2,
       'genes': {}
   }
   
   for gene in all_genes:
       # 50/50 chance to inherit from each parent
       if random.random() < 0.5:
           offspring_DNA['genes'][gene] = parent_A.genes[gene]
       else:
           offspring_DNA['genes'][gene] = parent_B.genes[gene]
       
       # Apply mutation
       if random.random() < MUTATION_RATE:
           offspring_DNA['genes'][gene] = mutate(offspring_DNA['genes'][gene])
   ```

4. **Advantages Over Asexual Reproduction:**
   - Combines beneficial traits from two successful parents
   - Faster adaptation through genetic recombination
   - Natural quality control through mate selection
   - Maintains genetic diversity in population

5. **Evolution of Mating Strategies:**
   - **Selective Strategy:** High DNA strength sense, refuse weak mates
   - **Opportunistic Strategy:** Low/no mate selection, reproduce often
   - **Resource-Based:** Only reproduce when well-fed and safe
   - Natural selection determines which strategy succeeds

**Population Dynamics:**
- Sexual reproduction creates in-world population growth
- Death creates population decline
- Balance through resource scarcity and energy costs
- No artificial respawning needed with replication system
- Extinct species can be re-seeded or lost permanently

#### Cooperation vs Competition - Emergent Social Evolution

**The Altruism Dilemma:**
With Attack, Defend, Replicate, and Revive actions, dots face complex social decisions:

**Competitive Strategies (Selfish):**
- **Pure Aggressor:** Attack enabled, Revive disabled
  - Kills weak dots for food
  - No energy spent on helping others
  - High short-term energy gain
  - Risk: May kill potential mates, reduce population

- **Opportunistic:** Attack and Defend enabled
  - Attacks weak, defends from strong
  - Self-preservation focused
  - Balanced energy management

**Cooperative Strategies (Altruistic):**
- **Pure Helper:** Revive enabled, Attack disabled
  - Saves dying dots, builds "allies"
  - Long-term population sustainability
  - Energy cost for helping
  - Benefit: More reproduction partners available

- **Selective Helper:** Revive with DNA strength detection
  - Only helps high-quality genetic partners
  - Invests in strong dots for later reproduction
  - Strategic altruism
  - Smart long-term strategy

**Hybrid Strategies (Context-Dependent):**
- **Intelligent Social:** All actions enabled, smart prioritization
  - Attack weak/useless dots → food
  - Revive strong/valuable dots → reproduction
  - Defend when threatened
  - Replicate with revived strong partners
  - Requires high brain capacity and DNA strength sense
  - Most complex but potentially most successful

**Evolutionary Pressures:**
1. **Abundant Resources:** Competition less important, cooperation thrives
2. **Scarce Resources:** Aggression becomes necessary, altruism costly
3. **High Population:** Competition increases, selective helping emerges
4. **Low Population:** Cooperation critical for species survival

**Emergent Behaviors:**
- **Reciprocal Altruism:** Dots that help each other survive longer together
- **Exploitation:** Selfish dots benefit from helpers without helping back
- **Vengeance/Memory:** Advanced dots may remember who attacked/helped
- **Territory/Groups:** Cooperative dots may cluster, aggressive dots isolated
- **Evolution of Morality:** Population may evolve toward optimal cooperation level

**The "Revive → Replicate" Power Play:**
```
Scenario:
1. Strong Dot A (DNA: 250) encounters dying Strong Dot B (DNA: 280, energy: 0)
2. Dot A has DNA strength detection and revive enabled
3. Decision Matrix:
   - Attack B → gain ~150 food (immediate)
   - Revive B → lose ~50 energy, gain potential mate (long-term)
4. Dot A revives Dot B (strategic investment)
5. Dot B recovers energy from nearby food
6. Dot A approaches Dot B for replication
7. Dot B assesses Dot A (strong DNA detected)
8. Both replicate → Offspring with DNA ~265 (avg of 250 + 280)
9. Offspring stronger than if Dot A reproduced with weaker partner
```

**Natural Selection Outcomes:**
- Pure aggression may dominate in scarcity → population crash
- Pure altruism may be exploited → helpers die out
- **Selective cooperation likely optimal:** Help the strong, eliminate the weak
- Creates evolutionary pressure toward **intelligent social behavior**

---

## 💡 Wants & Needs System

### Core Needs (Survival Mechanics)
1. **Energy/Power**
   - Depletes over time (metabolism)
   - Depletes faster when moving
   - Required for all actions
   - Death when energy reaches 0

2. **Health/Life**
   - Can be damaged by collisions, attacks, environmental hazards
   - May regenerate slowly when well-fed
   - Death when health reaches 0

3. **Hunger**
   - Increases over time
   - Drives food-seeking behavior
   - High hunger = faster energy depletion

### Secondary Wants (Behavior Modifiers)
1. **Safety** - Avoid threats and dangerous areas
2. **Exploration** - Discover new food sources
3. **Social** - Cooperation vs competition behaviors (future enhancement)

### Need Prioritization System
- Dynamic priority based on urgency
- Example: If energy < 20%, food-seeking overrides all else
- If health < 30%, flee/hide behavior activates

---

## 🔋 Resource System (DNA-Integrated)

### Core Resources
All dots have three primary resources that determine survival:

1. **Energy/Power**
   - Current: 0 to Max (determined by DNA)
   - Max capacity: `actions.movement_max_energy.POINTS` allocation
   - Depletes with actions (movement, attack, defend)
   - Replenished by eating
   - **Death condition:** Energy reaches 0 → rapid life drain → death

2. **Health/Life**
   - Current: 0 to Max (can be DNA-influenced in future)
   - Max capacity: Base value (e.g., 100) or DNA-enhanced
   - Decreases from attacks, collisions (optional)
   - Regenerates when eating at full energy
   - **Death condition:** Health reaches 0 → immediate death

3. **DNA Points**
   - Total accumulated: Base + earned through Stage 3 eating
   - Available for allocation: Must be distributed across abilities
   - Determines effectiveness of all abilities
   - Inherited with mutations, grows during lifetime

### Dot Attributes (Now DNA-Controlled)
All attributes are now controlled by the DNA system described above:

- **Max Power/Energy** → `actions.movement_max_energy.POINTS`
- **Max Health** → Base value or future DNA parameter
- **Metabolism Rate** → Calculated from energy costs of equipped actions
- **Movement Speed** → `actions.movement_speed.POINTS`
- **Power Efficiency** → Inverse of action energy costs
- **Eating Efficiency** → `actions.eat.POINTS`
- **Vision Radius** → `senses.vision_distance.POINTS` + `senses.vision_fov.POINTS`
- **Regeneration Rate** → Stage 2 eating health conversion rate
- **Attack Power** → `actions.attack.POINTS`
- **Defense** → `actions.defend.POINTS`

**All attributes now emergent from DNA configuration and point allocation.**

---

## 🍎 Food System (Evolved Target Points)

### Food Properties
1. **Energy Content**
   - Base energy value (e.g., 50-500)
   - Calculated based on what died at that location
   - `food_value = deceased_dot.remaining_energy + (deceased_dot.max_health * 0.5)`

2. **Depletion Mechanics**
   - Food has finite energy
   - Multiple dots can share food until depleted
   - When depleted, food disappears

3. **Food Types** (future enhancement)
   - **Corpse Food**: Created when dot dies
   - **Ambient Food**: Spawns naturally over time
   - **Plant Food**: Renewable sources that regenerate

4. **Food Spawning**
   - Natural food spawn rate (configurable)
   - Food appears at random locations
   - Maximum food cap to prevent overcrowding

### Death → Food Cycle
When a dot dies:
```
1. Calculate food value from dot's state
2. Create food entity at death location
3. Food contains energy based on:
   - Remaining energy in dot
   - Portion of dot's health
   - Portion of dot's body mass (max_power * 0.1)
```

---

## ⚔️ Death Mechanics

### Death Conditions
1. **Energy Depletion**
   - Power/energy reaches 0
   - Dot cannot move or perform actions
   - Dies after X seconds of 0 energy

2. **Health Depletion**
   - Health reaches 0 from:
     - Attacks from other dots (future)
     - Environmental hazards (future)
     - Collisions with obstacles (optional)

3. **Starvation**
   - Combined effect of high hunger + low energy
   - Accelerated death

### Death Consequences
- Body remains as food source
- Genetic material available for evolution
- Contributes to ecosystem energy cycle

---

## 🔄 Evolution & Learning

### Genetic Algorithm 2.0
1. **Fitness Calculation**
   - Lifespan (how long survived)
   - Food collected
   - Energy efficiency
   - Distance traveled
   - Goals reached (optional bonus)

2. **Heritable Traits**
   - All resource attributes (max_power, metabolism, etc.)
   - Brain structure/weights
   - Behavioral tendencies

3. **Mutation System**
   - Attribute mutations (±5-10% variance)
   - Brain mutations (neural network weights or Q-table)
   - Mutation rate adaptive to population health

### Reinforcement Learning 2.0
1. **State Space Expansion**
   - Internal state: energy, health, hunger levels
   - Environmental perception: nearby food, dots, obstacles
   - Goal distance (optional)

2. **Action Space Expansion**
   - Movement (8 directions)
   - Eat (when near food)
   - Rest (conserve energy)
   - Attack/Defend (future)

3. **Reward Structure**
   - +Large: Successfully eating food
   - +Medium: Surviving longer
   - +Small: Moving toward food when hungry
   - -Small: Energy depletion
   - -Medium: Health damage
   - -Large: Death

---

## 🎮 Simulation Environment

### World Properties
1. **Food Distribution**
   - Natural spawn points
   - Corpse-based food
   - Renewable vs finite resources

2. **Obstacles**
   - Static barriers (walls)
   - Dynamic hazards (future: moving obstacles)
   - Safe zones (future: areas with low risk)

3. **Environmental Factors** (future)
   - Day/night cycles affecting visibility
   - Weather affecting movement/energy
   - Terrain types with different properties

### Population Dynamics
1. **Population Cap**
   - Maximum dots allowed
   - Natural population control via resource scarcity

2. **Reproduction** (future enhancement)
   - Sexual reproduction: combine traits from 2 parents
   - Energy cost for reproduction
   - Population growth when resources abundant

3. **Extinction Prevention**
   - Minimum population auto-spawn
   - Preserve genetic diversity

---

## 📊 Metrics & Visualization

### Performance Tracking
1. **Individual Dot Stats**
   - Current energy, health, hunger
   - Age/lifespan
   - Food consumed
   - Distance traveled

2. **Population Stats**
   - Total population
   - Average lifespan
   - Average fitness
   - Genetic diversity metrics

3. **Ecosystem Stats**
   - Total food available
   - Food consumption rate
   - Death rate
   - Birth rate (if reproduction implemented)

### Visual Enhancements
1. **Dot Appearance**
   - Size based on max_power
   - Color based on energy level (red = low, green = high)
   - Brightness based on health

2. **HUD Elements**
   - Population graph over time
   - Resource availability chart
   - Selected dot detailed stats panel

3. **Food Visualization**
   - Size based on energy content
   - Different colors for food types
   - Depletion animation

---

## 🏗️ Implementation Phases

### Phase 1: Core DNA & Resource System ✅ (Start Here)
- [ ] Design DNA data structure (switches + points)
- [ ] Implement DNA profile class
- [ ] Implement energy/power system (with DNA-based max capacity)
- [ ] Implement health system
- [ ] Implement hunger system (links to eating behavior)
- [ ] Add resource depletion based on actions
- [ ] Add death from energy/health depletion
- [ ] Implement DNA point budget validation
- [ ] Create DNA visualization (show enabled abilities)

### Phase 2: Brain & Sense System
- [ ] Implement Brain class with slot system
- [ ] Add memory system (DNA-controlled capacity)
- [ ] Implement sense slots (limited by DNA)
- [ ] Implement action slots (limited by DNA)
- [ ] Create Vision Distance sense
- [ ] Create Vision FOV sense
- [ ] Create Dot Detection sense
- [ ] Create Food Detection sense
- [ ] Create Power Detection sense
- [ ] Create Food Amount Detection sense
- [ ] Implement sense priority system

### Phase 3: Action System
- [ ] Implement action slot management
- [ ] Create Movement action (speed + energy capacity trade-off)
- [ ] Create Eat action (Stage 1-3 progression)
- [ ] Create Defend action
- [ ] Create Attack action
- [ ] Create Replicate action (mutual consent system)
- [ ] Create Revive action (energy transfer system)
- [ ] Implement energy costs for each action
- [ ] Implement action prioritization AI (attack vs revive decisions)

### Phase 4: Food System & Environment
- [ ] Convert goal points to food entities
- [ ] Implement eating mechanics (Stages 1-3)
- [ ] Add food depletion
- [ ] Implement death → food conversion (DNA-based)
- [ ] Add natural food spawning
- [ ] Balance food scarcity/abundance

### Phase 5: Growth & Evolution
- [ ] Implement age-based brain growth
- [ ] Implement Stage 3 eating → DNA point accumulation
- [ ] Create DNA point allocation AI
- [ ] Implement DNA inheritance with mutations (asexual)
- [ ] Implement sexual reproduction system (replicate action)
- [ ] Create genetic crossover algorithm (combine parent DNA)
- [ ] Implement mate selection AI (DNA strength assessment)
- [ ] Implement cooperation vs competition AI (attack vs revive decisions)
- [ ] Add mutation system (switch flips + point variations)
- [ ] Balance natural selection pressures
- [ ] Test population dynamics with sexual reproduction
- [ ] Test emergent social behaviors (cooperation, exploitation)

### Phase 6: Polish & Balance
- [ ] UI/UX improvements (DNA display, resource bars)
- [ ] Statistics dashboard (population genetics)
- [ ] Save/load ecosystem state (with DNA profiles)
- [ ] Extensive parameter tuning
- [ ] Performance optimization (spatial partitioning)

### Phase 7: Advanced Features
- [ ] Combat system refinement (attack/defend balance)
- [ ] Reproduction system (sexual selection)
- [ ] Environmental factors (day/night, terrain)
- [ ] Multiple species/subspecies emergence
- [ ] Predator-prey dynamics
- [ ] Social behaviors (flocking, cooperation)

---

## 🔧 Technical Considerations

### Performance Optimization
1. **Spatial Partitioning**
   - Quad-tree or grid for efficient neighbor searches
   - Critical when many dots check for nearby food

2. **Update Batching**
   - Update dots in batches
   - Limit perception calculations per frame

3. **Efficient Rendering**
   - Only render visible entities
   - Use sprite batching

### Code Architecture
1. **Entity Component System** (recommended refactor)
   - Separate data (components) from behavior (systems)
   - Better for complex simulations

2. **Component Classes**
   - `Brain` component
   - `Resources` component (energy, health, hunger)
   - `Attributes` component (max_power, metabolism, etc.)
   - `Perception` component
   - `Physics` component

3. **System Classes**
   - `MovementSystem`
   - `EatingSystem`
   - `EvolutionSystem`
   - `DeathSystem`
   - `FoodSpawnSystem`

### Configuration
- Move all tunable parameters to external config file (JSON/YAML)
- Allow runtime parameter adjustment
- Save configuration with simulation state

---

## 🎯 Success Criteria

### Minimum Viable Ecosystem (MVE)
1. Dots survive by finding and eating food
2. Dots die from energy depletion
3. Dead dots become food
4. Population self-sustains with food spawning
5. Evolution produces better-adapted dots over time

### Advanced Success
1. Emergent behaviors (flocking, territory, migration)
2. Stable ecosystem with balanced population
3. Visible adaptation to environmental changes
4. Diverse strategies among dot population

---

## ✅ FINALIZED DESIGN DECISIONS

**Status:** All critical decisions answered and locked in for implementation.
**Date Finalized:** January 1, 2026

### Project Philosophy & Approach

1. **DNA Point Economy**
   - Starting DNA points per dot? (Suggested: 100)
**✅ ANSWER:** No prescriptive eating logic, fully emergent from DNA priorities

**System Design:**
```python
# Brain receives state information each tick
state = {
    'energy': current_energy,
    'health': current_health,
    'food_nearby': nearby_food_locations,
    'currently_eating': bool
}

# AI calculates action utilities based on DNA
utilities = {
    'continue_eating': food_seeking_dna * hunger_level,
    'move_to_food': food_detection_dna * food_nearby,
    'attack_dot': attack_dna * dot_nearby * aggression,
    'move_explore': movement_dna * exploration_drive
}

# Choose highest utility action
action = max(utilities, key=utilities.get)
```

**No Hard-Coded Rules:**
- Dot doesn't "know" when to stop eating
- High food DNA → eats longer, seeks food more
- High attack DNA → prioritizes hunting over eating
- High movement DNA → explores more, eats less
- Behavior emerges from DNA priority distribution

**Food → Energy Conversion (SIMPLE):**
```python
# Dead dot becomes food
dead_dot_food_value = dot.dna_points_total  # 1 DNA point = 1 food point

# Eating converts food to energy/health/DNA
if eating and food_available:
    if energy < max_energy:
        energy += 1  # Stage 1: Fill energy (1:1)
    elif health < max_health:
        health += 1  # Stage 2: Heal (1:1)
    elif brain_capacity > dna_points:
        dna_points += 1  # Stage 3: Grow (1:1)
    
    food_at_location -= 1  # Deplete food
```

**Simple 1:1 Ratios:**
- 1 food point = 1 energy point
- 1 food point = 1 health point
- 1 food point = 1 DNA point
- Dead dot with 200 DNA = 200 food points available

---

### 11. Replication Energy Costs

**✅ ANSWER:** Percentage-based with no death risk

**Sexual Reproduction:**
```python
ENERGY_COST_SEXUAL = 0.40  # 40% each parent
MIN_ENERGY_THRESHOLD = 0.40  # Must have ≥40% to attempt

# Parent energy calculation
parent_A_donation = parent_A.current_energy * 0.40
parent_B_donation = parent_B.current_energy * 0.40

parent_A.energy -= parent_A_donation
parent_B.energy -= parent_B_donation

# Offspring energy (based on parent health/energy)
offspring_energy = (parent_A_donation + parent_B_donation) * parent_health_factor
# parent_health_factor: 0.8-1.0 based on parent health
```

**Asexual Reproduction:**
```python
ENERGY_COST_ASEXUAL = 0.80  # 80% single parent
MIN_ENERGY_THRESHOLD = 0.80  # Must have ≥80% to attempt

parent_donation = parent.current_energy * 0.80
parent.energy -= parent_donation

offspring_energy = parent_donation * parent_health_factor
```

**Offspring Quality:**
- Low parent energy → weaker offspring (less starting energy)
- Low parent health → offspring may have reduced max health
- High parent DNA → offspring inherits strong genetics

**No Death Risk:** Percentage-based ensures parent survives with ≥20% energy

---

### 12. Revive Mechanics - INSTANT ENERGY TRANSFER

**✅ ANSWER:** One-tick instant transfer

**Revive Action:**
```python
def revive_dot(donor, recipient):
    # Requirements
    if not donor.dna.revive.enabled:
        return False
    if recipient.energy > 0:  # Already alive
        return False
    if donor.energy < donor.max_energy * 0.50:  # Need 50% energy
        return False
    if distance(donor, recipient) > REVIVE_RANGE:  # Must be close
        return False
    
    # Instant transfer
    energy_to_donate = min(
        donor.current_energy * 0.50,  # Max 50% of donor energy
        recipient.max_energy * 0.25    # Target: 25% of recipient max
    )
    
    donor.energy -= energy_to_donate
    recipient.energy = energy_to_donate
    
    # Reward donor
    donor.dna_points += 1  # Cooperation reward
    
    # Log event
    log(f"Dot {donor.id} revived Dot {recipient.id}")
    
    return True
```

**Parameters:**
- `REVIVE_RANGE`: 30 pixels
- `DONOR_COST`: 50% of current energy (max)
- `RECIPIENT_RECOVERY`: 25% of max energy
- `COOPERATION_REWARD`: +1 DNA point

**No Interruption:** Single-tick action, instant completion

---

### 13. Social Memory & Interaction System

**✅ ANSWER:** Age-scaled memory with new Social Sense feature

**Memory Capacity:**
```python
memory_slots = base_memory + (age_in_seconds * memory_growth_rate)

# Example:
# Age 0s:  10 memory slots (recent events only)
# Age 30s: 25 memory slots
# Age 60s: 40 memory slots (extensive history)
```

**Social Sense (NEW DNA ABILITY):**
```python
social_sense = {
    'enabled': bool,  # DNA switch
    'points': int,    # Effectiveness level
    'functions': [
        'compare_dna_profiles',
        'assess_threat_level',
        'remember_interactions',
        'build_relationship_memory'
    ]
}
```

**Social Sense Capabilities:**
1. **DNA Profile Comparison:**
   ```python
   def compare_profiles(self_dna, other_dna):
       # Count matching enabled abilities
       similarity = count_matching_switches(self_dna, other_dna)
       
       # Compare strength
       strength_diff = other_dna.total_points - self_dna.total_points
       
       # Analyze threat (attack DNA present?)
       has_attack = other_dna.attack.enabled
       has_defend = other_dna.defend.enabled
       
       return {
           'similarity': similarity,
           'stronger': strength_diff > 0,
           'aggressive': has_attack and not has_defend,
           'defensive': has_defend,
           'passive': not has_attack and not has_defend
       }
   ```

2. **Interaction Memory:**
   - Remember last N dots encountered (N = memory slots / 2)
   - Remember outcomes: attacked, helped, mated, ignored
   - Use history to predict future behavior

3. **Threat Assessment:**
   - Compare attack DNA: `other.attack > self.defend` → threat
   - Compare speed: `other.speed > self.speed` → can't escape
   - Compare health: `other.health > self.health` → vulnerable
   - **No prescription:** AI receives data, decides action

**Emergent Personality Recognition:**
- High attack DNA + no defend = "Aggressive"
- High defend + no attack = "Defensive"
- No attack + no defend = "Passive"
- High revive = "Helpful"
- High replicate + DNA sense = "Selective breeder"

**Complexity Note:** May require dedicated prototyping phase before full integration

---

### 14. Cooperation Incentive & Reward System

**✅ ANSWER:** Multi-level reward structure

**Dot-Level Rewards (Fitness Function):**
```python
fitness = (
    age_survived * AGE_WEIGHT +              # Primary: survival
    dna_points_total * DNA_WEIGHT +          # Secondary: strength
    successful_reproductions * REPRO_WEIGHT + # Legacy
    cooperation_actions * COOP_WEIGHT        # Social behavior
)

AGE_WEIGHT = 10      # Heavy emphasis on survival
DNA_WEIGHT = 5       # Moderate emphasis on growth
REPRO_WEIGHT = 20    # High value on passing genes
COOP_WEIGHT = 2      # Small boost for cooperation
```

**Cooperation Rewards:**
- Successful revive → +1 DNA point (immediate)
- Successful reproduction → +10 fitness points
- Long life → exponential fitness increase

**Population-Level Goals:**
```python
population_fitness = (
    average_dna_points +
    average_age +
    population_stability +
    genetic_diversity
)
```

**Reward Triggers:**
- Age increase → fitness +
- DNA points accumulate → fitness +
- Max energy/health increase → fitness +
- Population avg DNA increase → population fitness +
- Population avg health >50% → stable bonus

**Penalty Triggers:**
- Health decrease from actions → fitness -
- Zero food scenarios → population fitness -
- High dot:food ratio → starvation penalty
- Population crash without DNA improvement → severe penalty

**Stagnation Detection:**
- 10 minutes with no population change (±std dev) = stagnation
- Trigger: increase mutation rate OR increase food spawning

---

### 15. AI System Architecture

**✅ ANSWER:** Utility-based AI → Hybrid learning system

**Phase 1-3: Utility-Based AI**
```python
class DotAI:
    def calculate_utilities(self, state, dna):
        utilities = {}
        
        # Each action gets utility score
        utilities['eat'] = (
            dna.eat.points *
            (1 - state.energy / state.max_energy) *  # Hunger
            state.food_nearby_count
        )
        
        utilities['attack'] = (
            dna.attack.points *
            state.weak_dots_nearby *
            (state.energy / state.max_energy)  # Only if energized
        )
        
        utilities['replicate'] = (
            dna.replicate.points *
            state.strong_mates_nearby *
            (state.energy > 0.40)  # Energy threshold
        )
        
        utilities['move_to_food'] = (
            dna.movement_speed.points *
            dna.food_detection.points *
            (1 - state.energy / state.max_energy)
        )
        
        return utilities
    
    def decide_action(self, utilities):
        # Choose highest utility
        return max(utilities, key=utilities.get)
```

**Phase 4+: Hybrid Learning Layer**
- Utility weights adjusted by reinforcement learning
- Successful action sequences reinforced
- Failed strategies penalized
- Still interpretable and debuggable

**Architecture Principles:**
- High cohesion: related functions grouped
- Low coupling: easy to swap AI systems
- Modular: can test different AI approaches
- Observable: log all decisions for analysis

---

### 16. Sense Management

**✅ ANSWER:** Static loadout (equipped at birth)

**Implementation:**
- Senses enabled based on DNA at birth
- No dynamic switching during lifetime
- Brain processes all enabled senses simultaneously (within slot limits)
- Generational adaptation only
- Simpler implementation, clearer emergent specialization

---

### 17. Visualization Strategy

**✅ ANSWER:** Clean default + toggleable debug layers

**Default View:**
```python
# Dot rendering
color = energy_to_color(dot.energy, dot.max_energy)  # Red→Yellow→Green
size = scale_by_dna(dot.dna_points, min=2, max=8)    # Bigger = stronger

# Minimal info
draw_circle(dot.pos, size, color)
```

**Debug Layers (Keyboard Toggles):**
- `V` key: Show vision cones/ranges
- `D` key: Show DNA profile overlay
- `M` key: Show memory/recent decisions
- `S` key: Show social relationships (lines between dots)
- `Click` dot: Select for detailed stats panel

**Selected Dot Panel:**
```
╔═══ Dot #42 ════════════╗
║ Age: 45s              ║
║ Energy: 85/150 ████░  ║
║ Health: 92/100 █████░ ║
║ DNA Points: 165       ║
║                       ║
║ Active Abilities:     ║
║ ✓ Vision Distance     ║
║ ✓ Food Detection      ║
║ ✓ Attack              ║
║ ✓ Replicate           ║
║                       ║
║ Recent Actions:       ║
║ • Attacked Dot #37    ║
║ • Ate food (+50 E)    ║
║ • Mated with Dot #29  ║
╚═══════════════════════╝
```

---

### 18. Controls & Features

**✅ ANSWER:** Essential controls only

**Must-Have:**
- Spacebar: Pause/Play
- 1-5 keys: Speed control (0.5x, 1x, 2x, 5x, 10x)
- S key: Manual save
- Auto-save on pause/exit
- ESC: Exit (with auto-save)

**Nice-to-Have:**
- E key: Export current population DNA profiles (JSON)
- L key: Export evolution statistics (CSV)
- R key: Reset simulation

**Not Needed:**
- Rewind/replay (too complex for v1.0)

---

### 19. Performance Targets

**✅ ANSWER:** Scale from 10 to 5000 dots @ 60 FPS

**Targets:**
- **MVP:** 10 dots @ 60 FPS (testing)
- **Target:** 100 dots @ 60 FPS (normal gameplay)
- **Stress Test:** 5000 dots @ 60 FPS (if possible)

**Platform:**
- High-end development machine (RTX 4070 Ti)
- CUDA available for future neural network training
- Can leverage GPU for parallel computation

**Optimization Strategy:**
1. Spatial partitioning (quad-tree) for dot detection
2. Only update visible dots (culling)
3. Batch rendering
4. Profile and optimize hotspots
5. Consider GPU acceleration for AI calculations if needed

---

### 20. Data Persistence & Logging

**✅ ANSWER:** Comprehensive logging for debugging and analysis

**Critical Logging (JSON format):**
```json
{
  "simulation_state": {
    "timestamp": "2026-01-01T12:00:00",
    "generation": 42,
    "dots": [
      {
        "id": 1,
        "age": 45,
        "energy": 85,
        "health": 92,
        "dna_points": 165,
        "dna_profile": {...},
        "position": [400, 300],
        "state": "eating"
      }
    ],
    "food": [...],
    "population_stats": {
      "avg_dna": 145.5,
      "avg_age": 32.1,
      "avg_health": 78.3
    }
  }
}
```

**Genetic History (CSV):**
```csv
generation,best_dna,avg_dna,population,avg_age,fitness
1,120,95,100,15.2,450
2,135,102,98,18.7,520
3,142,108,102,21.3,580
```

**Event Logging:**
```python
log.info(f"Gen {gen}: Dot {id} unlocked ability: {ability}")
log.warning(f"⚠️ Low population: {count} dots (threshold: {min})")
log.debug(f"Dot {id} decision: {action} (utility: {score})")
```

**Auto-Save:**
- Every 60 seconds (1 generation)
- On pause
- On exit
- Before auto-seeding

---

### 21. Success Metrics & Validation

**✅ ANSWER:** Defined KPIs for ecosystem health

**Survival Metrics:**
- **Minimum Runtime:** 10 minutes without extinction
- **Average Health:** >50% population
- **Population Growth:** Positive trend over 10 minutes
- **Food Stability:** Dot:food ratio between 0.2 and 5.0

**Evolution Metrics:**
- **DNA Growth:** Max DNA points increasing per generation
- **Fitness Growth:** Average fitness increasing
- **Diversity:** ≥3 distinct strategies visible
- **Lifespan:** Average age increasing

**Reward Triggers (Positive):**
- Age increase
- DNA point accumulation
- Max energy/health increase
- Population health increase
- Population age increase
- Successful cooperation events

**Penalty Triggers (Negative):**
- Zero food events
- Dot:food ratio imbalance
- Actions causing health decrease
- Population crash (without DNA improvement)
- Extended stagnation (10 min no change)

**Failure Modes:**
- Population extinction <10 minutes
- Average health <30% for 5+ minutes
- Zero evolution (no DNA improvement over 20 generations)
- Runaway growth (dots become unkillable)

---

### 22. MVP Scope

**✅ ANSWER:** Agreed core features + demo capability

**Minimum Viable Product (v1.0):**
1. ✅ DNA system (brain, senses, actions with switches + points)
2. ✅ Movement action (DNA-controlled speed)
3. ✅ Eating action (3-stage: energy → health → DNA growth)
4. ✅ Energy depletion + starvation + death mechanics
5. ✅ Food system:
   - Initial clustered spawning
   - Death → food conversion
   - Natural food spawning
6. ✅ Reproduction:
   - Asexual (80% energy cost)
   - Sexual (40% energy, mutual consent)
7. ✅ Evolution:
   - DNA inheritance with mutations
   - Age-gated brain growth
   - Natural selection
8. ✅ Visualization:
   - Color-coded dots (energy level)
   - Size-scaled dots (DNA strength)
   - Basic stats display
9. ✅ **Demo:** Watch 1-2 dots perform actions, debug decisions

**Phase 1 Deliverable:**
- Single dot can move, eat, gain energy, grow DNA
- Observable decision-making
- Logging system functional

---

### 23. Development Phases - UPDATED

**Phase Execution Strategy:**
- ✅ Thin vertical slices (working end-to-end quickly)
- ✅ Incremental complexity (simple → advanced)
- ✅ Test each phase before proceeding
- ✅ Modular, future-proof architecture

**Prioritization:**
- **Phase 1-3:** CRITICAL (DNA, senses, actions)
- **Phase 4:** CRITICAL (food ecosystem)
- **Phase 5:** HIGH (evolution)
- **Phase 6:** MEDIUM (polish)
- **Phase 7:** LOW (advanced features for v2.0)

---

### 24. Timeline & Commitment

**✅ ANSWER:** Living project with iterative development

**Development Style:**
- Rapid prototyping → test → refine → integrate
- Clean architecture from day one (but not over-engineered)
- Continuous iteration and experimentation
- Long-term learning journey

**Milestones:**
- **Week 1-2:** Phase 1 (DNA + Core Resources)
- **Week 3-4:** Phase 2-3 (Senses + Actions)
- **Week 5-6:** Phase 4 (Food Ecosystem)
- **Week 7-8:** Phase 5 (Evolution + Reproduction)
- **Week 9+:** Phase 6-7 (Polish + Advanced Features)

**Success Definition:** Working ecosystem that demonstrates emergent complexity and visible evolution

---

## 📝 REMAINING OPEN QUESTIONS (For Future Refinement)

**These are minor tuning parameters to be determined during testing:**

1. **Exact Numerical Values:**
   - Brain growth rate: 1.0 or 2.0 points/second?
   - Ability unlock chance: 0.01 (1%) or 0.005 (0.5%)?
   - Food spawn rate: 1 per 30s or 1 per 60s?
   - Attack base damage: 5, 10, or 15?
   - Defend damage reduction formula coefficients?

2. **Population Balance:**
   - Optimal starting population: 20? 50? 100?
   - Min stability threshold: 10 dots or 15?
   - Food cluster count: 5 or 10?
   - Items per cluster: 10 or 20?

3. **Social Sense Complexity:**
   - How detailed should DNA profile comparison be?
   - Should dots track relationship "scores"?
   - Memory persistence: short-term only or long-term?

4. **Advanced Features (Post-MVP):**
   - Territory/group mechanics?
   - Reputation system?
   - Multi-species evolution?
   - Environmental hazards?

**Approach:** Start with reasonable defaults, tune based on observed behavior during testing.

3. **Sense Ranges & Effectiveness**
   - Maximum vision distance possible? (e.g., 500 pixels)
   - DNA point to range conversion rate? (e.g., 1 point = 5 pixels)
   - Should sense range cost energy to maintain? (passive energy drain)
   - How accurate should food amount detection be? (exact value or estimate range?)

4. **Brain Slot System**
   - Starting sense slots? (Suggested: 2-3)
   - Starting action slots? (Suggested: 2-3)
   - Maximum slots possible? (Suggested: 8-10 each)
   - Age-based slot gain rate? (e.g., +1 slot every 100 seconds)

5. **Attack/Defend Mechanics**
   - Should attack success be guaranteed or probabilistic?
   - Can dots attack while moving or must they stop?
   - Defense: complete immunity or damage reduction?
   - Attack range? (melee only or can be DNA-extended?)

6. **Food System Balance**
   - Natural food spawn rate? (e.g., 1 food per 10 seconds)
   - Food energy content range? (50-500 per food item)
   - Should food deplete gradually or instantly when eaten?
   - Maximum concurrent food items? (10? 20? 50?)

7. **Evolution & Mutation**
   - Switch flip probability? (Suggested: 1-5% per gene)
   - Point mutation range? (Suggested: ±10-15%)
   - Should evolution allow enabling currently disabled abilities?
   - Mutation rate: fixed or adaptive to population health?

8. **Growth & Aging**
   - Should there be a maximum age/lifespan?
   - Do older dots have any disadvantages? (slower movement?)
   - Can dots "level down" or lose abilities?
   - Should DNA points be permanent or can they decay?

9. **AI Brain Architecture**
   - Use existing Q-Learning and adapt it to DNA system?
   - Switch to neural networks for more complex decisions?
   - Hybrid: simple rule-based + learning system?
   - How does AI decide DNA point allocation when earned?

10. **Reproduction Balance**
    - Minimum energy threshold for replication? (60%? 80%?)
    - Energy cost for parents? (30%? 50%? Each or total?)
    - Cooldown period between reproductions?
    - Should reproduction create immediate offspring or "egg" with gestation?
    - Can dots die during reproduction if attacked?
    - Maximum offspring per parent lifetime?

11. **Mate Selection AI**
    - What DNA strength differential triggers mate rejection?
    - Should dots prefer similar strength or stronger mates?
    - Can dots learn better mate selection strategies?
    - Should there be mate preference beyond DNA strength?

12. **Revive/Cooperation Mechanics**
    - Energy transfer efficiency? (50%? 70%? 90%?)
    - Minimum donor energy to revive? (50%? 60%?)
    - How much energy to donate per revive? (Fixed or variable?)
    - Can revive be rejected by recipient?
    - Should there be a "memory" of who helped whom?
    - Cooldown between revive actions?
    - Can dots revive themselves if they find food at 0 energy?

13. **Social Evolution Balance**
    - Should pure aggression be viable long-term?
    - Should pure altruism be sustainable?
    - What's the optimal cooperation/competition ratio?
    - Should helping behavior be rewarded in fitness?
    - Can exploitation (taking help, not giving) thrive?

14. **Visual Feedback**
    - How to show DNA-enabled abilities? (icon system?)
    - How to display resource bars without clutter?
    - Show vision cones/ranges? (debug mode?)
    - DNA point accumulation visual effect?

### Balance Philosophy Questions

1. **Should we balance for:**
   - Stable long-term ecosystem with steady population?
   - Cyclical boom-bust population dynamics?
   - Gradual evolution toward super-dots?
   - Diverse strategies (specialists vs generalists)?

2. **Food scarcity strategy:**
   - Abundant food = focus on combat/competition evolution
   - Scarce food = focus on efficiency/sensing evolution
   - Dynamic scarcity based on population?

3. **Aggression vs Cooperation:**
   - Should aggressive (attack-enabled) dots dominate?
   - Can cooperative (revive-enabled) dots create stable communities?
   - Should selective cooperation (help strong, kill weak) be optimal?
   - Balance to allow multiple social strategies?
   - Can pure altruism survive or will it be exploited?
   - Should memory/reputation systems emerge?

---

## 🚀 Getting Started

**Immediate Next Steps:**
1. ✅ Review and refine the DNA system architecture
2. Answer critical design decisions (see Open Questions section)
3. Define initial default DNA values and balance parameters
4. Create DNA Profile class structure
5. Create new development branch: `feature/dna-system-2.0`
6. Start Phase 1 implementation

**Questions to Answer Before Coding:**
1. **DNA Economy:** Starting points (100?), earning rate, maximum cap?
2. **Starting DNA Configuration:** What's the "default" dot DNA profile?
3. **Sense/Action Slot Defaults:** How many slots do dots start with?
4. **Energy Cost Balance:** What are the base energy costs for each action?
5. **Brain Architecture:** Q-Learning adaptation or neural network?
6. **Food Balance:** Spawn rate, energy content, depletion mechanics?
7. **Attack/Defend Mechanics:** Damage formulas, energy costs, success rates?

**Finalized Starting Configuration:**
```python
DEFAULT_DNA_CONFIG = {
    'DNA_points_total': 100,  # Base starting budget
    'DNA_points_max': None,   # Unlimited, age-gated by brain capacity
    
    'brain': {
        'base_capacity': 100,  # Starting brain size
        'growth_rate': 1.5,    # Points per second of life
        'memory_size': {'enabled': True, 'points': 10},      # ~15 memory slots
        'sense_slots': {'enabled': True, 'points': 12},      # ~3 sense slots
        'action_slots': {'enabled': True, 'points': 8},      # ~3 action slots
    },
    
    'senses': {
        'vision_distance': {'enabled': True, 'points': 15},  # ~125 pixel range
        'vision_fov': {'enabled': True, 'points': 15},       # ~135° FOV
        'dot_detection': {'enabled': True, 'points': 8},     # Basic awareness
        'food_detection': {'enabled': True, 'points': 12},   # Primary survival sense
        'power_detection': {'enabled': False, 'points': 0},  # Advanced (evolve)
        'food_amount_detection': {'enabled': False, 'points': 0},  # Advanced
        'dna_strength_detection': {'enabled': False, 'points': 0}, # Advanced
        'social_sense': {'enabled': False, 'points': 0},     # Advanced
    },
    
    'actions': {
        'movement_speed': {'enabled': True, 'points': 8},    # Moderate speed
        'movement_max_energy': {'enabled': True, 'points': 12}, # ~160 max energy
        'defend': {'enabled': False, 'points': 0},           # Evolve to unlock
        'attack': {'enabled': False, 'points': 0},           # Evolve to unlock
        'eat': {'enabled': True, 'points': 0},               # Always enabled, 0 cost
        'replicate': {'enabled': False, 'points': 0},        # Evolve to unlock
        'revive': {'enabled': False, 'points': 0},           # Evolve to unlock
    },
    
    'personality': {
        'mate_selectivity': 1.0,  # Random 0.5-2.0 at birth
        'aggression': 0.5,        # Random 0.0-1.0 at birth
        'exploration': 0.5,       # Random 0.0-1.0 at birth
    }
}

# Total points allocated: 10+12+8+15+15+8+12+8+12 = 100 ✓
# Perfect budget fit!

# Evolution unlocks: power_detection, food_amount, dna_strength, social_sense,
#                    defend, attack, replicate, revive
```

**Key Configuration Parameters:**
```python
# Simulation timing
BASE_LIFESPAN = 60  # seconds
LIFESPAN_SCALING = 0.1  # seconds per DNA point above 150
TARGET_GENERATION_TIME = 60  # seconds

# Energy & Resources
ENERGY_CONVERSION_RATE = 1.0  # 1 food point = 1 energy point
HEALTH_CONVERSION_RATE = 1.0  # 1 food point = 1 health point
DNA_CONVERSION_RATE = 1.0     # 1 food point = 1 DNA point (Stage 3)

# Food system
INITIAL_FOOD_CLUSTERS = 6
FOOD_PER_CLUSTER = 10
FOOD_ENERGY_RANGE = (50, 200)
NATURAL_SPAWN_RATE = 1  # food items per 30 seconds

# Population
STARTING_POPULATION = 50
MIN_POPULATION_THRESHOLD = 10
MIN_FOOD_THRESHOLD = 20

# Death & Starvation
STARVATION_SPEED_MULTIPLIER = 0.10  # 10% normal speed
STARVATION_HEALTH_DRAIN = 1.5  # health per frame at 0 energy

# Combat
ATTACK_FAILURE_CHANCE = 0.05  # 5%
DEFENSE_FAILURE_CHANCE = 0.05  # 5%
BASE_ATTACK_DAMAGE = 10
BASE_DEFENSE_REDUCTION = 0.20  # 20%

# Reproduction
SEXUAL_ENERGY_COST = 0.40  # 40% each parent
ASEXUAL_ENERGY_COST = 0.80  # 80% single parent
MIN_REPRODUCTION_ENERGY = 0.40  # Must have 40% energy

# Revive
REVIVE_DONOR_COST = 0.50  # Max 50% of donor energy
REVIVE_RECIPIENT_TARGET = 0.25  # Target 25% of recipient max
REVIVE_RANGE = 30  # pixels
COOPERATION_REWARD = 1  # DNA point for successful revive

# Evolution
MUTATION_RATE_SWITCH = 0.03  # 3% chance to flip DNA switch
MUTATION_RATE_POINTS = 0.15  # ±15% point variation
ABILITY_UNLOCK_CHANCE = 0.01  # 1% per eating tick when full
ABILITY_BRAIN_COST = 20  # Brain capacity increase for new ability

# Performance
TARGET_FPS = 60
MAX_DOTS = 5000
```

**Code Structure Preview:**
```
dot_ai_2.0/
├── src/
│   ├── core/
│   │   ├── dna.py          # DNA profile, inheritance, mutation
│   │   ├── brain.py        # Brain class, slots, processing
│   │   ├── resources.py    # Energy, health, hunger
│   │   └── dot.py          # Main Dot class (refactored)
│   ├── senses/
│   │   ├── base_sense.py   # Abstract sense class
│   │   ├── vision.py       # Vision distance & FOV
│   │   ├── detection.py    # Dot/Food/Power detection
│   │   └── manager.py      # Sense slot management
│   ├── actions/
│   │   ├── base_action.py  # Abstract action class
│   │   ├── movement.py     # Movement action
│   │   ├── eating.py       # Eating action (Stages 1-3)
│   │   ├── combat.py       # Attack & Defend actions
│   │   ├── reproduction.py # Replicate action & mate selection
│   │   └── manager.py      # Action slot management
│   ├── environment/
│   │   ├── food.py         # Food entities
│   │   ├── obstacles.py    # Obstacles
│   │   └── world.py        # World management
│   ├── ai/
│   │   ├── decision.py     # Decision-making system
│   │   ├── priority.py     # Need/want prioritization
│   │   └── learning.py     # Q-Learning or NN
│   └── utils/
│       ├── config.py       # Configuration management
│       └── genetics.py     # Evolution utilities
├── tests/
│   ├── test_dna.py
│   ├── test_brain.py
│   └── test_actions.py
├── config/
│   └── default_config.yaml # Tunable parameters
├── dot_ai.py               # Legacy v1.0
├── dot_ai_2.0.py           # New main entry point
└── DOT_AI_2.0_PLAN.md      # This document
```

---

## 📚 References & Inspiration

- Boids algorithm (flocking behavior)
- Evolutionary algorithms in games
- Ecosystem simulation games (SimLife, Spore)
- Multi-agent systems research
- Predator-prey models (Lotka-Volterra)

---

**Document Version:** 1.0
**Last Updated:** January 1, 2026
**Status:** Planning Phase - Ready for Review
