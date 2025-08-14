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
        """Get all valid times for a specific algorithm (excluding DNF times)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                # First, check if penalty columns exist, if not add them
                cur.execute("PRAGMA table_info(times)")
                columns = [col[1] for col in cur.fetchall()]
                
                if 'plus_two' not in columns:
                    cur.execute("ALTER TABLE times ADD COLUMN plus_two BOOLEAN DEFAULT 0")
                if 'dnf' not in columns:
                    cur.execute("ALTER TABLE times ADD COLUMN dnf BOOLEAN DEFAULT 0")
                
                cur.execute("""
                    SELECT 
                        CASE 
                            WHEN COALESCE(t.plus_two, 0) = 1 THEN t.time_seconds + 2.0
                            ELSE t.time_seconds
                        END as adjusted_time,
                        t.timestamp
                    FROM times t
                    JOIN algorithms a ON t.algorithm_id = a.id
                    WHERE a.name = ? AND COALESCE(t.dnf, 0) = 0
                    ORDER BY t.timestamp DESC
                """, (algorithm_name,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting algorithm times: {e}")
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
    
    def get_algorithm_times_with_ids(self, algorithm_name: str) -> List[Tuple[int, float, str, bool, bool]]:
        """Get all times for a specific algorithm with IDs and penalty flags"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                # First, check if penalty columns exist, if not add them
                cur.execute("PRAGMA table_info(times)")
                columns = [col[1] for col in cur.fetchall()]
                
                if 'plus_two' not in columns:
                    cur.execute("ALTER TABLE times ADD COLUMN plus_two BOOLEAN DEFAULT 0")
                if 'dnf' not in columns:
                    cur.execute("ALTER TABLE times ADD COLUMN dnf BOOLEAN DEFAULT 0")
                
                cur.execute("""
                    SELECT t.id, t.time_seconds, t.timestamp, 
                           COALESCE(t.plus_two, 0), COALESCE(t.dnf, 0)
                    FROM times t
                    JOIN algorithms a ON t.algorithm_id = a.id
                    WHERE a.name = ?
                    ORDER BY t.timestamp DESC
                """, (algorithm_name,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting times with IDs: {e}")
            return []
    
    def update_time_penalty(self, time_id: int, plus_two: bool = None, dnf: bool = None) -> bool:
        """Update penalty flags for a specific time"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                
                # Build update query based on provided parameters
                updates = []
                params = []
                
                if plus_two is not None:
                    updates.append("plus_two = ?")
                    params.append(plus_two)
                
                if dnf is not None:
                    updates.append("dnf = ?")
                    params.append(dnf)
                
                if updates:
                    params.append(time_id)
                    query = f"UPDATE times SET {', '.join(updates)} WHERE id = ?"
                    cur.execute(query, params)
                    conn.commit()
                    return cur.rowcount > 0
                return False
        except Exception as e:
            print(f"Error updating time penalty: {e}")
            return False
    
    def delete_time(self, time_id: int) -> bool:
        """Delete a specific time from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM times WHERE id = ?", (time_id,))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"Error deleting time: {e}")
            return False
