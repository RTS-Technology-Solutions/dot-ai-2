"""
=====================================================================
REAL-TIME METRICS MONITOR - Live Colony Evolution Dashboard
=====================================================================

This is a STANDALONE utility program that runs ALONGSIDE the simulation
to provide real-time analytics and visualization of colony evolution.

WHAT THIS DOES:
- Reads log files in real-time (tails the data streams)
- Displays live charts of colony metrics over time
- Shows generation statistics and trends
- Monitors individual dot lifetimes and DNA evolution
- Updates automatically as simulation generates new data

HOW TO USE:
1. Start the main simulation (main.py)
2. Run this monitor in a separate terminal/window
3. Monitor will auto-detect the latest session
4. Live charts update as data flows in

REQUIREMENTS:
- matplotlib (for charting)
- pandas (for data analysis)

Install: pip install matplotlib pandas

USAGE:
    python monitor.py                    # Auto-detect latest session
    python monitor.py SESSION_NAME       # Monitor specific session
    python monitor.py --list             # List available sessions

CHARTS DISPLAYED:
1. Population over time
2. Average DNA points evolution
3. Energy distribution
4. Birth/death rates
5. Generation survival times
6. Reproduction type breakdown
=====================================================================
"""

import sys
import time
import json
import csv
from pathlib import Path
from datetime import datetime
import argparse

try:
    import matplotlib
    matplotlib.use('TkAgg')  # Use Tk backend for interactive windows
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    import matplotlib.gridspec as gridspec
except ImportError:
    print("ERROR: matplotlib not installed!")
    print("Install with: pip install matplotlib")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed!")
    print("Install with: pip install pandas")
    sys.exit(1)


