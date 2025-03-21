import sqlite3
import datetime

def create_database():
    """إنشاء قاعدة بيانات SQLite جديدة مع جدول الحجوزات"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    # إنشاء جدول للطاولات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tables (
        table_id INTEGER PRIMARY KEY,
        capacity INTEGER NOT NULL
    )
    ''')
    
    # إنشاء جدول للحجوزات
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
    
    # إضافة بعض الطاولات الافتراضية
    tables = [
        (1, 2), (2, 2), (3, 4), (4, 4), (5, 6), (6, 8)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO tables VALUES (?, ?)', tables)
    
    conn.commit()
    conn.close()
    
    print("تم إنشاء قاعدة البيانات بنجاح")

def check_availability(guests_number, date, time):
    """التحقق من توفر طاولات مناسبة للحجز"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    # البحث عن الطاولات المناسبة التي تستوعب عدد الضيوف
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
    """إنشاء حجز جديد في قاعدة البيانات"""
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

# إنشاء قاعدة البيانات عند استدعاء الملف مباشرة
if __name__ == "__main__":
    create_database()