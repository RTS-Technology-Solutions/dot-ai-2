"""
🔍 GENERATION COMPARER
Compare statistics across multiple generations to identify trends.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import json

def compare_generations(log_dir, gen_list=None):
    """Compare specific generations or all generations"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"❌ Log directory not found: {log_dir}")
        return
    
    print("="*80)
    print("🔍 GENERATION COMPARISON")
    print("="*80)
    print(f"📁 Analyzing: {log_path.name}")
    print()
    
    # Load data
    try:
        lifetimes = pd.read_csv(log_path / "dot_lifetimes.csv")
        gen_summary = pd.read_csv(log_path / "generation_summary.csv")
        
        # Load colony metrics for incomplete generation reconstruction
        with open(log_path / "colony_metrics.jsonl", 'r') as f:
            colony_data = [json.loads(line) for line in f]
        colony_df = pd.DataFrame(colony_data)
        
    except FileNotFoundError as e:
        print(f"❌ Missing file: {e}")
        return
    
    # Detect and reconstruct incomplete generations
    max_gen_in_summary = gen_summary['generation'].max()
    max_gen_in_lifetimes = lifetimes['generation'].max()
    max_gen_in_colony = colony_df['generation'].max()
    
    if max_gen_in_lifetimes > max_gen_in_summary or max_gen_in_colony > max_gen_in_summary:
        incomplete_gen = max(max_gen_in_lifetimes, max_gen_in_colony)
        print(f"⚠️  Detected incomplete Generation {incomplete_gen} - reconstructing from colony data...")
        
        # Reconstruct metrics
        crash_gen_metrics = colony_df[colony_df['generation'] == incomplete_gen]
        crash_gen_dots = lifetimes[lifetimes['generation'] == incomplete_gen]
        
        if len(crash_gen_metrics) > 0:
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
            gen_summary = pd.concat([gen_summary, pd.DataFrame([crash_summary])], ignore_index=True)
            print(f"✅ Reconstructed Generation {incomplete_gen}\n")
    
    # Determine which generations to compare
    if gen_list is None:
        gen_list = sorted(lifetimes['generation'].unique())
    
    print(f"Comparing Generations: {gen_list}")
    print()
    
    # Build comparison table
    comparison_data = []
    
    for gen_num in gen_list:
        gen_dots = lifetimes[lifetimes['generation'] == gen_num]
        gen_info = gen_summary[gen_summary['generation'] == gen_num].iloc[0]
        
        comparison_data.append({
            'Generation': gen_num,
            'Dots Created': len(gen_dots),
            'Avg DNA': gen_dots['total_dna_points'].mean(),
            'Max DNA': gen_dots['total_dna_points'].max(),
            'Avg Lifetime': gen_dots['lifetime'].mean(),
            'Max Lifetime': gen_dots['lifetime'].max(),
            'Avg Offspring': gen_dots['offspring_count'].mean(),
            'Total Births': gen_info['total_births'],
            'Sexual %': (gen_info['sexual_births'] / gen_info['total_births'] * 100) if gen_info['total_births'] > 0 else 0,
            'Peak Pop': gen_info['peak_population'],
            'Survival Time': gen_info['survival_time'],
            'Combat Deaths': gen_info['combat_kills'],
            'Starvation Deaths': gen_info['starvation_deaths']
        })
    
    df = pd.DataFrame(comparison_data)
    
    print("📊 COMPARISON TABLE:")
    print(df.to_string(index=False))
    
    # Calculate trends
    print(f"\n📈 TRENDS:")
    
    if len(df) >= 2:
        dna_growth = ((df['Avg DNA'].iloc[-1] - df['Avg DNA'].iloc[0]) / df['Avg DNA'].iloc[0]) * 100
        lifetime_growth = ((df['Avg Lifetime'].iloc[-1] - df['Avg Lifetime'].iloc[0]) / df['Avg Lifetime'].iloc[0]) * 100
        offspring_growth = ((df['Avg Offspring'].iloc[-1] - df['Avg Offspring'].iloc[0]) / df['Avg Offspring'].iloc[0]) * 100
        
        print(f"  DNA Growth: {dna_growth:+.1f}% (Gen {gen_list[0]} → Gen {gen_list[-1]})")
        print(f"  Lifetime Growth: {lifetime_growth:+.1f}%")
        print(f"  Offspring Growth: {offspring_growth:+.1f}%")
        
        # Check for improvement
        if dna_growth > 10:
            print(f"  ✅ DNA is increasing (learning curve)")
        if lifetime_growth > 10:
            print(f"  ✅ Survival time is increasing")
        if offspring_growth > 10:
            print(f"  ✅ Reproduction rate is increasing")
    
    # Visualization
    print(f"\n📊 Generating comparison charts...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'Generation Comparison - {log_path.name}', fontsize=16, fontweight='bold')
    
    # 1. DNA Evolution
    axes[0, 0].plot(df['Generation'], df['Avg DNA'], marker='o', linewidth=2, label='Avg DNA', color='green')
    axes[0, 0].plot(df['Generation'], df['Max DNA'], marker='s', linewidth=2, label='Max DNA', color='lightgreen', alpha=0.7)
    axes[0, 0].set_title('DNA Points Evolution', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Generation')
    axes[0, 0].set_ylabel('DNA Points')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Lifetime Evolution
    axes[0, 1].plot(df['Generation'], df['Avg Lifetime'], marker='o', linewidth=2, label='Avg Lifetime', color='blue')
    axes[0, 1].plot(df['Generation'], df['Max Lifetime'], marker='s', linewidth=2, label='Max Lifetime', color='lightblue', alpha=0.7)
    axes[0, 1].set_title('Lifetime Evolution', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Generation')
    axes[0, 1].set_ylabel('Seconds')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Population Size
    axes[0, 2].bar(df['Generation'], df['Dots Created'], color='purple', alpha=0.7)
    axes[0, 2].set_title('Dots Created per Generation', fontsize=12, fontweight='bold')
    axes[0, 2].set_xlabel('Generation')
    axes[0, 2].set_ylabel('Dots')
    axes[0, 2].grid(True, alpha=0.3, axis='y')
    
    # 4. Reproduction Rate
    axes[1, 0].plot(df['Generation'], df['Avg Offspring'], marker='o', linewidth=2, color='red')
    axes[1, 0].set_title('Avg Offspring per Dot', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Generation')
    axes[1, 0].set_ylabel('Offspring Count')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Sexual Reproduction %
    axes[1, 1].plot(df['Generation'], df['Sexual %'], marker='o', linewidth=2, color='magenta')
    axes[1, 1].set_title('Sexual Reproduction Rate', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Generation')
    axes[1, 1].set_ylabel('Percentage (%)')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_ylim(0, 100)
    
    # 6. Death Causes
    x = df['Generation'].values
    combat = df['Combat Deaths'].values
    starvation = df['Starvation Deaths'].values
    
    axes[1, 2].bar(x, combat, label='Combat', color='red', alpha=0.7)
    axes[1, 2].bar(x, starvation, bottom=combat, label='Starvation', color='orange', alpha=0.7)
    axes[1, 2].set_title('Death Causes by Generation', fontsize=12, fontweight='bold')
    axes[1, 2].set_xlabel('Generation')
    axes[1, 2].set_ylabel('Deaths')
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_path = log_path / 'analysis_generation_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✅ Saved to: {output_path}")
    
    print("="*80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        log_dir = sys.argv[1]
        
        # Optional: specify generations to compare
        if len(sys.argv) > 2:
            gen_list = [int(g) for g in sys.argv[2:]]
        else:
            gen_list = None
    else:
        # Find most recent log directory
        logs_dir = Path("../logs")
        if logs_dir.exists():
            log_dirs = sorted([d for d in logs_dir.iterdir() if d.is_dir()], reverse=True)
            if log_dirs:
                log_dir = str(log_dirs[0])
                gen_list = None
            else:
                print("❌ No log directories found in ../logs/")
                sys.exit(1)
        else:
            print("❌ Logs directory not found: ../logs/")
            sys.exit(1)
    
    compare_generations(log_dir, gen_list)
