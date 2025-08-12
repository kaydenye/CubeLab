import sqlite3

def init_db():
    conn = sqlite3.connect("cubelab.db")  # Creates file if it doesn't exist
    cursor = conn.cursor()

    # Create table for algorithms
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS algorithms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            notation TEXT NOT NULL
        )
    """)

    # Create table for tags
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # Create many-to-many link table for algorithm-tag relationship
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS algorithm_tags (
            algorithm_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (algorithm_id) REFERENCES algorithms(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id),
            PRIMARY KEY (algorithm_id, tag_id)
        )
    """)

    # Create table for storing times
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            algorithm_id INTEGER,
            time_seconds REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (algorithm_id) REFERENCES algorithms(id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()