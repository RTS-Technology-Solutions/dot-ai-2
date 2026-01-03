"""
🚀 POPULATION EXPLOSION ANALYSIS
Analyzes runs where the population exploded due to successful evolutionary strategies.
"""

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def analyze_explosion(log_dir):
    """Analyze a simulation run for population explosion patterns"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_dir}")
        return
    
    print("="*80)
    print("🚀 POPULATION EXPLOSION DEEP DIVE ANALYSIS")
    print("="*80)
    print(f"📁 Analyzing: {log_path.name}")
    print()
    
    # Load all data
    try:
        lifetimes = pd.read_csv(log_path / "dot_lifetimes.csv")
        gen_summary = pd.read_csv(log_path / "generation_summary.csv")
        
        # Load colony metrics (JSONL format)
        colony_data = []
        with open(log_path / "colony_metrics.jsonl", 'r') as f:
            for line in f:
                colony_data.append(json.loads(line))
        colony_df = pd.DataFrame(colony_data)
        
    except FileNotFoundError as e:
        print(f"❌ Missing required file: {e}")
        return
    
    # ===== HEADLINE STATS =====
    print(f"📊 HEADLINE STATS:")
    print(f"  Total Dots Created: {len(lifetimes):,}")
    print(f"  Total Generations: {gen_summary['generation'].max()}")
    print(f"  Total Runtime: {colony_df['session_time'].max()/60:.1f} minutes")
    print(f"  Final Session Time: {colony_df['session_time'].max():.1f} seconds")
    
    # ===== GENERATION BREAKDOWN =====
    print(f"\n📈 DOTS CREATED PER GENERATION:")
    for gen in sorted(lifetimes['generation'].unique()):
        gen_dots = lifetimes[lifetimes['generation'] == gen]
        print(f"  Gen {gen}: {len(gen_dots):>6,} dots (avg DNA: {gen_dots['total_dna_points'].mean():>7.1f})")
    
    # Find the explosion generation (most dots)
    explosion_gen = lifetimes['generation'].value_counts().idxmax()
    explosion_dots = lifetimes[lifetimes['generation'] == explosion_gen]
    
    print(f"\n🎯 GENERATION {explosion_gen} (THE EXPLOSION):")
    print(f"  Dots Created: {len(explosion_dots):,}")
    print(f"  Avg DNA: {explosion_dots['total_dna_points'].mean():.2f}")
    print(f"  Max DNA: {explosion_dots['total_dna_points'].max():.2f}")
    print(f"  Min DNA: {explosion_dots['total_dna_points'].min():.2f}")
    print(f"  Avg Lifetime: {explosion_dots['lifetime'].mean():.2f}s")
    print(f"  Max Lifetime: {explosion_dots['lifetime'].max():.2f}s")
    
    # ===== DNA CHAMPIONS =====
    print(f"\n👑 TOP 10 HIGHEST DNA DOTS:")
    top_dna = lifetimes.nlargest(10, 'total_dna_points')[
        ['dot_id', 'generation', 'lifetime', 'total_dna_points', 'offspring_count', 'death_cause']
    ]
    print(top_dna.to_string(index=False))
    
    # ===== TOP BREEDERS =====
    print(f"\n💕 TOP 10 MOST OFFSPRING:")
    top_breeders = lifetimes.nlargest(10, 'offspring_count')[
        ['dot_id', 'generation', 'lifetime', 'total_dna_points', 'offspring_count', 'death_cause']
    ]
    print(top_breeders.to_string(index=False))
    
    # ===== DNA GROWTH ANALYSIS =====
    print(f"\n🧬 DNA GROWTH ANALYSIS:")
    print(f"  Starting DNA Budget: 100 points")
    print(f"  Max Observed DNA: {lifetimes['total_dna_points'].max():.2f} points")
    print(f"  Growth Factor: {lifetimes['total_dna_points'].max() / 100:.2f}x")
    print(f"  Maximum DNA Gain: {lifetimes['total_dna_points'].max() - 100:.2f} points from eating!")
    
    # ===== TOTAL DNA IN SYSTEM =====
    total_dna = lifetimes.groupby('generation')['total_dna_points'].sum()
    print(f"\n💎 TOTAL DNA IN SYSTEM:")
    for gen, dna_sum in total_dna.items():
        avg_per_dot = dna_sum / len(lifetimes[lifetimes['generation'] == gen])
        print(f"  Gen {gen}: {dna_sum:>12,.1f} total DNA ({avg_per_dot:.1f} avg/dot)")
    
    # ===== DEATH ANALYSIS =====
    print(f"\n⚰️ DEATH CAUSES (Generation {explosion_gen}):")
    death_counts = explosion_dots['death_cause'].value_counts()
    for cause, count in death_counts.items():
        pct = (count / len(explosion_dots)) * 100
        print(f"  {cause.capitalize()}: {count:,} ({pct:.1f}%)")
    
    # ===== OFFSPRING DISTRIBUTION =====
    print(f"\n👶 OFFSPRING DISTRIBUTION (Gen {explosion_gen}):")
    offspring_stats = explosion_dots['offspring_count'].describe()
    print(f"  Mean: {offspring_stats['mean']:.2f}")
    print(f"  Median: {offspring_stats['50%']:.0f}")
    print(f"  Max: {offspring_stats['max']:.0f}")
    print(f"  Dots with 0 offspring: {(explosion_dots['offspring_count'] == 0).sum():,}")
    print(f"  Dots with 1+ offspring: {(explosion_dots['offspring_count'] >= 1).sum():,}")
    print(f"  Dots with 3+ offspring: {(explosion_dots['offspring_count'] >= 3).sum():,}")
    
    # ===== TIMELINE ANALYSIS =====
    explosion_metrics = colony_df[colony_df['generation'] == explosion_gen]
    if len(explosion_metrics) > 0:
        print(f"\n⏱️ GENERATION {explosion_gen} TIMELINE:")
        print(f"  Start Time: {explosion_metrics['session_time'].min():.1f}s")
        print(f"  End Time: {explosion_metrics['session_time'].max():.1f}s")
        print(f"  Duration: {explosion_metrics['simulation_time'].max():.1f}s")
        print(f"  Peak Population: {explosion_metrics['population'].max()}")
        print(f"  Max Avg DNA: {explosion_metrics['avg_dna'].max():.1f}")
        if 'total_births' in explosion_metrics.columns:
            print(f"  Total Births Logged: {explosion_metrics['total_births'].max()}")
        
        # Find peak birth rate
        explosion_metrics = explosion_metrics.copy()
        explosion_metrics['birth_rate'] = explosion_metrics['total_births'].diff() if 'total_births' in explosion_metrics.columns else 0
        if 'birth_rate' in explosion_metrics.columns and explosion_metrics['birth_rate'].max() > 0:
            peak_idx = explosion_metrics['birth_rate'].idxmax()
            peak_row = explosion_metrics.loc[peak_idx]
            print(f"\n🔥 EXPLOSION PEAK:")
            print(f"  Time: {peak_row['simulation_time']:.1f}s")
            print(f"  Population: {peak_row['population']:.0f}")
            print(f"  Avg DNA: {peak_row['avg_dna']:.1f}")
    
    # ===== VISUALIZATION =====
    print(f"\n📊 Generating visualizations...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'Population Explosion Analysis - {log_path.name}', fontsize=16, fontweight='bold')
    
    # 1. Generation progression
    gen_counts = lifetimes['generation'].value_counts().sort_index()
    axes[0, 0].bar(gen_counts.index, gen_counts.values, color='steelblue', alpha=0.8)
    axes[0, 0].set_title('Dots Created per Generation', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Generation')
    axes[0, 0].set_ylabel('Dots Created')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # 2. DNA evolution
    dna_by_gen = lifetimes.groupby('generation')['total_dna_points'].mean()
    axes[0, 1].plot(dna_by_gen.index, dna_by_gen.values, marker='o', linewidth=2, markersize=8, color='green')
    axes[0, 1].set_title('Average DNA per Generation', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Generation')
    axes[0, 1].set_ylabel('DNA Points')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Starting DNA')
    axes[0, 1].legend()
    
    # 3. Survival time
    survival_by_gen = gen_summary.set_index('generation')['survival_time']
    axes[0, 2].plot(survival_by_gen.index, survival_by_gen.values, marker='s', linewidth=2, markersize=8, color='purple')
    axes[0, 2].set_title('Survival Time per Generation', fontsize=12, fontweight='bold')
    axes[0, 2].set_xlabel('Generation')
    axes[0, 2].set_ylabel('Seconds')
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. DNA distribution (explosion gen)
    axes[1, 0].hist(explosion_dots['total_dna_points'], bins=50, color='orange', alpha=0.7, edgecolor='black')
    axes[1, 0].set_title(f'DNA Distribution (Gen {explosion_gen})', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('DNA Points')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].axvline(x=100, color='red', linestyle='--', alpha=0.5, label='Starting DNA')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    axes[1, 0].legend()
    
    # 5. Lifetime vs DNA (explosion gen)
    scatter = axes[1, 1].scatter(explosion_dots['total_dna_points'], explosion_dots['lifetime'], 
                                  c=explosion_dots['offspring_count'], cmap='viridis', alpha=0.6, s=20)
    axes[1, 1].set_title(f'DNA vs Lifetime (Gen {explosion_gen})', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('DNA Points')
    axes[1, 1].set_ylabel('Lifetime (seconds)')
    axes[1, 1].grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=axes[1, 1])
    cbar.set_label('Offspring Count', rotation=270, labelpad=15)
    
    # 6. Population over time (explosion gen)
    if len(explosion_metrics) > 0:
        axes[1, 2].plot(explosion_metrics['simulation_time'], explosion_metrics['population'], 
                       linewidth=2, color='red', alpha=0.8)
        axes[1, 2].set_title(f'Population Over Time (Gen {explosion_gen})', fontsize=12, fontweight='bold')
        axes[1, 2].set_xlabel('Time (seconds)')
        axes[1, 2].set_ylabel('Population')
        axes[1, 2].grid(True, alpha=0.3)
        axes[1, 2].fill_between(explosion_metrics['simulation_time'], explosion_metrics['population'], alpha=0.3, color='red')
    
    plt.tight_layout()
    output_path = log_path / 'analysis_explosion.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✅ Saved to: {output_path}")
    
    # ===== SUMMARY =====
    print("\n" + "="*80)
    print("🎉 CONCLUSION:")
    print("  The evolutionary memory system successfully created compound exponential growth!")
    print("  Each generation built on the previous, discovering increasingly efficient")
    print("  feeding → DNA growth → reproduction strategies until reaching critical mass.")
    print("="*80)
    
    return {
        'total_dots': len(lifetimes),
        'explosion_gen': explosion_gen,
        'max_dna': lifetimes['total_dna_points'].max(),
        'peak_population': explosion_metrics['population'].max() if len(explosion_metrics) > 0 else 0
    }


if __name__ == "__main__":
    # Default to most recent log directory
    import os
    
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
    
    analyze_explosion(log_dir)
