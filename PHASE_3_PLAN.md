# 🎯 PHASE 3 IMPLEMENTATION PLAN

**Goal:** Combat, Reproduction, and Death Mechanics  
**Status:** 🟡 READY TO START

---

## 📦 DELIVERABLES

### Must-Have Features
1. ✅ Attack action (damage other dots)
2. ✅ Defend action (reduce incoming damage)
3. ✅ Replicate action (asexual reproduction)
4. ✅ Death → Food conversion
5. ✅ Combat mechanics with 5% failure rate
6. ✅ Energy costs for all actions
7. ✅ Utility-based AI (weighted action selection)
8. ✅ Action priority system
9. ✅ Visual indicators for combat
10. ✅ Population management

---

## 🎮 ACTIONS TO IMPLEMENT

### 1. **Attack Action** ⚔️

**Mechanics:**
- Requires `attack` gene enabled
- Target must be within range (based on gene points)
- Costs 5% energy per attack attempt
- Deals damage = 10 + (gene_points * 0.5)
- **5% probabilistic failure chance** (miss)
- Attack priority based on gene points

**DNA Configuration:**
```python
attack_range = 30 + (attack_points * 2)  # pixels
attack_damage = 10 + (attack_points * 0.5)  # health damage
attack_cost = max_energy * 0.05  # 5% energy
```

**Decision Logic:**
```python
# Attack if:
# - Enemy nearby with low health
# - Own health > 50%
# - Attack enabled
utility = (1.0 - target_health_ratio) * attack_priority
```

---

### 2. **Defend Action** 🛡️

**Mechanics:**
- Requires `defend` gene enabled
- Passive damage reduction when active
- Costs 3% energy per second while active
- Reduces incoming damage by percentage
- Higher gene points = better defense

**DNA Configuration:**
```python
defense_reduction = 0.3 + (defend_points * 0.01)  # 30-80% reduction
defense_cost = max_energy * 0.03  # 3% energy per second
```

**Decision Logic:**
```python
# Defend if:
# - Being attacked
# - Low health
# - Defend enabled
utility = (1.0 - own_health_ratio) * defend_priority
```

---

### 3. **Replicate Action** 🧬

**Mechanics:**
- Requires `replicate` gene enabled
- **Asexual reproduction** (Phase 3 only, sexual in Phase 4)
- Costs **80% of max energy**
- Only works if energy > 80%
- Creates child with mutated DNA
- Child spawns nearby
- Parent loses 80% energy

**DNA Configuration:**
```python
replication_cost = max_energy * 0.80  # 80% energy
mutation_rate = 0.1  # 10% chance per gene
mutation_amount = 5  # +/- 5 points max
```

**Decision Logic:**
```python
# Replicate if:
# - Energy > 80%
# - Health > 70%
# - Replicate enabled
# - Not starving
utility = energy_ratio * health_ratio * replicate_priority
```

---

### 4. **Death → Food Conversion** 💀➡️🍎

**Mechanics:**
- When dot dies, create food at death location
- Food energy = remaining dot energy + health
- Allows cannibalism/recycling energy
- Bodies decay over time

**Implementation:**
```python
def on_dot_death(dot):
    food_energy = dot.resources.energy + (dot.resources.health * 0.5)
    food = Food(next_id, dot.position, food_energy)
    world.food.append(food)
```

---

## 🧠 UTILITY-BASED AI SYSTEM

### Action Selection Algorithm

```python
def decide_action(self, perceived_world):
    """
    Calculate utility for each action
    Choose highest utility action
    """
    utilities = {}
    
    # 1. SEEK FOOD
    if perceived_world['food']:
        hunger_urgency = self.resources.hunger
        utilities['seek_food'] = hunger_urgency * 10
    
    # 2. ATTACK
    if self.dna.attack.enabled and perceived_world['dots']:
        nearest_dot = find_nearest(perceived_world['dots'])
        if distance_to(nearest_dot) < attack_range:
            enemy_weakness = 1.0 - nearest_dot.health_ratio
            utilities['attack'] = enemy_weakness * self.dna.attack.points
    
    # 3. DEFEND
    if self.dna.defend.enabled:
        if self.resources.health < 50:
            danger_level = 1.0 - self.resources.get_health_ratio()
            utilities['defend'] = danger_level * self.dna.defend.points
    
    # 4. REPLICATE
    if self.dna.replicate.enabled:
        if self.resources.energy > self.resources.max_energy * 0.8:
            readiness = self.resources.get_energy_ratio()
            utilities['replicate'] = readiness * self.dna.replicate.points
    
    # 5. IDLE (baseline)
    utilities['idle'] = 1.0
    
    # Choose action with highest utility
    return max(utilities, key=utilities.get)
```

