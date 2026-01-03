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
    
    # Calculate stats
    total_dots = len(lifetimes)
    total_gens = gen_summary['generation'].max()
    total_time = colony_df['session_time'].max()
    
    print(f"\n⏱️  RUNTIME:")
    print(f"  Total Time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  Generations: {total_gens}")
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
    print(f"  {'Gen':<6} {'Dots':<8} {'Avg DNA':<10} {'Survival':<12} {'Births':<8} {'Peak Pop':<8}")
    print(f"  {'-'*6} {'-'*8} {'-'*10} {'-'*12} {'-'*8} {'-'*8}")
    
    for _, row in gen_summary.iterrows():
        gen_num = int(row['generation'])
        gen_dots = lifetimes[lifetimes['generation'] == gen_num]
        avg_dna = gen_dots['total_dna_points'].mean()
        
        print(f"  {gen_num:<6} {len(gen_dots):<8,} {avg_dna:<10.1f} {row['survival_time']:<12.1f} "
              f"{row['total_births']:<8.0f} {row['peak_population']:<8.0f}")
    
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