class MetricsMonitor:
    """
    Real-time monitor for simulation metrics
    Reads log files and displays live charts
    """
    
    def __init__(self, session_dir):
        """
        Initialize monitor for a specific session
        
        Args:
            session_dir: Path to session log directory
        """
        self.session_dir = Path(session_dir)
        
        if not self.session_dir.exists():
            raise ValueError(f"Session directory not found: {session_dir}")
        
        # File paths
        self.colony_metrics_path = self.session_dir / "colony_metrics.jsonl"
        self.generation_summary_path = self.session_dir / "generation_summary.csv"
        self.events_path = self.session_dir / "events.jsonl"
        
        # Data storage
        self.colony_data = []
        self.generation_data = []
        self.events = []
        
        # File positions (for tailing)
        self.colony_file_pos = 0
        self.generation_file_pos = 0
        self.events_file_pos = 0
        
        # Setup figure
        self.setup_figure()
        
        print(f"📊 Monitoring session: {self.session_dir.name}")
        print(f"📁 Location: {self.session_dir}")
        print("")
    
    def setup_figure(self):
        """Setup matplotlib figure with subplots"""
        # Create figure with dark background
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('DOT AI - COLONY EVOLUTION MONITOR', fontsize=16, fontweight='bold')
        
        # Create grid layout (3 rows, 3 columns)
        gs = gridspec.GridSpec(3, 3, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # Row 1: Population & DNA
        self.ax_population = self.fig.add_subplot(gs[0, :2])
        self.ax_dna = self.fig.add_subplot(gs[0, 2])
        
        # Row 2: Energy & Health
        self.ax_energy = self.fig.add_subplot(gs[1, :2])
        self.ax_food = self.fig.add_subplot(gs[1, 2])
        
        # Row 3: Generations & Reproduction
        self.ax_generations = self.fig.add_subplot(gs[2, :2])
        self.ax_reproduction = self.fig.add_subplot(gs[2, 2])
        
        # Configure axes
        self._configure_axes()
    
    def _configure_axes(self):
        """Configure axis labels and styling"""
        # Population chart
        self.ax_population.set_title('Colony Population Over Time', fontweight='bold')
        self.ax_population.set_xlabel('Session Time (seconds)')
        self.ax_population.set_ylabel('Population')
        self.ax_population.grid(True, alpha=0.3)
        
        # DNA chart
        self.ax_dna.set_title('DNA Points', fontweight='bold')
        self.ax_dna.set_xlabel('Session Time (s)')
        self.ax_dna.set_ylabel('Avg DNA')
        self.ax_dna.grid(True, alpha=0.3)
        
        # Energy chart
        self.ax_energy.set_title('Colony Energy Over Time', fontweight='bold')
        self.ax_energy.set_xlabel('Session Time (seconds)')
        self.ax_energy.set_ylabel('Energy')
        self.ax_energy.grid(True, alpha=0.3)
        
        # Food chart
        self.ax_food.set_title('Food Count', fontweight='bold')
        self.ax_food.set_xlabel('Session Time (s)')
        self.ax_food.set_ylabel('Food Items')
        self.ax_food.grid(True, alpha=0.3)
        
        # Generations chart
        self.ax_generations.set_title('Generation Survival Times', fontweight='bold')
        self.ax_generations.set_xlabel('Generation Number')
        self.ax_generations.set_ylabel('Survival Time (seconds)')
        self.ax_generations.grid(True, alpha=0.3)
        
        # Reproduction chart
        self.ax_reproduction.set_title('Reproduction Types', fontweight='bold')
    
    def read_new_data(self):
        """Read new data from log files (tail behavior)"""
        # Read colony metrics
        if self.colony_metrics_path.exists():
            with open(self.colony_metrics_path, 'r') as f:
                f.seek(self.colony_file_pos)
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            self.colony_data.append(data)
                        except json.JSONDecodeError:
                            pass
                self.colony_file_pos = f.tell()
        
        # Read generation summaries
        if self.generation_summary_path.exists():
            try:
                df = pd.read_csv(self.generation_summary_path)
                self.generation_data = df.to_dict('records')
            except Exception:
                pass
    
    def update_charts(self, frame):
        """Update all charts with new data"""
        # Read new data
        self.read_new_data()
        
        if not self.colony_data:
            return
        
        # Clear all axes
        self.ax_population.clear()
        self.ax_dna.clear()
        self.ax_energy.clear()
        self.ax_food.clear()
        self.ax_generations.clear()
        self.ax_reproduction.clear()
        
        # Reconfigure after clearing
        self._configure_axes()
        
        # Extract data for plotting - USE SESSION_TIME for continuous timeline
        times = [d['session_time'] for d in self.colony_data]
        populations = [d['population'] for d in self.colony_data]
        avg_dnas = [d['avg_dna'] for d in self.colony_data]
        avg_energies = [d['avg_energy'] for d in self.colony_data]
        total_energies = [d['total_energy'] for d in self.colony_data]
        food_counts = [d['food_count'] for d in self.colony_data]
        generations = [d['generation'] for d in self.colony_data]
        
        # Plot population
        self.ax_population.plot(times, populations, 'cyan', linewidth=2, label='Population')
        self.ax_population.fill_between(times, populations, alpha=0.3, color='cyan')
        
        # Mark generation transitions
        if len(self.colony_data) > 1:
            prev_gen = generations[0]
            for i, gen in enumerate(generations[1:], 1):
                if gen != prev_gen:
                    self.ax_population.axvline(x=times[i], color='white', linestyle='--', 
                                              alpha=0.3, linewidth=1)
                prev_gen = gen
        
        self.ax_population.legend(loc='upper left')
        
        # Add current value annotation
        if populations:
            current_pop = populations[-1]
            self.ax_population.text(0.98, 0.95, f'Current: {current_pop}', 
                                   transform=self.ax_population.transAxes,
                                   ha='right', va='top', fontsize=12, 
                                   bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        # Plot DNA
        self.ax_dna.plot(times, avg_dnas, 'lime', linewidth=2)
        self.ax_dna.fill_between(times, avg_dnas, alpha=0.3, color='lime')
        if avg_dnas:
            self.ax_dna.text(0.98, 0.95, f'{avg_dnas[-1]:.1f}', 
                           transform=self.ax_dna.transAxes,
                           ha='right', va='top', fontsize=14, fontweight='bold')
        
        # Plot energy
        self.ax_energy.plot(times, avg_energies, 'yellow', linewidth=2, label='Avg Energy/Dot')
        self.ax_energy.plot(times, total_energies, 'orange', linewidth=2, alpha=0.7, label='Total Energy')
        self.ax_energy.legend(loc='upper left')
        
        # Plot food
        self.ax_food.plot(times, food_counts, 'red', linewidth=2)
        self.ax_food.fill_between(times, food_counts, alpha=0.3, color='red')
        if food_counts:
            self.ax_food.text(0.98, 0.95, f'{food_counts[-1]}', 
                            transform=self.ax_food.transAxes,
                            ha='right', va='top', fontsize=14, fontweight='bold')
        
        # Plot generation survival times
        if self.generation_data:
            gens = [d['generation'] for d in self.generation_data]
            survival_times = [d['survival_time'] for d in self.generation_data]
            
            self.ax_generations.bar(gens, survival_times, color='magenta', alpha=0.7)
            
            # Add trend line if enough data
            if len(gens) > 1:
                z = pd.Series(survival_times).rolling(window=min(3, len(gens)), center=True).mean()
                self.ax_generations.plot(gens, z, 'cyan', linewidth=2, label='Trend')
                self.ax_generations.legend(loc='upper left')
        
        # Plot reproduction type breakdown (pie chart)
        # Use current generation data if available (from colony snapshots)
        # Otherwise fall back to completed generation summaries
        total_sexual = 0
        total_asexual = 0
        
        # First try to get current generation data from latest colony snapshot
        if self.colony_data:
            latest = self.colony_data[-1]
            total_sexual = latest.get('gen_sexual_births', 0)
            total_asexual = latest.get('gen_asexual_births', 0)
        
        # If no current data, sum up all completed generations
        if total_sexual == 0 and total_asexual == 0 and self.generation_data:
            total_sexual = sum(d.get('sexual_births', 0) for d in self.generation_data)
            total_asexual = sum(d.get('asexual_births', 0) for d in self.generation_data)
        
        total_births = total_sexual + total_asexual
        
        if total_births > 0:
            sizes = [total_sexual, total_asexual]
            labels = [f'Sexual\n{total_sexual}', f'Asexual\n{total_asexual}']
            colors = ['#ff69b4', '#00ff00']
            explode = (0.1, 0)
            
            self.ax_reproduction.pie(sizes, explode=explode, labels=labels, colors=colors,
                                    autopct='%1.1f%%', shadow=True, startangle=90,
                                    textprops={'fontsize': 10, 'weight': 'bold'})
        else:
            # Show message when no births yet
            self.ax_reproduction.text(0.5, 0.5, 'No births yet', 
                                     transform=self.ax_reproduction.transAxes,
                                     ha='center', va='center', fontsize=12,
                                     color='gray', style='italic')
        
        # Update title with session info
        if self.colony_data:
            latest = self.colony_data[-1]
            gen = latest.get('generation', 0)
            sim_time = latest.get('simulation_time', 0)
            
            self.fig.suptitle(
                f'DOT AI - COLONY EVOLUTION MONITOR | Gen {gen} | Time: {sim_time:.1f}s',
                fontsize=16, fontweight='bold'
            )
    
    def run(self, update_interval=1000):
        """
        Start monitoring with live updates
        
        Args:
            update_interval: Update interval in milliseconds (default: 1000ms = 1s)
        """
        print("🚀 Starting real-time monitor...")
        print(f"🔄 Refresh rate: {update_interval}ms")
        print("")
        print("Charts will update automatically as simulation runs.")
        print("Close this window to stop monitoring.")
        print("")
        
        # Create animation (updates charts periodically)
        ani = FuncAnimation(self.fig, self.update_charts, interval=update_interval,
                           cache_frame_data=False)
        
        # Show window
        plt.show()


def list_sessions(log_dir="logs"):
    """List all available logging sessions"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        print(f"No log directory found: {log_dir}")
        return []
    
    sessions = [d for d in log_path.iterdir() if d.is_dir()]
    
    if not sessions:
        print(f"No sessions found in {log_dir}")
        return []
    
    print("Available sessions:")
    print("=" * 60)
    
    for session in sorted(sessions, reverse=True):
        metadata_path = session / "session_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            start_time = metadata.get('start_time', 'Unknown')
            print(f"📁 {session.name}")
            print(f"   Started: {start_time}")
            print("")
    
    print("=" * 60)
    return sessions


def get_latest_session(log_dir="logs"):
    """Get the most recent logging session based on file activity"""
    log_path = Path(log_dir)
    
    if not log_path.exists():
        return None
    
    sessions = [d for d in log_path.iterdir() if d.is_dir()]
    
    if not sessions:
        return None
    
    # Get the most recently modified file in each session directory
    def get_latest_file_time(session_dir):
        files = list(session_dir.glob('*'))
        if not files:
            return session_dir.stat().st_mtime
        return max(f.stat().st_mtime for f in files)
    
    # Sort by most recent file activity (not directory modification time)
    latest = max(sessions, key=get_latest_file_time)
    return latest


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Real-time monitor for Dot AI simulation metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python monitor.py                     # Auto-detect latest session
  python monitor.py 20260102_143025     # Monitor specific session
  python monitor.py --list              # List available sessions
  python monitor.py --refresh 500       # Update every 500ms
        """
    )
    
    parser.add_argument('session', nargs='?', default=None,
                       help='Session name to monitor (default: latest)')
    parser.add_argument('--list', action='store_true',
                       help='List available sessions and exit')
    parser.add_argument('--refresh', type=int, default=1000,
                       help='Chart refresh interval in milliseconds (default: 1000)')
    parser.add_argument('--log-dir', default='logs',
                       help='Log directory path (default: logs)')
    
    args = parser.parse_args()
    
    # List sessions and exit
    if args.list:
        list_sessions(args.log_dir)
        return
    
    # Determine session to monitor
    if args.session:
        session_dir = Path(args.log_dir) / args.session
    else:
        print("🔍 Auto-detecting latest session...")
        session_dir = get_latest_session(args.log_dir)
        
        if session_dir is None:
            print("❌ No sessions found!")
            print(f"   Expected location: {args.log_dir}/")
            print("")
            print("Make sure the simulation is running and generating logs.")
            print("You can also specify a session name manually.")
            return
        
        print(f"✅ Found latest session: {session_dir.name}")
        print("")
    
    # Check if session exists
    if not session_dir.exists():
        print(f"❌ Session not found: {session_dir}")
        print("")
        print("Available sessions:")
        list_sessions(args.log_dir)
        return
    
    # Create and run monitor
    try:
        monitor = MetricsMonitor(session_dir)
        monitor.run(update_interval=args.refresh)
    except KeyboardInterrupt:
        print("")
        print("🛑 Monitor stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
