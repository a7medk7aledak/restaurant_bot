import sqlite3
import datetime

def create_database():
    """Create a new SQLite database with a reservations table."""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    # Create a tables table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tables (
        table_id INTEGER PRIMARY KEY,
        capacity INTEGER NOT NULL
    )
    ''')
    
    # Create a reservations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        customer_name TEXT,
        guests_number INTEGER,
        reservation_date TEXT,
        reservation_time TEXT,
        created_at TEXT,
        FOREIGN KEY (table_id) REFERENCES tables(table_id)
    )
    ''')
    
    # Insert some default tables
    tables = [
        (1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 8)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO tables VALUES (?, ?)', tables)
    
    conn.commit()
    conn.close()
    
    print("Database created successfully.")

def check_availability(guests_number, date, time):
    """Check the availability of tables for reservation."""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    # Find a suitable table that can accommodate the number of guests
    cursor.execute('''
    SELECT table_id FROM tables 
    WHERE capacity >= ? AND table_id NOT IN (
        SELECT table_id FROM reservations 
        WHERE reservation_date = ? AND reservation_time = ?
    )
    ORDER BY capacity ASC
    LIMIT 1
    ''', (guests_number, date, time))
    
    available_table = cursor.fetchone()
    conn.close()
    
    if available_table:
        return available_table[0]
    return None

def make_reservation(table_id, customer_name, guests_number, date, time):
    """Create a new reservation in the database."""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
    INSERT INTO reservations 
    (table_id, customer_name, guests_number, reservation_date, reservation_time, created_at) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (table_id, customer_name, guests_number, date, time, created_at))
    
    conn.commit()
    reservation_id = cursor.lastrowid
    conn.close()
    
    return reservation_id

# Create the database when the script is run directly
if __name__ == "__main__":
    create_database()
