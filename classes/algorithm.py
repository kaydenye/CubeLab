#   Name: Kayden Ye
#   Date: 30/06/2025
#   File: classes/algorithm.py

import sqlite3

class Algorithm:
    db_path = "cubelab.db"

    def __init__(self, 
                 name: str, 
                 notation: str, 
                 tags: list = []):
        self.name = name
        self.notation = notation
        self.tags = tags

    def __str__(self):
        return f"Name: {self.name}, Notation: {self.notation}, Tags: {self.tags}"
        
    def get_name(self):
        return self.name
    
    def get_notation(self):
        return self.notation
    
    def get_tags(self):
        return self.tags
    
    def set_name(self, new_name):
        self.name = new_name

    def set_notation(self, new_notation):
        self.notation = new_notation

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def save_to_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if algorithm with the same name already exists
        cursor.execute("SELECT id FROM algorithms WHERE name = ?", (self.name,))
        existing = cursor.fetchone()

        # Insert algorithm
        cursor.execute("""
            INSERT INTO algorithms (name, notation) VALUES (?, ?)
        """, (self.name, self.notation))
        algorithm_id = cursor.lastrowid

        for tag in self.tags:
            tag_name = str(tag)

            # Insert tag if not exists
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_id = cursor.fetchone()[0]

            # Link algorithm to tag
            cursor.execute("""
                INSERT OR IGNORE INTO algorithm_tags (algorithm_id, tag_id)
                VALUES (?, ?)
            """, (algorithm_id, tag_id))

        conn.commit()
        conn.close()

    @classmethod
    def clear_all_algorithms(cls):
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()

        # Delete from linking table first to avoid foreign key constraint errors
        cursor.execute("DELETE FROM algorithm_tags")
        cursor.execute("DELETE FROM algorithms")
        cursor.execute("DELETE FROM tags")
        # Optional: Uncomment below to also clear all unused tags
        # cursor.execute("DELETE FROM tags")

        conn.commit()
        conn.close()
        print("All algorithms (and links) deleted.")

    @classmethod
    def load_from_db(cls, name):
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()

        # Get algorithm
        cursor.execute("SELECT id, notation FROM algorithms WHERE name = ?", (name,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"No algorithm found with name '{name}'")

        algorithm_id, notation = result

        # Get tags
        cursor.execute("""
            SELECT tags.name FROM tags
            JOIN algorithm_tags ON tags.id = algorithm_tags.tag_id
            WHERE algorithm_tags.algorithm_id = ?
        """, (algorithm_id,))
        tags = [row[0] for row in cursor.fetchall()]

        conn.close()
        return cls(name, notation, tags)