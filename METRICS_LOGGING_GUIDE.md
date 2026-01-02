# 📊 Metrics Logging & Monitoring System

## Overview

The Dot AI 2.0 simulation now includes a comprehensive **metrics logging and monitoring system** that allows you to:

1. **Log all simulation events** to structured data files
2. **Track colony evolution** over time with detailed metrics
3. **Monitor the simulation in real-time** using a live dashboard
4. **Analyze historical data** programmatically for research

All printed terminal output is now also captured as structured JSON/CSV data for future analysis!

---

## 🎯 What Gets Logged

### 1. Events Stream (`events.jsonl`)
Real-time event log of everything that happens:
- **BIRTH**: Dot births (with parent IDs, DNA points, generation)
- **DEATH**: Dot deaths (with lifetime, cause: combat/starvation)
- **ATTACK**: Combat events (attacker, target, damage, hit/miss)
- **REPRODUCTION**: Sexual/asexual reproduction events
- **EXTINCTION**: Generation extinction events
- **GENERATION_END**: End-of-generation summaries

### 2. Colony Metrics (`colony_metrics.jsonl`)
Sampled every second during simulation:
- **Population**: Current dot count
- **DNA Statistics**: Average, min, max DNA points
- **Energy**: Total, average, min, max energy across colony
- **Health**: Average health
- **Age**: Average and maximum dot age
- **Food**: Food count and total available energy
- **Cumulative Stats**: Total births, deaths, attacks

### 3. Generation Summary (`generation_summary.csv`)
One row per generation with:
- Survival time
- Peak population
- Total births (sexual vs asexual)
- Total deaths (combat vs starvation)
- Average DNA points
- Session timestamp

### 4. Dot Lifetimes (`dot_lifetimes.csv`)
Individual tracking of every dot:
- Birth and death times
- Lifetime duration
- Total DNA points
- Offspring count
- Death cause

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `matplotlib` - For charting
- `pandas` - For data analysis
- (pygame, numpy already installed)

### Step 2: Run the Simulation

```bash
python main.py
```

The simulation will automatically create a logging session in `logs/YYYYMMDD_HHMMSS/`.

**You'll see:**
```
📊 Starting logging session: 20260102_143025
📊 Metrics logger initialized: logs\20260102_143025
```

### Step 3: Start the Real-Time Monitor

In a **separate terminal/window**, run:

```bash
python monitor.py
```

The monitor will:
1. Auto-detect the latest session
2. Open a live dashboard with 6 charts
3. Update every second as the simulation runs
4. Show real-time colony evolution metrics

---

## 📈 Monitor Dashboard

The real-time monitor displays **6 interactive charts**:

### Row 1: Population & DNA
- **🌍 Colony Population Over Time**: Live population graph with current count
- **🧬 DNA Points**: Average DNA points evolution

### Row 2: Energy & Resources
- **⚡ Colony Energy**: Average and total energy trends
- **🍎 Food Count**: Available food resources

### Row 3: Generations & Reproduction
- **📊 Generation Survival Times**: Bar chart of how long each generation survived
- **💕 Reproduction Types**: Pie chart showing sexual vs asexual reproduction breakdown

The dashboard updates live and displays current generation number and simulation time in the title.

---

## 🛠️ Monitor Commands

### Auto-detect latest session:
```bash
python monitor.py
```

### Monitor specific session:
```bash
python monitor.py 20260102_143025
```

### List all available sessions:
```bash
python monitor.py --list
```

### Faster refresh rate (500ms instead of 1000ms):
```bash
python monitor.py --refresh 500
```

### Custom log directory:
```bash
python monitor.py --log-dir my_experiments
```

---

## 📁 File Structure

```
logs/
├── 20260102_143025/              # Session folder (timestamp)
│   ├── session_metadata.json    # Session info
│   ├── events.jsonl              # Event stream
│   ├── colony_metrics.jsonl     # Colony metrics (sampled every 1s)
│   ├── generation_summary.csv   # Generation summaries
│   └── dot_lifetimes.csv         # Individual dot tracking
│
└── 20260102_150330/              # Another session
    └── ...
```

---

## 🔬 Programmatic Data Analysis

You can analyze the logged data with Python:

### Example: Load and analyze generation data

```python
import pandas as pd
import json

# Load generation summaries
df = pd.read_csv('logs/20260102_143025/generation_summary.csv')

# Calculate average survival time
avg_survival = df['survival_time'].mean()
print(f"Average generation survival: {avg_survival:.2f}s")

# Find most successful generation
best_gen = df.loc[df['survival_time'].idxmax()]
print(f"Best generation: {best_gen['generation']} ({best_gen['survival_time']:.2f}s)")

# Analyze reproduction trends
print(f"Sexual reproduction rate: {df['sexual_births'].sum() / df['total_births'].sum() * 100:.1f}%")
```

### Example: Load colony metrics timeline

