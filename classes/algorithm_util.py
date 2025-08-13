#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/algorithm_util.py

import sqlite3
from typing import List, Tuple, Optional
from .algorithm import Algorithm

class AlgorithmUtil:
    """Service class to handle algorithm database operations"""
    
    def __init__(self):
        self.db_path = Algorithm.db_path
    
    def get_algorithms_with_filters(self, search_query: str = "", filter_tags: set = None, sort_order: str = "asc") -> List[str]:
        """Get algorithms filtered by search and tags"""
        if filter_tags is None:
            filter_tags = set()
            
        order_sql = "ASC" if sort_order == "asc" else "DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            tags = list(filter_tags)
            has_tags = len(tags) > 0
            has_search = bool(search_query)
            
            if has_tags:
                placeholders = ",".join(["?"] * len(tags))
                where_parts = [f"t.name IN ({placeholders})"]
                params = tags[:]
                
                if has_search:
                    where_parts.append("(LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?)")
                    params.extend([f"%{search_query}%", f"%{search_query}%"])
                
                where_clause = " AND ".join(where_parts)
                sql = f"""
                    SELECT DISTINCT a.name
                    FROM algorithms a
                    JOIN algorithm_tags at ON at.algorithm_id = a.id
                    JOIN tags t ON t.id = at.tag_id
                    WHERE {where_clause}
                    ORDER BY a.name COLLATE NOCASE {order_sql}
                """
                cur.execute(sql, params)
                return [r[0] for r in cur.fetchall()]
            else:
                if has_search:
                    cur.execute(
                        f"""
                        SELECT a.name
                        FROM algorithms a
                        WHERE LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?
                        ORDER BY a.name COLLATE NOCASE {order_sql}
                        """,
                        (f"%{search_query}%", f"%{search_query}%")
                    )
                    return [r[0] for r in cur.fetchall()]
                else:
                    cur.execute(f"SELECT name FROM algorithms ORDER BY name COLLATE NOCASE {order_sql}")
                    return [r[0] for r in cur.fetchall()]
    
    def get_algorithm_details(self, name: str) -> Optional[Tuple[str, List[str]]]:
        """Get algorithm notation and tags by name"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT notation FROM algorithms WHERE name = ?", (name,))
            notation_row = cur.fetchone()
            if not notation_row:
                return None
            
            notation = notation_row[0]
            
            cur.execute(
                """
                SELECT tags.name FROM tags
                JOIN algorithm_tags ON tags.id = algorithm_tags.tag_id
                JOIN algorithms ON algorithms.id = algorithm_tags.algorithm_id
                WHERE algorithms.name = ?
                """,
                (name,),
            )
            tags = [t[0] for t in cur.fetchall()]
            
            return notation, tags
    
    def remove_algorithm(self, name: str) -> bool:
        """Remove algorithm and return success status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM algorithms WHERE name = ?", (name,))
                res = cur.fetchone()
                if res:
                    alg_id = res[0]
                    # Remove tag relations first for FK integrity
                    cur.execute("DELETE FROM algorithm_tags WHERE algorithm_id = ?", (alg_id,))
                    cur.execute("DELETE FROM algorithms WHERE id = ?", (alg_id,))
                    conn.commit()
                    return True
            return False
        except Exception:
            return False
    
    def get_all_tags(self) -> List[str]:
        """Return list of all tag names"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM tags ORDER BY name COLLATE NOCASE ASC")
                return [r[0] for r in cur.fetchall()]
        except Exception:
            return []
    
    def algorithm_exists(self, name: str) -> bool:
        """Check if algorithm with given name exists"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM algorithms WHERE name=?", (name,))
            return cur.fetchone() is not None
