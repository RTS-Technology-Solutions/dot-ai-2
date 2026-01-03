"""
📊 QUICK STATS OVERVIEW
Fast summary of any simulation run.
"""

import pandas as pd
import json
from pathlib import Path
import sys

def quick_stats(log_dir):
    """Display quick overview stats for a simulation run"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_dir}")
        return
    
    print("="*80)
    print(f"📊 QUICK STATS: {log_path.name}")
    print("="*80)
    
    # Load data
    try:
        lifetimes = pd.read_csv(log_path / "dot_lifetimes.csv")
        gen_summary = pd.read_csv(log_path / "generation_summary.csv")
        
        # Load colony metrics
        colony_data = []
        with open(log_path / "colony_metrics.jsonl", 'r') as f:
            for line in f:
                colony_data.append(json.loads(line))
        colony_df = pd.DataFrame(colony_data)
        
    except FileNotFoundError as e:
        print(f"❌ Missing file: {e}")
        return
    
    # Detect incomplete generations (crashed before summary was written)
    max_gen_in_summary = gen_summary['generation'].max()
    max_gen_in_lifetimes = lifetimes['generation'].max()
    max_gen_in_colony = colony_df['generation'].max()
    
    incomplete_gen = None
    if max_gen_in_lifetimes > max_gen_in_summary or max_gen_in_colony > max_gen_in_summary:
        incomplete_gen = max(max_gen_in_lifetimes, max_gen_in_colony)
        print(f"\n⚠️  INCOMPLETE GENERATION DETECTED!")
        print(f"  Generation {incomplete_gen} crashed before final metrics could be saved.")
        print(f"  Reconstructing from real-time data...")
        
        # Reconstruct Generation metrics from colony_metrics and lifetimes
        crash_gen_metrics = colony_df[colony_df['generation'] == incomplete_gen]
        crash_gen_dots = lifetimes[lifetimes['generation'] == incomplete_gen]
        
        if len(crash_gen_metrics) > 0:
            # Build a summary row for the crashed generation
            crash_summary = {
                'generation': incomplete_gen,
                'survival_time': crash_gen_metrics['simulation_time'].max(),
                'total_births': crash_gen_metrics['total_births'].max() if 'total_births' in crash_gen_metrics.columns else len(crash_gen_dots),
                'sexual_births': crash_gen_metrics['gen_sexual_births'].max() if 'gen_sexual_births' in crash_gen_metrics.columns else 0,
                'asexual_births': crash_gen_metrics['gen_asexual_births'].max() if 'gen_asexual_births' in crash_gen_metrics.columns else 0,
                'combat_kills': (crash_gen_dots['death_cause'] == 'combat').sum(),
                'starvation_deaths': (crash_gen_dots['death_cause'] == 'starvation').sum(),
                'peak_population': crash_gen_metrics['population'].max()
            }
            
            # Append to gen_summary
            gen_summary = pd.concat([gen_summary, pd.DataFrame([crash_summary])], ignore_index=True)
            print(f"  ✅ Reconstructed Gen {incomplete_gen} metrics from {len(crash_gen_metrics)} colony snapshots")
    
    # Calculate stats
    total_dots = len(lifetimes)
    total_gens = gen_summary['generation'].max()
    total_time = colony_df['session_time'].max()
    
    print(f"\n⏱️  RUNTIME:")
    print(f"  Total Time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  Generations: {int(total_gens)}")
    if incomplete_gen:
        print(f"  ⚠️  Generation {incomplete_gen} incomplete (crashed)")
    print(f"  Avg Time/Gen: {total_time/total_gens:.1f}s")
    
    print(f"\n👥 POPULATION:")
    print(f"  Total Dots Created: {total_dots:,}")
    print(f"  Avg/Generation: {total_dots/total_gens:.0f}")
    print(f"  Peak Population: {colony_df['population'].max()}")
    
    print(f"\n🧬 DNA EVOLUTION:")
    print(f"  Starting Budget: 100 points")
    print(f"  Final Avg: {lifetimes[lifetimes['generation'] == total_gens]['total_dna_points'].mean():.1f}")
    print(f"  Maximum Observed: {lifetimes['total_dna_points'].max():.1f}")
    print(f"  Growth Factor: {lifetimes['total_dna_points'].max() / 100:.2f}x")
    
    print(f"\n💕 REPRODUCTION:")
    total_births = gen_summary['total_births'].sum()
    total_sexual = gen_summary['sexual_births'].sum()
    total_asexual = gen_summary['asexual_births'].sum()
    print(f"  Total Births: {total_births}")
    print(f"  Sexual: {total_sexual} ({total_sexual/total_births*100:.1f}%)")
    print(f"  Asexual: {total_asexual} ({total_asexual/total_births*100:.1f}%)")
    
    print(f"\n⚰️  DEATHS:")
    total_combat = gen_summary['combat_kills'].sum()
    total_starvation = gen_summary['starvation_deaths'].sum()
    total_deaths = total_combat + total_starvation
    print(f"  Total Deaths: {total_deaths}")
    print(f"  Combat: {total_combat} ({total_combat/total_deaths*100:.1f}%)")
    print(f"  Starvation: {total_starvation} ({total_starvation/total_deaths*100:.1f}%)")
    
    print(f"\n🏆 RECORDS:")
    longest_life = lifetimes.loc[lifetimes['lifetime'].idxmax()]
    most_offspring = lifetimes.loc[lifetimes['offspring_count'].idxmax()]
    highest_dna = lifetimes.loc[lifetimes['total_dna_points'].idxmax()]
    
    print(f"  Longest Life: Dot #{longest_life['dot_id']:.0f} ({longest_life['lifetime']:.1f}s)")
    print(f"  Most Offspring: Dot #{most_offspring['dot_id']:.0f} ({most_offspring['offspring_count']:.0f} children)")
    print(f"  Highest DNA: Dot #{highest_dna['dot_id']:.0f} ({highest_dna['total_dna_points']:.1f} points)")
    
    print(f"\n📈 GENERATION BREAKDOWN:")
    if incomplete_gen:
        print(f"  (⚠️ = Incomplete/Crashed Generation)")
    print(f"  {'Gen':<6} {'Dots':<8} {'Avg DNA':<10} {'Survival':<12} {'Births':<8} {'Peak Pop':<8}")
    print(f"  {'-'*6} {'-'*8} {'-'*10} {'-'*12} {'-'*8} {'-'*8}")
    
    for _, row in gen_summary.iterrows():
        gen_num = int(row['generation'])
        gen_dots = lifetimes[lifetimes['generation'] == gen_num]
        avg_dna = gen_dots['total_dna_points'].mean()
        
        marker = "⚠️" if gen_num == incomplete_gen else "  "
        print(f"{marker}{gen_num:<6} {len(gen_dots):<8,} {avg_dna:<10.1f} {row['survival_time']:<12.1f} "
              f"{row['total_births']:<8.0f} {row['peak_population']:<8.0f}")
    
    print("="*80)
    
    # Detailed crash analysis if applicable
    if incomplete_gen:
        print(f"\n🔍 GENERATION {incomplete_gen} CRASH ANALYSIS:")
        crash_gen_metrics = colony_df[colony_df['generation'] == incomplete_gen]
        crash_gen_dots = lifetimes[lifetimes['generation'] == incomplete_gen]
        
        print(f"\n  📊 RECONSTRUCTED METRICS:")
        print(f"    Dots Created: {len(crash_gen_dots):,}")
        print(f"    Avg DNA: {crash_gen_dots['total_dna_points'].mean():.1f}")
        print(f"    Max DNA: {crash_gen_dots['total_dna_points'].max():.1f}")
        print(f"    Peak Population: {crash_gen_metrics['population'].max()}")
        print(f"    Total Births: {crash_gen_metrics['total_births'].max() if 'total_births' in crash_gen_metrics.columns else len(crash_gen_dots)}")
        print(f"    Simulation Time: {crash_gen_metrics['simulation_time'].max():.1f}s")
        
        print(f"\n  ⏱️  TIMELINE:")
        print(f"    Started: {crash_gen_metrics['session_time'].min():.1f}s")
        print(f"    Crashed: {crash_gen_metrics['session_time'].max():.1f}s")
        print(f"    Duration: {crash_gen_metrics['simulation_time'].max():.1f}s")
        
        print(f"\n  📈 POPULATION TRAJECTORY:")
        # Sample population at different points
        time_points = [0, 0.25, 0.5, 0.75, 1.0]
        max_time = crash_gen_metrics['simulation_time'].max()
        for tp in time_points:
            target_time = max_time * tp
            closest_idx = (crash_gen_metrics['simulation_time'] - target_time).abs().idxmin()
            snapshot = crash_gen_metrics.loc[closest_idx]
            print(f"    t={snapshot['simulation_time']:.1f}s: {snapshot['population']:.0f} dots (avg DNA: {snapshot['avg_dna']:.1f})")
        
        print(f"\n  💥 LIKELY CRASH CAUSE:")
        max_pop = crash_gen_metrics['population'].max()
        if max_pop > 50:
            print(f"    Population overload: {max_pop} concurrent dots")
            print(f"    System likely couldn't handle simulation complexity")
        if crash_gen_dots['total_dna_points'].max() > 200:
            print(f"    Extreme DNA growth: {crash_gen_dots['total_dna_points'].max():.1f} points")
            print(f"    High-complexity dots may have caused performance issues")
        
        print(f"\n  🧬 DNA DISTRIBUTION (Gen {incomplete_gen}):")
        dna_bins = [0, 100, 150, 200, 250, 300, 500, 1000, 10000]
        dna_counts = pd.cut(crash_gen_dots['total_dna_points'], bins=dna_bins).value_counts().sort_index()
        for interval, count in dna_counts.items():
            if count > 0:
                pct = (count / len(crash_gen_dots)) * 100
                print(f"    {interval}: {count:,} dots ({pct:.1f}%)")
        
        print("="*80)
    
    # Identify interesting patterns
    print("\n💡 OBSERVATIONS:")
    
    # Check for population explosion
    max_gen_dots = lifetimes['generation'].value_counts().max()
    if max_gen_dots > 1000:
        explosion_gen = lifetimes['generation'].value_counts().idxmax()
        print(f"  🚀 Population explosion in Generation {explosion_gen} ({max_gen_dots:,} dots!)")
    
    # Check for DNA growth
    if lifetimes['total_dna_points'].max() > 150:
        print(f"  🧬 Significant DNA growth detected (max {lifetimes['total_dna_points'].max():.1f} points)")
    
    # Check for long survival
    if gen_summary['survival_time'].max() > 300:
        longest_gen = gen_summary.loc[gen_summary['survival_time'].idxmax(), 'generation']
        print(f"  ⏱️  Extended survival in Generation {longest_gen:.0f} ({gen_summary['survival_time'].max():.1f}s)")
    
    # Check reproduction success
    if total_sexual / total_births > 0.6:
        print(f"  💕 High sexual reproduction rate ({total_sexual/total_births*100:.1f}%)")
    
    print("="*80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        log_dir = sys.argv[1]
    else:
        # Find most recent log directory
        logs_dir = Path("../logs")
        if logs_dir.exists():
            log_dirs = sorted([d for d in logs_dir.iterdir() if d.is_dir()], reverse=True)
            if log_dirs:
                log_dir = str(log_dirs[0])
            else:
                print("❌ No log directories found in ../logs/")
                sys.exit(1)
        else:
            print("❌ Logs directory not found: ../logs/")
            sys.exit(1)
    
    quick_stats(log_dir)
