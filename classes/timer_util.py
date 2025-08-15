#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/timer_util.py

import sqlite3
import time
from .algorithm import Algorithm

class TimerUtil:
    """
    Function: Service class to handle stopwatch recording and statistics
    Inputs: none
    Outputs: none
    """
    def __init__(self):
        self.db_path = Algorithm.db_path
    
    def _ensure_times_columns(self, cursor):
        """
        Function: Ensure new columns exist on the times table
        Inputs: SQLite cursor
        Outputs: None (alters schema if needed)
        """
        cursor.execute("PRAGMA table_info(times)")
        columns = {col[1] for col in cursor.fetchall()}
        # Penalty columns used throughout the app
        if 'plus_two' not in columns:
            cursor.execute("ALTER TABLE times ADD COLUMN plus_two BOOLEAN DEFAULT 0")
        if 'dnf' not in columns:
            cursor.execute("ALTER TABLE times ADD COLUMN dnf BOOLEAN DEFAULT 0")

    def save_time(self, algorithm_name, time_seconds) :
        """
        Function: Save a stopwatch time to the database
        Inputs: algorithm_name, time_seconds
        Outputs: True on success, false otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get algorithm ID
                cursor.execute("SELECT id FROM algorithms WHERE name = ?", (algorithm_name,))
                result = cursor.fetchone()
                if result:
                    algorithm_id = result[0]
                    # Insert the time
                    cursor.execute(
                        "INSERT INTO times (algorithm_id, time_seconds, plus_two, dnf) VALUES (?, ?, 0, 0)",
                        (algorithm_id, time_seconds)
                    )
                    conn.commit()
                    return True
                return False
        except Exception:
            return False
    
    def get_algorithm_times(self, algorithm_name):
        """
        Function: Get all valid times for an algorithm, excluding DNF
        Inputs: algorithm_name
        Outputs: List of adjusted_time_seconds, timestamp
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                
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
    
    def get_time_count(self, algorithm_name):
        """
        Function: Get the number of times recorded for an algorithm
        Inputs: algorithm_name
        Outputs: Count for times for algorithm_name
        """
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
    
    def get_time_statistics(self, times_data):
        """
        Function: Calculate statistics from times
        Inputs: times_data which is list of time_seconds and timestamp
        Outputs: Dictionary with keys for personal best, worst, average, count or empty dictionary
        """
        if not times_data:
            return {}
        
        times_only = [t[0] for t in times_data]
        return {
            'best': min(times_only),
            'worst': max(times_only),
            'average': sum(times_only) / len(times_only),
            'count': len(times_only)
        }
    
    def get_algorithm_times_with_ids(self, algorithm_name):
        """
        Function: Get all times for an algorithm including IDs and penalties (+2, DNF)
        Inputs: algorithm_name
        Outputs: id, time_seconds, timestamp, plus_two, dnf
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                
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
    
    def update_time_penalty(self, time_id, plus_two=None, dnf=None):
        """
        Function: Update penalties for a specific time
        Inputs: time_id, plus_two, dnf
        Outputs: True if time was updated, false otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()

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
    
    def delete_time(self, time_id):
        """
        Function: Delete a specific time from the database
        Inputs: time_id
        Outputs: True if time was deleted, false otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM times WHERE id = ?", (time_id,))
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"Error deleting time: {e}")
            return False
