# 📊 Analysis Tools

This folder contains Python scripts for analyzing simulation data from dot-ai-2 runs.

## 📁 Scripts

### 1. **quick_stats.py** - Fast Overview
Get a quick summary of any simulation run.

```bash
# Analyze most recent run
python quick_stats.py

# Analyze specific run
python quick_stats.py ../logs/20260102_223524
```

**Shows:**
- Runtime and generation count
- Population statistics
- DNA evolution metrics
- Reproduction breakdown
- Death causes
- Record holders

---

### 2. **explosion_analysis.py** - Population Explosion Deep Dive
Detailed analysis for runs where population exploded.

```bash
python explosion_analysis.py
```

**Analyzes:**
- When explosion occurred (which generation)
- DNA growth patterns (100 → 700+ points!)
- Top performers (highest DNA, most offspring)
- Timeline breakdown
- Death pattern analysis

**Outputs:**
- Console report with detailed stats
- `analysis_explosion.png` - 6 visualization charts

---

### 3. **dna_pattern_analyzer.py** - Champion DNA Analysis
Identifies what gene combinations led to success.

```bash
python dna_pattern_analyzer.py
```

**Analyzes:**
- Champion identification (top 10% by fitness)
- DNA pattern correlations
- Success factors (DNA vs lifetime vs offspring)
- Death cause patterns
- Strategy differences

**Outputs:**
- Console report with correlations
- `analysis_dna_patterns.png` - Pattern visualizations

---

### 4. **generation_comparer.py** - Cross-Generation Trends
Compare statistics across generations to see evolution.

```bash
# Compare all generations
python generation_comparer.py

# Compare specific generations
python generation_comparer.py ../logs/20260102_223524 1 3 5 7
```

**Shows:**
- Generation-by-generation comparison table
- Trend analysis (DNA growth, lifetime improvement)
- Visual progression charts

**Outputs:**
- Comparison table
- `analysis_generation_comparison.png` - Trend charts

---

## 🚀 Quick Start

```bash
# 1. Navigate to analysis folder
cd analysis

# 2. Run quick overview
python quick_stats.py

# 3. If you see population explosion, run deep dive
python explosion_analysis.py

# 4. Analyze DNA patterns
python dna_pattern_analyzer.py

# 5. Check evolution trends
python generation_comparer.py
```

---

## 📊 Output Files

All scripts save visualization charts to the log directory:

- `analysis_explosion.png` - Population explosion charts
- `analysis_dna_patterns.png` - DNA pattern analysis
- `analysis_generation_comparison.png` - Generation trends

---

## 💡 Example Workflow

After running simulation overnight:

```bash
# 1. Quick check
python quick_stats.py
# Output: "Population explosion in Generation 7 (12,088 dots!)"

# 2. Investigate explosion
python explosion_analysis.py
# Output: Detailed breakdown of Gen 7 explosion

# 3. Find winning strategies
python dna_pattern_analyzer.py
# Output: Champions had avg 715 DNA, high feeding genes

# 4. Track evolution
python generation_comparer.py
# Output: DNA grew 615% from Gen 1 to Gen 7
```

---

## 📦 Requirements

All scripts use standard scientific Python libraries:

```
pandas
numpy
matplotlib
```

Already installed if you have the main simulation requirements.

---

## 🔧 Customization

Each script can be imported and used programmatically:

```python
from explosion_analysis import analyze_explosion

results = analyze_explosion("../logs/20260102_223524")
print(f"Max DNA reached: {results['max_dna']}")
```

---

## 📝 Notes

- Scripts default to analyzing the **most recent log directory**
- All scripts work with standard log output format (CSV + JSONL)
- Charts are automatically saved alongside the data
- Safe to run multiple times (overwrites old charts)

---

**Happy Analyzing! 🧬**