```python
# Load colony metrics (JSONL format)
metrics = []
with open('logs/20260102_143025/colony_metrics.jsonl', 'r') as f:
    for line in f:
        metrics.append(json.loads(line))

# Convert to DataFrame
df = pd.DataFrame(metrics)

# Plot population over time
import matplotlib.pyplot as plt
plt.plot(df['simulation_time'], df['population'])
plt.title('Population Over Time')
plt.xlabel('Simulation Time (s)')
plt.ylabel('Population')
plt.show()
```

### Example: Analyze individual dot lifetimes

```python
# Load dot lifetimes
lifetimes = pd.read_csv('logs/20260102_143025/dot_lifetimes.csv')

# Average lifetime by generation
avg_lifetime_by_gen = lifetimes.groupby('generation')['lifetime'].mean()
print(avg_lifetime_by_gen)

# Most successful dots (by offspring count)
top_breeders = lifetimes.nlargest(10, 'offspring_count')
print(top_breeders[['dot_id', 'lifetime', 'offspring_count', 'total_dna_points']])
```

---

## 🧪 Research Use Cases

### 1. **DNA Evolution Studies**
Track how average DNA points change over generations to identify optimal strategies.

### 2. **Reproduction Strategy Analysis**
Compare sexual vs asexual reproduction success rates across different environments.

### 3. **Survival Metrics**
Identify which DNA profiles lead to longest survival times.

### 4. **Population Dynamics**
Study population boom/bust cycles and their correlation with food availability.

### 5. **Combat vs Cooperation**
Analyze attack frequency and its impact on colony survival.

---

## ⚙️ Configuration

### Adjust Colony Metrics Sampling Rate

In `core/metrics_logger.py`:

```python
self.colony_metric_interval = 1.0  # Log every N seconds (default: 1.0)
```

Lower values = more frequent sampling (larger files).

### Adjust Monitor Refresh Rate

```bash
python monitor.py --refresh 250  # Update every 250ms (4 times per second)
```

---

## 🎓 Educational Benefits

This monitoring system teaches:

1. **Data Science**: Working with time-series data, JSON/CSV formats
2. **Real-time Systems**: Live data streaming and visualization
3. **Scientific Computing**: Using matplotlib and pandas for analysis
4. **Systems Design**: Separation of concerns (simulation vs monitoring)
5. **Research Methods**: Structured data collection and analysis

---

## 💡 Tips & Tricks

### Run Long Experiments Overnight
The simulation logs everything automatically - you can analyze the data later:

```bash
# Run simulation overnight
python main.py

# Next morning, analyze the data
python -c "
import pandas as pd
df = pd.read_csv('logs/LATEST_SESSION/generation_summary.csv')
print(df.describe())
"
```

### Compare Multiple Sessions
```python
import pandas as pd
import glob

# Load all generation summaries
all_sessions = []
for file in glob.glob('logs/*/generation_summary.csv'):
    df = pd.read_csv(file)
    df['session'] = file.split('/')[1]  # Extract session name
    all_sessions.append(df)

combined = pd.concat(all_sessions)
print(combined.groupby('session')['survival_time'].mean())
```

### Export Charts Programmatically
Modify `monitor.py` to save charts instead of displaying:

```python
# In monitor.py, replace plt.show() with:
plt.savefig('colony_evolution.png', dpi=300, bbox_inches='tight')
```

---

## 🐛 Troubleshooting

### Monitor shows empty charts
- Make sure the simulation is running and generating data
- Check that the session directory contains log files
- Verify files aren't empty (simulation may have just started)

### "matplotlib not installed" error
```bash
pip install matplotlib pandas
```

### Monitor not updating
- Increase refresh rate: `python monitor.py --refresh 500`
- Check terminal for errors
- Verify log files are being written (check file timestamps)

---

## 📚 File Format Specifications

### JSONL Format (JSON Lines)
Each line is a complete JSON object:
```json
{"session_time": 10.5, "event_type": "BIRTH", "data": {"dot_id": 5}}
{"session_time": 11.2, "event_type": "ATTACK", "data": {"attacker_id": 3}}
```

Read with:
```python
import json
with open('events.jsonl', 'r') as f:
    for line in f:
        event = json.loads(line)
        print(event)
```

### CSV Format
Standard CSV with headers:
```csv
generation,survival_time,peak_population,total_births
1,45.3,8,12
2,67.8,15,23
```

Read with pandas:
```python
import pandas as pd
df = pd.read_csv('generation_summary.csv')
```

---

## 🎯 Next Steps

1. **Run your first monitored session**: Start both simulation and monitor
2. **Experiment with parameters**: Change `initial_dots`, `initial_food` in main.py
3. **Analyze your data**: Try the programmatic examples above
4. **Compare strategies**: Run multiple sessions and compare results
5. **Extend the system**: Add your own custom metrics and charts!

Happy evolving! 🧬✨
