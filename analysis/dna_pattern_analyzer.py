"""
🧬 DNA PATTERN ANALYZER
Analyzes which gene combinations led to success.
Identifies champion DNA patterns and winning strategies.
"""

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
from collections import defaultdict

def analyze_dna_patterns(log_dir):
    """Analyze DNA patterns from champion dots"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_dir}")
        return
    
    print("="*80)
    print("🧬 DNA PATTERN ANALYSIS")
    print("="*80)
    print(f"📁 Analyzing: {log_path.name}")
    print()
    
    # Load data
    try:
        lifetimes = pd.read_csv(log_path / "dot_lifetimes.csv")
    except FileNotFoundError as e:
        print(f"❌ Missing required file: {e}")
        return
    
    # Use lifetimes data directly (contains DNA info)
    dot_data = lifetimes.copy()
    
    print(f"📊 Dataset: {len(dot_data)} dots with complete lifetime data")
    
    # ===== IDENTIFY CHAMPIONS =====
    # Champions = top 10% by fitness score
    # Use total_reward if available, otherwise default to 0
    dot_data['reward'] = 0  # Default value since we don't have reward data in lifetimes
    dot_data['fitness'] = (dot_data['lifetime'] * 
                          (1 + dot_data['offspring_count']) * 
                          (1 + dot_data['reward'] / 100))
    
    fitness_threshold = dot_data['fitness'].quantile(0.90)
    champions = dot_data[dot_data['fitness'] >= fitness_threshold]
    
    print(f"\n👑 CHAMPIONS (Top 10% by fitness):")
    print(f"  Total Champions: {len(champions)}")
    print(f"  Fitness Threshold: {fitness_threshold:.2f}")
    print(f"  Avg Lifetime: {champions['lifetime'].mean():.2f}s")
    print(f"  Avg Offspring: {champions['offspring_count'].mean():.2f}")
    print(f"  Avg DNA: {champions['total_dna_points'].mean():.2f}")
    
    # ===== GENE PATTERN ANALYSIS =====
    print(f"\n🔬 ANALYZING GENE PATTERNS...")
    
    # We need to load individual dot birth data to see gene allocations
    # This requires reading the dot_births.csv which has DNA snapshots
    
    # For now, analyze DNA point totals
    print(f"\n📈 DNA POINT DISTRIBUTION:")
    print(f"  Champions:")
    print(f"    Mean: {champions['total_dna_points'].mean():.2f}")
    print(f"    Median: {champions['total_dna_points'].median():.2f}")
    print(f"    Min: {champions['total_dna_points'].min():.2f}")
    print(f"    Max: {champions['total_dna_points'].max():.2f}")
    print(f"\n  Non-Champions:")
    non_champions = dot_data[dot_data['fitness'] < fitness_threshold]
    print(f"    Mean: {non_champions['total_dna_points'].mean():.2f}")
    print(f"    Median: {non_champions['total_dna_points'].median():.2f}")
    print(f"    Min: {non_champions['total_dna_points'].min():.2f}")
    print(f"    Max: {non_champions['total_dna_points'].max():.2f}")
    
    # ===== STRATEGY ANALYSIS =====
    print(f"\n🎯 SUCCESS CORRELATIONS:")
    
    # Correlation: DNA vs Lifetime
    dna_lifetime_corr = dot_data['total_dna_points'].corr(dot_data['lifetime'])
    print(f"  DNA ↔ Lifetime: {dna_lifetime_corr:.3f}")
    
    # Correlation: DNA vs Offspring
    dna_offspring_corr = dot_data['total_dna_points'].corr(dot_data['offspring_count'])
    print(f"  DNA ↔ Offspring: {dna_offspring_corr:.3f}")
    
    # Correlation: Lifetime vs Offspring
    lifetime_offspring_corr = dot_data['lifetime'].corr(dot_data['offspring_count'])
    print(f"  Lifetime ↔ Offspring: {lifetime_offspring_corr:.3f}")
    
    # ===== DEATH CAUSE ANALYSIS =====
    print(f"\n⚰️ DEATH PATTERNS:")
    print(f"  Champions:")
    champ_deaths = champions['death_cause'].value_counts()
    for cause, count in champ_deaths.items():
        pct = (count / len(champions)) * 100
        print(f"    {cause.capitalize()}: {count} ({pct:.1f}%)")
    
    print(f"\n  Non-Champions:")
    non_champ_deaths = non_champions['death_cause'].value_counts()
    for cause, count in non_champ_deaths.items():
        pct = (count / len(non_champions)) * 100
        print(f"    {cause.capitalize()}: {count} ({pct:.1f}%)")
    
    # ===== VISUALIZATION =====
    print(f"\n📊 Generating visualizations...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(f'DNA Pattern Analysis - {log_path.name}', fontsize=16, fontweight='bold')
    
    # 1. Champion vs Non-Champion DNA distribution
    axes[0, 0].hist([champions['total_dna_points'], non_champions['total_dna_points']], 
                    bins=30, label=['Champions', 'Non-Champions'], alpha=0.7, color=['gold', 'gray'])
    axes[0, 0].set_title('DNA Distribution: Champions vs Non-Champions', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('DNA Points')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # 2. Fitness scatter plot
    axes[0, 1].scatter(dot_data['total_dna_points'], dot_data['fitness'], 
                      c=dot_data['offspring_count'], cmap='plasma', alpha=0.5, s=20)
    axes[0, 1].set_title('DNA vs Fitness Score', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('DNA Points')
    axes[0, 1].set_ylabel('Fitness Score')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].axhline(y=fitness_threshold, color='red', linestyle='--', alpha=0.5, label='Champion Threshold')
    axes[0, 1].legend()
    
    # 3. Lifetime vs Offspring (colored by DNA)
    scatter = axes[1, 0].scatter(dot_data['lifetime'], dot_data['offspring_count'],
                                c=dot_data['total_dna_points'], cmap='viridis', alpha=0.6, s=30)
    axes[1, 0].set_title('Lifetime vs Offspring (colored by DNA)', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Lifetime (seconds)')
    axes[1, 0].set_ylabel('Offspring Count')
    axes[1, 0].grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=axes[1, 0])
    cbar.set_label('DNA Points', rotation=270, labelpad=15)
    
    # 4. Death causes comparison
    death_data = pd.DataFrame({
        'Champions': champ_deaths / len(champions) * 100,
        'Non-Champions': non_champ_deaths / len(non_champions) * 100
    }).fillna(0)
    
    death_data.plot(kind='bar', ax=axes[1, 1], color=['gold', 'gray'], alpha=0.8)
    axes[1, 1].set_title('Death Causes: Champions vs Non-Champions (%)', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Death Cause')
    axes[1, 1].set_ylabel('Percentage')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    output_path = log_path / 'analysis_dna_patterns.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✅ Saved to: {output_path}")
    
    # ===== TOP PERFORMERS =====
    print(f"\n🏆 TOP 10 CHAMPIONS:")
    top_champions = champions.nlargest(10, 'fitness')[
        ['dot_id', 'generation', 'lifetime', 'total_dna_points', 'offspring_count', 'fitness', 'death_cause']
    ]
    print(top_champions.to_string(index=False))
    
    print("\n" + "="*80)
    print("💡 KEY INSIGHTS:")
    if dna_lifetime_corr > 0.3:
        print("  ✅ Higher DNA strongly correlates with longer survival")
    if dna_offspring_corr > 0.3:
        print("  ✅ Higher DNA strongly correlates with more offspring")
    if lifetime_offspring_corr > 0.5:
        print("  ✅ Longer survival strongly correlates with reproduction success")
    
    # Check if champions died differently
    champ_starvation_pct = champ_deaths.get('starvation', 0) / len(champions) * 100
    non_champ_starvation_pct = non_champ_deaths.get('starvation', 0) / len(non_champions) * 100
    
    if champ_starvation_pct < non_champ_starvation_pct * 0.7:
        print("  ✅ Champions are much better at avoiding starvation")
    
    print("="*80)


if __name__ == "__main__":
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
    
    analyze_dna_patterns(log_dir)
