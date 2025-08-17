#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/timer_util.py

import sqlite3
import time
from .algorithm import Algorithm

class TimerUtil:
    def __init__(self):
        self.db_path = Algorithm.db_path

    # algorithm_name: str, name of the algorithm (str for database lookup)
    # time_seconds: float, time to save (float for precision to three decimals)
    # Returns: bool (True on success, false otherwise)
    def save_time(self, algorithm_name, time_seconds) :
        """
        Function: Save a stopwatch time to the database
        Input: algorithm_name, time_seconds
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
    
    # algorithm_name: str, name of the algorithm (str for database lookup)
    # Returns: list of (adjusted_time_seconds, timestamp)
    def get_algorithm_times(self, algorithm_name):
        """
        Function: Get all valid times for an algorithm, excluding times that have a DNF 
        Input: algorithm_name
        Outputs: List of adjusted_time_seconds, timestamp
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
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
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting algorithm times: {e}")
            return []
    
    # algorithm_name: str, name of the algorithm (str for database lookup)
    # Returns: int (number of times recorded for a particular algorithm)
    def get_time_count(self, algorithm_name):
        """
        Function: Get the number of times recorded for an algorithm
        Input: algorithm_name
        Outputs: Count for times for algorithm_name
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM times t
                    JOIN algorithms a ON t.algorithm_id = a.id
                    WHERE a.name = ?
                """, (algorithm_name,))
                return cursor.fetchone()[0]
        except Exception:
            return 0
    
    # times_data: list, list of (time_seconds, timestamp) tuples (list for stats)
    # Returns: dict (keys: best, worst, average, count)
    def get_time_statistics(self, times_data):
        """
        Function: Calculate statistics from times
        Input: times_data which is list of time_seconds and timestamp
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
    
    # algorithm_name: str, name of the algorithm (str for database lookup)
    # Returns: list of (id, time_seconds, timestamp, plus_two, dnf)
    def get_algorithm_times_with_ids(self, algorithm_name):
        """
        Function: Get all times for an algorithm including IDs and penalties (+2, DNF)
        Input: algorithm_name
        Outputs: id, time_seconds, timestamp, plus_two, dnf
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.time_seconds, t.timestamp, 
                           COALESCE(t.plus_two, 0), COALESCE(t.dnf, 0)
                    FROM times t
                    JOIN algorithms a ON t.algorithm_id = a.id
                    WHERE a.name = ?
                    ORDER BY t.timestamp DESC
                """, (algorithm_name,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error getting times with IDs: {e}")
            return []

    # time_id: int, unique ID of the time entry (int for database key)
    # plus_two: bool or None, set +2 penalty (bool for database update)
    # dnf: bool or None, set DNF status (bool for database update)
    # Returns: bool (True if updated, false otherwise)
    def update_time_penalty(self, time_id, plus_two=None, dnf=None):
        """
        Function: Update penalties for a specific time
        Input: time_id, plus_two, dnf
        Outputs: True if time was updated, false otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

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
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.rowcount > 0
                return False
        except Exception as e:
            print(f"Error updating time penalty: {e}")
            return False
    
    # time_id: int, unique ID of the time entry (int for database key)
    # Returns: bool (True if deleted, false otherwise)
    def delete_time(self, time_id):
        """
        Function: Delete a specific time from the database
        Input: time_id
        Outputs: True if time was deleted, false otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM times WHERE id = ?", (time_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting time: {e}")
            return False
