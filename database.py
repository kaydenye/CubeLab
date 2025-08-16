import sqlite3

def init_db():
    """Initialise the SQLite database schema and migrate if needed."""
    conn = sqlite3.connect("cubelab.db")  # Creates file if it doesn't exist
    cursor = conn.cursor()

    # Optional but recommended
    try:
        cursor.execute("PRAGMA foreign_keys = ON")
    except Exception:
        pass

    # Create table for algorithms
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS algorithms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            notation TEXT NOT NULL
        )
        """
    )

    # Create table for tags
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """
    )

    # Create many-to-many link table for algorithm-tag relationship
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS algorithm_tags (
            algorithm_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (algorithm_id) REFERENCES algorithms(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id),
            PRIMARY KEY (algorithm_id, tag_id)
        )
        """
    )

    # Create table for storing times with penalty columns
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            algorithm_id INTEGER,
            time_seconds REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            plus_two BOOLEAN DEFAULT 0,
            dnf BOOLEAN DEFAULT 0,
            FOREIGN KEY (algorithm_id) REFERENCES algorithms(id)
        )
        """
    )

    # Migrate existing times table to include new columns if missing
    try:
        cursor.execute("PRAGMA table_info(times)")
        cols = {row[1] for row in cursor.fetchall()}
        if "plus_two" not in cols:
            cursor.execute("ALTER TABLE times ADD COLUMN plus_two BOOLEAN DEFAULT 0")
        if "dnf" not in cols:
            cursor.execute("ALTER TABLE times ADD COLUMN dnf BOOLEAN DEFAULT 0")
    except Exception:
        # If PRAGMA fails, ignore and proceed
        pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()