"""
Timing utilities for performance monitoring and analysis.
"""
import time
import datetime
from typing import Dict, Optional
from config.constants import TIMING_CONFIG


class TimingTracker:
    """Class to track timing for different components of the system."""
    
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}
        self.total_start_time: Optional[float] = None
        self.enabled = TIMING_CONFIG.get("enable_timing", True)
        self.precision = TIMING_CONFIG.get("timing_precision", 3)
        
    def start_total_timer(self) -> None:
        """Start the total system timer."""
        if not self.enabled:
            return
            
        self.total_start_time = time.time()
        current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"⏱️ [TIMING] System started at {current_time}")
        
    def start_timer(self, operation_name: str) -> None:
        """Start timing an operation."""
        if not self.enabled:
            return
            
        self.start_times[operation_name] = time.time()
        current_time = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"⏱️ [TIMING] Started {operation_name} at {current_time}")
        
    def stop_timer(self, operation_name: str) -> Optional[float]:
        """Stop timing an operation and record the duration."""
        if not self.enabled:
            return None
            
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            self.timings[operation_name] = duration
            print(f"⏱️ [TIMING] Completed {operation_name} in {duration:.{self.precision}f} seconds")
            del self.start_times[operation_name]
            return duration
        return None
        
    def get_total_time(self) -> Optional[float]:
        """Get the total system execution time."""
        if not self.enabled or not self.total_start_time:
            return None
            
        total_time = time.time() - self.total_start_time
        print(f"⏱️ [TIMING] Total system execution time: {total_time:.{self.precision}f} seconds")
        return total_time
        
    def print_timing_summary(self) -> None:
        """Print a comprehensive timing summary."""
        if not self.enabled:
            return
            
        print(f"\n{'='*60}")
        print(f"⏱️ TIMING SUMMARY")
        print(f"{'='*60}")
        
        total_time = self.get_total_time()
        if total_time:
            print(f"🕒 Total System Time: {total_time:.{self.precision}f} seconds")
            
        if self.timings:
            print(f"\n📊 Component Breakdown:")
            for operation, duration in sorted(self.timings.items()):
                percentage = (duration / total_time * 100) if total_time else 0
                print(f"   • {operation}: {duration:.{self.precision}f}s ({percentage:.1f}%)")
                
        print(f"{'='*60}\n")
        
    def reset(self) -> None:
        """Reset all timing data."""
        self.timings.clear()
        self.start_times.clear()
        self.total_start_time = None
        
    def get_timing(self, operation_name: str) -> Optional[float]:
        """Get the timing for a specific operation."""
        return self.timings.get(operation_name)
        
    def get_all_timings(self) -> Dict[str, float]:
        """Get all recorded timings."""
        return self.timings.copy()


# Global timing tracker instance
timing_tracker = TimingTracker() 