---

## ⚔️ COMBAT SYSTEM

### Attack Resolution

```python
def execute_attack(attacker, target):
    """Execute attack with probabilistic failure"""
    # 5% chance to miss
    if random.random() < 0.05:
        return "MISS"
    
    # Calculate damage
    base_damage = 10
    dna_damage = attacker.dna.attack.points * 0.5
    total_damage = base_damage + dna_damage
    
    # Apply defense reduction
    if target.is_defending:
        defense_reduction = 0.3 + (target.dna.defend.points * 0.01)
        total_damage *= (1.0 - defense_reduction)
    
    # Apply damage
    target.resources.deplete_health(total_damage)
    
    # Energy cost for attacker
    attacker.resources.deplete_energy(attacker.resources.max_energy * 0.05)
    
    return "HIT"
```

---

## 🎨 VISUAL INDICATORS

### Combat Visualization

- **Red flash** on hit dot
- **"MISS!"** text for failed attacks
- **Damage numbers** floating up
- **Shield icon** when defending
- **Attack range circle** (debug mode)

### Reproduction Visualization

- **Heart icon** above parent
- **Sparkle effect** at birth
- **DNA inheritance line** (debug)

---

## 💰 ENERGY COSTS SUMMARY

| Action | Energy Cost | Condition |
|--------|-------------|-----------|
| Idle | 2.0/sec | Always |
| Move | 1.0/sec | When moving |
| Eat | 0% | Free |
| Attack | 5% | Per attempt |
| Defend | 3%/sec | While active |
| Replicate | 80% | One-time |

---

## 🎯 ACCEPTANCE CRITERIA

1. ✅ Dots can attack and damage each other
2. ✅ Attacks have 5% miss chance
3. ✅ Defend reduces incoming damage
4. ✅ Dots can replicate when energy > 80%
5. ✅ Children have mutated DNA
6. ✅ Dead dots become food
7. ✅ Utility AI chooses actions intelligently
8. ✅ Combat visuals display correctly
9. ✅ Population remains stable (births = deaths)
10. ✅ Different DNA strategies emerge

---

## 🚀 IMPLEMENTATION ORDER

1. **Step 1:** Add Attack action
   - Attack execution
   - Damage calculation
   - Energy cost
   - Visual feedback

2. **Step 2:** Add Defend action
   - Defense state tracking
   - Damage reduction
   - Energy drain
   - Visual indicator

3. **Step 3:** Add Replicate action
   - Asexual reproduction
   - DNA mutation
   - Child spawning
   - Energy cost

4. **Step 4:** Death → Food conversion
   - Create food on death
   - Energy transfer
   - Position handling

5. **Step 5:** Utility-based AI
   - Action utility calculation
   - Weighted selection
   - Priority balancing

6. **Step 6:** Combat visuals
   - Hit effects
   - Damage numbers
   - State indicators

---

## 📊 EXPECTED BEHAVIORS

### Aggressive Strategy
- High attack points
- Low defend points
- Seeks out weak dots
- High risk, high reward

### Defensive Strategy
- High defend points
- Low attack points
- Avoids combat
- Focuses on survival

### Reproductive Strategy
- High replicate points
- Focuses on energy gathering
- Rapid population growth
- Lower individual survivability

### Balanced Strategy
- Moderate all stats
- Adapts to situations
- Stable population
- Long-term survival

---

**Phase 3 Status:** 🟡 READY TO IMPLEMENT  
**Estimated Time:** 3-4 hours  
**Complexity:** Medium-High  

Ready to start implementing! 🚀
