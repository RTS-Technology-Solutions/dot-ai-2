"""
=====================================================================
METRICS LOGGER - Data Collection & Analysis System
=====================================================================

This module handles ALL data logging for the simulation, converting
print statements into structured, analyzable data files.

WHAT THIS DOES:
- Logs all events to JSON file (timestamped, structured)
- Tracks generational metrics (births, deaths, DNA evolution)
- Records colony-wide statistics (population, energy, etc.)
- Provides data export for external analysis tools

FILE OUTPUTS:
1. events.jsonl - Event stream (one JSON object per line)
   - Combat events, births, deaths, etc.
   - Timestamped for precise timeline reconstruction
   
2. generation_summary.csv - Generational metrics
   - One row per generation
   - Survival time, births, deaths, peak population, etc.
   
3. colony_metrics.jsonl - Real-time colony stats
   - Sampled every N seconds (configurable)
   - Population, avg DNA, energy distribution, etc.
   
4. dot_lifetimes.csv - Individual dot tracking
   - Birth time, death time, DNA profile, reproduction success

USAGE:
    logger = MetricsLogger(session_name="experiment_01")
    logger.log_event("BIRTH", {"dot_id": 5, "parent_id": 3})
    logger.log_colony_metrics(simulation)
    logger.log_generation_end(summary)
    logger.close()
=====================================================================
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path


class MetricsLogger:
    """
    Structured data logger for simulation metrics and events
    """
    
    def __init__(self, session_name=None, output_dir="logs"):
        """
        Initialize logger with session name
        
        Args:
            session_name: Unique identifier for this run (default: timestamp)
            output_dir: Directory to store log files
        """
        # Create session name if not provided
        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.session_name = session_name
        self.output_dir = Path(output_dir)
        self.session_dir = self.output_dir / session_name
        
        # Create directories
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Track session start time
        self.session_start = time.time()
        self.simulation_start = None  # Set when simulation starts
        
        # File handles
        self.events_file = None
        self.colony_metrics_file = None
        self.generation_summary_file = None
        self.dot_lifetimes_file = None
        
        # CSV writers
        self.generation_csv_writer = None
        self.dot_lifetimes_csv_writer = None
        
        # Tracking
        self.dot_birth_times = {}  # dot_id -> birth timestamp
        self.colony_metric_interval = 1.0  # Log colony metrics every N seconds
        self.last_colony_metric_time = 0.0
        
        # Open files
        self._open_files()
        
        # Log session start
        self._log_session_start()
        
        print(f"📊 Metrics logger initialized: {self.session_dir}")
    
    def _open_files(self):
        """Open all log files"""
        # Events log (JSONL - JSON Lines format)
        events_path = self.session_dir / "events.jsonl"
        self.events_file = open(events_path, 'w', encoding='utf-8')
        
        # Colony metrics log (JSONL)
        colony_path = self.session_dir / "colony_metrics.jsonl"
        self.colony_metrics_file = open(colony_path, 'w', encoding='utf-8')
        
        # Generation summary (CSV)
        gen_path = self.session_dir / "generation_summary.csv"
        self.generation_summary_file = open(gen_path, 'w', newline='', encoding='utf-8')
        gen_fields = [
            'generation', 'survival_time', 'peak_population', 'total_births',
            'sexual_births', 'asexual_births', 'total_deaths', 'combat_kills',
            'starvation_deaths', 'avg_dna_points', 'session_time'
        ]
        self.generation_csv_writer = csv.DictWriter(self.generation_summary_file, fieldnames=gen_fields)
        self.generation_csv_writer.writeheader()
        
        # Dot lifetimes (CSV)
        dot_path = self.session_dir / "dot_lifetimes.csv"
        self.dot_lifetimes_file = open(dot_path, 'w', newline='', encoding='utf-8')
        dot_fields = [
            'dot_id', 'generation', 'birth_time', 'death_time', 'lifetime',
            'total_dna_points', 'offspring_count', 'death_cause'
        ]
        self.dot_lifetimes_csv_writer = csv.DictWriter(self.dot_lifetimes_file, fieldnames=dot_fields)
        self.dot_lifetimes_csv_writer.writeheader()
    
    def _log_session_start(self):
        """Log session metadata"""
        metadata = {
            'session_name': self.session_name,
            'start_time': datetime.now().isoformat(),
            'version': '2.0',
            'description': 'Dot AI Evolution Simulation'
        }
        
        metadata_path = self.session_dir / "session_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def get_session_time(self):
        """Get time elapsed since session start (seconds)"""
        return time.time() - self.session_start
    
    def log_event(self, event_type, data, simulation_time=None):
        """
        Log a discrete event to the events stream
        
        Args:
            event_type: Type of event (BIRTH, DEATH, ATTACK, etc.)
            data: Dictionary of event-specific data
            simulation_time: Simulation time (optional, for correlation)
        """
        event = {
            'session_time': self.get_session_time(),
            'simulation_time': simulation_time,
            'event_type': event_type,
            'data': data
        }
        
        # Write as single-line JSON
        self.events_file.write(json.dumps(event) + '\n')
        self.events_file.flush()  # Ensure immediate write
    
    def log_colony_metrics(self, simulation, force=False):
        """
        Log current colony-wide metrics
        
        Args:
            simulation: DotSimulation instance
            force: Force logging even if interval not reached
        """
        # Calculate metrics
        dots = simulation.dots
        food = simulation.food
        
        # Population stats
        population = len(dots)
        if population == 0:
            return  # No dots to measure
        
        # Check if enough time has passed
        # Handle generation resets where time_elapsed goes back to 0
        time_since_last = simulation.time_elapsed - self.last_colony_metric_time
        if not force and time_since_last < self.colony_metric_interval and time_since_last >= 0:
            return
        
        self.last_colony_metric_time = simulation.time_elapsed
        
        # DNA statistics
        total_dna = sum(d.dna.get_total_points() for d in dots)
        avg_dna = total_dna / population
        min_dna = min(d.dna.get_total_points() for d in dots)
        max_dna = max(d.dna.get_total_points() for d in dots)
        
        # Energy statistics
        total_energy = sum(d.resources.energy for d in dots)
        avg_energy = total_energy / population
        min_energy = min(d.resources.energy for d in dots)
        max_energy = max(d.resources.energy for d in dots)
        
        # Health statistics
        total_health = sum(d.resources.health for d in dots)
        avg_health = total_health / population
        
        # Age statistics
        ages = [d.brain.age for d in dots]
        avg_age = sum(ages) / population
        max_age = max(ages)
        
        # Food availability
        food_count = len(food)
        total_food_energy = sum(f.energy_value for f in food)
        
        metrics = {
            'session_time': self.get_session_time(),
            'simulation_time': simulation.time_elapsed,
            'generation': simulation.generation,
            
            # Population
            'population': population,
            
            # DNA
            'avg_dna': round(avg_dna, 2),
            'min_dna': min_dna,
            'max_dna': max_dna,
            
            # Energy
            'avg_energy': round(avg_energy, 2),
            'min_energy': round(min_energy, 2),
            'max_energy': round(max_energy, 2),
            'total_energy': round(total_energy, 2),
            
            # Health
            'avg_health': round(avg_health, 2),
            
            # Age
            'avg_age': round(avg_age, 2),
            'max_age': round(max_age, 2),
            
            # Food
            'food_count': food_count,
            'total_food_energy': total_food_energy,
            
            # Cumulative stats
            'total_births': simulation.total_births,
            'total_deaths': simulation.total_dots_died,
            'total_attacks': simulation.total_attacks,
            
            # Current generation stats (for real-time monitoring)
            'gen_sexual_births': simulation.current_gen_metrics.get('sexual_births', 0),
            'gen_asexual_births': simulation.current_gen_metrics.get('asexual_births', 0),
        }
        
        # Write as single-line JSON
        self.colony_metrics_file.write(json.dumps(metrics) + '\n')
        self.colony_metrics_file.flush()
    
    def log_dot_birth(self, dot_id, generation, parent_ids, dna_points, simulation_time):
        """
        Track dot birth for lifetime analysis
        
        Args:
            dot_id: Unique dot identifier
            generation: Generation number
            parent_ids: List of parent IDs
            dna_points: Total DNA points
            simulation_time: Current simulation time
        """
        self.dot_birth_times[dot_id] = {
            'generation': generation,
            'birth_time': simulation_time,
            'dna_points': dna_points,
            'offspring_count': 0
        }
        
        # Log birth event
        self.log_event('BIRTH', {
            'dot_id': dot_id,
            'generation': generation,
            'parent_ids': parent_ids,
            'dna_points': dna_points
        }, simulation_time)
    
    def log_dot_death(self, dot_id, cause, simulation_time):
        """
        Track dot death and write lifetime record
        
        Args:
            dot_id: Unique dot identifier
            cause: Death cause (combat, starvation, etc.)
            simulation_time: Current simulation time
        """
        if dot_id not in self.dot_birth_times:
            return  # Dot wasn't tracked (old generation?)
        
        birth_data = self.dot_birth_times[dot_id]
        lifetime = simulation_time - birth_data['birth_time']
        
        # Write to lifetime CSV
        self.dot_lifetimes_csv_writer.writerow({
            'dot_id': dot_id,
            'generation': birth_data['generation'],
            'birth_time': round(birth_data['birth_time'], 2),
            'death_time': round(simulation_time, 2),
            'lifetime': round(lifetime, 2),
            'total_dna_points': birth_data['dna_points'],
            'offspring_count': birth_data['offspring_count'],
            'death_cause': cause
        })
        self.dot_lifetimes_file.flush()
        
        # Log death event
        self.log_event('DEATH', {
            'dot_id': dot_id,
            'cause': cause,
            'lifetime': round(lifetime, 2)
        }, simulation_time)
        
        # Remove from tracking
        del self.dot_birth_times[dot_id]
    
    def log_attack(self, attacker_id, target_id, damage, hit, simulation_time):
        """Log combat event"""
        self.log_event('ATTACK', {
            'attacker_id': attacker_id,
            'target_id': target_id,
            'damage': round(damage, 2) if damage else 0,
            'hit': hit
        }, simulation_time)
    
    def log_reproduction(self, parent_ids, child_id, reproduction_type, simulation_time):
        """
        Log reproduction event
        
        Args:
            parent_ids: List of parent IDs
            child_id: Offspring ID
            reproduction_type: 'sexual' or 'asexual'
            simulation_time: Current simulation time
        """
        # Update offspring count for parents
        for parent_id in parent_ids:
            if parent_id in self.dot_birth_times:
                self.dot_birth_times[parent_id]['offspring_count'] += 1
        
        self.log_event('REPRODUCTION', {
            'parent_ids': parent_ids,
            'child_id': child_id,
            'type': reproduction_type
        }, simulation_time)
    
    def log_generation_end(self, summary):
        """
        Log generation summary to CSV
        
        Args:
            summary: Dictionary of generation metrics
        """
        # Calculate avg DNA if available
        avg_dna = 0
        if summary.get('avg_dna_snapshots'):
            avg_dna = summary['avg_dna_snapshots'][-1][1] if summary['avg_dna_snapshots'] else 0
        
        # Write to CSV
        self.generation_csv_writer.writerow({
            'generation': summary['generation'],
            'survival_time': round(summary.get('survival_time', 0), 2),
            'peak_population': summary['peak_population'],
            'total_births': summary['births'],
            'sexual_births': summary['sexual_births'],
            'asexual_births': summary['asexual_births'],
            'total_deaths': summary['deaths'],
            'combat_kills': summary['combat_kills'],
            'starvation_deaths': summary['starvation_deaths'],
            'avg_dna_points': round(avg_dna, 2),
            'session_time': round(self.get_session_time(), 2)
        })
        self.generation_summary_file.flush()
        
        # Reset colony metrics timer for new generation
        # (since simulation time_elapsed will reset to 0)
        self.last_colony_metric_time = 0.0
        
        # Also log as event
        self.log_event('GENERATION_END', summary, summary.get('survival_time', 0))
    
    def log_extinction(self, generation, simulation_time):
        """Log extinction event"""
        self.log_event('EXTINCTION', {
            'generation': generation,
        }, simulation_time)
    
    def close(self):
        """Close all file handles"""
        if self.events_file:
            self.events_file.close()
        if self.colony_metrics_file:
            self.colony_metrics_file.close()
        if self.generation_summary_file:
            self.generation_summary_file.close()
        if self.dot_lifetimes_file:
            self.dot_lifetimes_file.close()
        
        print(f"📊 Metrics logger closed: {self.session_dir}")
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
