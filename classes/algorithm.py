#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/algorithm.py

import sqlite3

class Algorithm:    
    # Centralized database path used by other services (e.g., TimerUtil)
    db_path = "cubelab.db"
    def __init__(self, name=None, notation=None, tags=None):
        """
        Function: Initialize Algorithm service or model instance
        Inputs: optional name, notation, tags (list[str]) for create/save flows
        Outputs: instance with db_path and optional fields set
        """
        self.db_path = Algorithm.db_path
        self.name = name
        self.notation = notation
        self.tags = tags or []

    def get_algorithms_with_filters(self, search_query, filter_tags, sort_order):
        """
        Function: Get algorithms based on the tags that the user has selected
        Inputs: search_query, filter_tags, sort_order
        Outputs: List of algorithm names
        """
        if filter_tags is None:
            filter_tags = set()
            
        order_sql = "ASC" if sort_order == "asc" else "DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
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
                cursor.execute(sql, params)
                return [r[0] for r in cursor.fetchall()]
            else:
                if has_search:
                    cursor.execute(
                        f"""
                        SELECT a.name
                        FROM algorithms a
                        WHERE LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?
                        ORDER BY a.name COLLATE NOCASE {order_sql}
                        """,
                        (f"%{search_query}%", f"%{search_query}%")
                    )
                    return [r[0] for r in cursor.fetchall()]
                else:
                    cursor.execute(f"SELECT name FROM algorithms ORDER BY name COLLATE NOCASE {order_sql}")
                    return [r[0] for r in cursor.fetchall()]

    def get_algorithm_details(self, name):
        """
        Function: Get algorithm details by name
        Inputs: name
        Outputs: Tuple of notation and tags
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT notation FROM algorithms WHERE name = ?", (name,))
            notation_row = cursor.fetchone()
            if not notation_row:
                return None
            
            notation = notation_row[0]

            cursor.execute(
                """
                SELECT tags.name FROM tags
                JOIN algorithm_tags ON tags.id = algorithm_tags.tag_id
                JOIN algorithms ON algorithms.id = algorithm_tags.algorithm_id
                WHERE algorithms.name = ?
                """,
                (name,),
            )
            tags = [t[0] for t in cursor.fetchall()]

            return notation, tags
    
    def save_to_db(self):
        """
        Function: Save this algorithm (and tags) to the database
        Inputs: uses self.name, self.notation, self.tags
        Outputs: algorithm_id
        """
        if not self.name or not self.notation:
            raise ValueError("name and notation are required")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Insert algorithm
            cursor.execute(
                "INSERT INTO algorithms (name, notation) VALUES (?, ?)",
                (self.name, self.notation)
            )
            algorithm_id = cursor.lastrowid
            # Ensure tags exist and link them
            for tag in self.tags:
                tag_name = tag.strip()
                if not tag_name:
                    continue
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag_row = cursor.fetchone()
                if tag_row:
                    tag_id = tag_row[0]
                    cursor.execute(
                        "INSERT OR IGNORE INTO algorithm_tags (algorithm_id, tag_id) VALUES (?, ?)",
                        (algorithm_id, tag_id)
                    )
            conn.commit()
            return algorithm_id
    
    def remove_algorithm(self, name):
        """
        Function: Remove an algorithm by name
        Inputs: name
        Outputs: True if removed, false otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM algorithms WHERE name = ?", (name,))
                res = cursor.fetchone()
                if res:
                    alg_id = res[0]
                    cursor.execute("DELETE FROM algorithm_tags WHERE algorithm_id = ?", (alg_id,))
                    cursor.execute("DELETE FROM algorithms WHERE id = ?", (alg_id,))
                    conn.commit()
                    return True
            return False
        except Exception:
            return False
    
    def get_all_tags(self):
        """
        Function: Get all tags
        Inputs: none
        Outputs: List of tags
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM tags ORDER BY name COLLATE NOCASE ASC")
                return [r[0] for r in cursor.fetchall()]
        except Exception:
            return []
    
    def algorithm_exists(self, name):
        """
        Function: Check if an algorithm exists by name
        Inputs: name
        Outputs: True if exists, false otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM algorithms WHERE name=?", (name,))
            return cursor.fetchone() is not None
