#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/timer_util.py

import sqlite3
import time
from typing import List, Tuple, Optional
from datetime import datetime
from .algorithm import Algorithm

class TimerUtil:
    """Service class to handle timer recording and statistics"""
    
    def __init__(self):
        self.db_path = Algorithm.db_path
    
    def save_time(self, algorithm_name: str, time_seconds: float) -> bool:
        """Save a timer result to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                # Get algorithm ID
                cur.execute("SELECT id FROM algorithms WHERE name = ?", (algorithm_name,))
                result = cur.fetchone()
                if result:
                    algorithm_id = result[0]
                    # Insert the time
                    cur.execute(
                        "INSERT INTO times (algorithm_id, time_seconds) VALUES (?, ?)",
                        (algorithm_id, time_seconds)
                    )
                    conn.commit()
                    return True
                return False
        except Exception:
            return False
    
    def get_algorithm_times(self, algorithm_name: str) -> List[Tuple[float, str]]:
        """Get all times for a specific algorithm"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT t.time_seconds, t.timestamp
                    FROM times t
                    JOIN algorithms a ON t.algorithm_id = a.id
                    WHERE a.name = ?
                    ORDER BY t.timestamp DESC
                """, (algorithm_name,))
                return cur.fetchall()
        except Exception:
            return []
    
    def get_time_count(self, algorithm_name: str) -> int:
        """Get the number of times recorded for an algorithm"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT COUNT(*) FROM times t
                    JOIN algorithms a ON t.algorithm_id = a.id
                    WHERE a.name = ?
                """, (algorithm_name,))
                return cur.fetchone()[0]
        except Exception:
            return 0
    
    def get_time_statistics(self, times_data: List[Tuple[float, str]]) -> dict:
        """Calculate statistics from times data"""
        if not times_data:
            return {}
        
        times_only = [t[0] for t in times_data]
        return {
            'best': min(times_only),
            'worst': max(times_only),
            'average': sum(times_only) / len(times_only),
            'count': len(times_only)
        }
