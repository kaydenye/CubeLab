#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: classes/algorithm.py


import sqlite3

class Algorithm:    
    db_path = "cubelab.db"
    # name (str or None): Algorithm name, string for easy matching/display
    # notation (str or None): Algorithm notation, string for move sequences
    # tags (list of str or None): Tags for categorization, list allows multiple tags
    def __init__(self, name: str = None, notation: str = None, tags: list = None):
        self.db_path = Algorithm.db_path
        self.name = name
        self.notation = notation
        self.tags = tags or []

    # search_query (str): Text to search for, string for pattern matching
    # filter_tags (set of str): Tags to filter by, set for uniqueness/fast lookup
    # sort_order (str): 'asc' or 'desc', string for clarity
    # Returns: list of str, algorithm names
    # Data Source: cubelab.db, tables: algorithms, tags, algorithm_tags
    def get_algorithms_with_filters(self, search_query: str, filter_tags: set, sort_order: str) -> list:
        """
        Function: Get algorithms based on the tags that the user has selected using a quicksort algorithm
        Input: search_query (str), filter_tags (set), sort_order (str)
        Outputs: List of algorithm names
        """
        if filter_tags is None:
            filter_tags = set()
        
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
                """
                cursor.execute(sql, params)
                results = [r[0] for r in cursor.fetchall()]
            else:
                if has_search:
                    cursor.execute(
                        f"""
                        SELECT a.name
                        FROM algorithms a
                        WHERE LOWER(a.name) LIKE ? OR LOWER(a.notation) LIKE ?
                        """,
                        (f"%{search_query}%", f"%{search_query}%")
                    )
                    results = [r[0] for r in cursor.fetchall()]
                else:
                    cursor.execute("SELECT name FROM algorithms")
                    results = [r[0] for r in cursor.fetchall()]
            
            sorted_results = self._quicksort(results)
            
            # Reverse if descending order
            if sort_order == "desc":
                sorted_results.reverse()
                
            return sorted_results

    # array (list of str): List to partition, list allows in-place sorting
    # low (int): Start index, int for indexing
    # high (int): End index, int for indexing
    # Returns: int, partition index
    def _partition(self, array: list, low: int, high: int) -> int:
        """
        Function: Partition function for quicksort
        Input: array (list), low (int), high (int)
        Outputs: Partition index (int)
        """
        pivot = array[high]

        i = low - 1
        for j in range(low, high):
            if array[j].lower() <= pivot.lower():
                i = i + 1
                (array[i], array[j]) = (array[j], array[i])

        (array[i + 1], array[high]) = (array[high], array[i + 1])
        return i + 1

    # array (list of str): List to sort
    # Returns: list of str, sorted list
    def _quicksort(self, array: list, low: int = None, high: int = None) -> list:
        """
        Function: Sort array using quicksort algorithm
        Input: array (list of strings)
        Outputs: Sorted list
        """
        if low is None or high is None:
            # Initial call: make a copy and sort the whole array
            arr = array.copy()
            return self._quicksort(arr, 0, len(arr) - 1)
        if low < high:
            pi = self._partition(array, low, high)
            self._quicksort(array, low, pi - 1)
            self._quicksort(array, pi + 1, high)
        return array

    # name (str): Algorithm name to look up, string for matching
    # Returns: tuple (notation: str, tags: list of str) or None
    # Data Source: cubelab.db, tables: algorithms, tags, algorithm_tags
    def get_algorithm_details(self, name: str) -> tuple:
        """
        Function: Get algorithm details by name
        Input: name (str)
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

    # self.name (str): Algorithm name, string for matching algorithm with database
    # self.notation (str): Notation, string for moves
    # self.tags (list of str): Tags, list for multiple values
    # Returns: int, new algorithm's database ID
    # Data Source: cubelab.db, tables: algorithms, tags, algorithm_tags
    def save_to_db(self) -> int:
        """
        Function: Save this algorithm (and tags) to the database
        Input: uses self.name, self.notation, self.tags
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

    # name (str): Name of algorithm to remove, string for matching algorithm name with database
    # Returns: bool, True if removed, false otherwise
    # Data Source: cubelab.db, tables: algorithms, tags, algorithm_tags
    def remove_algorithm(self, name: str) -> bool:
        """
        Function: Remove an algorithm by name and cleanup unused tags
        Input: name
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
                    
                    # Clean up any tags that are no longer used
                    self.cleanup_unused_tags()
                    return True
            return False
        except Exception:
            return False
    
    def update_algorithm(self, original_name: str, new_name: str, new_notation: str, new_tags: list) -> bool:
        """
        Function: Update an existing algorithm with new details
        Input: original_name (str), new_name (str), new_notation (str), new_tags (list)
        Outputs: True if updated successfully, false otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the algorithm ID
                cursor.execute("SELECT id FROM algorithms WHERE name = ?", (original_name,))
                result = cursor.fetchone()
                if not result:
                    return False
                
                algorithm_id = result[0]
                
                # Update algorithm name and notation
                cursor.execute(
                    "UPDATE algorithms SET name = ?, notation = ? WHERE id = ?",
                    (new_name, new_notation, algorithm_id)
                )
                
                # Remove existing tag associations
                cursor.execute("DELETE FROM algorithm_tags WHERE algorithm_id = ?", (algorithm_id,))
                
                # Add new tags
                for tag_name in new_tags:
                    # Check if tag exists, if not create it
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                    tag_row = cursor.fetchone()
                    
                    if tag_row:
                        tag_id = tag_row[0]
                    else:
                        # Create new tag
                        cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                        tag_id = cursor.lastrowid
                    
                    # Link algorithm to tag
                    cursor.execute(
                        "INSERT INTO algorithm_tags (algorithm_id, tag_id) VALUES (?, ?)",
                        (algorithm_id, tag_id)
                    )
                
                conn.commit()
                
                # Clean up any tags that are no longer used
                self.cleanup_unused_tags()
                
                return True
        except Exception:
            return False
    
    # Returns: list of str, all tag names
    # Data Source: cubelab.db, table: tags
    def get_all_tags(self) -> list:
        """
        Function: Get all tags
        Input: none
        Outputs: List of tags
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM tags")
                results = [r[0] for r in cursor.fetchall()]
                return self._quicksort(results)
        except Exception:
            return []
    
    # Returns: int, number of tags deleted
    # Data Source: cubelab.db, tables: tags, algorithm_tags
    def cleanup_unused_tags(self) -> int:
        """
        Function: Delete tags that are not linked to any algorithms
        Input: none
        Outputs: Number of tags deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Find tags that have no algorithm associations
                cursor.execute("""
                    DELETE FROM tags 
                    WHERE id NOT IN (
                        SELECT DISTINCT tag_id 
                        FROM algorithm_tags
                    )
                """)
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except Exception as e:
            print(f"Error cleaning up unused tags: {e}")
            return 0
    
    # Returns: list of str, unused tag names
    # Data Source: cubelab.db, tables: tags, algorithm_tags
    def get_unused_tags(self) -> list:
        """
        Function: Get list of tags that are not linked to any algorithms to delete from the database
        Input: none
        Outputs: List of unused tag names
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM tags 
                    WHERE id NOT IN (
                        SELECT DISTINCT tag_id 
                        FROM algorithm_tags
                    )
                """)
                results = [r[0] for r in cursor.fetchall()]
                return self._quicksort(results)
        except Exception as e:
            print(f"Error getting unused tags: {e}")
            return []
    
    # name (str): The name to check for existence, string for matching algorithm name to database
    # Returns: bool, True if exists, false otherwise
    # Data Source: cubelab.db, table: algorithms
    def algorithm_exists(self, name: str) -> bool:
        """
        Function: Check if an algorithm exists by name
        Input: name
        Outputs: True if exists, false otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM algorithms WHERE name=?", (name,))
            return cursor.fetchone() is not None
